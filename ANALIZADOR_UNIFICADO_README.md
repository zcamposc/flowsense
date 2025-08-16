# 🚀 Analizador de Video Unificado

## Descripción

El nuevo comando `process` unifica todas las funcionalidades de análisis de video en un solo comando configurable, eliminando la confusión de tener múltiples comandos separados.

## ✨ Funcionalidades Unificadas

### **1. Detección Básica** (siempre activa)
- Detección de objetos con YOLO
- Bounding boxes con etiquetas
- Colores basados en confianza
- Estadísticas en tiempo real

### **2. Tracking de Objetos** (opcional: `--enable-tracking`)
- Seguimiento de objetos entre frames
- IDs únicos y estables
- Trayectorias visuales
- Filtrado de detecciones inestables (5+ frames)

### **3. Estadísticas por Frame** (opcional: `--enable-stats`)
- Archivo de texto con estadísticas por frame
- Objetos detectados, IDs confirmados, IDs únicos
- En zonas y cruzando líneas (si están habilitadas)

### **4. Análisis de Zonas** (opcional: `--enable-zones`)
- Zonas de interés (polígonos)
- Líneas de cruce
- Alertas automáticas
- Visualización de zonas en el video

## 🎯 Uso del Comando Unificado

### **Sintaxis Básica**
```bash
uv run src/main.py process \
    --video-path "video.mp4" \
    --model-path "model.pt"
```

### **Ejemplos de Uso**

#### **1. Solo Detección Básica** (equivalente al antiguo `video`)
```bash
uv run src/main.py process \
    --video-path "data/videos/video_2.mp4" \
    --model-path "models/yolov8n.pt" \
    --show
```

#### **2. Con Tracking** (equivalente al antiguo `track`)
```bash
uv run src/main.py process \
    --video-path "data/videos/video_2.mp4" \
    --model-path "models/yolov8n.pt" \
    --enable-tracking \
    --show
```

#### **3. Con Tracking + Estadísticas** (mejora del antiguo `track`)
```bash
uv run src/main.py process \
    --video-path "data/videos/video_2.mp4" \
    --model-path "models/yolov8n.pt" \
    --enable-tracking \
    --enable-stats \
    --show
```

#### **4. Con Tracking + Zonas** (equivalente al antiguo `analyze`)
```bash
uv run src/main.py process \
    --video-path "data/videos/video_2.mp4" \
    --model-path "models/yolov8n.pt" \
    --enable-tracking \
    --enable-zones "configs/zonas.json" \
    --show
```

#### **5. Modo Completo** (todas las funcionalidades)
```bash
uv run src/main.py process \
    --video-path "data/videos/video_2.mp4" \
    --model-path "models/yolov8n.pt" \
    --enable-tracking \
    --enable-stats \
    --enable-zones "configs/zonas.json" \
    --show
```

## 🔧 Parámetros Disponibles

| Parámetro | Tipo | Descripción | Por Defecto |
|-----------|------|-------------|-------------|
| `--video-path` | str | Ruta del video de entrada | **Requerido** |
| `--model-path` | str | Ruta del modelo YOLO | **Requerido** |
| `--output-path` | str | Ruta del video de salida | Auto-generado |
| `--show` | bool | Mostrar visualización | `True` |
| `--classes` | str | Clases a detectar (ej: "person,car") | `"person"` |
| `--enable-tracking` | bool | Habilitar tracking | `False` |
| `--enable-stats` | bool | Habilitar estadísticas | `False` |
| `--enable-zones` | str | Archivo JSON de zonas | `None` |
| `--save-video` | bool | Guardar video procesado | `True` |

## 📊 Archivos de Salida

### **1. Video Procesado**
- **Ubicación**: `outputs/{video}_{modelo}.mp4`
- **Formato**: H.264 (compatible)
- **Contenido**: Frame con todas las visualizaciones habilitadas

### **2. Estadísticas por Frame** (si `--enable-stats`)
- **Ubicación**: `outputs/{video}_{modelo}_unified_stats.txt`
- **Formato**: TSV (Tab-Separated Values)
- **Columnas**: Frame | Objetos_Detectados | IDs_Confirmados | IDs_Unicos | En_Zonas | Cruzaron_Lineas

## 🔄 Migración desde Comandos Antiguos

### **Antes (3 comandos separados):**
```bash
# Solo detección
uv run src/main.py video --video-path "video.mp4" --model-path "model.pt"

# Solo tracking
uv run src/main.py track --video-path "video.mp4" --model-path "model.pt"

# Solo análisis con zonas
uv run src/main.py analyze --video-path "video.mp4" --model-path "model.pt" --zones-json "zonas.json"
```

### **Después (1 comando unificado):**
```bash
# Solo detección
uv run src/main.py process --video-path "video.mp4" --model-path "model.pt"

# Solo tracking
uv run src/main.py process --video-path "video.mp4" --model-path "model.pt" --enable-tracking

# Solo análisis con zonas
uv run src/main.py process --video-path "video.mp4" --model-path "model.pt" --enable-tracking --enable-zones "zonas.json"
```

## ✅ Ventajas del Sistema Unificado

1. **🎯 Una sola interfaz** - Menos confusión
2. **🔧 Funcionalidades combinables** - Activa lo que necesites
3. **📚 Código mantenible** - Una sola función principal
4. **🔄 Consistencia** - Mismo comportamiento en todas las opciones
5. **⚡ Flexibilidad** - Desde detección básica hasta análisis completo
6. **📊 Estadísticas mejoradas** - Incluye métricas de zonas y líneas

## 🚨 Comandos Antiguos (Deprecados)

Los comandos antiguos siguen funcionando pero se recomienda migrar al nuevo `process`:

- `video` → `process` (sin flags adicionales)
- `track` → `process --enable-tracking --enable-stats`
- `analyze` → `process --enable-tracking --enable-zones`

## 🧪 Prueba del Sistema Unificado

Para probar que todo funciona correctamente:

```bash
# Probar modo básico
uv run src/main.py process \
    --video-path "data/videos/video_2.mp4" \
    --model-path "models/yolov8n.pt" \
    --show

# Probar modo completo
uv run src/main.py process \
    --video-path "data/videos/video_2.mp4" \
    --model-path "models/yolov8n.pt" \
    --enable-tracking \
    --enable-stats \
    --show
```

¡El analizador unificado está listo para usar! 🎉
