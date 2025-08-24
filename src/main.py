"""
CLI para análisis de video unificado usando YOLO.
"""
import typer
from typing import Optional
from video_unified import procesar_video_unificado
from utils.paths import get_abs_path


app = typer.Typer(
    help="Análisis de video unificado con YOLO, tracking y análisis de zonas."
)


def ejecutar_video_con_excepciones(func, *args, **kwargs):
    """
    Ejecuta una función de procesamiento de video y maneja las excepciones.
    """
    try:
        func(*args, **kwargs)
        typer.echo("Procesamiento de video finalizado.")
    except FileNotFoundError as e:
        typer.echo(str(e))
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"Error durante el procesamiento: {str(e)}")
        raise typer.Exit(code=1)


@app.command()
def process(
    video_path: str = typer.Option(
        ..., help="Ruta del archivo de video de entrada"
    ),
    model_path: str = typer.Option(
        ..., help="Ruta al modelo YOLO (por ejemplo, yolov8n.pt)"
    ),
    output_path: Optional[str] = typer.Option(
        None, help="Ruta para guardar el video de salida"
    ),
    show: bool = typer.Option(
        True, help="Mostrar visualización en tiempo real"
    ),
    classes: Optional[str] = typer.Option(
        None,
        help="Lista de objetos a detectar (ej: person,car,dog). "
             "Por defecto: detecta TODOS los objetos. Ver clases disponibles en: "
             "https://github.com/ultralytics/ultralytics/blob/main/"
             "ultralytics/cfg/datasets/coco.yaml"
    ),
    conf_threshold: Optional[float] = typer.Option(
        None, 
        help="Umbral de confianza para detecciones (0.0-1.0). "
             "Si no se especifica, usa la configuración por defecto de YOLO"
    ),
    enable_stats: bool = typer.Option(
        False, help="Habilitar generación de estadísticas por frame"
    ),
    enable_zones: bool = typer.Option(
        False,
        help="Habilitar análisis de zonas y líneas"
    ),
    zones_config: Optional[str] = typer.Option(
        None,
        help="Ruta al archivo JSON de configuración de zonas"
    ),
    save_video: bool = typer.Option(
        True, help="Guardar video procesado"
    ),
    enable_database: bool = typer.Option(
        False, help="Habilitar funcionalidad de base de datos"
    )
) -> None:
    """
    Procesa un video usando el analizador unificado con YOLO, 
    tracking y análisis de zonas.
    """
    # Convertir rutas relativas a absolutas
    video_abs_path = get_abs_path(video_path)
    model_abs_path = get_abs_path(model_path)
    output_abs_path = (
        None if output_path is None else get_abs_path(output_path)
    )
    
    # Convertir lista de clases si se proporciona
    class_list = None
    if classes:
        class_list = [c.strip() for c in classes.split(',')]

    ejecutar_video_con_excepciones(
        procesar_video_unificado,
        video_abs_path,
        model_abs_path,
        output_abs_path,
        show_video=show,
        classes=class_list,
        conf_threshold=conf_threshold,
        enable_stats=enable_stats,
        enable_zones=enable_zones,
        zones_config=zones_config,
        save_video=save_video,
        enable_database=enable_database
    )


if __name__ == "__main__":
    app()
