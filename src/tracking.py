import cv2
from ultralytics import YOLO
from typing import Optional
from utils.file_manager import generar_nombre_salida
import numpy as np


def realizar_tracking(
    video_path: str,
    model_path: str,
    output_path: Optional[str] = None,
    show: bool = True,
    classes: Optional[list[str]] = None
) -> None:
    """
    Realiza seguimiento de objetos en un video usando YOLO en modo tracking.

    Args:
        video_path (str): Ruta del archivo de video de entrada.
        model_path (str): Ruta al modelo YOLO pre-entrenado.
        output_path (Optional[str]): Ruta para guardar el video de salida.
        show (bool): Si es True, muestra el video mientras se procesa.
        classes (Optional[list[str]]): Lista de clases a detectar. Si es None,
            detecta todas.
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

    unique_person_ids = set()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Configurar las clases a detectar
        if classes is not None:
            class_ids = [model.names.index(c) for c in classes]
        else:
            class_ids = None
            
        # Ejecutar tracking
        results = model.track(frame, persist=True, classes=class_ids)
        
        if results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            track_ids = results[0].boxes.id.int().cpu().numpy()
            confidences = results[0].boxes.conf.cpu().numpy()
            detected_classes = results[0].boxes.cls.cpu().numpy()

            for box, track_id, conf, cls in zip(
                boxes, track_ids, confidences, detected_classes
            ):
                x1, y1, x2, y2 = map(int, box)
                class_name = model.names[int(cls)]
                unique_person_ids.add(int(track_id))
                label = f"ID: {int(track_id)} {class_name} {conf:.2f}"
                cv2.rectangle(
                    frame, (x1, y1), (x2, y2), (0, 255, 0), 2
                )
                # Colocar etiqueta con fondo negro para mejor visibilidad
                # Obtener tamaño de la etiqueta
                label_size = cv2.getTextSize(
                    label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2
                )[0]
                cv2.rectangle(
                    frame,
                    (x1, y1 - 30),
                    (x1 + label_size[0], y1),
                    (0, 0, 0),
                    -1
                )
                cv2.putText(
                    frame, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
                )
        if writer is not None:
            writer.write(frame)
            
        if show:
            cv2.imshow('Seguimiento de Objetos', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    if writer is not None:
        writer.release()
    n_ids = len(unique_person_ids)
    print(f"Tracking finalizado. Total IDs únicos: {n_ids}")


def punto_en_poligono(point, polygon):
    """Devuelve True si el punto está dentro del polígono
    (usando ray casting)."""
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
