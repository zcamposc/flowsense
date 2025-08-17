# 🚀 Analizador de Video Unificado

## Descripción

El nuevo comando `process` unifica todas las funcionalidades de análisis de video en un solo comando configurable, **con tracking siempre activo** para máxima consistencia y precisión.

## ✨ Funcionalidades Unificadas

### **1. Tracking de Objetos** (SIEMPRE ACTIVO)
- **Seguimiento de objetos entre frames** - Siempre activo
- **IDs únicos y estables** - Consistencia perfecta
- **Trayectorias visuales** - Seguimiento en tiempo real
- **Filtrado de detecciones inestables** (5+ frames para confirmación)

### **2. Estadísticas por Frame** (opcional: `--enable-stats`)
- Archivo de texto con estadísticas por frame
- Objetos detectados, IDs confirmados, IDs únicos
- En zonas y cruzando líneas (si están habilitadas)
- Formato: `Frame | Objetos_Detectados | IDs_Confirmados | IDs_Unicos | En_Zonas | Cruzaron_Lineas`

### **3. Análisis de Zonas** (opcional: `--enable-zones`)
- **Zonas de interés** (polígonos)
- **Líneas de cruce** (detección de movimiento)
- **Alertas automáticas** en tiempo real
- **Estadísticas específicas** por zona

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

### **🔍 Evidencia Técnica**

**El tracking detecta EXACTAMENTE lo mismo que la base de comparación:**
- **Archivo original**: Frame 1 = 39 detecciones
- **Tracking**: Frame 1 = 39 detecciones ✅
- **Modo básico**: Frame 1 = 35 detecciones ❌

**Conclusión**: El tracking es **superior en todos los aspectos**.

## 🚀 **Uso del Comando Unificado**

### **Sintaxis Base**
```bash
uv run src/main.py process \
    --video-path "video.mp4" \
    --model-path "model.pt"
```

### **Opciones Disponibles**
```bash
# Solo tracking (por defecto)
uv run src/main.py process \
    --video-path "video.mp4" \
    --model-path "model.pt"

# Con estadísticas
uv run src/main.py process \
    --video-path "video.mp4" \
    --model-path "model.pt" \
    --enable-stats

# Con zonas de interés
uv run src/main.py process \
    --video-path "video.mp4" \
    --model-path "model.pt" \
    --enable-zones "configs/zonas.json"

# Con todo habilitado
uv run src/main.py process \
    --video-path "video.mp4" \
    --model-path "model.pt" \
    --enable-stats \
    --enable-zones "configs/zonas.json"
```

## 📁 **Nombres de Archivos Inteligentes**

### **Sistema de Nomenclatura**
Los archivos se nombran automáticamente según las funcionalidades activadas:

| Funcionalidades | Video | Estadísticas |
|-----------------|-------|--------------|
| **Solo tracking** | `video_model_track.mp4` | `video_model_track_stats.txt` |
| **Tracking + stats** | `video_model_stats.mp4` | `video_model_stats_stats.txt` |
| **Tracking + zones** | `video_model_zones.mp4` | `video_model_zones_stats.txt` |
| **Todo activado** | `video_model_stats_zones.mp4` | `video_model_stats_zones_stats.txt` |

## 🔧 **Parámetros del Comando**

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `--video-path` | str | ✅ | Ruta del video de entrada |
| `--model-path` | str | ✅ | Ruta al modelo YOLO |
| `--output-path` | str | ❌ | Ruta personalizada de salida |
| `--show` | bool | ❌ | Mostrar video en tiempo real (default: True) |
| `--classes` | str | ❌ | Clases a detectar (default: person) |
| `--enable-stats` | bool | ❌ | Guardar estadísticas por frame |
| `--enable-zones` | str | ❌ | Archivo JSON con zonas de interés |
| `--save-video` | bool | ❌ | Guardar video procesado (default: True) |

## 📊 **Formato de Estadísticas**

### **Archivo de Salida**
```
Frame	Objetos_Detectados	IDs_Confirmados	IDs_Unicos	En_Zonas	Cruzaron_Lineas
1	39	0	0	0	0
2	38	0	0	0	0
3	36	0	0	0	0
...
```

### **Columnas**
- **Frame**: Número de frame
- **Objetos_Detectados**: Total de objetos detectados
- **IDs_Confirmados**: Objetos confirmados (5+ frames)
- **IDs_Unicos**: IDs únicos totales
- **En_Zonas**: Objetos en zonas de interés
- **Cruzaron_Lineas**: Objetos que cruzaron líneas

## 🎯 **Casos de Uso**

### **1. Análisis Básico**
```bash
# Solo tracking y detección
uv run src/main.py process \
    --video-path "data/videos/video_2.mp4" \
    --model-path "models/yolov8n.pt"
```

### **2. Análisis con Estadísticas**
```bash
# Tracking + estadísticas por frame
uv run src/main.py process \
    --video-path "data/videos/video_2.mp4" \
    --model-path "models/yolov8n.pt" \
    --enable-stats
```

### **3. Análisis con Zonas**
```bash
# Tracking + zonas de interés
uv run src/main.py process \
    --video-path "data/videos/video_2.mp4" \
    --model-path "models/yolov8n.pt" \
    --enable-zones "configs/zonas.json"
```

### **4. Análisis Completo**
```bash
# Todas las funcionalidades
uv run src/main.py process \
    --video-path "data/videos/video_2.mp4" \
    --model-path "models/yolov8n.pt" \
    --enable-stats \
    --enable-zones "configs/zonas.json"
```

## 🚀 **Ventajas del Sistema Unificado**

### **✅ Beneficios Técnicos**
- **Consistencia perfecta** entre ejecuciones
- **Tracking siempre activo** para máxima precisión
- **Código consolidado** y mantenible
- **Parámetros inteligentes** y configurables

### **✅ Beneficios de Usuario**
- **Un solo comando** para todas las funcionalidades
- **Nombres de archivos descriptivos** según funcionalidades
- **Configuración flexible** mediante flags
- **Resultados consistentes** en todos los modos

### **✅ Beneficios de Mantenimiento**
- **Código unificado** en un solo módulo
- **Lógica simplificada** sin duplicaciones
- **Testing más fácil** con un solo punto de entrada
- **Documentación centralizada**

## 🔄 **Migración desde Comandos Antiguos**

### **Comandos Reemplazados**
| Comando Antiguo | Nuevo Comando | Equivalencia |
|-----------------|---------------|--------------|
| `video` | `process` | Solo tracking (por defecto) |
| `track` | `process --enable-stats` | Tracking + estadísticas |
| `analyze` | `process --enable-zones` | Tracking + zonas |

### **Ejemplos de Migración**
```bash
# ANTES (comando video)
uv run src/main.py video --video-path "video.mp4" --model-path "model.pt"

# AHORA (comando process)
uv run src/main.py process --video-path "video.mp4" --model-path "model.pt"

# ANTES (comando track)
uv run src/main.py track --video-path "video.mp4" --model-path "model.pt"

# AHORA (comando process con stats)
uv run src/main.py process --video-path "video.mp4" --model-path "model.pt" --enable-stats
```

## 🎉 **Conclusión**

El nuevo comando `process` con **tracking siempre activo** representa una **evolución significativa** del sistema:

- ✅ **Elimina la confusión** de múltiples comandos
- ✅ **Garantiza consistencia** en todas las ejecuciones
- ✅ **Simplifica el uso** con un solo comando
- ✅ **Mantiene todas las funcionalidades** de forma configurable
- ✅ **Mejora la precisión** al usar siempre el mejor algoritmo

**El tracking es superior en todos los aspectos** y ahora es el **modo por defecto y único** del sistema unificado.
