#!/usr/bin/env python3
"""
Script de debug para probar la lógica de detección de zonas.
"""

import json
from utils.geometry import punto_en_poligono


def debug_zone_detection():
    """Prueba la lógica de detección de zonas."""
    
    # Cargar configuración de zonas
    zones_file = ("configs/polygonos_zonas_restriccion_20250818_193036/"
                  "zonas.json")
    with open(zones_file, "r") as f:
        zones_config = json.load(f)
    
    polygons = zones_config["polygons"]
    
    print(f"Zonas cargadas: {len(polygons)}")
    
    # Simular algunas posiciones de prueba
    test_positions = [
        (300, 500),   # Debería estar en zona 1
        (1200, 600),  # Debería estar en zona 2
        (800, 800),   # No debería estar en ninguna zona
        (200, 200),   # No debería estar en ninguna zona
    ]
    
    for i, (x, y) in enumerate(test_positions):
        print(f"\nPosición de prueba {i+1}: ({x}, {y})")
        
        for j, polygon in enumerate(polygons):
            is_in_zone = punto_en_poligono((x, y), polygon)
            print(f"  Zona {j+1}: {'SÍ' if is_in_zone else 'NO'}")
    
    # Simular tracking de un objeto
    print("\n" + "="*50)
    print("SIMULACIÓN DE TRACKING")
    print("="*50)
    
    # Simular que un objeto entra y sale de la zona 1
    track_id = 1
    ids_en_zona = set()
    
    # Frame 1: Objeto entra en zona 1
    pos1 = (300, 500)
    is_in_zone1 = punto_en_poligono(pos1, polygons[0])
    
    if is_in_zone1 and track_id not in ids_en_zona:
        ids_en_zona.add(track_id)
        print(f"Frame 1: Objeto {track_id} ENTRÓ en zona 1")
    elif not is_in_zone1 and track_id in ids_en_zona:
        ids_en_zona.discard(track_id)
        print(f"Frame 1: Objeto {track_id} SALIÓ de zona 1")
    
    # Frame 2: Objeto sale de zona 1
    pos2 = (800, 800)
    is_in_zone2 = punto_en_poligono(pos2, polygons[0])
    
    if is_in_zone2 and track_id not in ids_en_zona:
        ids_en_zona.add(track_id)
        print(f"Frame 2: Objeto {track_id} ENTRÓ en zona 1")
    elif not is_in_zone2 and track_id in ids_en_zona:
        ids_en_zona.discard(track_id)
        print(f"Frame 2: Objeto {track_id} SALIÓ de zona 1")
    
    print(f"Estado final: Objeto en zona = {track_id in ids_en_zona}")


if __name__ == "__main__":
    debug_zone_detection()
