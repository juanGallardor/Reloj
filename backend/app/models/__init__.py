"""
Módulo de Modelos Pydantic.
Contiene todos los modelos de datos para validación y serialización.
"""

# Modelos de Alarma
from app.models.alarm import (
    Alarm,
    AlarmCreate,
    AlarmUpdate,
    VALID_DAYS,
)

# Modelos de Lap
from app.models.lap import (
    Lap,
    LapCreate,
    LapStatistics,
)

# Modelos de Zona Horaria
from app.models.timezone import (
    Timezone,
    TimezoneCreate,
    FavoriteTimezone,
    generate_timezone_id,
)

# Modelos de Configuración
from app.models.settings import (
    Settings,
    SettingsUpdate,
    SettingsResponse,
    AVAILABLE_SOUNDS,
    AVAILABLE_THEMES,
    TIME_FORMATS,
)


__all__ = [
    # Alarmas
    'Alarm',
    'AlarmCreate',
    'AlarmUpdate',
    'VALID_DAYS',
    
    # Laps
    'Lap',
    'LapCreate',
    'LapStatistics',
    
    # Zonas Horarias
    'Timezone',
    'TimezoneCreate',
    'FavoriteTimezone',
    'generate_timezone_id',
    
    # Configuración
    'Settings',
    'SettingsUpdate',
    'SettingsResponse',
    'AVAILABLE_SOUNDS',
    'AVAILABLE_THEMES',
    'TIME_FORMATS',
]

__version__ = '1.0.0'