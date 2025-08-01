import cv2
from ultralytics import YOLO
from typing import Optional
from utils.file_manager import generar_nombre_salida


def procesar_video(
    video_path: str,
    model_path: str,
    output_path: Optional[str] = None,
    show: bool = True,
    classes: Optional[list[str]] = None
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
        
        results = model(frame)
        for result in results:
            boxes = result.boxes
            for box in boxes:
                cls = int(box.cls[0])
                if cls in class_ids:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    conf = float(box.conf[0])
                    class_name = get_class_name(cls)
                    label = f"{class_name} {conf:.2f}"
                    cv2.rectangle(
                        frame, (x1, y1), (x2, y2), (0, 255, 0), 2
                    )
                    cv2.putText(
                        frame, label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
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
    print(f"Video procesado guardado en: {output_path}")
