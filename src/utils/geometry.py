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
