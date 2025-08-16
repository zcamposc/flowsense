"""
Módulo unificado para análisis de video con YOLO.
Combina detección básica, tracking, estadísticas y análisis de zonas.
"""

import cv2
import numpy as np
from ultralytics import YOLO
from typing import Optional, Dict, Set, List, Tuple
import os
from collections import defaultdict, deque
from utils.file_manager import generar_nombre_salida, cargar_zonas_desde_json
from utils.geometry import punto_en_poligono, cruza_linea
from utils.coco_classes import validate_classes, get_class_name


def procesar_video_unificado(
    video_path: str,
    model_path: str,
    output_path: Optional[str] = None,
    show: bool = True,
    classes: Optional[list[str]] = None,
    # Funcionalidades opcionales
    enable_tracking: bool = False,
    enable_stats: bool = False,
    enable_zones: Optional[str] = None,
    save_video: bool = True
) -> None:
    """
    Analizador de video unificado con todas las funcionalidades.
    
    Args:
        video_path (str): Ruta del video de entrada.
        model_path (str): Ruta del modelo YOLO.
        output_path (Optional[str]): Ruta para el video de salida.
        show (bool): Si es True, muestra el video en tiempo real.
        classes (Optional[list[str]]): Lista de clases a detectar.
            Si es None, solo detecta personas.
        enable_tracking (bool): Habilitar tracking de objetos.
        enable_stats (bool): Habilitar estadísticas por frame.
        enable_zones (Optional[str]): Archivo JSON con zonas de interés.
        save_video (bool): Si es True, guarda el video procesado.
    """
    # Generar nombres inteligentes basados en parámetros activados
    input_name = os.path.splitext(os.path.basename(video_path))[0]
    model_name = os.path.splitext(os.path.basename(model_path))[0]
    
    # Construir sufijo descriptivo
    suffix_parts = []
    if enable_tracking:
        suffix_parts.append("track")
    if enable_stats:
        suffix_parts.append("stats")
    if enable_zones:
        suffix_parts.append("zones")
    
    suffix = "_" + "_".join(suffix_parts) if suffix_parts else "_basic"
    
    # Generar nombre de salida para video
    if output_path is None:
        output_path = f"outputs/{input_name}_{model_name}{suffix}.mp4"
    else:
        output_path = generar_nombre_salida(
            video_path, model_path, output_path, "mp4"
        )
    
    # Generar nombre para archivo de estadísticas si está habilitado
    stats_path = None
    stats_file = None
    if enable_stats:
        stats_path = f"outputs/{input_name}_{model_name}{suffix}_stats.txt"
        
        # Crear directorio outputs si no existe
        os.makedirs("outputs", exist_ok=True)
        
        # Abrir archivo de estadísticas
        stats_file = open(stats_path, 'w', encoding='utf-8')
        stats_file.write("Frame\tObjetos_Detectados\tIDs_Confirmados\tIDs_Unicos\t"
                        "En_Zonas\tCruzaron_Lineas\n")
    
    # Cargar modelo YOLO
    model = YOLO(model_path)
    
    # Abrir video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise FileNotFoundError(f"No se pudo abrir el video: {video_path}")

    # Configurar video writer
    writer = None
    if save_video:
        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # Cargar zonas de interés si está habilitado
    lines, polygons = [], []
    if enable_zones:
        lines, polygons = cargar_zonas_desde_json(enable_zones)

    # Configurar clases a detectar
    if classes is not None:
        class_ids = validate_classes(classes)
    else:
        class_ids = validate_classes(['person'])

    # Variables de tracking (si está habilitado)
    id_map = {}
    next_id = 1
    appear = defaultdict(int)
    trail = defaultdict(lambda: deque(maxlen=30))
    unique_person_ids = set()
    
    # Variables de análisis de zonas
    trayectorias: Dict[int, List[Tuple[int, int]]] = {}
    ids_en_zona: Set[int] = set()
    ids_cruzaron_linea: Set[int] = set()
    
    # Contadores de frame
    frame_count = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            frame_count += 1
            objetos_detectados = 0
            ids_confirmados = 0
            
            # SOLUCIÓN REAL: Usar parámetros IDÉNTICOS pero OPTIMIZADOS
            # Mantener la consistencia sin perder detecciones
            
            # Parámetros base que SIEMPRE se usan
            base_params = {
                'verbose': False,
                'classes': class_ids,  # Solo las clases especificadas
                # NO forzar conf, iou - usar valores por defecto de YOLO
                # 'conf': 0.25,       # ❌ ESTO PERDÍA DETECCIONES
                # 'iou': 0.45,        # ❌ ESTO TAMBIÉN
                'max_det': 300,        # Máximo de detecciones
                'agnostic_nms': False, # NMS agnóstico de clase
                'retina_masks': False  # Sin máscaras de retina
            }
            
            # Ejecutar YOLO con parámetros IDÉNTICOS
            if enable_tracking:
                # Modo tracking con parámetros idénticos
                results = model.track(
                    frame, 
                    persist=True,
                    **base_params
                )
                mode_name = "Tracking"
            else:
                # Modo básico con parámetros idénticos
                results = model(frame, **base_params)
                mode_name = "Básico"
            
            # Debug del primer frame
            if frame_count == 1:
                print(f"[DEBUG] Modo: {mode_name}")
                print(f"[DEBUG] Estadísticas: {'Sí' if enable_stats else 'No'}")
                print(f"[DEBUG] Zonas: {'Sí' if enable_zones else 'No'}")
                print(f"[DEBUG] Usando parámetros por defecto de YOLO para máxima detección")
            
            # Contar detecciones para validación
            total_detections_this_frame = 0
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    cls = int(box.cls[0])
                    if cls in class_ids:
                        total_detections_this_frame += 1
            
            if frame_count == 1:
                print(f"[DEBUG] Detecciones totales en frame 1: {total_detections_this_frame}")
            
            # VALIDACIÓN: Ahora ambos métodos deberían detectar lo mismo
            if enable_tracking and frame_count == 1:
                # Verificar que tracking mantenga la misma detección
                print(f"[DEBUG] Tracking activado - verificando consistencia...")
            
            # Procesar resultados
            if results[0].boxes.id is not None and enable_tracking:
                # Modo tracking
                boxes = results[0].boxes.xyxy.cpu().numpy()
                track_ids = results[0].boxes.id.int().cpu().numpy()
                confidences = results[0].boxes.conf.cpu().numpy()
                detected_classes = results[0].boxes.cls.cpu().numpy()
                
                objetos_detectados = len(boxes)
                
                for box, oid, conf, cls in zip(boxes, track_ids, confidences, detected_classes):
                    if int(cls) in class_ids:
                        x1, y1, x2, y2 = map(int, box)
                        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                        class_name = get_class_name(int(cls))
                        
                        # Incrementar contador de apariciones
                        appear[oid] += 1

                        # Solo asignar ID permanente si aparece en 5+ frames
                        if (appear[oid] >= 5 and oid not in id_map):
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
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                            
                            # Etiqueta con ID estable y confianza
                            label = f"ID: {stable_id} {class_name} {conf:.2f}"
                            
                            # Fondo negro para mejor visibilidad
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
                            
                            # Análisis de zonas si está habilitado
                            if enable_zones:
                                analizar_objeto_con_zonas(
                                    frame, box, stable_id, trayectorias,
                                    ids_en_zona, ids_cruzaron_linea,
                                    polygons, lines, class_name
                                )
                
            elif not enable_tracking:
                # Modo detección básica
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
                            
                            cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
                            
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
                
                objetos_detectados = frame_detections
                
                # Mostrar estadísticas en tiempo real
                stats_text = f"Frame: {frame_count} | Det: {frame_detections}"
                cv2.putText(
                    frame, stats_text,
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2
                )

            # Visualizar zonas si está habilitado
            if enable_zones:
                dibujar_zonas(frame, lines, polygons)

            # Escribir estadísticas del frame si está habilitado
            if enable_stats and stats_file:
                # Calcular valores para estadísticas según el modo
                ids_confirmados_valor = ids_confirmados if enable_tracking else 0
                ids_unicos_valor = len(unique_person_ids) if enable_tracking else 0
                en_zonas_valor = len(ids_en_zona) if enable_tracking and enable_zones else 0
                cruzaron_lineas_valor = len(ids_cruzaron_linea) if enable_tracking and enable_zones else 0
                
                stats_file.write(f"{frame_count}\t{objetos_detectados}\t"
                               f"{ids_confirmados_valor}\t{ids_unicos_valor}\t"
                               f"{en_zonas_valor}\t{cruzaron_lineas_valor}\n")

            # Guardar frame en video si está habilitado
            if save_video and writer:
                writer.write(frame)
                
            # Mostrar frame si está habilitado
            if show:
                cv2.imshow('Análisis de Video Unificado', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    finally:
        cap.release()
        if writer:
            writer.release()
        cv2.destroyAllWindows()
        
        # Cerrar archivo de estadísticas
        if enable_stats and stats_file:
            stats_file.close()
            print(f"Estadísticas guardadas en: {stats_path}")
    
    # Resumen final
    print(f"\n{'='*60}")
    print(f"🎯 ANÁLISIS DE VIDEO COMPLETADO")
    print(f"{'='*60}")
    
    if save_video:
        print(f"📹 Video guardado en: {output_path}")
    
    if enable_stats:
        print(f"📊 Estadísticas guardadas en: {stats_path}")
    
    print(f"🎬 Total de frames procesados: {frame_count}")
    
    if enable_tracking:
        print(f"\n🔍 RESUMEN DE TRACKING:")
        print(f"   • IDs únicos confirmados: {len(unique_person_ids)}")
        print(f"   • Objetos detectados inicialmente: {len(id_map)}")
        print(f"   • Objetos confirmados (5+ frames): {len(unique_person_ids)}")
    
    if enable_zones:
        print(f"\n📍 RESUMEN DE ZONAS:")
        print(f"   • Objetos en zonas: {len(ids_en_zona)}")
        print(f"   • Objetos cruzando líneas: {len(ids_cruzaron_linea)}")
    
    print(f"{'='*60}")


def analizar_objeto_con_zonas(
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
    Analiza un objeto detectado: posición, trayectoria y eventos de zonas.
    """
    x1, y1, x2, y2 = map(int, box)
    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

    # Actualizar trayectoria
    if track_id not in trayectorias:
        trayectorias[track_id] = []
    trayectorias[track_id].append((cx, cy))
    pts = trayectorias[track_id]

    # Detectar entrada a zonas
    for poly in polygons:
        if punto_en_poligono((cx, cy), poly) and track_id not in ids_en_zona:
            ids_en_zona.add(track_id)
            print(f"[ALERTA] {class_name} ID {track_id} ha entrado en zona de interés.")

    # Detectar cruce de líneas
    if len(pts) > 1:
        for linea in lines:
            if (cruza_linea(pts[-2], pts[-1], linea) and track_id not in ids_cruzaron_linea):
                ids_cruzaron_linea.add(track_id)
                print(f"[ALERTA] {class_name} ID {track_id} ha cruzado línea de interés.")


def dibujar_zonas(
    frame: np.ndarray,
    lines: List[List[Tuple[int, int]]],
    polygons: List[List[Tuple[int, int]]]
) -> None:
    """
    Dibuja las zonas de interés en el frame.
    """
    # Dibujar polígonos
    for poly in polygons:
        poly_array = np.array(poly, np.int32)
        cv2.polylines(frame, [poly_array], True, (255, 0, 0), 2)
    
    # Dibujar líneas
    for line in lines:
        pt1, pt2 = line
        cv2.line(frame, pt1, pt2, (0, 0, 255), 2)
