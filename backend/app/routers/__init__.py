"""
Módulo de Routers - Endpoints de la API.
Contiene todos los routers de FastAPI para los diferentes módulos.
"""

from app.routers import alarms, stopwatch, timezones, settings

__all__ = [
    'alarms',
    'stopwatch',
    'timezones',
    'settings',
]

__version__ = '1.0.0'