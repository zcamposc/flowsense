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
from utils.file_manager import generar_nombre_salida, cargar_zonas_desde_json, cargar_nombres_zonas
from utils.geometry import punto_en_poligono, cruza_linea
from utils.coco_classes import validate_classes, get_class_name

# Importar módulos necesarios
from datetime import datetime

# Importar módulo de persistencia
try:
    from persistence import CSVWriter, DetectionEvent
    PERSISTENCE_AVAILABLE = True
except ImportError:
    PERSISTENCE_AVAILABLE = False
    print("[INFO] Módulo de persistencia no disponible.")


def procesar_video_unificado(
    video_path: str,
    model_path: str,
    output_path: Optional[str] = None,
    show: bool = True,
    classes: Optional[list[str]] = None,
    conf_threshold: Optional[float] = None,
    # Funcionalidades opcionales
    enable_stats: bool = False,
    enable_zones: Optional[str] = None,
    save_video: bool = True,
    # Nueva funcionalidad: Base de datos
    enable_database: bool = False
) -> None:
    """
    Analizador de video unificado con tracking siempre activo.
    
    Args:
        video_path (str): Ruta del video de entrada.
        model_path (str): Ruta del modelo YOLO.
        output_path (Optional[str]): Ruta para el video de salida.
        show (bool): Si es True, muestra el video en tiempo real.
        classes (Optional[list[str]]): Lista de clases a detectar.
            Si es None, solo detecta personas.
        conf_threshold (Optional[float]): Umbral de confianza para detecciones.
            Si es None, usa la configuración por defecto de YOLO.
        enable_stats (bool): Habilitar estadísticas por frame.
        enable_zones (Optional[str]): Archivo JSON con zonas de interés.
        save_video (bool): Si es True, guarda el video procesado.
        enable_database (bool): Habilitar funcionalidad de base de datos.
    """
    # Generar nombres inteligentes basados en parámetros activados
    input_name = os.path.splitext(os.path.basename(video_path))[0]
    model_name = os.path.splitext(os.path.basename(model_path))[0]
    
    # Construir sufijo descriptivo
    suffix_parts = []
    if enable_stats:
        suffix_parts.append("stats")
    if enable_zones:
        suffix_parts.append("zones")
    
    suffix = "_" + "_".join(suffix_parts) if suffix_parts else "_track"
    
    # Generar nombre de salida para video
    if output_path is None:
        # Generar nombre único automático con timestamp para evitar sobrescrituras
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"outputs/{input_name}_{model_name}{suffix}_{timestamp}.mp4"
    else:
        output_path = generar_nombre_salida(
            video_path, model_path, output_path, "mp4"
        )
    
    # Generar nombre para archivo de estadísticas si está habilitado
    stats_path = None
    stats_file = None
    if enable_stats:
        # Siempre usar el mismo nombre base que el video (con sufijo _stats)
        output_base = os.path.splitext(os.path.basename(output_path))[0]
        stats_path = f"outputs/{output_base}_stats.txt"
        
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
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # Cargar zonas de interés si está habilitado
    lines, polygons = [], []
    if enable_zones:
        lines, polygons = cargar_zonas_desde_json(enable_zones)

    # Inicializar módulo de persistencia
    persistence_writer = None
    zones_config = []
    
    if PERSISTENCE_AVAILABLE:
        try:
            # Crear directorio para CSV
            csv_output_dir = f"outputs/csv_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Inicializar escritor de CSV
            persistence_writer = CSVWriter(csv_output_dir)
            
            # Cargar nombres personalizados de zonas si están disponibles
            zone_names = cargar_nombres_zonas(enable_zones)
            
            # Configurar zonas para el escritor
            if enable_zones and polygons:
                for i, polygon in enumerate(polygons):
                    zone_id = zone_names.get(f"polygon_{i+1}", f"zone_polygon_{i+1}")
                    zones_config.append((zone_id, "polygon", polygon))
            
            if enable_zones and lines:
                for i, line in enumerate(lines):
                    line_id = zone_names.get(f"line_{i+1}", f"zone_line_{i+1}")
                    zones_config.append((line_id, "line", line))
                    
        except Exception as e:
            print(f"[ERROR] No se pudo inicializar persistencia: {e}")
            persistence_writer = None
            zones_config = []

    # Configurar clases a detectar
    if classes is not None:
        class_ids = validate_classes(classes)
    else:
        # Si no se especifican clases, usar solo 'person' por defecto
        class_ids = validate_classes(['person'])

    # Variables de tracking (siempre activo)
    # Variables de tracking
    id_map = {}
    next_id = 1
    trail = defaultdict(lambda: deque(maxlen=30))
    unique_person_ids = set()
    
    # Variables de análisis de zonas
    trayectorias: Dict[int, List[Tuple[int, int]]] = {}
    ids_en_zona: Dict[int, Set[str]] = {}  # track_id -> set of zone_ids
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
            
            # Tracking siempre activo para máxima consistencia
            # Usar parámetros por defecto de YOLO para máxima detección
            
            # Preparar parámetros para YOLO
            track_params = {
                'persist': True,
                'verbose': False
            }
            
            # Agregar conf_threshold solo si se especifica
            if conf_threshold is not None:
                track_params['conf'] = conf_threshold
            
            # Ejecutar YOLO con tracking SIEMPRE activo
            results = model.track(frame, **track_params)
            
            # Contar detecciones para validación
            total_detections_this_frame = 0
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    cls = int(box.cls[0])
                    if cls in class_ids:
                        total_detections_this_frame += 1
            
            # Procesar resultados (tracking siempre activo)
            if results[0].boxes.id is not None:
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
                        
                        # Asignar ID permanente inmediatamente
                        if oid not in id_map:
                            id_map[oid] = next_id
                            next_id += 1

                        # Procesar todos los objetos trackeados
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
                            
                            # Escribir detección usando módulo de persistencia
                            if persistence_writer:
                                try:
                                    # Calcular timestamp en milisegundos
                                    timestamp_ms = int(frame_count * (1000 / cap.get(cv2.CAP_PROP_FPS)))
                                    
                                    detection = DetectionEvent(
                                        frame_number=frame_count,
                                        timestamp_ms=timestamp_ms,
                                        track_id=stable_id,
                                        class_name=class_name,
                                        confidence=conf,
                                        bbox_x1=x1,
                                        bbox_y1=y1,
                                        bbox_x2=x2,
                                        bbox_y2=y2,
                                        center_x=cx,
                                        center_y=cy
                                    )
                                    persistence_writer.write_detection(detection)
                                except Exception as e:
                                    print(f"[ERROR] No se pudo guardar detección: {e}")
                            
                            # Análisis de zonas si está habilitado
                            if enable_zones:
                                # Calcular timestamp en milisegundos
                                timestamp_ms = int(frame_count * (1000 / cap.get(cv2.CAP_PROP_FPS)))
                                
                                analizar_objeto_con_zonas(
                                    frame, box, stable_id, trayectorias,
                                    ids_en_zona, ids_cruzaron_linea,
                                    polygons, lines, class_name,
                                    frame_number=frame_count,
                                    timestamp_ms=timestamp_ms,
                                    persistence_writer=persistence_writer,
                                    zones_config=zones_config,
                                    conf=conf
                                )
                
            # Mostrar estadísticas en tiempo real
            stats_text = f"Frame: {frame_count} | Det: {objetos_detectados} | IDs: {len(unique_person_ids)}"
            cv2.putText(
                frame, stats_text,
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2
            )

            # Visualizar zonas si está habilitado
            if enable_zones:
                dibujar_zonas(frame, lines, polygons)

            # Escribir estadísticas del frame si está habilitado
            if enable_stats and stats_file:
                # Tracking siempre activo - todas las estadísticas disponibles
                en_zonas_valor = sum(len(zones) for zones in ids_en_zona.values()) if enable_zones else 0
                cruzaron_lineas_valor = len(ids_cruzaron_linea) if enable_zones else 0
                
                stats_file.write(f"{frame_count}\t{objetos_detectados}\t"
                               f"{ids_confirmados}\t{len(unique_person_ids)}\t"
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
    
    # Cerrar módulo de persistencia
    if persistence_writer:
        try:
            persistence_writer.close()
        except Exception as e:
            print(f"[ERROR] No se pudo cerrar persistencia: {e}")
    
    # Resumen final
    print(f"\n{'='*60}")
    print(f"🎯 ANÁLISIS DE VIDEO COMPLETADO")
    print(f"{'='*60}")
    
    if save_video:
        print(f"📹 Video guardado en: {output_path}")
    
    if enable_stats:
        print(f"📊 Estadísticas guardadas en: {stats_path}")
    
    if persistence_writer:
        summary = persistence_writer.get_summary()
        print(f"🗄️  Archivos CSV generados en: {summary['output_dir']}")
        print(f"   • frame_detections.csv (enfoque sin optimizar): {summary['detection_count']} registros")
        print(f"   • zone_events.csv (eventos de zona optimizados)")
        print(f"   • line_crossing_events.csv (cruces de línea optimizados)")
        print(f"   • minute_statistics.csv (estadísticas por minuto)")
        print(f"   • Total eventos optimizados: {summary['event_count']}")
    
    print(f"🎬 Total de frames procesados: {frame_count}")
    
    print(f"\n🔍 RESUMEN DE TRACKING:")
    print(f"   • IDs únicos confirmados: {len(unique_person_ids)}")
    print(f"   • Objetos detectados inicialmente: {len(id_map)}")
    print(f"   • Objetos confirmados (5+ frames): {len(unique_person_ids)}")
    
    if enable_zones:
        print(f"\n📍 RESUMEN DE ZONAS:")
        print(f"   • Objetos en zonas: {sum(len(zones) for zones in ids_en_zona.values())}")
        print(f"   • Objetos cruzando líneas: {len(ids_cruzaron_linea)}")
    
    print(f"{'='*60}")


def analizar_objeto_con_zonas(
    frame: np.ndarray,
    box: np.ndarray,
    track_id: int,
    trayectorias: Dict[int, List[Tuple[int, int]]],
    ids_en_zona: Dict[int, Set[str]],
    ids_cruzaron_linea: Set[int],
    polygons: List[List[Tuple[int, int]]],
    lines: List[List[Tuple[int, int]]],
    class_name: str = "objeto",
    # Parámetros adicionales para persistencia
    frame_number: int = 0,
    timestamp_ms: int = 0,
    persistence_writer = None,
    zones_config: List[Tuple] = None,
    conf: float = 0.0 # Added conf parameter
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

    # Detectar entrada y salida de zonas
    for i, poly in enumerate(polygons):
        is_in_zone = punto_en_poligono((cx, cy), poly)
        
        if is_in_zone:
            # ENTRADA a zona
            if track_id not in ids_en_zona:
                ids_en_zona[track_id] = set()  # Initialize if not exists
            ids_en_zona[track_id].add(f"polygon_{i+1}")
            print(f"[ALERTA] {class_name} ID {track_id} ha entrado en zona de interés.")
            
            # Guardar evento usando módulo de persistencia
            if persistence_writer and zones_config:
                for zone_id, zone_type, zone_coords in zones_config:
                    if zone_type == "polygon" and zone_coords == poly:
                        try:
                            zone_name = f"polygon_{zone_id.split('_')[-1]}"
                            persistence_writer.check_zone_event(
                                track_id=track_id,
                                zone_id=zone_id,
                                zone_name=zone_name,
                                is_in_zone=True,
                                frame_number=frame_number,
                                timestamp_ms=timestamp_ms,
                                position_x=cx,
                                position_y=cy,
                                class_name=class_name,
                                confidence=conf
                            )
                        except Exception as e:
                            print(f"[ERROR] No se pudo guardar evento: {e}")
                            
        elif not is_in_zone and track_id in ids_en_zona and f"polygon_{i+1}" in ids_en_zona[track_id]:
            # SALIDA de zona
            ids_en_zona[track_id].discard(f"polygon_{i+1}")
            print(f"[ALERTA] {class_name} ID {track_id} ha salido de zona de interés.")
            
            # Guardar evento usando módulo de persistencia
            if persistence_writer and zones_config:
                for zone_id, zone_type, zone_coords in zones_config:
                    if zone_type == "polygon" and zone_coords == poly:
                        try:
                            zone_name = f"polygon_{zone_id.split('_')[-1]}"
                            result = persistence_writer.check_zone_event(
                                track_id=track_id,
                                zone_id=zone_id,
                                zone_name=zone_name,
                                is_in_zone=False,  # SALIDA
                                frame_number=frame_number,
                                timestamp_ms=timestamp_ms,
                                position_x=cx,
                                position_y=cy,
                                class_name=class_name,
                                confidence=conf
                            )
                            if result:
                                print(f"[CSV] Evento de zona guardado: exit para track {track_id}")
                        except Exception as e:
                            print(f"[ERROR] Error al guardar evento de salida: {e}")

    # Detectar cruce de líneas
    if len(pts) > 1:
        for i, linea in enumerate(lines):
            if (cruza_linea(pts[-2], pts[-1], linea) and track_id not in ids_cruzaron_linea):
                ids_cruzaron_linea.add(track_id)
                print(f"[ALERTA] {class_name} ID {track_id} ha cruzado línea de interés.")
                
                # Guardar cruce usando módulo de persistencia
                if persistence_writer and zones_config:
                    for zone_id, zone_type, zone_coords in zones_config:
                        if zone_type == "line" and zone_coords == linea:
                            try:
                                # Determinar dirección del cruce
                                prev_x, prev_y = pts[-2]
                                direction = "left_to_right" if cx > prev_x else "right_to_left"
                                
                                line_name = f"line_{zone_id.split('_')[-1]}"
                                persistence_writer.check_line_crossing(
                                    track_id=track_id,
                                    line_id=zone_id,
                                    line_name=line_name,
                                    crossed_line=True,
                                    direction=direction,
                                    frame_number=frame_number,
                                    timestamp_ms=timestamp_ms,
                                    position_x=cx,
                                    position_y=cy,
                                    class_name=class_name,
                                    confidence=conf
                                )
                            except Exception as e:
                                print(f"[ERROR] No se pudo guardar cruce: {e}")


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
