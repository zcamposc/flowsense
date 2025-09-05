"""
Funciones de geometría para el análisis de video.
"""
import numpy as np


def punto_en_poligono(point, polygon):
    """
    Devuelve True si el punto está dentro del polígono usando ray casting.

    Args:
        point: Tupla (x, y) con las coordenadas del punto.
        polygon: Lista de puntos (x, y) que forman el polígono.
    """
    x, y = point
    poly = np.array(polygon)
    n = len(poly)
    inside = False
    p1x, p1y = poly[0]
    for i in range(n+1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside


def cruza_linea(p1, p2, linea):
    """
    Devuelve True si el segmento p1-p2 cruza la línea definida.

    Args:
        p1: Punto inicial del segmento (x1, y1)
        p2: Punto final del segmento (x2, y2)
        linea: Lista de dos puntos que definen la línea
    """
    a1, a2 = np.array(linea[0]), np.array(linea[1])
    b1, b2 = np.array(p1), np.array(p2)

    def ccw(A, B, C):
        return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

    return (ccw(a1, b1, b2) != ccw(a2, b1, b2)) and (
        ccw(a1, a2, b1) != ccw(a1, a2, b2)
    )


def determinar_direccion_cruce(prev_pos, current_pos, line_coords):
    """
    Determina la dirección de cruce usando el método de producto cruz.
    Más preciso que solo comparar coordenadas X, especialmente para líneas diagonales.
    
    Args:
        prev_pos: Posición anterior (x, y)
        current_pos: Posición actual (x, y)  
        line_coords: Lista de dos puntos que definen la línea [(x1,y1), (x2,y2)]
        
    Returns:
        str: "left_to_right" o "right_to_left"
    """
    # Vector de la línea (del punto inicial al final)
    line_start, line_end = line_coords
    line_vector = (line_end[0] - line_start[0], line_end[1] - line_start[1])
    
    # Vector del movimiento del objeto
    movement_vector = (current_pos[0] - prev_pos[0], current_pos[1] - prev_pos[1])
    
    # Producto cruz para determinar dirección relativa a la línea
    # Si > 0: left_to_right, Si < 0: right_to_left
    cross_product = line_vector[0] * movement_vector[1] - line_vector[1] * movement_vector[0]
    direction = "left_to_right" if cross_product > 0 else "right_to_left"

    return direction


def determinar_lado_del_punto(point, line_coords):
    """
    Usa el producto cruz para determinar si un punto está a la 'izquierda' o 'derecha' de la línea.
    Esto es clave para la lógica de estado.
    """
    line_start, line_end = line_coords
    line_vec = (line_end[0] - line_start[0], line_end[1] - line_start[1])
    point_vec = (point[0] - line_start[0], point[1] - line_start[1])
    
    cross_product = line_vec[0] * point_vec[1] - line_vec[1] * point_vec[0]
    
    # Devuelve el estado/zona del punto
    return "derecha" if cross_product > 0 else "izquierda"


def calcular_distancia_punto_a_linea(punto, linea):
    """Calcula la distancia perpendicular de un punto a una línea."""
    x0, y0 = punto
    x1, y1 = linea[0]
    x2, y2 = linea[1]
    
    # Fórmula de distancia punto-línea
    numerador = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
    denominador = ((y2 - y1) ** 2 + (x2 - x1) ** 2) ** 0.5
    
    return numerador / denominador if denominador > 0 else float('inf')


def determinar_lado_de_linea(point, line_coords):
    """
    Determina en qué lado de una línea se encuentra un punto usando el producto cruz.
    
    Args:
        point: Tupla (x, y) con las coordenadas del punto
        line_coords: Lista de dos puntos [(x1,y1), (x2,y2)] que definen la línea
        
    Returns:
        str: "izquierda" o "derecha" dependiendo del lado del punto
    """
    line_start, line_end = line_coords
    
    # Vector de la línea
    line_vec = (line_end[0] - line_start[0], line_end[1] - line_start[1])
    
    # Vector del punto inicial de línea al punto
    point_vec = (point[0] - line_start[0], point[1] - line_start[1])
    
    # Producto cruz para determinar el lado
    cross_product = line_vec[0] * point_vec[1] - line_vec[1] * point_vec[0]
    
    # Si el producto cruz es positivo, el punto está a la "derecha"
    # Si es negativo, está a la "izquierda"
    return "derecha" if cross_product > 0 else "izquierda"