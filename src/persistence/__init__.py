"""
Módulo de persistencia para el análisis de video.
Maneja la escritura de datos en diferentes formatos (CSV, BD, etc.).
"""

from .csv_writer import CSVWriter, DetectionEvent, ZoneEvent, LineCrossingEvent

__all__ = ['CSVWriter', 'DetectionEvent', 'ZoneEvent', 'LineCrossingEvent']
