"""
Servicio de base de datos para integración con el sistema de análisis de video.
Maneja la lógica de negocio y la integración con el sistema existente.
"""

import logging
import json
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from uuid import UUID
import cv2
import numpy as np

from .models import (
    VideoAnalysis, Zone, FrameDetection, ZoneEvent, LineCrossingEvent,
    ZoneType, EventType, CrossingDirection, AnalysisStatus, AnalysisConfig
)
from .repository import (
    VideoAnalysisRepository, ZoneRepository, FrameDetectionRepository,
    ZoneEventRepository, LineCrossingRepository, StatisticsRepository
)
from .connection import initialize_database, get_db_manager

logger = logging.getLogger(__name__)


class VideoAnalysisService:
    """Servicio principal para análisis de video con base de datos."""
    
    def __init__(self):
        """Inicializar el servicio."""
        self.video_repo = VideoAnalysisRepository()
        self.zone_repo = ZoneRepository()
        self.detection_repo = FrameDetectionRepository()
        self.zone_event_repo = ZoneEventRepository()
        self.line_crossing_repo = LineCrossingRepository()
        self.stats_repo = StatisticsRepository()
        
        # Estado del análisis actual
        self.current_analysis_id: Optional[UUID] = None
        self.zones_cache: Dict[str, Zone] = {}
        self.track_zone_status: Dict[int, Dict[UUID, str]] = {}  # track_id -> {zone_id: status}
    
    def initialize_database(self) -> bool:
        """Inicializar la base de datos."""
        return initialize_database()
    
    def start_analysis(self, video_path: str, model_name: str, 
                      config: AnalysisConfig) -> Optional[UUID]:
        """Iniciar un nuevo análisis de video."""
        try:
            # Crear registro de análisis
            analysis = VideoAnalysis(
                video_path=video_path,
                model_name=model_name,
                analysis_config=config.dict(),
                status=AnalysisStatus.RUNNING
            )
            
            analysis_id = self.video_repo.create_analysis(analysis)
            if not analysis_id:
                logger.error("No se pudo crear el análisis")
                return None
            
            self.current_analysis_id = analysis_id
            logger.info(f"Análisis iniciado con ID: {analysis_id}")
            
            # Cargar zonas si están configuradas
            if config.enable_zones:
                self._load_zones_from_config(config.enable_zones)
            
            return analysis_id
            
        except Exception as e:
            logger.error(f"Error al iniciar análisis: {e}")
            return None
    
    def _load_zones_from_config(self, zones_file: str) -> None:
        """Cargar zonas desde archivo de configuración."""
        try:
            with open(zones_file, 'r') as f:
                zones_data = json.load(f)
            
            # Cargar líneas
            for i, line_coords in enumerate(zones_data.get('lines', [])):
                zone = Zone(
                    video_analysis_id=self.current_analysis_id,
                    zone_name=f"line_{i+1}",
                    zone_type=ZoneType.LINE,
                    coordinates=line_coords
                )
                zone_id = self.zone_repo.create_zone(zone)
                if zone_id:
                    zone.id = zone_id
                    self.zones_cache[zone.zone_name] = zone
            
            # Cargar polígonos
            for i, polygon_coords in enumerate(zones_data.get('polygons', [])):
                zone = Zone(
                    video_analysis_id=self.current_analysis_id,
                    zone_name=f"polygon_{i+1}",
                    zone_type=ZoneType.POLYGON,
                    coordinates=polygon_coords
                )
                zone_id = self.zone_repo.create_zone(zone)
                if zone_id:
                    zone.id = zone_id
                    self.zones_cache[zone.zone_name] = zone
            
            logger.info(f"Cargadas {len(self.zones_cache)} zonas")
            
        except Exception as e:
            logger.error(f"Error al cargar zonas: {e}")
    
    def process_frame_detections(self, frame_number: int, timestamp_ms: int,
                               detections: List[Dict[str, Any]]) -> None:
        """Procesar detecciones de un frame."""
        if not self.current_analysis_id:
            logger.error("No hay análisis activo")
            return
        
        try:
            # Crear detecciones en lote
            frame_detections = []
            for detection in detections:
                frame_detection = FrameDetection(
                    video_analysis_id=self.current_analysis_id,
                    frame_number=frame_number,
                    timestamp_ms=timestamp_ms,
                    track_id=detection['track_id'],
                    class_name=detection['class_name'],
                    confidence=detection['confidence'],
                    bbox_x1=detection['bbox'][0],
                    bbox_y1=detection['bbox'][1],
                    bbox_x2=detection['bbox'][2],
                    bbox_y2=detection['bbox'][3],
                    center_x=detection['center'][0],
                    center_y=detection['center'][1]
                )
                frame_detections.append(frame_detection)
            
            # Guardar detecciones
            if frame_detections:
                self.detection_repo.create_bulk_detections(frame_detections)
            
            # Analizar eventos de zonas
            self._analyze_zone_events(frame_number, timestamp_ms, detections)
            
        except Exception as e:
            logger.error(f"Error al procesar detecciones: {e}")
    
    def _analyze_zone_events(self, frame_number: int, timestamp_ms: int,
                           detections: List[Dict[str, Any]]) -> None:
        """Analizar eventos de zonas para las detecciones del frame."""
        for detection in detections:
            track_id = detection['track_id']
            center_x, center_y = detection['center']
            
            # Inicializar estado del track si no existe
            if track_id not in self.track_zone_status:
                self.track_zone_status[track_id] = {}
            
            # Analizar cada zona
            for zone in self.zones_cache.values():
                if zone.zone_type == ZoneType.POLYGON:
                    self._analyze_polygon_zone(zone, track_id, center_x, center_y,
                                             frame_number, timestamp_ms)
                elif zone.zone_type == ZoneType.LINE:
                    self._analyze_line_zone(zone, track_id, center_x, center_y,
                                          frame_number, timestamp_ms)
    
    def _analyze_polygon_zone(self, zone: Zone, track_id: int, center_x: int,
                            center_y: int, frame_number: int, 
                            timestamp_ms: int) -> None:
        """Analizar eventos de zona tipo polígono."""
        from utils.geometry import punto_en_poligono
        
        current_status = self.track_zone_status[track_id].get(zone.id, 'outside')
        is_inside = punto_en_poligono((center_x, center_y), zone.coordinates)
        
        # Detectar cambios de estado
        if is_inside and current_status == 'outside':
            # Entrada a zona
            event = ZoneEvent(
                video_analysis_id=self.current_analysis_id,
                zone_id=zone.id,
                track_id=track_id,
                event_type=EventType.ENTER,
                frame_number=frame_number,
                timestamp_ms=timestamp_ms,
                position_x=center_x,
                position_y=center_y
            )
            self.zone_event_repo.create_zone_event(event)
            self.track_zone_status[track_id][zone.id] = 'inside'
            logger.info(f"Track {track_id} entró en zona {zone.zone_name}")
            
        elif not is_inside and current_status == 'inside':
            # Salida de zona
            event = ZoneEvent(
                video_analysis_id=self.current_analysis_id,
                zone_id=zone.id,
                track_id=track_id,
                event_type=EventType.EXIT,
                frame_number=frame_number,
                timestamp_ms=timestamp_ms,
                position_x=center_x,
                position_y=center_y
            )
            self.zone_event_repo.create_zone_event(event)
            self.track_zone_status[track_id][zone.id] = 'outside'
            logger.info(f"Track {track_id} salió de zona {zone.zone_name}")
    
    def _analyze_line_zone(self, zone: Zone, track_id: int, center_x: int,
                          center_y: int, frame_number: int, 
                          timestamp_ms: int) -> None:
        """Analizar eventos de zona tipo línea."""
        # Obtener posición anterior del track
        # Nota: En una implementación real, necesitarías mantener un historial
        # de posiciones para detectar cruces de línea
        
        # Por simplicidad, aquí solo detectamos si el punto está cerca de la línea
        # En una implementación completa, necesitarías:
        # 1. Mantener historial de posiciones del track
        # 2. Detectar cruces usando la función cruza_linea
        # 3. Determinar dirección del cruce
        
        # Ejemplo simplificado:
        line_start = zone.coordinates[0]
        line_end = zone.coordinates[1]
        
        # Calcular distancia a la línea
        distance = self._distance_to_line(center_x, center_y, line_start, line_end)
        
        if distance < 10:  # Umbral de proximidad
            # Aquí detectarías el cruce real usando historial de posiciones
            pass
    
    def _distance_to_line(self, x: int, y: int, line_start: List[int], 
                         line_end: List[int]) -> float:
        """Calcular distancia de un punto a una línea."""
        x1, y1 = line_start
        x2, y2 = line_end
        
        # Fórmula de distancia punto-línea
        numerator = abs((y2-y1)*x - (x2-x1)*y + x2*y1 - y2*x1)
        denominator = ((y2-y1)**2 + (x2-x1)**2)**0.5
        
        return numerator / denominator if denominator > 0 else float('inf')
    
    def complete_analysis(self, total_frames: int, fps: float, 
                         width: int, height: int) -> bool:
        """Completar el análisis de video."""
        if not self.current_analysis_id:
            logger.error("No hay análisis activo")
            return False
        
        try:
            # Actualizar información del análisis
            success = self.video_repo.update_analysis_status(
                self.current_analysis_id,
                AnalysisStatus.COMPLETED.value,
                datetime.now()
            )
            
            if success:
                logger.info(f"Análisis {self.current_analysis_id} completado")
                self.current_analysis_id = None
                self.zones_cache.clear()
                self.track_zone_status.clear()
            
            return success
            
        except Exception as e:
            logger.error(f"Error al completar análisis: {e}")
            return False
    
    def get_analysis_summary(self, analysis_id: UUID) -> Optional[Dict[str, Any]]:
        """Obtener resumen de un análisis."""
        return self.stats_repo.get_analysis_summary(analysis_id)
    
    def get_zone_events(self, analysis_id: UUID, zone_name: Optional[str] = None,
                       track_id: Optional[int] = None) -> List[ZoneEvent]:
        """Obtener eventos de zona."""
        zone_id = None
        if zone_name:
            # Buscar zona por nombre
            zones = self.zone_repo.get_zones_by_analysis(analysis_id)
            for zone in zones:
                if zone.zone_name == zone_name:
                    zone_id = zone.id
                    break
        
        return self.zone_event_repo.get_zone_events(analysis_id, zone_id, track_id)
    
    def get_line_crossings(self, analysis_id: UUID, zone_name: Optional[str] = None,
                          track_id: Optional[int] = None) -> List[LineCrossingEvent]:
        """Obtener cruces de línea."""
        zone_id = None
        if zone_name:
            # Buscar zona por nombre
            zones = self.zone_repo.get_zones_by_analysis(analysis_id)
            for zone in zones:
                if zone.zone_name == zone_name:
                    zone_id = zone.id
                    break
        
        return self.line_crossing_repo.get_line_crossings(analysis_id, zone_id, track_id)
    
    def get_minute_statistics(self, analysis_id: UUID, 
                            start_time: Optional[datetime] = None,
                            end_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Obtener estadísticas por minuto."""
        return self.stats_repo.get_minute_statistics(analysis_id, start_time, end_time)


# Instancia global del servicio
video_service = VideoAnalysisService()


def get_video_service() -> VideoAnalysisService:
    """Obtener la instancia global del servicio de video."""
    return video_service
