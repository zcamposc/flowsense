import cv2
from ultralytics import YOLO
from typing import Optional


def detectar_objetos_en_imagen(
    image_path: str,
    model_path: str,
    output_path: Optional[str] = None,
    show: bool = True,
    classes: Optional[list[str]] = None,
    conf_threshold: float = 0.25
) -> None:
    """
    Detecta objetos en una imagen usando un modelo YOLO y guarda la imagen
    resultante con los bounding boxes.

    Args:
        image_path (str): Ruta de la imagen de entrada.
        model_path (str): Ruta al modelo YOLO pre-entrenado.
        output_path (Optional[str]): Ruta para guardar la imagen de salida.
            Si es None, se usará 'output_image.png'.
        show (bool): Si es True, muestra la imagen con las detecciones.
        classes (Optional[list[str]]): Lista de clases a detectar.
            Si es None, solo detecta personas.

    Raises:
        FileNotFoundError: Si la imagen no se puede cargar.
        ValueError: Si alguna de las clases especificadas no es válida.
    """
    model = YOLO(model_path)
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(
            f"No se pudo cargar la imagen: {image_path}"
        )

    from utils.coco_classes import validate_classes, get_class_name
    
    # Por defecto, solo detecta personas
    class_ids = (
        validate_classes(['person'])
        if classes is None
        else validate_classes(classes)
    )
    
    # Ejecutar detección (igual que sript_test.py - sin parámetro conf)
    results = model(image, verbose=False)
    
    detections_count = 0
    for result in results:
        boxes = result.boxes
        for box in boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            
            # Solo procesar si la clase está en la lista de interés
            if cls in class_ids:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                class_name = get_class_name(cls)
                label = f"{class_name} {conf:.2f}"
                
                # Dibujar bounding box con color basado en confianza
                color = (0, 255, 0) if conf > 0.5 else (0, 165, 255)
                thickness = 2 if conf > 0.5 else 1
                
                cv2.rectangle(
                    image, (x1, y1), (x2, y2), color, thickness
                )
                
                # Fondo negro para mejor visibilidad del texto
                label_size = cv2.getTextSize(
                    label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2
                )[0]
                cv2.rectangle(
                    image,
                    (x1, y1 - 30),
                    (x1 + label_size[0], y1),
                    (0, 0, 0),
                    -1
                )
                
                cv2.putText(
                    image, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2
                )
                
                detections_count += 1

    if output_path is None:
        output_path = 'output_image.png'
    cv2.imwrite(output_path, image)
    print(f"Imagen de salida guardada en: {output_path}")
    print(f"Total de objetos detectados: {detections_count}")
    
    if show:
        cv2.imshow('Detección de Objetos', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
