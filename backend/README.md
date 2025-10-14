# 🕐 Clock App Backend

Backend API para aplicación de reloj digital implementando **Listas Circulares Dobles** como estructura de datos principal.

## 📋 Características

- ⏰ **Alarmas**: Gestión completa de alarmas con repetición por días (Lista Circular Doble)
- ⏱️ **Cronómetro**: Control de tiempo y registro de vueltas (Lista Circular Doble)
- 🌍 **Zonas Horarias**: Gestión de zonas horarias favoritas con WorldTimeAPI (Lista Circular Doble)
- ⚙️ **Configuración**: Formato de hora, sonidos y volumen

## 🏗️ Estructura de Datos

El proyecto implementa **Listas Circulares Dobles** manualmente para:
- **Alarmas**: Ordenadas por hora con navegación circular
- **Laps**: Último agregado primero con navegación bidireccional
- **Zonas Horarias Favoritas**: Orden personalizado con navegación circular

### ¿Por qué Listas Circulares Dobles?

- **Circular**: Después del último elemento se vuelve al primero automáticamente
- **Doble**: Navegación en ambas direcciones (prev/next)
- **Eficiente**: Inserción y eliminación en O(1) cuando se tiene referencia al nodo

## 🚀 Instalación

### Prerrequisitos

- Python 3.10 o superior
- pip (gestor de paquetes de Python)

### Pasos

1. **Navegar al directorio del backend**
```bash
cd backend
```

2. **Crear entorno virtual**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus configuraciones si es necesario
```

5. **Ejecutar la aplicación**
```bash
# Opción 1: Con uvicorn directamente
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Opción 2: Ejecutar el archivo main.py
python -m app.main
```

6. **Acceder a la documentación**
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc
- API Base: http://localhost:8000

## 📁 Estructura del Proyecto

```
backend/
│
├── app/
│   ├── __init__.py
│   ├── main.py                    # Punto de entrada FastAPI
│   ├── config.py                  # Configuración
│   │
│   ├── data_structures/           # 🔴 Listas Circulares Dobles
│   │   ├── __init__.py
│   │   ├── node.py                # Clase Node
│   │   └── circular_doubly_linked_list.py  # Lista circular doble
│   │
│   ├── models/                    # Modelos Pydantic
│   │   ├── __init__.py
│   │   ├── alarm.py               # Modelo Alarma
│   │   ├── lap.py                 # Modelo Lap
│   │   ├── timezone.py            # Modelo Zona Horaria
│   │   └── settings.py            # Modelo Configuración
│   │
│   ├── services/                  # Lógica de negocio (usa listas circulares)
│   │   ├── __init__.py
│   │   ├── alarm_service.py       # Gestión de alarmas
│   │   ├── stopwatch_service.py   # Gestión de cronómetro
│   │   ├── timezone_service.py    # Gestión de zonas horarias
│   │   └── settings_service.py    # Gestión de configuración
│   │
│   ├── routers/                   # Endpoints API
│   │   ├── __init__.py
│   │   ├── alarms.py              # /api/alarms
│   │   ├── stopwatch.py           # /api/stopwatch
│   │   ├── timezones.py           # /api/timezones
│   │   └── settings.py            # /api/settings
│   │
│   ├── database/                  # Persistencia
│   │   ├── __init__.py
│   │   └── json_db.py             # Guardar/cargar JSON
│   │
│   └── utils/                     # Utilidades
│       ├── __init__.py
│       └── time_utils.py          # Funciones de tiempo
│
├── data/                          # 🔴 Datos persistidos (JSON)
│   ├── alarms.json
│   ├── laps.json
│   ├── timezones.json
│   └── settings.json
│
├── requirements.txt               # Dependencias Python
├── .env                           # Variables de entorno
├── .env.example                   # Ejemplo de .env
└── README.md                      # Este archivo
```

## 🔌 API Endpoints

### Alarmas (`/api/alarms`)

- `POST /` - Crear alarma
- `GET /` - Listar todas las alarmas
- `GET /{alarm_id}` - Obtener alarma específica
- `PUT /{alarm_id}` - Actualizar alarma
- `DELETE /{alarm_id}` - Eliminar alarma
- `PATCH /{alarm_id}/toggle` - Activar/desactivar alarma
- `GET /next` - Obtener próxima alarma que sonará
- `GET /{alarm_id}/navigate?direction=next|prev` - Navegar circularmente

### Cronómetro (`/api/stopwatch`)

- `POST /laps` - Agregar lap
- `GET /laps` - Listar todos los laps
- `DELETE /laps` - Limpiar todos los laps
- `GET /laps/fastest` - Lap más rápido
- `GET /laps/slowest` - Lap más lento
- `GET /laps/statistics` - Estadísticas completas
- `GET /laps/{lap_number}/navigate?direction=next|prev` - Navegar entre laps

### Zonas Horarias (`/api/timezones`)

- `GET /` - Listar zonas horarias disponibles
- `GET /search?query=...` - Buscar zonas
- `GET /favorites` - Listar favoritos
- `POST /favorites` - Agregar a favoritos
- `DELETE /favorites/{timezone_id}` - Quitar de favoritos
- `PUT /favorites/reorder` - Reordenar favorito
- `GET /favorites/{timezone_id}/navigate?direction=next|prev` - Navegar entre favoritos
- `GET /{timezone_id}/current` - Obtener hora actual en zona

### Configuración (`/api/settings`)

- `GET /` - Obtener configuración
- `PUT /` - Actualizar configuración
- `POST /reset` - Restaurar valores por defecto
- `PATCH /volume` - Actualizar volumen
- `POST /volume/toggle-mute` - Mutear/desmutear

## 🧪 Probar la Implementación

### 1. Probar Estructura de Datos

```bash
# Probar Node
python -m app.data_structures.node

# Probar Lista Circular Doble
python -m app.data_structures.circular_doubly_linked_list
```

### 2. Probar Modelos

```bash
python -m app.models.alarm
python -m app.models.lap
python -m app.models.timezone
python -m app.models.settings
```

### 3. Probar Servicios

```bash
python -m app.services.alarm_service
python -m app.services.stopwatch_service
python -m app.services.timezone_service
python -m app.services.settings_service
```

### 4. Probar API

```bash
# Iniciar servidor
uvicorn app.main:app --reload

# Acceder a documentación interactiva
# http://localhost:8000/api/docs
```

## 🌍 Integración con WorldTimeAPI

El servicio de zonas horarias utiliza **WorldTimeAPI** para obtener datos reales:

- **URL**: http://worldtimeapi.org/api
- **Gratuito**: Sin API key necesaria
- **Cache**: 24 horas para optimizar rendimiento
- **Fallback**: Conjunto básico de 15 ciudades si falla la API

## 💾 Persistencia de Datos

Los datos se guardan automáticamente en archivos JSON:

- `data/alarms.json` - Alarmas
- `data/laps.json` - Laps del cronómetro
- `data/timezones.json` - Zonas horarias favoritas
- `data/settings.json` - Configuración del usuario

## 🎓 Conceptos de Estructuras de Datos

### Lista Circular Doble - Operaciones

```python
# Insertar al inicio: O(1)
lista.insert_at_beginning(data)

# Insertar al final: O(1)
lista.insert_at_end(data)

# Insertar ordenado: O(n)
lista.insert_sorted(data, key_func)

# Eliminar: O(n) búsqueda + O(1) eliminación
lista.delete(data)

# Navegar circular: O(1)
lista.get_next(current_data)
lista.get_previous(current_data)

# Obtener todos: O(n)
lista.get_all()
```

### Ventajas de la Lista Circular Doble

1. **Navegación Circular**: Ideal para interfaces tipo carrusel
2. **Bidireccional**: Navegar adelante y atrás eficientemente
3. **Sin Límites**: No hay "final" de la lista
4. **Flexible**: Inserción y eliminación eficientes

## 🔧 Configuración

### Variables de Entorno (`.env`)

```env
# Application Settings
APP_NAME="Clock App API"
DEBUG=True
ENVIRONMENT="development"

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:3000

# Data Storage
DATA_DIR=./data

# Server Configuration
HOST=0.0.0.0
PORT=8000
RELOAD=True
```

## 📚 Dependencias Principales

- **FastAPI**: Framework web moderno y rápido
- **Uvicorn**: Servidor ASGI
- **Pydantic**: Validación de datos
- **Requests**: HTTP requests para WorldTimeAPI

## 🐛 Debugging

### Ver Logs

```bash
# Los logs se muestran en consola
# Para más detalle, cambiar DEBUG=True en .env
```

### Verificar Archivos JSON

```bash
# Ver contenido de archivos de datos
cat data/alarms.json
cat data/laps.json
cat data/timezones.json
cat data/settings.json
```

## 🚀 Producción

Para producción, usar:

```bash
# Instalar gunicorn
pip install gunicorn

# Ejecutar con gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

## 📝 Notas Importantes

1. **Listas Circulares**: Todo el proyecto usa listas circulares dobles implementadas manualmente
2. **Sin ORM**: Persistencia simple con JSON (no SQL/MongoDB)
3. **API Externa**: WorldTimeAPI para zonas horarias reales
4. **CORS**: Habilitado para localhost:3000 (frontend Next.js)

## 🤝 Contribuir

Este es un proyecto académico de Estructuras de Datos. Las contribuciones son bienvenidas siguiendo estas guías:

1. Mantener el uso de listas circulares dobles
2. Documentar todo el código con docstrings
3. Incluir type hints en Python
4. Agregar ejemplos en los archivos

## 📄 Licencia

Proyecto académico - Universidad [Tu Universidad]

## 👨‍💻 Autor

[Tu Nombre] - Proyecto de Estructuras de Datos

---

**¿Preguntas?** Revisa la documentación en `/api/docs` o contacta al autor.