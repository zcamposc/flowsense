"""
Modelos Pydantic para la base de datos de análisis de video.
Define las estructuras de datos para todas las entidades.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


# =====================================================
# MODELOS PARA TIMESCALEDB
# FASE 9: Base de Datos de Series de Tiempo
# =====================================================

class AnalysisConfig(BaseModel):
    """Configuración del análisis de video."""
    classes: Optional[List[str]] = None
    conf_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    enable_stats: bool = True
    enable_zones: bool = True
    save_video: bool = True
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class VideoAnalysis(BaseModel):
    """Modelo para análisis de video."""
    id: Optional[UUID] = None
    video_path: str
    model_name: str
    analysis_config: Optional[AnalysisConfig] = None
    status: str = "running"
    total_frames: int = 0
    fps: Optional[float] = None
    resolution_width: Optional[int] = None
    resolution_height: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class Zone(BaseModel):
    """Modelo para zonas de análisis."""
    id: Optional[UUID] = None
    video_analysis_id: Optional[UUID] = None
    zone_name: str
    zone_type: str  # 'polygon' o 'line'
    coordinates: List[List[float]]
    created_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


# FrameDetection eliminado - tabla no necesaria para optimización
# Solo se mantienen los eventos significativos (zone_events, line_crossing_events)


class ZoneEvent(BaseModel):
    """Modelo para eventos de entrada/salida de zona - Optimizado para TimescaleDB."""
    id: Optional[UUID] = None
    time: datetime = Field(..., description="Timestamp absoluto (fecha ejecución + offset)")
    video_time_ms: int = Field(..., description="Timestamp relativo al video en milisegundos")
    video_analysis_id: Optional[UUID] = None
    zone_id: Optional[UUID] = None
    track_id: int = Field(..., description="ID del track")
    event_type: str = Field(..., description="Tipo de evento: 'enter' o 'exit'")
    class_name: str = Field(..., description="Nombre de la clase detectada")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confianza de la detección")
    position_x: int = Field(..., description="Posición X del objeto")
    position_y: int = Field(..., description="Posición Y del objeto")
    
    @classmethod
    def from_event_data(cls, video_analysis_id: UUID, zone_id: UUID, 
                       timestamp_ms: int, track_id: int, event_type: str,
                       class_name: str, confidence: float, position: List[int],
                       analysis_start_time: Optional[datetime] = None):
        """Crea una instancia desde datos de evento."""
        # Convertir timestamp_ms relativo a datetime absoluto
        # timestamp_ms es relativo al inicio del video, necesitamos convertirlo a timestamp absoluto
        from datetime import timedelta
        base_time = analysis_start_time or datetime.now()  # Usar tiempo de inicio del análisis como base
        time = base_time + timedelta(milliseconds=timestamp_ms)
        
        return cls(
            video_analysis_id=video_analysis_id,
            time=time,
            video_time_ms=timestamp_ms,
            zone_id=zone_id,
            track_id=track_id,
            event_type=event_type,
            class_name=class_name,
            confidence=confidence,
            position_x=position[0],
            position_y=position[1]
        )
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


class LineCrossingEvent(BaseModel):
    """Modelo para eventos de cruce de línea - Optimizado para TimescaleDB."""
    id: Optional[UUID] = None
    time: datetime = Field(..., description="Timestamp absoluto (fecha ejecución + offset)")
    video_time_ms: int = Field(..., description="Timestamp relativo al video en milisegundos")
    video_analysis_id: Optional[UUID] = None
    zone_id: Optional[UUID] = None
    track_id: int = Field(..., description="ID del track")
    direction: str = Field(..., description="Dirección del cruce: 'left_to_right' o 'right_to_left'")
    class_name: str = Field(..., description="Nombre de la clase detectada")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confianza de la detección")
    position_x: int = Field(..., description="Posición X del objeto")
    position_y: int = Field(..., description="Posición Y del objeto")
    
    @classmethod
    def from_crossing_data(cls, video_analysis_id: UUID, zone_id: UUID,
                          timestamp_ms: int, track_id: int, direction: str,
                          class_name: str, confidence: float, 
                          position: List[int],
                          analysis_start_time: Optional[datetime] = None):
        """Crea una instancia desde datos de cruce."""
        # Convertir timestamp_ms relativo a datetime absoluto
        # timestamp_ms es relativo al inicio del video, necesitamos convertirlo a timestamp absoluto
        from datetime import timedelta
        base_time = analysis_start_time or datetime.now()  # Usar tiempo de inicio del análisis como base
        time = base_time + timedelta(milliseconds=timestamp_ms)
        
        return cls(
            video_analysis_id=video_analysis_id,
            time=time,
            video_time_ms=timestamp_ms,
            zone_id=zone_id,
            track_id=track_id,
            direction=direction,
            class_name=class_name,
            confidence=confidence,
            position_x=position[0],
            position_y=position[1]
        )
    
    @classmethod
    def from_event_data(cls, video_analysis_id: UUID, zone_id: UUID,
                       timestamp_ms: int, track_id: int, direction: str,
                       class_name: str, confidence: float, 
                       position: List[int],
                       analysis_start_time: Optional[datetime] = None):
        """Método alternativo para mantener compatibilidad con el código existente."""
        return cls.from_crossing_data(
            video_analysis_id=video_analysis_id,
            zone_id=zone_id,
            timestamp_ms=timestamp_ms,
            track_id=track_id,
            direction=direction,
            class_name=class_name,
            confidence=confidence,
            position=position,
            analysis_start_time=analysis_start_time
        )
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }


# MinuteStatistics eliminado - tabla no necesaria
# Las estadísticas se calculan dinámicamente desde zone_events y line_crossing_events
