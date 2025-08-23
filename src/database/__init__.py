"""
Módulo de base de datos para el sistema de series de tiempo.
Proporciona almacenamiento persistente para análisis de video.
"""

from .models import (
    VideoAnalysis, Zone, FrameDetection, ZoneEvent, LineCrossingEvent,
    ZoneType, EventType, CrossingDirection, AnalysisStatus, AnalysisConfig
)
from .service import VideoAnalysisService, get_video_service
from .connection import initialize_database, get_db_manager

__all__ = [
    'VideoAnalysis',
    'Zone', 
    'FrameDetection',
    'ZoneEvent',
    'LineCrossingEvent',
    'ZoneType',
    'EventType',
    'CrossingDirection',
    'AnalysisStatus',
    'AnalysisConfig',
    'VideoAnalysisService',
    'get_video_service',
    'initialize_database',
    'get_db_manager'
]
