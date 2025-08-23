#!/usr/bin/env python3
"""
Módulo para manejar la persistencia de datos en formato CSV.
Separa la lógica de optimización del script principal.
"""

import os
import csv
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass


@dataclass
class DetectionEvent:
    """Representa una detección de objeto."""
    frame_number: int
    timestamp_ms: int
    track_id: int
    class_name: str
    confidence: float
    bbox_x1: int
    bbox_y1: int
    bbox_x2: int
    bbox_y2: int
    center_x: int
    center_y: int


@dataclass
class ZoneEvent:
    """Representa un evento de zona (entrada/salida)."""
    track_id: int
    zone_id: str
    zone_name: str
    event_type: str  # 'enter' o 'exit'
    frame_number: int
    timestamp_ms: int
    position_x: int
    position_y: int
    class_name: str  # Tipo de objeto detectado
    confidence: float  # Precisión del modelo


@dataclass
class LineCrossingEvent:
    """Representa un cruce de línea."""
    track_id: int
    line_id: str
    line_name: str
    direction: str  # 'left_to_right' o 'right_to_left'
    frame_number: int
    timestamp_ms: int
    position_x: int
    position_y: int
    class_name: str  # Tipo de objeto detectado
    confidence: float  # Precisión del modelo


class CSVWriter:
    """
    Maneja la escritura de datos en formato CSV con lógica de optimización.
    """
    
    def __init__(self, output_dir: str, analysis_id: str = "analysis_001"):
        """
        Inicializa el escritor de CSV.
        
        Args:
            output_dir: Directorio donde guardar los archivos CSV
            analysis_id: ID del análisis actual
        """
        self.output_dir = output_dir
        self.analysis_id = analysis_id
        self.csv_files = {}
        self.writers = {}
        
        # Estado para tracking de optimización
        self.track_zone_status: Dict[int, Set[str]] = {}  # track_id -> set of zone_ids
        self.track_line_crossings: Set[Tuple[int, str]] = set()  # (track_id, line_id)
        
        # Contadores para IDs únicos
        self.event_counter = 0
        self.detection_counter = 0
        
        self._create_csv_files()
    
    def _create_csv_files(self):
        """Crea los archivos CSV y sus writers."""
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Definir archivos CSV
        csv_configs = {
            'frame_detections': {
                'filename': 'frame_detections.csv',
                'headers': ['id', 'analysis_id', 'frame_number', 'timestamp_ms', 'track_id', 
                           'class_name', 'confidence', 'bbox_x1', 'bbox_y1', 'bbox_x2', 
                           'bbox_y2', 'center_x', 'center_y', 'created_at']
            },
            'zone_events': {
                'filename': 'zone_events.csv',
                'headers': ['id', 'analysis_id', 'zone_id', 'zone_name', 'track_id', 
                           'event_type', 'frame_number', 'timestamp_ms', 'position_x', 
                           'position_y', 'class_name', 'confidence', 'created_at']
            },
            'line_crossing_events': {
                'filename': 'line_crossing_events.csv',
                'headers': ['id', 'analysis_id', 'line_id', 'line_name', 'track_id', 
                           'direction', 'frame_number', 'timestamp_ms', 'position_x', 
                           'position_y', 'class_name', 'confidence', 'created_at']
            },
            'minute_statistics': {
                'filename': 'minute_statistics.csv',
                'headers': ['id', 'analysis_id', 'minute_timestamp', 'total_detections', 
                           'unique_tracks', 'zone_entries', 'zone_exits', 'line_crossings', 
                           'created_at']
            }
        }
        
        # Crear archivos y writers
        for key, config in csv_configs.items():
            filepath = os.path.join(self.output_dir, config['filename'])
            file_handle = open(filepath, 'w', newline='', encoding='utf-8')
            writer = csv.writer(file_handle)
            
            # Escribir headers
            writer.writerow(config['headers'])
            
            self.csv_files[key] = file_handle
            self.writers[key] = writer
        
        print(f"[CSV] Archivos creados en: {self.output_dir}")
    
    def write_detection(self, detection: DetectionEvent):
        """
        Escribe una detección de frame (enfoque sin optimizar).
        Se guarda TODA detección de frame.
        """
        self.detection_counter += 1
        detection_id = f"detection_{detection.track_id}_{detection.frame_number}_{detection.timestamp_ms}"
        
        row = [
            detection_id,
            self.analysis_id,
            detection.frame_number,
            detection.timestamp_ms,
            detection.track_id,
            detection.class_name,
            f"{detection.confidence:.4f}",
            detection.bbox_x1,
            detection.bbox_y1,
            detection.bbox_x2,
            detection.bbox_y2,
            detection.center_x,
            detection.center_y,
            datetime.now().isoformat()
        ]
        
        self.writers['frame_detections'].writerow(row)
    
    def write_zone_event(self, event: ZoneEvent):
        """
        Escribe un evento de zona (enfoque optimizado).
        Solo se guarda cuando hay cambio de estado (entrada/salida).
        """
        self.event_counter += 1
        event_id = f"event_{event.track_id}_{event.frame_number}_{event.timestamp_ms}"
        
        row = [
            event_id,
            self.analysis_id,
            event.zone_id,
            event.zone_name,
            event.track_id,
            event.event_type,
            event.frame_number,
            event.timestamp_ms,
            event.position_x,
            event.position_y,
            event.class_name,
            event.confidence,
            datetime.now().isoformat()
        ]
        
        self.writers['zone_events'].writerow(row)
        print(f"[CSV] Evento de zona guardado: {event.event_type} para track {event.track_id}")
    
    def write_line_crossing(self, event: LineCrossingEvent):
        """
        Escribe un cruce de línea (enfoque optimizado).
        Solo se guarda cuando se cruza una línea.
        """
        self.event_counter += 1
        event_id = f"crossing_{event.track_id}_{event.frame_number}_{event.timestamp_ms}"
        
        row = [
            event_id,
            self.analysis_id,
            event.line_id,
            event.line_name,
            event.track_id,
            event.direction,
            event.frame_number,
            event.timestamp_ms,
            event.position_x,
            event.position_y,
            event.class_name,
            event.confidence,
            datetime.now().isoformat()
        ]
        
        self.writers['line_crossing_events'].writerow(row)
        print(f"[CSV] Cruce de línea guardado: {event.direction} para track {event.track_id}")
    
    def check_zone_event(self, track_id: int, zone_id: str, zone_name: str, 
                        is_in_zone: bool, frame_number: int, timestamp_ms: int, 
                        position_x: int, position_y: int, class_name: str = "", 
                        confidence: float = 0.0) -> bool:
        """
        Verifica si hay un cambio de estado en zona y escribe el evento si es necesario.
        
        Returns:
            True si se escribió un evento, False si no hubo cambio
        """
        # Inicializar tracking para este track si no existe
        if track_id not in self.track_zone_status:
            self.track_zone_status[track_id] = set()
        
        current_zones = self.track_zone_status[track_id]
        
        # Verificar si hay cambio de estado
        if is_in_zone and zone_id not in current_zones:
            # ENTRADA a zona
            current_zones.add(zone_id)
            
            # Crear evento de entrada
            event = ZoneEvent(
                zone_id=zone_id,
                zone_name=zone_name,
                track_id=track_id,
                event_type="enter",
                frame_number=frame_number,
                timestamp_ms=timestamp_ms,
                position_x=position_x,
                position_y=position_y,
                class_name=class_name,
                confidence=confidence
            )
            self.write_zone_event(event)
            return True
            
        elif not is_in_zone and zone_id in current_zones:
            # SALIDA de zona
            current_zones.discard(zone_id)
            
            # Crear evento de salida
            event = ZoneEvent(
                zone_id=zone_id,
                zone_name=zone_name,
                track_id=track_id,
                event_type="exit",
                frame_number=frame_number,
                timestamp_ms=timestamp_ms,
                position_x=position_x,
                position_y=position_y,
                class_name=class_name,
                confidence=confidence
            )
            self.write_zone_event(event)
            return True
        
        return False
    
    def check_line_crossing(self, track_id: int, line_id: str, line_name: str,
                           crossed_line: bool, direction: str, frame_number: int, 
                           timestamp_ms: int, position_x: int, position_y: int, 
                           class_name: str = "", confidence: float = 0.0) -> bool:
        """
        Verifica si hay un cruce de línea y escribe el evento si es necesario.
        
        Returns:
            True si se escribió un evento, False si no hubo cruce
        """
        crossing_key = (track_id, line_id)
        
        if crossed_line and crossing_key not in self.track_line_crossings:
            # Nuevo cruce de línea
            event = LineCrossingEvent(
                track_id=track_id,
                line_id=line_id,
                line_name=line_name,
                direction=direction,
                frame_number=frame_number,
                timestamp_ms=timestamp_ms,
                position_x=position_x,
                position_y=position_y,
                class_name=class_name,
                confidence=confidence
            )
            self.write_line_crossing(event)
            self.track_line_crossings.add(crossing_key)
            return True
        
        return False
    
    def close(self):
        """Cierra todos los archivos CSV."""
        for file_handle in self.csv_files.values():
            file_handle.close()
        
        print(f"[CSV] Archivos cerrados en: {self.output_dir}")
        print(f"   • Detecciones escritas: {self.detection_counter}")
        print(f"   • Eventos optimizados: {self.event_counter}")
    
    def get_summary(self) -> Dict:
        """Retorna un resumen de los datos escritos."""
        return {
            'detection_count': self.detection_counter,
            'event_count': self.event_counter,
            'output_dir': self.output_dir
        }
