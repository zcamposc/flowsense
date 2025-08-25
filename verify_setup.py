#!/usr/bin/env python3
"""
Script de verificación de configuración TimescaleDB
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv


def main():
    print("🔍 Verificando configuración de TimescaleDB...")

    # Cargar variables de entorno
    load_dotenv()

    # Verificar variables de entorno
    required_vars = ['DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
    missing_vars = []

    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print(f"❌ Variables de entorno faltantes: {', '.join(missing_vars)}")
        print("💡 Asegúrate de tener un archivo .env configurado")
        return False

    # Probar conexión
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        print("✅ Conexión a base de datos exitosa")
        cursor = conn.cursor()

        # Verificar TimescaleDB
        cursor.execute("""
            SELECT default_version, installed_version
            FROM pg_available_extensions
            WHERE name = 'timescaledb'
        """)
        result = cursor.fetchone()

        if result:
            print(f"✅ TimescaleDB instalado: versión {result[1]}")
        else:
            print("❌ TimescaleDB no encontrado")
            return False

        # Verificar hypertables
        cursor.execute("""
            SELECT hypertable_name, num_chunks
            FROM timescaledb_information.hypertables
        """)
        hypertables = cursor.fetchall()

        if hypertables:
            print("✅ Hypertables encontradas:")
            for table, chunks in hypertables:
                print(f"   • {table}: {chunks} chunks")
        else:
            print("⚠️  No se encontraron hypertables")

        # Verificar tablas principales
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = [row[0] for row in cursor.fetchall()]

        expected_tables = ['video_analyses', 'zones', 'zone_events',
                           'line_crossing_events']
        missing_tables = [t for t in expected_tables if t not in tables]

        if missing_tables:
            print(f"❌ Tablas faltantes: {', '.join(missing_tables)}")
            return False
        else:
            print("✅ Todas las tablas principales encontradas")

        conn.close()
        print("\n🎉 Configuración de TimescaleDB completada exitosamente!")
        print("\n🚀 Puedes empezar a usar el análisis con base de datos:")
        print("   uv run src/main.py --video-path 'video.mp4' "
              "--model-path 'model.pt' --enable-zones 'config.json' "
              "--enable-database")

        return True

    except psycopg2.Error as e:
        print(f"❌ Error de conexión a base de datos: {e}")
        print("\n💡 Sugerencias:")
        print("   • Verificar que Docker esté corriendo: docker-compose ps")
        print("   • Verificar logs: docker-compose logs timescaledb")
        print("   • Verificar configuración en .env")
        return False

    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
