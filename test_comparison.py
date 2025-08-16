#!/usr/bin/env python3
"""
Script para comparar directamente los resultados de tracking entre
sript_test.py y src/tracking.py para identificar las diferencias.
"""

import cv2
from ultralytics import YOLO
import numpy as np
from collections import defaultdict, deque


def test_sript_test_method():
    """
    Implementa exactamente la misma lógica que sript_test.py
    """
    print("🧪 Probando método de sript_test.py...")
    
    model = YOLO("models/yolov8n.pt")
    cap = cv2.VideoCapture("data/videos/video_2.mp4")
    
    # Variables de tracking (igual que sript_test.py)
    id_map = {}
    next_id = 1
    trail = defaultdict(lambda: deque(maxlen=30))
    appear = defaultdict(int)
    frame_count = 0
    
    # Contadores para este frame
    total_detections = 0
    confirmed_objects = 0
    
    # Leer solo el primer frame para comparar
    ret, frame = cap.read()
    if not ret:
        print("❌ No se pudo leer el frame")
        return
    
    frame_count += 1
    
    # Ejecutar YOLO tracking (EXACTAMENTE igual que sript_test.py)
    results = model.track(frame, persist=True, classes=[0], verbose=False)
    
    if results[0].boxes.id is not None:
        boxes = results[0].boxes.xyxy.numpy()
        ids = results[0].boxes.id.numpy()
        
        total_detections = len(boxes)
        print(f"  📊 Frame {frame_count}: {total_detections} detecciones totales")
        
        for box, oid in zip(boxes, ids):
            appear[oid] += 1
            
            if appear[oid] >= 5 and oid not in id_map:
                id_map[oid] = next_id
                next_id += 1
            
            if oid in id_map:
                confirmed_objects += 1
        
        print(f"  ✅ Objetos confirmados: {confirmed_objects}")
        print(f"  🆔 IDs únicos: {len(id_map)}")
    
    cap.release()
    return total_detections, confirmed_objects, len(id_map)


def test_src_tracking_method():
    """
    Implementa la lógica de src/tracking.py
    """
    print("🔧 Probando método de src/tracking.py...")
    
    model = YOLO("models/yolov8n.pt")
    cap = cv2.VideoCapture("data/videos/video_2.mp4")
    
    # Variables de tracking (igual que src/tracking.py)
    id_map = {}
    next_id = 1
    trail = defaultdict(lambda: deque(maxlen=30))
    appear = defaultdict(int)
    frame_count = 0
    
    # Contadores para este frame
    objetos_detectados = 0
    ids_confirmados = 0
    
    # Leer solo el primer frame para comparar
    ret, frame = cap.read()
    if not ret:
        print("❌ No se pudo leer el frame")
        return
    
    frame_count += 1
    
    # Configurar clases (igual que src/tracking.py)
    classes = ["person"]
    if classes is not None:
        class_ids = [model.names.index(c) for c in classes]
    else:
        class_ids = [0]
    
    # Ejecutar YOLO tracking (igual que src/tracking.py)
    results = model.track(
        frame, 
        persist=True, 
        classes=class_ids, 
        conf=0.5,  # Usar 0.5 como en sript_test.py
        verbose=False
    )
    
    if results[0].boxes.id is not None:
        boxes = results[0].boxes.xyxy.cpu().numpy()
        track_ids = results[0].boxes.id.int().cpu().numpy()
        confidences = results[0].boxes.conf.cpu().numpy()
        detected_classes = results[0].boxes.cls.cpu().numpy()
        
        objetos_detectados = len(boxes)
        print(f"  📊 Frame {frame_count}: {objetos_detectados} objetos detectados")
        
        for box, oid, conf, cls in zip(boxes, track_ids, confidences, detected_classes):
            appear[oid] += 1
            
            if appear[oid] >= 5 and oid not in id_map:
                id_map[oid] = next_id
                next_id += 1
            
            if oid in id_map:
                ids_confirmados += 1
        
        print(f"  ✅ IDs confirmados: {ids_confirmados}")
        print(f"  🆔 IDs únicos: {len(id_map)}")
    
    cap.release()
    return objetos_detectados, ids_confirmados, len(id_map)


def main():
    """
    Función principal que compara ambos métodos
    """
    print("🔍 COMPARACIÓN DE MÉTODOS DE TRACKING")
    print("=" * 50)
    print()
    
    # Probar método de sript_test.py
    result1 = test_sript_test_method()
    print()
    
    # Probar método de src/tracking.py
    result2 = test_src_tracking_method()
    print()
    
    # Comparar resultados
    print("📊 COMPARACIÓN DE RESULTADOS")
    print("=" * 50)
    
    if result1 and result2:
        det1, conf1, ids1 = result1
        det2, conf2, ids2 = result2
        
        print(f"Frame 1 - sript_test.py:")
        print(f"  Detecciones: {det1}")
        print(f"  Confirmados: {conf1}")
        print(f"  IDs únicos: {ids1}")
        print()
        
        print(f"Frame 1 - src/tracking.py:")
        print(f"  Detecciones: {det2}")
        print(f"  Confirmados: {conf2}")
        print(f"  IDs únicos: {ids2}")
        print()
        
        print(f"Diferencias:")
        print(f"  Detecciones: {det1} vs {det2} (diff: {det1 - det2})")
        print(f"  Confirmados: {conf1} vs {conf2} (diff: {conf1 - conf2})")
        print(f"  IDs únicos: {ids1} vs {ids2} (diff: {ids1 - ids2})")
        
        if det1 == det2 and conf1 == conf2 and ids1 == ids2:
            print("\n✅ ¡Los métodos producen resultados IDÉNTICOS!")
        else:
            print("\n❌ Los métodos producen resultados DIFERENTES")
            print("   Esto explica las diferencias en los archivos de estadísticas")


if __name__ == "__main__":
    main()
