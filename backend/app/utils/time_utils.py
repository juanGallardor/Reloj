"""
Utilidades para manejo de tiempo.
Funciones auxiliares para formateo y conversión de tiempo.
"""

from datetime import datetime, timedelta
from typing import Tuple


def format_seconds_to_time(seconds: float) -> str:
    """
    Formatea segundos a formato MM:SS.ms
    
    Args:
        seconds: Tiempo en segundos
        
    Returns:
        str: Tiempo formateado (ej: "01:23.45")
        
    Example:
        >>> format_seconds_to_time(83.45)
        "01:23.45"
    """
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60
    return f"{minutes:02d}:{remaining_seconds:05.2f}"


def parse_time_string(time_str: str) -> Tuple[int, int]:
    """
    Parsea un string de tiempo HH:MM a tupla de horas y minutos.
    
    Args:
        time_str: String en formato "HH:MM"
        
    Returns:
        Tuple[int, int]: (horas, minutos)
        
    Raises:
        ValueError: Si el formato no es válido
        
    Example:
        >>> parse_time_string("14:30")
        (14, 30)
    """
    try:
        hours, minutes = time_str.split(":")
        return int(hours), int(minutes)
    except Exception as e:
        raise ValueError(f"Formato de hora inválido: {time_str}. Debe ser HH:MM")


def is_valid_time(time_str: str) -> bool:
    """
    Verifica si un string tiene formato de hora válido HH:MM.
    
    Args:
        time_str: String a validar
        
    Returns:
        bool: True si es válido
        
    Example:
        >>> is_valid_time("14:30")
        True
        >>> is_valid_time("25:00")
        False
    """
    try:
        hours, minutes = parse_time_string(time_str)
        return 0 <= hours <= 23 and 0 <= minutes <= 59
    except:
        return False


def convert_12h_to_24h(time_str: str, period: str) -> str:
    """
    Convierte hora de formato 12h a 24h.
    
    Args:
        time_str: Hora en formato "HH:MM"
        period: "AM" o "PM"
        
    Returns:
        str: Hora en formato 24h "HH:MM"
        
    Example:
        >>> convert_12h_to_24h("02:30", "PM")
        "14:30"
        >>> convert_12h_to_24h("12:00", "AM")
        "00:00"
    """
    hours, minutes = parse_time_string(time_str)
    
    if period.upper() == "PM" and hours != 12:
        hours += 12
    elif period.upper() == "AM" and hours == 12:
        hours = 0
    
    return f"{hours:02d}:{minutes:02d}"


def convert_24h_to_12h(time_str: str) -> Tuple[str, str]:
    """
    Convierte hora de formato 24h a 12h.
    
    Args:
        time_str: Hora en formato "HH:MM"
        
    Returns:
        Tuple[str, str]: (hora_12h, periodo)
        
    Example:
        >>> convert_24h_to_12h("14:30")
        ("02:30", "PM")
        >>> convert_24h_to_12h("00:00")
        ("12:00", "AM")
    """
    hours, minutes = parse_time_string(time_str)
    
    period = "AM" if hours < 12 else "PM"
    display_hour = hours % 12
    if display_hour == 0:
        display_hour = 12
    
    return f"{display_hour:02d}:{minutes:02d}", period


def get_time_difference(time1: str, time2: str) -> int:
    """
    Calcula diferencia en minutos entre dos horas.
    
    Args:
        time1: Hora en formato "HH:MM"
        time2: Hora en formato "HH:MM"
        
    Returns:
        int: Diferencia en minutos (puede ser negativa)
        
    Example:
        >>> get_time_difference("14:30", "15:00")
        30
    """
    h1, m1 = parse_time_string(time1)
    h2, m2 = parse_time_string(time2)
    
    total1 = h1 * 60 + m1
    total2 = h2 * 60 + m2
    
    return total2 - total1


def add_minutes_to_time(time_str: str, minutes: int) -> str:
    """
    Agrega minutos a una hora.
    
    Args:
        time_str: Hora en formato "HH:MM"
        minutes: Minutos a agregar
        
    Returns:
        str: Nueva hora en formato "HH:MM"
        
    Example:
        >>> add_minutes_to_time("14:30", 45)
        "15:15"
    """
    hours, mins = parse_time_string(time_str)
    
    # Crear datetime para usar sus métodos
    dt = datetime(2000, 1, 1, hours, mins)
    dt += timedelta(minutes=minutes)
    
    return dt.strftime("%H:%M")


def is_time_between(check_time: str, start_time: str, end_time: str) -> bool:
    """
    Verifica si una hora está entre dos horas.
    
    Args:
        check_time: Hora a verificar
        start_time: Hora de inicio
        end_time: Hora de fin
        
    Returns:
        bool: True si está en el rango
        
    Example:
        >>> is_time_between("15:00", "14:00", "16:00")
        True
    """
    check = parse_time_string(check_time)
    start = parse_time_string(start_time)
    end = parse_time_string(end_time)
    
    check_mins = check[0] * 60 + check[1]
    start_mins = start[0] * 60 + start[1]
    end_mins = end[0] * 60 + end[1]
    
    if start_mins <= end_mins:
        return start_mins <= check_mins <= end_mins
    else:
        # Caso cuando cruza medianoche
        return check_mins >= start_mins or check_mins <= end_mins


def get_current_time_str() -> str:
    """
    Obtiene la hora actual como string HH:MM.
    
    Returns:
        str: Hora actual
        
    Example:
        >>> get_current_time_str()
        "14:30"
    """
    return datetime.now().strftime("%H:%M")


def get_timestamp() -> str:
    """
    Obtiene timestamp actual en formato ISO.
    
    Returns:
        str: Timestamp ISO
        
    Example:
        >>> get_timestamp()
        "2025-10-11T14:30:00.123456"
    """
    return datetime.now().isoformat()


# ============================================================================
# TESTS Y EJEMPLOS
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("🕐 UTILIDADES DE TIEMPO - EJEMPLOS")
    print("=" * 70)
    
    # Ejemplo 1: Formatear segundos
    print("\n1️⃣ Formatear segundos:")
    print(f"   83.45s → {format_seconds_to_time(83.45)}")
    print(f"   125.67s → {format_seconds_to_time(125.67)}")
    
    # Ejemplo 2: Parsear tiempo
    print("\n2️⃣ Parsear tiempo:")
    h, m = parse_time_string("14:30")
    print(f"   '14:30' → {h} horas, {m} minutos")
    
    # Ejemplo 3: Validar tiempo
    print("\n3️⃣ Validar tiempo:")
    print(f"   '14:30' es válido: {is_valid_time('14:30')}")
    print(f"   '25:00' es válido: {is_valid_time('25:00')}")
    
    # Ejemplo 4: Convertir 12h a 24h
    print("\n4️⃣ Convertir 12h → 24h:")
    print(f"   02:30 PM → {convert_12h_to_24h('02:30', 'PM')}")
    print(f"   12:00 AM → {convert_12h_to_24h('12:00', 'AM')}")
    
    # Ejemplo 5: Convertir 24h a 12h
    print("\n5️⃣ Convertir 24h → 12h:")
    time_12h, period = convert_24h_to_12h("14:30")
    print(f"   14:30 → {time_12h} {period}")
    
    # Ejemplo 6: Diferencia de tiempo
    print("\n6️⃣ Diferencia de tiempo:")
    diff = get_time_difference("14:30", "15:45")
    print(f"   14:30 a 15:45 → {diff} minutos")
    
    # Ejemplo 7: Agregar minutos
    print("\n7️⃣ Agregar minutos:")
    new_time = add_minutes_to_time("14:30", 45)
    print(f"   14:30 + 45 min → {new_time}")
    
    # Ejemplo 8: Tiempo entre rango
    print("\n8️⃣ Verificar rango:")
    print(f"   15:00 está entre 14:00 y 16:00: {is_time_between('15:00', '14:00', '16:00')}")
    
    # Ejemplo 9: Hora actual
    print("\n9️⃣ Hora actual:")
    print(f"   {get_current_time_str()}")
    print(f"   Timestamp: {get_timestamp()}")
    
    print("\n" + "=" * 70)