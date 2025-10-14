"""
Router de Cronómetro - Endpoints API para gestión de laps.
Todos los endpoints usan StopwatchService con lista circular doble.
"""

from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import Optional

from app.models.lap import Lap, LapCreate, LapStatistics
from app.services.stopwatch_service import StopwatchService


# ============================================================================
# CONFIGURACIÓN DEL ROUTER
# ============================================================================

router = APIRouter(
    responses={
        404: {"description": "Lap no encontrado"},
        400: {"description": "Datos inválidos"}
    }
)


# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================

def get_stopwatch_service() -> StopwatchService:
    """
    Dependency para obtener instancia del servicio de cronómetro.
    """
    return StopwatchService()


# ============================================================================
# ENDPOINTS - GESTIÓN DE LAPS
# ============================================================================

@router.post(
    "/laps",
    response_model=Lap,
    status_code=status.HTTP_201_CREATED,
    summary="Agregar lap",
    description="Registra un nuevo lap en el cronómetro"
)
async def create_lap(
    lap_data: LapCreate,
    service: StopwatchService = Depends(get_stopwatch_service)
) -> Lap:
    """
    Agrega un nuevo lap al cronómetro.
    """
    try:
        lap = service.add_lap(
            lap_time=lap_data.lap_time,
            total_time=lap_data.total_time
        )
        return lap
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error agregando lap: {str(e)}"
        )


@router.get(
    "/laps",
    response_model=list[Lap],
    summary="Listar laps",
    description="Obtiene todos los laps en orden (más reciente primero)"
)
async def get_laps(
    service: StopwatchService = Depends(get_stopwatch_service)
) -> list[Lap]:
    """
    Obtiene todos los laps del cronómetro.
    """
    return service.get_all_laps()


@router.delete(
    "/laps",
    status_code=status.HTTP_200_OK,
    summary="Limpiar laps",
    description="Elimina todos los laps del cronómetro"
)
async def clear_laps(
    service: StopwatchService = Depends(get_stopwatch_service)
) -> dict:
    """
    Limpia todos los laps del cronómetro.
    """
    service.clear_laps()
    
    return {
        "message": "All laps cleared",
        "remaining_laps": 0
    }


@router.get(
    "/laps/{lap_id}",
    response_model=Lap,
    summary="Obtener lap",
    description="Obtiene un lap específico por su ID"
)
async def get_lap(
    lap_id: int,
    service: StopwatchService = Depends(get_stopwatch_service)
) -> Lap:
    """
    Obtiene un lap por su ID.
    """
    lap = service.get_lap_by_id(lap_id)
    
    if not lap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lap con ID {lap_id} no encontrado"
        )
    
    return lap


@router.delete(
    "/laps/{lap_id}",
    status_code=status.HTTP_200_OK,
    summary="Eliminar lap",
    description="Elimina un lap específico"
)
async def delete_lap(
    lap_id: int,
    service: StopwatchService = Depends(get_stopwatch_service)
) -> dict:
    """
    Elimina un lap específico.
    """
    deleted = service.delete_lap(lap_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lap con ID {lap_id} no encontrado"
        )
    
    return {
        "message": "Lap deleted",
        "lap_id": lap_id
    }


@router.get(
    "/laps/fastest",
    response_model=Optional[Lap],
    summary="Lap más rápido",
    description="Obtiene el lap con el tiempo más rápido"
)
async def get_fastest_lap(
    service: StopwatchService = Depends(get_stopwatch_service)
) -> Optional[Lap]:
    """
    Obtiene el lap más rápido registrado.
    """
    return service.get_fastest_lap()


@router.get(
    "/laps/slowest",
    response_model=Optional[Lap],
    summary="Lap más lento",
    description="Obtiene el lap con el tiempo más lento"
)
async def get_slowest_lap(
    service: StopwatchService = Depends(get_stopwatch_service)
) -> Optional[Lap]:
    """
    Obtiene el lap más lento registrado.
    """
    return service.get_slowest_lap()


@router.get(
    "/laps/statistics",
    response_model=LapStatistics,
    summary="Estadísticas de laps",
    description="Obtiene estadísticas completas de todos los laps"
)
async def get_lap_statistics(
    service: StopwatchService = Depends(get_stopwatch_service)
) -> LapStatistics:
    """
    Obtiene estadísticas completas de los laps.
    """
    return service.get_statistics()


@router.get(
    "/laps/{lap_number}/navigate",
    response_model=Lap,
    summary="Navegar entre laps",
    description="Navega circularmente entre laps (siguiente o anterior)"
)
async def navigate_lap(
    lap_number: int,
    direction: str = Query(..., regex="^(next|prev)$", description="Dirección: 'next' o 'prev'"),
    service: StopwatchService = Depends(get_stopwatch_service)
) -> Lap:
    """
    Navega circularmente entre laps.
    """
    if direction not in ["next", "prev"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Direction debe ser 'next' o 'prev'"
        )
    
    lap = service.navigate_lap(lap_number, direction)
    
    if not lap:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lap número {lap_number} no encontrado"
        )
    
    return lap


@router.get(
    "/laps/first",
    response_model=Optional[Lap],
    summary="Primer lap",
    description="Obtiene el primer lap (más reciente)"
)
async def get_first_lap(
    service: StopwatchService = Depends(get_stopwatch_service)
) -> Optional[Lap]:
    """
    Obtiene el primer lap (más reciente).
    """
    return service.get_first_lap()


@router.get(
    "/laps/last",
    response_model=Optional[Lap],
    summary="Último lap",
    description="Obtiene el último lap (más antiguo)"
)
async def get_last_lap(
    service: StopwatchService = Depends(get_stopwatch_service)
) -> Optional[Lap]:
    """
    Obtiene el último lap (más antiguo).
    """
    return service.get_last_lap()


@router.get(
    "/laps/filter/faster",
    response_model=list[Lap],
    summary="Laps más rápidos",
    description="Obtiene laps más rápidos que un tiempo dado"
)
async def get_laps_faster_than(
    time: float = Query(..., gt=0, description="Tiempo en segundos"),
    service: StopwatchService = Depends(get_stopwatch_service)
) -> list[Lap]:
    """
    Obtiene laps más rápidos que un tiempo específico.
    """
    return service.get_laps_faster_than(time)


@router.get(
    "/laps/filter/slower",
    response_model=list[Lap],
    summary="Laps más lentos",
    description="Obtiene laps más lentos que un tiempo dado"
)
async def get_laps_slower_than(
    time: float = Query(..., gt=0, description="Tiempo en segundos"),
    service: StopwatchService = Depends(get_stopwatch_service)
) -> list[Lap]:
    """
    Obtiene laps más lentos que un tiempo específico.
    """
    return service.get_laps_slower_than(time)


@router.get(
    "/stats/summary",
    summary="Resumen de estadísticas",
    description="Obtiene resumen rápido del cronómetro"
)
async def get_stopwatch_summary(
    service: StopwatchService = Depends(get_stopwatch_service)
) -> dict:
    """
    Obtiene resumen rápido del cronómetro.
    """
    stats = service.get_statistics()
    
    return {
        "total_laps": stats.total_laps,
        "average_time": stats.average_lap_time,
        "total_elapsed": stats.total_elapsed_time,
        "fastest_time": stats.fastest_lap.lap_time if stats.fastest_lap else None,
        "slowest_time": stats.slowest_lap.lap_time if stats.slowest_lap else None
    }


@router.get(
    "/health",
    summary="Health check del servicio de cronómetro"
)
async def stopwatch_service_health(
    service: StopwatchService = Depends(get_stopwatch_service)
) -> dict:
    """
    Verifica que el servicio de cronómetro esté funcionando.
    """
    return {
        "status": "healthy",
        "service": "StopwatchService",
        "total_laps": service.count_laps(),
        "data_structure": "Circular Doubly Linked List"
    }