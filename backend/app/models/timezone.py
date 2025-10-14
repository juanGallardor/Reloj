"""
Modelos Pydantic para Zonas Horarias.
Define la estructura de datos para gestión de zonas horarias del reloj.
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator
import re


# ============================================================================
# CONSTANTES
# ============================================================================

# Regex para validar formato de offset UTC
# Acepta: UTC+5, UTC-5, UTC+5:30, UTC-5:45, etc.
UTC_OFFSET_PATTERN = re.compile(
    r'^UTC[+-](?:1[0-4]|[0-9])(?::(?:[03]0|45))?$'
)


# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def generate_timezone_id(country: str, city: str) -> str:
    """
    Genera un ID único para una zona horaria basado en país y ciudad.
    
    Args:
        country: Nombre del país
        city: Nombre de la ciudad
        
    Returns:
        str: ID en formato "pais-ciudad" (normalizado)
        
    Example:
        >>> generate_timezone_id("Colombia", "Bogotá")
        "colombia-bogota"
    """
    # Convertir a minúsculas y eliminar acentos/espacios
    country_normalized = country.lower().strip()
    city_normalized = city.lower().strip()
    
    # Reemplazar espacios por guiones
    country_normalized = country_normalized.replace(" ", "-")
    city_normalized = city_normalized.replace(" ", "-")
    
    # Eliminar caracteres especiales comunes
    replacements = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'ñ': 'n', 'ü': 'u', 'ä': 'a', 'ö': 'o', 'ë': 'e'
    }
    
    for old, new in replacements.items():
        country_normalized = country_normalized.replace(old, new)
        city_normalized = city_normalized.replace(old, new)
    
    return f"{country_normalized}-{city_normalized}"


# ============================================================================
# MODELO PRINCIPAL - TIMEZONE
# ============================================================================

class Timezone(BaseModel):
    """
    Modelo principal para una zona horaria.
    
    Representa una zona horaria con su país, ciudad, offset UTC
    y si está marcada como favorita.
    
    Attributes:
        id: ID único en formato "pais-ciudad"
        country: Nombre del país
        city: Nombre de la ciudad
        offset: Offset UTC (ej: "UTC-5", "UTC+5:30")
        is_favorite: Si está en la lista de favoritos
    """
    
    id: str = Field(
        ...,
        description="ID único en formato 'pais-ciudad'",
        examples=["colombia-bogota", "estados-unidos-new-york"]
    )
    
    country: str = Field(
        ...,
        description="Nombre del país",
        min_length=2,
        max_length=100,
        examples=["Colombia", "Estados Unidos", "España"]
    )
    
    city: str = Field(
        ...,
        description="Nombre de la ciudad",
        min_length=2,
        max_length=100,
        examples=["Bogotá", "New York", "Madrid"]
    )
    
    offset: str = Field(
        ...,
        description="Offset UTC en formato UTC±X o UTC±X:30",
        examples=["UTC-5", "UTC+5:30", "UTC+0", "UTC-3:30"]
    )
    
    is_favorite: bool = Field(
        default=False,
        description="Si la zona horaria está marcada como favorita"
    )
    
    # ========================================================================
    # VALIDADORES
    # ========================================================================
    
    @field_validator('country', 'city')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """
        Valida que country y city no estén vacíos.
        
        Args:
            v: String a validar
            
        Returns:
            str: String validado y sin espacios extra
            
        Raises:
            ValueError: Si el string está vacío
        """
        v = v.strip()
        if not v:
            raise ValueError("El campo no puede estar vacío")
        return v
    
    @field_validator('offset')
    @classmethod
    def validate_offset_format(cls, v: str) -> str:
        """
        Valida que el offset tenga formato UTC válido.
        
        Formatos válidos:
        - UTC+0 a UTC+14
        - UTC-0 a UTC-12
        - UTC±X:30 (media hora)
        - UTC±X:45 (45 minutos)
        
        Args:
            v: String con el offset
            
        Returns:
            str: Offset validado
            
        Raises:
            ValueError: Si el formato no es válido
        """
        v = v.strip().upper()  # Normalizar a mayúsculas
        
        if not UTC_OFFSET_PATTERN.match(v):
            raise ValueError(
                f"Formato de offset inválido: '{v}'. "
                f"Debe ser UTC±X o UTC±X:30 donde X es un número entre 0 y 14"
            )
        
        return v
    
    @field_validator('id')
    @classmethod
    def validate_id_format(cls, v: str) -> str:
        """
        Valida que el ID tenga el formato correcto.
        
        Args:
            v: ID a validar
            
        Returns:
            str: ID validado
            
        Raises:
            ValueError: Si el formato no es válido
        """
        v = v.strip().lower()
        
        if not v or '-' not in v:
            raise ValueError(
                f"ID inválido: '{v}'. Debe tener formato 'pais-ciudad'"
            )
        
        parts = v.split('-')
        if len(parts) < 2:
            raise ValueError(
                f"ID inválido: '{v}'. Debe contener al menos un país y una ciudad"
            )
        
        return v
    
    # ========================================================================
    # MÉTODOS HELPERS
    # ========================================================================
    
    def get_full_name(self) -> str:
        """
        Retorna el nombre completo "Ciudad, País".
        
        Returns:
            str: Nombre completo
        """
        return f"{self.city}, {self.country}"
    
    def get_offset_hours(self) -> float:
        """
        Convierte el offset a horas decimales.
        
        Returns:
            float: Offset en horas (ej: -5.0, 5.5, -3.5)
        """
        # Extraer el número del offset
        offset_str = self.offset.replace("UTC", "").strip()
        
        if ':' in offset_str:
            # Tiene minutos (ej: +5:30)
            parts = offset_str.split(':')
            hours = float(parts[0])
            minutes = float(parts[1])
            
            # Ajustar signo
            sign = 1 if hours >= 0 else -1
            return hours + (sign * minutes / 60)
        else:
            # Solo horas (ej: +5)
            return float(offset_str)
    
    def get_offset_description(self) -> str:
        """
        Retorna descripción del offset.
        
        Returns:
            str: Descripción del offset (ej: "5 horas adelante", "3.5 horas atrás")
        """
        hours = self.get_offset_hours()
        
        if hours == 0:
            return "Hora UTC (sin diferencia)"
        elif hours > 0:
            return f"{abs(hours)} horas adelante de UTC"
        else:
            return f"{abs(hours)} horas atrás de UTC"
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "colombia-bogota",
                "country": "Colombia",
                "city": "Bogotá",
                "offset": "UTC-5",
                "is_favorite": True
            }
        }


# ============================================================================
# MODELO DE CREACIÓN - TIMEZONE CREATE
# ============================================================================

class TimezoneCreate(BaseModel):
    """
    Modelo para crear una nueva zona horaria.
    
    El ID se genera automáticamente a partir del país y ciudad.
    
    Attributes:
        country: Nombre del país (requerido)
        city: Nombre de la ciudad (requerido)
        offset: Offset UTC (requerido)
    """
    
    country: str = Field(
        ...,
        description="Nombre del país",
        min_length=2,
        max_length=100,
        examples=["Colombia", "Japón"]
    )
    
    city: str = Field(
        ...,
        description="Nombre de la ciudad",
        min_length=2,
        max_length=100,
        examples=["Bogotá", "Tokyo"]
    )
    
    offset: str = Field(
        ...,
        description="Offset UTC",
        examples=["UTC-5", "UTC+9"]
    )
    
    # Reutilizar validadores
    @field_validator('country', 'city')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El campo no puede estar vacío")
        return v
    
    @field_validator('offset')
    @classmethod
    def validate_offset_format(cls, v: str) -> str:
        v = v.strip().upper()
        if not UTC_OFFSET_PATTERN.match(v):
            raise ValueError(f"Formato de offset inválido: '{v}'")
        return v
    
    def generate_id(self) -> str:
        """
        Genera el ID único para esta zona horaria.
        
        Returns:
            str: ID generado
        """
        return generate_timezone_id(self.country, self.city)
    
    class Config:
        json_schema_extra = {
            "example": {
                "country": "Colombia",
                "city": "Bogotá",
                "offset": "UTC-5"
            }
        }


# ============================================================================
# MODELO PARA FAVORITOS - FAVORITE TIMEZONE
# ============================================================================

class FavoriteTimezone(BaseModel):
    """
    Modelo para zona horaria en la lista de favoritos.
    
    Incluye información adicional sobre el orden en la lista circular.
    
    Attributes:
        id: ID único de la zona horaria
        country: Nombre del país
        city: Nombre de la ciudad
        offset: Offset UTC
        order: Posición en la lista de favoritos (para orden circular)
    """
    
    id: str = Field(
        ...,
        description="ID único de la zona horaria"
    )
    
    country: str = Field(
        ...,
        description="Nombre del país"
    )
    
    city: str = Field(
        ...,
        description="Nombre de la ciudad"
    )
    
    offset: str = Field(
        ...,
        description="Offset UTC"
    )
    
    order: int = Field(
        ...,
        description="Posición en la lista circular de favoritos",
        ge=0
    )
    
    def get_full_name(self) -> str:
        """Retorna el nombre completo."""
        return f"{self.city}, {self.country}"
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "colombia-bogota",
                "country": "Colombia",
                "city": "Bogotá",
                "offset": "UTC-5",
                "order": 0
            }
        }


# ============================================================================
# TESTS Y EJEMPLOS
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("🌍 EJEMPLOS DE MODELOS DE ZONA HORARIA")
    print("=" * 70)
    
    # Ejemplo 1: Crear timezone completa
    print("\n1️⃣ Crear zona horaria completa:")
    tz = Timezone(
        id="colombia-bogota",
        country="Colombia",
        city="Bogotá",
        offset="UTC-5",
        is_favorite=True
    )
    print(f"   ID: {tz.id}")
    print(f"   Nombre completo: {tz.get_full_name()}")
    print(f"   Offset: {tz.offset} ({tz.get_offset_hours()} horas)")
    print(f"   Descripción: {tz.get_offset_description()}")
    
    # Ejemplo 2: TimezoneCreate y generar ID
    print("\n2️⃣ Crear nueva zona horaria (TimezoneCreate):")
    new_tz = TimezoneCreate(
        country="Japón",
        city="Tokyo",
        offset="UTC+9"
    )
    print(f"   ID generado: {new_tz.generate_id()}")
    print(f"   {new_tz.model_dump_json(indent=2)}")
    
    # Ejemplo 3: Zonas horarias con media hora
    print("\n3️⃣ Zonas horarias con offset de media hora:")
    india = Timezone(
        id="india-new-delhi",
        country="India",
        city="New Delhi",
        offset="UTC+5:30"
    )
    print(f"   {india.get_full_name()}: {india.offset}")
    print(f"   Offset en horas: {india.get_offset_hours()}")
    
    # Ejemplo 4: FavoriteTimezone
    print("\n4️⃣ Zona horaria favorita con orden:")
    fav = FavoriteTimezone(
        id="colombia-bogota",
        country="Colombia",
        city="Bogotá",
        offset="UTC-5",
        order=0
    )
    print(f"   {fav.get_full_name()} - Orden: {fav.order}")
    
    # Ejemplo 5: Validaciones
    print("\n5️⃣ Pruebas de validación:")
    try:
        invalid_offset = Timezone(
            id="test-city",
            country="Test",
            city="City",
            offset="GMT+5"  # Formato inválido
        )
    except Exception as e:
        print(f"   ❌ Offset inválido: {e}")
    
    try:
        invalid_id = Timezone(
            id="invalid",  # Falta el guion
            country="Test",
            city="City",
            offset="UTC+5"
        )
    except Exception as e:
        print(f"   ❌ ID inválido: {e}")
    
    # Ejemplo 6: Generar IDs
    print("\n6️⃣ Generación de IDs:")
    test_cases = [
        ("Colombia", "Bogotá"),
        ("Estados Unidos", "New York"),
        ("España", "Madrid"),
        ("Reino Unido", "Londres")
    ]
    
    for country, city in test_cases:
        id_generated = generate_timezone_id(country, city)
        print(f"   {country}, {city} → {id_generated}")
    
    print("\n" + "=" * 70)