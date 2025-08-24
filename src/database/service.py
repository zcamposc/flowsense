"""
Servicio principal de base de datos para análisis de video.
Maneja todas las operaciones CRUD y consultas de la base de datos.
"""

import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID

from .connection import get_db_connection
from .models import (
    VideoAnalysis, AnalysisConfig, Zone,
    ZoneEvent, LineCrossingEvent
)

# Configurar logging
logger = logging.getLogger(__name__)


class VideoAnalysisService:
    """Servicio para manejar análisis de video en TimescaleDB."""
    
    def __init__(self):
        """Inicializa el servicio de base de datos."""
        self.db = get_db_connection()
        self.current_analysis_id: Optional[UUID] = None
        self.analysis_start_time: Optional[datetime] = None
    
    def start_analysis(self, video_path: str, model_name: str, 
                      config: Optional[AnalysisConfig] = None) -> UUID:
        """Inicia un nuevo análisis de video."""
        try:
            cursor = self.db.get_cursor()
            if not cursor:
                raise Exception("No se pudo obtener cursor de base de datos")
            
            start_time = datetime.now()
            analysis = VideoAnalysis(
                video_path=video_path,
                model_name=model_name,
                analysis_config=config,
                status="running",
                started_at=start_time
            )
            
            # Almacenar el timestamp de inicio para usar en las detecciones
            self.analysis_start_time = start_time
            
            cursor.execute("""
                INSERT INTO video_analyses (
                    video_path, model_name, analysis_config, status, started_at
                ) VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (
                analysis.video_path,
                analysis.model_name,
                json.dumps(analysis.analysis_config.dict()) if analysis.analysis_config else None,
                analysis.status,
                analysis.started_at
            ))
            
            result = cursor.fetchone()
            logger.info(f"DEBUG: fetchone() result type: {type(result)}")
            logger.info(f"DEBUG: fetchone() result: {result}")
            if isinstance(result, dict):
                analysis_id = result.get('id')
            else:
                analysis_id = result[0] if result else None
            if not analysis_id:
                raise Exception("No se pudo obtener ID del análisis")
            self.current_analysis_id = analysis_id
            
            self.db.commit()
            logger.info(f"✅ Análisis iniciado con ID: {analysis_id}")
            
            return analysis_id
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Error al iniciar análisis: {e}")
            raise
    
    def complete_analysis(self, total_frames: int, fps: float, 
                         width: int, height: int) -> bool:
        """Completa un análisis de video."""
        if not self.current_analysis_id:
            logger.error("❌ No hay análisis activo")
            return False
        
        try:
            cursor = self.db.get_cursor()
            if not cursor:
                raise Exception("No se pudo obtener cursor de base de datos")
            
            cursor.execute("""
                UPDATE video_analyses 
                SET status = 'completed', 
                    total_frames = %s,
                    fps = %s,
                    resolution_width = %s,
                    resolution_height = %s,
                    completed_at = %s
                WHERE id = %s
            """, (
                total_frames, fps, width, height, 
                datetime.now(), self.current_analysis_id
            ))
            
            self.db.commit()
            logger.info(f"✅ Análisis completado: {total_frames} frames")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Error al completar análisis: {e}")
            return False
    
    def add_zone(self, zone_name: str, zone_type: str, 
                 coordinates: List[List[float]]) -> Optional[UUID]:
        """Agrega una zona al análisis actual."""
        if not self.current_analysis_id:
            logger.error("❌ No hay análisis activo")
            return None
        
        try:
            logger.info(f"🔍 [DEBUG] Intentando agregar zona: {zone_name} ({zone_type})")
            logger.info(f"🔍 [DEBUG] video_analysis_id: {self.current_analysis_id}")
            logger.info(f"🔍 [DEBUG] coordinates: {coordinates}")
            
            cursor = self.db.get_cursor()
            if not cursor:
                raise Exception("No se pudo obtener cursor de base de datos")
            
            zone = Zone(
                video_analysis_id=self.current_analysis_id,
                zone_name=zone_name,
                zone_type=zone_type,
                coordinates=coordinates
            )
            
            logger.info(f"🔍 [DEBUG] Zone object created: {zone}")
            
            cursor.execute("""
                INSERT INTO zones (video_analysis_id, zone_name, zone_type, coordinates)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (
                str(zone.video_analysis_id) if zone.video_analysis_id else None,
                zone.zone_name,
                zone.zone_type,
                json.dumps(zone.coordinates)
            ))
            
            result = cursor.fetchone()
            logger.info(f"🔍 [DEBUG] fetchone result: {result}")
            if isinstance(result, dict):
                zone_id = result.get('id')
            else:
                zone_id = result[0] if result else None
            if not zone_id:
                raise Exception("No se pudo obtener ID de la zona")
            self.db.commit()
            
            logger.info(f"✅ Zona agregada: {zone_name} ({zone_type}) - ID: {zone_id}")
            return zone_id
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Error al agregar zona: {e}")
            return None
    
    def save_frame_detection(self, frame_number: int, timestamp_ms: int,
                           track_id: int, class_name: str, confidence: float,
                           bbox: List[int], center: List[int]) -> bool:
        """
        DEPRECATED: No guarda detecciones individuales para optimizar base de datos.
        Solo los eventos significativos (zone_events, line_crossing_events) se guardan.
        """
        # No hacer nada - tabla frame_detections eliminada para optimización
        logger.debug(f"🔄 Frame detection no guardada (optimización): frame {frame_number}, track {track_id}")
        return True
    
    def save_zone_event(self, zone_id: UUID, track_id: int, event_type: str,
                        class_name: str, confidence: float, 
                        position: List[int], timestamp_ms: int) -> bool:
        """Guarda un evento de zona."""
        if not self.current_analysis_id:
            logger.error("❌ No hay análisis activo")
            return False
        
        try:
            logger.info(f"�� [DEBUG] Intentando guardar evento de zona: {event_type} para track {track_id}")
            logger.info(f"🔍 [DEBUG] zone_id: {zone_id}, class_name: {class_name}")
            
            cursor = self.db.get_cursor()
            if not cursor:
                raise Exception("No se pudo obtener cursor de base de datos")
            
            # Crear instancia del modelo con timestamp de inicio
            event = ZoneEvent.from_event_data(
                video_analysis_id=self.current_analysis_id,
                zone_id=zone_id,
                track_id=track_id,
                event_type=event_type,
                class_name=class_name,
                confidence=confidence,
                position=position,
                timestamp_ms=timestamp_ms,
                analysis_start_time=self.analysis_start_time
            )
            
            logger.info(f"🔍 [DEBUG] ZoneEvent object created: {event}")
            
            cursor.execute("""
                INSERT INTO zone_events (
                    time, video_time_ms, video_analysis_id, zone_id, track_id, event_type,
                    class_name, confidence, position_x, position_y
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                event.time,
                event.video_time_ms,
                str(event.video_analysis_id) if event.video_analysis_id else None,
                str(event.zone_id) if event.zone_id else None,
                event.track_id,
                event.event_type,
                event.class_name,
                event.confidence,
                event.position_x,
                event.position_y
            ))
            
            self.db.commit()
            logger.info(f"✅ Evento de zona guardado: {event_type} para track {track_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Error al guardar evento de zona: {e}")
            return False
    
    def save_line_crossing(self, zone_id: UUID, track_id: int, direction: str,
                           class_name: str, confidence: float, 
                           position: List[int], timestamp_ms: int) -> bool:
        """Guarda un cruce de línea."""
        if not self.current_analysis_id:
            logger.error("❌ No hay análisis activo")
            return False
        
        try:
            logger.info(f"🔍 [DEBUG] Intentando guardar cruce de línea: {direction} para track {track_id}")
            logger.info(f"🔍 [DEBUG] zone_id: {zone_id}, class_name: {class_name}")
            
            cursor = self.db.get_cursor()
            if not cursor:
                raise Exception("No se pudo obtener cursor de base de datos")
            
            # Crear instancia del modelo usando el método correcto con timestamp de inicio
            event = LineCrossingEvent.from_event_data(
                video_analysis_id=self.current_analysis_id,
                zone_id=zone_id,
                timestamp_ms=timestamp_ms,
                track_id=track_id,
                direction=direction,
                class_name=class_name,
                confidence=confidence,
                position=position,
                analysis_start_time=self.analysis_start_time
            )
            
            logger.info(f"🔍 [DEBUG] LineCrossingEvent object created: {event}")
            
            # Consulta SQL ajustada para el esquema de TimescaleDB
            cursor.execute("""
                INSERT INTO line_crossing_events (
                    time, video_time_ms, video_analysis_id, zone_id, track_id, direction,
                    class_name, confidence, position_x, position_y
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                event.time,
                event.video_time_ms,
                str(event.video_analysis_id) if event.video_analysis_id else None,
                str(event.zone_id) if event.zone_id else None,
                event.track_id,
                event.direction,
                event.class_name,
                event.confidence,
                event.position_x,
                event.position_y
            ))
            
            self.db.commit()
            logger.info(f"✅ Cruce de línea guardado: {direction} para track {track_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Error al guardar cruce de línea: {e}")
            return False
    
    def get_zone_id_by_name(self, zone_name: str) -> Optional[UUID]:
        """Obtiene el ID de una zona por su nombre."""
        if not self.current_analysis_id:
            logger.error("❌ No hay análisis activo")
            return None
        
        try:
            cursor = self.db.get_cursor()
            if not cursor:
                raise Exception("No se pudo obtener cursor de base de datos")
            
            cursor.execute("""
                SELECT id FROM zones 
                WHERE video_analysis_id = %s AND zone_name = %s
            """, (self.current_analysis_id, zone_name))
            
            result = cursor.fetchone()
            if result:
                return result['id']
            return None
            
        except Exception as e:
            logger.error(f"❌ Error al obtener ID de zona '{zone_name}': {e}")
            return None
    
    def get_analysis_summary(self) -> Optional[Dict[str, Any]]:
        """Obtiene un resumen del análisis actual."""
        if not self.current_analysis_id:
            logger.error("❌ No hay análisis activo")
            return None
        
        try:
            cursor = self.db.get_cursor()
            if not cursor:
                raise Exception("No se pudo obtener cursor de base de datos")
            
            cursor.execute("""
                SELECT * FROM analysis_summary 
                WHERE id = %s
            """, (self.current_analysis_id,))
            
            result = cursor.fetchone()
            if result:
                return dict(result)
            return None
            
        except Exception as e:
            logger.error(f"❌ Error al obtener resumen: {e}")
            return None
    
    def close(self):
        """Cierra la conexión a la base de datos."""
        if self.db:
            self.db.disconnect()
            logger.info("🔌 Conexión a base de datos cerrada")


# Función de conveniencia para obtener el servicio
def get_video_service() -> VideoAnalysisService:
    """Obtiene una instancia del servicio de análisis de video."""
    return VideoAnalysisService()
