import os
from database import db
from models import Empresa, Tanque, Cliente, VentaSalida, IngresoTanque
from datetime import datetime, timedelta
import random

def seed_data():
    # Only seed if no company exists
    if Empresa.query.first() is not None:
        return

    # 1. Empresa
    empresa = Empresa(
        nombre_estacion="ATVA Petrol", 
        nit="123456789", 
        direccion="Av. Principal Nro. 100", 
        ciudad="Sucre", 
        telefono="71168949",
        stock_minimo_global=1000,
        factor_holgura=10, # 10%
        cupo_base_cliente_nuevo=50
    )
    db.session.add(empresa)
    db.session.commit()

    # 2. Tanques
    t1 = Tanque(id_empresa=empresa.id_empresa, identificador="T-01", tipo_carburante="Gasolina Especial", capacidad_maxima=10000, stock_actual=6200, stock_minimo=1200)
    t2 = Tanque(id_empresa=empresa.id_empresa, identificador="T-02", tipo_carburante="Diesel", capacidad_maxima=15000, stock_actual=8400, stock_minimo=1800)
    t3 = Tanque(id_empresa=empresa.id_empresa, identificador="T-03", tipo_carburante="Gasolina Premium", capacidad_maxima=8000, stock_actual=2500, stock_minimo=1000)
    db.session.add_all([t1, t2, t3])
    db.session.commit()

    # 3. Clientes
    clientes_data = [
        ("1111111", "Juan Pérez", "ABC1234", "Particular", "Activo"),
        ("2222222", "Transporte Central", "BUS4567", "Transporte Publico", "Activo"),
        ("3333333", "Carlos Gómez", "XYZ7890", "Particular", "Suspendido"),
        ("4444444", "Logística Express", "TRK0001", "Empresa", "Activo"),
        ("5555555", "María López", "DEF5678", "Particular", "Activo"),
        ("6666666", "Taxi Seguro", "TAX9999", "Transporte Publico", "Activo"),
        ("7777777", "Roberto Carlos", "MNO1111", "Particular", "Activo"),
        ("8888888", "Distribuidora del Sur", "CAM2222", "Empresa", "Activo"),
        ("9999999", "Elena Torres", "LMN3333", "Particular", "Activo"),
        ("1010101", "Juanita Alimaña", "PQR4444", "Particular", "Activo"),
    ]
    clientes = []
    for ci, nombre, placa, tipo, estado in clientes_data:
        c = Cliente(ci_nit=ci, nombre_razon_social=nombre, placa_vehiculo=placa, tipo_cliente=tipo, estado=estado)
        db.session.add(c)
        clientes.append(c)
    db.session.commit()

    # 4. Ingresos
    now = datetime.utcnow()
    for i in range(1, 7):
        tanque = random.choice([t1, t2, t3])
        ingreso = IngresoTanque(
            id_tanque=tanque.id_tanque,
            litros_ingresados=random.randint(1000, 3000),
            numero_factura=f"F-{1000+i}",
            proveedor=f"Proveedor {i}",
            fecha_hora=now - timedelta(days=random.randint(1, 20))
        )
        db.session.add(ingreso)
    db.session.commit()

    # 5. Ventas (últimos 28 días)
    for i in range(15):
        cliente = random.choice(clientes)
        tanque = random.choice([t1, t2, t3])
        litros = random.randint(20, 100)
        estado = random.choice(['Autorizada', 'Limitada', 'Bloqueada'])
        
        venta = VentaSalida(
            id_cliente=cliente.id_cliente,
            id_tanque=tanque.id_tanque,
            litros_solicitados=litros,
            litros_autorizados=litros if estado == 'Autorizada' else (litros - 10 if estado == 'Limitada' else 0),
            promedio_semanal=random.uniform(20.0, 60.0),
            limite_permitido=random.uniform(40.0, 80.0),
            estado_venta=estado,
            mensaje_validacion=f"Venta de prueba {estado}",
            fecha_hora=now - timedelta(days=random.randint(1, 27))
        )
        db.session.add(venta)
    db.session.commit()

if __name__ == "__main__":
    from app import app
    with app.app_context():
        # Cuando se corre directo, recreamos la BD para test
        db.drop_all()
        db.create_all()
        seed_data()
        print("Seed data generado correctamente.")
