"""
Módulo de conexión a la base de datos PostgreSQL.
Maneja la conexión y configuración de la base de datos.
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, Dict, Any
import logging
from pathlib import Path

# Cargar variables de entorno desde .env
try:
    from dotenv import load_dotenv
    
    # Buscar archivo .env en el directorio raíz del proyecto
    project_root = Path(__file__).parent.parent.parent
    env_path = project_root / ".env"
    
    if env_path.exists():
        load_dotenv(env_path)
        logger = logging.getLogger(__name__)
        logger.info(f"✅ Archivo .env cargado desde: {env_path}")
    else:
        logger = logging.getLogger(__name__)
        logger.warning(f"⚠️  Archivo .env no encontrado en: {env_path}")
        logger.info("💡 Crea un archivo .env basado en env.example")
        
except ImportError:
    logger = logging.getLogger(__name__)
    logger.warning("⚠️  python-dotenv no instalado. Usando variables de entorno del sistema")


class DatabaseConnection:
    """Maneja la conexión a la base de datos PostgreSQL."""
    
    def __init__(self):
        """Inicializa la conexión a la base de datos."""
        self.connection = None
        self.config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', ''),
            'database': os.getenv('DB_NAME', 'video_analysis')
        }
        
        # Log de configuración (sin mostrar password)
        safe_config = self.config.copy()
        safe_config['password'] = '*' * len(self.config['password']) if self.config['password'] else 'NO CONFIGURADA'
        logger.info(f"🔧 Configuración de BD: {safe_config}")
    
    def connect(self) -> bool:
        """Establece conexión a la base de datos."""
        try:
            self.connection = psycopg2.connect(
                host=self.config['host'],
                port=self.config['port'],
                user=self.config['user'],
                password=self.config['password'],
                database=self.config['database']
            )
            logger.info("✅ Conexión a base de datos establecida")
            return True
        except Exception as e:
            logger.error(f"❌ Error al conectar a la base de datos: {e}")
            return False
    
    def disconnect(self):
        """Cierra la conexión a la base de datos."""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("🔌 Conexión a base de datos cerrada")
    
    def get_cursor(self, dict_cursor: bool = True):
        """Obtiene un cursor para ejecutar consultas."""
        if not self.connection or self.connection.closed:
            if not self.connect():
                return None
        
        if dict_cursor:
            return self.connection.cursor(cursor_factory=RealDictCursor)
        return self.connection.cursor()
    
    def commit(self):
        """Confirma los cambios en la base de datos."""
        if self.connection and not self.connection.closed:
            self.connection.commit()
    
    def rollback(self):
        """Revierte los cambios en la base de datos."""
        if self.connection and not self.connection.closed:
            self.connection.rollback()
    
    def test_connection(self) -> bool:
        """Prueba la conexión a la base de datos."""
        try:
            cursor = self.get_cursor(dict_cursor=False)
            if cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                cursor.close()
                return result[0] == 1
            return False
        except Exception as e:
            logger.error(f"❌ Error en prueba de conexión: {e}")
            return False
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


# Instancia global de conexión
_db_connection = None


def get_db_connection() -> DatabaseConnection:
    """Obtiene la instancia global de conexión a la base de datos."""
    global _db_connection
    if _db_connection is None:
        _db_connection = DatabaseConnection()
    return _db_connection


def initialize_database() -> bool:
    """Inicializa la base de datos."""
    try:
        connection = get_db_connection()
        return connection.test_connection()
    except Exception as e:
        logger.error(f"❌ Error al inicializar base de datos: {e}")
        return False


def get_database_info() -> Dict[str, str]:
    """Obtiene información de configuración de la base de datos."""
    connection = get_db_connection()
    safe_config = connection.config.copy()
    safe_config['password'] = '*' * len(connection.config['password']) if connection.config['password'] else 'NO CONFIGURADA'
    return safe_config
