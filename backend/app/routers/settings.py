"""
Router de Configuración - Endpoints API para gestión de configuración.
Maneja las preferencias del usuario para el reloj.
"""

from fastapi import APIRouter, HTTPException, status, Depends

from fastapi import Body
from app.models.settings import Settings, SettingsUpdate, SettingsResponse
from app.services.settings_service import SettingsService


# ============================================================================
# CONFIGURACIÓN DEL ROUTER
# ============================================================================

router = APIRouter(
    responses={
        400: {"description": "Datos inválidos"}
    }
)


# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================

def get_settings_service() -> SettingsService:
    """
    Dependency para obtener instancia del servicio de configuración.
    """
    return SettingsService()


# ============================================================================
# ENDPOINTS - GESTIÓN DE CONFIGURACIÓN
# ============================================================================

@router.get(
    "/",
    response_model=SettingsResponse,
    summary="Obtener configuración",
    description="Obtiene la configuración actual del usuario"
)
async def get_settings(
    service: SettingsService = Depends(get_settings_service)
) -> SettingsResponse:
    """
    Obtiene la configuración actual.
    """
    return service.get_settings_response()


@router.put(
    "/",
    response_model=Settings,
    summary="Actualizar configuración",
    description="Actualiza la configuración del usuario"
)
async def update_settings(
    settings_data: SettingsUpdate,
    service: SettingsService = Depends(get_settings_service)
) -> Settings:
    """
    Actualiza la configuración del usuario.
    """
    try:
        updated = service.update_settings(settings_data)
        return updated
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error actualizando configuración: {str(e)}"
        )


@router.post(
    "/reset",
    response_model=Settings,
    summary="Restaurar configuración",
    description="Restaura la configuración a valores por defecto"
)
async def reset_settings(
    service: SettingsService = Depends(get_settings_service)
) -> Settings:
    """
    Restaura la configuración a valores por defecto.
    """
    return service.reset_to_defaults()


@router.patch(
    "/time-format",
    response_model=Settings,
    summary="Actualizar formato de hora",
    description="Actualiza solo el formato de hora"
)
async def update_time_format(
    data: dict = Body(..., example={"time_format": "12h"}),  # CAMBIADO
    service: SettingsService = Depends(get_settings_service)
) -> Settings:
    """Actualiza solo el formato de hora."""
    time_format = data.get("time_format")
    if time_format not in ["12h", "24h"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="time_format debe ser '12h' o '24h'"
        )
    return service.update_time_format(time_format)


@router.patch(
    "/alarm-sound", 
    response_model=Settings,
    summary="Actualizar sonido de alarma",
    description="Actualiza solo el sonido de alarma"
)
async def update_alarm_sound(
    data: dict = Body(..., example={"sound": "gentle"}),  # CAMBIADO
    service: SettingsService = Depends(get_settings_service)
) -> Settings:
    """Actualiza solo el sonido de alarma."""
    sound = data.get("sound")
    if not sound:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Se requiere el campo 'sound'"
        )
    try:
        return service.update_alarm_sound(sound)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch(
    "/volume",
    response_model=Settings,
    summary="Actualizar volumen",
    description="Actualiza solo el volumen de alarma"
)
async def update_volume(
    data: dict = Body(..., example={"volume": 75}),  # CAMBIADO
    service: SettingsService = Depends(get_settings_service)
) -> Settings:
    """Actualiza solo el volumen."""
    volume = data.get("volume")
    if volume is None or volume < 0 or volume > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El volumen debe estar entre 0 y 100"
        )
    return service.update_alarm_volume(volume)


@router.patch(
    "/theme",
    response_model=Settings,
    summary="Actualizar tema",
    description="Actualiza solo el tema de la aplicación"
)
async def update_theme(
    data: dict = Body(..., example={"theme": "dark"}),  # CAMBIADO
    service: SettingsService = Depends(get_settings_service)
) -> Settings:
    """Actualiza solo el tema."""
    theme = data.get("theme")
    if theme not in ["light", "dark", "auto"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="theme debe ser 'light', 'dark' o 'auto'"
        )
    return service.update_theme(theme)


@router.patch(
    "/volume/increase",
    response_model=Settings,
    summary="Aumentar volumen",
    description="Aumenta el volumen en una cantidad específica"
)
async def increase_volume(
    data: dict = Body(..., example={"amount": 10}),  # CAMBIADO
    service: SettingsService = Depends(get_settings_service)
) -> Settings:
    """Aumenta el volumen."""
    amount = data.get("amount", 10)
    if amount < 1 or amount > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La cantidad debe estar entre 1 y 100"
        )
    return service.increase_volume(amount)


@router.patch(
    "/volume/decrease",
    response_model=Settings,
    summary="Disminuir volumen", 
    description="Disminuye el volumen en una cantidad específica"
)
async def decrease_volume(
    data: dict = Body(..., example={"amount": 10}),  # CAMBIADO
    service: SettingsService = Depends(get_settings_service)
) -> Settings:
    """Disminuye el volumen."""
    amount = data.get("amount", 10)
    if amount < 1 or amount > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La cantidad debe estar entre 1 y 100"
        )
    return service.decrease_volume(amount)



@router.get(
    "/info",
    summary="Información de configuración",
    description="Obtiene información sobre las opciones disponibles"
)
async def get_settings_info(
    service: SettingsService = Depends(get_settings_service)
) -> dict:
    """
    Obtiene información sobre las opciones de configuración disponibles.
    """
    response = service.get_settings_response()
    current = service.get_settings()
    
    return {
        "current_settings": {
            "time_format": current.time_format,
            "alarm_sound": current.alarm_sound,
            "alarm_volume": current.alarm_volume,
            "volume_level": current.get_volume_level_description(),
            "theme": current.theme,
            "is_muted": current.is_volume_muted(),
        },
        "available_options": {
            "time_formats": response.available_time_formats,
            "sounds": response.available_sounds,
            "themes": response.available_themes,
        },
        "examples": {
            "time_12h": current.format_time_example(14, 30) if current.time_format == "12h" else "02:30 PM",
            "time_24h": current.format_time_example(14, 30) if current.time_format == "24h" else "14:30",
            "sound_path": current.get_sound_file_path(),
        }
    }


@router.get(
    "/export",
    summary="Exportar configuración",
    description="Exporta la configuración como JSON para backup"
)
async def export_settings(
    service: SettingsService = Depends(get_settings_service)
) -> dict:
    """
    Exporta la configuración actual como JSON.
    """
    return service.export_settings()


@router.post(
    "/import",
    response_model=Settings,
    summary="Importar configuración",
    description="Importa configuración desde JSON"
)
async def import_settings(
    data: dict,
    service: SettingsService = Depends(get_settings_service)
) -> Settings:
    """
    Importa configuración desde un diccionario JSON.
    """
    try:
        return service.import_settings(data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error importando configuración: {str(e)}"
        )


@router.get(
    "/health",
    summary="Health check del servicio de configuración"
)
async def settings_service_health(
    service: SettingsService = Depends(get_settings_service)
) -> dict:
    """
    Verifica que el servicio de configuración esté funcionando.
    """
    current = service.get_settings()
    
    return {
        "status": "healthy",
        "service": "SettingsService",
        "current_config": {
            "time_format": current.time_format,
            "theme": current.theme,
            "volume": current.alarm_volume,
        }
    }