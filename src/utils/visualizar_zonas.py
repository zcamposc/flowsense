#!/usr/bin/env python3
"""
Script para visualizar zonas y líneas configuradas.

Uso:
    python visualizar_zonas.py --image "imagen.png" --zones "zonas.json"
    python visualizar_zonas.py --video "video.mp4" --frame 5 --zones "zonas.json"
"""

import cv2
import json
import argparse
import os
import sys
import numpy as np
from pathlib import Path


def draw_zones_on_image(image_path, zonas, output_path=None):
    """Dibuja las zonas y líneas configuradas en la imagen."""
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"No se pudo cargar la imagen: {image_path}")
    
    # Crear una copia para dibujar
    img_with_zones = img.copy()
    
    # Dibujar líneas
    for i, line in enumerate(zonas.get("lines", [])):
        if len(line) == 2:
            # Dibujar línea
            cv2.line(img_with_zones, line[0], line[1], (0, 0, 255), 3)
            # Dibujar puntos
            cv2.circle(img_with_zones, line[0], 8, (0, 0, 255), -1)
            cv2.circle(img_with_zones, line[1], 8, (0, 0, 255), -1)
            # Agregar texto
            cv2.putText(img_with_zones, f"L{i+1}", 
                       (line[0][0] + 10, line[0][1] - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    
    # Dibujar polígonos
    for i, polygon in enumerate(zonas.get("polygons", [])):
        if len(polygon) >= 3:
            # Convertir a array de numpy
            polygon_array = np.array(polygon, dtype=np.int32)
            # Dibujar polígono
            cv2.polylines(img_with_zones, [polygon_array], True, (255, 0, 0), 3)
            # Dibujar puntos
            for pt in polygon:
                cv2.circle(img_with_zones, pt, 6, (255, 0, 0), -1)
            # Agregar texto (centro del polígono)
            center_x = sum(pt[0] for pt in polygon) // len(polygon)
            center_y = sum(pt[1] for pt in polygon) // len(polygon)
            cv2.putText(img_with_zones, f"Z{i+1}", 
                       (center_x - 20, center_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
    
    # Agregar leyenda
    legend_y = 30
    cv2.putText(img_with_zones, "LEYENDA:", (10, legend_y), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    legend_y += 25
    
    # Leyenda para líneas
    cv2.putText(img_with_zones, "L1, L2, ... = Lineas de cruce (ROJO)", 
               (10, legend_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    legend_y += 20
    
    # Leyenda para polígonos
    cv2.putText(img_with_zones, "Z1, Z2, ... = Zonas de interes (AZUL)", 
               (10, legend_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
    
    # Guardar imagen si se especifica output_path
    if output_path:
        cv2.imwrite(output_path, img_with_zones)
        print(f"📸 Imagen con zonas guardada: {output_path}")
    
    return img_with_zones


def extract_frame_from_video(video_path, frame_number=0):
    """Extrae un frame específico de un video."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"No se pudo abrir el video: {video_path}")
    
    # Obtener información del video
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = total_frames / fps if fps > 0 else 0
    
    print(f"📹 Video: {os.path.basename(video_path)}")
    print(f"   • Total frames: {total_frames}")
    print(f"   • FPS: {fps:.2f}")
    print(f"   • Duración: {duration:.2f} segundos")
    
    # Ir al frame especificado
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        raise ValueError(f"No se pudo leer el frame {frame_number}")
    
    # Generar nombre para el frame extraído
    video_name = Path(video_path).stem
    frame_path = f"{video_name}_frame_{frame_number:04d}.png"
    
    # Guardar el frame
    cv2.imwrite(frame_path, frame)
    print(f"📸 Frame extraído: {frame_path}")
    
    return frame_path


def load_zones(zones_file):
    """Carga la configuración de zonas desde un archivo JSON."""
    try:
        with open(zones_file, 'r', encoding='utf-8') as f:
            zonas = json.load(f)
        
        # Validar estructura
        if not isinstance(zonas, dict):
            raise ValueError("El archivo JSON debe contener un objeto")
        
        if "lines" not in zonas and "polygons" not in zonas:
            raise ValueError("El archivo debe contener 'lines' y/o 'polygons'")
        
        return zonas
    except FileNotFoundError:
        raise ValueError(f"No se encontró el archivo: {zones_file}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Error en el formato JSON: {e}")


def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(
        description="Visualizar zonas y líneas configuradas",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  # Visualizar zonas en imagen existente
  python visualizar_zonas.py --image "imagen.png" --zones "zonas.json"
  
  # Extraer frame de video y visualizar zonas
  python visualizar_zonas.py --video "video.mp4" --frame 5 --zones "zonas.json"
  
  # Guardar imagen con zonas dibujadas
  python visualizar_zonas.py --image "imagen.png" --zones "zonas.json" --output "zonas_visual.png"
  
  # Solo mostrar sin guardar
  python visualizar_zonas.py --image "imagen.png" --zones "zonas.json" --no-save
        """
    )
    
    # Argumentos de entrada
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--image", "-i",
        help="Ruta a la imagen de referencia"
    )
    input_group.add_argument(
        "--video", "-v",
        help="Ruta al video de referencia"
    )
    
    # Argumentos requeridos
    parser.add_argument(
        "--zones", "-z",
        required=True,
        help="Archivo JSON con configuración de zonas"
    )
    
    # Argumentos opcionales
    parser.add_argument(
        "--frame", "-f",
        type=int,
        default=0,
        help="Número de frame a extraer del video (por defecto: 0)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Archivo de salida para la imagen con zonas"
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="No guardar imagen, solo mostrar"
    )
    parser.add_argument(
        "--no-display",
        action="store_true",
        help="No mostrar ventana, solo guardar"
    )
    
    args = parser.parse_args()
    
    try:
        # Cargar configuración de zonas
        print(f"📁 Cargando configuración: {args.zones}")
        zonas = load_zones(args.zones)
        
        print(f"📊 Líneas configuradas: {len(zonas.get('lines', []))}")
        print(f"📊 Polígonos configurados: {len(zonas.get('polygons', []))}")
        
        # Determinar la imagen a usar
        if args.video:
            image_path = extract_frame_from_video(args.video, args.frame)
        else:
            image_path = args.image
            
        # Verificar que la imagen existe
        if not os.path.exists(image_path):
            print(f"❌ Error: La imagen no existe: {image_path}")
            sys.exit(1)
        
        print(f"🖼️  Usando imagen: {image_path}")
        print("=" * 50)
        
        # Dibujar zonas en la imagen
        img_with_zones = draw_zones_on_image(image_path, zonas, args.output)
        
        # Mostrar imagen si no se especifica --no-display
        if not args.no_display:
            cv2.imshow("Zonas y Líneas Configuradas", img_with_zones)
            print("\n👁️  VISUALIZACIÓN DE ZONAS")
            print("• Líneas ROJAS: Detección de cruces")
            print("• Polígonos AZULES: Zonas de interés")
            print("• Presiona cualquier tecla para cerrar...")
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        
        # Mostrar resumen
        print("\n" + "=" * 50)
        print("✅ VISUALIZACIÓN COMPLETADA")
        print("=" * 50)
        
        if zonas.get("lines"):
            print("\n📍 LÍNEAS CONFIGURADAS:")
            for i, line in enumerate(zonas["lines"], 1):
                print(f"   L{i}: {line[0]} → {line[1]}")
        
        if zonas.get("polygons"):
            print("\n📍 POLÍGONOS CONFIGURADOS:")
            for i, poly in enumerate(zonas["polygons"], 1):
                print(f"   Z{i}: {len(poly)} puntos")
        
        if args.output:
            print(f"\n📸 Imagen guardada: {args.output}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Visualización cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
