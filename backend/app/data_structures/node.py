"""
Implementación de la clase Node para Lista Circular Doble.
Estructura fundamental para almacenar datos con enlaces bidireccionales.
"""

from typing import TypeVar, Generic, Optional


# Type variable genérico para permitir cualquier tipo de dato
T = TypeVar('T')


class Node(Generic[T]):
    """
    Nodo de una Lista Circular Doble.
    
    Un nodo contiene:
    - data: El dato almacenado (puede ser cualquier tipo)
    - prev: Referencia al nodo anterior
    - next: Referencia al nodo siguiente
    
    En una lista circular doble:
    - El primer nodo tiene prev apuntando al último nodo
    - El último nodo tiene next apuntando al primer nodo
    - Si solo hay un nodo, prev y next apuntan a sí mismo
    
    Attributes:
        data (T): El dato almacenado en el nodo
        prev (Node[T] | None): Referencia al nodo anterior
        next (Node[T] | None): Referencia al nodo siguiente
    
    Example:
        >>> node1 = Node(10)
        >>> node2 = Node("Hello")
        >>> node3 = Node({"id": 1, "name": "Alarm"})
    """
    
    def __init__(self, data: T) -> None:
        """
        Inicializa un nuevo nodo con el dato proporcionado.
        
        Por defecto, los punteros prev y next son None.
        Estos se configuran cuando el nodo se inserta en la lista.
        
        Args:
            data (T): El dato a almacenar en el nodo
        """
        self.data: T = data
        self.prev: Optional['Node[T]'] = None
        self.next: Optional['Node[T]'] = None
    
    def __repr__(self) -> str:
        """
        Representación en string del nodo para debugging.
        
        Muestra el dato almacenado de forma legible.
        No muestra los punteros prev/next para evitar recursión infinita.
        
        Returns:
            str: Representación del nodo
            
        Example:
            >>> node = Node(42)
            >>> print(node)
            Node(42)
        """
        return f"Node({self.data})"
    
    def __str__(self) -> str:
        """
        Conversión a string para impresión amigable.
        
        Returns:
            str: Representación del dato del nodo
        """
        return str(self.data)
    
    def has_prev(self) -> bool:
        """
        Verifica si el nodo tiene un nodo anterior.
        
        Returns:
            bool: True si tiene prev, False si prev es None
        """
        return self.prev is not None
    
    def has_next(self) -> bool:
        """
        Verifica si el nodo tiene un nodo siguiente.
        
        Returns:
            bool: True si tiene next, False si next es None
        """
        return self.next is not None
    
    def is_circular(self) -> bool:
        """
        Verifica si el nodo es circular (apunta a sí mismo).
        Esto ocurre cuando hay un solo nodo en la lista.
        
        Returns:
            bool: True si prev y next apuntan a sí mismo
        """
        return self.prev is self and self.next is self


# ============================================================================
# EJEMPLO DE USO Y TESTS
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🔗 EJEMPLO DE USO DE LA CLASE NODE")
    print("=" * 60)
    
    # Crear nodos con diferentes tipos de datos
    print("\n1️⃣ Creando nodos con diferentes tipos de datos:")
    node_int = Node(42)
    node_str = Node("Hola Mundo")
    node_dict = Node({"id": 1, "time": "07:00", "label": "Despertar"})
    node_list = Node([1, 2, 3, 4, 5])
    
    print(f"   Nodo entero: {node_int}")
    print(f"   Nodo string: {node_str}")
    print(f"   Nodo dict: {node_dict}")
    print(f"   Nodo list: {node_list}")
    
    # Crear una mini lista circular con 3 nodos
    print("\n2️⃣ Creando lista circular simple con 3 nodos:")
    n1 = Node("A")
    n2 = Node("B")
    n3 = Node("C")
    
    # Conectar los nodos circularmente
    n1.next = n2
    n1.prev = n3
    
    n2.next = n3
    n2.prev = n1
    
    n3.next = n1
    n3.prev = n2
    
    print(f"   n1.data = {n1.data}, prev = {n1.prev.data}, next = {n1.next.data}")
    print(f"   n2.data = {n2.data}, prev = {n2.prev.data}, next = {n2.next.data}")
    print(f"   n3.data = {n3.data}, prev = {n3.prev.data}, next = {n3.next.data}")
    
    # Navegar circularmente
    print("\n3️⃣ Navegando circularmente desde n1:")
    current = n1
    print(f"   Inicio: {current.data}")
    for i in range(5):
        current = current.next
        print(f"   Paso {i+1}: {current.data}")
    
    # Verificar circularidad
    print("\n4️⃣ Verificando propiedades:")
    single_node = Node("Solo")
    single_node.prev = single_node
    single_node.next = single_node
    
    print(f"   n1 tiene prev: {n1.has_prev()}")
    print(f"   n1 tiene next: {n1.has_next()}")
    print(f"   single_node es circular: {single_node.is_circular()}")
    print(f"   n1 es circular: {n1.is_circular()}")
    
    print("\n" + "=" * 60)
    print("✅ Ejemplo completado exitosamente")
    print("=" * 60)