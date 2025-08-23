"""
Modelos Pydantic para la base de datos de series de tiempo.
Sistema de almacenamiento optimizado para eventos de video.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum


class ZoneType(str, Enum):
    """Tipos de zonas soportados."""
    POLYGON = "polygon"
    LINE = "line"


class EventType(str, Enum):
    """Tipos de eventos de zona."""
    ENTER = "enter"
    EXIT = "exit"


class CrossingDirection(str, Enum):
    """Direcciones de cruce de líneas."""
    LEFT_TO_RIGHT = "left_to_right"
    RIGHT_TO_LEFT = "right_to_left"


class AnalysisStatus(str, Enum):
    """Estados de análisis de video."""
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# =====================================================
# MODELOS DE CONFIGURACIÓN
# =====================================================

class VideoAnalysis(BaseModel):
    """Modelo para registro de análisis de video."""
    id: Optional[UUID] = None
    video_path: str = Field(..., description="Ruta del archivo de video")
    model_name: str = Field(..., description="Nombre del modelo YOLO utilizado")
    analysis_config: Dict[str, Any] = Field(..., description="Configuración completa del análisis")
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: AnalysisStatus = Field(default=AnalysisStatus.RUNNING, description="Estado del análisis")
    total_frames: Optional[int] = None
    fps: Optional[float] = None
    resolution_width: Optional[int] = None
    resolution_height: Optional[int] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class Zone(BaseModel):
    """Modelo para configuración de zonas."""
    id: Optional[UUID] = None
    video_analysis_id: Optional[UUID] = None
    zone_name: str = Field(..., description="Nombre único de la zona")
    zone_type: ZoneType = Field(..., description="Tipo de zona (polígono o línea)")
    coordinates: List[List[int]] = Field(..., description="Coordenadas de la zona")
    created_at: Optional[datetime] = None

    @validator('coordinates')
    def validate_coordinates(cls, v, values):
        """Validar coordenadas según el tipo de zona."""
        zone_type = values.get('zone_type')
        
        if zone_type == ZoneType.LINE:
            if len(v) != 2:
                raise ValueError("Una línea debe tener exactamente 2 puntos")
            for point in v:
                if len(point) != 2:
                    raise ValueError("Cada punto debe tener 2 coordenadas (x, y)")
        
        elif zone_type == ZoneType.POLYGON:
            if len(v) < 3:
                raise ValueError("Un polígono debe tener al menos 3 puntos")
            for point in v:
                if len(point) != 2:
                    raise ValueError("Cada punto debe tener 2 coordenadas (x, y)")
        
        return v

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


# =====================================================
# MODELOS DE EVENTOS DE SERIES DE TIEMPO
# =====================================================

class FrameDetection(BaseModel):
    """Modelo para detecciones individuales por frame."""
    id: Optional[UUID] = None
    video_analysis_id: Optional[UUID] = None
    frame_number: int = Field(..., description="Número de frame")
    timestamp_ms: int = Field(..., description="Timestamp en milisegundos desde inicio del video")
    track_id: int = Field(..., description="ID único del track")
    class_name: str = Field(..., description="Nombre de la clase detectada")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confianza de la detección")
    bbox_x1: int = Field(..., description="Coordenada X1 del bounding box")
    bbox_y1: int = Field(..., description="Coordenada Y1 del bounding box")
    bbox_x2: int = Field(..., description="Coordenada X2 del bounding box")
    bbox_y2: int = Field(..., description="Coordenada Y2 del bounding box")
    center_x: int = Field(..., description="Coordenada X del centro")
    center_y: int = Field(..., description="Coordenada Y del centro")
    created_at: Optional[datetime] = None

    @validator('bbox_x2')
    def validate_bbox_x2(cls, v, values):
        """Validar que x2 > x1."""
        if 'bbox_x1' in values and v <= values['bbox_x1']:
            raise ValueError("bbox_x2 debe ser mayor que bbox_x1")
        return v

    @validator('bbox_y2')
    def validate_bbox_y2(cls, v, values):
        """Validar que y2 > y1."""
        if 'bbox_y1' in values and v <= values['bbox_y1']:
            raise ValueError("bbox_y2 debe ser mayor que bbox_y1")
        return v

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class ZoneEvent(BaseModel):
    """Modelo para eventos de entrada/salida de zonas."""
    id: Optional[UUID] = None
    video_analysis_id: Optional[UUID] = None
    zone_id: Optional[UUID] = None
    track_id: int = Field(..., description="ID único del track")
    event_type: EventType = Field(..., description="Tipo de evento (entrada o salida)")
    frame_number: int = Field(..., description="Número de frame")
    timestamp_ms: int = Field(..., description="Timestamp en milisegundos")
    position_x: int = Field(..., description="Posición X del evento")
    position_y: int = Field(..., description="Posición Y del evento")
    created_at: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class LineCrossingEvent(BaseModel):
    """Modelo para eventos de cruce de líneas."""
    id: Optional[UUID] = None
    video_analysis_id: Optional[UUID] = None
    zone_id: Optional[UUID] = None
    track_id: int = Field(..., description="ID único del track")
    direction: CrossingDirection = Field(..., description="Dirección del cruce")
    frame_number: int = Field(..., description="Número de frame")
    timestamp_ms: int = Field(..., description="Timestamp en milisegundos")
    position_x: int = Field(..., description="Posición X del cruce")
    position_y: int = Field(..., description="Posición Y del cruce")
    created_at: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


# =====================================================
# MODELOS DE AGREGACIÓN
# =====================================================

class MinuteStatistics(BaseModel):
    """Modelo para estadísticas agregadas por minuto."""
    id: Optional[UUID] = None
    video_analysis_id: Optional[UUID] = None
    minute_timestamp: datetime = Field(..., description="Timestamp del minuto")
    total_detections: int = Field(default=0, ge=0, description="Total de detecciones")
    unique_tracks: int = Field(default=0, ge=0, description="Tracks únicos")
    zone_entries: int = Field(default=0, ge=0, description="Entradas a zonas")
    zone_exits: int = Field(default=0, ge=0, description="Salidas de zonas")
    line_crossings: int = Field(default=0, ge=0, description="Cruces de líneas")
    created_at: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class HourStatistics(BaseModel):
    """Modelo para estadísticas agregadas por hora."""
    id: Optional[UUID] = None
    video_analysis_id: Optional[UUID] = None
    hour_timestamp: datetime = Field(..., description="Timestamp de la hora")
    total_detections: int = Field(default=0, ge=0, description="Total de detecciones")
    unique_tracks: int = Field(default=0, ge=0, description="Tracks únicos")
    zone_entries: int = Field(default=0, ge=0, description="Entradas a zonas")
    zone_exits: int = Field(default=0, ge=0, description="Salidas de zonas")
    line_crossings: int = Field(default=0, ge=0, description="Cruces de líneas")
    created_at: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


# =====================================================
# MODELOS DE CONSULTA Y RESPUESTA
# =====================================================

class TrackZoneStatus(BaseModel):
    """Modelo para estado actual de tracks en zonas."""
    video_analysis_id: UUID
    zone_id: UUID
    zone_name: str
    track_id: int
    current_status: str = Field(..., description="Estado actual: inside, outside, unknown")
    last_event_time: int = Field(..., description="Timestamp del último evento")

    class Config:
        json_encoders = {
            UUID: lambda v: str(v)
        }


class AnalysisSummary(BaseModel):
    """Modelo para resumen de análisis."""
    video_analysis_id: UUID
    video_path: str
    model_name: str
    status: AnalysisStatus
    total_frames: Optional[int] = None
    fps: Optional[float] = None
    total_unique_tracks: int = Field(default=0, ge=0)
    total_detections: int = Field(default=0, ge=0)
    total_zone_events: int = Field(default=0, ge=0)
    total_line_crossings: int = Field(default=0, ge=0)
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


# =====================================================
# MODELOS DE CONFIGURACIÓN DE ANÁLISIS
# =====================================================

class AnalysisConfig(BaseModel):
    """Modelo para configuración de análisis."""
    classes: Optional[List[str]] = Field(default=None, description="Clases a detectar")
    conf_threshold: float = Field(default=0.25, ge=0.0, le=1.0, description="Umbral de confianza")
    enable_stats: bool = Field(default=False, description="Habilitar estadísticas")
    enable_zones: Optional[str] = Field(default=None, description="Archivo de configuración de zonas")
    save_video: bool = Field(default=True, description="Guardar video procesado")
    show_video: bool = Field(default=True, description="Mostrar video en tiempo real")

    class Config:
        schema_extra = {
            "example": {
                "classes": ["person"],
                "conf_threshold": 0.25,
                "enable_stats": True,
                "enable_zones": "configs/zonas.json",
                "save_video": True,
                "show_video": False
            }
        }


# =====================================================
# MODELOS DE CONSULTA TEMPORAL
# =====================================================

class TimeRangeQuery(BaseModel):
    """Modelo para consultas por rango de tiempo."""
    video_analysis_id: UUID
    start_timestamp_ms: Optional[int] = Field(default=None, description="Timestamp de inicio")
    end_timestamp_ms: Optional[int] = Field(default=None, description="Timestamp de fin")
    track_ids: Optional[List[int]] = Field(default=None, description="IDs de tracks específicos")
    zone_ids: Optional[List[UUID]] = Field(default=None, description="IDs de zonas específicas")

    class Config:
        json_encoders = {
            UUID: lambda v: str(v)
        }


class ZoneQuery(BaseModel):
    """Modelo para consultas específicas de zonas."""
    video_analysis_id: UUID
    zone_id: Optional[UUID] = None
    zone_name: Optional[str] = None
    event_type: Optional[EventType] = None
    track_id: Optional[int] = None

    class Config:
        json_encoders = {
            UUID: lambda v: str(v)
        }


class LineCrossingQuery(BaseModel):
    """Modelo para consultas de cruces de líneas."""
    video_analysis_id: UUID
    zone_id: Optional[UUID] = None
    zone_name: Optional[str] = None
    direction: Optional[CrossingDirection] = None
    track_id: Optional[int] = None

    class Config:
        json_encoders = {
            UUID: lambda v: str(v)
        }
