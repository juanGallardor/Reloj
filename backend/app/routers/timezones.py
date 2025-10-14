"""
Router de Zonas Horarias - CORREGIDO: Orden de endpoints arreglado.
El problema era que /{timezone_id} capturaba /favorites antes.
"""

from fastapi import APIRouter, HTTPException, status, Query, Body, Depends
from typing import Optional
from datetime import datetime, timedelta

from app.models.timezone import Timezone, TimezoneCreate, FavoriteTimezone
from app.services.timezone_service import TimezoneService


# ============================================================================
# CONFIGURACIÓN DEL ROUTER
# ============================================================================

router = APIRouter(
    responses={
        404: {"description": "Zona horaria no encontrada"},
        400: {"description": "Datos inválidos"}
    }
)


# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================

def get_timezone_service() -> TimezoneService:
    """Dependency para obtener instancia del servicio de zonas horarias."""
    return TimezoneService()


# ============================================================================
# ENDPOINTS - ORDEN CORRECTO (ESPECÍFICOS PRIMERO, DINÁMICOS DESPUÉS)
# ============================================================================

# ⚠️ IMPORTANTE: Los endpoints específicos DEBEN ir ANTES de /{timezone_id}
# para que FastAPI no confunda "favorites" con un timezone_id

@router.get(
    "/",
    response_model=list[Timezone],
    summary="Listar zonas horarias",
    description="Obtiene todas las zonas horarias disponibles"
)
async def get_timezones(
    refresh: bool = Query(False, description="Forzar refresh desde la API"),
    service: TimezoneService = Depends(get_timezone_service)
) -> list[Timezone]:
    """Obtiene todas las zonas horarias disponibles."""
    return service.get_available_timezones(force_refresh=refresh)


@router.get(
    "/search",
    response_model=list[Timezone],
    summary="Buscar zonas horarias",
    description="Busca zonas horarias por país, ciudad o región"
)
async def search_timezones(
    query: str = Query(..., min_length=2, description="Término de búsqueda"),
    service: TimezoneService = Depends(get_timezone_service)
) -> list[Timezone]:
    """Busca zonas horarias por término de búsqueda."""
    return service.search_timezone(query)


@router.get(
    "/countries",
    response_model=list[str],
    summary="Listar países",
    description="Obtiene lista de países únicos disponibles"
)
async def get_countries(
    service: TimezoneService = Depends(get_timezone_service)
) -> list[str]:
    """Obtiene lista de países únicos con zonas horarias disponibles."""
    return service.get_countries()


@router.post(
    "/refresh",
    summary="Refrescar desde API",
    description="Fuerza actualización de zonas horarias desde WorldTimeAPI"
)
async def refresh_timezones(
    service: TimezoneService = Depends(get_timezone_service)
) -> dict:
    """Fuerza refresh de zonas horarias desde WorldTimeAPI."""
    success = service.refresh_timezones()
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No se pudo actualizar desde WorldTimeAPI. Usando datos en cache."
        )
    
    return {
        "message": "Timezones refreshed successfully",
        "total_timezones": len(service.get_available_timezones())
    }


@router.get(
    "/stats",
    summary="Estadísticas de zonas horarias"
)
async def get_timezone_stats(
    service: TimezoneService = Depends(get_timezone_service)
) -> dict:
    """Obtiene estadísticas del servicio de zonas horarias."""
    return service.get_stats()


@router.get(
    "/health",
    summary="Health check del servicio de zonas horarias"
)
async def timezone_service_health(
    service: TimezoneService = Depends(get_timezone_service)
) -> dict:
    """Verifica que el servicio de zonas horarias esté funcionando."""
    stats = service.get_stats()
    
    return {
        "status": "healthy",
        "service": "TimezoneService",
        "total_available": stats["total_available"],
        "total_favorites": stats["total_favorites"],
        "api_source": "WorldTimeAPI",
        "data_structure": "Circular Doubly Linked List (for favorites)"
    }


# ============================================================================
# ENDPOINTS DE FAVORITOS - ANTES DE /{timezone_id}
# ============================================================================

@router.get(
    "/favorites",
    response_model=list[FavoriteTimezone],
    summary="Listar favoritos",
    description="Obtiene zonas horarias favoritas en orden"
)
async def get_favorites(
    service: TimezoneService = Depends(get_timezone_service)
) -> list[FavoriteTimezone]:
    """Obtiene todas las zonas horarias favoritas."""
    return service.get_favorites()


@router.post(
    "/favorites",
    response_model=FavoriteTimezone,
    status_code=status.HTTP_201_CREATED,
    summary="Agregar a favoritos",
    description="Agrega una zona horaria a la lista de favoritos"
)
async def add_favorite(
    timezone_id: str = Body(..., embed=True, description="ID de la zona horaria"),
    service: TimezoneService = Depends(get_timezone_service)
) -> FavoriteTimezone:
    """Agrega una zona horaria a favoritos."""
    favorite = service.add_favorite(timezone_id)
    
    if not favorite:
        tz = service.get_timezone_by_id(timezone_id)
        if not tz:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Zona horaria '{timezone_id}' no encontrada"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Zona horaria '{timezone_id}' ya está en favoritos"
            )
    
    return favorite


@router.put(
    "/favorites/reorder",
    response_model=list[FavoriteTimezone],
    summary="Reordenar favorito",
    description="Cambia el orden de una zona horaria favorita"
)
async def reorder_favorite(
    data: dict = Body(..., example={"timezone_id": "colombia-bogota", "new_position": 0}),
    service: TimezoneService = Depends(get_timezone_service)
) -> list[FavoriteTimezone]:
    """Reordena una zona horaria favorita."""
    timezone_id = data.get("timezone_id")
    new_position = data.get("new_position")
    
    if not timezone_id or new_position is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe proporcionar 'timezone_id' y 'new_position'"
        )
    
    reordered = service.reorder_favorite(timezone_id, new_position)
    
    if not reordered:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se pudo reordenar la zona '{timezone_id}'"
        )
    
    return service.get_favorites()


@router.get(
    "/favorites/check/{timezone_id}",
    summary="Verificar si es favorito",
    description="Verifica si una zona horaria está en favoritos"
)
async def check_if_favorite(
    timezone_id: str,
    service: TimezoneService = Depends(get_timezone_service)
) -> dict:
    """Verifica si una zona horaria está en favoritos."""
    is_favorite = service.is_favorite(timezone_id)
    
    return {
        "timezone_id": timezone_id,
        "is_favorite": is_favorite
    }


@router.delete(
    "/favorites/{timezone_id}",
    status_code=status.HTTP_200_OK,
    summary="Quitar de favoritos",
    description="Elimina una zona horaria de la lista de favoritos"
)
async def remove_favorite(
    timezone_id: str,
    service: TimezoneService = Depends(get_timezone_service)
) -> dict:
    """Elimina una zona horaria de favoritos."""
    removed = service.remove_favorite(timezone_id)
    
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Zona horaria '{timezone_id}' no está en favoritos"
        )
    
    return {
        "message": "Removed from favorites",
        "timezone_id": timezone_id
    }


@router.get(
    "/favorites/{timezone_id}/navigate",
    response_model=FavoriteTimezone,
    summary="Navegar entre favoritos",
    description="Navega circularmente entre zonas horarias favoritas"
)
async def navigate_favorites(
    timezone_id: str,
    direction: str = Query(..., regex="^(next|prev)$", description="Dirección: 'next' o 'prev'"),
    service: TimezoneService = Depends(get_timezone_service)
) -> FavoriteTimezone:
    """Navega circularmente entre favoritos."""
    if direction not in ["next", "prev"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Direction debe ser 'next' o 'prev'"
        )
    
    favorite = service.navigate_favorites(timezone_id, direction)
    
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Zona horaria '{timezone_id}' no está en favoritos"
        )
    
    return favorite


# ============================================================================
# ENDPOINTS CON PARÁMETROS DINÁMICOS - AL FINAL
# ============================================================================

@router.get(
    "/by-country/{country}",
    response_model=list[Timezone],
    summary="Zonas por país",
    description="Obtiene todas las zonas horarias de un país específico"
)
async def get_timezones_by_country(
    country: str,
    service: TimezoneService = Depends(get_timezone_service)
) -> list[Timezone]:
    """Obtiene todas las zonas horarias de un país."""
    return service.get_timezones_by_country(country)


@router.get(
    "/{timezone_id}/current",
    summary="Hora actual",
    description="Calcula la hora actual en una zona horaria específica"
)
async def get_current_time(
    timezone_id: str,
    service: TimezoneService = Depends(get_timezone_service)
) -> dict:
    """Obtiene la hora actual en una zona horaria específica."""
    timezone = service.get_timezone_by_id(timezone_id)
    
    if not timezone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Zona horaria '{timezone_id}' no encontrada"
        )
    
    utc_now = datetime.utcnow()
    offset_hours = timezone.get_offset_hours()
    local_time = utc_now + timedelta(hours=offset_hours)
    
    return {
        "timezone_id": timezone_id,
        "city": timezone.city,
        "country": timezone.country,
        "offset": timezone.offset,
        "utc_time": utc_now.strftime("%H:%M:%S"),
        "current_time": local_time.strftime("%H:%M:%S"),
        "current_date": local_time.strftime("%Y-%m-%d"),
        "day_of_week": local_time.strftime("%A"),
        "full_datetime": local_time.isoformat()
    }


@router.get(
    "/{timezone_id}",
    response_model=Timezone,
    summary="Obtener zona horaria",
    description="Obtiene una zona horaria específica por su ID"
)
async def get_timezone(
    timezone_id: str,
    service: TimezoneService = Depends(get_timezone_service)
) -> Timezone:
    """Obtiene una zona horaria por su ID."""
    timezone = service.get_timezone_by_id(timezone_id)
    
    if not timezone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Zona horaria '{timezone_id}' no encontrada"
        )
    
    return timezone