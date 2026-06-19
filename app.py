import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import db
from models import Empresa, Tanque, Cliente, IngresoTanque, VentaSalida
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecreto'
# Usa la base de datos de SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///atva_petrol.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()
    try:
        from seed import seed_data
        seed_data()
    except Exception as e:
        print("Error al hacer seed_data:", e)

@app.route('/health')
def health():
    return 'OK'

# Decorador simple para requerir login
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- RUTAS DE AUTENTICACIÓN ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == 'admin123':
            session['logged_in'] = True
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Credenciales incorrectas', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Sesión cerrada', 'info')
    return redirect(url_for('login'))

# --- DASHBOARD ---
@app.route('/')
@login_required
def dashboard():
    total_clientes = Cliente.query.count()
    clientes_activos = Cliente.query.filter_by(estado='Activo').count()
    clientes_suspendidos = Cliente.query.filter_by(estado='Suspendido').count()
    total_tanques = Tanque.query.count()
    stock_total = db.session.query(db.func.sum(Tanque.stock_actual)).scalar() or 0
    ventas_autorizadas = VentaSalida.query.filter_by(estado_venta='Autorizada').count()
    ventas_limitadas = VentaSalida.query.filter_by(estado_venta='Limitada').count()
    ventas_bloqueadas = VentaSalida.query.filter_by(estado_venta='Bloqueada').count()
    ingresos_registrados = IngresoTanque.query.count()
    
    # Alertas
    alertas_stock = Tanque.query.filter(Tanque.stock_actual < Tanque.stock_minimo).all()
    clientes_suspendidos_lista = Cliente.query.filter_by(estado='Suspendido').all()
    ventas_problematicas = VentaSalida.query.filter(VentaSalida.estado_venta.in_(['Limitada', 'Bloqueada'])).order_by(VentaSalida.fecha_hora.desc()).limit(5).all()
    
    # Últimas ventas (8)
    ultimas_ventas = VentaSalida.query.order_by(VentaSalida.fecha_hora.desc()).limit(8).all()

    return render_template('dashboard.html', 
                           total_clientes=total_clientes,
                           clientes_activos=clientes_activos,
                           clientes_suspendidos=clientes_suspendidos,
                           total_tanques=total_tanques,
                           stock_total=stock_total,
                           ventas_autorizadas=ventas_autorizadas,
                           ventas_limitadas=ventas_limitadas,
                           ventas_bloqueadas=ventas_bloqueadas,
                           ingresos_registrados=ingresos_registrados,
                           alertas_stock=alertas_stock,
                           clientes_suspendidos_lista=clientes_suspendidos_lista,
                           ventas_problematicas=ventas_problematicas,
                           ultimas_ventas=ultimas_ventas)

# --- EMPRESA ---
@app.route('/empresa', methods=['GET', 'POST'])
@login_required
def empresa():
    empresa_info = Empresa.query.first()
    if not empresa_info:
        # Por si no hay seed
        empresa_info = Empresa(nombre_estacion='AVTA Petrol', nit='0', direccion='', ciudad='', telefono='')
        db.session.add(empresa_info)
        db.session.commit()

    if request.method == 'POST':
        empresa_info.nombre_estacion = request.form.get('nombre_estacion')
        empresa_info.nit = request.form.get('nit')
        empresa_info.direccion = request.form.get('direccion')
        empresa_info.ciudad = request.form.get('ciudad')
        empresa_info.telefono = request.form.get('telefono')
        empresa_info.stock_minimo_global = float(request.form.get('stock_minimo_global', 1000))
        empresa_info.factor_holgura = float(request.form.get('factor_holgura', 10))
        empresa_info.cupo_base_cliente_nuevo = float(request.form.get('cupo_base_cliente_nuevo', 50))
        
        db.session.commit()
        flash('Datos de empresa actualizados', 'success')
        return redirect(url_for('empresa'))

    return render_template('empresa/index.html', empresa=empresa_info)

# --- TANQUES ---
@app.route('/tanques')
@login_required
def tanques():
    lista_tanques = Tanque.query.all()
    return render_template('tanques/index.html', tanques=lista_tanques)

@app.route('/tanques/crear', methods=['POST'])
@login_required
def crear_tanque():
    identificador = request.form.get('identificador')
    tipo_carburante = request.form.get('tipo_carburante')
    capacidad_maxima = float(request.form.get('capacidad_maxima'))
    stock_minimo = float(request.form.get('stock_minimo'))
    
    if stock_minimo > capacidad_maxima:
        flash('El stock mínimo no puede superar la capacidad máxima', 'danger')
        return redirect(url_for('tanques'))
        
    empresa = Empresa.query.first()
    nuevo = Tanque(identificador=identificador, tipo_carburante=tipo_carburante, 
                   capacidad_maxima=capacidad_maxima, stock_minimo=stock_minimo, 
                   id_empresa=empresa.id_empresa)
    db.session.add(nuevo)
    db.session.commit()
    flash('Tanque creado', 'success')
    return redirect(url_for('tanques'))

@app.route('/tanques/eliminar/<int:id>')
@login_required
def eliminar_tanque(id):
    tanque = Tanque.query.get_or_404(id)
    if tanque.ingresos or tanque.ventas:
        flash('No se puede eliminar el tanque porque tiene movimientos.', 'danger')
    else:
        db.session.delete(tanque)
        db.session.commit()
        flash('Tanque eliminado.', 'success')
    return redirect(url_for('tanques'))

# --- CLIENTES ---
@app.route('/clientes')
@login_required
def clientes():
    lista_clientes = Cliente.query.all()
    return render_template('clientes/index.html', clientes=lista_clientes)

@app.route('/clientes/crear', methods=['POST'])
@login_required
def crear_cliente():
    ci_nit = request.form.get('ci_nit')
    nombre = request.form.get('nombre_razon_social')
    placa = request.form.get('placa_vehiculo')
    tipo = request.form.get('tipo_cliente')
    estado = request.form.get('estado', 'Activo')
    
    # Validar duplicados
    existente = Cliente.query.filter((Cliente.ci_nit == ci_nit) | (Cliente.placa_vehiculo == placa)).first()
    if existente:
        flash(f'Ya existe un cliente con el CI/NIT {existente.ci_nit} o la placa {existente.placa_vehiculo}', 'danger')
        return redirect(url_for('clientes'))
    
    nuevo = Cliente(ci_nit=ci_nit, nombre_razon_social=nombre, placa_vehiculo=placa, tipo_cliente=tipo, estado=estado)
    db.session.add(nuevo)
    db.session.commit()
    flash('Cliente registrado', 'success')
    return redirect(url_for('clientes'))

@app.route('/clientes/estado/<int:id>')
@login_required
def cambiar_estado_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    cliente.estado = 'Suspendido' if cliente.estado == 'Activo' else 'Activo'
    db.session.commit()
    flash(f'Estado cambiado a {cliente.estado}', 'success')
    return redirect(url_for('clientes'))

# --- INGRESOS ---
@app.route('/ingresos', methods=['GET', 'POST'])
@login_required
def ingresos():
    if request.method == 'POST':
        id_tanque = int(request.form.get('id_tanque'))
        litros = float(request.form.get('litros_ingresados'))
        factura = request.form.get('numero_factura')
        proveedor = request.form.get('proveedor')
        
        if litros <= 0:
            flash('Los litros deben ser mayor a 0', 'danger')
            return redirect(url_for('ingresos'))

        tanque = Tanque.query.get(id_tanque)
        if tanque.stock_actual + litros > tanque.capacidad_maxima:
            flash(f'El ingreso supera la capacidad máxima del tanque ({tanque.capacidad_maxima}L). Stock actual: {tanque.stock_actual}L', 'danger')
            return redirect(url_for('ingresos'))
            
        ingreso = IngresoTanque(id_tanque=id_tanque, litros_ingresados=litros, numero_factura=factura, proveedor=proveedor)
        tanque.stock_actual += litros
        
        db.session.add(ingreso)
        db.session.commit()
        flash('Ingreso registrado correctamente', 'success')
        return redirect(url_for('ingresos'))
        
    tanque_id = request.args.get('tanque_id')
    query = IngresoTanque.query
    if tanque_id:
        query = query.filter_by(id_tanque=tanque_id)
        
    lista_ingresos = query.order_by(IngresoTanque.fecha_hora.desc()).all()
    tanques_list = Tanque.query.all()
    return render_template('ingresos/index.html', ingresos=lista_ingresos, tanques=tanques_list, tanque_filtro=tanque_id)

# --- VENTAS ---
@app.route('/ventas')
@login_required
def ventas():
    lista_ventas = VentaSalida.query.order_by(VentaSalida.fecha_hora.desc()).all()
    return render_template('ventas/index.html', ventas=lista_ventas)

@app.route('/ventas/nueva', methods=['GET', 'POST'])
@login_required
def nueva_venta():
    empresa_info = Empresa.query.first()
    tanques_list = Tanque.query.all()
    
    if request.method == 'POST':
        placa_documento = request.form.get('placa_documento')
        id_tanque = int(request.form.get('id_tanque'))
        litros_solicitados = float(request.form.get('litros_solicitados'))
        
        if litros_solicitados <= 0:
            flash('Los litros solicitados deben ser mayor a 0', 'danger')
            return redirect(url_for('nueva_venta'))

        # Buscar cliente
        cliente = Cliente.query.filter((Cliente.placa_vehiculo == placa_documento) | (Cliente.ci_nit == placa_documento)).first()
        
        if not cliente:
            # Crear cliente express si no existe
            cliente = Cliente(ci_nit=placa_documento, nombre_razon_social='Cliente ' + placa_documento, placa_vehiculo=placa_documento, tipo_cliente='Particular')
            db.session.add(cliente)
            db.session.commit()
            flash('Cliente registrado automáticamente', 'info')

        if cliente.estado == 'Suspendido':
            flash('El cliente está suspendido. No se puede realizar la venta.', 'danger')
            return redirect(url_for('nueva_venta'))

        # Calcular promedio 28 días
        hace_28_dias = datetime.utcnow() - timedelta(days=28)
        ventas_previas = VentaSalida.query.filter(
            VentaSalida.id_cliente == cliente.id_cliente,
            VentaSalida.fecha_hora >= hace_28_dias,
            VentaSalida.estado_venta.in_(['Autorizada', 'Limitada'])
        ).all()
        
        total_litros_28 = sum(v.litros_autorizados for v in ventas_previas)
        
        if total_litros_28 > 0:
            promedio_semanal = total_litros_28 / 4
            limite_permitido = promedio_semanal + (promedio_semanal * empresa_info.factor_holgura / 100)
        else:
            promedio_semanal = 0
            limite_permitido = empresa_info.cupo_base_cliente_nuevo

        tanque = Tanque.query.get(id_tanque)
        
        # Validaciones de venta
        estado_venta = ''
        litros_autorizados = 0
        mensaje = ''
        
        if tanque.stock_actual < litros_solicitados and tanque.stock_actual < limite_permitido:
            # Aunque no pueda todo, podría tratar de dar el máximo, pero simplifiquemos a Bloqueada si no hay stock ni para lo solicitado y el limite
            estado_venta = 'Bloqueada'
            litros_autorizados = 0
            mensaje = 'Stock insuficiente en el tanque.'
        else:
            if litros_solicitados <= limite_permitido:
                if tanque.stock_actual >= litros_solicitados:
                    estado_venta = 'Autorizada'
                    litros_autorizados = litros_solicitados
                    mensaje = 'Venta autorizada por el total solicitado.'
                    tanque.stock_actual -= litros_autorizados
                else:
                    estado_venta = 'Bloqueada'
                    litros_autorizados = 0
                    mensaje = 'Stock insuficiente.'
            else:
                if tanque.stock_actual >= limite_permitido:
                    estado_venta = 'Limitada'
                    litros_autorizados = limite_permitido
                    mensaje = 'La cantidad solicitada supera el límite permitido. Solo se autoriza el cupo permitido.'
                    tanque.stock_actual -= litros_autorizados
                else:
                    estado_venta = 'Bloqueada'
                    litros_autorizados = 0
                    mensaje = 'Stock insuficiente.'

        venta = VentaSalida(
            id_cliente=cliente.id_cliente,
            id_tanque=id_tanque,
            litros_solicitados=litros_solicitados,
            litros_autorizados=litros_autorizados,
            promedio_semanal=promedio_semanal,
            limite_permitido=limite_permitido,
            estado_venta=estado_venta,
            mensaje_validacion=mensaje
        )
        db.session.add(venta)
        db.session.commit()
        
        if estado_venta == 'Autorizada':
            flash(mensaje, 'success')
        elif estado_venta == 'Limitada':
            flash(mensaje, 'warning')
        else:
            flash(mensaje, 'danger')

        return render_template('ventas/resultado.html', venta=venta, cliente=cliente)

    return render_template('ventas/nueva.html', tanques=tanques_list)

# --- REPORTES ---
@app.route('/reportes')
@login_required
def reportes():
    ventas = VentaSalida.query.order_by(VentaSalida.fecha_hora.desc()).all()
    tanques = Tanque.query.all()
    return render_template('reportes/index.html', ventas=ventas, tanques=tanques)

if __name__ == '__main__':
    app.run(debug=True)
