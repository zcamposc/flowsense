import cv2
from ultralytics import YOLO
from typing import Optional
from utils.file_manager import generar_nombre_salida


def procesar_video(
    video_path: str,
    model_path: str,
    output_path: Optional[str] = None,
    show: bool = True,
    classes: Optional[list[str]] = None,
    conf_threshold: float = 0.25
) -> None:
    """
    Detecta objetos en un video usando un modelo YOLO y guarda el video procesado.

    Args:
        video_path (str): Ruta del archivo de video de entrada.
        model_path (str): Ruta al modelo YOLO pre-entrenado.
        output_path (Optional[str]): Ruta para guardar el video de salida.
        show (bool): Si es True, muestra el video en tiempo real.
        classes (Optional[list[str]]): Lista de clases a detectar.
            Si es None, solo detecta personas.
        conf_threshold (float): Umbral de confianza para detecciones.
            Por defecto 0.25 para mayor sensibilidad.
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

    frame_count = 0
    total_detections = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        from utils.coco_classes import validate_classes, get_class_name
        
        # Por defecto, solo detecta personas
        class_ids = (
            validate_classes(['person'])
            if classes is None
            else validate_classes(classes)
        )
        
        # Ejecutar detección (igual que sript_test.py - sin parámetro conf)
        results = model(frame, verbose=False)
        
        frame_detections = 0
        for result in results:
            boxes = result.boxes
            for box in boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                
                if cls in class_ids:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    class_name = get_class_name(cls)
                    label = f"{class_name} {conf:.2f}"
                    
                    # Dibujar bounding box con color basado en confianza
                    color = (0, 255, 0) if conf > 0.5 else (0, 165, 255)
                    thickness = 2 if conf > 0.5 else 1
                    
                    cv2.rectangle(
                        frame, (x1, y1), (x2, y2), color, thickness
                    )
                    
                    # Fondo negro para mejor visibilidad del texto
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
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2
                    )
                    
                    frame_detections += 1
        
        total_detections += frame_detections
        
        # Mostrar estadísticas en tiempo real
        stats_text = f"Frame: {frame_count} | Det: {frame_detections}"
        cv2.putText(
            frame, stats_text,
            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2
        )
        
        if writer is not None:
            writer.write(frame)
            
        if show:
            cv2.imshow('Detección de Objetos', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    if writer is not None:
        writer.release()
    cv2.destroyAllWindows()
    
    print(f"Video procesado guardado en: {output_path}")
    print(f"Total de frames procesados: {frame_count}")
    print(f"Total de detecciones: {total_detections}")
    avg_detections = total_detections/frame_count if frame_count > 0 else 0
    print(f"Promedio de detecciones por frame: {avg_detections:.2f}")
