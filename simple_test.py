#!/usr/bin/env python3
"""
Script simple para probar la diferencia entre ambos métodos de tracking
"""

from ultralytics import YOLO
import cv2

def main():
    print("🔍 COMPARACIÓN SIMPLE DE MÉTODOS")
    print("=" * 40)
    
    # Cargar modelo
    model = YOLO("models/yolov8n.pt")
    
    # Cargar video
    cap = cv2.VideoCapture("data/videos/video_2.mp4")
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print("❌ No se pudo leer el frame")
        return
    
    print("📊 Probando Frame 1...")
    print()
    
    # Método 1: sript_test.py
    print("1️⃣ Método sript_test.py:")
    results1 = model.track(frame, persist=True, classes=[0], verbose=False)
    
    if results1[0].boxes.id is not None:
        boxes1 = results1[0].boxes.xyxy.numpy()
        print(f"   Detecciones: {len(boxes1)}")
        print(f"   IDs únicos: {len(set(results1[0].boxes.id.numpy()))}")
    else:
        print("   No se detectaron objetos")
    
    print()
    
    # Método 2: src/tracking.py
    print("2️⃣ Método src/tracking.py:")
    results2 = model.track(
        frame, 
        persist=True, 
        classes=[0],  # Usar [0] directamente como sript_test.py
        conf=0.5,     # Usar 0.5 explícitamente
        verbose=False
    )
    
    if results2[0].boxes.id is not None:
        boxes2 = results2[0].boxes.xyxy.cpu().numpy()
        print(f"   Detecciones: {len(boxes2)}")
        print(f"   IDs únicos: {len(set(results2[0].boxes.id.int().cpu().numpy()))}")
    else:
        print("   No se detectaron objetos")
    
    print()
    
    # Comparar
    if results1[0].boxes.id is not None and results2[0].boxes.id is not None:
        det1 = len(boxes1)
        det2 = len(boxes2)
        
        print("📈 COMPARACIÓN:")
        print(f"   sript_test.py: {det1} detecciones")
        print(f"   src/tracking.py: {det2} detecciones")
        print(f"   Diferencia: {det1 - det2}")
        
        if det1 == det2:
            print("   ✅ ¡MISMOS RESULTADOS!")
        else:
            print("   ❌ RESULTADOS DIFERENTES")
            
            # Verificar si es por el parámetro conf
            print("\n🔍 Probando sin parámetro conf...")
            results3 = model.track(frame, persist=True, classes=[0], verbose=False)
            
            if results3[0].boxes.id is not None:
                det3 = len(results3[0].boxes.xyxy.numpy())
                print(f"   Sin conf: {det3} detecciones")
                
                if det3 == det1:
                    print("   ✅ El parámetro conf=0.5 es la causa")
                else:
                    print("   ❌ Hay otra causa diferente")

if __name__ == "__main__":
    main()
