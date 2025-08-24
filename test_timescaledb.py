#!/usr/bin/env python3
"""
Script de prueba para TimescaleDB
FASE 9: Base de Datos de Series de Tiempo
"""

import os
import sys
from datetime import datetime, timedelta

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_timescaledb_connection():
    """Prueba la conexión a TimescaleDB."""
    print("🔌 PROBANDO CONEXIÓN A TIMESCALEDB")
    print("=" * 50)
    
    try:
        import psycopg2
        
        # Conectar a TimescaleDB
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="cgallego",
            password="postgres123",
            database="video_analysis"
        )
        
        cursor = conn.cursor()
        
        # Verificar versión
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ Conectado a: {version}")
        
        # Verificar extensión TimescaleDB
        cursor.execute("SELECT * FROM pg_available_extensions WHERE name = 'timescaledb';")
        timescale_info = cursor.fetchone()
        if timescale_info:
            print(f"✅ TimescaleDB disponible: {timescale_info[1]}")
        else:
            print("❌ TimescaleDB no disponible")
            return False
        
        # Verificar hypertables
        cursor.execute("SELECT hypertable_name, num_chunks FROM timescaledb_information.hypertables;")
        hypertables = cursor.fetchall()
        print(f"✅ Hypertables encontradas: {len(hypertables)}")
        for name, chunks in hypertables:
            print(f"   • {name}: {chunks} chunks")
        
        # Verificar tablas
        cursor.execute("""
            SELECT table_name, table_type 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        print(f"✅ Tablas encontradas: {len(tables)}")
        for name, table_type in tables:
            print(f"   • {name} ({table_type})")
        
        cursor.close()
        conn.close()
        
        print("✅ Conexión a TimescaleDB exitosa")
        return True
        
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_timescaledb_functionality():
    """Prueba la funcionalidad básica de TimescaleDB."""
    print("\n🧪 PROBANDO FUNCIONALIDAD DE TIMESCALEDB")
    print("=" * 50)
    
    try:
        import psycopg2
        
        # Conectar a TimescaleDB
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="cgallego",
            password="postgres123",
            database="video_analysis"
        )
        
        cursor = conn.cursor()
        
        # Crear análisis de prueba
        cursor.execute("""
            INSERT INTO video_analyses (video_path, model_name, status, started_at)
            VALUES (%s, %s, %s, %s)
            RETURNING id;
        """, (
            "test_video.mp4",
            "yolov8n.pt",
            "running",
            datetime.now()
        ))
        
        analysis_id = cursor.fetchone()[0]
        print(f"✅ Análisis de prueba creado: {analysis_id}")
        
        # Agregar zona de prueba
        cursor.execute("""
            INSERT INTO zones (video_analysis_id, zone_name, zone_type, coordinates)
            VALUES (%s, %s, %s, %s)
            RETURNING id;
        """, (
            analysis_id,
            "test_zone",
            "polygon",
            '[[100, 100], [200, 100], [200, 200], [100, 200]]'
        ))
        
        zone_id = cursor.fetchone()[0]
        print(f"✅ Zona de prueba creada: {zone_id}")
        
        # Insertar detecciones de prueba
        now = datetime.now()
        for i in range(5):
            timestamp = now + timedelta(seconds=i)
            cursor.execute("""
                INSERT INTO frame_detections (
                    time, video_analysis_id, frame_number, track_id, class_name,
                    confidence, bbox_x1, bbox_y1, bbox_x2, bbox_y2,
                    center_x, center_y
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                timestamp, analysis_id, i, i, "person", 0.95,
                100 + i*10, 100 + i*10, 150 + i*10, 150 + i*10,
                125 + i*10, 125 + i*10
            ))
        
        print("✅ 5 detecciones de prueba insertadas")
        
        # Insertar evento de zona de prueba
        cursor.execute("""
            INSERT INTO zone_events (
                time, video_analysis_id, zone_id, track_id, event_type,
                class_name, confidence, position_x, position_y
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            now, analysis_id, zone_id, 1, "enter",
            "person", 0.95, 150, 150
        ))
        
        print("✅ Evento de zona de prueba insertado")
        
        # Probar consulta de agregación por tiempo
        cursor.execute("""
            SELECT 
                time_bucket('1 second', time) as second_bucket,
                COUNT(*) as total_detections,
                COUNT(DISTINCT track_id) as unique_tracks
            FROM frame_detections 
            WHERE video_analysis_id = %s
            GROUP BY second_bucket
            ORDER BY second_bucket;
        """, (analysis_id,))
        
        results = cursor.fetchall()
        print(f"✅ Consulta de agregación exitosa: {len(results)} buckets")
        for bucket, total, tracks in results:
            print(f"   • {bucket}: {total} detecciones, {tracks} tracks")
        
        # Limpiar datos de prueba
        cursor.execute("DELETE FROM zone_events WHERE video_analysis_id = %s", (analysis_id,))
        cursor.execute("DELETE FROM frame_detections WHERE video_analysis_id = %s", (analysis_id,))
        cursor.execute("DELETE FROM zones WHERE video_analysis_id = %s", (analysis_id,))
        cursor.execute("DELETE FROM video_analyses WHERE id = %s", (analysis_id,))
        
        print("✅ Datos de prueba limpiados")
        
        cursor.close()
        conn.close()
        
        print("✅ Funcionalidad de TimescaleDB verificada")
        return True
        
    except Exception as e:
        print(f"❌ Error en funcionalidad: {e}")
        return False

def main():
    """Función principal de prueba."""
    print("🚀 PRUEBA DE TIMESCALEDB - FASE 9")
    print("=" * 50)
    
    # Probar conexión
    if not test_timescaledb_connection():
        print("\n❌ No se pudo conectar a TimescaleDB")
        return False
    
    # Probar funcionalidad
    if not test_timescaledb_functionality():
        print("\n❌ Error en funcionalidad de TimescaleDB")
        return False
    
    print("\n🎉 ¡PRUEBA DE TIMESCALEDB COMPLETADA EXITOSAMENTE!")
    print("\n💡 PRÓXIMOS PASOS:")
    print("   1. TimescaleDB está funcionando correctamente")
    print("   2. El esquema optimizado está listo")
    print("   3. Puedes ejecutar análisis de video con --enable-database")
    
    return True

if __name__ == "__main__":
    main()

