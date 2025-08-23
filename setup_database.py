#!/usr/bin/env python3
"""
Script para configurar e inicializar la base de datos PostgreSQL.
Ejecuta el esquema de base de datos y crea las tablas necesarias.
"""

import os
import sys
import logging
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from database.connection import initialize_database, get_db_manager
from database.models import AnalysisConfig

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_database():
    """Configurar e inicializar la base de datos."""
    logger.info("🚀 Iniciando configuración de base de datos...")
    
    # Verificar variables de entorno
    required_vars = ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"❌ Variables de entorno faltantes: {', '.join(missing_vars)}")
        logger.info("💡 Configura las siguientes variables de entorno:")
        logger.info("   export DB_HOST=localhost")
        logger.info("   export DB_NAME=video_analysis")
        logger.info("   export DB_USER=postgres")
        logger.info("   export DB_PASSWORD=tu_password")
        return False
    
    try:
        # Inicializar base de datos
        logger.info("📊 Inicializando base de datos...")
        success = initialize_database()
        
        if success:
            logger.info("✅ Base de datos inicializada correctamente")
            
            # Probar conexión
            manager = get_db_manager()
            if manager.test_connection():
                logger.info("✅ Conexión a base de datos verificada")
                return True
            else:
                logger.error("❌ No se pudo verificar la conexión")
                return False
        else:
            logger.error("❌ Error al inicializar la base de datos")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error durante la configuración: {e}")
        return False


def test_database_operations():
    """Probar operaciones básicas de la base de datos."""
    logger.info("🧪 Probando operaciones de base de datos...")
    
    try:
        from database.service import get_video_service
        
        service = get_video_service()
        
        # Probar creación de configuración
        config = AnalysisConfig(
            classes=["person"],
            conf_threshold=0.25,
            enable_stats=True,
            enable_zones="configs/zonas.json",
            save_video=True,
            show_video=False
        )
        
        logger.info("✅ Configuración de análisis creada correctamente")
        logger.info(f"   Configuración: {config.dict()}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en pruebas de operaciones: {e}")
        return False


def main():
    """Función principal del script."""
    logger.info("=" * 60)
    logger.info("🎯 CONFIGURADOR DE BASE DE DATOS - FASE 9")
    logger.info("=" * 60)
    
    # Configurar base de datos
    if not setup_database():
        logger.error("❌ Falló la configuración de la base de datos")
        sys.exit(1)
    
    # Probar operaciones
    if not test_database_operations():
        logger.error("❌ Fallaron las pruebas de operaciones")
        sys.exit(1)
    
    logger.info("=" * 60)
    logger.info("🎉 ¡Base de datos configurada exitosamente!")
    logger.info("=" * 60)
    logger.info("📋 Próximos pasos:")
    logger.info("   1. Ejecutar análisis de video con: uv run src/main.py process")
    logger.info("   2. Los datos se guardarán automáticamente en la base de datos")
    logger.info("   3. Consultar datos con las funciones del módulo database")


if __name__ == "__main__":
    main()
