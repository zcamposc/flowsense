"""
Utilidades para manejo de rutas del proyecto.
"""
import os

# Obtener la ruta raíz del proyecto (dos niveles arriba de este archivo)
ROOT_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
        )
    )


def get_abs_path(relative_path: str) -> str:
    """
    Convierte una ruta relativa a la raíz del proyecto en una ruta absoluta.

    Args:
        relative_path: Ruta relativa a la raíz del proyecto

    Returns:
        Ruta absoluta
    """
    return os.path.join(ROOT_DIR, relative_path)
