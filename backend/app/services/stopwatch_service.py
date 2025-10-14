"""
Servicio de gestión de cronómetro y laps usando Lista Circular Doble.
Implementa la lógica para registrar y navegar entre vueltas del cronómetro.
"""

from datetime import datetime
from typing import Optional
import logging

from app.data_structures.circular_doubly_linked_list import CircularDoublyLinkedList
from app.models.lap import Lap, LapCreate, LapStatistics
from app.database.json_db import JSONDatabase
from app.config import get_settings

logger = logging.getLogger(__name__)


class StopwatchService:
    """
    Servicio para gestionar laps del cronómetro usando lista circular doble.
    
    La lista circular doble permite:
    - Laps en orden (más reciente primero)
    - Navegación bidireccional entre laps
    - Acceso circular a todos los laps
    
    Attributes:
        laps: Lista circular doble de laps
        json_db: Base de datos JSON para persistencia
    """
    
    def __init__(self):
        """Inicializa el servicio y carga laps desde JSON."""
        self.laps = CircularDoublyLinkedList[Lap]()
        settings = get_settings()
        self.json_db = JSONDatabase(settings.LAPS_FILE)
        self._load_from_json()
        logger.info("StopwatchService inicializado")
    
    # ========================================================================
    # MÉTODOS PÚBLICOS - GESTIÓN DE LAPS
    # ========================================================================
    
    def add_lap(self, lap_time: float, total_time: float) -> Lap:
        """
        Agrega un nuevo lap al cronómetro.
        
        El lap se inserta al inicio de la lista (más reciente primero).
        
        Args:
            lap_time: Tiempo de la vuelta en segundos
            total_time: Tiempo total acumulado en segundos
            
        Returns:
            Lap: Lap creado
        """
        # Generar ID y número de lap
        new_id = self._generate_id()
        lap_number = self._get_next_lap_number()
        
        # Crear objeto Lap
        lap = Lap(
            id=new_id,
            lap_number=lap_number,
            lap_time=round(lap_time, 2),
            total_time=round(total_time, 2),
            timestamp=datetime.now()
        )
        
        # Insertar al INICIO (último lap primero)
        self.laps.insert_at_beginning(lap)
        
        # Persistir
        self._save_to_json()
        
        logger.info(f"Lap agregado: #{lap_number}, tiempo={lap_time:.2f}s")
        return lap
    
    def get_all_laps(self) -> list[Lap]:
        """
        Obtiene todos los laps en orden (más reciente primero).
        
        Returns:
            list[Lap]: Lista de laps
        """
        return self.laps.get_all()
    
    def get_lap_by_id(self, lap_id: int) -> Optional[Lap]:
        """
        Busca un lap por su ID.
        
        Args:
            lap_id: ID del lap a buscar
            
        Returns:
            Lap | None: Lap encontrado o None
        """
        node = self.laps.find(lambda l: l.id == lap_id)
        return node.data if node else None
    
    def get_lap_by_number(self, lap_number: int) -> Optional[Lap]:
        """
        Busca un lap por su número.
        
        Args:
            lap_number: Número del lap
            
        Returns:
            Lap | None: Lap encontrado o None
        """
        node = self.laps.find(lambda l: l.lap_number == lap_number)
        return node.data if node else None
    
    # ========================================================================
    # MÉTODOS DE ANÁLISIS
    # ========================================================================
    
    def get_fastest_lap(self) -> Optional[Lap]:
        """
        Encuentra el lap más rápido.
        
        Returns:
            Lap | None: Lap más rápido o None si no hay laps
        """
        if self.laps.is_empty():
            return None
        
        all_laps = self.get_all_laps()
        return min(all_laps, key=lambda l: l.lap_time)
    
    def get_slowest_lap(self) -> Optional[Lap]:
        """
        Encuentra el lap más lento.
        
        Returns:
            Lap | None: Lap más lento o None si no hay laps
        """
        if self.laps.is_empty():
            return None
        
        all_laps = self.get_all_laps()
        return max(all_laps, key=lambda l: l.lap_time)
    
    def get_average_lap_time(self) -> float:
        """
        Calcula el tiempo promedio de los laps.
        
        Returns:
            float: Tiempo promedio en segundos
        """
        if self.laps.is_empty():
            return 0.0
        
        all_laps = self.get_all_laps()
        total = sum(lap.lap_time for lap in all_laps)
        return round(total / len(all_laps), 2)
    
    def get_statistics(self) -> LapStatistics:
        """
        Obtiene estadísticas completas de los laps.
        
        Returns:
            LapStatistics: Estadísticas de todos los laps
        """
        all_laps = self.get_all_laps()
        
        if not all_laps:
            return LapStatistics(
                total_laps=0,
                fastest_lap=None,
                slowest_lap=None,
                average_lap_time=0.0,
                total_elapsed_time=0.0
            )
        
        # Calcular estadísticas
        fastest = self.get_fastest_lap()
        slowest = self.get_slowest_lap()
        average = self.get_average_lap_time()
        
        # El tiempo total es el total_time del último lap (el más reciente)
        total_elapsed = all_laps[0].total_time if all_laps else 0.0
        
        return LapStatistics(
            total_laps=len(all_laps),
            fastest_lap=fastest,
            slowest_lap=slowest,
            average_lap_time=average,
            total_elapsed_time=total_elapsed
        )
    
    # ========================================================================
    # MÉTODOS DE NAVEGACIÓN CIRCULAR
    # ========================================================================
    
    def navigate_lap(self, lap_number: int, direction: str) -> Optional[Lap]:
        """
        Navega circularmente entre laps.
        
        Args:
            lap_number: Número del lap actual
            direction: "next" o "prev"
            
        Returns:
            Lap | None: Siguiente/anterior lap o None
        """
        # Buscar lap actual
        lap = self.get_lap_by_number(lap_number)
        if not lap:
            return None
        
        # Navegar según dirección
        if direction == "next":
            next_data = self.laps.get_next(lap)
        elif direction == "prev":
            next_data = self.laps.get_previous(lap)
        else:
            logger.warning(f"Dirección inválida: {direction}")
            return None
        
        return next_data
    
    def get_first_lap(self) -> Optional[Lap]:
        """
        Obtiene el primer lap (más reciente).
        
        Returns:
            Lap | None: Primer lap o None
        """
        if self.laps.is_empty():
            return None
        return self.laps.head.data
    
    def get_last_lap(self) -> Optional[Lap]:
        """
        Obtiene el último lap (más antiguo).
        
        Returns:
            Lap | None: Último lap o None
        """
        if self.laps.is_empty():
            return None
        return self.laps.head.prev.data
    
    # ========================================================================
    # MÉTODOS DE LIMPIEZA
    # ========================================================================
    
    def clear_laps(self) -> None:
        """
        Limpia todos los laps del cronómetro.
        """
        self.laps.clear()
        self._save_to_json()
        logger.info("Laps limpiados")
    
    def delete_lap(self, lap_id: int) -> bool:
        """
        Elimina un lap específico.
        
        Args:
            lap_id: ID del lap a eliminar
            
        Returns:
            bool: True si se eliminó, False si no existía
        """
        lap = self.get_lap_by_id(lap_id)
        if not lap:
            return False
        
        deleted = self.laps.delete(lap)
        if deleted:
            self._save_to_json()
            logger.info(f"Lap eliminado: ID={lap_id}")
        
        return deleted
    
    # ========================================================================
    # MÉTODOS DE CONSULTA
    # ========================================================================
    
    def count_laps(self) -> int:
        """
        Cuenta el número total de laps.
        
        Returns:
            int: Cantidad de laps
        """
        return len(self.laps)
    
    def get_laps_faster_than(self, time: float) -> list[Lap]:
        """
        Obtiene laps más rápidos que un tiempo dado.
        
        Args:
            time: Tiempo en segundos
            
        Returns:
            list[Lap]: Laps más rápidos
        """
        return self.laps.find_all(lambda l: l.lap_time < time)
    
    def get_laps_slower_than(self, time: float) -> list[Lap]:
        """
        Obtiene laps más lentos que un tiempo dado.
        
        Args:
            time: Tiempo en segundos
            
        Returns:
            list[Lap]: Laps más lentos
        """
        return self.laps.find_all(lambda l: l.lap_time > time)
    
    # ========================================================================
    # MÉTODOS PRIVADOS - PERSISTENCIA Y AUXILIARES
    # ========================================================================
    
    def _load_from_json(self) -> None:
        """Carga laps desde el archivo JSON."""
        data = self.json_db.read_as_list()
        
        # Cargar en orden inverso para mantener el orden correcto
        # (el más reciente debe estar al inicio)
        for item in reversed(data):
            try:
                lap = Lap(**item)
                self.laps.insert_at_end(lap)
            except Exception as e:
                logger.error(f"Error cargando lap: {e}")
        
        logger.info(f"Cargados {len(self.laps)} laps desde JSON")
    
    def _save_to_json(self) -> None:
        """Guarda el estado actual de laps en JSON."""
        data = [lap.model_dump(mode='json') for lap in self.get_all_laps()]
        self.json_db.write(data)
        logger.debug(f"Guardados {len(data)} laps en JSON")
    
    def _generate_id(self) -> int:
        """
        Genera un nuevo ID único para un lap.
        
        Returns:
            int: Nuevo ID
        """
        if self.laps.is_empty():
            return 1
        
        all_laps = self.get_all_laps()
        max_id = max(lap.id for lap in all_laps)
        return max_id + 1
    
    def _get_next_lap_number(self) -> int:
        """
        Obtiene el siguiente número de lap.
        
        Returns:
            int: Número del próximo lap
        """
        if self.laps.is_empty():
            return 1
        
        all_laps = self.get_all_laps()
        max_number = max(lap.lap_number for lap in all_laps)
        return max_number + 1


# ============================================================================
# EJEMPLO DE USO Y TESTS
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("⏱️  EJEMPLO DE USO - STOPWATCH SERVICE")
    print("=" * 70)
    
    # Crear servicio
    service = StopwatchService()
    
    # Limpiar laps previos
    service.clear_laps()
    
    # Ejemplo 1: Agregar laps
    print("\n1️⃣ Agregar laps:")
    lap1 = service.add_lap(lap_time=15.23, total_time=15.23)
    print(f"   ✅ Lap #{lap1.lap_number}: {lap1.format_lap_time()}")
    
    lap2 = service.add_lap(lap_time=12.45, total_time=27.68)
    print(f"   ✅ Lap #{lap2.lap_number}: {lap2.format_lap_time()}")
    
    lap3 = service.add_lap(lap_time=18.90, total_time=46.58)
    print(f"   ✅ Lap #{lap3.lap_number}: {lap3.format_lap_time()}")
    
    lap4 = service.add_lap(lap_time=14.56, total_time=61.14)
    print(f"   ✅ Lap #{lap4.lap_number}: {lap4.format_lap_time()}")
    
    # Ejemplo 2: Listar todos los laps
    print("\n2️⃣ Todos los laps (más reciente primero):")
    for lap in service.get_all_laps():
        print(f"   Lap #{lap.lap_number}: {lap.format_lap_time()} (Total: {lap.format_total_time()})")
    
    # Ejemplo 3: Encontrar más rápido y más lento
    print("\n3️⃣ Análisis de laps:")
    fastest = service.get_fastest_lap()
    slowest = service.get_slowest_lap()
    average = service.get_average_lap_time()
    
    print(f"   🏆 Más rápido: Lap #{fastest.lap_number} - {fastest.format_lap_time()}")
    print(f"   🐌 Más lento: Lap #{slowest.lap_number} - {slowest.format_lap_time()}")
    print(f"   📊 Promedio: {average:.2f}s")
    
    # Ejemplo 4: Navegación circular
    print("\n4️⃣ Navegación circular desde Lap #2:")
    current = lap2
    print(f"   Actual: Lap #{current.lap_number}")
    
    next_lap = service.navigate_lap(current.lap_number, "next")
    print(f"   Siguiente: Lap #{next_lap.lap_number}")
    
    prev_lap = service.navigate_lap(current.lap_number, "prev")
    print(f"   Anterior: Lap #{prev_lap.lap_number}")
    
    # Ejemplo 5: Estadísticas completas
    print("\n5️⃣ Estadísticas completas:")
    stats = service.get_statistics()
    print(f"   Total de laps: {stats.total_laps}")
    print(f"   Más rápido: {stats.fastest_lap.format_lap_time()}")
    print(f"   Más lento: {stats.slowest_lap.format_lap_time()}")
    print(f"   Promedio: {stats.format_average_time()}")
    print(f"   Tiempo total: {stats.format_total_time()}")
    
    # Ejemplo 6: Filtrar laps
    print("\n6️⃣ Filtrar laps más rápidos que 16s:")
    fast_laps = service.get_laps_faster_than(16.0)
    for lap in fast_laps:
        print(f"   Lap #{lap.lap_number}: {lap.format_lap_time()}")
    
    # Ejemplo 7: Primer y último lap
    print("\n7️⃣ Primer y último lap:")
    first = service.get_first_lap()
    last = service.get_last_lap()
    print(f"   Primero (más reciente): Lap #{first.lap_number}")
    print(f"   Último (más antiguo): Lap #{last.lap_number}")
    
    # Ejemplo 8: Limpiar laps
    print("\n8️⃣ Limpiar todos los laps:")
    service.clear_laps()
    print(f"   ✅ Laps limpiados. Total restante: {service.count_laps()}")
    
    print("\n" + "=" * 70)