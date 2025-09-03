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
from ultralytics import YOLO


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

# Configurar límite de carga de archivos (en MB)
# Por defecto Streamlit tiene límite de 200MB
# Puedes aumentarlo con esta configuración
MAX_FILE_SIZE_MB = 1000  # Aumentar a 1GB
st.write(f"Límite máximo de archivo: {MAX_FILE_SIZE_MB} MB")

# Título principal
st.title("🎥 FlowSense - Inteligencia que entiende el flujo de tu cliente")
st.markdown("**Demo interactivo para análisis de video con detección de personas, tracking y análisis de zonas**")

# Sidebar para configuración
st.sidebar.header("⚙️ Configuración")

# Selector de tema
st.sidebar.subheader("🎨 Tema")
theme_option = st.sidebar.selectbox(
    "Seleccionar tema",
    ["Automático (sistema)", "Claro", "Oscuro"],
    help="Cambia el tema de la interfaz. 'Automático' usa la configuración de tu sistema."
)

# Aplicar tema dinámicamente
def apply_theme(theme_choice):
    """Aplica el tema seleccionado mediante CSS personalizado"""
    if theme_choice == "Claro":
        st.markdown("""
        <style>
        /* Tema claro mejorado */
        .stApp {
            background-color: #FFFFFF !important;
            color: #262730 !important;
        }
        .stSidebar {
            background-color: #F0F2F6 !important;
        }
        .stSidebar .stSelectbox > div > div {
            background-color: #FFFFFF !important;
            color: #262730 !important;
        }
        .stButton > button {
            background-color: #FF6B6B !important;
            color: #FFFFFF !important;
            border: none !important;
        }
        .stButton > button[data-testid="baseButton-secondary"] {
            background-color: #6C757D !important;
            color: #FFFFFF !important;
        }
        .stTextInput > div > div > input {
            background-color: #FFFFFF !important;
            color: #262730 !important;
            border: 1px solid #D1D5DB !important;
        }
        .stSlider > div > div > div {
            color: #262730 !important;
        }
        .stCheckbox > label {
            color: #262730 !important;
        }
        .stRadio > label {
            color: #262730 !important;
        }
        .stSelectbox > label {
            color: #262730 !important;
        }
        </style>
        """, unsafe_allow_html=True)
    elif theme_choice == "Oscuro":
        st.markdown("""
        <style>
        /* Tema oscuro mejorado */
        .stApp {
            background-color: #0E1117 !important;
            color: #FAFAFA !important;
        }
        .stSidebar {
            background-color: #262730 !important;
        }
        .stSidebar .stSelectbox > div > div {
            background-color: #262730 !important;
            color: #FAFAFA !important;
        }
        .stButton > button {
            background-color: #FF6B6B !important;
            color: #FFFFFF !important;
            border: none !important;
        }
        .stButton > button[data-testid="baseButton-secondary"] {
            background-color: #6C757D !important;
            color: #FFFFFF !important;
        }
        .stTextInput > div > div > input {
            background-color: #262730 !important;
            color: #FAFAFA !important;
            border: 1px solid #4B5563 !important;
        }
        .stSlider > div > div > div {
            color: #FAFAFA !important;
        }
        .stCheckbox > label {
            color: #FAFAFA !important;
        }
        .stRadio > label {
            color: #FAFAFA !important;
        }
        .stSelectbox > label {
            color: #FAFAFA !important;
        }
        </style>
        """, unsafe_allow_html=True)

if theme_option != "Automático (sistema)":
    apply_theme(theme_option)
    st.sidebar.info(f"💡 Tema aplicado: {theme_option}")

st.sidebar.markdown("---")
st.sidebar.markdown("**Clase detectada:** Personas")
st.sidebar.markdown("**Lugar:** Punto de venta de motos")

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
        
        # Crear archivo temporal para el video con nombre descriptivo
        # Obtener nombre original del archivo
        original_name = os.path.splitext(video_file.name)[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Crear archivo temporal con nombre más descriptivo
        temp_dir = tempfile.gettempdir()
        tmp_video_path = os.path.join(temp_dir, f"streamlit_{original_name}_{timestamp}.mp4")
        
        with open(tmp_video_path, 'wb') as tmp_video:
            tmp_video.write(video_file.read())
        
        # Verificar que el modelo existe
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Modelo no encontrado: {model_path}")
        
        # Verificar que el CLI existe
        cli_path = "src/main.py"
        if not os.path.exists(cli_path):
            raise FileNotFoundError(f"CLI no encontrado: {cli_path}")
        
        # Construir comando
        cmd = [
            sys.executable, cli_path,
            "--video-path", tmp_video_path,
            "--model-path", model_path
        ]
        
        # Agregar flags de visualización
        if config.get("save_video", True):
            cmd.append("--save-video")
        else:
            cmd.append("--no-save-video")
            
        if config.get("show_processing", False):
            cmd.append("--show")
        else:
            cmd.append("--no-show")
        
        # Agregar parámetros opcionales
        if config.get('classes'):
            cmd.extend(["--classes", config['classes']])
        
        if config.get('conf_threshold'):
            cmd.extend(["--conf-threshold", str(config['conf_threshold'])])
        
        if config.get('enable_stats'):
            cmd.append("--enable-stats")
        
        if config.get('enable_zones') and config.get('zones_config'):
            ##cmd.extend(["--enable-zones", "true", "--zones-config", config['zones_config']])
            cmd.append("--enable-zones")
            cmd.extend(["--zones-config", config['zones_config']])
        
        logger.info(f"Ejecutando comando: {' '.join(cmd)}")
        
        # Ejecutar comando con timeout configurable
        timeout_minutes = config.get('timeout_minutes', 30)  # Por defecto 30 minutos
        timeout_seconds = timeout_minutes * 60
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            cwd=os.getcwd(),
            timeout=timeout_seconds
        )
        
        logger.info(f"Análisis completado con código: {result.returncode}")
        
        return result.returncode == 0, result.stdout, result.stderr
        
    except subprocess.TimeoutExpired:
        timeout_msg = f"Análisis excedió el tiempo límite de {timeout_minutes} minutos"
        logger.error(timeout_msg)
        
        # Buscar resultados parciales
        outputs_dir = "outputs"
        partial_results_msg = "\n\n⚠️ RESULTADOS PARCIALES DISPONIBLES:\n"
        
        if os.path.exists(outputs_dir):
            # Buscar CSV parciales
            csv_dirs = [d for d in os.listdir(outputs_dir) if d.startswith('csv_analysis_')]
            if csv_dirs:
                latest_csv_dir = max(csv_dirs, key=lambda x: os.path.getctime(os.path.join(outputs_dir, x)))
                partial_results_msg += f"• Datos CSV parciales en: {latest_csv_dir}\n"
            
            # Buscar video parcial
            video_files = [f for f in os.listdir(outputs_dir) if f.endswith('.mp4')]
            if video_files:
                latest_video = max(video_files, key=lambda x: os.path.getctime(os.path.join(outputs_dir, x)))
                partial_results_msg += f"• Video parcial disponible: {latest_video}\n"
        
        return False, partial_results_msg, timeout_msg
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
use_default_conf = st.sidebar.checkbox(
    "Usar umbral por defecto del modelo",
    value=True,
    help="Si está marcado, usa la configuración por defecto de YOLO (recomendado)"
)

if use_default_conf:
    conf_threshold = None
    st.sidebar.info("🎯 Usando configuración por defecto de YOLO")
else:
    conf_threshold = st.sidebar.slider(
        "Umbral de confianza personalizado",
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

# Configuración de visualización
st.sidebar.subheader("🖥️ Visualización")
show_processing = st.sidebar.checkbox(
    "Mostrar procesamiento en tiempo real",
    value=False,
    help="Muestra una ventana con el video siendo procesado (puede ralentizar el procesamiento)"
)

save_video = st.sidebar.checkbox(
    "Guardar video procesado",
    value=True,
    help="Guarda el video con las detecciones y análisis"
)

# Configuración de timeout
timeout_minutes = st.sidebar.slider(
    "Tiempo límite (minutos)",
    min_value=5,
    max_value=120,
    value=30,
    step=5,
    help="Tiempo máximo para el procesamiento antes de detenerse automáticamente"
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
    configs_dir = Path("configs")
    available_configs = []
    
    # Buscar archivos JSON en subdirectorios de configs
    if os.path.exists(configs_dir):
        for subdir in configs_dir.iterdir():
            if subdir.is_dir():
                json_file = subdir / "zonas.json"
                if json_file.exists():
                    available_configs.append(str(json_file))
        
        # También buscar archivos JSON directamente en configs
        for file in configs_dir.glob("*.json"):
            available_configs.append(str(file))
    
    if available_configs:
        selected_config = st.sidebar.selectbox(
            "Archivo de configuración de zonas",
            available_configs,
            help="Selecciona un archivo JSON con la configuración de zonas"
        )
        zones_config = selected_config
        
        # Mostrar preview de la zona si existe la imagen
        if selected_config:
            config_path = Path(selected_config)
            visual_image_path = config_path.parent / "zonas_visual.png"
            
            if visual_image_path.exists():
                st.sidebar.subheader("🖼️ Vista previa de zonas")
                st.sidebar.image(
                    str(visual_image_path), 
                    caption=f"Configuración: {config_path.parent.name}",
                    use_container_width=True
                )
                
                # Mostrar información adicional de la configuración
                try:
                    import json
                    with open(selected_config, 'r') as f:
                        zone_data = json.load(f)
                    
                    lines_count = len(zone_data.get('lines', []))
                    polygons_count = len(zone_data.get('polygons', []))
                    
                    st.sidebar.info(f"📊 Líneas: {lines_count} | Polígonos: {polygons_count}")
                    
                    # Mostrar nombres de las zonas si existen
                    if lines_count > 0:
                        st.sidebar.markdown("**Líneas configuradas:**")
                        for i, line in enumerate(zone_data.get('lines', []), 1):
                            line_name = line.get('name', f'Línea {i}')
                            st.sidebar.markdown(f"• {line_name}")
                    
                    if polygons_count > 0:
                        st.sidebar.markdown("**Polígonos configurados:**")
                        for i, polygon in enumerate(zone_data.get('polygons', []), 1):
                            poly_name = polygon.get('name', f'Polígono {i}')
                            st.sidebar.markdown(f"• {poly_name}")
                            
                except Exception as e:
                    st.sidebar.warning(f"No se pudo leer la configuración: {e}")
            else:
                st.sidebar.info("💡 No hay imagen de vista previa disponible")
    else:
        st.sidebar.warning("No se encontraron archivos de configuración de zonas")

# Área principal
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📹 Análisis de Video", "📊 Estadísticas", "📍 Eventos de Zonas", "📈 Gráficos", "🖼️ Configuración de Zonas"])

with tab1:
    st.header("Análisis de Video")
    
    # Subida de archivo
    uploaded_file = st.file_uploader(
        "Selecciona un video para analizar",
        type=['mp4', 'avi', 'mov', 'mkv'],
        help=f"Formatos soportados: MP4, AVI, MOV, MKV. Límite máximo: {MAX_FILE_SIZE_MB} MB"
    )
    
    if uploaded_file is not None:
        # Validar tamaño del archivo
        file_size_mb = uploaded_file.size / (1024*1024)
        if file_size_mb > MAX_FILE_SIZE_MB:
            st.error(f"❌ El archivo es demasiado grande ({file_size_mb:.2f} MB). El límite máximo es {MAX_FILE_SIZE_MB} MB.")
            st.info("💡 Para archivos más grandes, considera usar el CLI directamente desde la terminal.")
            st.stop()
        
        # Mostrar información del video
        st.subheader("📋 Información del Video")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Nombre del archivo", uploaded_file.name)
        with col2:
            st.metric("Tamaño", f"{file_size_mb:.2f} MB")
        with col3:
            st.metric("Tipo", uploaded_file.type)
        
        # Mostrar resumen de configuración antes del análisis
        st.subheader("📋 Resumen de Configuración")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Modelo:** {os.path.basename(selected_model)}")
            st.write(f"**Clases:** {'Todas' if not classes_input else classes_input}")
            st.write(f"**Confianza:** {'Por defecto' if conf_threshold is None else f'{conf_threshold:.2f}'}")
            st.write(f"**Estadísticas:** {'✅ Sí' if enable_stats else '❌ No'}")
        
        with col2:
            st.write(f"**Zonas:** {'✅ Sí' if enable_zones else '❌ No'}")
            if enable_zones and zones_config:
                config_name = Path(zones_config).parent.name
                st.write(f"**Config. Zonas:** {config_name}")
            st.write(f"**Guardar Video:** {'✅ Sí' if save_video else '❌ No'}")
            st.write(f"**Tiempo Límite:** {timeout_minutes} minutos")
        
        # Botón para ejecutar análisis
        if st.button("🚀 Ejecutar Análisis", type="primary"):
            # Mostrar información sobre cómo detener el análisis
            st.info("⚠️ **Importante:** Una vez iniciado el análisis, para detenerlo completamente debes:")
            st.markdown("""
            1. **Presionar `Ctrl+C`** en la terminal donde corre Streamlit
            2. **Volver a ejecutar** `uv run streamlit run streamlit_demo.py`
            3. Los **resultados parciales** se guardarán automáticamente
            """)
            
            # Mostrar progreso estimado
            file_size_gb = file_size_mb / 1024
            estimated_time = max(5, int(file_size_gb * 10))  # Estimación básica
            st.warning(f"⏱️ Tiempo estimado: ~{estimated_time} minutos (basado en {file_size_mb:.1f} MB)")
            
            # Crear indicadores de progreso
            progress_bar = st.progress(0)
            status_text = st.empty()
            time_text = st.empty()
            
            # Configuración del análisis
            config = {
                'classes': classes_input if classes_input else None,
                'conf_threshold': conf_threshold,
                'enable_stats': enable_stats,
                'enable_zones': enable_zones,
                'zones_config': zones_config,
                'show_processing': show_processing,
                'save_video': save_video,
                'timeout_minutes': timeout_minutes
            }
            
            # Mostrar progreso inicial
            status_text.text("🚀 Iniciando análisis...")
            progress_bar.progress(10)
            
            import time
            start_time = time.time()
            
            # Ejecutar análisis
            with st.spinner("Procesando video..."):
                success, stdout, stderr = run_video_analysis(uploaded_file, selected_model, config)
            
            # Calcular tiempo transcurrido
            elapsed_time = time.time() - start_time
            time_text.success(f"⏱️ Tiempo de procesamiento: {elapsed_time/60:.1f} minutos")
            progress_bar.progress(100)
            
            if success:
                st.success("✅ Análisis completado exitosamente!")
                
                # Mostrar salida del comando
                if stdout:
                    st.text_area("Salida del análisis:", stdout, height=200)
            else:
                # Verificar si es timeout y hay resultados parciales
                if "tiempo límite" in stderr and "RESULTADOS PARCIALES" in stdout:
                    st.warning("⏱️ Análisis interrumpido por tiempo límite")
                    st.info("📊 Se encontraron resultados parciales que puedes revisar:")
                    if stdout:
                        st.text_area("Resultados parciales:", stdout, height=150)
                    
                    # Intentar cargar datos parciales
                    try:
                        outputs_dir = "outputs"
                        if os.path.exists(outputs_dir):
                            # Buscar el directorio CSV más reciente
                            csv_dirs = [d for d in os.listdir(outputs_dir) if d.startswith('csv_analysis_')]
                            if csv_dirs:
                                latest_dir = max(csv_dirs, key=lambda x: os.path.getctime(os.path.join(outputs_dir, x)))
                                output_dir = os.path.join(outputs_dir, latest_dir)
                                
                                # Cargar datos parciales
                                csv_data = load_csv_data(output_dir)
                                st.session_state.csv_data = csv_data
                                st.session_state.output_dir = output_dir
                                
                                st.success("📈 Datos parciales cargados. Revisa las pestañas de estadísticas y gráficos.")
                    except Exception as e:
                        st.error(f"Error al cargar datos parciales: {e}")
                else:
                    st.error("❌ Error durante el análisis:")
                    if stderr:
                        st.text_area("Error:", stderr, height=200)
                    if stdout:
                        st.text_area("Salida:", stdout, height=200)
                    # No continuar con el procesamiento de archivos si hay error
                    success = False
                
            # Buscar archivos de salida (para éxito o resultados parciales)
            if success or ("RESULTADOS PARCIALES" in stdout):
                outputs_dir = "outputs"
                if os.path.exists(outputs_dir):
                    # Buscar el directorio CSV más reciente
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
                        
                        # Cargar datos CSV si no se han cargado ya
                        if 'csv_data' not in st.session_state:
                            csv_data = load_csv_data(output_dir)
                            st.session_state.csv_data = csv_data
                            st.session_state.output_dir = output_dir

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
        
        # Eventos de zonas (polígonos)
        if csv_data.get('zone_events') is not None and len(csv_data['zone_events']) > 0:
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
        elif csv_data.get('zone_events') is not None:
            st.info("📍 No se detectaron eventos de zona (entradas/salidas de polígonos)")
            st.info("💡 Tu configuración actual solo tiene líneas. Para eventos de zona, agrega polígonos a la configuración.")
        
        # Cruces de líneas
        if csv_data.get('line_crossing_events') is not None and len(csv_data['line_crossing_events']) > 0:
            st.subheader("🔄 Cruces de Líneas")
            df_lines = csv_data['line_crossing_events']
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Cruces", len(df_lines))
            with col2:
                st.metric("🟢 Salidas (Izq → Der)", len(df_lines[df_lines['direction'] == 'left_to_right']))
            with col3:
                st.metric("🔴 Entradas (Der → Izq)", len(df_lines[df_lines['direction'] == 'right_to_left']))
            
            # Gráfico de cruces por dirección
            # direction_counts = df_lines['direction'].value_counts()
            # fig = px.pie(values=direction_counts.values, names=direction_counts.index,
            #             title='Distribución de Cruces por Dirección')
            # st.plotly_chart(fig, use_container_width=True)
            direction_counts = df_lines['direction'].value_counts().reset_index()
            direction_counts.columns = ["direction", "count"]

            fig = px.bar(
                direction_counts,
                x="direction",
                y="count",
                orientation="v",
                title="Distribución de Cruces por Dirección",
                text="count"
            )
            fig.update_layout(yaxis_title="Dirección", xaxis_title="Cantidad")
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabla de cruces
            st.subheader("📋 Detalles de Cruces")
            st.dataframe(df_lines, use_container_width=True)
        elif csv_data.get('line_crossing_events') is not None:
            st.info("🔄 No se detectaron cruces de líneas en este análisis")
            st.info("💡 Verifica que los objetos crucen las líneas configuradas")
        
        # Mensaje si no hay datos de zonas ni líneas
        if (csv_data.get('zone_events') is None or len(csv_data['zone_events']) == 0) and \
           (csv_data.get('line_crossing_events') is None or len(csv_data['line_crossing_events']) == 0):
            st.warning("⚠️ No se encontraron eventos de zonas ni cruces de líneas")
            st.info("💡 Verifica que el análisis de zonas esté habilitado y configurado correctamente")
    else:
        st.info("📊 Ejecuta un análisis de video con zonas habilitadas para ver los eventos")
        st.markdown("""
        **Para ver eventos:**
        1. Habilita "Análisis de zonas" en el panel lateral
        2. Selecciona una configuración de zonas
        3. Ejecuta el análisis de video
        """)

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
            ## fig.update_xaxis(title='Clase')
            ##fig.update_yaxis(title='Número de Detecciones')
            fig.update_layout(
            xaxis_title="Clase",
            yaxis_title="Número de Detecciones"
            ) 
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

with tab5:
    st.header("🖼️ Configuración de Zonas")
    
    if enable_zones and zones_config:
        config_path = Path(zones_config)
        
        # Mostrar imagen grande de la configuración
        visual_image_path = config_path.parent / "zonas_visual.png"
        if visual_image_path.exists():
            st.subheader(f"Vista de Configuración: {config_path.parent.name}")
            
            # Mostrar imagen en tamaño completo
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.image(
                    str(visual_image_path), 
                    caption="Zonas configuradas para análisis",
                    use_container_width=True
                )
            
            with col2:
                # Información detallada de la configuración
                try:
                    import json
                    with open(zones_config, 'r') as f:
                        zone_data = json.load(f)
                    
                    st.subheader("📊 Resumen de Configuración")
                    
                    lines_count = len(zone_data.get('lines', []))
                    polygons_count = len(zone_data.get('polygons', []))
                    
                    st.metric("Líneas", lines_count)
                    st.metric("Polígonos", polygons_count)
                    
                    # Detalles de líneas
                    if lines_count > 0:
                        st.subheader("📏 Líneas Configuradas")
                        for i, line in enumerate(zone_data.get('lines', []), 1):
                            line_name = line.get('name', f'Línea {i}')
                            line_id = line.get('id', f'line_{i}')
                            coords = line.get('coordinates', [])
                            
                            with st.expander(f"🔸 {line_name}"):
                                st.write(f"**ID:** {line_id}")
                                st.write(f"**Nombre:** {line_name}")
                                if coords and len(coords) >= 2:
                                    st.write(f"**Punto 1:** ({coords[0][0]}, {coords[0][1]})")
                                    st.write(f"**Punto 2:** ({coords[1][0]}, {coords[1][1]})")
                                st.write("**Función:** Detecta cruces de personas/objetos")
                    
                    # Detalles de polígonos
                    if polygons_count > 0:
                        st.subheader("📐 Polígonos Configurados")
                        for i, polygon in enumerate(zone_data.get('polygons', []), 1):
                            poly_name = polygon.get('name', f'Polígono {i}')
                            poly_id = polygon.get('id', f'polygon_{i}')
                            coords = polygon.get('coordinates', [])
                            
                            with st.expander(f"🔹 {poly_name}"):
                                st.write(f"**ID:** {poly_id}")
                                st.write(f"**Nombre:** {poly_name}")
                                st.write(f"**Puntos:** {len(coords)} vértices")
                                st.write("**Función:** Detecta entradas y salidas de zona")
                    
                    # Mostrar JSON raw si se desea
                    if st.checkbox("Mostrar configuración JSON"):
                        st.subheader("📄 Configuración JSON")
                        st.json(zone_data)
                        
                except Exception as e:
                    st.error(f"Error al leer la configuración: {e}")
        else:
            st.warning("No se encontró la imagen de visualización de zonas")
            st.info("💡 Para generar la imagen de visualización, usa la herramienta de configuración de zonas")
    
    elif enable_zones and not zones_config:
        st.info("Selecciona una configuración de zonas en el panel lateral para ver la vista previa")
    
    else:
        st.info("Habilita el análisis de zonas en el panel lateral para ver las configuraciones disponibles")
        
        # Mostrar configuraciones disponibles sin habilitar zonas
        st.subheader("📂 Configuraciones Disponibles")
        configs_dir = Path("configs")
        if configs_dir.exists():
            available_configs = []
            for subdir in configs_dir.iterdir():
                if subdir.is_dir():
                    json_file = subdir / "zonas.json"
                    visual_file = subdir / "zonas_visual.png"
                    if json_file.exists():
                        available_configs.append((str(json_file), visual_file.exists()))
            
            if available_configs:
                st.write(f"Se encontraron {len(available_configs)} configuraciones:")
                
                for config_path, has_visual in available_configs:
                    config_name = Path(config_path).parent.name
                    visual_status = "✅ Con imagen" if has_visual else "❌ Sin imagen"
                    st.write(f"• **{config_name}** - {visual_status}")
            else:
                st.write("No se encontraron configuraciones de zonas")
        else:
            st.write("El directorio 'configs' no existe")

# Footer
st.markdown("---")
st.markdown("**FlowSense Demo** - Análisis de video con YOLO, tracking y análisis de zonas")
st.markdown("Desarrollado con ❤️ usando Streamlit")
