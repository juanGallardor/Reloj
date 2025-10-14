"""
Modelos Pydantic para Laps del Cronómetro.
Define la estructura de datos para las vueltas registradas en el cronómetro.
"""

from datetime import datetime
from pydantic import BaseModel, Field, field_validator


# ============================================================================
# MODELO PRINCIPAL - LAP
# ============================================================================

class Lap(BaseModel):
    """
    Modelo principal para un lap (vuelta) del cronómetro.
    
    Representa una vuelta registrada con su tiempo individual,
    tiempo acumulado y metadata.
    
    Attributes:
        id: Identificador único del lap
        lap_number: Número de vuelta (1, 2, 3...)
        lap_time: Tiempo de la vuelta en segundos
        total_time: Tiempo total acumulado hasta este lap
        timestamp: Fecha y hora en que se registró el lap
    """
    
    id: int = Field(
        ...,
        description="ID único del lap",
        ge=1
    )
    
    lap_number: int = Field(
        ...,
        description="Número de la vuelta",
        ge=1,
        examples=[1, 2, 3]
    )
    
    lap_time: float = Field(
        ...,
        description="Tiempo de la vuelta en segundos (con 2 decimales)",
        gt=0,
        examples=[12.45, 30.78, 60.12]
    )
    
    total_time: float = Field(
        ...,
        description="Tiempo total acumulado en segundos (con 2 decimales)",
        gt=0,
        examples=[12.45, 43.23, 103.35]
    )
    
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Fecha y hora en que se registró el lap"
    )
    
    # ========================================================================
    # VALIDADORES
    # ========================================================================
    
    @field_validator('lap_time', 'total_time')
    @classmethod
    def validate_positive_time(cls, v: float) -> float:
        """
        Valida que los tiempos sean positivos y los redondea a 2 decimales.
        
        Args:
            v: Tiempo en segundos
            
        Returns:
            float: Tiempo validado y redondeado
            
        Raises:
            ValueError: Si el tiempo no es positivo
        """
        if v <= 0:
            raise ValueError("El tiempo debe ser mayor que 0")
        
        # Redondear a 2 decimales para consistencia
        return round(v, 2)
    
    @field_validator('lap_number')
    @classmethod
    def validate_lap_number(cls, v: int) -> int:
        """
        Valida que el número de lap sea positivo.
        
        Args:
            v: Número de lap
            
        Returns:
            int: Número de lap validado
            
        Raises:
            ValueError: Si el número no es positivo
        """
        if v < 1:
            raise ValueError("El número de lap debe ser mayor o igual a 1")
        return v
    
    # ========================================================================
    # MÉTODOS HELPERS
    # ========================================================================
    
    def format_time(self, time_seconds: float) -> str:
        """
        Formatea un tiempo en segundos a formato MM:SS.ms
        
        Args:
            time_seconds: Tiempo en segundos
            
        Returns:
            str: Tiempo formateado (ejemplo: "01:23.45")
        """
        minutes = int(time_seconds // 60)
        seconds = time_seconds % 60
        return f"{minutes:02d}:{seconds:05.2f}"
    
    def format_lap_time(self) -> str:
        """
        Retorna el lap_time formateado como MM:SS.ms
        
        Returns:
            str: Tiempo de vuelta formateado
        """
        return self.format_time(self.lap_time)
    
    def format_total_time(self) -> str:
        """
        Retorna el total_time formateado como MM:SS.ms
        
        Returns:
            str: Tiempo total formateado
        """
        return self.format_time(self.total_time)
    
    def get_pace_description(self) -> str:
        """
        Retorna una descripción del ritmo del lap.
        
        Returns:
            str: Descripción del ritmo ("Rápido", "Normal", "Lento")
        """
        if self.lap_time < 10:
            return "Muy rápido"
        elif self.lap_time < 30:
            return "Rápido"
        elif self.lap_time < 60:
            return "Normal"
        else:
            return "Lento"
    
    def to_display_dict(self) -> dict:
        """
        Retorna un diccionario con formato listo para mostrar en UI.
        
        Returns:
            dict: Diccionario con tiempos formateados
        """
        return {
            "id": self.id,
            "lap_number": self.lap_number,
            "lap_time_formatted": self.format_lap_time(),
            "total_time_formatted": self.format_total_time(),
            "pace": self.get_pace_description(),
            "timestamp": self.timestamp.isoformat()
        }
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "lap_number": 1,
                "lap_time": 12.45,
                "total_time": 12.45,
                "timestamp": "2025-10-11T10:30:00"
            }
        }


# ============================================================================
# MODELO DE CREACIÓN - LAP CREATE
# ============================================================================

class LapCreate(BaseModel):
    """
    Modelo para crear un nuevo lap.
    
    Solo requiere los tiempos, el resto se genera automáticamente.
    
    Attributes:
        lap_time: Tiempo de la vuelta en segundos (requerido)
        total_time: Tiempo total acumulado (requerido)
    """
    
    lap_time: float = Field(
        ...,
        description="Tiempo de la vuelta en segundos",
        gt=0,
        examples=[12.45, 30.78]
    )
    
    total_time: float = Field(
        ...,
        description="Tiempo total acumulado en segundos",
        gt=0,
        examples=[12.45, 43.23]
    )
    
    # ========================================================================
    # VALIDADORES
    # ========================================================================
    
    @field_validator('lap_time', 'total_time')
    @classmethod
    def validate_positive_time(cls, v: float) -> float:
        """Valida que los tiempos sean positivos y los redondea."""
        if v <= 0:
            raise ValueError("El tiempo debe ser mayor que 0")
        return round(v, 2)
    
    @field_validator('total_time')
    @classmethod
    def validate_total_greater_than_zero(cls, v: float) -> float:
        """Valida que el tiempo total sea positivo."""
        if v <= 0:
            raise ValueError("El tiempo total debe ser mayor que 0")
        return round(v, 2)
    
    class Config:
        json_schema_extra = {
            "example": {
                "lap_time": 12.45,
                "total_time": 12.45
            }
        }


# ============================================================================
# MODELO DE ESTADÍSTICAS - LAP STATISTICS
# ============================================================================

class LapStatistics(BaseModel):
    """
    Modelo para estadísticas de laps.
    
    Proporciona información agregada sobre todos los laps registrados.
    
    Attributes:
        total_laps: Cantidad total de laps
        fastest_lap: Lap más rápido (o None si no hay laps)
        slowest_lap: Lap más lento (o None si no hay laps)
        average_lap_time: Tiempo promedio de los laps
        total_elapsed_time: Tiempo total transcurrido
    """
    
    total_laps: int = Field(
        ...,
        description="Cantidad total de laps registrados",
        ge=0
    )
    
    fastest_lap: Lap | None = Field(
        default=None,
        description="El lap más rápido"
    )
    
    slowest_lap: Lap | None = Field(
        default=None,
        description="El lap más lento"
    )
    
    average_lap_time: float = Field(
        default=0.0,
        description="Tiempo promedio de los laps en segundos",
        ge=0
    )
    
    total_elapsed_time: float = Field(
        default=0.0,
        description="Tiempo total transcurrido en segundos",
        ge=0
    )
    
    def format_average_time(self) -> str:
        """Formatea el tiempo promedio."""
        if self.average_lap_time == 0:
            return "00:00.00"
        minutes = int(self.average_lap_time // 60)
        seconds = self.average_lap_time % 60
        return f"{minutes:02d}:{seconds:05.2f}"
    
    def format_total_time(self) -> str:
        """Formatea el tiempo total."""
        if self.total_elapsed_time == 0:
            return "00:00.00"
        minutes = int(self.total_elapsed_time // 60)
        seconds = self.total_elapsed_time % 60
        return f"{minutes:02d}:{seconds:05.2f}"
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_laps": 5,
                "fastest_lap": {
                    "id": 2,
                    "lap_number": 2,
                    "lap_time": 10.23,
                    "total_time": 25.67,
                    "timestamp": "2025-10-11T10:30:00"
                },
                "slowest_lap": {
                    "id": 4,
                    "lap_number": 4,
                    "lap_time": 18.90,
                    "total_time": 78.45,
                    "timestamp": "2025-10-11T10:32:00"
                },
                "average_lap_time": 14.56,
                "total_elapsed_time": 72.80
            }
        }


# ============================================================================
# TESTS Y EJEMPLOS
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("⏱️  EJEMPLOS DE MODELOS DE LAP")
    print("=" * 70)
    
    # Ejemplo 1: Crear lap completo
    print("\n1️⃣ Crear lap completo:")
    lap = Lap(
        id=1,
        lap_number=1,
        lap_time=12.45,
        total_time=12.45
    )
    print(f"   Lap #{lap.lap_number}")
    print(f"   Tiempo vuelta: {lap.format_lap_time()}")
    print(f"   Tiempo total: {lap.format_total_time()}")
    print(f"   Ritmo: {lap.get_pace_description()}")
    
    # Ejemplo 2: Crear varios laps
    print("\n2️⃣ Crear múltiples laps:")
    laps = [
        Lap(id=1, lap_number=1, lap_time=15.23, total_time=15.23),
        Lap(id=2, lap_number=2, lap_time=12.45, total_time=27.68),
        Lap(id=3, lap_number=3, lap_time=18.90, total_time=46.58),
    ]
    
    for lap in laps:
        print(f"   Lap #{lap.lap_number}: {lap.format_lap_time()} (Total: {lap.format_total_time()})")
    
    # Ejemplo 3: LapCreate
    print("\n3️⃣ Crear nuevo lap (LapCreate):")
    new_lap = LapCreate(lap_time=14.56, total_time=61.14)
    print(f"   {new_lap.model_dump_json(indent=2)}")
    
    # Ejemplo 4: Estadísticas
    print("\n4️⃣ Estadísticas de laps:")
    stats = LapStatistics(
        total_laps=3,
        fastest_lap=laps[1],  # 12.45
        slowest_lap=laps[2],  # 18.90
        average_lap_time=15.53,
        total_elapsed_time=46.58
    )
    print(f"   Total de laps: {stats.total_laps}")
    print(f"   Más rápido: {stats.fastest_lap.format_lap_time()}")
    print(f"   Más lento: {stats.slowest_lap.format_lap_time()}")
    print(f"   Promedio: {stats.format_average_time()}")
    print(f"   Tiempo total: {stats.format_total_time()}")
    
    # Ejemplo 5: Display dict
    print("\n5️⃣ Formato para UI:")
    display = lap.to_display_dict()
    print(f"   {display}")
    
    # Ejemplo 6: Validaciones
    print("\n6️⃣ Pruebas de validación:")
    try:
        invalid = LapCreate(lap_time=-5.0, total_time=10.0)
    except Exception as e:
        print(f"   ❌ Tiempo negativo: {e}")
    
    try:
        invalid = LapCreate(lap_time=5.123456, total_time=10.0)
        print(f"   ✅ Redondeo automático: {invalid.lap_time}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "=" * 70)