#!/usr/bin/env python3
"""
Script de prueba para verificar la funcionalidad de la base de datos.
"""

import os
import sys
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

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_database_connection():
    """Prueba la conexión a la base de datos."""
    print("🧪 PROBANDO CONEXIÓN A BASE DE DATOS")
    print("=" * 50)
    
    try:
        from database.connection import initialize_database
        success = initialize_database()
        
        if success:
            print("✅ Conexión a base de datos exitosa")
            return True
        else:
            print("❌ No se pudo conectar a la base de datos")
            return False
            
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("💡 Asegúrate de que las dependencias estén instaladas:")
        print("   uv add psycopg2-binary pydantic python-dotenv")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False


def test_database_service():
    """Prueba el servicio de base de datos."""
    print("\n🧪 PROBANDO SERVICIO DE BASE DE DATOS")
    print("=" * 50)
    
    try:
        from database.service import get_video_service
        from database.models import AnalysisConfig
        
        service = get_video_service()
        print("✅ Servicio de base de datos creado")
        
        # Probar configuración
        config = AnalysisConfig(
            classes=["person"],
            conf_threshold=0.25,
            enable_stats=True,
            enable_zones="configs/zonas.json"
        )
        print("✅ Configuración de análisis creada")
        
        # Probar inicio de análisis
        analysis_id = service.start_analysis(
            video_path="data/videos/test_video.mp4",
            model_name="yolov8n.pt",
            config=config
        )
        print(f"✅ Análisis iniciado con ID: {analysis_id}")
        
        # Probar agregar zona
        zone_id = service.add_zone(
            zone_name="zona_prueba",
            zone_type="polygon",
            coordinates=[[100, 100], [300, 100], [300, 300], [100, 300]]
        )
        print(f"✅ Zona agregada con ID: {zone_id}")
        
        # Probar guardar detección
        success = service.save_frame_detection(
            frame_number=1,
            timestamp_ms=1000,
            track_id=42,
            class_name="person",
            confidence=0.95,
            bbox=[100, 200, 150, 300],
            center=[125, 250]
        )
        print(f"✅ Detección guardada: {success}")
        
        # Probar guardar evento de zona
        success = service.save_zone_event(
            zone_id=zone_id,
            track_id=42,
            event_type="enter",
            frame_number=1,
            timestamp_ms=1000,
            position=[125, 250],
            class_name="person",
            confidence=0.95
        )
        print(f"✅ Evento de zona guardado: {success}")
        
        # Completar análisis
        success = service.complete_analysis(
            total_frames=100,
            fps=30.0,
            width=1920,
            height=1080
        )
        print(f"✅ Análisis completado: {success}")
        
        # Obtener resumen
        summary = service.get_analysis_summary()
        if summary:
            print(f"✅ Resumen obtenido: {summary['total_detections']} detecciones")
        
        # Cerrar servicio
        service.close()
        print("✅ Servicio cerrado correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba de servicio: {e}")
        return False


def main():
    """Función principal de pruebas."""
    print("🚀 PRUEBAS DE BASE DE DATOS - FASE 9")
    print("=" * 60)
    
    # Verificar archivo .env
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        print(f"📁 Archivo .env encontrado: {env_file}")
    else:
        print("⚠️  Archivo .env no encontrado")
        print("💡 Crea un archivo .env basado en env.example:")
        print("   cp env.example .env")
        print("   nano .env")
    
    # Verificar variables de entorno
    print("\n🔧 CONFIGURACIÓN:")
    db_vars = ['DB_HOST', 'DB_PORT', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']
    for var in db_vars:
        value = os.getenv(var, 'NO CONFIGURADA')
        if var == 'DB_PASSWORD':
            masked_value = '*' * len(value) if value != 'NO CONFIGURADA' else value
            print(f"   • {var}: {masked_value}")
        else:
            print(f"   • {var}: {value}")
    
    # Prueba 1: Conexión
    print("\n📡 PASO 1: Probando conexión a PostgreSQL...")
    if not test_database_connection():
        print("\n💡 SOLUCIÓN:")
        print("   1. Asegúrate de que PostgreSQL esté instalado y ejecutándose")
        print("   2. Configura las variables en tu archivo .env")
        print("   3. O usa variables de entorno del sistema")
        print("   4. Ejecuta: python setup_database.py")
        return False
    
    # Prueba 2: Servicio
    print("\n🧪 PASO 2: Probando servicio de base de datos...")
    if not test_database_service():
        print("\n💡 SOLUCIÓN:")
        print("   1. Verifica que la base de datos esté configurada correctamente")
        print("   2. Ejecuta: python setup_database.py")
        return False
    
    print("\n🎉 ¡TODAS LAS PRUEBAS PASARON!")
    print("\n💡 La base de datos está lista para usar con:")
    print("   uv run src/main.py --enable-database")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
