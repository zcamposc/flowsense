"""
Módulo de conexión a PostgreSQL para el sistema de series de tiempo.
"""

import os
import logging
from typing import Optional
from contextlib import contextmanager
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Configuración de la base de datos PostgreSQL."""
    
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = int(os.getenv('DB_PORT', '5432'))
        self.database = os.getenv('DB_NAME', 'video_analysis')
        self.user = os.getenv('DB_USER', 'postgres')
        self.password = os.getenv('DB_PASSWORD', '')
        self.min_connections = int(os.getenv('DB_MIN_CONNECTIONS', '1'))
        self.max_connections = int(os.getenv('DB_MAX_CONNECTIONS', '10'))
    
    def get_connection_string(self) -> str:
        """Obtener string de conexión para PostgreSQL."""
        return (
            f"host={self.host} "
            f"port={self.port} "
            f"dbname={self.database} "
            f"user={self.user} "
            f"password={self.password}"
        )


class DatabaseManager:
    """Gestor de conexiones a la base de datos."""
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        self.config = config or DatabaseConfig()
        self.pool: Optional[SimpleConnectionPool] = None
        self._initialize_pool()
    
    def _initialize_pool(self) -> None:
        """Inicializar el pool de conexiones."""
        try:
            self.pool = SimpleConnectionPool(
                minconn=self.config.min_connections,
                maxconn=self.config.max_connections,
                dsn=self.config.get_connection_string()
            )
            logger.info("Pool de conexiones inicializado correctamente")
        except Exception as e:
            logger.error(f"Error al inicializar pool de conexiones: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Obtener conexión del pool con manejo automático."""
        conn = None
        try:
            conn = self.pool.getconn()
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Error en conexión de base de datos: {e}")
            raise
        finally:
            if conn:
                self.pool.putconn(conn)
    
    @contextmanager
    def get_cursor(self, commit: bool = True):
        """Obtener cursor con manejo automático de transacciones."""
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            try:
                yield cursor
                if commit:
                    conn.commit()
            except Exception as e:
                conn.rollback()
                logger.error(f"Error en cursor de base de datos: {e}")
                raise
            finally:
                cursor.close()
    
    def test_connection(self) -> bool:
        """Probar la conexión a la base de datos."""
        try:
            with self.get_cursor(commit=False) as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return result is not None
        except Exception as e:
            logger.error(f"Error al probar conexión: {e}")
            return False
    
    def close(self) -> None:
        """Cerrar el pool de conexiones."""
        if self.pool:
            self.pool.closeall()
            logger.info("Pool de conexiones cerrado")


# Instancia global del gestor de base de datos
db_manager: Optional[DatabaseManager] = None


def get_db_manager() -> DatabaseManager:
    """Obtener la instancia global del gestor de base de datos."""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
    return db_manager


def initialize_database() -> bool:
    """Inicializar la base de datos y crear tablas si no existen."""
    try:
        manager = get_db_manager()
        
        if not manager.test_connection():
            logger.error("No se pudo conectar a la base de datos")
            return False
        
        # Crear tablas si no existen
        with manager.get_cursor() as cursor:
            # Leer y ejecutar el esquema SQL
            schema_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'database_schema.sql'
            )
            
            if os.path.exists(schema_path):
                with open(schema_path, 'r', encoding='utf-8') as f:
                    schema_sql = f.read()
                
                # Ejecutar el esquema
                cursor.execute(schema_sql)
                logger.info("Esquema de base de datos creado/actualizado")
            else:
                logger.warning("Archivo de esquema no encontrado")
        
        return True
        
    except Exception as e:
        logger.error(f"Error al inicializar base de datos: {e}")
        return False


def close_database() -> None:
    """Cerrar la conexión a la base de datos."""
    global db_manager
    if db_manager:
        db_manager.close()
        db_manager = None
        logger.info("Conexión a base de datos cerrada")


# Función de utilidad para ejecutar consultas
def execute_query(query: str, params: Optional[tuple] = None) -> list:
    """Ejecutar una consulta y retornar resultados."""
    manager = get_db_manager()
    with manager.get_cursor() as cursor:
        cursor.execute(query, params)
        return cursor.fetchall()


def execute_command(command: str, params: Optional[tuple] = None) -> int:
    """Ejecutar un comando (INSERT, UPDATE, DELETE) y retornar filas afectadas."""
    manager = get_db_manager()
    with manager.get_cursor() as cursor:
        cursor.execute(command, params)
        return cursor.rowcount
