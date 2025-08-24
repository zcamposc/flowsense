#!/usr/bin/env python3
"""
Script para configurar la base de datos PostgreSQL para la FASE 9.
Crea el esquema completo y las tablas necesarias para análisis de video.
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from typing import Optional, Dict, Any
import json
from pathlib import Path

# Cargar variables de entorno desde .env
try:
    from dotenv import load_dotenv
    
    # Buscar archivo .env en el directorio raíz del proyecto
    project_root = Path(__file__).parent
    env_path = project_root / ".env"
    
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Archivo .env cargado desde: {env_path}")
    else:
        print(f"⚠️  Archivo .env no encontrado en: {env_path}")
        print("💡 Crea un archivo .env basado en env.example")
        
except ImportError:
    print("⚠️  python-dotenv no instalado. Usando variables de entorno del sistema")

# Configuración de la base de datos
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'video_analysis')
}


def test_connection() -> bool:
    """Prueba la conexión a PostgreSQL."""
    try:
        # Intentar conectar sin especificar base de datos
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        conn.close()
        print("✅ Conexión a PostgreSQL exitosa")
        return True
    except Exception as e:
        print(f"❌ Error de conexión a PostgreSQL: {e}")
        return False


def create_database() -> bool:
    """Crea la base de datos si no existe."""
    try:
        # Conectar a PostgreSQL sin especificar base de datos
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Verificar si la base de datos existe
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_CONFIG['database'],))
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f"CREATE DATABASE {DB_CONFIG['database']}")
            print(f"✅ Base de datos '{DB_CONFIG['database']}' creada")
        else:
            print(f"ℹ️  Base de datos '{DB_CONFIG['database']}' ya existe")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error al crear base de datos: {e}")
        return False


def execute_sql_file(cursor, sql_file: str) -> bool:
    """Ejecuta un archivo SQL."""
    try:
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Dividir por punto y coma para ejecutar cada comando por separado
        commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip()]
        
        for command in commands:
            if command and not command.startswith('--'):
                cursor.execute(command)
        
        print(f"✅ Archivo SQL ejecutado: {sql_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error al ejecutar {sql_file}: {e}")
        return False


def setup_schema() -> bool:
    """Configura el esquema de la base de datos."""
    try:
        # Conectar a la base de datos específica
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database']
        )
        cursor = conn.cursor()
        
        # Ejecutar el esquema SQL
        schema_file = 'database_schema.sql'
        if os.path.exists(schema_file):
            success = execute_sql_file(cursor, schema_file)
            if success:
                conn.commit()
                print("✅ Esquema de base de datos configurado correctamente")
            else:
                conn.rollback()
                print("❌ Error al configurar el esquema")
                return False
        else:
            print(f"❌ Archivo de esquema no encontrado: {schema_file}")
            return False
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error al configurar esquema: {e}")
        return False


def verify_tables() -> bool:
    """Verifica que todas las tablas se hayan creado correctamente."""
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database']
        )
        cursor = conn.cursor()
        
        # Listar todas las tablas
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        expected_tables = [
            'video_analyses',
            'zones', 
            'frame_detections',
            'zone_events',
            'line_crossing_events',
            'minute_statistics'
        ]
        
        print("\n📊 TABLAS CREADAS:")
        for table in expected_tables:
            if table in tables:
                print(f"   ✅ {table}")
            else:
                print(f"   ❌ {table} (FALTANTE)")
        
        # Verificar vistas
        cursor.execute("""
            SELECT viewname 
            FROM pg_views 
            WHERE schemaname = 'public'
            ORDER BY viewname
        """)
        
        views = [row[0] for row in cursor.fetchall()]
        expected_views = ['analysis_summary', 'unique_tracks_per_analysis']
        
        print("\n👁️  VISTAS CREADAS:")
        for view in expected_views:
            if view in views:
                print(f"   ✅ {view}")
            else:
                print(f"   ❌ {view} (FALTANTE)")
        
        cursor.close()
        conn.close()
        
        missing_tables = [t for t in expected_tables if t not in tables]
        missing_views = [v for v in expected_views if v not in views]
        
        return len(missing_tables) == 0 and len(missing_views) == 0
        
    except Exception as e:
        print(f"❌ Error al verificar tablas: {e}")
        return False


def create_sample_data() -> bool:
    """Crea algunos datos de ejemplo para probar la base de datos."""
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database']
        )
        cursor = conn.cursor()
        
        # Insertar análisis de ejemplo
        cursor.execute("""
            INSERT INTO video_analyses (video_path, model_name, analysis_config, status, total_frames, fps)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            'data/videos/sample_video.mp4',
            'yolov8n.pt',
            json.dumps({'classes': ['person'], 'conf_threshold': 0.25}),
            'completed',
            1500,
            30.0
        ))
        
        analysis_id = cursor.fetchone()[0]
        print(f"✅ Análisis de ejemplo creado con ID: {analysis_id}")
        
        # Insertar zona de ejemplo
        cursor.execute("""
            INSERT INTO zones (video_analysis_id, zone_name, zone_type, coordinates)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (
            analysis_id,
            'entrada_principal',
            'polygon',
            json.dumps([[100, 100], [300, 100], [300, 300], [100, 300]])
        ))
        
        zone_id = cursor.fetchone()[0]
        print(f"✅ Zona de ejemplo creada con ID: {zone_id}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Datos de ejemplo creados correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error al crear datos de ejemplo: {e}")
        return False


def main():
    """Función principal de configuración."""
    print("🚀 CONFIGURACIÓN DE BASE DE DATOS - FASE 9")
    print("=" * 50)
    
    # Verificar variables de entorno
    print("\n🔧 CONFIGURACIÓN:")
    for key, value in DB_CONFIG.items():
        if key == 'password':
            masked_value = '*' * len(value) if value else 'NO CONFIGURADA'
            print(f"   • {key}: {masked_value}")
        else:
            print(f"   • {key}: {value}")
    
    # Verificar archivo .env
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        print(f"\n📁 Archivo .env encontrado: {env_file}")
    else:
        print(f"\n⚠️  Archivo .env no encontrado")
        print("💡 Crea un archivo .env basado en env.example:")
        print("   cp env.example .env")
        print("   nano .env")
    
    # Paso 1: Probar conexión
    print("\n📡 PASO 1: Probando conexión a PostgreSQL...")
    if not test_connection():
        print("\n💡 SOLUCIÓN:")
        print("   1. Asegúrate de que PostgreSQL esté instalado y ejecutándose")
        print("   2. Configura las variables en tu archivo .env")
        print("   3. O usa variables de entorno del sistema")
        return False
    
    # Paso 2: Crear base de datos
    print("\n🗄️  PASO 2: Creando base de datos...")
    if not create_database():
        return False
    
    # Paso 3: Configurar esquema
    print("\n🏗️  PASO 3: Configurando esquema...")
    if not setup_schema():
        return False
    
    # Paso 4: Verificar tablas
    print("\n✅ PASO 4: Verificando tablas...")
    if not verify_tables():
        return False
    
    # Paso 5: Crear datos de ejemplo (opcional)
    print("\n📝 PASO 5: Creando datos de ejemplo...")
    create_sample_data()
    
    print("\n🎉 ¡CONFIGURACIÓN COMPLETADA!")
    print("\n💡 PRÓXIMOS PASOS:")
    print("   1. La base de datos está lista para usar")
    print("   2. Puedes integrar el módulo de base de datos en tu código")
    print("   3. Usa --enable-database para activar la funcionalidad")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
