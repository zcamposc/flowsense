"""
CLI para detección y análisis de objetos en imágenes y videos usando YOLO.
"""
import typer
from typing import Optional
from detect import detectar_objetos_en_imagen
from video_processing import procesar_video
from tracking import realizar_tracking
from video_unified import procesar_video_unificado
from utils.file_manager import generar_nombre_salida
from utils.paths import get_abs_path


app = typer.Typer(help="Detección de personas en imágenes usando YOLO.")


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
def video(
    video_path: str = typer.Option(
        ..., help="Ruta del archivo de video de entrada"
    ),
    model_path: str = typer.Option(
        ..., help="Ruta al modelo YOLO (por ejemplo, yolov8n.pt)"
    ),
    output_path: Optional[str] = typer.Option(
        None, help="Ruta para guardar el video de salida con detecciones"
    ),
    show: bool = typer.Option(
        True, help="Mostrar visualización en tiempo real"
    ),
    classes: Optional[str] = typer.Option(
        None,
        help="Lista de objetos a detectar (ej: person,car,dog). "
             "Por defecto: person"
    ),
    conf_threshold: float = typer.Option(
        0.25, help="Umbral de confianza para detecciones (0.0-1.0)"
    )
) -> None:
    """
    Detecta personas en un video usando un modelo YOLO.
    Muestra resultados en tiempo real y guarda el video procesado.
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
        procesar_video,
        video_abs_path,
        model_abs_path,
        output_abs_path,
        show=show,
        classes=class_list,
        conf_threshold=conf_threshold
    )


@app.command()
def track(
    video_path: str = typer.Option(
        ..., help="Ruta del archivo de video de entrada"
    ),
    model_path: str = typer.Option(
        ..., help="Ruta al modelo YOLO (por ejemplo, yolov8n.pt)"
    ),
    output_path: Optional[str] = typer.Option(
        None, help="Ruta para guardar el video de salida con tracking"
    ),
    show: bool = typer.Option(
        True, help="Mostrar visualización en tiempo real"
    ),
    classes: Optional[str] = typer.Option(
        None,
        help="Lista de objetos a detectar (ej: person,car). "
             "Por defecto: person"
    ),
    conf_threshold: float = typer.Option(
        0.25, help="Umbral de confianza para detecciones (0.0-1.0)"
    ),
    save_stats: bool = typer.Option(
        True, help="Guardar estadísticas de detección por frame en "
                   "archivo de texto"
    )
) -> None:
    """
    Realiza seguimiento de objetos en un video usando YOLO.
    
    Detecta y hace seguimiento de los objetos especificados.
    Muestra y cuenta los IDs únicos de seguimiento.
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
        realizar_tracking,
        video_abs_path,
        model_abs_path,
        output_abs_path,
        show=show,
        classes=class_list,
        conf_threshold=conf_threshold,
        save_stats=save_stats
    )


@app.command()
def analyze(
    video_path: str = typer.Option(
        ..., help="Ruta del archivo de video de entrada"
    ),
    model_path: str = typer.Option(
        ..., help="Ruta al modelo YOLO (por ejemplo, yolov8n.pt)"
    ),
    zones_json: Optional[str] = typer.Option(
        None, help="Archivo JSON con definición de zonas de interés"
    ),
    output_path: Optional[str] = typer.Option(
        None, help="Ruta para guardar el video de salida con análisis"
    ),
    show: bool = typer.Option(
        True, help="Mostrar visualización en tiempo real"
    ),
    classes: Optional[str] = typer.Option(
        None,
        help="Lista de objetos a detectar (ej: person,car). "
             "Por defecto: person"
    ),
    conf_threshold: float = typer.Option(
        0.25, help="Umbral de confianza para detecciones (0.0-1.0)"
    )
) -> None:
    """
    Analiza video con detección de movimiento y zonas de interés.
    Genera alertas basadas en las definiciones del archivo JSON.
    """
    from video_analysis import analizar_video
    # Convertir rutas relativas a absolutas
    video_abs_path = get_abs_path(video_path)
    model_abs_path = get_abs_path(model_path)
    zones_abs_path = None if zones_json is None else get_abs_path(zones_json)
    output_abs_path = (
        None if output_path is None else get_abs_path(output_path)
    )
    
    # Convertir lista de clases si se proporciona
    class_list = None
    if classes:
        class_list = [c.strip() for c in classes.split(',')]

    ejecutar_video_con_excepciones(
        analizar_video,
        video_abs_path,
        model_abs_path,
        zones_abs_path,
        output_abs_path,
        show=show,
        classes=class_list,
        conf_threshold=conf_threshold
    )


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
        help="Lista de objetos a detectar (ej: person,car). "
             "Por defecto: person"
    ),
    enable_tracking: bool = typer.Option(
        False, help="Habilitar tracking de objetos"
    ),
    enable_stats: bool = typer.Option(
        False, help="Habilitar estadísticas por frame"
    ),
    enable_zones: Optional[str] = typer.Option(
        None, help="Archivo JSON con definición de zonas de interés"
    ),
    save_video: bool = typer.Option(
        True, help="Guardar video procesado"
    )
) -> None:
    """
    Analizador de video unificado con todas las funcionalidades.
    
    Combina detección básica, tracking, estadísticas y análisis de zonas
    en un solo comando configurable.
    """
    # Convertir rutas relativas a absolutas
    video_abs_path = get_abs_path(video_path)
    model_abs_path = get_abs_path(model_path)
    output_abs_path = (
        None if output_path is None else get_abs_path(output_path)
    )
    zones_abs_path = None if enable_zones is None else get_abs_path(enable_zones)

    # Convertir lista de clases si se proporciona
    class_list = None
    if classes:
        class_list = [c.strip() for c in classes.split(',')]
    
    ejecutar_video_con_excepciones(
        procesar_video_unificado,
        video_abs_path,
        model_abs_path,
        output_abs_path,
        show=show,
        classes=class_list,
        enable_tracking=enable_tracking,
        enable_stats=enable_stats,
        enable_zones=zones_abs_path,
        save_video=save_video
    )


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    image: str = typer.Option(
        None, help="Ruta de la imagen de entrada"
    ),
    model: str = typer.Option(
        None, help="Ruta al modelo YOLO (por ejemplo, yolov8n.pt)"
    ),
    output: Optional[str] = typer.Option(
        None, help="Ruta para guardar la imagen de salida"
    ),
    show: bool = typer.Option(
        True, help="Mostrar visualización en tiempo real"
    ),
    classes: Optional[str] = typer.Option(
        None,
        help="Lista de objetos a detectar (ej: person,car). "
             "Por defecto: person"
    ),
    conf_threshold: float = typer.Option(
        0.25, help="Umbral de confianza para detecciones (0.0-1.0)"
    )
) -> None:
    """Detecta personas en una imagen usando YOLO."""
    if ctx.invoked_subcommand is not None:
        return
        
    if not image or not model:
        typer.echo("Se requieren los parámetros --image y --model")
        raise typer.Exit(code=1)
        
    # Convertir rutas relativas a absolutas
    image_path = get_abs_path(image)
    model_path = get_abs_path(model)
    output_path = generar_nombre_salida(
        image, model_path, output, "png"
    )
    output_path = get_abs_path(output_path)
    
    # Convertir lista de clases si se proporciona
    class_list = None
    if classes:
        class_list = [c.strip() for c in classes.split(',')]

    try:
        detectar_objetos_en_imagen(
            image_path,
            model_path,
            output_path,
            show=show,
            classes=class_list
        )
    except FileNotFoundError as e:
        typer.echo(str(e))
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
