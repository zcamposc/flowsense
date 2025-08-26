#!/usr/bin/env python3
"""
Script de depuración para verificar el problema con la vista analysis_summary.
"""

import psycopg2
import os

def debug_analysis_summary():
    """Verificar el problema con la vista analysis_summary."""
    try:
        # Conectar a la base de datos
        conn = psycopg2.connect(
            host='localhost',
            port='5432',
            user='cgallego',
            password='postgres123',
            database='video_analysis'
        )
        
        cursor = conn.cursor()
        
        print("🔍 VERIFICANDO PROBLEMA CON ANALYSIS_SUMMARY")
        print("=" * 50)
        
        # Verificar análisis más reciente
        cursor.execute("""
            SELECT id, video_path, model_name, created_at 
            FROM video_analyses 
            ORDER BY created_at DESC 
            LIMIT 1
        """)
        
        analysis = cursor.fetchone()
        if not analysis:
            print("❌ No hay análisis de video en la base de datos")
            return
        
        analysis_id, video_path, model_name, created_at = analysis
        print(f"📹 Análisis más reciente:")
        print(f"   • ID: {analysis_id}")
        print(f"   • Video: {video_path}")
        print(f"   • Modelo: {model_name}")
        print(f"   • Fecha: {created_at}")
        print()
        
        # Verificar conteos reales en las tablas
        cursor.execute("""
            SELECT COUNT(*) as total_detections
            FROM frame_detections 
            WHERE video_analysis_id = %s
        """, (analysis_id,))
        
        real_detections = cursor.fetchone()[0]
        print(f"📊 Total de detecciones reales: {real_detections}")
        
        cursor.execute("""
            SELECT COUNT(*) as total_cruces
            FROM line_crossing_events 
            WHERE video_analysis_id = %s
        """, (analysis_id,))
        
        real_cruces = cursor.fetchone()[0]
        print(f"➡️  Total de cruces de línea reales: {real_cruces}")
        
        # Verificar qué muestra la vista
        cursor.execute("""
            SELECT total_detections, total_line_crossings
            FROM analysis_summary 
            WHERE id = %s
        """, (analysis_id,))
        
        summary = cursor.fetchone()
        if summary:
            summary_detections, summary_crossings = summary
            print(f"\n📋 Resumen de la vista analysis_summary:")
            print(f"   • Total detecciones: {summary_detections}")
            print(f"   • Total cruces de línea: {summary_crossings}")
            
            print(f"\n⚠️  DISCREPANCIAS:")
            if summary_detections != real_detections:
                print(f"   • Detecciones: Vista={summary_detections}, Real={real_detections}")
            if summary_crossings != real_cruces:
                print(f"   • Cruces: Vista={summary_crossings}, Real={real_cruces}")
        
        # Verificar la estructura de la vista
        print(f"\n🔍 ESTRUCTURA DE LA VISTA ANALYSIS_SUMMARY:")
        cursor.execute("""
            SELECT definition FROM pg_views WHERE viewname = 'analysis_summary'
        """)
        
        view_definition = cursor.fetchone()
        if view_definition:
            print("   • Definición de la vista:")
            print(view_definition[0])
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_analysis_summary()
