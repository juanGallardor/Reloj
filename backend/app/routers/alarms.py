"""
Router de Alarmas - Endpoints API para gestión de alarmas.
Todos los endpoints usan AlarmService con lista circular doble.
"""

from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import Optional

from app.models.alarm import Alarm, AlarmCreate, AlarmUpdate
from app.services.alarm_service import AlarmService


# ============================================================================
# CONFIGURACIÓN DEL ROUTER
# ============================================================================

router = APIRouter(
    responses={
        404: {"description": "Alarma no encontrada"},
        400: {"description": "Datos inválidos"}
    }
)


# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================

def get_alarm_service() -> AlarmService:
    """
    Dependency para obtener instancia del servicio de alarmas.
    """
    return AlarmService()


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post(
    "/",
    response_model=Alarm,
    status_code=status.HTTP_201_CREATED,
    summary="Crear alarma",
    description="Crea una nueva alarma y la inserta ordenada por hora en la lista circular"
)
async def create_alarm(
    alarm_data: AlarmCreate,
    service: AlarmService = Depends(get_alarm_service)
) -> Alarm:
    """
    Crea una nueva alarma.
    
    - **time**: Hora en formato HH:MM (00:00 - 23:59)
    - **label**: Etiqueta descriptiva (max 100 caracteres)
    - **enabled**: Si está activa (default: True)
    - **days**: Días de repetición (default: [])
    
    La alarma se inserta en la lista circular ordenada por hora.
    """
    try:
        alarm = service.create_alarm(alarm_data)
        return alarm
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creando alarma: {str(e)}"
        )


@router.get(
    "/",
    response_model=list[Alarm],
    summary="Listar alarmas",
    description="Obtiene todas las alarmas ordenadas por hora"
)
async def get_alarms(
    service: AlarmService = Depends(get_alarm_service)
) -> list[Alarm]:
    """
    Obtiene todas las alarmas ordenadas por hora.
    """
    return service.get_all_alarms()


@router.get(
    "/{alarm_id}",
    response_model=Alarm,
    summary="Obtener alarma",
    description="Obtiene una alarma específica por su ID"
)
async def get_alarm(
    alarm_id: int,
    service: AlarmService = Depends(get_alarm_service)
) -> Alarm:
    """
    Obtiene una alarma por su ID.
    """
    alarm = service.get_alarm_by_id(alarm_id)
    
    if not alarm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alarma con ID {alarm_id} no encontrada"
        )
    
    return alarm


@router.put(
    "/{alarm_id}",
    response_model=Alarm,
    summary="Actualizar alarma",
    description="Actualiza una alarma existente. Si cambia la hora, se reordena en la lista"
)
async def update_alarm(
    alarm_id: int,
    alarm_data: AlarmUpdate,
    service: AlarmService = Depends(get_alarm_service)
) -> Alarm:
    """
    Actualiza una alarma existente.
    """
    alarm = service.update_alarm(alarm_id, alarm_data)
    
    if not alarm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alarma con ID {alarm_id} no encontrada"
        )
    
    return alarm


@router.delete(
    "/{alarm_id}",
    status_code=status.HTTP_200_OK,
    summary="Eliminar alarma",
    description="Elimina una alarma de la lista circular"
)
async def delete_alarm(
    alarm_id: int,
    service: AlarmService = Depends(get_alarm_service)
) -> dict:
    """
    Elimina una alarma.
    """
    deleted = service.delete_alarm(alarm_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alarma con ID {alarm_id} no encontrada"
        )
    
    return {
        "message": "Alarm deleted",
        "alarm_id": alarm_id
    }


@router.patch(
    "/{alarm_id}/toggle",
    response_model=Alarm,
    summary="Activar/Desactivar alarma",
    description="Cambia el estado enabled de una alarma"
)
async def toggle_alarm(
    alarm_id: int,
    service: AlarmService = Depends(get_alarm_service)
) -> Alarm:
    """
    Activa o desactiva una alarma.
    """
    alarm = service.toggle_alarm(alarm_id)
    
    if not alarm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alarma con ID {alarm_id} no encontrada"
        )
    
    return alarm


@router.get(
    "/next",
    response_model=Optional[Alarm],
    summary="Próxima alarma",
    description="Obtiene la próxima alarma activa que sonará"
)
async def get_next_alarm(
    service: AlarmService = Depends(get_alarm_service)
) -> Optional[Alarm]:
    """
    Obtiene la próxima alarma activa que sonará.
    """
    return service.get_next_alarm()


@router.get(
    "/{alarm_id}/navigate",
    response_model=Alarm,
    summary="Navegar entre alarmas",
    description="Navega circularmente entre alarmas (siguiente o anterior)"
)
async def navigate_alarm(
    alarm_id: int,
    direction: str = Query(..., regex="^(next|prev)$", description="Dirección: 'next' o 'prev'"),
    service: AlarmService = Depends(get_alarm_service)
) -> Alarm:
    """
    Navega circularmente entre alarmas.
    """
    if direction not in ["next", "prev"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Direction debe ser 'next' o 'prev'"
        )
    
    alarm = service.navigate_alarm(alarm_id, direction)
    
    if not alarm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alarma con ID {alarm_id} no encontrada"
        )
    
    return alarm


@router.get(
    "/stats/summary",
    summary="Estadísticas de alarmas",
    description="Obtiene estadísticas generales de alarmas"
)
async def get_alarm_stats(
    service: AlarmService = Depends(get_alarm_service)
) -> dict:
    """
    Obtiene estadísticas de alarmas.
    """
    total = service.count_alarms()
    active = service.count_active_alarms()
    next_alarm = service.get_next_alarm()
    
    return {
        "total_alarms": total,
        "active_alarms": active,
        "inactive_alarms": total - active,
        "next_alarm": next_alarm.model_dump() if next_alarm else None
    }


@router.get(
    "/active",
    response_model=list[Alarm],
    summary="Alarmas activas",
    description="Obtiene solo las alarmas que están activas"
)
async def get_active_alarms(
    service: AlarmService = Depends(get_alarm_service)
) -> list[Alarm]:
    """
    Obtiene solo las alarmas activas (enabled=True).
    """
    return service.get_active_alarms()


@router.get(
    "/health",
    summary="Health check del servicio de alarmas"
)
async def alarm_service_health(
    service: AlarmService = Depends(get_alarm_service)
) -> dict:
    """
    Verifica que el servicio de alarmas esté funcionando.
    """
    return {
        "status": "healthy",
        "service": "AlarmService",
        "total_alarms": service.count_alarms(),
        "data_structure": "Circular Doubly Linked List"
    }