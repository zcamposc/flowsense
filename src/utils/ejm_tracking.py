#!/usr/bin/env python3
"""
Script de configuración interactiva de zonas y líneas de interés.

Uso:
    python ejm_tracking.py --image "imagen.png"
    python ejm_tracking.py --video "video.mp4" --frame 5
    python ejm_tracking.py --help
"""

import cv2
import json
import argparse
import os
import sys
from pathlib import Path


def draw_points(img, points, color=(0, 255, 0)):
    """Dibuja puntos y líneas en la imagen."""
    for pt in points:
        cv2.circle(img, pt, 5, color, -1)
    if len(points) > 1:
        cv2.polylines(img, [np.array(points)], False, color, 2)


def select_line(image_path):
    """Permite al usuario seleccionar una línea haciendo clic en 2 puntos."""
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"No se pudo cargar la imagen: {image_path}")
    
    clone = img.copy()
    points = []

    def click_event(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN and len(points) < 2:
            points.append((x, y))
            cv2.circle(img, (x, y), 5, (0, 0, 255), -1)
            if len(points) == 2:
                cv2.line(img, points[0], points[1], (0, 0, 255), 2)
            cv2.imshow("Selecciona 2 puntos para la línea", img)

    cv2.imshow("Selecciona 2 puntos para la línea", img)
    cv2.setMouseCallback("Selecciona 2 puntos para la línea", click_event)
    
    print("🔄 Selecciona 2 puntos para la línea:")
    print("   • Haz clic en el primer punto")
    print("   • Haz clic en el segundo punto")
    
    while len(points) < 2:
        cv2.waitKey(1)
    
    cv2.destroyAllWindows()
    print(f"✅ Línea configurada: {points[0]} → {points[1]}")
    return points


def select_polygon(image_path):
    """Permite al usuario seleccionar un polígono haciendo clic en múltiples puntos."""
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"No se pudo cargar la imagen: {image_path}")
    
    clone = img.copy()
    points = []

    def click_event(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            points.append((x, y))
            cv2.circle(img, (x, y), 5, (255, 0, 0), -1)
            if len(points) > 1:
                cv2.line(img, points[-2], points[-1], (255, 0, 0), 2)
            cv2.imshow("Haz clic para el polígono, Enter para terminar", img)

    cv2.imshow("Haz clic para el polígono, Enter para terminar", img)
    cv2.setMouseCallback("Haz clic para el polígono, Enter para terminar",
                         click_event)
    
    print("🔄 Selecciona puntos para el polígono:")
    print("   • Haz clic en múltiples puntos")
    print("   • Presiona ENTER cuando hayas terminado (mínimo 3 puntos)")
    
    while True:
        key = cv2.waitKey(1)
        if key == 13 and len(points) > 2:  # Enter
            break
        elif key == 27:  # ESC para cancelar
            cv2.destroyAllWindows()
            return None
    
    cv2.destroyAllWindows()
    print(f"✅ Polígono configurado con {len(points)} puntos")
    return points


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


def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(
        description="Configuración interactiva de zonas y líneas de interés",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  # Usar imagen existente
  python ejm_tracking.py --image "imagen.png"
  
  # Extraer frame de video y configurar zonas
  python ejm_tracking.py --video "video.mp4" --frame 10
  
  # Especificar archivo de salida
  python ejm_tracking.py --image "imagen.png" --output "mi_zonas.json"
  
  # Solo líneas (sin polígonos)
  python ejm_tracking.py --image "imagen.png" --lines-only
  
  # Solo polígonos (sin líneas)
  python ejm_tracking.py --image "imagen.png" --polygons-only
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
    
    # Argumentos opcionales
    parser.add_argument(
        "--frame", "-f",
        type=int,
        default=0,
        help="Número de frame a extraer del video (por defecto: 0)"
    )
    parser.add_argument(
        "--output", "-o",
        default="zonas.json",
        help="Archivo de salida JSON (por defecto: zonas.json)"
    )
    parser.add_argument(
        "--lines-only",
        action="store_true",
        help="Configurar solo líneas (sin polígonos)"
    )
    parser.add_argument(
        "--polygons-only",
        action="store_true",
        help="Configurar solo polígonos (sin líneas)"
    )
    parser.add_argument(
        "--config-dir",
        default="configs",
        help="Directorio para guardar la configuración (por defecto: configs)"
    )
    
    args = parser.parse_args()
    
    try:
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
        
        # Inicializar estructura de zonas
        zonas = {"lines": [], "polygons": []}
        
        # Configurar líneas
        if not args.polygons_only:
            print("\n🎯 CONFIGURACIÓN DE LÍNEAS")
            print("-" * 30)
            
            while True:
                try:
                    linea = select_line(image_path)
                    zonas["lines"].append(linea)
                    
                    # Preguntar si agregar más líneas
                    response = input("\n¿Agregar otra línea? (s/n): ").lower().strip()
                    if response not in ['s', 'si', 'y', 'yes']:
                        break
                except KeyboardInterrupt:
                    print("\n⚠️  Configuración de líneas cancelada")
                    break
        
        # Configurar polígonos
        if not args.lines_only:
            print("\n🎯 CONFIGURACIÓN DE POLÍGONOS")
            print("-" * 30)
            
            while True:
                try:
                    poligono = select_polygon(image_path)
                    if poligono is None:
                        print("⚠️  Polígono cancelado")
                        break
                    
                    zonas["polygons"].append(poligono)
                    
                    # Preguntar si agregar más polígonos
                    response = input("\n¿Agregar otro polígono? (s/n): ").lower().strip()
                    if response not in ['s', 'si', 'y', 'yes']:
                        break
                except KeyboardInterrupt:
                    print("\n⚠️  Configuración de polígonos cancelada")
                    break
        
        # Crear directorio de configuración si no existe
        config_dir = Path(args.config_dir)
        config_dir.mkdir(exist_ok=True)
        
        # Guardar configuración
        output_path = config_dir / args.output
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(zonas, f, indent=2, ensure_ascii=False)
        
        print("\n" + "=" * 50)
        print("🎉 CONFIGURACIÓN COMPLETADA")
        print("=" * 50)
        print(f"📁 Archivo guardado: {output_path}")
        print(f"📊 Líneas configuradas: {len(zonas['lines'])}")
        print(f"📊 Polígonos configurados: {len(zonas['polygons'])}")
        
        # Mostrar resumen de la configuración
        if zonas["lines"]:
            print("\n📍 LÍNEAS CONFIGURADAS:")
            for i, line in enumerate(zonas["lines"], 1):
                print(f"   {i}. {line[0]} → {line[1]}")
        
        if zonas["polygons"]:
            print("\n📍 POLÍGONOS CONFIGURADOS:")
            for i, poly in enumerate(zonas["polygons"], 1):
                print(f"   {i}. {len(poly)} puntos")
        
        print(f"\n🚀 Para usar esta configuración:")
        print(f"   uv run src/main.py process \\")
        print(f"       --video-path \"tu_video.mp4\" \\")
        print(f"       --model-path \"tu_modelo.pt\" \\")
        print(f"       --enable-zones \"{output_path}\"")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Configuración cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()