# ATVA Petrol - Sistema de Gestión de Inventario y Venta Controlada de Carburantes

**Autor:** [TU NOMBRE COMPLETO]

## Descripción
ATVA Petrol es una plataforma web centralizada para la gestión de inventario y venta controlada de carburantes en una estación de servicio. Controla tanques de Gasolina y Diésel, registrando ingresos y procesando ventas controladas mediante un algoritmo de cupo dinámico basado en el historial de compra.

## Módulos del Sistema
- **Dashboard:** Resumen de métricas, alertas de stock mínimo y últimas ventas.
- **Empresa:** Configuración de la estación y parámetros del algoritmo.
- **Tanques:** Gestión de inventario de carburantes con alertas visuales de stock.
- **Clientes:** Registro y bloqueo de clientes.
- **Ingresos:** Registro de reposición de combustible a los tanques.
- **Venta Controlada:** Módulo principal que autoriza, limita o bloquea la venta.
- **Reportes:** Historial de ventas, tanques y validaciones.

## Regla de Negocio: Venta Controlada
El algoritmo calcula el **promedio semanal** en base a las compras de los últimos 28 días. 
El **límite permitido** es el promedio semanal más un porcentaje de "factor de holgura" (configurado en Empresa). Si el cliente no tiene historial, se le asigna el "cupo base".
- **Autorizada:** Solicitud <= Límite.
- **Limitada:** Solicitud > Límite. Solo se autoriza la cantidad límite.
- **Bloqueada:** Stock insuficiente o cliente suspendido.

## Tecnologías
- Python Flask
- SQLite (con SQLAlchemy)
- HTML5, Bootstrap 5, CSS personalizado (Jinja2)

## Ejecución Local
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python seed.py
flask run
```

## Despliegue en Render
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn app:app`
