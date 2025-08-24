"""
Repositorio de datos para el sistema de series de tiempo.
Maneja todas las operaciones CRUD de la base de datos.
"""

import json
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

from .connection import get_db_manager
from .models import (
    VideoAnalysis, Zone, ZoneEvent, LineCrossingEvent, AnalysisConfig
)

logger = logging.getLogger(__name__)


class VideoAnalysisRepository:
    """Repositorio para operaciones de análisis de video."""
    
    @staticmethod
    def create_analysis(analysis: VideoAnalysis) -> Optional[UUID]:
        """Crear un nuevo análisis de video."""
        try:
            manager = get_db_manager()
            with manager.get_cursor() as cursor:
                query = """
                INSERT INTO video_analyses (
                    video_path, model_name, analysis_config, status,
                    total_frames, fps, resolution_width, resolution_height
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """
                cursor.execute(query, (
                    analysis.video_path,
                    analysis.model_name,
                    json.dumps(analysis.analysis_config),
                    analysis.status.value,
                    analysis.total_frames,
                    analysis.fps,
                    analysis.resolution_width,
                    analysis.resolution_height
                ))
                result = cursor.fetchone()
                return result['id'] if result else None
        except Exception as e:
            logger.error(f"Error al crear análisis: {e}")
            return None
    
    @staticmethod
    def update_analysis_status(analysis_id: UUID, status: str, 
                             completed_at: Optional[datetime] = None) -> bool:
        """Actualizar el estado de un análisis."""
        try:
            manager = get_db_manager()
            with manager.get_cursor() as cursor:
                query = """
                UPDATE video_analyses 
                SET status = %s, completed_at = %s
                WHERE id = %s
                """
                cursor.execute(query, (status, completed_at, analysis_id))
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error al actualizar estado: {e}")
            return False
    
    @staticmethod
    def get_analysis(analysis_id: UUID) -> Optional[VideoAnalysis]:
        """Obtener un análisis por ID."""
        try:
            manager = get_db_manager()
            with manager.get_cursor() as cursor:
                query = "SELECT * FROM video_analyses WHERE id = %s"
                cursor.execute(query, (analysis_id,))
                result = cursor.fetchone()
                
                if result:
                    return VideoAnalysis(
                        id=result['id'],
                        video_path=result['video_path'],
                        model_name=result['model_name'],
                        analysis_config=json.loads(result['analysis_config']),
                        status=result['status'],
                        created_at=result['created_at'],
                        completed_at=result['completed_at'],
                        total_frames=result['total_frames'],
                        fps=result['fps'],
                        resolution_width=result['resolution_width'],
                        resolution_height=result['resolution_height']
                    )
                return None
        except Exception as e:
            logger.error(f"Error al obtener análisis: {e}")
            return None


class ZoneRepository:
    """Repositorio para operaciones de zonas."""
    
    @staticmethod
    def create_zone(zone: Zone) -> Optional[UUID]:
        """Crear una nueva zona."""
        try:
            manager = get_db_manager()
            with manager.get_cursor() as cursor:
                query = """
                INSERT INTO zones (
                    video_analysis_id, zone_name, zone_type, coordinates
                ) VALUES (%s, %s, %s, %s)
                RETURNING id
                """
                cursor.execute(query, (
                    zone.video_analysis_id,
                    zone.zone_name,
                    zone.zone_type.value,
                    json.dumps(zone.coordinates)
                ))
                result = cursor.fetchone()
                return result['id'] if result else None
        except Exception as e:
            logger.error(f"Error al crear zona: {e}")
            return None
    
    @staticmethod
    def get_zones_by_analysis(analysis_id: UUID) -> List[Zone]:
        """Obtener todas las zonas de un análisis."""
        try:
            manager = get_db_manager()
            with manager.get_cursor() as cursor:
                query = "SELECT * FROM zones WHERE video_analysis_id = %s"
                cursor.execute(query, (analysis_id,))
                results = cursor.fetchall()
                
                zones = []
                for result in results:
                    zones.append(Zone(
                        id=result['id'],
                        video_analysis_id=result['video_analysis_id'],
                        zone_name=result['zone_name'],
                        zone_type=result['zone_type'],
                        coordinates=json.loads(result['coordinates']),
                        created_at=result['created_at']
                    ))
                return zones
        except Exception as e:
            logger.error(f"Error al obtener zonas: {e}")
            return []


class FrameDetectionRepository:
    """Repositorio para operaciones de detecciones por frame."""
    
    @staticmethod
    def create_detection(detection: FrameDetection) -> Optional[UUID]:
        """Crear una nueva detección."""
        try:
            manager = get_db_manager()
            with manager.get_cursor() as cursor:
                query = """
                INSERT INTO frame_detections (
                    video_analysis_id, frame_number, timestamp_ms, track_id,
                    class_name, confidence, bbox_x1, bbox_y1, bbox_x2, bbox_y2,
                    center_x, center_y
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """
                cursor.execute(query, (
                    detection.video_analysis_id,
                    detection.frame_number,
                    detection.timestamp_ms,
                    detection.track_id,
                    detection.class_name,
                    detection.confidence,
                    detection.bbox_x1,
                    detection.bbox_y1,
                    detection.bbox_x2,
                    detection.bbox_y2,
                    detection.center_x,
                    detection.center_y
                ))
                result = cursor.fetchone()
                return result['id'] if result else None
        except Exception as e:
            logger.error(f"Error al crear detección: {e}")
            return None
    
    @staticmethod
    def create_bulk_detections(detections: List[FrameDetection]) -> int:
        """Crear múltiples detecciones en lote."""
        if not detections:
            return 0
        
        try:
            manager = get_db_manager()
            with manager.get_cursor() as cursor:
                query = """
                INSERT INTO frame_detections (
                    video_analysis_id, frame_number, timestamp_ms, track_id,
                    class_name, confidence, bbox_x1, bbox_y1, bbox_x2, bbox_y2,
                    center_x, center_y
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (video_analysis_id, frame_number, track_id) 
                DO NOTHING
                """
                
                values = []
                for detection in detections:
                    values.append((
                        detection.video_analysis_id,
                        detection.frame_number,
                        detection.timestamp_ms,
                        detection.track_id,
                        detection.class_name,
                        detection.confidence,
                        detection.bbox_x1,
                        detection.bbox_y1,
                        detection.bbox_x2,
                        detection.bbox_y2,
                        detection.center_x,
                        detection.center_y
                    ))
                
                cursor.executemany(query, values)
                return cursor.rowcount
        except Exception as e:
            logger.error(f"Error al crear detecciones en lote: {e}")
            return 0


class ZoneEventRepository:
    """Repositorio para operaciones de eventos de zona."""
    
    @staticmethod
    def create_zone_event(event: ZoneEvent) -> Optional[UUID]:
        """Crear un nuevo evento de zona."""
        try:
            manager = get_db_manager()
            with manager.get_cursor() as cursor:
                query = """
                INSERT INTO zone_events (
                    video_analysis_id, zone_id, track_id, event_type,
                    frame_number, timestamp_ms, position_x, position_y
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """
                cursor.execute(query, (
                    event.video_analysis_id,
                    event.zone_id,
                    event.track_id,
                    event.event_type.value,
                    event.frame_number,
                    event.timestamp_ms,
                    event.position_x,
                    event.position_y
                ))
                result = cursor.fetchone()
                return result['id'] if result else None
        except Exception as e:
            logger.error(f"Error al crear evento de zona: {e}")
            return None
    
    @staticmethod
    def get_zone_events(analysis_id: UUID, zone_id: Optional[UUID] = None,
                       track_id: Optional[int] = None) -> List[ZoneEvent]:
        """Obtener eventos de zona con filtros opcionales."""
        try:
            manager = get_db_manager()
            with manager.get_cursor() as cursor:
                query = "SELECT * FROM zone_events WHERE video_analysis_id = %s"
                params = [analysis_id]
                
                if zone_id:
                    query += " AND zone_id = %s"
                    params.append(zone_id)
                
                if track_id:
                    query += " AND track_id = %s"
                    params.append(track_id)
                
                query += " ORDER BY timestamp_ms"
                cursor.execute(query, tuple(params))
                results = cursor.fetchall()
                
                events = []
                for result in results:
                    events.append(ZoneEvent(
                        id=result['id'],
                        video_analysis_id=result['video_analysis_id'],
                        zone_id=result['zone_id'],
                        track_id=result['track_id'],
                        event_type=result['event_type'],
                        frame_number=result['frame_number'],
                        timestamp_ms=result['timestamp_ms'],
                        position_x=result['position_x'],
                        position_y=result['position_y'],
                        created_at=result['created_at']
                    ))
                return events
        except Exception as e:
            logger.error(f"Error al obtener eventos de zona: {e}")
            return []


class LineCrossingRepository:
    """Repositorio para operaciones de cruces de línea."""
    
    @staticmethod
    def create_line_crossing(event: LineCrossingEvent) -> Optional[UUID]:
        """Crear un nuevo evento de cruce de línea."""
        try:
            manager = get_db_manager()
            with manager.get_cursor() as cursor:
                query = """
                INSERT INTO line_crossing_events (
                    video_analysis_id, zone_id, track_id, direction,
                    frame_number, timestamp_ms, position_x, position_y
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """
                cursor.execute(query, (
                    event.video_analysis_id,
                    event.zone_id,
                    event.track_id,
                    event.direction.value,
                    event.frame_number,
                    event.timestamp_ms,
                    event.position_x,
                    event.position_y
                ))
                result = cursor.fetchone()
                return result['id'] if result else None
        except Exception as e:
            logger.error(f"Error al crear cruce de línea: {e}")
            return None
    
    @staticmethod
    def get_line_crossings(analysis_id: UUID, zone_id: Optional[UUID] = None,
                          track_id: Optional[int] = None) -> List[LineCrossingEvent]:
        """Obtener cruces de línea con filtros opcionales."""
        try:
            manager = get_db_manager()
            with manager.get_cursor() as cursor:
                query = "SELECT * FROM line_crossing_events WHERE video_analysis_id = %s"
                params = [analysis_id]
                
                if zone_id:
                    query += " AND zone_id = %s"
                    params.append(zone_id)
                
                if track_id:
                    query += " AND track_id = %s"
                    params.append(track_id)
                
                query += " ORDER BY timestamp_ms"
                cursor.execute(query, tuple(params))
                results = cursor.fetchall()
                
                events = []
                for result in results:
                    events.append(LineCrossingEvent(
                        id=result['id'],
                        video_analysis_id=result['video_analysis_id'],
                        zone_id=result['zone_id'],
                        track_id=result['track_id'],
                        direction=result['direction'],
                        frame_number=result['frame_number'],
                        timestamp_ms=result['timestamp_ms'],
                        position_x=result['position_x'],
                        position_y=result['position_y'],
                        created_at=result['created_at']
                    ))
                return events
        except Exception as e:
            logger.error(f"Error al obtener cruces de línea: {e}")
            return []


class StatisticsRepository:
    """Repositorio para operaciones de estadísticas."""
    
    @staticmethod
    def get_analysis_summary(analysis_id: UUID) -> Optional[Dict[str, Any]]:
        """Obtener resumen de estadísticas de un análisis."""
        try:
            manager = get_db_manager()
            with manager.get_cursor() as cursor:
                query = """
                SELECT 
                    va.video_path,
                    va.model_name,
                    va.status,
                    va.total_frames,
                    va.fps,
                    COUNT(DISTINCT ze.track_id) as total_unique_tracks,
                    COUNT(ze.id) as total_zone_events,
                    COUNT(lce.id) as total_line_crossings
                FROM video_analyses va
                LEFT JOIN zone_events ze ON va.id = ze.video_analysis_id
                LEFT JOIN line_crossing_events lce ON va.id = lce.video_analysis_id
                WHERE va.id = %s
                GROUP BY va.id, va.video_path, va.model_name, va.status, 
                         va.total_frames, va.fps
                """
                cursor.execute(query, (analysis_id,))
                result = cursor.fetchone()
                return dict(result) if result else None
        except Exception as e:
            logger.error(f"Error al obtener resumen: {e}")
            return None
    
    @staticmethod
    def get_minute_statistics(analysis_id: UUID, 
                            start_time: Optional[datetime] = None,
                            end_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        DEPRECATED: Tabla minute_statistics eliminada para optimización.
        Usa get_analysis_summary() para estadísticas agregadas.
        """
        logger.warning("⚠️ get_minute_statistics() deprecated - tabla eliminada")
        return []
