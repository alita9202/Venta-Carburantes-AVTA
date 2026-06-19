import os
from database import db
from app import app
from models import Empresa, Tanque, Cliente, VentaSalida, IngresoTanque

with app.app_context():
    # Eliminar DB y crearla
    db.drop_all()
    db.create_all()

    # 1. Empresa
    empresa = Empresa(
        nombre_estacion="AVTA Petrol", 
        nit="123456789", 
        direccion="Av. Siempre Viva 123", 
        ciudad="Sucre", 
        telefono="77712345",
        stock_minimo_global=1000,
        factor_holgura=15, # 15%
        cupo_base_cliente_nuevo=50
    )
    db.session.add(empresa)
    db.session.commit()

    # 2. Tanques
    t1 = Tanque(id_empresa=empresa.id_empresa, identificador="T-01", tipo_carburante="Gasolina", capacidad_maxima=10000, stock_actual=5000, stock_minimo=1000)
    t2 = Tanque(id_empresa=empresa.id_empresa, identificador="T-02", tipo_carburante="Diesel", capacidad_maxima=15000, stock_actual=7000, stock_minimo=1500)
    db.session.add_all([t1, t2])
    db.session.commit()

    # 3. Clientes
    c1 = Cliente(ci_nit="111111", nombre_razon_social="Juan Pérez", placa_vehiculo="ABC123", tipo_cliente="Particular", estado="Activo")
    c2 = Cliente(ci_nit="222222", nombre_razon_social="Transporte Central", placa_vehiculo="BUS456", tipo_cliente="Transporte Publico", estado="Activo")
    c3 = Cliente(ci_nit="333333", nombre_razon_social="Cliente Suspendido", placa_vehiculo="SUS999", tipo_cliente="Particular", estado="Suspendido")
    db.session.add_all([c1, c2, c3])
    db.session.commit()

    print("Seed generado correctamente!")
