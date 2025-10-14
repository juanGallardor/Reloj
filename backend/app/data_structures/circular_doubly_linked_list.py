"""
Implementación de Lista Circular Doble (Circular Doubly Linked List).
Estructura de datos fundamental para el proyecto de reloj digital.
"""

from typing import TypeVar, Generic, Callable, Optional, List, Any
from app.data_structures.node import Node


T = TypeVar('T')


class CircularDoublyLinkedList(Generic[T]):
    """
    Lista Circular Doble genérica.
    
    Características:
    - Circular: El último nodo apunta al primero y viceversa
    - Doble: Se puede navegar en ambas direcciones (prev y next)
    - Genérica: Puede almacenar cualquier tipo de dato
    
    Propiedades:
    - Si la lista está vacía: head = None
    - Si hay un solo nodo: head.prev = head.next = head
    - Si hay múltiples nodos: head.prev apunta al último, último.next apunta a head
    
    Uso en el proyecto:
    - Alarmas: Ordenadas por hora, navegación circular
    - Laps: Último agregado primero, navegación bidireccional
    - Zonas horarias: Orden personalizado por usuario
    
    Attributes:
        head (Node[T] | None): Primer nodo de la lista
    """
    
    def __init__(self) -> None:
        """Inicializa una lista circular doble vacía."""
        self.head: Optional[Node[T]] = None
    
    # ========================================================================
    # MÉTODOS DE CONSULTA
    # ========================================================================
    
    def is_empty(self) -> bool:
        """
        Verifica si la lista está vacía.
        
        Returns:
            bool: True si la lista está vacía, False en caso contrario
        """
        return self.head is None
    
    def size(self) -> int:
        """
        Cuenta el número de nodos en la lista.
        
        Returns:
            int: Cantidad de nodos
        """
        if self.is_empty():
            return 0
        
        count = 1
        current = self.head.next
        
        # Recorrer hasta volver al head
        while current != self.head:
            count += 1
            current = current.next
        
        return count
    
    # ========================================================================
    # MÉTODOS DE INSERCIÓN
    # ========================================================================
    
    def insert_at_beginning(self, data: T) -> None:
        """
        Inserta un nuevo nodo al inicio de la lista.
        
        Args:
            data (T): Dato a insertar
        """
        new_node = Node(data)
        
        if self.is_empty():
            # Lista vacía: el nodo apunta a sí mismo
            new_node.next = new_node
            new_node.prev = new_node
            self.head = new_node
        else:
            # Obtener el último nodo
            last = self.head.prev
            
            # Conectar el nuevo nodo
            new_node.next = self.head
            new_node.prev = last
            
            # Actualizar el antiguo head y el último nodo
            self.head.prev = new_node
            last.next = new_node
            
            # El nuevo nodo es el nuevo head
            self.head = new_node
    
    def insert_at_end(self, data: T) -> None:
        """
        Inserta un nuevo nodo al final de la lista.
        
        Args:
            data (T): Dato a insertar
        """
        new_node = Node(data)
        
        if self.is_empty():
            # Lista vacía: el nodo apunta a sí mismo
            new_node.next = new_node
            new_node.prev = new_node
            self.head = new_node
        else:
            # Obtener el último nodo
            last = self.head.prev
            
            # Conectar el nuevo nodo
            new_node.next = self.head
            new_node.prev = last
            
            # Actualizar conexiones
            last.next = new_node
            self.head.prev = new_node
    
    def insert_sorted(self, data: T, key_func: Callable[[T], Any]) -> None:
        """
        Inserta un dato manteniendo el orden según una función de comparación.
        Útil para alarmas ordenadas por hora.
        
        Args:
            data (T): Dato a insertar
            key_func (Callable): Función que extrae la clave de ordenamiento
                                 Ejemplo: lambda x: x["time"] para ordenar por hora
        """
        new_node = Node(data)
        
        if self.is_empty():
            # Lista vacía
            new_node.next = new_node
            new_node.prev = new_node
            self.head = new_node
            return
        
        # Obtener la clave del nuevo dato
        new_key = key_func(data)
        
        # Si debe ir al principio
        if new_key < key_func(self.head.data):
            last = self.head.prev
            
            new_node.next = self.head
            new_node.prev = last
            
            self.head.prev = new_node
            last.next = new_node
            
            self.head = new_node
            return
        
        # Buscar posición correcta
        current = self.head
        
        while True:
            # Si llegamos al final o encontramos un nodo mayor
            if current.next == self.head or key_func(current.next.data) > new_key:
                # Insertar después de current
                new_node.next = current.next
                new_node.prev = current
                
                current.next.prev = new_node
                current.next = new_node
                break
            
            current = current.next
    
    # ========================================================================
    # MÉTODOS DE ELIMINACIÓN
    # ========================================================================
    
    def delete(self, data: T) -> bool:
        """
        Elimina el primer nodo que contenga el dato especificado.
        
        Args:
            data (T): Dato a eliminar
            
        Returns:
            bool: True si se eliminó, False si no se encontró
        """
        if self.is_empty():
            return False
        
        current = self.head
        
        # Buscar el nodo a eliminar
        while True:
            if current.data == data:
                # Caso 1: Solo hay un nodo
                if current.next == current:
                    self.head = None
                else:
                    # Caso 2: El nodo a eliminar es el head
                    if current == self.head:
                        self.head = current.next
                    
                    # Reconectar los nodos adyacentes
                    current.prev.next = current.next
                    current.next.prev = current.prev
                
                return True
            
            current = current.next
            
            # Si dimos la vuelta completa sin encontrar
            if current == self.head:
                break
        
        return False
    
    def delete_by_condition(self, condition: Callable[[T], bool]) -> int:
        """
        Elimina todos los nodos que cumplan una condición.
        
        Args:
            condition (Callable): Función que retorna True si el nodo debe eliminarse
            
        Returns:
            int: Cantidad de nodos eliminados
        """
        if self.is_empty():
            return 0
        
        deleted_count = 0
        current = self.head
        nodes_to_delete = []
        
        # Primera pasada: identificar nodos a eliminar
        while True:
            if condition(current.data):
                nodes_to_delete.append(current.data)
            
            current = current.next
            if current == self.head:
                break
        
        # Segunda pasada: eliminar los nodos
        for data in nodes_to_delete:
            if self.delete(data):
                deleted_count += 1
        
        return deleted_count
    
    def clear(self) -> None:
        """Vacía completamente la lista."""
        self.head = None
    
    # ========================================================================
    # MÉTODOS DE BÚSQUEDA
    # ========================================================================
    
    def search(self, data: T) -> Optional[Node[T]]:
        """
        Busca un nodo que contenga el dato especificado.
        
        Args:
            data (T): Dato a buscar
            
        Returns:
            Node[T] | None: Nodo encontrado o None si no existe
        """
        if self.is_empty():
            return None
        
        current = self.head
        
        while True:
            if current.data == data:
                return current
            
            current = current.next
            
            if current == self.head:
                break
        
        return None
    
    def find(self, condition: Callable[[T], bool]) -> Optional[Node[T]]:
        """
        Busca el primer nodo que cumpla una condición.
        
        Args:
            condition (Callable): Función que retorna True si el nodo coincide
            
        Returns:
            Node[T] | None: Primer nodo que cumple la condición o None
        """
        if self.is_empty():
            return None
        
        current = self.head
        
        while True:
            if condition(current.data):
                return current
            
            current = current.next
            
            if current == self.head:
                break
        
        return None
    
    def find_all(self, condition: Callable[[T], bool]) -> List[T]:
        """
        Busca todos los nodos que cumplan una condición.
        
        Args:
            condition (Callable): Función que retorna True si el nodo coincide
            
        Returns:
            List[T]: Lista con todos los datos que cumplen la condición
        """
        result = []
        
        if self.is_empty():
            return result
        
        current = self.head
        
        while True:
            if condition(current.data):
                result.append(current.data)
            
            current = current.next
            
            if current == self.head:
                break
        
        return result
    
    # ========================================================================
    # MÉTODOS DE NAVEGACIÓN CIRCULAR
    # ========================================================================
    
    def get_next(self, current_data: T) -> Optional[T]:
        """
        Obtiene el dato siguiente de forma circular.
        
        Args:
            current_data (T): Dato actual
            
        Returns:
            T | None: Dato siguiente o None si no se encuentra
        """
        node = self.search(current_data)
        if node is None:
            return None
        
        return node.next.data
    
    def get_previous(self, current_data: T) -> Optional[T]:
        """
        Obtiene el dato anterior de forma circular.
        
        Args:
            current_data (T): Dato actual
            
        Returns:
            T | None: Dato anterior o None si no se encuentra
        """
        node = self.search(current_data)
        if node is None:
            return None
        
        return node.prev.data
    
    # ========================================================================
    # MÉTODOS DE CONVERSIÓN
    # ========================================================================
    
    def get_all(self) -> List[T]:
        """
        Obtiene todos los datos de la lista como una lista de Python.
        
        Returns:
            List[T]: Lista con todos los datos
        """
        if self.is_empty():
            return []
        
        result = []
        current = self.head
        
        while True:
            result.append(current.data)
            current = current.next
            
            if current == self.head:
                break
        
        return result
    
    def get_all_reverse(self) -> List[T]:
        """
        Obtiene todos los datos en orden inverso.
        
        Returns:
            List[T]: Lista con todos los datos en orden inverso
        """
        if self.is_empty():
            return []
        
        result = []
        current = self.head.prev  # Empezar desde el último
        
        while True:
            result.append(current.data)
            current = current.prev
            
            if current == self.head.prev:
                break
        
        return result
    
    # ========================================================================
    # MÉTODOS DE REPRESENTACIÓN
    # ========================================================================
    
    def __repr__(self) -> str:
        """
        Representación en string de la lista para debugging.
        
        Returns:
            str: Representación de la lista
        """
        if self.is_empty():
            return "CircularDoublyLinkedList([])"
        
        items = self.get_all()
        items_str = " <-> ".join(str(item) for item in items)
        return f"CircularDoublyLinkedList([{items_str}] ⟲)"
    
    def __str__(self) -> str:
        """
        Conversión a string para impresión.
        
        Returns:
            str: String con todos los elementos
        """
        return str(self.get_all())
    
    def __len__(self) -> int:
        """
        Permite usar len() con la lista.
        
        Returns:
            int: Tamaño de la lista
        """
        return self.size()
    
    def __iter__(self):
        """
        Permite iterar sobre la lista con un for loop.
        
        Yields:
            T: Cada dato de la lista
        """
        if self.is_empty():
            return
        
        current = self.head
        
        while True:
            yield current.data
            current = current.next
            
            if current == self.head:
                break


# ============================================================================
# EJEMPLOS Y TESTS
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("🔗 EJEMPLOS DE USO - LISTA CIRCULAR DOBLE")
    print("=" * 70)
    
    # Ejemplo 1: Lista de números
    print("\n1️⃣ Lista de números:")
    lista = CircularDoublyLinkedList[int]()
    
    lista.insert_at_end(10)
    lista.insert_at_end(20)
    lista.insert_at_end(30)
    lista.insert_at_beginning(5)
    
    print(f"   Lista: {lista}")
    print(f"   Tamaño: {len(lista)}")
    print(f"   Siguiente a 20: {lista.get_next(20)}")
    print(f"   Anterior a 20: {lista.get_previous(20)}")
    
    # Ejemplo 2: Lista ordenada de alarmas
    print("\n2️⃣ Lista ordenada de alarmas (por hora):")
    alarmas = CircularDoublyLinkedList[dict]()
    
    alarmas.insert_sorted({"hora": "08:00", "label": "Trabajo"}, lambda x: x["hora"])
    alarmas.insert_sorted({"hora": "07:00", "label": "Despertar"}, lambda x: x["hora"])
    alarmas.insert_sorted({"hora": "22:00", "label": "Dormir"}, lambda x: x["hora"])
    alarmas.insert_sorted({"hora": "12:00", "label": "Almuerzo"}, lambda x: x["hora"])
    
    print("   Alarmas ordenadas:")
    for alarma in alarmas:
        print(f"      {alarma['hora']} - {alarma['label']}")
    
    # Ejemplo 3: Navegación circular
    print("\n3️⃣ Navegación circular:")
    current = alarmas.head.data
    print(f"   Empezando en: {current['hora']}")
    for i in range(6):
        current = alarmas.get_next(current)
        print(f"   Siguiente: {current['hora']}")
    
    # Ejemplo 4: Búsqueda y eliminación
    print("\n4️⃣ Búsqueda y eliminación:")
    alarma_encontrada = alarmas.find(lambda x: x["hora"] == "12:00")
    print(f"   Encontrada: {alarma_encontrada.data if alarma_encontrada else 'No'}")
    
    alarmas.delete({"hora": "12:00", "label": "Almuerzo"})
    print(f"   Después de eliminar: {[a['hora'] for a in alarmas]}")
    
    print("\n" + "=" * 70)
    print("✅ Ejemplos completados")
    print("=" * 70)