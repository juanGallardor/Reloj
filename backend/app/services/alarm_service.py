"""
Servicio de gestión de alarmas usando Lista Circular Doble.
Implementa toda la lógica de negocio para el sistema de alarmas.
"""

from datetime import datetime
from typing import Optional
import logging

from app.data_structures.circular_doubly_linked_list import CircularDoublyLinkedList
from app.models.alarm import Alarm, AlarmCreate, AlarmUpdate
from app.database.json_db import JSONDatabase
from app.config import get_settings

logger = logging.getLogger(__name__)


class AlarmService:
    """
    Servicio para gestionar alarmas usando lista circular doble.
    
    La lista circular doble permite:
    - Alarmas ordenadas por hora
    - Navegación circular entre alarmas
    - Encontrar la próxima alarma eficientemente
    
    Attributes:
        alarms: Lista circular doble de alarmas
        json_db: Base de datos JSON para persistencia
    """
    
    def __init__(self):
        """Inicializa el servicio y carga alarmas desde JSON."""
        self.alarms = CircularDoublyLinkedList[Alarm]()
        settings = get_settings()
        self.json_db = JSONDatabase(settings.ALARMS_FILE)
        self._load_from_json()
        logger.info("AlarmService inicializado")
    
    # ========================================================================
    # MÉTODOS PÚBLICOS - CRUD
    # ========================================================================
    
    def create_alarm(self, alarm_data: AlarmCreate) -> Alarm:
        """
        Crea una nueva alarma.
        
        Genera un nuevo ID, crea el objeto Alarm, lo inserta en la lista
        ordenada por hora y persiste los cambios.
        
        Args:
            alarm_data: Datos de la alarma a crear
            
        Returns:
            Alarm: Alarma creada
        """
        # Generar nuevo ID
        new_id = self._generate_id()
        
        # Crear objeto Alarm
        alarm = Alarm(
            id=new_id,
            time=alarm_data.time,
            label=alarm_data.label,
            enabled=alarm_data.enabled,
            days=alarm_data.days,
            created_at=datetime.now()
        )
        
        # Insertar en lista ordenada por hora
        self.alarms.insert_sorted(alarm, key_func=self._alarm_sort_key)
        
        # Persistir
        self._save_to_json()
        
        logger.info(f"Alarma creada: ID={alarm.id}, hora={alarm.time}")
        return alarm
    
    def get_all_alarms(self) -> list[Alarm]:
        """
        Obtiene todas las alarmas ordenadas por hora.
        
        Returns:
            list[Alarm]: Lista de todas las alarmas
        """
        return self.alarms.get_all()
    
    def get_alarm_by_id(self, alarm_id: int) -> Optional[Alarm]:
        """
        Busca una alarma por su ID.
        
        Args:
            alarm_id: ID de la alarma a buscar
            
        Returns:
            Alarm | None: Alarma encontrada o None
        """
        node = self.alarms.find(lambda a: a.id == alarm_id)
        return node.data if node else None
    
    def update_alarm(self, alarm_id: int, update_data: AlarmUpdate) -> Optional[Alarm]:
        """
        Actualiza una alarma existente.
        
        Si cambió la hora, reordena la alarma en la lista.
        
        Args:
            alarm_id: ID de la alarma a actualizar
            update_data: Datos a actualizar
            
        Returns:
            Alarm | None: Alarma actualizada o None si no existe
        """
        # Buscar alarma
        alarm = self.get_alarm_by_id(alarm_id)
        if not alarm:
            logger.warning(f"Alarma no encontrada: ID={alarm_id}")
            return None
        
        # Guardar hora anterior para detectar cambios
        old_time = alarm.time
        
        # Actualizar campos proporcionados
        if update_data.time is not None:
            alarm.time = update_data.time
        if update_data.label is not None:
            alarm.label = update_data.label
        if update_data.enabled is not None:
            alarm.enabled = update_data.enabled
        if update_data.days is not None:
            alarm.days = update_data.days
        
        # Si cambió la hora, reordenar en la lista
        if update_data.time is not None and update_data.time != old_time:
            # Eliminar y reinsertar para mantener orden
            self.alarms.delete(alarm)
            self.alarms.insert_sorted(alarm, key_func=self._alarm_sort_key)
            logger.info(f"Alarma reordenada: ID={alarm_id}, {old_time} -> {alarm.time}")
        
        # Persistir cambios
        self._save_to_json()
        
        logger.info(f"Alarma actualizada: ID={alarm_id}")
        return alarm
    
    def delete_alarm(self, alarm_id: int) -> bool:
        """
        Elimina una alarma.
        
        Args:
            alarm_id: ID de la alarma a eliminar
            
        Returns:
            bool: True si se eliminó, False si no existía
        """
        # Buscar alarma
        alarm = self.get_alarm_by_id(alarm_id)
        if not alarm:
            logger.warning(f"Alarma no encontrada para eliminar: ID={alarm_id}")
            return False
        
        # Eliminar de la lista circular
        deleted = self.alarms.delete(alarm)
        
        if deleted:
            # Persistir cambios
            self._save_to_json()
            logger.info(f"Alarma eliminada: ID={alarm_id}")
        
        return deleted
    
    def toggle_alarm(self, alarm_id: int) -> Optional[Alarm]:
        """
        Activa/desactiva una alarma.
        
        Args:
            alarm_id: ID de la alarma
            
        Returns:
            Alarm | None: Alarma actualizada o None si no existe
        """
        alarm = self.get_alarm_by_id(alarm_id)
        if not alarm:
            return None
        
        # Cambiar estado
        alarm.enabled = not alarm.enabled
        
        # Persistir
        self._save_to_json()
        
        status = "activada" if alarm.enabled else "desactivada"
        logger.info(f"Alarma {status}: ID={alarm_id}")
        
        return alarm
    
    # ========================================================================
    # MÉTODOS DE NAVEGACIÓN CIRCULAR
    # ========================================================================
    
    def get_next_alarm(self) -> Optional[Alarm]:
        """
        Retorna la próxima alarma activa que sonará.
        
        Busca la siguiente alarma habilitada comparando con la hora actual.
        
        Returns:
            Alarm | None: Próxima alarma activa o None si no hay
        """
        if self.alarms.is_empty():
            return None
        
        # Obtener hora actual en formato HH:MM
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        
        # Buscar primera alarma activa después de la hora actual
        all_alarms = self.get_all_alarms()
        
        # Primero buscar alarmas después de la hora actual
        for alarm in all_alarms:
            if alarm.enabled and alarm.time > current_time:
                return alarm
        
        # Si no hay ninguna después, la primera alarma del día siguiente
        # (circularidad: después de 23:59 viene 00:00)
        for alarm in all_alarms:
            if alarm.enabled:
                return alarm
        
        # No hay alarmas activas
        return None
    
    def navigate_alarm(self, alarm_id: int, direction: str) -> Optional[Alarm]:
        """
        Navega circularmente entre alarmas.
        
        Args:
            alarm_id: ID de la alarma actual
            direction: "next" o "prev"
            
        Returns:
            Alarm | None: Siguiente/anterior alarma o None
        """
        # Buscar alarma actual
        alarm = self.get_alarm_by_id(alarm_id)
        if not alarm:
            return None
        
        # Navegar según dirección
        if direction == "next":
            next_data = self.alarms.get_next(alarm)
        elif direction == "prev":
            next_data = self.alarms.get_previous(alarm)
        else:
            logger.warning(f"Dirección inválida: {direction}")
            return None
        
        return next_data
    
    # ========================================================================
    # MÉTODOS DE CONSULTA
    # ========================================================================
    
    def get_active_alarms(self) -> list[Alarm]:
        """
        Retorna solo las alarmas activas.
        
        Returns:
            list[Alarm]: Lista de alarmas habilitadas
        """
        return self.alarms.find_all(lambda a: a.enabled)
    
    def get_alarms_by_day(self, day: str) -> list[Alarm]:
        """
        Retorna alarmas que suenan en un día específico.
        
        Args:
            day: Día de la semana ("Lun", "Mar", etc.)
            
        Returns:
            list[Alarm]: Alarmas de ese día
        """
        return self.alarms.find_all(lambda a: day in a.days or not a.days)
    
    def count_alarms(self) -> int:
        """
        Cuenta el número total de alarmas.
        
        Returns:
            int: Cantidad de alarmas
        """
        return len(self.alarms)
    
    def count_active_alarms(self) -> int:
        """
        Cuenta el número de alarmas activas.
        
        Returns:
            int: Cantidad de alarmas habilitadas
        """
        return len(self.get_active_alarms())
    
    # ========================================================================
    # MÉTODOS PRIVADOS - PERSISTENCIA Y AUXILIARES
    # ========================================================================
    
    def _load_from_json(self) -> None:
        """Carga alarmas desde el archivo JSON."""
        data = self.json_db.read_as_list()
        
        for item in data:
            try:
                alarm = Alarm(**item)
                # Insertar en orden
                self.alarms.insert_sorted(alarm, key_func=self._alarm_sort_key)
            except Exception as e:
                logger.error(f"Error cargando alarma: {e}")
        
        logger.info(f"Cargadas {len(self.alarms)} alarmas desde JSON")
    
    def _save_to_json(self) -> None:
        """Guarda el estado actual de alarmas en JSON."""
        data = [alarm.model_dump(mode='json') for alarm in self.get_all_alarms()]
        self.json_db.write(data)
        logger.debug(f"Guardadas {len(data)} alarmas en JSON")
    
    def _generate_id(self) -> int:
        """
        Genera un nuevo ID único para una alarma.
        
        Returns:
            int: Nuevo ID
        """
        if self.alarms.is_empty():
            return 1
        
        # Obtener el ID máximo actual
        all_alarms = self.get_all_alarms()
        max_id = max(alarm.id for alarm in all_alarms)
        return max_id + 1
    
    @staticmethod
    def _alarm_sort_key(alarm: Alarm) -> str:
        """
        Función clave para ordenar alarmas por hora.
        
        Args:
            alarm: Alarma a evaluar
            
        Returns:
            str: Hora de la alarma (formato HH:MM)
        """
        return alarm.time


# ============================================================================
# EJEMPLO DE USO Y TESTS
# ============================================================================

if __name__ == "__main__":
    import tempfile
    from pathlib import Path
    
    print("=" * 70)
    print("⏰ EJEMPLO DE USO - ALARM SERVICE")
    print("=" * 70)
    
    # Crear servicio con archivo temporal
    service = AlarmService()
    
    # Ejemplo 1: Crear alarmas
    print("\n1️⃣ Crear alarmas:")
    alarm1 = service.create_alarm(AlarmCreate(
        time="07:00",
        label="Despertar",
        days=["Lun", "Mar", "Mié", "Jue", "Vie"]
    ))
    print(f"   ✅ Creada: {alarm1.time} - {alarm1.label}")
    
    alarm2 = service.create_alarm(AlarmCreate(
        time="14:00",
        label="Almuerzo"
    ))
    print(f"   ✅ Creada: {alarm2.time} - {alarm2.label}")
    
    alarm3 = service.create_alarm(AlarmCreate(
        time="22:00",
        label="Dormir",
        days=["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    ))
    print(f"   ✅ Creada: {alarm3.time} - {alarm3.label}")
    
    # Ejemplo 2: Listar todas las alarmas (ordenadas)
    print("\n2️⃣ Todas las alarmas (ordenadas por hora):")
    for alarm in service.get_all_alarms():
        status = "🔔" if alarm.enabled else "🔕"
        print(f"   {status} {alarm.time} - {alarm.label} ({alarm.get_days_formatted()})")
    
    # Ejemplo 3: Obtener próxima alarma
    print("\n3️⃣ Próxima alarma:")
    next_alarm = service.get_next_alarm()
    if next_alarm:
        print(f"   ⏰ {next_alarm.time} - {next_alarm.label}")
    
    # Ejemplo 4: Navegación circular
    print("\n4️⃣ Navegación circular desde alarma 1:")
    current = alarm1
    print(f"   Actual: {current.time} - {current.label}")
    
    next_alarm = service.navigate_alarm(current.id, "next")
    print(f"   Siguiente: {next_alarm.time} - {next_alarm.label}")
    
    next_next = service.navigate_alarm(next_alarm.id, "next")
    print(f"   Siguiente: {next_next.time} - {next_next.label}")
    
    prev_alarm = service.navigate_alarm(current.id, "prev")
    print(f"   Anterior: {prev_alarm.time} - {prev_alarm.label}")
    
    # Ejemplo 5: Toggle alarma
    print("\n5️⃣ Desactivar alarma:")
    toggled = service.toggle_alarm(alarm2.id)
    status = "activa" if toggled.enabled else "inactiva"
    print(f"   Alarma {alarm2.time} ahora está {status}")
    
    # Ejemplo 6: Actualizar alarma
    print("\n6️⃣ Actualizar alarma (cambiar hora):")
    updated = service.update_alarm(alarm2.id, AlarmUpdate(time="13:30"))
    print(f"   Alarma actualizada: {updated.time} - {updated.label}")
    
    # Verificar que se reordenó
    print("   Orden después de actualizar:")
    for alarm in service.get_all_alarms():
        print(f"      {alarm.time} - {alarm.label}")
    
    # Ejemplo 7: Estadísticas
    print("\n7️⃣ Estadísticas:")
    print(f"   Total de alarmas: {service.count_alarms()}")
    print(f"   Alarmas activas: {service.count_active_alarms()}")
    
    # Ejemplo 8: Eliminar alarma
    print("\n8️⃣ Eliminar alarma:")
    deleted = service.delete_alarm(alarm3.id)
    print(f"   ✅ Alarma eliminada: {deleted}")
    print(f"   Total restante: {service.count_alarms()}")
    
    print("\n" + "=" * 70)