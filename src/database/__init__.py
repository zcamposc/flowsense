"""
Módulo de base de datos para la FASE 9: Base de Datos de Series de Tiempo.
Proporciona funcionalidades para almacenar y consultar datos de análisis de video.
"""

from .service import VideoAnalysisService
from .models import AnalysisConfig

__all__ = ['VideoAnalysisService', 'AnalysisConfig']
