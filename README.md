# Proyecto de Procesamiento de Videos con YOLOv8

## Descripción

Este proyecto implementa un sistema completo de detección y análisis de objetos en imágenes y videos usando YOLOv8. Incluye funcionalidades avanzadas como tracking de objetos, análisis de zonas de interés, y un sistema de confirmación mejorado para reducir falsos negativos.

## Características Principales

### 🎯 **Detección Mejorada**
- **Sistema de confirmación**: Solo asigna IDs a objetos que aparecen en 5+ frames consecutivos
- **Tracking persistente**: Mantiene identidad de objetos entre frames
- **Umbral de confianza configurable**: Por defecto 0.25 para máxima sensibilidad
- **Filtrado inteligente**: Reduce falsos positivos y falsos negativos

### 📹 **Funcionalidades de Video**
- **Detección básica**: Identificación de objetos en tiempo real
- **Tracking avanzado**: Seguimiento de objetos con IDs únicos y trayectorias
- **Análisis de zonas**: Detección de entrada en áreas específicas y cruce de líneas
- **Estadísticas en tiempo real**: Contadores de frames y detecciones

### 🖼️ **Procesamiento de Imágenes**
- **Detección de objetos**: Identificación con bounding boxes y etiquetas
- **Colores dinámicos**: Verde para alta confianza, naranja para baja
- **Fondo negro en etiquetas**: Mejor visibilidad del texto

## Instalación

```bash
# Clonar el repositorio
git clone <repository-url>
cd videos_yolo

# Instalar dependencias
pip install -r requirements.txt
```

## 🚀 **Sistema Unificado (Recomendado)**

### **Comando Principal: `process`**
```bash
# Solo tracking (por defecto)
uv run src/main.py process \
    --video-path "data/videos/video.mp4" \
    --model-path "models/yolov8n.pt"

# Con estadísticas por frame
uv run src/main.py process \
    --video-path "data/videos/video.mp4" \
    --model-path "models/yolov8n.pt" \
    --enable-stats

# Con zonas de interés
uv run src/main.py process \
    --video-path "data/videos/video.mp4" \
    --model-path "models/yolov8n.pt" \
    --enable-zones "configs/zonas.json"

# Con todas las funcionalidades
uv run src/main.py process \
    --video-path "data/videos/video.mp4" \
    --model-path "models/yolov8n.pt" \
    --enable-stats \
    --enable-zones "configs/zonas.json"
```

## 🎯 **Configuración de Zonas de Interés**

### **Script Interactivo de Configuración Mejorado**
```bash
# Desde cualquier directorio
uv run python src/utils/ejm_tracking.py --help

# Usar imagen existente
uv run python src/utils/ejm_tracking.py --image "imagen.png"

# Extraer frame de video y configurar zonas (Recomendado)
uv run python src/utils/ejm_tracking.py --video "video.mp4" --frame 5

# Solo líneas o solo polígonos
uv run python src/utils/ejm_tracking.py --image "imagen.png" --lines-only
uv run python src/utils/ejm_tracking.py --image "imagen.png" --polygons-only
```

**Ventajas:**
- ✅ **Parámetros de línea de comandos** (no más rutas hardcodeadas)
- ✅ **Extracción automática de frames** desde videos
- ✅ **Múltiples líneas y polígonos** en una sesión
- ✅ **Archivos de salida personalizados**
- ✅ **Validación automática** de archivos

### **Documentación Completa**
Ver `CONFIGURACION_ZONAS_README.md` para instrucciones detalladas.

## 📚 **Comandos Antiguos (Deprecados)**

> **Nota**: Se recomienda usar el nuevo comando `process` unificado.

### Detección en Imágenes
```bash
python src/main.py \
    --image "data/images/person.jpg" \
    --model "models/yolov8x.pt" \
    --conf-threshold 0.25 \
    --show
```

### Procesamiento de Video
```bash
python src/main.py video \
    --video-path "data/videos/people.mp4" \
    --model-path "models/yolov8x.pt" \
    --conf-threshold 0.25 \
    --show
```

### Tracking de Objetos
```bash
python src/main.py track \
    --video-path "data/videos/people.mp4" \
    --model-path "models/yolov8x.pt" \
    --show
```

### Análisis con Zonas de Interés
```bash
python src/main.py analyze \
    --video-path "data/videos/people.mp4" \
    --model-path "models/yolov8x.pt" \
    --zones-json "configs/zonas.json" \
    --conf-threshold 0.25 \
    --show
```

## Parámetros Principales

- `--conf-threshold`: Umbral de confianza (0.0-1.0, por defecto 0.25)
- `--classes`: Lista de clases a detectar (ej: "person,car,dog")
- `--show`: Mostrar visualización en tiempo real
- `--output`: Ruta de salida personalizada

## Modelos Recomendados

Para lograr la **máxima detección** de personas:

1. **YOLOv8x** (`yolov8x.pt`) - Máxima precisión
2. **YOLOv8l** (`yolov8l.pt`) - Alta precisión
3. **YOLOv8m** (`yolov8m.pt`) - Buena precisión

> **Nota**: Los modelos más grandes requieren GPU para tiempo real.

## 🎯 **Ventajas del Sistema Unificado**

### ✅ **Consistencia Perfecta**
- **Tracking siempre activo** para máxima precisión
- **Mismos resultados** entre ejecuciones
- **Sin pérdida de detecciones** como en comandos antiguos

### ✅ **Simplicidad de Uso**
- **Un solo comando** (`process`) para todas las funcionalidades
- **Flags opcionales** para habilitar características
- **Nombres de archivos inteligentes** según funcionalidades activadas

### ✅ **Funcionalidades Avanzadas**
- **Estadísticas por frame** con conteo de objetos en zonas
- **Análisis de zonas** con alertas en tiempo real
- **Tracking estable** con IDs únicos confirmados

## 🔧 **Mejoras Implementadas**

### **Sistema de Confirmación**
- Filtra detecciones breves (menos de 5 frames)
- Asigna IDs estables y secuenciales
- Reduce falsos positivos automáticamente

### **Visualización Mejorada**
- Colores basados en confianza
- Trayectorias de movimiento
- Etiquetas con fondo negro
- Estadísticas en tiempo real

### **Optimizaciones de Rendimiento**
- Tracking persistente habilitado
- Umbral de confianza configurable
- Procesamiento eficiente de frames

## Estructura del Proyecto

```
videos_yolo/
├── src/
│   ├── main.py              # CLI principal (sistema unificado)
│   ├── video_unified.py     # Analizador unificado con tracking
│   ├── detect.py            # Detección en imágenes
│   ├── tracking.py          # Tracking de objetos (legacy)
│   ├── video_processing.py  # Procesamiento de video (legacy)
│   ├── video_analysis.py    # Análisis avanzado (legacy)
│   └── utils/               # Utilidades
│       ├── ejm_tracking.py  # Script de configuración de zonas
│       ├── file_manager.py  # Gestión de archivos
│       ├── geometry.py      # Funciones geométricas
│       └── coco_classes.py  # Clases COCO
├── models/                  # Modelos YOLO
├── configs/                 # Configuraciones (zonas.json)
├── data/                    # Datos de entrada
├── outputs/                 # Resultados
└── docs/                    # Documentación
    ├── ANALIZADOR_UNIFICADO_README.md
    ├── CONFIGURACION_ZONAS_README.md
    └── RESUMEN_CONSOLIDACION.md
```

## Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📚 **Documentación Adicional**

### **Guías Detalladas**
- **`ANALIZADOR_UNIFICADO_README.md`** - Sistema unificado completo
- **`CONFIGURACION_ZONAS_README.md`** - Configuración de zonas y líneas
- **`RESUMEN_CONSOLIDACION.md`** - Resumen de la consolidación

### **Scripts de Configuración**
- **`src/utils/ejm_tracking.py`** - Configuración interactiva de zonas
- **`configs/zonas.json`** - Archivo de configuración de zonas

## 🚀 **Inicio Rápido**

### **1. Instalación**
```bash
git clone <repository-url>
cd videos_yolo
pip install -r requirements.txt
```

### **2. Uso Básico**
```bash
# Solo tracking
uv run src/main.py process \
    --video-path "data/videos/video.mp4" \
    --model-path "models/yolov8n.pt"
```

### **3. Configurar Zonas**
```bash
cd src/utils
python ejm_tracking.py
# Seguir instrucciones interactivas
```

### **4. Análisis Completo**
```bash
uv run src/main.py process \
    --video-path "data/videos/video.mp4" \
    --model-path "models/yolov8n.pt" \
    --enable-stats \
    --enable-zones "configs/zonas.json"
```

## Agradecimientos

- [Ultralytics](https://github.com/ultralytics/ultralytics) por YOLOv8
- [OpenCV](https://opencv.org/) por el procesamiento de video
- [Typer](https://typer.tiangolo.com/) por la interfaz CLI