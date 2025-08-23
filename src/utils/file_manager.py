import os
import json
from typing import Optional, Tuple, List


def generar_nombre_salida(
    input_path: str,
    model_path: str,
    output_path: Optional[str],
    extension: str
) -> str:
    """
    Genera un nombre de archivo de salida basado en el nombre del archivo
    de entrada y el modelo utilizado.

    Args:
        input_path (str): Ruta del archivo de entrada.
        model_path (str): Ruta del modelo YOLO utilizado.
        output_path (Optional[str]): Ruta definida manualmente para la salida.
        extension (str): Extensión del archivo de salida (e.g., 'png', 'mp4').

    Returns:
        str: Nombre del archivo de salida.
    """
    if output_path:
        return output_path

    input_name = os.path.splitext(os.path.basename(input_path))[0]
    model_name = os.path.splitext(os.path.basename(model_path))[0]
    return f"outputs/{input_name}_{model_name}.{extension}"


def cargar_zonas_desde_json(
    json_path: str
) -> Tuple[
    List[List[Tuple[float, float]]],
    List[List[Tuple[float, float]]]
]:
    """
    Carga zonas de interés (líneas o polígonos) desde un archivo JSON.
    
    Soporta dos formatos:
    
    1. Formato simple (antiguo):
    {
        "lines": [ [[x1, y1], [x2, y2]], ... ],
        "polygons": [ [[x1, y1], [x2, y2], [x3, y3], ...], ... ]
    }
    
    2. Formato con nombres (nuevo):
    {
        "lines": [
            {
                "id": "line_entrada_principal",
                "name": "entrada_principal", 
                "coordinates": [[x1, y1], [x2, y2]]
            }
        ],
        "polygons": [
            {
                "id": "zone_entrada_principal",
                "name": "entrada_principal",
                "coordinates": [[x1, y1], [x2, y2], [x3, y3], ...]
            }
        ]
    }

    Args:
        json_path (str): Ruta del archivo JSON de entrada.

    Returns:
        Tuple[
            List[List[Tuple[float, float]]],
            List[List[Tuple[float, float]]]
        ]:
            - Una lista de líneas, donde cada línea es una lista de tuplas
              (x, y).
            - Una lista de polígonos, donde cada polígono es una lista de
              tuplas (x, y).
    """
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # Procesar líneas
    lines = []
    for line in data.get('lines', []):
        if isinstance(line, dict):
            # Formato nuevo: diccionario con coordinates
            coordinates = line.get('coordinates', [])
            lines.append(coordinates)
        else:
            # Formato antiguo: lista directa
            lines.append(line)
    
    # Procesar polígonos
    polygons = []
    for polygon in data.get('polygons', []):
        if isinstance(polygon, dict):
            # Formato nuevo: diccionario con coordinates
            coordinates = polygon.get('coordinates', [])
            polygons.append(coordinates)
        else:
            # Formato antiguo: lista directa
            polygons.append(polygon)
    
    return lines, polygons


def cargar_nombres_zonas(
    json_path: str
) -> dict:
    """
    Carga los nombres personalizados de zonas desde un archivo JSON.
    
    Args:
        json_path (str): Ruta del archivo JSON de entrada.

    Returns:
        dict: Diccionario con los nombres de zonas indexados por posición.
              Ej: {"polygon_1": "zone_entrada_principal", "line_1": "line_entrada"}
    """
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        zone_names = {}
        
        # Procesar polígonos
        for i, polygon in enumerate(data.get('polygons', []), 1):
            if isinstance(polygon, dict):
                zone_names[f"polygon_{i}"] = polygon.get('id', f"zone_polygon_{i}")
        
        # Procesar líneas
        for i, line in enumerate(data.get('lines', []), 1):
            if isinstance(line, dict):
                zone_names[f"line_{i}"] = line.get('id', f"zone_line_{i}")
        
        return zone_names
    except Exception:
        # Si hay error, retornar diccionario vacío
        return {}
