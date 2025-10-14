"""
Sistema de persistencia con archivos JSON.
Maneja lectura y escritura de datos en archivos JSON.
"""

import json
from pathlib import Path
from typing import Any
import logging

logger = logging.getLogger(__name__)


class JSONDatabase:
    """
    Clase para gestionar persistencia de datos en archivos JSON.
    
    Proporciona métodos para leer y escribir datos de forma segura
    con manejo de errores apropiado.
    
    Attributes:
        file_path (Path): Ruta al archivo JSON
    """
    
    def __init__(self, file_path: Path | str):
        """
        Inicializa la base de datos JSON.
        
        Args:
            file_path: Ruta al archivo JSON
        """
        self.file_path = Path(file_path)
        self._ensure_file_exists()
    
    def _ensure_file_exists(self) -> None:
        """
        Asegura que el archivo JSON exista.
        Si no existe, crea el archivo con una lista vacía.
        """
        if not self.file_path.exists():
            # Crear directorio si no existe
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Crear archivo con lista vacía
            self.write([])
            logger.info(f"Archivo JSON creado: {self.file_path}")
    
    def read(self) -> Any:
        """
        Lee datos del archivo JSON.
        
        Returns:
            Any: Datos leídos del archivo (generalmente lista o dict)
            
        Raises:
            json.JSONDecodeError: Si el archivo no es JSON válido
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.debug(f"Datos leídos de {self.file_path.name}")
                return data
        except json.JSONDecodeError as e:
            logger.error(f"Error decodificando JSON en {self.file_path}: {e}")
            # Retornar lista vacía si el archivo está corrupto
            return []
        except Exception as e:
            logger.error(f"Error leyendo {self.file_path}: {e}")
            return []
    
    def write(self, data: Any) -> bool:
        """
        Escribe datos al archivo JSON.
        
        Args:
            data: Datos a escribir (debe ser serializable a JSON)
            
        Returns:
            bool: True si se escribió exitosamente, False en caso contrario
        """
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            logger.debug(f"Datos escritos en {self.file_path.name}")
            return True
        except Exception as e:
            logger.error(f"Error escribiendo en {self.file_path}: {e}")
            return False
    
    def read_as_dict(self) -> dict:
        """
        Lee datos del archivo asegurando que sea un diccionario.
        
        Returns:
            dict: Diccionario leído o vacío si hay error
        """
        data = self.read()
        return data if isinstance(data, dict) else {}
    
    def read_as_list(self) -> list:
        """
        Lee datos del archivo asegurando que sea una lista.
        
        Returns:
            list: Lista leída o vacía si hay error
        """
        data = self.read()
        return data if isinstance(data, list) else []
    
    def append(self, item: Any) -> bool:
        """
        Agrega un item a una lista en el archivo JSON.
        
        Args:
            item: Item a agregar
            
        Returns:
            bool: True si se agregó exitosamente
        """
        data = self.read_as_list()
        data.append(item)
        return self.write(data)
    
    def clear(self) -> bool:
        """
        Limpia el archivo escribiendo una lista vacía.
        
        Returns:
            bool: True si se limpió exitosamente
        """
        return self.write([])
    
    def exists(self) -> bool:
        """
        Verifica si el archivo existe.
        
        Returns:
            bool: True si existe
        """
        return self.file_path.exists()
    
    def delete(self) -> bool:
        """
        Elimina el archivo JSON.
        
        Returns:
            bool: True si se eliminó exitosamente
        """
        try:
            if self.file_path.exists():
                self.file_path.unlink()
                logger.info(f"Archivo eliminado: {self.file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error eliminando {self.file_path}: {e}")
            return False


# ============================================================================
# EJEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    import tempfile
    
    print("=" * 70)
    print("💾 EJEMPLO DE USO - JSON DATABASE")
    print("=" * 70)
    
    # Crear archivo temporal
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = Path(f.name)
    
    print(f"\n📁 Archivo temporal: {temp_path}")
    
    # Crear instancia
    db = JSONDatabase(temp_path)
    
    # Ejemplo 1: Escribir lista
    print("\n1️⃣ Escribir lista de alarmas:")
    alarmas = [
        {"id": 1, "time": "07:00", "label": "Despertar"},
        {"id": 2, "time": "14:00", "label": "Almuerzo"},
    ]
    db.write(alarmas)
    print(f"   ✅ Alarmas guardadas: {alarmas}")
    
    # Ejemplo 2: Leer datos
    print("\n2️⃣ Leer alarmas:")
    data = db.read()
    print(f"   📖 Datos leídos: {data}")
    
    # Ejemplo 3: Agregar item
    print("\n3️⃣ Agregar nueva alarma:")
    db.append({"id": 3, "time": "22:00", "label": "Dormir"})
    data = db.read()
    print(f"   ✅ Después de agregar: {data}")
    
    # Ejemplo 4: Limpiar
    print("\n4️⃣ Limpiar archivo:")
    db.clear()
    data = db.read()
    print(f"   🧹 Después de limpiar: {data}")
    
    # Ejemplo 5: Escribir diccionario
    print("\n5️⃣ Escribir configuración (dict):")
    config = {"time_format": "24h", "volume": 50}
    db.write(config)
    data = db.read_as_dict()
    print(f"   ⚙️  Configuración guardada: {data}")
    
    # Limpiar archivo temporal
    temp_path.unlink()
    print("\n🗑️  Archivo temporal eliminado")
    
    print("\n" + "=" * 70)