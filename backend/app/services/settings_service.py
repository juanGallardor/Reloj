"""
Servicio de gestión de configuración de la aplicación.
Maneja las preferencias del usuario para el reloj.
"""

from typing import Optional
import logging

from app.models.settings import Settings, SettingsUpdate, SettingsResponse
from app.database.json_db import JSONDatabase
from app.config import get_settings as get_app_settings

logger = logging.getLogger(__name__)


class SettingsService:
    """
    Servicio para gestionar la configuración de la aplicación.
    
    No usa lista circular doble ya que solo maneja un objeto de configuración.
    
    Attributes:
        settings: Configuración actual del usuario
        json_db: Base de datos JSON para persistencia
    """
    
    def __init__(self):
        """Inicializa el servicio y carga configuración desde JSON."""
        app_settings = get_app_settings()
        self.json_db = JSONDatabase(app_settings.SETTINGS_FILE)
        self.settings = self._load_from_json()
        logger.info("SettingsService inicializado")
    
    # ========================================================================
    # MÉTODOS PÚBLICOS - GESTIÓN DE CONFIGURACIÓN
    # ========================================================================
    
    def get_settings(self) -> Settings:
        """
        Obtiene la configuración actual.
        
        Returns:
            Settings: Configuración actual
        """
        return self.settings
    
    def get_settings_response(self) -> SettingsResponse:
        """
        Obtiene la configuración con metadata adicional.
        
        Returns:
            SettingsResponse: Configuración con opciones disponibles
        """
        return SettingsResponse(
            time_format=self.settings.time_format,
            alarm_sound=self.settings.alarm_sound,
            alarm_volume=self.settings.alarm_volume,
            theme=self.settings.theme,
        )
    
    def update_settings(self, update_data: SettingsUpdate) -> Settings:
        """
        Actualiza la configuración del usuario.
        
        Solo actualiza los campos proporcionados, manteniendo el resto.
        
        Args:
            update_data: Datos a actualizar
            
        Returns:
            Settings: Configuración actualizada
        """
        # Validar que hay al menos un cambio
        if not update_data.has_changes():
            logger.warning("No hay cambios en la configuración")
            return self.settings
        
        # Actualizar solo campos proporcionados
        if update_data.time_format is not None:
            self.settings.time_format = update_data.time_format
            logger.info(f"Formato de hora actualizado: {update_data.time_format}")
        
        if update_data.alarm_sound is not None:
            self.settings.alarm_sound = update_data.alarm_sound
            logger.info(f"Sonido de alarma actualizado: {update_data.alarm_sound}")
        
        if update_data.alarm_volume is not None:
            self.settings.alarm_volume = update_data.alarm_volume
            logger.info(f"Volumen actualizado: {update_data.alarm_volume}%")
        
        if update_data.theme is not None:
            self.settings.theme = update_data.theme
            logger.info(f"Tema actualizado: {update_data.theme}")
        
        # Persistir cambios
        self._save_to_json()
        
        logger.info("Configuración actualizada exitosamente")
        return self.settings
    
    def reset_to_defaults(self) -> Settings:
        """
        Restaura la configuración a valores por defecto.
        
        Returns:
            Settings: Configuración por defecto
        """
        # Crear configuración por defecto
        self.settings = Settings()
        
        # Persistir
        self._save_to_json()
        
        logger.info("Configuración restaurada a valores por defecto")
        return self.settings
    
    # ========================================================================
    # MÉTODOS PARA CAMPOS ESPECÍFICOS
    # ========================================================================
    
    def update_time_format(self, time_format: str) -> Settings:
        """
        Actualiza solo el formato de hora.
        
        Args:
            time_format: "12h" o "24h"
            
        Returns:
            Settings: Configuración actualizada
        """
        update_data = SettingsUpdate(time_format=time_format)
        return self.update_settings(update_data)
    
    def update_alarm_sound(self, sound: str) -> Settings:
        """
        Actualiza solo el sonido de alarma.
        
        Args:
            sound: Nombre del sonido
            
        Returns:
            Settings: Configuración actualizada
        """
        update_data = SettingsUpdate(alarm_sound=sound)
        return self.update_settings(update_data)
    
    def update_alarm_volume(self, volume: int) -> Settings:
        """
        Actualiza solo el volumen.
        
        Args:
            volume: Volumen (0-100)
            
        Returns:
            Settings: Configuración actualizada
        """
        update_data = SettingsUpdate(alarm_volume=volume)
        return self.update_settings(update_data)
    
    def update_theme(self, theme: str) -> Settings:
        """
        Actualiza solo el tema.
        
        Args:
            theme: "light", "dark" o "auto"
            
        Returns:
            Settings: Configuración actualizada
        """
        update_data = SettingsUpdate(theme=theme)
        return self.update_settings(update_data)
    
    def toggle_mute(self) -> Settings:
        """
        Activa/desactiva el mute del volumen.
        
        Si el volumen es > 0, lo pone en 0.
        Si el volumen es 0, lo pone en 50.
        
        Returns:
            Settings: Configuración actualizada
        """
        new_volume = 0 if self.settings.alarm_volume > 0 else 50
        return self.update_alarm_volume(new_volume)
    
    def increase_volume(self, amount: int = 10) -> Settings:
        """
        Aumenta el volumen en una cantidad específica.
        
        Args:
            amount: Cantidad a aumentar (default: 10)
            
        Returns:
            Settings: Configuración actualizada
        """
        new_volume = min(100, self.settings.alarm_volume + amount)
        return self.update_alarm_volume(new_volume)
    
    def decrease_volume(self, amount: int = 10) -> Settings:
        """
        Disminuye el volumen en una cantidad específica.
        
        Args:
            amount: Cantidad a disminuir (default: 10)
            
        Returns:
            Settings: Configuración actualizada
        """
        new_volume = max(0, self.settings.alarm_volume - amount)
        return self.update_alarm_volume(new_volume)
    
    # ========================================================================
    # MÉTODOS DE CONSULTA
    # ========================================================================
    
    def is_12h_format(self) -> bool:
        """
        Verifica si está en formato 12h.
        
        Returns:
            bool: True si es formato 12h
        """
        return self.settings.time_format == "12h"
    
    def is_24h_format(self) -> bool:
        """
        Verifica si está en formato 24h.
        
        Returns:
            bool: True si es formato 24h
        """
        return self.settings.time_format == "24h"
    
    def is_muted(self) -> bool:
        """
        Verifica si el volumen está muteado.
        
        Returns:
            bool: True si el volumen es 0
        """
        return self.settings.is_volume_muted()
    
    def get_volume_percentage(self) -> float:
        """
        Obtiene el volumen como porcentaje normalizado (0.0 - 1.0).
        
        Returns:
            float: Volumen normalizado
        """
        return self.settings.alarm_volume / 100.0
    
    # ========================================================================
    # MÉTODOS PRIVADOS - PERSISTENCIA
    # ========================================================================
    
    def _load_from_json(self) -> Settings:
        """
        Carga configuración desde el archivo JSON.
        
        Si no existe o hay error, retorna configuración por defecto.
        
        Returns:
            Settings: Configuración cargada
        """
        try:
            data = self.json_db.read_as_dict()
            
            if not data:
                # No existe archivo, usar defaults
                logger.info("No se encontró configuración, usando valores por defecto")
                settings = Settings()
                self._save_to_json()  # Guardar defaults
                return settings
            
            # Cargar desde JSON
            settings = Settings(**data)
            logger.info("Configuración cargada desde JSON")
            return settings
            
        except Exception as e:
            logger.error(f"Error cargando configuración: {e}")
            logger.info("Usando configuración por defecto")
            return Settings()
    
    def _save_to_json(self) -> None:
        """Guarda la configuración actual en JSON."""
        try:
            data = self.settings.model_dump(mode='json')
            self.json_db.write(data)
            logger.debug("Configuración guardada en JSON")
        except Exception as e:
            logger.error(f"Error guardando configuración: {e}")
    
    def export_settings(self) -> dict:
        """
        Exporta la configuración como diccionario.
        
        Útil para backup o transferencia.
        
        Returns:
            dict: Configuración como diccionario
        """
        return self.settings.model_dump()
    
    def import_settings(self, data: dict) -> Settings:
        """
        Importa configuración desde un diccionario.
        
        Args:
            data: Diccionario con configuración
            
        Returns:
            Settings: Configuración importada
        """
        try:
            self.settings = Settings(**data)
            self._save_to_json()
            logger.info("Configuración importada exitosamente")
            return self.settings
        except Exception as e:
            logger.error(f"Error importando configuración: {e}")
            raise


# ============================================================================
# EJEMPLO DE USO Y TESTS
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("⚙️  EJEMPLO DE USO - SETTINGS SERVICE")
    print("=" * 70)
    
    # Crear servicio
    service = SettingsService()
    
    # Ejemplo 1: Obtener configuración actual
    print("\n1️⃣ Configuración actual:")
    settings = service.get_settings()
    print(f"   Formato de hora: {settings.time_format}")
    print(f"   Sonido: {settings.alarm_sound}")
    print(f"   Volumen: {settings.alarm_volume}% ({settings.get_volume_level_description()})")
    print(f"   Tema: {settings.theme}")
    print(f"   Ejemplo de hora: {settings.format_time_example()}")
    
    # Ejemplo 2: Actualizar múltiples campos
    print("\n2️⃣ Actualizar configuración:")
    update_data = SettingsUpdate(
        time_format="12h",
        alarm_sound="gentle",
        alarm_volume=75
    )
    updated = service.update_settings(update_data)
    print(f"   ✅ Formato: {updated.time_format}")
    print(f"   ✅ Sonido: {updated.alarm_sound}")
    print(f"   ✅ Volumen: {updated.alarm_volume}%")
    print(f"   Ejemplo: {updated.format_time_example()}")
    
    # Ejemplo 3: Actualizar campo individual
    print("\n3️⃣ Cambiar solo el tema:")
    service.update_theme("light")
    print(f"   ✅ Tema: {service.get_settings().theme}")
    
    # Ejemplo 4: Control de volumen
    print("\n4️⃣ Control de volumen:")
    print(f"   Volumen inicial: {service.get_settings().alarm_volume}%")
    
    service.increase_volume(15)
    print(f"   Después de aumentar 15%: {service.get_settings().alarm_volume}%")
    
    service.decrease_volume(20)
    print(f"   Después de disminuir 20%: {service.get_settings().alarm_volume}%")
    
    # Ejemplo 5: Mute
    print("\n5️⃣ Toggle mute:")
    service.toggle_mute()
    print(f"   ¿Muteado?: {service.is_muted()}")
    print(f"   Volumen: {service.get_settings().alarm_volume}%")
    
    service.toggle_mute()
    print(f"   Después de toggle: {service.get_settings().alarm_volume}%")
    
    # Ejemplo 6: Respuesta con metadata
    print("\n6️⃣ Respuesta con metadata:")
    response = service.get_settings_response()
    print(f"   Sonidos disponibles: {response.available_sounds}")
    print(f"   Temas disponibles: {response.available_themes}")
    
    # Ejemplo 7: Exportar/Importar
    print("\n7️⃣ Exportar configuración:")
    exported = service.export_settings()
    print(f"   {exported}")
    
    # Ejemplo 8: Restaurar defaults
    print("\n8️⃣ Restaurar valores por defecto:")
    service.reset_to_defaults()
    defaults = service.get_settings()
    print(f"   Formato: {defaults.time_format}")
    print(f"   Sonido: {defaults.alarm_sound}")
    print(f"   Volumen: {defaults.alarm_volume}%")
    print(f"   Tema: {defaults.theme}")
    
    # Ejemplo 9: Consultas
    print("\n9️⃣ Consultas:")
    print(f"   ¿Formato 12h?: {service.is_12h_format()}")
    print(f"   ¿Formato 24h?: {service.is_24h_format()}")
    print(f"   ¿Muteado?: {service.is_muted()}")
    print(f"   Volumen normalizado: {service.get_volume_percentage()}")
    
    print("\n" + "=" * 70)