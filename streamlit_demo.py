"""
Demo de Streamlit para FlowSense - Análisis de Video con YOLO.

Este módulo proporciona una interfaz web interactiva para mostrar la funcionalidad
de la aplicación FlowSense, incluyendo análisis de video con YOLO, tracking de objetos
y análisis de zonas.

Módulos:
    - Análisis de video con diferentes modelos YOLO
    - Visualización de datos CSV generados
    - Gráficos interactivos y estadísticas
    - Configuración de zonas de interés

Autor: FlowSense Team
Versión: 1.0.0
"""

import streamlit as st
import pandas as pd
import numpy as np
import cv2
import os
import tempfile
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import subprocess
import sys
from typing import Dict, List, Optional, Tuple, Any
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de la página
st.set_page_config(
    page_title="FlowSense Demo",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("🎥 FlowSense - Análisis de Video con YOLO")
st.markdown("**Demo interactivo para análisis de video con detección de objetos, tracking y análisis de zonas**")

# Sidebar para configuración
st.sidebar.header("⚙️ Configuración")

def run_video_analysis(video_file: Any, model_path: str, config: Dict[str, Any]) -> Tuple[bool, str, str]:
    """
    Ejecuta el análisis de video usando el CLI de la aplicación FlowSense.
    
    Args:
        video_file: Archivo de video subido por el usuario
        model_path: Ruta al modelo YOLO a utilizar
        config: Diccionario con configuración del análisis
        
    Returns:
        Tuple[bool, str, str]: (éxito, stdout, stderr)
        
    Raises:
        FileNotFoundError: Si no se encuentra el modelo o el CLI
        subprocess.SubprocessError: Si hay error en la ejecución del comando
    """
    tmp_video_path = None
    try:
        logger.info(f"Iniciando análisis con modelo: {model_path}")
        
        # Crear archivo temporal para el video
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_video:
            tmp_video.write(video_file.read())
            tmp_video_path = tmp_video.name
        
        # Verificar que el modelo existe
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Modelo no encontrado: {model_path}")
        
        # Verificar que el CLI existe
        cli_path = "src/main.py"
        if not os.path.exists(cli_path):
            raise FileNotFoundError(f"CLI no encontrado: {cli_path}")
        
        # Construir comando
        cmd = [
            sys.executable, cli_path, "process",
            "--video-path", tmp_video_path,
            "--model-path", model_path,
            "--save-video", "true",
            "--show", "false"
        ]
        
        # Agregar parámetros opcionales
        if config.get('classes'):
            cmd.extend(["--classes", config['classes']])
        
        if config.get('conf_threshold'):
            cmd.extend(["--conf-threshold", str(config['conf_threshold'])])
        
        if config.get('enable_stats'):
            cmd.append("--enable-stats")
        
        if config.get('enable_zones') and config.get('zones_config'):
            cmd.extend(["--enable-zones", "true", "--zones-config", config['zones_config']])
        
        logger.info(f"Ejecutando comando: {' '.join(cmd)}")
        
        # Ejecutar comando
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            cwd=os.getcwd(),
            timeout=300  # 5 minutos de timeout
        )
        
        logger.info(f"Análisis completado con código: {result.returncode}")
        
        return result.returncode == 0, result.stdout, result.stderr
        
    except subprocess.TimeoutExpired:
        logger.error("Análisis excedió el tiempo límite")
        return False, "", "Análisis excedió el tiempo límite de 5 minutos"
    except Exception as e:
        logger.error(f"Error durante el análisis: {e}")
        return False, "", str(e)
    finally:
        # Limpiar archivo temporal
        if tmp_video_path and os.path.exists(tmp_video_path):
            try:
                os.unlink(tmp_video_path)
            except OSError as e:
                logger.warning(f"No se pudo eliminar archivo temporal: {e}")

def load_csv_data(output_dir: str) -> Dict[str, Optional[pd.DataFrame]]:
    """
    Carga los datos CSV generados por el análisis de video.
    
    Args:
        output_dir: Directorio donde se encuentran los archivos CSV
        
    Returns:
        Dict[str, Optional[pd.DataFrame]]: Diccionario con los DataFrames cargados
        
    Raises:
        FileNotFoundError: Si el directorio de salida no existe
        pd.errors.EmptyDataError: Si algún archivo CSV está vacío
    """
    if not os.path.exists(output_dir):
        raise FileNotFoundError(f"Directorio de salida no encontrado: {output_dir}")
    
    data: Dict[str, Optional[pd.DataFrame]] = {}
    
    csv_files = {
        'frame_detections': 'frame_detections.csv',
        'zone_events': 'zone_events.csv', 
        'line_crossing_events': 'line_crossing_events.csv',
        'minute_statistics': 'minute_statistics.csv'
    }
    
    for key, filename in csv_files.items():
        filepath = os.path.join(output_dir, filename)
        if os.path.exists(filepath):
            try:
                logger.info(f"Cargando archivo CSV: {filename}")
                df = pd.read_csv(filepath)
                if df.empty:
                    logger.warning(f"Archivo CSV vacío: {filename}")
                    data[key] = None
                else:
                    data[key] = df
                    logger.info(f"Archivo CSV cargado exitosamente: {filename} ({len(df)} filas)")
            except pd.errors.EmptyDataError:
                logger.warning(f"Archivo CSV vacío: {filename}")
                data[key] = None
            except Exception as e:
                logger.error(f"Error cargando {filename}: {e}")
                st.error(f"Error cargando {filename}: {e}")
                data[key] = None
        else:
            logger.info(f"Archivo CSV no encontrado: {filename}")
            data[key] = None
    
    return data

def display_video(video_path: str) -> None:
    """
    Muestra el video procesado en la interfaz de Streamlit.
    
    Args:
        video_path: Ruta al archivo de video a mostrar
        
    Raises:
        FileNotFoundError: Si el archivo de video no existe
    """
    if not os.path.exists(video_path):
        st.error(f"Video no encontrado: {video_path}")
        logger.error(f"Video no encontrado: {video_path}")
        return
    
    try:
        # Verificar que es un archivo de video válido
        if not video_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            st.warning(f"Formato de video no soportado: {video_path}")
            return
        
        # Mostrar información del video
        file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
        st.info(f"📹 Video procesado ({file_size:.2f} MB)")
        
        # Mostrar el video
        st.video(video_path)
        
    except Exception as e:
        st.error(f"Error mostrando video: {e}")
        logger.error(f"Error mostrando video: {e}")

def validate_environment() -> bool:
    """
    Valida que el entorno esté configurado correctamente.
    
    Returns:
        bool: True si el entorno es válido, False en caso contrario
    """
    errors = []
    
    # Verificar directorio de modelos
    models_dir = "models"
    if not os.path.exists(models_dir):
        errors.append("Directorio 'models/' no encontrado")
    else:
        available_models = [f for f in os.listdir(models_dir) if f.endswith('.pt')]
        if not available_models:
            errors.append("No se encontraron modelos YOLO (.pt) en el directorio 'models/'")
    
    # Verificar CLI
    cli_path = "src/main.py"
    if not os.path.exists(cli_path):
        errors.append(f"CLI no encontrado: {cli_path}")
    
    # Verificar directorio de salidas
    outputs_dir = "outputs"
    if not os.path.exists(outputs_dir):
        try:
            os.makedirs(outputs_dir)
            logger.info("Directorio 'outputs/' creado")
        except OSError as e:
            errors.append(f"No se pudo crear directorio 'outputs/': {e}")
    
    # Mostrar errores si los hay
    if errors:
        st.error("❌ Errores de configuración:")
        for error in errors:
            st.error(f"• {error}")
        
        st.info("💡 Soluciones:")
        st.info("• Descarga modelos YOLO: `wget https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.pt -P models/`")
        st.info("• Asegúrate de estar en el directorio raíz del proyecto")
        st.info("• Ejecuta el script de configuración: `./setup_streamlit_demo.sh`")
        
        return False
    
    return True

# Validar entorno
if not validate_environment():
    st.stop()

# Configuración de modelos disponibles
models_dir = "models"
available_models = []
if os.path.exists(models_dir):
    for file in os.listdir(models_dir):
        if file.endswith('.pt'):
            available_models.append(os.path.join(models_dir, file))

# Selección de modelo
selected_model = st.sidebar.selectbox(
    "🤖 Modelo YOLO",
    available_models,
    help="Selecciona el modelo YOLO a usar para el análisis"
)

# Configuración de clases
st.sidebar.subheader("🎯 Detección de Objetos")
classes_input = st.sidebar.text_input(
    "Clases a detectar (opcional)",
    placeholder="person,car,dog (separadas por coma)",
    help="Deja vacío para detectar todos los objetos. Ejemplo: person,car,dog"
)

# Umbral de confianza
conf_threshold = st.sidebar.slider(
    "Umbral de confianza",
    min_value=0.1,
    max_value=1.0,
    value=0.5,
    step=0.05,
    help="Confianza mínima para considerar una detección válida"
)

# Configuración de estadísticas
enable_stats = st.sidebar.checkbox(
    "📊 Generar estadísticas",
    value=True,
    help="Genera estadísticas detalladas por frame"
)

# Configuración de zonas
st.sidebar.subheader("📍 Análisis de Zonas")
enable_zones = st.sidebar.checkbox(
    "Habilitar análisis de zonas",
    help="Analiza entradas/salidas de zonas y cruces de líneas"
)

zones_config = None
if enable_zones:
    # Mostrar archivos de configuración disponibles
    configs_dir = "configs"
    available_configs = []
    if os.path.exists(configs_dir):
        for file in os.listdir(configs_dir):
            if file.endswith('.json'):
                available_configs.append(os.path.join(configs_dir, file))
    
    if available_configs:
        selected_config = st.sidebar.selectbox(
            "Archivo de configuración de zonas",
            available_configs,
            help="Selecciona un archivo JSON con la configuración de zonas"
        )
        zones_config = selected_config
    else:
        st.sidebar.warning("No se encontraron archivos de configuración de zonas")

# Área principal
tab1, tab2, tab3, tab4 = st.tabs(["📹 Análisis de Video", "📊 Estadísticas", "📍 Eventos de Zonas", "📈 Gráficos"])

with tab1:
    st.header("Análisis de Video")
    
    # Subida de archivo
    uploaded_file = st.file_uploader(
        "Selecciona un video para analizar",
        type=['mp4', 'avi', 'mov', 'mkv'],
        help="Formatos soportados: MP4, AVI, MOV, MKV"
    )
    
    if uploaded_file is not None:
        # Mostrar información del video
        st.subheader("📋 Información del Video")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Nombre del archivo", uploaded_file.name)
        with col2:
            st.metric("Tamaño", f"{uploaded_file.size / (1024*1024):.2f} MB")
        with col3:
            st.metric("Tipo", uploaded_file.type)
        
        # Botón para ejecutar análisis
        if st.button("🚀 Ejecutar Análisis", type="primary"):
            with st.spinner("Ejecutando análisis de video..."):
                # Configuración del análisis
                config = {
                    'classes': classes_input if classes_input else None,
                    'conf_threshold': conf_threshold,
                    'enable_stats': enable_stats,
                    'enable_zones': enable_zones,
                    'zones_config': zones_config
                }
                
                # Ejecutar análisis
                success, stdout, stderr = run_video_analysis(uploaded_file, selected_model, config)
                
                if success:
                    st.success("✅ Análisis completado exitosamente!")
                    
                    # Mostrar salida del comando
                    if stdout:
                        st.text_area("Salida del análisis:", stdout, height=200)
                    
                    # Buscar archivos de salida
                    outputs_dir = "outputs"
                    if os.path.exists(outputs_dir):
                        # Buscar el directorio más reciente
                        dirs = [d for d in os.listdir(outputs_dir) if d.startswith('csv_analysis_')]
                        if dirs:
                            latest_dir = max(dirs, key=lambda x: os.path.getctime(os.path.join(outputs_dir, x)))
                            output_dir = os.path.join(outputs_dir, latest_dir)
                            
                            # Buscar video de salida
                            video_files = [f for f in os.listdir(outputs_dir) if f.endswith('.mp4')]
                            if video_files:
                                latest_video = max(video_files, key=lambda x: os.path.getctime(os.path.join(outputs_dir, x)))
                                video_path = os.path.join(outputs_dir, latest_video)
                                
                                st.subheader("🎬 Video Procesado")
                                display_video(video_path)
                            
                            # Cargar datos CSV
                            csv_data = load_csv_data(output_dir)
                            
                            # Guardar datos en session state para otras pestañas
                            st.session_state.csv_data = csv_data
                            st.session_state.output_dir = output_dir
                            
                else:
                    st.error("❌ Error durante el análisis:")
                    if stderr:
                        st.text_area("Error:", stderr, height=200)
                    if stdout:
                        st.text_area("Salida:", stdout, height=200)

with tab2:
    st.header("📊 Estadísticas del Análisis")
    
    if 'csv_data' in st.session_state and st.session_state.csv_data:
        csv_data = st.session_state.csv_data
        
        # Estadísticas de detecciones por frame
        if csv_data.get('frame_detections') is not None:
            st.subheader("Detecciones por Frame")
            df_detections = csv_data['frame_detections']
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Detecciones", len(df_detections))
            with col2:
                st.metric("IDs Únicos", df_detections['track_id'].nunique())
            with col3:
                st.metric("Frames Procesados", df_detections['frame_number'].max())
            with col4:
                st.metric("Confianza Promedio", f"{df_detections['confidence'].mean():.3f}")
            
            # Gráfico de detecciones por frame
            detections_per_frame = df_detections.groupby('frame_number').size().reset_index(name='count')
            fig = px.line(detections_per_frame, x='frame_number', y='count', 
                         title='Detecciones por Frame')
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabla de detecciones
            st.subheader("Detecciones Recientes")
            st.dataframe(df_detections.tail(10), use_container_width=True)
        
        # Estadísticas por minuto
        if csv_data.get('minute_statistics') is not None:
            st.subheader("Estadísticas por Minuto")
            df_minute = csv_data['minute_statistics']
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Detecciones/Min", df_minute['total_detections'].sum())
            with col2:
                st.metric("Tracks Únicos/Min", df_minute['unique_tracks'].sum())
            with col3:
                st.metric("Cruces de Línea/Min", df_minute['line_crossings'].sum())
            
            # Gráfico de estadísticas por minuto
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df_minute['minute_timestamp'], y=df_minute['total_detections'], 
                                   mode='lines+markers', name='Detecciones'))
            fig.add_trace(go.Scatter(x=df_minute['minute_timestamp'], y=df_minute['unique_tracks'], 
                                   mode='lines+markers', name='Tracks Únicos'))
            fig.update_layout(title='Estadísticas por Minuto', xaxis_title='Tiempo', yaxis_title='Cantidad')
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Ejecuta un análisis de video para ver las estadísticas")

with tab3:
    st.header("📍 Eventos de Zonas")
    
    if 'csv_data' in st.session_state and st.session_state.csv_data:
        csv_data = st.session_state.csv_data
        
        # Eventos de zonas
        if csv_data.get('zone_events') is not None:
            st.subheader("Entradas y Salidas de Zonas")
            df_zones = csv_data['zone_events']
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Eventos", len(df_zones))
            with col2:
                st.metric("Entradas", len(df_zones[df_zones['event_type'] == 'enter']))
            with col3:
                st.metric("Salidas", len(df_zones[df_zones['event_type'] == 'exit']))
            
            # Gráfico de eventos por zona
            zone_events = df_zones.groupby(['zone_name', 'event_type']).size().reset_index(name='count')
            fig = px.bar(zone_events, x='zone_name', y='count', color='event_type',
                        title='Eventos por Zona', barmode='group')
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabla de eventos
            st.subheader("Eventos de Zona")
            st.dataframe(df_zones, use_container_width=True)
        
        # Cruces de líneas
        if csv_data.get('line_crossing_events') is not None:
            st.subheader("Cruces de Líneas")
            df_lines = csv_data['line_crossing_events']
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Cruces", len(df_lines))
            with col2:
                st.metric("Izq → Der", len(df_lines[df_lines['direction'] == 'left_to_right']))
            with col3:
                st.metric("Der → Izq", len(df_lines[df_lines['direction'] == 'right_to_left']))
            
            # Gráfico de cruces por dirección
            direction_counts = df_lines['direction'].value_counts()
            fig = px.pie(values=direction_counts.values, names=direction_counts.index,
                        title='Distribución de Cruces por Dirección')
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabla de cruces
            st.subheader("Cruces de Línea")
            st.dataframe(df_lines, use_container_width=True)
    else:
        st.info("Ejecuta un análisis de video con zonas habilitadas para ver los eventos")

with tab4:
    st.header("📈 Gráficos y Visualizaciones")
    
    if 'csv_data' in st.session_state and st.session_state.csv_data:
        csv_data = st.session_state.csv_data
        
        # Gráfico de confianza
        if csv_data.get('frame_detections') is not None:
            st.subheader("Distribución de Confianza")
            df_detections = csv_data['frame_detections']
            
            fig = px.histogram(df_detections, x='confidence', nbins=20, 
                             title='Distribución de Confianza de Detecciones')
            st.plotly_chart(fig, use_container_width=True)
        
        # Gráfico de clases detectadas
        if csv_data.get('frame_detections') is not None:
            st.subheader("Clases Detectadas")
            df_detections = csv_data['frame_detections']
            
            class_counts = df_detections['class_name'].value_counts()
            fig = px.bar(x=class_counts.index, y=class_counts.values,
                        title='Número de Detecciones por Clase')
            fig.update_xaxis(title='Clase')
            fig.update_yaxis(title='Número de Detecciones')
            st.plotly_chart(fig, use_container_width=True)
        
        # Gráfico de trayectorias (si hay datos de posición)
        if csv_data.get('frame_detections') is not None:
            st.subheader("Trayectorias de Objetos")
            df_detections = csv_data['frame_detections']
            
            # Seleccionar algunos tracks para visualizar
            unique_tracks = df_detections['track_id'].unique()
            selected_tracks = st.multiselect(
                "Selecciona tracks para visualizar:",
                unique_tracks[:10],  # Limitar a los primeros 10
                default=unique_tracks[:3] if len(unique_tracks) >= 3 else unique_tracks
            )
            
            if selected_tracks:
                fig = go.Figure()
                
                for track_id in selected_tracks:
                    track_data = df_detections[df_detections['track_id'] == track_id]
                    fig.add_trace(go.Scatter(
                        x=track_data['center_x'],
                        y=track_data['center_y'],
                        mode='lines+markers',
                        name=f'Track {track_id}',
                        line=dict(width=2)
                    ))
                
                fig.update_layout(
                    title='Trayectorias de Objetos',
                    xaxis_title='Posición X',
                    yaxis_title='Posición Y',
                    yaxis=dict(scaleanchor="x", scaleratio=1)
                )
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Ejecuta un análisis de video para ver los gráficos")

# Footer
st.markdown("---")
st.markdown("**FlowSense Demo** - Análisis de video con YOLO, tracking y análisis de zonas")
st.markdown("Desarrollado con ❤️ usando Streamlit")
