# 🎥 FlowSense Demo - Streamlit

Demo interactivo de Streamlit para mostrar la funcionalidad de FlowSense, una aplicación de análisis de video con YOLO, tracking de objetos y análisis de zonas.

## 🚀 Características del Demo

### 📹 Análisis de Video
- **Subida de videos**: Soporta formatos MP4, AVI, MOV, MKV
- **Configuración de modelos**: Selección de diferentes modelos YOLO
- **Parámetros personalizables**: 
  - Clases de objetos a detectar
  - Umbral de confianza
  - Análisis de estadísticas
  - Análisis de zonas

### 📊 Visualización de Datos
- **Estadísticas en tiempo real**: Detecciones por frame, IDs únicos, confianza promedio
- **Gráficos interactivos**: Distribución de confianza, clases detectadas, trayectorias
- **Eventos de zonas**: Entradas/salidas de zonas, cruces de líneas
- **Estadísticas por minuto**: Resúmenes temporales del análisis

### 📈 Gráficos y Análisis
- **Trayectorias de objetos**: Visualización de movimientos
- **Distribución de confianza**: Histogramas de confianza de detecciones
- **Análisis de clases**: Conteo de objetos por tipo
- **Eventos temporales**: Cronología de eventos de zonas

## 🛠️ Instalación

### 1. Instalar dependencias de Streamlit
```bash
# Con uv (recomendado)
uv pip install -r requirements_streamlit.txt

# O con pip tradicional
pip install -r requirements_streamlit.txt
```

### 2. Asegurar que tienes los modelos YOLO
El demo busca modelos en el directorio `models/`. Asegúrate de tener al menos un modelo:
```bash
# Ejemplo: descargar YOLOv8n
wget https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.pt -P models/
```

### 3. Ejecutar el demo
```bash
# Opción 1: Configuración automática (recomendado)
./setup_streamlit_demo.sh

# Opción 2: Ejecutar directamente con uv (recomendado para este proyecto)
uv run streamlit run streamlit_demo.py

# Opción 3: Ejecutar en modo headless (sin interacciones)
uv run streamlit run streamlit_demo.py --server.headless true

# Opción 4: Instalación manual con uv
uv pip install -r requirements_streamlit.txt
uv run streamlit run streamlit_demo.py
```

## 📁 Estructura de Archivos

```
├── streamlit_demo.py          # Aplicación principal de Streamlit
├── requirements_streamlit.txt # Dependencias específicas del demo
├── README_streamlit.md        # Esta documentación
├── models/                    # Modelos YOLO
│   ├── yolov8n.pt
│   ├── yolov8l.pt
│   └── ...
├── configs/                   # Configuraciones de zonas
│   ├── zonas.json
│   └── ...
└── outputs/                   # Salidas del análisis
    ├── csv_analysis_*/
    └── *.mp4
```

## 🎯 Uso del Demo

### 1. Configuración Inicial
- **Selecciona un modelo YOLO** en el sidebar
- **Configura las clases** a detectar (opcional)
- **Ajusta el umbral de confianza**
- **Habilita estadísticas y zonas** según necesites

### 2. Análisis de Video
- **Sube un video** en la pestaña "Análisis de Video"
- **Revisa la información** del archivo
- **Ejecuta el análisis** con el botón "🚀 Ejecutar Análisis"
- **Visualiza el video procesado** con detecciones y tracking

### 3. Exploración de Datos
- **Estadísticas**: Ve métricas generales y gráficos por frame
- **Eventos de Zonas**: Analiza entradas/salidas y cruces de líneas
- **Gráficos**: Explora trayectorias y distribuciones

## 🔧 Configuración Avanzada

### Archivos de Configuración de Zonas
Para usar análisis de zonas, necesitas archivos JSON con la configuración:

```json
{
  "polygons": [
    {
      "name": "zona_entrada",
      "points": [[100, 100], [200, 100], [200, 200], [100, 200]]
    }
  ],
  "lines": [
    {
      "name": "linea_entrada", 
      "points": [[50, 150], [250, 150]]
    }
  ]
}
```

### Modelos YOLO Soportados
- YOLOv8n (nano) - Más rápido, menos preciso
- YOLOv8s (small) - Balanceado
- YOLOv8m (medium) - Más preciso, más lento
- YOLOv8l (large) - Muy preciso, lento
- YOLOv8x (extra large) - Máxima precisión, muy lento

## 📊 Datos Generados

El demo genera varios archivos CSV con información detallada:

### frame_detections.csv
- Detecciones por frame con posición, confianza y track ID
- Información de bounding boxes y centroides

### zone_events.csv
- Eventos de entrada/salida de zonas
- Timestamps y posiciones de eventos

### line_crossing_events.csv
- Cruces de líneas con dirección
- Información temporal y espacial

### minute_statistics.csv
- Estadísticas agregadas por minuto
- Resúmenes de actividad

## 🎨 Personalización

### Temas y Estilos
El demo usa el tema por defecto de Streamlit. Puedes personalizarlo creando un archivo `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
```

### Agregar Nuevas Visualizaciones
Puedes extender el demo agregando nuevas pestañas o gráficos en `streamlit_demo.py`.

## 🐛 Solución de Problemas

### Error: "No se encontraron modelos YOLO"
- Asegúrate de tener archivos `.pt` en el directorio `models/`
- Descarga modelos desde: https://github.com/ultralytics/assets/releases

### Error: "Video no encontrado"
- Verifica que el análisis se completó correctamente
- Revisa los logs en la consola de Streamlit

### Error: "No se pudieron cargar datos CSV"
- Asegúrate de que el análisis generó archivos CSV
- Verifica que el directorio `outputs/` existe

## 📝 Notas Técnicas

- El demo ejecuta el CLI de FlowSense en segundo plano
- Los videos se procesan temporalmente para evitar conflictos
- Los datos se cargan dinámicamente desde los archivos CSV generados
- La interfaz es completamente reactiva y se actualiza automáticamente

## 🤝 Contribuciones

Para mejorar el demo:
1. Agrega nuevas visualizaciones
2. Mejora la interfaz de usuario
3. Optimiza el rendimiento
4. Agrega más opciones de configuración

## ⚠️ Limitaciones y Consideraciones

### Tamaño de Archivos
- **Límite aumentado**: Se ha configurado un límite de 1GB para carga de archivos (por defecto era 200MB)
- **Configuración**: El límite se puede ajustar en `.streamlit/config.toml`
- **Alternativa**: Para archivos más grandes, usa el CLI directamente desde la terminal

### Configuración de Confianza
- **Por defecto**: Usa la configuración por defecto de YOLO (recomendado)
- **Personalizado**: Opción para establecer umbral personalizado si es necesario
- **Consistencia**: Ahora coincide con el comportamiento del CLI

### Visualización
- **Procesamiento en tiempo real**: Opcional, puede ralentizar el análisis
- **Video guardado**: Opción para guardar o no el video procesado
- **Rendimiento**: Deshabilitar visualización mejora la velocidad

### Rendimiento
- **Memoria**: Videos muy largos pueden requerir mucha RAM
- **Procesamiento**: El análisis puede ser lento para videos grandes
- **Optimización**: Considera usar el CLI para análisis en lotes

## 📄 Licencia

Este demo es parte del proyecto FlowSense y sigue la misma licencia.
