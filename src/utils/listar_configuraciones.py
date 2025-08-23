#!/usr/bin/env python3
"""
Script para listar y gestionar configuraciones de zonas existentes.

Uso:
    python listar_configuraciones.py
    python listar_configuraciones.py --config-dir "configs"
    python listar_configuraciones.py --show-images
"""

import json
import argparse
import os
import sys
from pathlib import Path
from datetime import datetime


def parse_config_name(config_dir_name):
    """Parsea el nombre del directorio de configuración."""
    try:
        # Formato esperado: tipo_descripcion_YYYYMMDD_HHMMSS
        parts = config_dir_name.split('_')
        
        if len(parts) < 3:
            return {
                'tipo': 'desconocido',
                'descripcion': config_dir_name,
                'fecha': 'desconocida',
                'hora': 'desconocida'
            }
        
        # Extraer tipo y descripción
        tipo = parts[0]
        
        # Buscar el timestamp al final
        timestamp_part = parts[-1]
        if len(timestamp_part) == 6 and timestamp_part.isdigit():
            # Formato HHMMSS
            hora = timestamp_part[:2] + ":" + timestamp_part[2:4] + ":" + timestamp_part[4:]
            
            # Buscar fecha en formato YYYYMMDD
            fecha_part = parts[-2]
            if len(fecha_part) == 8 and fecha_part.isdigit():
                fecha = fecha_part[:4] + "-" + fecha_part[4:6] + "-" + fecha_part[6:]
                
                # Descripción es todo lo que está en medio
                descripcion = "_".join(parts[1:-2])
            else:
                fecha = "desconocida"
                descripcion = "_".join(parts[1:-1])
        else:
            fecha = "desconocida"
            hora = "desconocida"
            descripcion = "_".join(parts[1:])
        
        return {
            'tipo': tipo,
            'descripcion': descripcion or 'sin_descripcion',
            'fecha': fecha,
            'hora': hora
        }
    except Exception:
        return {
            'tipo': 'desconocido',
            'descripcion': config_dir_name,
            'fecha': 'desconocida',
            'hora': 'desconocida'
        }


def load_config_info(config_dir):
    """Carga información de una configuración."""
    config_file = config_dir / "zonas.json"
    visual_file = config_dir / "zonas_visual.png"
    frame_file = config_dir / "frame_original.png"
    
    info = {
        'directorio': config_dir.name,
        'config_file': str(config_file) if config_file.exists() else None,
        'visual_file': str(visual_file) if visual_file.exists() else None,
        'frame_file': str(frame_file) if frame_file.exists() else None,
        'existe': config_file.exists()
    }
    
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                zonas = json.load(f)
            
            info['lineas'] = len(zonas.get('lines', []))
            info['polygonos'] = len(zonas.get('polygons', []))
            info['total_elementos'] = info['lineas'] + info['polygonos']
        except Exception as e:
            info['error'] = str(e)
            info['lineas'] = 0
            info['polygonos'] = 0
            info['total_elementos'] = 0
    else:
        info['lineas'] = 0
        info['polygonos'] = 0
        info['total_elementos'] = 0
    
    return info


def list_configurations(config_dir_path, show_images=False):
    """Lista todas las configuraciones disponibles."""
    config_dir = Path(config_dir_path)
    
    if not config_dir.exists():
        print(f"❌ Error: El directorio {config_dir} no existe")
        return
    
    # Buscar directorios de configuración
    config_dirs = []
    for item in config_dir.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            config_dirs.append(item)
    
    if not config_dirs:
        print(f"📁 No se encontraron configuraciones en {config_dir}")
        return
    
    # Ordenar por fecha de creación (más reciente primero)
    config_dirs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    print(f"📁 Configuraciones encontradas en {config_dir}:")
    print("=" * 80)
    
    for i, config_dir_item in enumerate(config_dirs, 1):
        # Parsear nombre del directorio
        parsed = parse_config_name(config_dir_item.name)
        
        # Cargar información de la configuración
        info = load_config_info(config_dir_item)
        
        # Mostrar información
        print(f"{i:2d}. 📂 {config_dir_item.name}")
        print(f"    📅 Fecha: {parsed['fecha']} {parsed['hora']}")
        print(f"    🏷️  Tipo: {parsed['tipo']}")
        print(f"    📝 Descripción: {parsed['descripcion']}")
        
        if info['existe']:
            print(f"    📊 Elementos: {info['lineas']} líneas, {info['polygonos']} polígonos")
            print(f"    📄 Config: {info['config_file']}")
            
            if info['visual_file']:
                print(f"    🖼️  Visual: {info['visual_file']}")
            
            if info['frame_file']:
                print(f"    📸 Frame: {info['frame_file']}")
        else:
            print(f"    ❌ Configuración no válida")
        
        print()


def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(
        description="Listar y gestionar configuraciones de zonas existentes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  # Listar todas las configuraciones
  python listar_configuraciones.py
  
  # Listar desde directorio específico
  python listar_configuraciones.py --config-dir "mi_configs"
  
  # Mostrar información detallada de imágenes
  python listar_configuraciones.py --show-images
        """
    )
    
    parser.add_argument(
        "--config-dir",
        default="configs",
        help="Directorio de configuraciones (por defecto: configs)"
    )
    parser.add_argument(
        "--show-images",
        action="store_true",
        help="Mostrar información detallada de imágenes"
    )
    
    args = parser.parse_args()
    
    try:
        list_configurations(args.config_dir, args.show_images)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Operación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
