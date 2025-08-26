#!/usr/bin/env python3
"""
Script para verificar el FPS del video usando OpenCV.
"""

import cv2
import os
from datetime import datetime

def check_video_fps(video_path):
    """Verificar el FPS y propiedades del video."""
    try:
        # Abrir el video
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            print(f"❌ No se pudo abrir el video: {video_path}")
            return
        
        # Obtener propiedades del video
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = total_frames / fps if fps > 0 else 0
        
        print(f"📹 ANÁLISIS DEL VIDEO: {os.path.basename(video_path)}")
        print("=" * 50)
        print(f"🎬 FPS: {fps}")
        print(f"📊 Total de frames: {total_frames}")
        print(f"📐 Resolución: {width}x{height}")
        print(f"⏱️  Duración: {duration:.2f} segundos")
        
        # Verificar si el FPS es válido
        if fps <= 0:
            print(f"⚠️  PROBLEMA: FPS inválido ({fps})")
            print(f"   • Esto causará timestamps incorrectos")
            print(f"   • Los timestamps se calcularán como 0 o negativos")
        else:
            print(f"✅ FPS válido: {fps}")
            
            # Calcular algunos timestamps de ejemplo
            print(f"\n📅 EJEMPLOS DE TIMESTAMPS:")
            for frame in [1, 10, 100, 341]:
                if frame <= total_frames:
                    timestamp_ms = int(frame * (1000.0 / fps))
                    timestamp_sec = frame / fps
                    print(f"   • Frame {frame}: {timestamp_ms}ms ({timestamp_sec:.2f}s)")
        
        # Verificar fecha de procesamiento
        print(f"\n🕐 FECHA ACTUAL: {datetime.now()}")
        
        # Verificar si existe el archivo de salida más reciente
        output_dir = "outputs"
        if os.path.exists(output_dir):
            output_files = [f for f in os.listdir(output_dir) if f.endswith('.mp4')]
            if output_files:
                # Obtener el archivo más reciente
                latest_file = max(output_files, key=lambda x: os.path.getctime(os.path.join(output_dir, x)))
                latest_path = os.path.join(output_dir, latest_file)
                ctime = os.path.getctime(latest_path)
                ctime_str = datetime.fromtimestamp(ctime)
                print(f"📁 Último archivo procesado: {latest_file}")
                print(f"   • Fecha de creación: {ctime_str}")
        
        cap.release()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    video_path = "data/videos/video_2.mp4"
    check_video_fps(video_path)
