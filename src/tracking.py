import cv2
from ultralytics import YOLO
from typing import Optional
from utils.file_manager import generar_nombre_salida
import numpy as np
from collections import defaultdict, deque
import os


def realizar_tracking(
    video_path: str,
    model_path: str,
    output_path: Optional[str] = None,
    show: bool = True,
    classes: Optional[list[str]] = None,
    conf_threshold: float = 0.5,
    save_stats: bool = True
) -> None:
    """
    Realiza seguimiento de objetos en un video usando YOLO en modo tracking.

    Args:
        video_path (str): Ruta del archivo de video de entrada.
        model_path (str): Ruta al modelo YOLO pre-entrenado.
        output_path (Optional[str]): Ruta para guardar el video de salida.
        show (bool): Si es True, muestra el video mientras se procesa.
        classes (Optional[list[str]]): Lista de clases a detectar. Si es None,
            detecta solo personas.
        conf_threshold (float): Umbral de confianza para detecciones.
            Por defecto 0.25 para mayor sensibilidad.
        save_stats (bool): Si es True, guarda estadísticas de detección por 
            frame en un archivo de texto.
    """
    output_path = generar_nombre_salida(
        video_path, model_path, output_path, "mp4"
    )
    
    # Generar nombre para el archivo de estadísticas
    stats_path = None
    if save_stats:
        input_name = os.path.splitext(os.path.basename(video_path))[0]
        model_name = os.path.splitext(os.path.basename(model_path))[0]
        stats_path = f"outputs/{input_name}_{model_name}_" \
                     f"tracking_stats.txt"
        
        # Crear directorio outputs si no existe
        os.makedirs("outputs", exist_ok=True)
        
        # Abrir archivo de estadísticas
        stats_file = open(stats_path, 'w', encoding='utf-8')
        stats_file.write("Frame\tObjetos_Detectados\tIDs_Confirmados\t"
                         "IDs_Unicos\n")
    
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

    # Sistema de confirmación mejorado
    id_map = {}  # Mapeo de IDs de YOLO a IDs secuenciales estables
    next_id = 1  # Contador para IDs secuenciales
    appear = defaultdict(int)  # Contador de frames consecutivos por objeto
    trail = defaultdict(lambda: deque(maxlen=30))  # Trayectorias de objetos
    unique_person_ids = set()
    
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        frame_count += 1
        objetos_detectados = 0
        ids_confirmados = 0

        # Configurar las clases a detectar (igual que sript_test.py)
        if classes is not None:
            class_ids = [model.names.index(c) for c in classes]
        else:
            # Por defecto, solo detecta personas (clase 0)
            class_ids = [0]
            
        # Ejecutar tracking con persistencia (igual que sript_test.py)
        results = model.track(
            frame, 
            persist=True, 
            classes=class_ids, 
            verbose=False
        )
        
        if results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            track_ids = results[0].boxes.id.int().cpu().numpy()
            confidences = results[0].boxes.conf.cpu().numpy()
            detected_classes = results[0].boxes.cls.cpu().numpy()
            
            objetos_detectados = len(boxes)

            for box, oid, conf, cls in zip(
                boxes, track_ids, confidences, detected_classes
            ):
                x1, y1, x2, y2 = map(int, box)
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                class_name = model.names[int(cls)]
                
                # Incrementar contador de apariciones
                appear[oid] += 1

                # Solo asignar ID permanente si aparece en 5+ frames
                if (appear[oid] >= 5 and 
                    oid not in id_map):
                    id_map[oid] = next_id
                    next_id += 1

                # Solo procesar objetos confirmados
                if oid in id_map:
                    stable_id = id_map[oid]
                    unique_person_ids.add(stable_id)
                    ids_confirmados += 1
                    
                    # Agregar posición actual a la trayectoria
                    trail[stable_id].append((cx, cy))
                    
                    # Dibujar bounding box
                    cv2.rectangle(
                        frame, (x1, y1), (x2, y2), (0, 255, 0), 2
                    )
                    
                    # Etiqueta con ID estable y confianza
                    label = f"ID: {stable_id} {class_name} {conf:.2f}"
                    
                    # Fondo negro para mejor visibilidad
                    label_size = cv2.getTextSize(
                        label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2
                    )[0]
                    # Dibujar rectángulo negro como fondo para la etiqueta
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
                    
                    # Dibujar trayectoria
                    trail_points = list(trail[stable_id])
                    if len(trail_points) > 1:
                        for i in range(1, len(trail_points)):
                            cv2.line(
                                frame, 
                                trail_points[i - 1], 
                                trail_points[i], 
                                (0, 0, 255), 
                                2
                            )
                    
                    # Círculo en el centro del objeto
                    cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

        # Escribir estadísticas del frame en el archivo
        if save_stats and stats_file:
            stats_file.write(f"{frame_count}\t{objetos_detectados}\t"
                             f"{ids_confirmados}\t{len(unique_person_ids)}\n")

        if writer is not None:
            writer.write(frame)
            
        if show:
            cv2.imshow('Seguimiento de Objetos', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    if writer is not None:
        writer.release()
    cv2.destroyAllWindows()
    
    # Cerrar archivo de estadísticas
    if save_stats and stats_file:
        stats_file.close()
        print(f"Estadísticas de tracking guardadas en: "
              f"{stats_path}")
    
    n_ids = len(unique_person_ids)
    print(f"Tracking finalizado. Total IDs únicos confirmados: {n_ids}")
    print(f"Objetos detectados inicialmente: {len(id_map)}")
    print(f"Objetos confirmados (5+ frames): {n_ids}")
    print(f"Total de frames procesados: {frame_count}")


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
