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
    El formato esperado es:
    {
        "lines": [ [[x1, y1], [x2, y2]], ... ],
        "polygons": [ [[x1, y1], [x2, y2], [x3, y3], ...], ... ]
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
    lines = data.get('lines', [])
    polygons = data.get('polygons', [])
    return lines, polygons
