# ATVA Petrol - Sistema de Gestión de Inventario y Venta Controlada de Carburantes

**Autor:** [TU NOMBRE COMPLETO]  
**Proyecto Académico - Ingeniería de Software**

## Descripción
ATVA Petrol es una plataforma web centralizada para la gestión de inventario y venta controlada de carburantes en una estación de servicio. Controla tanques de Gasolina y Diésel, registrando ingresos y procesando ventas controladas mediante un algoritmo de cupo dinámico basado en el historial de compra. 

El sistema está diseñado para ser desplegado fácilmente en entornos de producción como Render e incluye autoconfiguración de base de datos.

## Módulos del Sistema
- **Dashboard:** Resumen de métricas, alertas de stock mínimo y últimas ventas.
- **Empresa:** Configuración de la estación y parámetros del algoritmo.
- **Tanques:** Gestión de inventario de carburantes con alertas visuales de stock y nivel de ocupación.
- **Clientes:** Directorio de clientes con buscador, registro rápido y funcionalidad de bloqueo.
- **Ingresos:** Registro de reposición de combustible a los tanques.
- **Venta Controlada:** Módulo principal que autoriza, limita o bloquea la venta. Generación de comprobante para impresión.
- **Reportes:** Historial de ventas, ocupación de tanques y resúmenes.

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
- Gunicorn (para producción)

## Usuario Demo
- **Usuario:** `admin`
- **Contraseña:** `admin123`

---

## Ejecución Local

1. Crear entorno virtual y activarlo:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Ejecutar la aplicación:
   ```bash
   flask run
   ```
   *(Nota: La base de datos y los datos iniciales de prueba se generarán automáticamente al iniciar por primera vez).*

---

## Despliegue en Render

El proyecto está listo para ser desplegado en Render (Web Service).
- **Runtime:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn app:app`

Al iniciar en Render, la base de datos se autoconfigurará creando las tablas y datos demo iniciales de forma automática.
También cuenta con una ruta `/health` para validaciones de estado.

## Enlaces
- **GitHub:** [Enlace a tu repositorio]
- **Render:** [Enlace de tu aplicación desplegada]
