"""
Módulo para análisis avanzado de video con YOLO.
"""
import cv2
import numpy as np
from ultralytics import YOLO
from typing import Optional, Dict, Set, List, Tuple
import typer
from utils.file_manager import generar_nombre_salida, cargar_zonas_desde_json
from utils.geometry import punto_en_poligono, cruza_linea


def analizar_video(
    video_path: str,
    model_path: str,
    zones_json: Optional[str] = None,
    output_path: Optional[str] = None,
    show: bool = True,
    classes: Optional[list[str]] = None
) -> None:
    """
    Analiza video con detección de objetos, trayectorias y zonas de interés.

    Args:
        video_path (str): Ruta del video de entrada.
        model_path (str): Ruta del modelo YOLO.
        zones_json (Optional[str]): Archivo JSON con zonas de interés.
        output_path (Optional[str]): Ruta para el video de salida.
        show (bool): Si es True, muestra el video en tiempo real.
        classes (Optional[list[str]]): Lista de clases a detectar.
            Si es None, solo detecta personas.
    """
    output_path = generar_nombre_salida(
        video_path, model_path, output_path, "mp4"
    )
    model = YOLO(model_path)
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise FileNotFoundError(f"No se pudo abrir el video: {video_path}")

    writer = None
    if output_path is not None:
        # Usar códec H.264 que es más compatible
        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        writer = cv2.VideoWriter(
            output_path, fourcc, fps, (width, height)
        )

    # Cargar zonas de interés
    lines, polygons = [], []
    if zones_json is not None:
        lines, polygons = cargar_zonas_desde_json(zones_json)

    # Tracking y análisis
    trayectorias: Dict[int, List[Tuple[int, int]]] = {}
    ids_en_zona: Set[int] = set()
    ids_cruzaron_linea: Set[int] = set()

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            from utils.coco_classes import validate_classes, get_class_name
            
            # Por defecto, solo detecta personas
            class_ids = validate_classes(['person']) if classes is None else validate_classes(classes)
            
            results = model.track(frame, persist=True)
            if results[0].boxes.id is not None:
                boxes = results[0].boxes.xyxy.cpu().numpy()
                track_ids = results[0].boxes.id.int().cpu().numpy()
                detected_classes = results[0].boxes.cls.cpu().numpy()

                for box, track_id, cls in zip(boxes, track_ids, detected_classes):
                    if int(cls) in class_ids:  # objeto de interés
                        class_name = get_class_name(int(cls))
                        analizar_persona(
                            frame, box, track_id, trayectorias,
                            ids_en_zona, ids_cruzaron_linea,
                            polygons, lines, class_name
                        )

            # Visualizar zonas
            dibujar_zonas(frame, lines, polygons)
            
            if show:
                cv2.imshow('Análisis de Video', frame)
            if writer is not None:
                writer.write(frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        cap.release()
        if writer is not None:
            writer.release()
        cv2.destroyAllWindows()

    typer.echo("Análisis de video finalizado.")


def analizar_persona(
    frame: np.ndarray,
    box: np.ndarray,
    track_id: int,
    trayectorias: Dict[int, List[Tuple[int, int]]],
    ids_en_zona: Set[int],
    ids_cruzaron_linea: Set[int],
    polygons: List[List[Tuple[int, int]]],
    lines: List[List[Tuple[int, int]]],
    class_name: str = "objeto"
) -> None:
    """
    Analiza un objeto detectado: posición, trayectoria y eventos.
    """
    x1, y1, x2, y2 = map(int, box)
    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
    track_id = int(track_id)

    # Actualizar trayectoria
    if track_id not in trayectorias:
        trayectorias[track_id] = []
    trayectorias[track_id].append((cx, cy))
    pts = trayectorias[track_id]

    # Dibujar trayectoria
    for i in range(1, len(pts)):
        cv2.line(frame, pts[i-1], pts[i], (0, 0, 255), 2)

    # Dibujar bounding box e ID
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.putText(
        frame, f"ID:{track_id}", (x1, y1-10),
        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
    )

    # Detectar entrada a zonas
    for poly in polygons:
        if punto_en_poligono((cx, cy), poly) and track_id not in ids_en_zona:
            ids_en_zona.add(track_id)
            typer.echo(
                f"[ALERTA] {class_name} ID {track_id} "
                f"ha entrado en zona de interés."
            )

    # Detectar cruce de líneas
    if len(pts) > 1:
        for linea in lines:
            if (cruza_linea(pts[-2], pts[-1], linea) and track_id not in ids_cruzaron_linea):
                ids_cruzaron_linea.add(track_id)
                typer.echo(
                    f"[ALERTA] {class_name} ID {track_id} "
                    f"ha cruzado línea de interés."
                )


def dibujar_zonas(
    frame: np.ndarray,
    lines: List[List[Tuple[int, int]]],
    polygons: List[List[Tuple[int, int]]]
) -> None:
    """
    Dibuja las zonas de interés en el frame.
    """
    for linea in lines:
        cv2.line(
            frame, tuple(linea[0]), tuple(linea[1]),
            (255, 0, 0), 2
        )
    
    for poly in polygons:
        pts = np.array(poly, np.int32).reshape((-1, 1, 2))
        cv2.polylines(
            frame, [pts], True,
            color=(0, 255, 255), thickness=2
        )
