"""
Modelos Pydantic para Configuración de la aplicación.
Define las preferencias y ajustes del usuario para el reloj.
"""

from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator


# ============================================================================
# CONSTANTES
# ============================================================================

# Sonidos de alarma disponibles (deben coincidir con archivos en /public/sounds/alarms/)
AVAILABLE_SOUNDS = [
    "classic",
    "gentle",
    "radar",
    "beacon",
    "chimes",
    "digital"
]

# Formatos de hora disponibles
TIME_FORMATS = ["12h", "24h"]

# Temas disponibles
AVAILABLE_THEMES = ["light", "dark", "auto"]


# ============================================================================
# MODELO PRINCIPAL - SETTINGS
# ============================================================================

class Settings(BaseModel):
    """
    Modelo principal para la configuración de la aplicación.
    
    Almacena las preferencias del usuario sobre formato de hora,
    sonidos de alarma, volumen y tema.
    
    Attributes:
        time_format: Formato de hora (12h o 24h)
        alarm_sound: Sonido de alarma seleccionado
        alarm_volume: Volumen de las alarmas (0-100)
        theme: Tema de la aplicación (light, dark, auto)
    """
    
    time_format: Literal["12h", "24h"] = Field(
        default="24h",
        description="Formato de visualización de hora"
    )
    
    alarm_sound: str = Field(
        default="classic",
        description="Sonido de alarma seleccionado",
        examples=["classic", "gentle", "radar"]
    )
    
    alarm_volume: int = Field(
        default=50,
        description="Volumen de las alarmas (0-100)",
        ge=0,
        le=100
    )
    
    theme: Literal["light", "dark", "auto"] = Field(
        default="dark",
        description="Tema de la aplicación"
    )
    
    # ========================================================================
    # VALIDADORES
    # ========================================================================
    
    @field_validator('alarm_volume')
    @classmethod
    def validate_volume_range(cls, v: int) -> int:
        """
        Valida que el volumen esté entre 0 y 100.
        
        Args:
            v: Valor del volumen
            
        Returns:
            int: Volumen validado
            
        Raises:
            ValueError: Si el volumen está fuera del rango
        """
        if v < 0 or v > 100:
            raise ValueError(
                f"El volumen debe estar entre 0 y 100, recibido: {v}"
            )
        return v
    
    @field_validator('alarm_sound')
    @classmethod
    def validate_alarm_sound(cls, v: str) -> str:
        """
        Valida que el sonido de alarma sea uno de los disponibles.
        
        Args:
            v: Nombre del sonido
            
        Returns:
            str: Sonido validado
            
        Raises:
            ValueError: Si el sonido no está disponible
        """
        if v not in AVAILABLE_SOUNDS:
            raise ValueError(
                f"Sonido de alarma inválido: '{v}'. "
                f"Sonidos disponibles: {', '.join(AVAILABLE_SOUNDS)}"
            )
        return v
    
    # ========================================================================
    # MÉTODOS HELPERS
    # ========================================================================
    
    def get_sound_file_path(self) -> str:
        """
        Retorna la ruta al archivo de sonido de alarma.
        
        Returns:
            str: Ruta relativa al archivo de sonido
        """
        return f"/sounds/alarms/{self.alarm_sound}.mp3"
    
    def is_volume_muted(self) -> bool:
        """
        Verifica si el volumen está en mute (0).
        
        Returns:
            bool: True si está muteado
        """
        return self.alarm_volume == 0
    
    def is_volume_max(self) -> bool:
        """
        Verifica si el volumen está al máximo (100).
        
        Returns:
            bool: True si está al máximo
        """
        return self.alarm_volume == 100
    
    def get_volume_level_description(self) -> str:
        """
        Retorna una descripción del nivel de volumen.
        
        Returns:
            str: Descripción ("Silenciado", "Bajo", "Medio", "Alto")
        """
        if self.alarm_volume == 0:
            return "Silenciado"
        elif self.alarm_volume <= 25:
            return "Bajo"
        elif self.alarm_volume <= 50:
            return "Medio"
        elif self.alarm_volume <= 75:
            return "Alto"
        else:
            return "Muy alto"
    
    def format_time_example(self, hour: int = 14, minute: int = 30) -> str:
        """
        Retorna un ejemplo de cómo se vería una hora con el formato actual.
        
        Args:
            hour: Hora en formato 24h (default: 14)
            minute: Minuto (default: 30)
            
        Returns:
            str: Hora formateada según las preferencias
        """
        if self.time_format == "12h":
            period = "PM" if hour >= 12 else "AM"
            display_hour = hour % 12
            if display_hour == 0:
                display_hour = 12
            return f"{display_hour:02d}:{minute:02d} {period}"
        else:
            return f"{hour:02d}:{minute:02d}"
    
    def to_display_dict(self) -> dict:
        """
        Retorna un diccionario con información formateada para la UI.
        
        Returns:
            dict: Configuración formateada
        """
        return {
            "time_format": self.time_format,
            "time_format_example": self.format_time_example(),
            "alarm_sound": self.alarm_sound,
            "alarm_sound_path": self.get_sound_file_path(),
            "alarm_volume": self.alarm_volume,
            "volume_level": self.get_volume_level_description(),
            "theme": self.theme,
        }
    
    class Config:
        json_schema_extra = {
            "example": {
                "time_format": "24h",
                "alarm_sound": "classic",
                "alarm_volume": 50,
                "theme": "dark"
            }
        }


# ============================================================================
# MODELO DE ACTUALIZACIÓN - SETTINGS UPDATE
# ============================================================================

class SettingsUpdate(BaseModel):
    """
    Modelo para actualizar la configuración.
    
    Todos los campos son opcionales. Solo se actualizan los campos
    que se proporcionen.
    
    Attributes:
        time_format: Nuevo formato de hora (opcional)
        alarm_sound: Nuevo sonido de alarma (opcional)
        alarm_volume: Nuevo volumen (opcional)
        theme: Nuevo tema (opcional)
    """
    
    time_format: Optional[Literal["12h", "24h"]] = Field(
        default=None,
        description="Nuevo formato de hora"
    )
    
    alarm_sound: Optional[str] = Field(
        default=None,
        description="Nuevo sonido de alarma"
    )
    
    alarm_volume: Optional[int] = Field(
        default=None,
        description="Nuevo volumen (0-100)",
        ge=0,
        le=100
    )
    
    theme: Optional[Literal["light", "dark", "auto"]] = Field(
        default=None,
        description="Nuevo tema"
    )
    
    # ========================================================================
    # VALIDADORES
    # ========================================================================
    
    @field_validator('alarm_volume')
    @classmethod
    def validate_volume_range(cls, v: Optional[int]) -> Optional[int]:
        """Valida el volumen si se proporciona."""
        if v is not None and (v < 0 or v > 100):
            raise ValueError(f"El volumen debe estar entre 0 y 100")
        return v
    
    @field_validator('alarm_sound')
    @classmethod
    def validate_alarm_sound(cls, v: Optional[str]) -> Optional[str]:
        """Valida el sonido si se proporciona."""
        if v is not None and v not in AVAILABLE_SOUNDS:
            raise ValueError(
                f"Sonido inválido: '{v}'. "
                f"Disponibles: {', '.join(AVAILABLE_SOUNDS)}"
            )
        return v
    
    def has_changes(self) -> bool:
        """
        Verifica si hay algún cambio en la actualización.
        
        Returns:
            bool: True si hay al menos un campo no None
        """
        return any([
            self.time_format is not None,
            self.alarm_sound is not None,
            self.alarm_volume is not None,
            self.theme is not None,
        ])
    
    class Config:
        json_schema_extra = {
            "example": {
                "alarm_volume": 75,
                "theme": "light"
            }
        }


# ============================================================================
# MODELO DE RESPUESTA - SETTINGS RESPONSE
# ============================================================================

class SettingsResponse(Settings):
    """
    Modelo de respuesta extendido con información adicional.
    
    Incluye metadata útil para la UI.
    """
    
    available_sounds: list[str] = Field(
        default=AVAILABLE_SOUNDS,
        description="Lista de sonidos disponibles"
    )
    
    available_themes: list[str] = Field(
        default=AVAILABLE_THEMES,
        description="Lista de temas disponibles"
    )
    
    available_time_formats: list[str] = Field(
        default=TIME_FORMATS,
        description="Lista de formatos de hora disponibles"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "time_format": "24h",
                "alarm_sound": "classic",
                "alarm_volume": 50,
                "theme": "dark",
                "available_sounds": AVAILABLE_SOUNDS,
                "available_themes": AVAILABLE_THEMES,
                "available_time_formats": TIME_FORMATS
            }
        }


# ============================================================================
# TESTS Y EJEMPLOS
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("⚙️  EJEMPLOS DE MODELOS DE CONFIGURACIÓN")
    print("=" * 70)
    
    # Ejemplo 1: Configuración por defecto
    print("\n1️⃣ Configuración por defecto:")
    settings = Settings()
    print(f"   Formato de hora: {settings.time_format}")
    print(f"   Sonido: {settings.alarm_sound}")
    print(f"   Volumen: {settings.alarm_volume}% ({settings.get_volume_level_description()})")
    print(f"   Tema: {settings.theme}")
    print(f"   Ejemplo de hora: {settings.format_time_example()}")
    
    # Ejemplo 2: Configuración personalizada
    print("\n2️⃣ Configuración personalizada:")
    custom = Settings(
        time_format="12h",
        alarm_sound="gentle",
        alarm_volume=75,
        theme="light"
    )
    print(f"   {custom.model_dump_json(indent=2)}")
    print(f"   Ruta del sonido: {custom.get_sound_file_path()}")
    print(f"   Ejemplo: {custom.format_time_example()}")
    
    # Ejemplo 3: Actualización parcial
    print("\n3️⃣ Actualización parcial (SettingsUpdate):")
    update = SettingsUpdate(
        alarm_volume=80,
        theme="dark"
    )
    print(f"   {update.model_dump_json(indent=2)}")
    print(f"   ¿Tiene cambios?: {update.has_changes()}")
    
    # Ejemplo 4: Display dict
    print("\n4️⃣ Formato para UI:")
    display = settings.to_display_dict()
    for key, value in display.items():
        print(f"   {key}: {value}")
    
    # Ejemplo 5: SettingsResponse con metadata
    print("\n5️⃣ Respuesta con metadata (SettingsResponse):")
    response = SettingsResponse(
        time_format="24h",
        alarm_sound="classic",
        alarm_volume=50,
        theme="dark"
    )
    print(f"   Sonidos disponibles: {response.available_sounds}")
    print(f"   Temas disponibles: {response.available_themes}")
    
    # Ejemplo 6: Validaciones
    print("\n6️⃣ Pruebas de validación:")
    
    # Volumen inválido
    try:
        invalid = Settings(alarm_volume=150)
    except Exception as e:
        print(f"   ❌ Volumen inválido: {e}")
    
    # Sonido inválido
    try:
        invalid = Settings(alarm_sound="inexistente")
    except Exception as e:
        print(f"   ❌ Sonido inválido: {e}")
    
    # Volumen válido
    try:
        valid = Settings(alarm_volume=0)
        print(f"   ✅ Volumen 0 válido: {valid.is_volume_muted()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Ejemplo 7: Diferentes niveles de volumen
    print("\n7️⃣ Descripción de niveles de volumen:")
    test_volumes = [0, 15, 40, 60, 85, 100]
    for vol in test_volumes:
        s = Settings(alarm_volume=vol)
        print(f"   Volumen {vol:3d}%: {s.get_volume_level_description()}")
    
    print("\n" + "=" * 70)