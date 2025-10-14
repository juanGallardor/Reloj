# 🕐 Clock App - Aplicación de Reloj Digital

> **Proyecto Académico de Estructuras de Datos**  
> Implementación completa de **Listas Circulares Dobles** en una aplicación moderna de reloj con alarmas, cronómetro y zonas horarias.

---

## 📋 Tabla de Contenidos

- [Descripción](#-descripción)
- [Características Principales](#-características-principales)
- [Stack Tecnológico](#-stack-tecnológico)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Requisitos Previos](#-requisitos-previos)
- [Instalación](#-instalación)
- [Ejecución del Proyecto](#-ejecución-del-proyecto)
- [Estructura de Datos](#-estructura-de-datos)
- [API Endpoints](#-api-endpoints)
- [Arquitectura Frontend](#-arquitectura-frontend)
- [Características Técnicas](#-características-técnicas)
- [Contribuir](#-contribuir)
- [Autor](#-autor)

---

## 🎯 Descripción

**Clock App** es una aplicación web completa de reloj digital desarrollada como proyecto académico para demostrar la implementación y uso de **Listas Circulares Dobles** como estructura de datos principal.

La aplicación combina un **backend robusto en Python/FastAPI** con un **frontend moderno en Next.js 15**, ofreciendo funcionalidades avanzadas de gestión de tiempo con una interfaz de usuario atractiva y responsiva.

### 🎓 Objetivo Académico

Demostrar el uso práctico de Listas Circulares Dobles en un proyecto real, implementando:
- Navegación circular entre elementos
- Inserción y eliminación eficiente
- Ordenamiento de datos
- Persistencia de información

---

## ✨ Características Principales

### ⏰ **Alarmas Inteligentes**
- ✅ Crear, editar y eliminar alarmas
- ✅ Activar/desactivar alarmas
- ✅ Configurar repetición por días de la semana
- ✅ Posponer alarmas (snooze) por 5 minutos
- ✅ Notificaciones del navegador
- ✅ Múltiples sonidos de alarma personalizables
- ✅ Control de volumen independiente
- ✅ Sincronización con zonas horarias

### ⏱️ **Cronómetro Profesional**
- ✅ Iniciar, pausar y reiniciar
- ✅ Guardar vueltas (laps) ilimitadas
- ✅ Estadísticas: lap más rápido/lento, promedio
- ✅ Persistencia del estado (continúa después de recargar)
- ✅ Navegación entre laps registrados
- ✅ Precisión de milisegundos

### 🌍 **Zonas Horarias**
- ✅ +200 zonas horarias disponibles
- ✅ Gestión de favoritos
- ✅ Búsqueda por país y ciudad
- ✅ Visualización de hora actual en tiempo real
- ✅ Integración con WorldTimeAPI
- ✅ Sincronización automática con alarmas

### ⚙️ **Configuración**
- ✅ Formato de hora (12h/24h)
- ✅ 6 sonidos de alarma diferentes
- ✅ Control de volumen con slider
- ✅ Tema oscuro con efectos neón cyan
- ✅ Persistencia de configuración

---

## 🛠️ Stack Tecnológico

### Backend

| Tecnología | Versión | Uso |
|-----------|---------|-----|
| **Python** | 3.10+ | Lenguaje principal |
| **FastAPI** | 0.104.1 | Framework web moderno |
| **Uvicorn** | 0.24.0 | Servidor ASGI |
| **Pydantic** | 2.5.0 | Validación de datos |
| **Requests** | 2.31.0 | HTTP client para WorldTimeAPI |

### Frontend

| Tecnología | Versión | Uso |
|-----------|---------|-----|
| **Next.js** | 15 | Framework React |
| **React** | 19 | Biblioteca UI |
| **TypeScript** | 5.x | Tipado estático |
| **Tailwind CSS** | 4.x | Estilos utility-first |
| **Framer Motion** | 11.x | Animaciones fluidas |
| **Lucide React** | Latest | Sistema de iconos |

### Estructura de Datos

- **Listas Circulares Dobles** (implementación manual)
- **Persistencia en JSON** (sin base de datos)
- **Context API de React** (gestión de estado global)

---

## 📁 Estructura del Proyecto

```
proyecto-reloj/
│
├── backend/                          # 🐍 Backend Python + FastAPI
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # Punto de entrada FastAPI
│   │   ├── config.py                 # Configuración
│   │   │
│   │   ├── data_structures/          # 🔴 LISTAS CIRCULARES DOBLES
│   │   │   ├── __init__.py
│   │   │   ├── node.py               # Clase Node
│   │   │   └── circular_doubly_linked_list.py
│   │   │
│   │   ├── models/                   # Modelos Pydantic
│   │   │   ├── __init__.py
│   │   │   ├── alarm.py
│   │   │   ├── lap.py
│   │   │   ├── timezone.py
│   │   │   └── settings.py
│   │   │
│   │   ├── services/                 # Lógica de negocio
│   │   │   ├── __init__.py
│   │   │   ├── alarm_service.py
│   │   │   ├── stopwatch_service.py
│   │   │   ├── timezone_service.py
│   │   │   └── settings_service.py
│   │   │
│   │   ├── routers/                  # Endpoints API REST
│   │   │   ├── __init__.py
│   │   │   ├── alarms.py
│   │   │   ├── stopwatch.py
│   │   │   ├── timezones.py
│   │   │   └── settings.py
│   │   │
│   │   ├── database/                 # Persistencia JSON
│   │   │   ├── __init__.py
│   │   │   └── json_db.py
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── time_utils.py
│   │
│   ├── data/                         # 🗄️ Datos persistidos
│   │   ├── alarms.json
│   │   ├── laps.json
│   │   ├── timezones.json
│   │   └── settings.json
│   │
│   ├── requirements.txt
│   ├── .env
│   └── README.md
│
├── frontend/                         # ⚛️ Frontend Next.js + React
│   ├── app/
│   │   ├── globals.css
│   │   ├── layout.tsx                # Layout principal con Providers
│   │   └── page.tsx                  # Página principal
│   │
│   ├── components/                   # 🎨 Componentes React
│   │   ├── alarms.tsx                # Gestión de alarmas
│   │   ├── stopwatch.tsx             # Cronómetro
│   │   ├── timezone-selector.tsx     # Selector de zonas horarias
│   │   ├── settings.tsx              # Configuración
│   │   ├── alarm-notification.tsx    # 🔔 Modal de alarma sonando
│   │   ├── analog-clock.tsx          # Reloj analógico
│   │   ├── clock-navbar.tsx          # Navegación principal
│   │   ├── custom-dropdown.tsx       # Dropdown personalizado
│   │   ├── theme-provider.tsx
│   │   └── theme-toggle.tsx
│   │
│   ├── contexts/                     # 🔄 Estado Global (Context API)
│   │   ├── alarm-context.tsx         # 🔔 Gestión global de alarmas
│   │   └── stopwatch-context.tsx     # ⏱️ Gestión global de cronómetro
│   │
│   ├── lib/                          # 📚 Utilidades y API Client
│   │   ├── api.ts                    # Cliente HTTP para backend
│   │   └── timezone-map.ts           # Mapeo de zonas horarias
│   │
│   ├── public/
│   │   ├── images/
│   │   │   ├── apple-watch.png
│   │   │   ├── clock-face-clean.png
│   │   │   └── world-map.png
│   │   │
│   │   └── sounds/                   # 🔊 Sonidos de alarma
│   │       └── alarms/
│   │           ├── classic.mp3
│   │           ├── gentle.mp3
│   │           ├── radar.mp3
│   │           ├── beacon.mp3
│   │           ├── chimes.mp3
│   │           └── digital.mp3
│   │
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── postcss.config.mjs
│   └── next.config.js
│
└── README.md                         # 📖 Este archivo
```

---

## 📦 Requisitos Previos

Asegúrate de tener instalado:

- **Python 3.10 o superior** ([Descargar Python](https://www.python.org/downloads/))
- **Node.js 18.17 o superior** ([Descargar Node.js](https://nodejs.org/))
- **npm o pnpm** (incluido con Node.js)
- **Git** (opcional, para clonar el repositorio)

---

## 🚀 Instalación

### 1️⃣ Clonar el Repositorio (Opcional)

```bash
git clone https://github.com/tu-usuario/clock-app.git
cd clock-app
```

### 2️⃣ Configurar Backend

```bash
# Navegar al directorio del backend
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Verificar instalación
python -c "import fastapi; print('✅ FastAPI instalado correctamente')"
```

### 3️⃣ Configurar Frontend

```bash
# Desde la raíz del proyecto
cd frontend

# Instalar dependencias
npm install
# o con pnpm:
pnpm install

# Verificar instalación
npm run build
```

### 4️⃣ Variables de Entorno

El backend ya incluye un archivo `.env` con la configuración por defecto:

```env
# backend/.env
APP_NAME=Clock App API
DEBUG=true
ENVIRONMENT=development
FRONTEND_URL=http://localhost:3000
HOST=0.0.0.0
PORT=8000
RELOAD=true
DATA_DIR=data
NEXT_PUBLIC_API_URL=http://localhost:8000
LOG_LEVEL=INFO
ENABLE_DOCS=true
```

Para el frontend, crea un archivo `.env.local` si necesitas personalizar:

```env
# frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## ▶️ Ejecución del Proyecto

### Opción 1: Ejecutar Backend y Frontend por Separado

#### **Backend (Terminal 1)**

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

✅ **Backend corriendo en:** http://localhost:8000  
📚 **Documentación API Swagger:** http://localhost:8000/api/docs  
📖 **Documentación ReDoc:** http://localhost:8000/api/redoc

#### **Frontend (Terminal 2)**

```bash
cd frontend
npm run dev
# o
pnpm dev
```

✅ **Frontend corriendo en:** http://localhost:3000

---

### Opción 2: Script de Inicio Automático

#### **Linux/Mac** (`start.sh`):

```bash
#!/bin/bash

# Iniciar backend en background
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Iniciar frontend
cd ../frontend
npm run dev

# Cleanup al cerrar
trap "kill $BACKEND_PID" EXIT
```

Dar permisos y ejecutar:
```bash
chmod +x start.sh
./start.sh
```

#### **Windows** (`start.bat`):

```batch
@echo off
start cmd /k "cd backend && venv\Scripts\activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
timeout /t 3
start cmd /k "cd frontend && npm run dev"
```

Ejecutar:
```cmd
start.bat
```

---

## 🔗 Estructura de Datos - Listas Circulares Dobles

### ¿Qué es una Lista Circular Doble?

Es una estructura de datos donde:
- Cada **nodo** tiene referencias a `prev` y `next`
- El **último nodo** apunta al primero (circular)
- Se puede **navegar en ambas direcciones**

```python
class Node:
    def __init__(self, data):
        self.data = data
        self.prev = None  # ⬅️ Nodo anterior
        self.next = None  # ➡️ Nodo siguiente

# Ejemplo visual:
# A ↔ B ↔ C ↔ A (circular)
#     ↑_______|
```

### Uso en el Proyecto

| Funcionalidad | Uso de Lista Circular Doble |
|--------------|----------------------------|
| **Alarmas** | Ordenadas por hora, navegación circular entre alarmas activas |
| **Laps del Cronómetro** | Último lap agregado primero, navegación bidireccional entre registros |
| **Zonas Horarias Favoritas** | Orden personalizado con navegación circular |

### Operaciones Principales

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
siguiente = lista.get_next(current_data)
anterior = lista.get_previous(current_data)

# Obtener todos: O(n)
elementos = lista.get_all()
```

### Ventajas de la Lista Circular Doble

1. **Navegación Circular**: Ideal para interfaces tipo carrusel o rotación infinita
2. **Bidireccional**: Navegar adelante y atrás eficientemente
3. **Sin Límites**: No hay "final" de la lista, siempre puedes continuar
4. **Flexible**: Inserción y eliminación eficientes en cualquier posición

---

## 🔌 API Endpoints

### 📍 Base URL: `http://localhost:8000/api`

### 🔔 Alarmas (`/alarms`)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/` | Crear nueva alarma |
| `GET` | `/` | Listar todas las alarmas |
| `GET` | `/{alarm_id}` | Obtener alarma específica |
| `PUT` | `/{alarm_id}` | Actualizar alarma |
| `DELETE` | `/{alarm_id}` | Eliminar alarma |
| `PATCH` | `/{alarm_id}/toggle` | Activar/desactivar alarma |
| `GET` | `/next` | Obtener próxima alarma que sonará |
| `GET` | `/active` | Listar alarmas activas |
| `GET` | `/{alarm_id}/navigate?direction=next\|prev` | Navegar circularmente |

#### Ejemplo - Crear Alarma:

```json
POST /api/alarms
{
  "time": "07:30",
  "label": "Despertar",
  "enabled": true,
  "days": ["Lun", "Mar", "Mié", "Jue", "Vie"]
}
```

#### Ejemplo - Respuesta:

```json
{
  "id": 1,
  "time": "07:30",
  "label": "Despertar",
  "enabled": true,
  "days": ["Lun", "Mar", "Mié", "Jue", "Vie"],
  "created_at": "2025-10-14T10:30:00"
}
```

---

### ⏱️ Cronómetro (`/stopwatch`)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/laps` | Agregar nuevo lap |
| `GET` | `/laps` | Listar todos los laps |
| `GET` | `/laps/{lap_id}` | Obtener lap específico |
| `DELETE` | `/laps/{lap_id}` | Eliminar lap específico |
| `DELETE` | `/laps` | Limpiar todos los laps |
| `GET` | `/laps/fastest` | Obtener lap más rápido |
| `GET` | `/laps/slowest` | Obtener lap más lento |
| `GET` | `/laps/statistics` | Obtener estadísticas completas |
| `GET` | `/laps/{lap_number}/navigate?direction=next\|prev` | Navegar entre laps |
| `GET` | `/laps/first` | Obtener primer lap |
| `GET` | `/laps/last` | Obtener último lap |

#### Ejemplo - Agregar Lap:

```json
POST /api/stopwatch/laps
{
  "lap_time": 45.23,
  "total_time": 135.67
}
```

#### Ejemplo - Estadísticas:

```json
GET /api/stopwatch/laps/statistics

{
  "total_laps": 5,
  "fastest_lap": { "id": 3, "lap_time": 42.10, ... },
  "slowest_lap": { "id": 2, "lap_time": 48.90, ... },
  "average_lap_time": 45.23,
  "total_elapsed_time": 226.15
}
```

---

### 🌍 Zonas Horarias (`/timezones`)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/` | Listar todas las zonas disponibles |
| `GET` | `/search?query=...` | Buscar por país/ciudad |
| `GET` | `/{timezone_id}` | Obtener zona específica |
| `GET` | `/countries` | Listar países disponibles |
| `GET` | `/by-country/{country}` | Obtener zonas por país |
| `GET` | `/favorites` | Listar favoritos |
| `POST` | `/favorites` | Agregar a favoritos |
| `DELETE` | `/favorites/{timezone_id}` | Quitar de favoritos |
| `PUT` | `/favorites/reorder` | Reordenar favorito |
| `GET` | `/favorites/{timezone_id}/navigate?direction=next\|prev` | Navegar entre favoritos |
| `GET` | `/{timezone_id}/current` | Obtener hora actual en zona |
| `GET` | `/favorites/check/{timezone_id}` | Verificar si es favorito |
| `POST` | `/refresh` | Refrescar zonas desde WorldTimeAPI |

#### Ejemplo - Agregar Favorito:

```json
POST /api/timezones/favorites
{
  "timezone_id": "japon-tokyo"
}
```

#### Ejemplo - Hora Actual:

```json
GET /api/timezones/japon-tokyo/current

{
  "timezone_id": "japon-tokyo",
  "city": "Tokyo",
  "country": "Japón",
  "offset": "UTC+9",
  "utc_time": "2025-10-14T10:30:00Z",
  "current_time": "19:30:00",
  "current_date": "2025-10-14",
  "day_of_week": "Martes",
  "full_datetime": "2025-10-14T19:30:00"
}
```

---

### ⚙️ Configuración (`/settings`)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/` | Obtener configuración actual |
| `PUT` | `/` | Actualizar configuración |
| `POST` | `/reset` | Restaurar valores por defecto |
| `PATCH` | `/time-format` | Actualizar formato de hora |
| `PATCH` | `/alarm-sound` | Actualizar sonido de alarma |
| `PATCH` | `/volume` | Actualizar volumen |
| `PATCH` | `/theme` | Actualizar tema |
| `POST` | `/volume/toggle-mute` | Mutear/desmutear |
| `PATCH` | `/volume/increase` | Aumentar volumen |
| `PATCH` | `/volume/decrease` | Disminuir volumen |

#### Ejemplo - Actualizar Configuración:

```json
PUT /api/settings
{
  "time_format": "24h",
  "alarm_sound": "gentle",
  "alarm_volume": 75,
  "theme": "dark"
}
```

#### Ejemplo - Respuesta Configuración:

```json
GET /api/settings

{
  "time_format": "24h",
  "alarm_sound": "gentle",
  "alarm_volume": 75,
  "theme": "dark",
  "available_sounds": [
    "classic", "gentle", "radar", 
    "beacon", "chimes", "digital"
  ],
  "available_themes": ["light", "dark", "auto"],
  "available_time_formats": ["12h", "24h"]
}
```

---

## ⚛️ Arquitectura Frontend

### Context API - Estado Global

El frontend utiliza **React Context API** para manejar estado global en dos contextos principales:

#### 🔔 `AlarmContext` (`contexts/alarm-context.tsx`)

Gestiona el estado global de las alarmas:

```typescript
interface AlarmContextType {
  ringingAlarm: Alarm | null;          // Alarma actualmente sonando
  snoozeAlarm: () => Promise<void>;    // Posponer 5 minutos
  dismissAlarm: () => void;            // Desactivar alarma
  isRinging: boolean;                  // Estado de alarma
  setActiveTimezone: (tz: FavoriteTimezone | null) => void;
}
```

**Características:**
- ✅ Verifica alarmas cada 10 segundos
- ✅ Sincroniza con zona horaria activa
- ✅ Reproduce sonidos de alarma
- ✅ Maneja notificaciones del navegador
- ✅ Sistema de snooze inteligente

#### ⏱️ `StopwatchContext` (`contexts/stopwatch-context.tsx`)

Gestiona el cronómetro:

```typescript
interface StopwatchContextType {
  time: number;                        // Tiempo transcurrido (ms)
  isRunning: boolean;                  // Estado del cronómetro
  laps: Lap[];                         // Lista de laps registrados
  startStop: () => void;               // Iniciar/pausar
  reset: () => void;                   // Reiniciar
  addLap: () => void;                  // Agregar lap
  formatTime: (ms: number) => {...};   // Formatear tiempo
}
```

**Características:**
- ✅ Persistencia en `localStorage`
- ✅ Sincronización con backend
- ✅ Precisión de milisegundos
- ✅ Continúa después de recargar página

---

### Componentes Principales

#### 📱 `page.tsx` - Página Principal

Componente raíz que:
- Maneja navegación entre secciones
- Gestiona zona horaria activa
- Renderiza componentes según sección activa
- Sincroniza timezone con alarmas

#### 🔔 `alarm-notification.tsx` - Modal de Alarma

Modal full-screen que aparece cuando suena una alarma:
- Animaciones con Framer Motion
- Soporte de teclado (ESC/ESPACIO)
- Botones de Snooze y Desactivar
- Efectos visuales de neón cyan

#### 🎨 `alarms.tsx` - Gestión de Alarmas

CRUD completo de alarmas:
- Crear con hora, label y días
- Editar inline
- Toggle activar/desactivar
- Selector de días de la semana

#### ⏱️ `stopwatch.tsx` - Cronómetro

Interfaz del cronómetro:
- Display de tiempo con formato HH:MM:SS.MS
- Botones Start/Stop, Lap, Reset
- Lista de laps con estadísticas

#### 🌍 `timezone-selector.tsx` - Selector de Zonas

Gestión de zonas horarias:
- Dropdown de países y ciudades
- Tarjetas de favoritos
- Hora en tiempo real
- Sistema de activación

---

### Cliente API (`lib/api.ts`)

Cliente TypeScript para comunicación con el backend:

```typescript
// Ejemplo de uso
import { alarmsAPI } from '@/lib/api';

// Crear alarma
const newAlarm = await alarmsAPI.create({
  time: "08:00",
  label: "Despertar",
  enabled: true,
  days: ["Lun", "Mar"]
});

// Listar alarmas
const alarms = await alarmsAPI.getAll();

// Toggle alarma
const updated = await alarmsAPI.toggle(1);
```

**Características:**
- ✅ Tipado estricto con TypeScript
- ✅ Manejo de errores centralizado
- ✅ Logging de requests/responses
- ✅ Funciones helper para todas las rutas

---

## 🎨 Características Técnicas

### Backend

- **Arquitectura en Capas**: Routers → Services → Data Structures → Persistence
- **Validación con Pydantic**: Modelos tipados y validación automática
- **CORS Configurado**: Permite requests desde `localhost:3000`
- **Documentación Automática**: Swagger UI y ReDoc
- **Persistencia JSON**: Sistema simple sin dependencias de DB
- **WorldTimeAPI Integration**: Datos de zonas horarias en tiempo real

### Frontend

- **Server Components**: Next.js 15 App Router
- **Client Components**: Interactividad con `"use client"`
- **Tailwind CSS v4**: Estilos utility-first modernos
- **Framer Motion**: Animaciones fluidas y profesionales
- **TypeScript Estricto**: Type safety en todo el código
- **Custom Hooks**: Lógica reutilizable
- **Responsive Design**: Funciona en móvil, tablet y desktop

### Características de UX/UI

- 🎨 **Tema Neón Cyan**: Paleta de colores futurista
- ✨ **Animaciones Suaves**: Transiciones con Framer Motion
- 🌓 **Modo Oscuro**: Predeterminado con opción de cambio
- 📱 **Responsive**: Adaptado a todos los tamaños de pantalla
- ⌨️ **Soporte de Teclado**: Atajos para acciones principales
- 🔔 **Notificaciones**: Sistema de notificaciones del navegador
- 💾 **Persistencia**: Estado guardado automáticamente

---

## 🧪 Testing y Debugging

### Probar Backend

```bash
# Activar entorno virtual
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate

# Probar estructura de datos
python -m app.data_structures.circular_doubly_linked_list

# Probar servicios
python -m app.services.alarm_service
python -m app.services.stopwatch_service

# Probar API manualmente
# Acceder a: http://localhost:8000/api/docs
```

### Logs del Backend

Los logs se muestran en la terminal donde ejecutaste `uvicorn`:

```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     POST /api/alarms - 201 Created
INFO:     GET /api/timezones - 200 OK
```

### Logs del Frontend

Abre la consola del navegador (F12) para ver:
- ✅ Confirmaciones de operaciones exitosas
- ⚠️ Warnings de validación
- ❌ Errores de API o lógica
- 📊 Información de debugging

---

## 🐛 Solución de Problemas Comunes

### ❌ Backend no inicia

```bash
# Error: No module named 'fastapi'
# Solución:
pip install -r requirements.txt

# Error: Port 8000 already in use
# Solución: Cambiar puerto en .env o matar proceso
lsof -ti:8000 | xargs kill -9  # Mac/Linux
netstat -ano | findstr :8000   # Windows - ver PID y matar
```

### ❌ Frontend no inicia

```bash
# Error: EADDRINUSE :::3000
# Solución: Matar proceso en puerto 3000
npx kill-port 3000

# Error: Module not found
# Solución: Reinstalar dependencias
rm -rf node_modules package-lock.json
npm install
```

### ❌ Las alarmas no suenan

- Verificar que el backend esté corriendo
- Verificar permisos de notificaciones del navegador
- Verificar que el volumen no esté en 0
- Revisar la consola del navegador para errores
- Verificar que los archivos de sonido existan en `/public/sounds/alarms/`

### ❌ Error de CORS

```
Access to fetch at 'http://localhost:8000/api/...' from origin 
'http://localhost:3000' has been blocked by CORS policy
```

**Solución**: Verificar que `FRONTEND_URL=http://localhost:3000` en `backend/.env`

---

## 📚 Recursos y Documentación

### APIs Utilizadas

- **FastAPI**: https://fastapi.tiangolo.com/
- **Next.js**: https://nextjs.org/docs
- **Framer Motion**: https://www.framer.com/motion/
- **WorldTimeAPI**: http://worldtimeapi.org/

### Estructuras de Datos

- Listas Circulares Dobles: [GeeksforGeeks](https://www.geeksforgeeks.org/doubly-circular-linked-list-set-1-introduction-and-insertion/)
- Big O Notation: [BigO Cheat Sheet](https://www.bigocheatsheet.com/)

---

## 🤝 Contribuir

Este es un proyecto académico. Las contribuciones son bienvenidas siguiendo estas guías:

1. **Fork** el repositorio
2. Crea una **rama** para tu feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** tus cambios (`git commit -m 'Add: amazing feature'`)
4. **Push** a la rama (`git push origin feature/AmazingFeature`)
5. Abre un **Pull Request**

### Guías de Contribución

- Mantener el uso de listas circulares dobles
- Documentar código con docstrings (Python) y JSDoc (TypeScript)
- Incluir type hints en Python
- Seguir convenciones de código (PEP 8 para Python)
- Agregar tests si es posible

---

## 📄 Licencia

Este proyecto es académico y está bajo la Licencia MIT.

```
MIT License

Copyright (c) 2025 [Tu Nombre]

Se concede permiso, de forma gratuita, a cualquier persona que obtenga una copia
de este software y archivos de documentación asociados (el "Software"), para usar
el Software sin restricciones, incluyendo sin limitación los derechos de usar,
copiar, modificar, fusionar, publicar, distribuir, sublicenciar y/o vender copias
del Software...
```

---

## 👨‍💻 Autor

**[Tu Nombre]**  
📧 Email: tu-email@ejemplo.com  
🎓 Universidad: [Tu Universidad]  
📚 Curso: Estructuras de Datos  
📅 Año: 2025

---

## 🙏 Agradecimientos

- A los profesores de Estructuras de Datos
- A la comunidad de FastAPI y Next.js
- A WorldTimeAPI por su servicio gratuito
- A todos los que contribuyeron con feedback

---

## 📞 Soporte

Si tienes preguntas o necesitas ayuda:

1. Revisa la [documentación de la API](http://localhost:8000/api/docs)
2. Consulta este README
3. Abre un issue en GitHub
4. Contacta al autor por email

---

## 🎉 Features Futuras (Roadmap)

- [ ] Agregar tests unitarios (pytest + jest)
- [ ] Implementar tema claro/oscuro completo
- [ ] Agregar más sonidos de alarma
- [ ] Exportar/importar configuración
- [ ] Modo "No Molestar"
- [ ] Historial de alarmas activadas
- [ ] Gráficas de estadísticas del cronómetro
- [ ] PWA (Progressive Web App)
- [ ] Soporte offline
- [ ] Integración con Google Calendar

---

<div align="center">

**⭐ Si te gustó este proyecto, dale una estrella en GitHub ⭐**

---

Hecho con ❤️ y ☕ para el curso de Estructuras de Datos

</div>