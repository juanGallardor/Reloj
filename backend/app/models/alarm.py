"""
Modelos Pydantic para Alarmas.
Define la estructura de datos y validaciones para el sistema de alarmas.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator
import re


# ============================================================================
# CONSTANTES
# ============================================================================

VALID_DAYS = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
TIME_PATTERN = re.compile(r'^([01]?[0-9]|2[0-3]):([0-5][0-9])$')


# ============================================================================
# MODELO PRINCIPAL - ALARM
# ============================================================================

class Alarm(BaseModel):
    """
    Modelo principal para una alarma.
    
    Representa una alarma con todos sus atributos para el sistema de reloj.
    Usado para almacenamiento y respuestas de la API.
    
    Attributes:
        id: Identificador único de la alarma
        time: Hora en formato HH:MM (24 horas)
        label: Etiqueta descriptiva de la alarma
        enabled: Si la alarma está activa o no
        days: Lista de días en que se repite la alarma
        created_at: Fecha y hora de creación de la alarma
    """
    
    id: int = Field(
        ...,
        description="ID único de la alarma",
        ge=1
    )
    
    time: str = Field(
        ...,
        description="Hora de la alarma en formato HH:MM (00:00 - 23:59)",
        examples=["07:30", "14:15", "22:00"]
    )
    
    label: str = Field(
        ...,
        description="Etiqueta descriptiva de la alarma",
        max_length=100,
        examples=["Despertar", "Reunión", "Tomar medicina"]
    )
    
    enabled: bool = Field(
        default=True,
        description="Indica si la alarma está activa"
    )
    
    days: list[str] = Field(
        default_factory=list,
        description="Días de la semana en que se repite la alarma",
        examples=[["Lun", "Mar", "Mié", "Jue", "Vie"]]
    )
    
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Fecha y hora de creación de la alarma"
    )
    
    # ========================================================================
    # VALIDADORES
    # ========================================================================
    
    @field_validator('time')
    @classmethod
    def validate_time_format(cls, v: str) -> str:
        """
        Valida que el tiempo tenga formato HH:MM válido (00:00 - 23:59).
        
        Args:
            v: String con el tiempo a validar
            
        Returns:
            str: Tiempo validado
            
        Raises:
            ValueError: Si el formato no es válido
        """
        if not TIME_PATTERN.match(v):
            raise ValueError(
                f"Formato de hora inválido: '{v}'. "
                f"Debe ser HH:MM (00:00 - 23:59)"
            )
        
        # Validar que la hora sea válida
        hours, minutes = map(int, v.split(':'))
        if hours > 23 or minutes > 59:
            raise ValueError(
                f"Hora fuera de rango: {v}. "
                f"Las horas deben estar entre 00-23 y los minutos entre 00-59"
            )
        
        return v
    
    @field_validator('label')
    @classmethod
    def validate_label(cls, v: str) -> str:
        """
        Valida que la etiqueta no esté vacía.
        
        Args:
            v: String con la etiqueta
            
        Returns:
            str: Etiqueta validada y sin espacios extra
            
        Raises:
            ValueError: Si la etiqueta está vacía
        """
        v = v.strip()
        if not v:
            raise ValueError("La etiqueta no puede estar vacía")
        return v
    
    @field_validator('days')
    @classmethod
    def validate_days(cls, v: list[str]) -> list[str]:
        """
        Valida que los días sean válidos y sin duplicados.
        
        Args:
            v: Lista de días
            
        Returns:
            list[str]: Lista de días validados
            
        Raises:
            ValueError: Si hay días inválidos o duplicados
        """
        # Permitir lista vacía (alarma de una sola vez)
        if not v:
            return v
        
        # Validar días únicos
        if len(v) != len(set(v)):
            raise ValueError("No puede haber días duplicados")
        
        # Validar que todos los días sean válidos
        invalid_days = [day for day in v if day not in VALID_DAYS]
        if invalid_days:
            raise ValueError(
                f"Días inválidos: {invalid_days}. "
                f"Los días válidos son: {VALID_DAYS}"
            )
        
        return v
    
    # ========================================================================
    # MÉTODOS HELPERS
    # ========================================================================
    
    def is_repeating(self) -> bool:
        """Verifica si la alarma se repite (tiene días configurados)."""
        return len(self.days) > 0
    
    def is_daily(self) -> bool:
        """Verifica si la alarma es diaria (todos los días)."""
        return len(self.days) == 7
    
    def is_weekday(self) -> bool:
        """Verifica si la alarma es solo días de semana."""
        weekdays = ["Lun", "Mar", "Mié", "Jue", "Vie"]
        return set(self.days) == set(weekdays)
    
    def is_weekend(self) -> bool:
        """Verifica si la alarma es solo fines de semana."""
        weekend = ["Sáb", "Dom"]
        return set(self.days) == set(weekend)
    
    def get_days_formatted(self) -> str:
        """
        Retorna los días formateados para mostrar.
        
        Returns:
            str: "Diaria", "Lun-Vie", "Sáb, Dom", etc.
        """
        if self.is_daily():
            return "Diaria"
        elif self.is_weekday():
            return "Lun-Vie"
        elif self.is_weekend():
            return "Fin de semana"
        elif not self.days:
            return "Una vez"
        else:
            return ", ".join(self.days)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "time": "07:30",
                "label": "Despertar",
                "enabled": True,
                "days": ["Lun", "Mar", "Mié", "Jue", "Vie"],
                "created_at": "2025-10-11T07:00:00"
            }
        }


# ============================================================================
# MODELO DE CREACIÓN - ALARM CREATE
# ============================================================================

class AlarmCreate(BaseModel):
    """
    Modelo para crear una nueva alarma.
    
    No incluye ID ni created_at ya que se generan automáticamente.
    
    Attributes:
        time: Hora de la alarma (requerido)
        label: Etiqueta descriptiva
        enabled: Si está activa (default True)
        days: Días de repetición (default lista vacía)
    """
    
    time: str = Field(
        ...,
        description="Hora de la alarma en formato HH:MM",
        examples=["07:30", "14:15"]
    )
    
    label: str = Field(
        default="Nueva Alarma",
        description="Etiqueta de la alarma",
        max_length=100
    )
    
    enabled: bool = Field(
        default=True,
        description="Si la alarma está activa"
    )
    
    days: list[str] = Field(
        default_factory=list,
        description="Días de repetición"
    )
    
    # Reutilizar validadores de Alarm
    @field_validator('time')
    @classmethod
    def validate_time_format(cls, v: str) -> str:
        if not TIME_PATTERN.match(v):
            raise ValueError(
                f"Formato de hora inválido: '{v}'. Debe ser HH:MM (00:00 - 23:59)"
            )
        hours, minutes = map(int, v.split(':'))
        if hours > 23 or minutes > 59:
            raise ValueError(f"Hora fuera de rango: {v}")
        return v
    
    @field_validator('label')
    @classmethod
    def validate_label(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("La etiqueta no puede estar vacía")
        return v
    
    @field_validator('days')
    @classmethod
    def validate_days(cls, v: list[str]) -> list[str]:
        if not v:
            return v
        if len(v) != len(set(v)):
            raise ValueError("No puede haber días duplicados")
        invalid_days = [day for day in v if day not in VALID_DAYS]
        if invalid_days:
            raise ValueError(f"Días inválidos: {invalid_days}")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "time": "07:30",
                "label": "Despertar temprano",
                "enabled": True,
                "days": ["Lun", "Mar", "Mié", "Jue", "Vie"]
            }
        }


# ============================================================================
# MODELO DE ACTUALIZACIÓN - ALARM UPDATE
# ============================================================================

class AlarmUpdate(BaseModel):
    """
    Modelo para actualizar una alarma existente.
    
    Todos los campos son opcionales. Solo se actualizan los campos
    que se proporcionen.
    
    Attributes:
        time: Nueva hora (opcional)
        label: Nueva etiqueta (opcional)
        enabled: Nuevo estado (opcional)
        days: Nuevos días de repetición (opcional)
    """
    
    time: Optional[str] = Field(
        default=None,
        description="Nueva hora de la alarma",
        examples=["08:00"]
    )
    
    label: Optional[str] = Field(
        default=None,
        description="Nueva etiqueta",
        max_length=100
    )
    
    enabled: Optional[bool] = Field(
        default=None,
        description="Nuevo estado activo/inactivo"
    )
    
    days: Optional[list[str]] = Field(
        default=None,
        description="Nuevos días de repetición"
    )
    
    # Validadores solo si el campo no es None
    @field_validator('time')
    @classmethod
    def validate_time_format(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not TIME_PATTERN.match(v):
            raise ValueError(f"Formato de hora inválido: '{v}'")
        hours, minutes = map(int, v.split(':'))
        if hours > 23 or minutes > 59:
            raise ValueError(f"Hora fuera de rango: {v}")
        return v
    
    @field_validator('label')
    @classmethod
    def validate_label(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("La etiqueta no puede estar vacía")
        return v
    
    @field_validator('days')
    @classmethod
    def validate_days(cls, v: Optional[list[str]]) -> Optional[list[str]]:
        if v is None:
            return v
        if len(v) != len(set(v)):
            raise ValueError("No puede haber días duplicados")
        invalid_days = [day for day in v if day not in VALID_DAYS]
        if invalid_days:
            raise ValueError(f"Días inválidos: {invalid_days}")
        return v
    
    @model_validator(mode='after')
    def check_at_least_one_field(self) -> 'AlarmUpdate':
        """Valida que al menos un campo esté presente para actualizar."""
        if all(getattr(self, field) is None for field in ['time', 'label', 'enabled', 'days']):
            raise ValueError("Debe proporcionar al menos un campo para actualizar")
        return self
    
    class Config:
        json_schema_extra = {
            "example": {
                "label": "Despertar más tarde",
                "time": "08:00"
            }
        }


# ============================================================================
# TESTS Y EJEMPLOS
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("⏰ EJEMPLOS DE MODELOS DE ALARMA")
    print("=" * 70)
    
    # Ejemplo 1: Crear alarma completa
    print("\n1️⃣ Crear alarma completa:")
    alarm = Alarm(
        id=1,
        time="07:30",
        label="Despertar",
        enabled=True,
        days=["Lun", "Mar", "Mié", "Jue", "Vie"]
    )
    print(f"   {alarm.model_dump_json(indent=2)}")
    print(f"   Repetición: {alarm.get_days_formatted()}")
    
    # Ejemplo 2: AlarmCreate
    print("\n2️⃣ Crear nueva alarma (AlarmCreate):")
    new_alarm = AlarmCreate(
        time="14:30",
        label="Reunión importante"
    )
    print(f"   {new_alarm.model_dump_json(indent=2)}")
    
    # Ejemplo 3: AlarmUpdate
    print("\n3️⃣ Actualizar alarma (AlarmUpdate):")
    update = AlarmUpdate(time="08:00", enabled=False)
    print(f"   {update.model_dump_json(indent=2)}")
    
    # Ejemplo 4: Validación de errores
    print("\n4️⃣ Pruebas de validación:")
    try:
        invalid = AlarmCreate(time="25:00", label="Inválida")
    except Exception as e:
        print(f"   ❌ Hora inválida: {e}")
    
    try:
        invalid_days = AlarmCreate(time="07:00", days=["Lunes", "Martes"])
    except Exception as e:
        print(f"   ❌ Días inválidos: {e}")
    
    print("\n" + "=" * 70)