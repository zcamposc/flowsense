#!/usr/bin/env python3
"""
Script para probar y visualizar la lógica de detección de cruce de línea
basada en geometría vectorial (producto cruz).
"""

import sys
import os
import cv2
import numpy as np
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils.geometry import determinar_direccion_cruce, determinar_lado_del_punto


def ejecutar_prueba_con_logica_de_estado():
    """
    Genera un informe visual que implementa una lógica de estado robusta
    para evitar falsos positivos en detecciones súbitas.
    """
    # --- CONFIGURACIÓN DEL LIENZO Y LA LÍNEA ---
    canvas_width, canvas_height = 1920, 1080
    canvas = np.ones((canvas_height, canvas_width, 3), dtype=np.uint8) * 245
    line_coords = [[1003, 851], [1666, 351]]
    line_start, line_end = line_coords

    def get_point_on_line(t):
        x = int(line_start[0] + t * (line_end[0] - line_start[0]))
        y = int(line_start[1] + t * (line_end[1] - line_start[1]))
        return (x, y)

    puntos_cruce = {f"C{i+1}": get_point_on_line(0.15 + i * 0.15) for i in range(6)}

    # --- CASOS DE PRUEBA ACTUALIZADOS ---
    # C6 ahora espera "No Contar" porque no hay un estado previo.
    test_cases = [
        {"id": "C1", "desc": "ENTRADA Perpendicular", "mov": [ (puntos_cruce["C1"][0]+80, puntos_cruce["C1"][1]+60), (puntos_cruce["C1"][0]-80, puntos_cruce["C1"][1]-60) ], "color": (0, 200, 0), "expected": "ENTRADA (der -> izq)"},
        {"id": "C2", "desc": "SALIDA Perpendicular", "mov": [ (puntos_cruce["C2"][0]-80, puntos_cruce["C2"][1]-60), (puntos_cruce["C2"][0]+80, puntos_cruce["C2"][1]+60) ], "color": (0, 0, 200), "expected": "SALIDA (izq -> der)"},
        {"id": "C3", "desc": "ENTRADA Diagonal", "mov": [ (puntos_cruce["C3"][0]+120, puntos_cruce["C3"][1]-20), (puntos_cruce["C3"][0]-40, puntos_cruce["C3"][1]-50) ], "color": (50, 255, 50), "expected": "ENTRADA (der -> izq)"},
        {"id": "C4", "desc": "SALIDA Diagonal", "mov": [ (puntos_cruce["C4"][0]-120, puntos_cruce["C4"][1]+20), (puntos_cruce["C4"][0]+40, puntos_cruce["C4"][1]+50) ], "color": (50, 50, 255), "expected": "SALIDA (izq -> der)"},
        {"id": "C5", "desc": "ENTRADA (cruce sutil)", "mov": [ (puntos_cruce["C5"][0]+40, puntos_cruce["C5"][1]-20), (puntos_cruce["C5"][0]+15, puntos_cruce["C5"][1]-30) ], "color": (255, 128, 0), "expected": "ENTRADA (der -> izq)"},
        {"id": "C6", "desc": "Aparición Súbita", "mov": [ (puntos_cruce["C6"][0]+25, puntos_cruce["C6"][1]+15), (puntos_cruce["C6"][0]+5, puntos_cruce["C6"][1]+5) ], "color": (200, 0, 200), "expected": "No Contar"} # <-- El cambio clave
    ]
    
    results_data = []
    
    # --- DIBUJAR VISUALIZACIÓN ---
    cv2.line(canvas, tuple(line_start), tuple(line_end), (0, 0, 0), 3)
    cv2.circle(canvas, tuple(line_start), 12, (0, 0, 200), -1)
    cv2.circle(canvas, tuple(line_end), 12, (200, 0, 0), -1)

    for case in test_cases:
        pos_inicial, pos_final = case["mov"]
        
        # --- LÓGICA DE ESTADO APLICADA ---
        estado_anterior = determinar_lado_del_punto(pos_inicial, line_coords)
        estado_actual = determinar_lado_del_punto(pos_final, line_coords)
        
        resultado_final = ""
        # Un cruce solo es válido si el estado (la zona) cambia.
        if estado_anterior != estado_actual:
            resultado_final = determinar_direccion_cruce(pos_inicial, pos_final, line_coords)
        else:
            # Si el objeto aparece y se mueve dentro de la misma zona, no hay cruce.
            resultado_final = "No Contar"

        status = "✅" if (resultado_final == case["expected"]) else "❌"
        
        results_data.append({
            "Caso": case["id"],
            "Descripción": case["desc"],
            "Resultado": resultado_final,
            "Estado": status
        })

        # Dibujar en el lienzo
        cv2.arrowedLine(canvas, pos_inicial, pos_final, case["color"], 3, tipLength=0.4)
        cv2.circle(canvas, pos_inicial, 10, case["color"], -1)
        cv2.circle(canvas, pos_inicial, 12, (0, 0, 0), 2)
        cv2.putText(canvas, case['id'], (pos_inicial[0] - 15, pos_inicial[1] - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 2)

    # --- DIBUJAR TABLA DE RESULTADOS EN LA IMAGEN ---
    table_x, table_y = 50, 100
    row_height = 40
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.7
    font_thickness = 2
    
    cv2.rectangle(canvas, (table_x - 20, table_y - 40), (table_x + 850, table_y + len(results_data) * row_height + 20), (220, 220, 220), -1)
    cv2.rectangle(canvas, (table_x - 20, table_y - 40), (table_x + 850, table_y + len(results_data) * row_height + 20), (0,0,0), 2)
    
    headers = {"Caso": 0, "Descripción": 100, "Resultado Detectado": 450, "Estado": 750}
    cv2.putText(canvas, "TABLA DE RESULTADOS (CON LÓGICA DE ESTADO)", (table_x, table_y - 10), font, 0.8, (0,0,0), 2)
    current_y = table_y + row_height

    for header, pos_x in headers.items():
        cv2.putText(canvas, header, (table_x + pos_x, current_y), font, font_scale, (0,0,0), font_thickness)
    
    cv2.line(canvas, (table_x, current_y + 10), (table_x + 830, current_y + 10), (0,0,0), 1)
    current_y += row_height

    for result in results_data:
        cv2.putText(canvas, result['Caso'], (table_x + headers['Caso'], current_y), font, font_scale, (0,0,0), 1)
        cv2.putText(canvas, result['Descripción'], (table_x + headers['Descripción'], current_y), font, font_scale, (0,0,0), 1)
        cv2.putText(canvas, result['Resultado'], (table_x + headers['Resultado Detectado'], current_y), font, font_scale, (0,0,0), 1)
        cv2.putText(canvas, result['Estado'], (table_x + headers['Estado'], current_y), font, font_scale, (0,0,0), 2)
        current_y += row_height

    # --- GUARDAR IMAGEN FINAL ---
    ruta_salida = "informe_final_con_logica_de_estado.png"
    cv2.imwrite(ruta_salida, canvas)
    print(f"\n✅ ¡Informe visual con lógica de estado generado exitosamente!")
    print(f"🖼️  Imagen guardada en: '{ruta_salida}'")

if __name__ == "__main__":
    ejecutar_prueba_con_logica_de_estado()