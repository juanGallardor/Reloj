"""
Clock App API - Backend FastAPI
================================
Aplicación de reloj digital implementando Listas Circulares Dobles.
Punto de entrada principal de la API.
"""

import time
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

# Importar routers
from app.routers.alarms import router as alarms_router
from app.routers.stopwatch import router as stopwatch_router
from app.routers.timezones import router as timezones_router
from app.routers.settings import router as settings_router

# Importar configuración
from app.config import settings as app_settings

# Configurar logging
logging.basicConfig(
    level=logging.INFO if app_settings.DEBUG else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# CREAR INSTANCIA DE FASTAPI
# ============================================================================

app = FastAPI(
    title="Clock App API",
    description="API REST para aplicación de reloj digital con Listas Circulares Dobles",
    version="1.0.0",
    docs_url="/api/docs" if app_settings.DEBUG else None,  # Swagger UI solo en dev
    redoc_url="/api/redoc" if app_settings.DEBUG else None,  # ReDoc solo en dev
)


# ============================================================================
# CONFIGURAR CORS
# ============================================================================

# Orígenes permitidos para CORS
origins = [
    "http://localhost:3000",      # Frontend Next.js en desarrollo
    "http://127.0.0.1:3000",      # Variante de localhost
    app_settings.FRONTEND_URL,     # URL desde configuración
]

# Si estamos en producción, agregar otros orígenes si los hay
if not app_settings.DEBUG:
    # Agregar URLs de producción aquí
    pass

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Permitir todos los headers
    expose_headers=["*"],
)


# ============================================================================
# MIDDLEWARE PARA LOGGING DE REQUESTS
# ============================================================================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware para registrar información de cada request.
    Útil para debugging y monitoreo.
    """
    start_time = time.time()
    
    # Obtener información del request
    client_host = request.client.host if request.client else "unknown"
    method = request.method
    path = request.url.path
    
    # Log del request entrante
    logger.info(f"🔵 {method} {path} - Cliente: {client_host}")
    
    # Procesar el request
    try:
        response = await call_next(request)
        
        # Calcular tiempo de procesamiento
        process_time = time.time() - start_time
        
        # Log del response
        status = response.status_code
        status_emoji = "✅" if status < 400 else "⚠️" if status < 500 else "❌"
        logger.info(
            f"{status_emoji} {method} {path} - Status: {status} - "
            f"Tiempo: {process_time:.3f}s"
        )
        
        # Agregar header con tiempo de procesamiento
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Error procesando {method} {path}: {str(e)}")
        raise


# ============================================================================
# INCLUIR ROUTERS
# ============================================================================

# Router de alarmas
app.include_router(
    alarms_router,
    prefix="/api/alarms",
    tags=["Alarmas"],
)

# Router de cronómetro
app.include_router(
    stopwatch_router,
    prefix="/api/stopwatch",
    tags=["Cronómetro"],
)

# Router de zonas horarias
app.include_router(
    timezones_router,
    prefix="/api/timezones",
    tags=["Zonas Horarias"],
)

# Router de configuración
app.include_router(
    settings_router,
    prefix="/api/settings",
    tags=["Configuración"],
)


# ============================================================================
# ENDPOINTS BÁSICOS
# ============================================================================

@app.get("/", response_class=JSONResponse)
async def root():
    """
    Endpoint raíz - Mensaje de bienvenida.
    """
    return {
        "message": "🕐 Clock App API",
        "version": "1.0.0",
        "description": "API REST con Listas Circulares Dobles",
        "docs": "/api/docs" if app_settings.DEBUG else "Documentación deshabilitada en producción",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/health", response_class=JSONResponse)
async def health_check():
    """
    Health check endpoint - Verifica que la API esté funcionando.
    Útil para monitoreo y balanceadores de carga.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "environment": app_settings.ENVIRONMENT,
        "debug_mode": app_settings.DEBUG,
        "uptime": "operational",
    }


@app.get("/api", response_class=JSONResponse)
async def api_info():
    """
    Información general de la API y endpoints disponibles.
    """
    return {
        "name": "Clock App API",
        "version": "1.0.0",
        "endpoints": {
            "alarms": "/api/alarms",
            "stopwatch": "/api/stopwatch",
            "timezones": "/api/timezones",
            "settings": "/api/settings",
        },
        "data_structure": "Listas Circulares Dobles",
        "documentation": "/api/docs" if app_settings.DEBUG else None,
    }


# ============================================================================
# EVENTOS DE INICIO Y CIERRE
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """
    Evento que se ejecuta al iniciar la aplicación.
    Útil para inicializar conexiones, cargar datos, etc.
    """
    logger.info("=" * 60)
    logger.info("🚀 Iniciando Clock App API")
    logger.info(f"📍 Entorno: {app_settings.ENVIRONMENT}")
    logger.info(f"🛠 Debug Mode: {app_settings.DEBUG}")
    logger.info(f"🌐 Frontend URL: {app_settings.FRONTEND_URL}")
    logger.info(f"💾 Data Directory: {app_settings.DATA_DIR}")
    logger.info("=" * 60)
    
    # Aquí podrías cargar datos desde JSON, inicializar caches, etc.
    # Por ejemplo:
    # await load_initial_data()


@app.on_event("shutdown")
async def shutdown_event():
    """
    Evento que se ejecuta al cerrar la aplicación.
    Útil para guardar datos, cerrar conexiones, etc.
    """
    logger.info("=" * 60)
    logger.info("🛑 Cerrando Clock App API")
    logger.info("💾 Guardando datos...")
    logger.info("=" * 60)
    
    # Aquí podrías guardar datos a JSON, cerrar conexiones, etc.
    # Por ejemplo:
    # await save_all_data()


# ============================================================================
# EJECUTAR CON UVICORN (SOLO PARA DESARROLLO)
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info("⚠️  Ejecutando servidor de desarrollo")
    logger.info("⚠️  NO USAR ESTO EN PRODUCCIÓN")
    logger.info(f"🌐 Servidor corriendo en http://{app_settings.HOST}:{app_settings.PORT}")
    
    uvicorn.run(
        "app.main:app",
        host=app_settings.HOST,
        port=app_settings.PORT,
        reload=app_settings.RELOAD,
        log_level="info" if app_settings.DEBUG else "warning",
    )