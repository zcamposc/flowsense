#!/usr/bin/env python3
"""
Herramienta de debugging para analizar cruces de línea problemáticos.
Permite extraer frames específicos y analizar la detección paso a paso.
Muestra cada frame del rango con detecciones YOLO y puntos de cruce.
"""

import cv2
import json
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict
import sys
import os
from ultralytics import YOLO

# Agregar src al path para importar módulos
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils.geometry import cruza_linea, determinar_direccion_cruce, calcular_distancia_punto_a_linea, determinar_lado_del_punto
from utils.file_manager import cargar_zonas_desde_json
from utils.coco_classes import COCO_CLASSES

def extract_frame_from_video(video_path: str, frame_number: int) -> np.ndarray:
    """Extrae un frame específico del video."""
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise ValueError(f"No se pudo abrir el video: {video_path}")
    
    # Ir al frame específico
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = cap.read()
    
    if not ret:
        raise ValueError(f"No se pudo leer el frame {frame_number}")
    
    cap.release()
    return frame

def analyze_line_geometry(line_coords: List[Tuple[int, int]]) -> Dict:
    """Analiza las características geométricas de una línea."""
    p1, p2 = line_coords
    x1, y1 = p1
    x2, y2 = p2
    
    # Calcular vector de la línea
    dx = x2 - x1
    dy = y2 - y1
    
    # Calcular ángulo
    angle_rad = np.arctan2(dy, dx)
    angle_deg = np.degrees(angle_rad)
    
    # Longitud
    length = np.sqrt(dx**2 + dy**2)
    
    # Determinar orientación
    if abs(dx) < 10:  # Línea casi vertical
        orientation = "vertical"
    elif abs(dy) < 10:  # Línea casi horizontal
        orientation = "horizontal"
    else:
        orientation = "diagonal"
    
    return {
        "start": p1,
        "end": p2,
        "vector": (dx, dy),
        "angle_degrees": angle_deg,
        "length": length,
        "orientation": orientation
    }

def simulate_crossing_detection(
    line_coords: List[Tuple[int, int]], 
    trajectory_points: List[Tuple[int, int]]
) -> List[Dict]:
    """Simula la detección de cruces para una trayectoria."""
    results = []
    
    for i in range(1, len(trajectory_points)):
        p1 = trajectory_points[i-1]
        p2 = trajectory_points[i]
        
        # Detectar cruce
        crosses = cruza_linea(p1, p2, line_coords)
        
        # Calcular dirección usando método actual
        prev_x, prev_y = p1
        curr_x, curr_y = p2
        direction_simple = "left_to_right" if curr_x > prev_x else "right_to_left"
        
        # Calcular dirección usando producto cruz (método mejorado)
        line_start, line_end = line_coords
        line_vector = (line_end[0] - line_start[0], line_end[1] - line_start[1])
        movement_vector = (curr_x - prev_x, curr_y - prev_y)
        
        cross_product = line_vector[0] * movement_vector[1] - line_vector[1] * movement_vector[0]
        direction_improved = "left_to_right" if cross_product > 0 else "right_to_left"
        
        results.append({
            "segment": i,
            "from": p1,
            "to": p2,
            "crosses": crosses,
            "direction_simple": direction_simple,
            "direction_improved": direction_improved,
            "cross_product": cross_product,
            "movement_vector": movement_vector
        })
    
    return results

def run_yolo_detection(model, frame: np.ndarray, conf_threshold: float = 0.5) -> List[Dict]:
    """Ejecuta detección YOLO en un frame y retorna las detecciones de personas."""
    results = model(frame, conf=conf_threshold, verbose=False)
    detections = []
    
    for result in results:
        boxes = result.boxes
        if boxes is not None:
            for i in range(len(boxes)):
                # Obtener datos de la detección
                box = boxes.xyxy[i].cpu().numpy()
                conf = float(boxes.conf[i].cpu().numpy())
                cls = int(boxes.cls[i].cpu().numpy())
                
                # Solo procesar personas (clase 0 en COCO)
                if cls == 0:  # person
                    x1, y1, x2, y2 = box
                    cx = int((x1 + x2) / 2)
                    cy = int((y1 + y2) / 2)
                    
                    detections.append({
                        'bbox': (int(x1), int(y1), int(x2), int(y2)),
                        'center': (cx, cy),
                        'confidence': conf,
                        'class_name': 'person'
                    })
    
    return detections

def visualize_frame_with_detections(
    frame: np.ndarray,
    line_coords: List[Tuple[int, int]],
    detections: List[Dict],
    frame_number: int,
    crossing_analysis: Dict = None
) -> np.ndarray:
    """Visualiza el frame con detecciones YOLO y análisis de cruces."""
    vis_frame = frame.copy()
    
    # Dibujar línea roja
    cv2.line(vis_frame, line_coords[0], line_coords[1], (0, 0, 255), 4)
    
    # Dibujar detecciones
    for i, detection in enumerate(detections):
        bbox = detection['bbox']
        center = detection['center']
        conf = detection['confidence']
        
        # Dibujar bounding box verde
        cv2.rectangle(vis_frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
        
        # Dibujar punto central azul
        cv2.circle(vis_frame, center, 6, (255, 0, 0), -1)
        
        # Calcular distancia a la línea
        distance = calcular_distancia_punto_a_linea(center, line_coords)
        side = determinar_lado_del_punto(center, line_coords)
        
        # Etiqueta con confianza y información
        label = f"ID:{i+1} {conf:.2f}"
        label_pos = (bbox[0], bbox[1] - 10)
        cv2.putText(vis_frame, label, label_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Información adicional debajo del bbox
        info_label = f"d={distance:.1f}px {side}"
        info_pos = (bbox[0], bbox[3] + 20)
        cv2.putText(vis_frame, info_label, info_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # Título del frame
    title = f"Frame {frame_number} - {len(detections)} detecciones"
    cv2.putText(vis_frame, title, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    # Información de análisis de cruces si está disponible
    if crossing_analysis:
        y_offset = 60
        for track_id, analysis in crossing_analysis.items():
            crossing_text = f"Track {track_id}: {analysis['status']}"
            if analysis.get('direction'):
                crossing_text += f" ({analysis['direction']})"
            cv2.putText(vis_frame, crossing_text, (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            y_offset += 25
    
    return vis_frame

def analyze_frame_range_with_detections():
    """Analiza un rango completo de frames con detecciones YOLO."""
    
    # Configuración
    video_path = "data/videos/DosR_Crop_5x (online-video-cutter.com)-2.mp4"
    config_path = "configs/lineas_entrada_principal_20250905_074615/zonas.json"
    model_path = "models/yolov8l.pt"
    conf_threshold = 0.5
    
    # Cargar modelo YOLO
    print("🔄 Cargando modelo YOLO...")
    model = YOLO(model_path)
    
    # Cargar configuración
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    line_coords = config["lines"][0]["coordinates"]
    line_name = config["lines"][0]["name"]
    
    print("=" * 80)
    print("🔍 ANÁLISIS DETALLADO DE FRAMES CON DETECCIONES")
    print("=" * 80)
    
    # Analizar geometría de la línea
    line_analysis = analyze_line_geometry(line_coords)
    print(f"\n📐 LÍNEA '{line_name}':")
    print(f"   • Coordenadas: {line_coords[0]} → {line_coords[1]}") 
    print(f"   • Ángulo: {line_analysis['angle_degrees']:.1f}°")
    print(f"   • Orientación: {line_analysis['orientation']}")
    
    # Escenarios a analizar
    scenarios = [
        {"name": "Escenario_1", "start": 527, "end": 534, "description": "2 entradas esperadas"},
        {"name": "Escenario_2", "start": 1045, "end": 1052, "description": "1 salida esperada"},
        {"name": "Escenario_3", "start": 1910, "end": 1930, "description": "2 entradas esperadas"}
    ]
    
    # Crear directorio para screenshots
    screenshots_dir = Path("debug_screenshots_detailed")
    screenshots_dir.mkdir(exist_ok=True)
    
    # Analizar cada escenario
    for scenario in scenarios[:1]:  # Empezar con el primer escenario
        print(f"\n🎯 ANALIZANDO {scenario['name']}: {scenario['description']}")
        print(f"   Frames {scenario['start']} - {scenario['end']}")
        
        # Crear subdirectorio para este escenario
        scenario_dir = screenshots_dir / scenario['name']
        scenario_dir.mkdir(exist_ok=True)
        
        # Simular tracking simple (asignar IDs basado en proximidad)
        track_history = {}
        next_track_id = 1
        
        # Analizar cada frame en el rango
        for frame_num in range(scenario['start'], scenario['end'] + 1):
            try:
                print(f"   📸 Procesando frame {frame_num}...")
                
                # Extraer frame
                frame = extract_frame_from_video(video_path, frame_num)
                
                # Ejecutar detección YOLO
                detections = run_yolo_detection(model, frame, conf_threshold)
                
                # Simular tracking simple (asignar IDs)
                current_tracks = assign_simple_track_ids(detections, track_history)
                
                # Analizar cruces potenciales
                crossing_analysis = analyze_potential_crossings(
                    current_tracks, track_history, line_coords, frame_num
                )
                
                # Actualizar historial de tracking
                update_track_history(track_history, current_tracks, frame_num)
                
                # Crear visualización
                vis_frame = visualize_frame_with_detections(
                    frame, line_coords, current_tracks, frame_num, crossing_analysis
                )
                
                # Guardar imagen
                output_path = scenario_dir / f"frame_{frame_num:04d}.png"
                cv2.imwrite(str(output_path), vis_frame)
                
                # Imprimir resumen del frame
                print(f"      • {len(detections)} detecciones encontradas")
                if crossing_analysis:
                    for track_id, analysis in crossing_analysis.items():
                        print(f"      • Track {track_id}: {analysis['status']}")
                
            except Exception as e:
                print(f"   ❌ Error en frame {frame_num}: {e}")
        
        print(f"   ✅ {scenario['name']} completado. Imágenes en {scenario_dir}")
    
    print(f"\n🎉 ANÁLISIS COMPLETADO")
    print(f"📁 Revisa las imágenes en: {screenshots_dir}")

def assign_simple_track_ids(detections: List[Dict], track_history: Dict) -> List[Dict]:
    """Asigna IDs de tracking simple basado en proximidad."""
    if not track_history:
        # Primer frame: asignar IDs secuenciales
        for i, detection in enumerate(detections):
            detection['track_id'] = i + 1
        return detections
    
    # Frames posteriores: asignar basado en proximidad
    assigned_tracks = []
    used_ids = set()
    
    for detection in detections:
        best_match_id = None
        min_distance = float('inf')
        
        # Buscar el track más cercano
        for track_id, history in track_history.items():
            if track_id in used_ids:
                continue
                
            if history['positions']:
                last_pos = history['positions'][-1]
                current_pos = detection['center']
                
                distance = np.sqrt(
                    (current_pos[0] - last_pos[0])**2 + 
                    (current_pos[1] - last_pos[1])**2
                )
                
                if distance < min_distance and distance < 200:  # Umbral de proximidad
                    min_distance = distance
                    best_match_id = track_id
        
        if best_match_id:
            detection['track_id'] = best_match_id
            used_ids.add(best_match_id)
        else:
            # Nuevo track
            new_id = max(track_history.keys(), default=0) + 1
            detection['track_id'] = new_id
        
        assigned_tracks.append(detection)
    
    return assigned_tracks

def update_track_history(track_history: Dict, current_tracks: List[Dict], frame_num: int):
    """Actualiza el historial de tracking."""
    for track in current_tracks:
        track_id = track['track_id']
        
        if track_id not in track_history:
            track_history[track_id] = {
                'positions': [],
                'confidences': [],
                'frames': [],
                'first_frame': frame_num
            }
        
        track_history[track_id]['positions'].append(track['center'])
        track_history[track_id]['confidences'].append(track['confidence'])
        track_history[track_id]['frames'].append(frame_num)

def analyze_potential_crossings(
    current_tracks: List[Dict], 
    track_history: Dict, 
    line_coords: List[Tuple[int, int]], 
    frame_num: int
) -> Dict:
    """Analiza cruces potenciales para los tracks actuales."""
    crossing_analysis = {}
    
    for track in current_tracks:
        track_id = track['track_id']
        current_pos = track['center']
        
        if track_id in track_history:
            positions = track_history[track_id]['positions']
            
            # Análisis de cruce normal (si hay historial)
            if len(positions) >= 1:  # Al menos una posición previa
                prev_pos = positions[-1]
                
                # Verificar cruce
                crosses = cruza_linea(prev_pos, current_pos, line_coords)
                
                if crosses:
                    direction = determinar_direccion_cruce(prev_pos, current_pos, line_coords)
                    crossing_analysis[track_id] = {
                        'status': 'CRUCE DETECTADO',
                        'direction': direction,
                        'type': 'normal',
                        'frame': frame_num
                    }
                else:
                    # Verificar si es aparición súbita cerca de línea
                    if len(positions) == 1:  # Primera aparición
                        distance = calcular_distancia_punto_a_linea(current_pos, line_coords)
                        side = determinar_lado_del_punto(current_pos, line_coords)
                        
                        if distance < 150:  # Cerca de la línea
                            crossing_analysis[track_id] = {
                                'status': 'APARICIÓN SÚBITA',
                                'side': side,
                                'distance': distance,
                                'type': 'sudden',
                                'frame': frame_num
                            }
                        else:
                            crossing_analysis[track_id] = {
                                'status': 'NORMAL',
                                'distance': distance,
                                'type': 'normal'
                            }
                    else:
                        crossing_analysis[track_id] = {
                            'status': 'SIN CRUCE',
                            'type': 'normal'
                        }
        else:
            # Nuevo track
            distance = calcular_distancia_punto_a_linea(current_pos, line_coords)
            crossing_analysis[track_id] = {
                'status': 'NUEVO TRACK',
                'distance': distance,
                'type': 'new'
            }
    
    return crossing_analysis

if __name__ == "__main__":
    analyze_frame_range_with_detections()