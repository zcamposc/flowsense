#!/usr/bin/env python3
"""
Herramienta Interactiva de Configuración de Zonas de Interés

Esta herramienta permite configurar zonas de análisis para el sistema de detección de video:
- Líneas de cruce: Para detectar movimiento direccional
- Polígonos de área: Para detectar entrada/salida de zonas específicas

Uso básico:
    uv run src/utils/configurar_zonas.py --lines --video "data/videos/video.mp4" --frame 5
    uv run src/utils/configurar_zonas.py --polygons --video "data/videos/video.mp4" --frame 10
    uv run src/utils/configurar_zonas.py --lines --polygons --video "data/videos/video.mp4"

Controles interactivos:
    LÍNEAS:
        - Clic izquierdo: Marcar puntos de la línea (mínimo 2)
        - Clic derecho: Finalizar línea actual
        - Tecla 'n': Nueva línea
        - Tecla 's': Guardar configuración
        - Tecla 'q': Salir sin guardar
    
    POLÍGONOS:
        - Clic izquierdo: Marcar vértices del polígono (mínimo 3)
        - Clic derecho: Cerrar polígono actual
        - Tecla 'n': Nuevo polígono
        - Tecla 's': Guardar configuración
        - Tecla 'q': Salir sin guardar

Organización automática:
    Las configuraciones se guardan en directorios con timestamp:
    configs/lineas_descripcion_20250825_143022/
    ├── zonas.json          # Configuración de zonas
    ├── zonas_visual.png    # Imagen con zonas dibujadas
    └── frame_original.png  # Frame de referencia original
"""

import cv2
import json
import argparse
import os
import sys
import numpy as np
from pathlib import Path
from datetime import datetime


def draw_zones_on_image(image_path, zonas, output_path=None):
    """Dibuja las zonas y líneas configuradas en la imagen."""
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"No se pudo cargar la imagen: {image_path}")
    
    # Crear una copia para dibujar
    img_with_zones = img.copy()
    
    # Dibujar líneas
    for i, line in enumerate(zonas.get("lines", [])):
        # Manejar tanto formato nuevo (dict) como antiguo (list)
        if isinstance(line, dict):
            line_coords = line["coordinates"]
            line_name = line["name"]
        else:
            line_coords = line
            line_name = f"L{i+1}"
            
        if len(line_coords) == 2:
            # Dibujar línea
            cv2.line(img_with_zones, line_coords[0], line_coords[1], (0, 0, 255), 3)
            # Dibujar puntos
            cv2.circle(img_with_zones, line_coords[0], 8, (0, 0, 255), -1)
            cv2.circle(img_with_zones, line_coords[1], 8, (0, 0, 255), -1)
            # Agregar texto
            cv2.putText(img_with_zones, line_name, 
                       (line_coords[0][0] + 10, line_coords[0][1] - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    
    # Dibujar polígonos
    for i, polygon in enumerate(zonas.get("polygons", [])):
        # Manejar tanto formato nuevo (dict) como antiguo (list)
        if isinstance(polygon, dict):
            polygon_coords = polygon["coordinates"]
            polygon_name = polygon["name"]
        else:
            polygon_coords = polygon
            polygon_name = f"Z{i+1}"
            
        if len(polygon_coords) >= 3:
            # Convertir a array de numpy
            polygon_array = np.array(polygon_coords, dtype=np.int32)
            # Dibujar polígono
            cv2.polylines(img_with_zones, [polygon_array], True, (255, 0, 0), 3)
            # Dibujar puntos
            for pt in polygon_coords:
                cv2.circle(img_with_zones, pt, 6, (255, 0, 0), -1)
            # Agregar texto (centro del polígono)
            center_x = sum(pt[0] for pt in polygon_coords) // len(polygon_coords)
            center_y = sum(pt[1] for pt in polygon_coords) // len(polygon_coords)
            cv2.putText(img_with_zones, polygon_name, 
                       (center_x - 20, center_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
    
    # Agregar leyenda
    legend_y = 30
    cv2.putText(img_with_zones, "LEYENDA:", (10, legend_y), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    legend_y += 25
    
    # Leyenda para líneas
    if zonas.get("lines"):
        cv2.putText(img_with_zones, "L1, L2, ... = Lineas de cruce (ROJO)", 
                   (10, legend_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        legend_y += 20
    
    # Leyenda para polígonos
    if zonas.get("polygons"):
        cv2.putText(img_with_zones, "Z1, Z2, ... = Zonas de interes (AZUL)", 
                   (10, legend_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
    
    # Guardar imagen si se especifica output_path
    if output_path:
        cv2.imwrite(output_path, img_with_zones)
        print(f"📸 Imagen con zonas guardada: {output_path}")
    
    return img_with_zones


def select_line(image_path):
    """Permite al usuario seleccionar una línea haciendo clic en 2 puntos."""
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"No se pudo cargar la imagen: {image_path}")
    
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


def generate_unique_name(config_type, description=""):
    """Genera un nombre único para la configuración."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = f"{config_type}_{timestamp}"
    
    if description:
        # Limpiar descripción para usar como nombre de archivo
        clean_desc = "".join(c for c in description if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_desc = clean_desc.replace(' ', '_')
        base_name = f"{config_type}_{clean_desc}_{timestamp}"
    
    return base_name


def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(
        description="Herramienta Interactiva de Configuración de Zonas de Interés",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EJEMPLOS DE USO:

  Configurar líneas de cruce:
    uv run src/utils/configurar_zonas.py --lines --video "data/videos/video.mp4" --frame 5
    uv run src/utils/configurar_zonas.py --lines --video "data/videos/video.mp4" --description "entrada_principal"

  Configurar polígonos de área:
    uv run src/utils/configurar_zonas.py --polygons --video "data/videos/video.mp4" --frame 10
    uv run src/utils/configurar_zonas.py --polygons --image "frame.png"

  Configurar ambos tipos:
    uv run src/utils/configurar_zonas.py --lines --polygons --video "data/videos/video.mp4"

  Con nombres personalizados:
    uv run src/utils/configurar_zonas.py --lines --video "data/videos/video.mp4" --line-names "entrada,salida"
    uv run src/utils/configurar_zonas.py --polygons --video "data/videos/video.mp4" --zone-names "area_restringida,zona_segura"

CONTROLES INTERACTIVOS:

  Para LÍNEAS:
    • Clic izquierdo: Marcar puntos de la línea (mínimo 2 puntos)
    • Clic derecho: Finalizar línea actual
    • Tecla 'n': Nueva línea
    • Tecla 's': Guardar configuración
    • Tecla 'q': Salir sin guardar

  Para POLÍGONOS:
    • Clic izquierdo: Marcar vértices del polígono (mínimo 3 puntos)
    • Clic derecho: Cerrar polígono actual
    • Tecla 'n': Nuevo polígono
    • Tecla 's': Guardar configuración
    • Tecla 'q': Salir sin guardar

HERRAMIENTAS RELACIONADAS:
    uv run src/utils/listar_configuraciones.py    # Ver configuraciones existentes
    uv run src/utils/visualizar_zonas.py          # Visualizar configuración específica
        """
    )
    
    # Argumentos de configuración
    parser.add_argument(
        "--lines",
        action="store_true",
        help="Configurar líneas de cruce para detectar movimiento direccional"
    )
    parser.add_argument(
        "--polygons",
        action="store_true",
        help="Configurar polígonos de área para detectar entrada/salida de zonas"
    )
    
    # Argumentos de entrada
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--image", "-i",
        help="Ruta a la imagen de referencia para configurar zonas"
    )
    input_group.add_argument(
        "--video", "-v",
        help="Ruta al video de referencia para extraer frame y configurar zonas"
    )
    
    # Argumentos opcionales
    parser.add_argument(
        "--frame", "-f",
        type=int,
        default=0,
        help="Número de frame a extraer del video (por defecto: 0, primer frame)"
    )
    parser.add_argument(
        "--description", "-d",
        help="Descripción personalizada para identificar la configuración (ej: 'entrada_principal')"
    )
    parser.add_argument(
        "--config-dir",
        default="configs",
        help="Directorio donde guardar la configuración (por defecto: configs/)"
    )
    parser.add_argument(
        "--line-names",
        help="Nombres personalizados para líneas separados por coma (ej: 'entrada_principal,salida_emergencia')"
    )
    parser.add_argument(
        "--zone-names", 
        help="Nombres personalizados para polígonos separados por coma (ej: 'area_restringida,zona_segura')"
    )
    
    args = parser.parse_args()
    
    # Verificar que se especifique al menos un tipo de configuración
    if not args.lines and not args.polygons:
        print("❌ Error: Debes especificar --lines y/o --polygons")
        sys.exit(1)
    
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
        
        # Generar nombre único para la configuración
        config_type = "completa" if args.lines and args.polygons else "lineas" if args.lines else "polygonos"
        unique_name = generate_unique_name(config_type, args.description)
        
        # Crear directorio de configuración si no existe
        config_dir = Path(args.config_dir)
        config_dir.mkdir(exist_ok=True)
        
        # Crear subdirectorio para esta configuración
        config_subdir = config_dir / unique_name
        config_subdir.mkdir(exist_ok=True)
        
        # Inicializar estructura de zonas
        zonas = {"lines": [], "polygons": []}
        
        # Procesar nombres personalizados
        line_names = []
        zone_names = []
        
        if args.line_names:
            line_names = [name.strip() for name in args.line_names.split(',')]
            print(f"📝 Nombres de líneas especificados: {line_names}")
        
        if args.zone_names:
            zone_names = [name.strip() for name in args.zone_names.split(',')]
            print(f"📝 Nombres de zonas especificados: {zone_names}")
        
        # Configurar líneas
        if args.lines:
            print("\n🎯 CONFIGURACIÓN DE LÍNEAS")
            print("-" * 30)
            
            # Determinar cuántas líneas configurar
            if line_names:
                num_lines = len(line_names)
                print(f"📊 Configurando {num_lines} líneas con nombres personalizados")
            else:
                num_lines = None
                print("📊 Configurando líneas (preguntará si agregar más)")
            
            line_count = 0
            while True:
                try:
                    linea = select_line(image_path)
                    
                    # Crear objeto de línea con nombre si está disponible
                    if line_names and line_count < len(line_names):
                        # Usar nombres específicos proporcionados
                        line_obj = {
                            "id": f"line_{line_names[line_count]}",
                            "name": line_names[line_count],
                            "coordinates": linea
                        }
                        zonas["lines"].append(line_obj)
                    elif args.description:
                        # Usar descripción para generar nombres automáticos
                        line_name = f"{args.description}_{line_count + 1}" if line_count > 0 else args.description
                        line_obj = {
                            "id": f"line_{line_name}",
                            "name": line_name,
                            "coordinates": linea
                        }
                        zonas["lines"].append(line_obj)
                    else:
                        # Formato simple si no hay nombres personalizados ni descripción
                        zonas["lines"].append(linea)
                    
                    line_count += 1
                    
                    # Mostrar nombre si está disponible
                    if line_names and line_count <= len(line_names):
                        print(f"✅ Línea '{line_names[line_count-1]}' configurada")
                    elif args.description:
                        line_name = f"{args.description}_{line_count}" if line_count > 1 else args.description
                        print(f"✅ Línea '{line_name}' configurada")
                    
                    # Preguntar si agregar más líneas (solo si no se especificaron nombres)
                    if line_names and line_count >= len(line_names):
                        print(f"✅ Todas las {len(line_names)} líneas configuradas")
                        break
                    elif not line_names:
                        response = input("\n¿Agregar otra línea? (s/n): ").lower().strip()
                        if response not in ['s', 'si', 'y', 'yes']:
                            break
                except KeyboardInterrupt:
                    print("\n⚠️  Configuración de líneas cancelada")
                    break
        
        # Configurar polígonos
        if args.polygons:
            print("\n🎯 CONFIGURACIÓN DE POLÍGONOS")
            print("-" * 30)
            
            # Determinar cuántos polígonos configurar
            if zone_names:
                num_zones = len(zone_names)
                print(f"📊 Configurando {num_zones} zonas con nombres personalizados")
            else:
                num_zones = None
                print("📊 Configurando zonas (preguntará si agregar más)")
            
            zone_count = 0
            while True:
                try:
                    poligono = select_polygon(image_path)
                    if poligono is None:
                        print("⚠️  Polígono cancelado")
                        break
                    
                    # Crear objeto de zona con nombre si está disponible
                    if zone_names and zone_count < len(zone_names):
                        # Usar nombres específicos proporcionados
                        zone_obj = {
                            "id": f"zone_{zone_names[zone_count]}",
                            "name": zone_names[zone_count],
                            "coordinates": poligono
                        }
                        zonas["polygons"].append(zone_obj)
                    elif args.description:
                        # Usar descripción para generar nombres automáticos
                        zone_name = f"{args.description}_{zone_count + 1}" if zone_count > 0 else args.description
                        zone_obj = {
                            "id": f"zone_{zone_name}",
                            "name": zone_name,
                            "coordinates": poligono
                        }
                        zonas["polygons"].append(zone_obj)
                    else:
                        # Formato simple si no hay nombres personalizados ni descripción
                        zonas["polygons"].append(poligono)
                    
                    zone_count += 1
                    
                    # Mostrar nombre si está disponible
                    if zone_names and zone_count <= len(zone_names):
                        print(f"✅ Zona '{zone_names[zone_count-1]}' configurada")
                    elif args.description:
                        zone_name = f"{args.description}_{zone_count}" if zone_count > 1 else args.description
                        print(f"✅ Zona '{zone_name}' configurada")
                    
                    # Preguntar si agregar más polígonos (solo si no se especificaron nombres)
                    if zone_names and zone_count >= len(zone_names):
                        print(f"✅ Todas las {len(zone_names)} zonas configuradas")
                        break
                    elif not zone_names:
                        response = input("\n¿Agregar otro polígono? (s/n): ").lower().strip()
                        if response not in ['s', 'si', 'y', 'yes']:
                            break
                except KeyboardInterrupt:
                    print("\n⚠️  Configuración de polígonos cancelada")
                    break
        
        # Guardar configuración
        config_file = config_subdir / "zonas.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(zonas, f, indent=2, ensure_ascii=False)
        
        # Generar imagen con zonas (SIEMPRE se guarda)
        image_file = config_subdir / "zonas_visual.png"
        draw_zones_on_image(image_path, zonas, str(image_file))
        
        # Guardar frame original
        frame_file = config_subdir / "frame_original.png"
        cv2.imwrite(str(frame_file), cv2.imread(image_path))
        
        print("\n" + "=" * 50)
        print("🎉 CONFIGURACIÓN COMPLETADA")
        print("=" * 50)
        print(f"📁 Directorio: {config_subdir}")
        print(f"📄 Configuración: {config_file}")
        print(f"🖼️  Imagen con zonas: {image_file}")
        print(f"📸 Frame original: {frame_file}")
        print(f"📊 Líneas configuradas: {len(zonas['lines'])}")
        print(f"📊 Polígonos configurados: {len(zonas['polygons'])}")
        
        # Mostrar resumen de la configuración
        if zonas["lines"]:
            print("\n📍 LÍNEAS CONFIGURADAS:")
            for i, line in enumerate(zonas["lines"], 1):
                if isinstance(line, dict):
                    print(f"   {i}. {line['name']} (ID: {line['id']})")
                else:
                    print(f"   {i}. {line[0]} → {line[1]}")
        
        if zonas["polygons"]:
            print("\n📍 POLÍGONOS CONFIGURADAS:")
            for i, poly in enumerate(zonas["polygons"], 1):
                if isinstance(poly, dict):
                    print(f"   {i}. {poly['name']} (ID: {poly['id']})")
                else:
                    print(f"   {i}. {len(poly)} puntos")
        
        print(f"\n🚀 Para usar esta configuración:")
        print(f"   uv run src/main.py process \\")
        print(f"       --video-path \"tu_video.mp4\" \\")
        print(f"       --model-path \"tu_modelo.pt\" \\")
        print(f"       --enable-zones \"{config_file}\"")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Configuración cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
