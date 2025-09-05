"""
Gestor de temas para la aplicación Streamlit de FlowSense.

Este módulo proporciona funcionalidades para cargar y aplicar diferentes
temas CSS en la interfaz de Streamlit, manteniendo el código principal
limpio y organizando los estilos en archivos separados.

Módulos:
    - Carga de archivos CSS desde el directorio styles/
    - Aplicación dinámica de temas
    - Validación de archivos de tema

Autor: FlowSense Team
Versión: 1.0.0
"""

import streamlit as st
from pathlib import Path
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ThemeManager:
    """
    Gestor de temas para la aplicación Streamlit.
    
    Esta clase maneja la carga y aplicación de diferentes temas CSS
    para la interfaz de usuario de Streamlit.
    
    Attributes:
        styles_dir (Path): Directorio donde se encuentran los archivos CSS
        themes (Dict[str, str]): Diccionario con los nombres y archivos de temas
    """
    
    def __init__(self, styles_dir: Optional[Path] = None):
        """
        Inicializa el gestor de temas.
        
        Args:
            styles_dir (Optional[Path]): Directorio de estilos. Si es None,
                                       usa el directorio 'styles' relativo al archivo actual.
        """
        if styles_dir is None:
            self.styles_dir = Path(__file__).parent
        else:
            self.styles_dir = styles_dir
            
        self.themes = {
            "Claro": "light_theme.css",
            "Oscuro": "dark_theme.css",
            "Automático (sistema)": "auto_theme.css"
        }
        
        logger.info(f"ThemeManager inicializado con directorio: {self.styles_dir}")
    
    def load_css_file(self, filename: str) -> Optional[str]:
        """
        Carga el contenido de un archivo CSS.
        
        Args:
            filename (str): Nombre del archivo CSS a cargar
            
        Returns:
            Optional[str]: Contenido del archivo CSS o None si hay error
            
        Raises:
            FileNotFoundError: Si el archivo CSS no existe
            IOError: Si hay error al leer el archivo
        """
        css_file = self.styles_dir / filename
        
        if not css_file.exists():
            logger.error(f"Archivo CSS no encontrado: {css_file}")
            return None
            
        try:
            with open(css_file, 'r', encoding='utf-8') as f:
                content = f.read()
                logger.info(f"Archivo CSS cargado exitosamente: {filename}")
                return content
        except IOError as e:
            logger.error(f"Error al leer archivo CSS {filename}: {e}")
            return None
    
    def apply_theme(self, theme_name: str) -> bool:
        """
        Aplica un tema específico a la interfaz de Streamlit.
        
        Args:
            theme_name (str): Nombre del tema a aplicar
            
        Returns:
            bool: True si el tema se aplicó correctamente, False en caso contrario
        """
        if theme_name not in self.themes:
            logger.warning(f"Tema no reconocido: {theme_name}")
            return False
            
        css_filename = self.themes[theme_name]
        css_content = self.load_css_file(css_filename)
        
        if css_content is None:
            logger.error(f"No se pudo cargar el tema: {theme_name}")
            return False
            
        # Aplicar CSS a Streamlit
        st.markdown(f"""
        <style>
        {css_content}
        </style>
        """, unsafe_allow_html=True)
        
        logger.info(f"Tema aplicado exitosamente: {theme_name}")
        return True
    
    def get_available_themes(self) -> list:
        """
        Obtiene la lista de temas disponibles.
        
        Returns:
            list: Lista de nombres de temas disponibles
        """
        return list(self.themes.keys())
    
    def validate_themes(self) -> Dict[str, bool]:
        """
        Valida que todos los archivos de tema existan.
        
        Returns:
            Dict[str, bool]: Diccionario con el estado de cada tema
        """
        validation_results = {}
        
        for theme_name, filename in self.themes.items():
            css_file = self.styles_dir / filename
            validation_results[theme_name] = css_file.exists()
            
            if not css_file.exists():
                logger.warning(f"Archivo de tema faltante: {filename}")
        
        return validation_results
    
    def show_theme_status(self, theme_name: str) -> None:
        """
        Muestra el estado del tema aplicado en el sidebar.
        
        Args:
            theme_name (str): Nombre del tema aplicado
        """
        if theme_name == "Claro":
            st.sidebar.warning("⚠️ Tema claro experimental - Se recomienda usar el tema Oscuro para mejor compatibilidad")
        elif theme_name == "Automático (sistema)":
            st.sidebar.info("💡 Usando tema del sistema")
        else:
            st.sidebar.success(f"✅ Tema aplicado: {theme_name}")
