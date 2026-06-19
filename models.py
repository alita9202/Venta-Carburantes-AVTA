from database import db
from datetime import datetime

class Empresa(db.Model):
    __tablename__ = 'empresa'
    id_empresa = db.Column(db.Integer, primary_key=True)
    nombre_estacion = db.Column(db.String(100), nullable=False)
    nit = db.Column(db.String(20), nullable=False)
    direccion = db.Column(db.String(200), nullable=False)
    ciudad = db.Column(db.String(50), nullable=False)
    telefono = db.Column(db.String(20))
    stock_minimo_global = db.Column(db.Float, nullable=False, default=1000)
    factor_holgura = db.Column(db.Float, nullable=False, default=10)
    cupo_base_cliente_nuevo = db.Column(db.Float, nullable=False, default=50)

    tanques = db.relationship('Tanque', backref='empresa', lazy=True)

class Tanque(db.Model):
    __tablename__ = 'tanque'
    id_tanque = db.Column(db.Integer, primary_key=True)
    id_empresa = db.Column(db.Integer, db.ForeignKey('empresa.id_empresa'), nullable=False)
    identificador = db.Column(db.String(50), nullable=False)
    tipo_carburante = db.Column(db.String(20), nullable=False)
    capacidad_maxima = db.Column(db.Float, nullable=False)
    stock_actual = db.Column(db.Float, nullable=False, default=0)
    stock_minimo = db.Column(db.Float, nullable=False)

    ingresos = db.relationship('IngresoTanque', backref='tanque', lazy=True)
    ventas = db.relationship('VentaSalida', backref='tanque', lazy=True)

class Cliente(db.Model):
    __tablename__ = 'cliente'
    id_cliente = db.Column(db.Integer, primary_key=True)
    ci_nit = db.Column(db.String(20), nullable=False, unique=True)
    nombre_razon_social = db.Column(db.String(100), nullable=False)
    placa_vehiculo = db.Column(db.String(20), nullable=False, unique=True)
    tipo_cliente = db.Column(db.String(50), nullable=False)
    estado = db.Column(db.String(20), nullable=False, default='Activo')

    ventas = db.relationship('VentaSalida', backref='cliente', lazy=True)

class IngresoTanque(db.Model):
    __tablename__ = 'ingreso_tanque'
    id_ingreso = db.Column(db.Integer, primary_key=True)
    id_tanque = db.Column(db.Integer, db.ForeignKey('tanque.id_tanque'), nullable=False)
    litros_ingresados = db.Column(db.Float, nullable=False)
    numero_factura = db.Column(db.String(50), nullable=False)
    proveedor = db.Column(db.String(100), nullable=False)
    fecha_hora = db.Column(db.DateTime, default=datetime.utcnow)

class VentaSalida(db.Model):
    __tablename__ = 'venta_salida'
    id_venta = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey('cliente.id_cliente'), nullable=False)
    id_tanque = db.Column(db.Integer, db.ForeignKey('tanque.id_tanque'), nullable=False)
    litros_solicitados = db.Column(db.Float, nullable=False)
    litros_autorizados = db.Column(db.Float, nullable=False)
    promedio_semanal = db.Column(db.Float, nullable=False)
    limite_permitido = db.Column(db.Float, nullable=False)
    estado_venta = db.Column(db.String(20), nullable=False)
    mensaje_validacion = db.Column(db.String(255))
    fecha_hora = db.Column(db.DateTime, default=datetime.utcnow)
