# 🚀 Sistema de Análisis de Video con YOLOv8

## 📋 Descripción

Sistema completo de detección y análisis de objetos en videos usando YOLOv8 con funcionalidades avanzadas como tracking de objetos, análisis de zonas de interés, y un sistema de confirmación mejorado para reducir falsos negativos.

## ✨ Características Principales

### 🎯 **Detección Mejorada**
- **Detección universal**: Por defecto detecta TODOS los objetos disponibles (80 clases COCO)
- **Filtrado opcional**: Usar `--classes` para detectar solo objetos específicos
- **Tracking persistente**: Mantiene identidad de objetos entre frames
- **Umbral de confianza configurable**: Por defecto usa configuración de YOLO para máxima detección
- **Filtrado inteligente**: Reduce falsos positivos y falsos negativos

### 📹 **Funcionalidades de Video**
- **Detección básica**: Identificación de objetos en tiempo real
- **Tracking avanzado**: Seguimiento de objetos con IDs únicos y trayectorias
- **Análisis de zonas**: Detección de entrada/salida en áreas específicas y cruce de líneas
- **Estadísticas en tiempo real**: Contadores de frames y detecciones
- **Persistencia CSV**: Guardado optimizado de eventos significativos

### 🖼️ **Procesamiento de Imágenes**
- **Detección de objetos**: Identificación con bounding boxes y etiquetas
- **Colores dinámicos**: Verde para alta confianza, naranja para baja
- **Fondo negro en etiquetas**: Mejor visibilidad del texto

### 📁 **Gestión Inteligente de Archivos**
- **Nombres únicos automáticos**: Timestamp para evitar sobrescrituras
- **Nombres personalizados**: Control total sobre nombres de archivos
- **Estadísticas sincronizadas**: Mismo nombre base que el video + `_stats`
- **Organización automática**: Archivos relacionados con nombres relacionados

## 🚀 **Sistema Unificado (Recomendado)**

### **Comando Principal: `process`**
```bash
# Solo tracking (por defecto)
uv run src/main.py \
    --video-path "data/videos/video.mp4" \
    --model-path "models/yolov8n.pt"

# Detectar solo personas y coches
uv run src/main.py \
    --video-path "data/videos/video.mp4" \
    --model-path "models/yolov8n.pt" \
    --classes "person,car"

# Detectar solo animales
uv run src/main.py \
    --video-path "data/videos/video.mp4" \
    --model-path "models/yolov8n.pt" \
    --classes "dog,cat,bird"

# Con estadísticas por frame
uv run src/main.py \
    --video-path "data/videos/video.mp4" \
    --model-path "models/yolov8n.pt" \
    --enable-stats

# Con zonas de interés
uv run src/main.py \
    --video-path "data/videos/video.mp4" \
    --model-path "models/yolov8n.pt" \
    --enable-zones "configs/zonas.json"

# Con todas las funcionalidades
uv run src/main.py \
    --video-path "data/videos/video.mp4" \
    --model-path "models/yolov8n.pt" \
    --enable-stats \
    --enable-zones "configs/zonas.json" \
    --enable-database
```

### **Parámetros Disponibles**

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `--video-path` | str | ✅ | Ruta del archivo de video de entrada |
| `--model-path` | str | ✅ | Ruta al modelo YOLO (ej: yolov8n.pt) |
| `--output-path` | str | ❌ | Ruta para guardar el video de salida |
| `--show` | bool | ❌ | Mostrar visualización en tiempo real (default: True) |
| `--classes` | str | ❌ | Lista de objetos a detectar (ej: person,car,dog). Por defecto: detecta TODOS los objetos. Ver clases disponibles en: https://github.com/ultralytics/ultralytics/blob/main/ultralytics/cfg/datasets/coco.yaml |
| `--conf-threshold` | float | ❌ | Umbral de confianza para detecciones (0.0-1.0). Si no se especifica, usa la configuración por defecto de YOLO |
| `--enable-stats` | bool | ❌ | Habilitar generación de estadísticas por frame |
| `--enable-zones` | str | ❌ | Ruta al archivo JSON de configuración de zonas |
| `--save-video` | bool | ❌ | Guardar video procesado (default: True) |
| `--enable-database` | bool | ❌ | Habilitar funcionalidad de base de datos |

## 🎯 **¿Por qué Tracking Siempre Activo?**

### **✅ Ventajas del Tracking Constante**

| Aspecto | Tracking Constante | Modo Básico |
|---------|-------------------|-------------|
| **Consistencia** | ✅ **Perfecta** | ❌ Variable |
| **Precisión** | ✅ **Mayor** | ❌ Menor |
| **Estabilidad** | ✅ **Estable** | ❌ Inestable |
| **Funcionalidad** | ✅ **Completa** | ❌ Limitada |
| **IDs únicos** | ✅ **Sí** | ❌ No |
| **Trayectorias** | ✅ **Sí** | ❌ No |

**Evidencia Técnica**: El tracking detecta EXACTAMENTE lo mismo que la base de comparación, pero con mayor estabilidad y funcionalidades adicionales.

## 📁 **Gestión de Archivos de Salida**

### **Nombres Automáticos (Sin Sobrescritura)**
Cuando no especificas `--output-path`, el sistema genera nombres únicos automáticamente:

```bash
# Genera nombres únicos con timestamp
uv run src/main.py \
    --video-path "data/videos/video_2.mp4" \
    --model-path "models/yolov8n.pt" \
    --enable-stats \
    --enable-zones "configs/zonas.json"
```

**Resultado:**
- Video: `outputs/video_2_yolov8n_stats_zones_20250818_213232.mp4`
- Estadísticas: `outputs/video_2_yolov8n_stats_zones_20250818_213232_stats.txt`
- CSV: `outputs/csv_analysis_20250818_213232/`

### **Nombres Personalizados**
Cuando especificas `--output-path`, las estadísticas usan el mismo nombre base:

```bash
# Nombres personalizados
uv run src/main.py \
    --video-path "data/videos/video_2.mp4" \
    --model-path "models/yolov8n.pt" \
    --enable-stats \
    --enable-zones "configs/zonas.json" \
    --output-path "outputs/video_2_lineas_entrada.mp4"
```

**Resultado:**
- Video: `outputs/video_2_lineas_entrada.mp4`
- Estadísticas: `outputs/video_2_lineas_entrada_stats.txt`

### **Sistema de Nomenclatura Inteligente**
Los archivos se nombran automáticamente según las funcionalidades activadas:

| Funcionalidades | Video | Estadísticas |
|-----------------|-------|--------------|
| **Solo tracking** | `video_model_track.mp4` | `video_model_track_stats.txt` |
| **Tracking + stats** | `video_model_stats.mp4` | `video_model_stats_stats.txt` |
| **Tracking + zones** | `video_model_zones.mp4` | `video_model_zones_stats.txt` |
| **Todo activado** | `video_model_stats_zones.mp4` | `video_model_stats_zones_stats.txt` |

## 🎯 **Configuración de Zonas de Interés**

### **Sistema Simplificado de Configuración**
```bash
# Configurar solo líneas
uv run python src/utils/configurar_zonas.py --lines --video "video.mp4" --frame 5

# Configurar solo polígonos
uv run python src/utils/configurar_zonas.py --polygons --image "imagen.png"

# Configurar ambos en una sesión
uv run python src/utils/configurar_zonas.py --lines --polygons --video "video.mp4" --frame 10

# Con descripción personalizada
uv run python src/utils/configurar_zonas.py --lines --video "video.mp4" --description "entrada_principal"

# Listar configuraciones existentes
uv run python src/utils/listar_configuraciones.py
```

### **Ventajas del Sistema Simplificado**
- ✅ **Configuración separada** (líneas y polígonos por separado)
- ✅ **Nombres únicos** con timestamp y descripción
- ✅ **Organización automática** en directorios separados
- ✅ **Imagen automática** siempre se guarda
- ✅ **Sin sobrescritura** de configuraciones anteriores

### **Estructura de Organización**
```
configs/
├── lineas_entrada_principal_20250818_192959/
│   ├── zonas.json          # ✅ Configuración específica
│   ├── zonas_visual.png    # ✅ Imagen con líneas
│   └── frame_original.png  # ✅ Frame de referencia
├── polygonos_zonas_restriccion_20250818_193036/
│   ├── zonas.json          # ✅ Configuración específica
│   ├── zonas_visual.png    # ✅ Imagen con polígonos
│   └── frame_original.png  # ✅ Frame de referencia
└── completa_edificio_20250818_193100/
    ├── zonas.json          # ✅ Configuración completa
    ├── zonas_visual.png    # ✅ Imagen con todo
    └── frame_original.png  # ✅ Frame de referencia
```

## 📊 **Sistema de Persistencia CSV**

### **Eventos Optimizados**
El sistema guarda solo eventos significativos, reduciendo el almacenamiento en un **99%**:

#### **Eventos de Zona (Polígonos)**
```csv
id,analysis_id,zone_id,zone_name,track_id,event_type,frame_number,timestamp_ms,position_x,position_y,created_at
event_1_1_40,1,zone_polygon_2,polygon_2,enter,1,40,1501,554
event_4_44_1760,4,zone_polygon_1,polygon_1,exit,44,1760,253,671
```

#### **Cruces de Línea**
```csv
id,analysis_id,line_id,line_name,track_id,direction,frame_number,timestamp_ms,position_x,position_y,created_at
event_1_15_600,1,line_1,linea_entrada,left_to_right,15,600,200,300
```

### **Archivos CSV Generados**
- `zone_events.csv` - Entradas y salidas de zonas
- `line_crossing_events.csv` - Cruces de líneas
- `minute_statistics.csv` - Estadísticas por minuto
- `frame_detections.csv` - Detecciones por frame (sin optimizar)

## 🗄️ **Integración con Base de Datos**

### **Funcionalidad Opcional**
El sistema mantiene toda su funcionalidad actual mientras agrega opcionalmente el guardado optimizado en PostgreSQL:

```bash
# Análisis tradicional (sin BD)
uv run src/main.py \
    --video-path "data/videos/video_2.mp4" \
    --model-path "models/yolov8n.pt" \
    --enable-stats \
    --enable-zones "configs/zonas.json"

# Análisis con base de datos
uv run src/main.py \
    --video-path "data/videos/video_2.mp4" \
    --model-path "models/yolov8n.pt" \
    --enable-stats \
    --enable-zones "configs/zonas.json" \
    --enable-database
```

### **Ventajas de la Base de Datos**
- ✅ **Solo eventos significativos** (entrada/salida de zonas, cruces de línea)
- ✅ **Reducción de 99%** en almacenamiento
- ✅ **Consultas SQL rápidas**
- ✅ **Escalabilidad mejorada**

## 📚 **Comandos Antiguos (Deprecados)**

> **Nota**: Se recomienda usar el nuevo comando unificado.

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
uv run src/main.py \
    --video-path "data/videos/video.mp4" \
    --model-path "models/yolov8n.pt"
```

### **3. Configurar Zonas**
```bash
# Configuración simplificada
uv run python src/utils/configurar_zonas.py --lines --video "video.mp4" --frame 5
```

### **4. Análisis Completo**
```bash
uv run src/main.py \
    --video-path "data/videos/video.mp4" \
    --model-path "models/yolov8n.pt" \
    --enable-stats \
    --enable-zones "configs/zonas.json"
```

### **5. Con Nombres Personalizados**
```bash
uv run src/main.py \
    --video-path "data/videos/video.mp4" \
    --model-path "models/yolov8n.pt" \
    --enable-stats \
    --enable-zones "configs/zonas.json" \
    --output-path "outputs/video_2_analisis_completo.mp4"
```

## 📁 Estructura del Proyecto

```
videos_yolo/
├── src/
│   ├── main.py              # CLI principal (sistema unificado)
│   ├── video_unified.py     # Analizador unificado con tracking
│   ├── persistence/         # Sistema de persistencia CSV
│   │   └── csv_writer.py    # Escritor optimizado de eventos
│   ├── database/            # Sistema de base de datos
│   │   ├── connection.py    # Conexión a PostgreSQL
│   │   ├── models.py        # Modelos de datos
│   │   └── service.py       # Servicio de BD
│   └── utils/               # Utilidades
│       ├── configurar_zonas.py  # Configuración simplificada de zonas
│       ├── listar_configuraciones.py  # Gestión de configuraciones
│       ├── file_manager.py  # Gestión de archivos
│       ├── geometry.py      # Funciones geométricas
│       └── coco_classes.py  # Clases COCO
├── models/                  # Modelos YOLO
├── configs/                 # Configuraciones (zonas.json)
├── data/                    # Datos de entrada
│   ├── images/              # Imágenes de prueba
│   └── videos/              # Videos de prueba
├── outputs/                 # Resultados
│   └── csv_analysis_*/      # Análisis CSV optimizados
└── examples/                # Ejemplos de salida
```

## 🎯 **Ventajas del Sistema Unificado**

### ✅ **Consistencia Perfecta**
- **Tracking siempre activo** para máxima precisión
- **Mismos resultados** entre ejecuciones
- **Sin pérdida de detecciones** como en comandos antiguos

### ✅ **Simplicidad de Uso**
- **Un solo comando** para todas las funcionalidades
- **Flags opcionales** para habilitar características
- **Nombres de archivos inteligentes** según funcionalidades activadas

### ✅ **Funcionalidades Avanzadas**
- **Estadísticas por frame** con conteo de objetos en zonas
- **Análisis de zonas** con alertas en tiempo real
- **Tracking estable** con IDs únicos confirmados
- **Persistencia optimizada** con solo eventos significativos

### ✅ **Gestión Inteligente de Archivos**
- **Sin sobrescrituras** con nombres únicos automáticos
- **Nombres descriptivos** para fácil identificación
- **Organización automática** de archivos relacionados
- **Flexibilidad total** para nombres personalizados

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
- Persistencia optimizada (99% menos datos)

### **Gestión de Archivos**
- Nombres únicos con timestamp automático
- Sincronización entre video y estadísticas
- Prevención de sobrescrituras
- Organización inteligente de archivos

## Modelos Recomendados

Para lograr la **máxima detección** de personas:

1. **YOLOv8x** (`yolov8x.pt`) - Máxima precisión
2. **YOLOv8l** (`yolov8l.pt`) - Alta precisión
3. **YOLOv8m** (`yolov8m.pt`) - Buena precisión

> **Nota**: Los modelos más grandes requieren GPU para tiempo real.

## 📚 **Documentación Adicional**

### **Guías Detalladas**
- **`FASES_PROYECTO.md`** - Historial completo del desarrollo del proyecto
- **`FASE_9_DATABASE_README.md`** - Documentación detallada de la integración con base de datos

### **Scripts de Configuración**
- **`src/utils/configurar_zonas.py`** - Configuración simplificada de zonas
- **`src/utils/listar_configuraciones.py`** - Gestión de configuraciones
- **`configs/zonas.json`** - Archivo de configuración de zonas

## Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## Agradecimientos

- [Ultralytics](https://github.com/ultralytics/ultralytics) por YOLOv8
- [OpenCV](https://opencv.org/) por el procesamiento de video
- [Typer](https://typer.tiangolo.com/) por la interfaz CLI