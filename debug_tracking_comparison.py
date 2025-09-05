#!/usr/bin/env python3
"""
Compara el tracking de YOLO en los frames 1045-1052:
1. Procesando desde el inicio (como script principal)
2. Saltando directamente a frame 1045 (como debug)
"""

import cv2
import json
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict, Set
import sys
import os
from ultralytics import YOLO
from collections import defaultdict, deque

# Agregar src al path para importar módulos
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils.geometry import cruza_linea, determinar_direccion_cruce
from utils.file_manager import cargar_zonas_desde_json, cargar_nombres_zonas
from utils.coco_classes import validate_classes, get_class_name

def comparar_tracking():
    """Compara tracking completo vs salto directo."""
    
    # Configuración
    video_path = "data/videos/DosR_Crop_5x (online-video-cutter.com)-2.mp4"
    config_path = "configs/lineas_entrada_principal_20250905_074615/zonas.json"  
    model_path = "models/yolov8l.pt"
    classes = ["person"]
    
    # Frames objetivo
    target_start = 1045
    target_end = 1052
    
    # Cargar modelo y configuración
    print("🔄 Cargando modelo YOLO...")
    model = YOLO(model_path)
    
    # Cargar zonas
    lines, polygons = cargar_zonas_desde_json(config_path)
    zone_names = cargar_nombres_zonas(config_path)
    
    # Configurar clases
    class_ids = validate_classes(classes)
    
    print("=" * 100)
    print("🔍 COMPARACIÓN DE TRACKING - FRAMES 1045-1052")
    print("=" * 100)
    print(f"📹 Video: {video_path}")
    print(f"🎯 Frames objetivo: {target_start} - {target_end}")
    
    # ===== MÉTODO 1: PROCESAMIENTO COMPLETO (como script principal) =====
    print(f"\n🚀 MÉTODO 1: PROCESAMIENTO COMPLETO (desde frame 0)")
    print("=" * 80)
    
    cap1 = cv2.VideoCapture(video_path)
    if not cap1.isOpened():
        raise FileNotFoundError(f"No se pudo abrir el video: {video_path}")
    
    # Variables para método completo
    id_map_completo = {}
    next_id_completo = 1
    trayectorias_completo: Dict[int, List[Tuple[int, int]]] = {}
    
    print(f"📊 Procesando {target_start} frames hasta llegar al objetivo...")
    
    # Procesar frames desde 0 hasta target_start
    for frame_num in range(target_start + (target_end - target_start + 1)):
        ret, frame = cap1.read()
        if not ret:
            break
            
        # Solo mostrar progreso cada 200 frames
        if frame_num % 200 == 0:
            print(f"   Frame {frame_num}...")
        
        # Tracking completo
        track_params = {'persist': True, 'verbose': False}
        results = model.track(frame, **track_params)
        
        # Procesar solo en el rango objetivo
        if target_start <= frame_num <= target_end:
            if results[0].boxes.id is not None:
                boxes = results[0].boxes.xyxy.cpu().numpy()
                track_ids = results[0].boxes.id.int().cpu().numpy()
                confidences = results[0].boxes.conf.cpu().numpy()
                detected_classes = results[0].boxes.cls.cpu().numpy()
                
                for box, oid, conf, cls in zip(boxes, track_ids, confidences, detected_classes):
                    if class_ids is None or int(cls) in class_ids:
                        x1, y1, x2, y2 = map(int, box)
                        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                        class_name = get_class_name(int(cls))
                        
                        # Asignar ID permanente
                        if oid not in id_map_completo:
                            id_map_completo[oid] = next_id_completo
                            next_id_completo += 1
                        
                        stable_id = id_map_completo[oid]
                        
                        # Actualizar trayectoria
                        if stable_id not in trayectorias_completo:
                            trayectorias_completo[stable_id] = []
                        trayectorias_completo[stable_id].append((cx, cy))
                        
                        if frame_num == target_start:  # Solo mostrar en el primer frame objetivo
                            print(f"   🎯 Frame {frame_num}: YOLO Track {oid} → ID estable {stable_id}, center=({cx},{cy})")
    
    cap1.release()
    
    # ===== MÉTODO 2: SALTO DIRECTO (como script debug) =====
    print(f"\n🚀 MÉTODO 2: SALTO DIRECTO (desde frame {target_start})")
    print("=" * 80)
    
    cap2 = cv2.VideoCapture(video_path)
    cap2.set(cv2.CAP_PROP_POS_FRAMES, target_start - 1)
    
    # Variables para método directo
    id_map_directo = {}
    next_id_directo = 1
    trayectorias_directo: Dict[int, List[Tuple[int, int]]] = {}
    
    for frame_num in range(target_start, target_end + 1):
        ret, frame = cap2.read()
        if not ret:
            break
        
        # Tracking directo (YOLO se reinicia)
        track_params = {'persist': True, 'verbose': False}
        results = model.track(frame, **track_params)
        
        if results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            track_ids = results[0].boxes.id.int().cpu().numpy()
            confidences = results[0].boxes.conf.cpu().numpy()
            detected_classes = results[0].boxes.cls.cpu().numpy()
            
            for box, oid, conf, cls in zip(boxes, track_ids, confidences, detected_classes):
                if class_ids is None or int(cls) in class_ids:
                    x1, y1, x2, y2 = map(int, box)
                    cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                    class_name = get_class_name(int(cls))
                    
                    # Asignar ID permanente
                    if oid not in id_map_directo:
                        id_map_directo[oid] = next_id_directo
                        next_id_directo += 1
                    
                    stable_id = id_map_directo[oid]
                    
                    # Actualizar trayectoria
                    if stable_id not in trayectorias_directo:
                        trayectorias_directo[stable_id] = []
                    trayectorias_directo[stable_id].append((cx, cy))
                    
                    if frame_num == target_start:  # Solo mostrar en el primer frame
                        print(f"   🎯 Frame {frame_num}: YOLO Track {oid} → ID estable {stable_id}, center=({cx},{cy})")
    
    cap2.release()
    
    # ===== COMPARACIÓN =====
    print(f"\n" + "=" * 100)
    print("📊 COMPARACIÓN DE RESULTADOS")
    print("=" * 100)
    
    print(f"🔄 MÉTODO COMPLETO:")
    print(f"   Total tracks detectados: {len(trayectorias_completo)}")
    for track_id, pts in trayectorias_completo.items():
        print(f"   Track {track_id}: {len(pts)} puntos - primeros: {pts[:2]}, últimos: {pts[-2:]}")
    
    print(f"\n🏃 MÉTODO DIRECTO:")
    print(f"   Total tracks detectados: {len(trayectorias_directo)}")
    for track_id, pts in trayectorias_directo.items():
        print(f"   Track {track_id}: {len(pts)} puntos - primeros: {pts[:2]}, últimos: {pts[-2:]}")
    
    # Análisis de cruces para ambos métodos
    linea = lines[0] if lines else None
    if linea:
        print(f"\n🚨 ANÁLISIS DE CRUCES:")
        print(f"📐 Línea: {linea}")
        
        # Cruces método completo
        cruces_completo = []
        ids_cruzaron_completo = set()
        
        for track_id, pts in trayectorias_completo.items():
            for i in range(1, len(pts)):
                if track_id not in ids_cruzaron_completo:
                    prev_pos = pts[i-1]
                    current_pos = pts[i]
                    
                    if cruza_linea(prev_pos, current_pos, linea):
                        direction = determinar_direccion_cruce(prev_pos, current_pos, linea)
                        cruces_completo.append((track_id, direction, prev_pos, current_pos))
                        ids_cruzaron_completo.add(track_id)
                        break
        
        # Cruces método directo
        cruces_directo = []
        ids_cruzaron_directo = set()
        
        for track_id, pts in trayectorias_directo.items():
            for i in range(1, len(pts)):
                if track_id not in ids_cruzaron_directo:
                    prev_pos = pts[i-1]
                    current_pos = pts[i]
                    
                    if cruza_linea(prev_pos, current_pos, linea):
                        direction = determinar_direccion_cruce(prev_pos, current_pos, linea)
                        cruces_directo.append((track_id, direction, prev_pos, current_pos))
                        ids_cruzaron_directo.add(track_id)
                        break
        
        print(f"\n🔄 CRUCES MÉTODO COMPLETO: {len(cruces_completo)}")
        for track_id, direction, prev, curr in cruces_completo:
            print(f"   Track {track_id}: {direction} - {prev} → {curr}")
        
        print(f"\n🏃 CRUCES MÉTODO DIRECTO: {len(cruces_directo)}")
        for track_id, direction, prev, curr in cruces_directo:
            print(f"   Track {track_id}: {direction} - {prev} → {curr}")
        
        print(f"\n🎯 DIAGNÓSTICO:")
        if len(cruces_completo) != len(cruces_directo):
            print("   ❌ DIFERENCIA EN DETECCIÓN DE CRUCES")
            print("   🔧 CAUSA: Tracking de YOLO asigna IDs diferentes")
            print("   💡 SOLUCIÓN: El script principal debe procesar el video completo")
        else:
            print("   ✅ Ambos métodos detectan la misma cantidad de cruces")

if __name__ == "__main__":
    comparar_tracking()
