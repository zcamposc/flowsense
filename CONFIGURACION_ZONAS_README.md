# 🎯 Configuración de Zonas y Líneas de Interés

## Descripción

Este documento explica cómo configurar **zonas de interés** (polígonos) y **líneas de cruce** para el análisis de video con el comando `process --enable-zones`.

## 🚀 **Script de Configuración Interactiva Mejorado**

### **Ubicación del Script**
```
src/utils/ejm_tracking.py
```

### **✨ Nuevas Funcionalidades**

| Característica | Descripción |
|----------------|-------------|
| **Parámetros de línea de comandos** | No más rutas hardcodeadas |
| **Extracción automática de frames** | Desde videos directamente |
| **Múltiples líneas y polígonos** | Configuración flexible |
| **Archivos de salida personalizados** | Nombres descriptivos |
| **Modo solo líneas/polígonos** | Configuración selectiva |
| **Directorio de configuración** | Organización automática |
| **Validación de archivos** | Verificación de existencia |
| **Manejo de errores** | Cancelación con Ctrl+C |
| **Ayuda integrada** | `--help` con ejemplos |

### **Uso del Script Mejorado**
```bash
# Desde cualquier directorio
uv run python src/utils/ejm_tracking.py --help

# Usar imagen existente
uv run python src/utils/ejm_tracking.py --image "imagen.png"

# Extraer frame de video y configurar zonas
uv run python src/utils/ejm_tracking.py --video "video.mp4" --frame 5

# Especificar archivo de salida personalizado
uv run python src/utils/ejm_tracking.py --image "imagen.png" --output "mi_zonas.json"

# Solo líneas (sin polígonos)
uv run python src/utils/ejm_tracking.py --image "imagen.png" --lines-only

# Solo polígonos (sin líneas)
uv run python src/utils/ejm_tracking.py --image "imagen.png" --polygons-only
```

## 📋 **Proceso de Configuración**

### **1. Preparación**

#### **Opción A: Imagen Existente**
- **Imagen de referencia**: Usa una imagen existente del video
- **Formato**: PNG, JPG, o cualquier formato soportado por OpenCV
- **Comando**: `--image "imagen.png"`

#### **Opción B: Extraer Frame de Video (Recomendado)**
- **Video de referencia**: Usa directamente el video de entrada
- **Frame específico**: Selecciona el frame exacto donde quieres configurar zonas
- **Comando**: `--video "video.mp4" --frame 5`
- **Ventajas**: 
  - ✅ **Sincronización perfecta** con el video de análisis
  - ✅ **No hay que extraer frames manualmente**
  - ✅ **Misma resolución y perspectiva**

### **2. Configuración de Líneas**
```bash
# El script te pedirá seleccionar una línea
uv run ejm_tracking.py
```

**Pasos para líneas:**
1. **Haz clic en 2 puntos** para definir la línea
2. **La línea se dibuja automáticamente** en rojo
3. **Presiona cualquier tecla** para continuar

### **3. Configuración de Polígonos**
```bash
# Después de la línea, el script te pedirá seleccionar un polígono
```

**Pasos para polígonos:**
1. **Haz clic en múltiples puntos** para crear el polígono
2. **Los puntos se conectan automáticamente** en azul
3. **Presiona ENTER** cuando hayas terminado (mínimo 3 puntos)

### **4. Generación del Archivo**
```bash
# El script genera automáticamente:
zonas.json  # Archivo de configuración
```

## 📁 **Formato del Archivo de Configuración**

### **Estructura JSON**
```json
{
  "lines": [
    [
      [x1, y1],  # Punto inicial de la línea
      [x2, y2]   # Punto final de la línea
    ]
  ],
  "polygons": [
    [
      [x1, y1],  # Punto 1 del polígono
      [x2, y2],  # Punto 2 del polígono
      [x3, y3],  # Punto 3 del polígono
      [x4, y4],  # Punto 4 del polígono
      [x1, y1]   # Punto final (cerrar el polígono)
    ]
  ]
}
```

### **Ejemplo Real**
```json
{
  "lines": [
    [
      [414, 360],
      [2714, 308]
    ]
  ],
  "polygons": [
    [
      [599, 541],
      [284, 771],
      [478, 1509],
      [1534, 1669],
      [2237, 1099],
      [1807, 627],
      [1146, 299],
      [598, 538]
    ]
  ]
}
```

## 🎯 **Tipos de Zonas**

### **1. Líneas de Cruce**
- **Propósito**: Detectar cuando un objeto cruza una línea virtual
- **Uso**: Entradas/salidas, límites de áreas, flujo de tráfico
- **Configuración**: Solo 2 puntos (inicio y fin)

### **2. Polígonos de Interés**
- **Propósito**: Detectar cuando un objeto entra en un área específica
- **Uso**: Zonas restringidas, áreas de monitoreo, puntos de interés
- **Configuración**: Mínimo 3 puntos, máximo ilimitado

## 🔧 **Personalización del Script**

### **Cambiar Imagen de Referencia**
```python
# En src/utils/ejm_tracking.py, línea 58
image_path = "tu_imagen.png"  # Cambia por tu imagen
```

### **Agregar Múltiples Líneas**
```python
# Modificar el script para agregar más líneas
print("Selecciona línea 1:")
linea1 = select_line(image_path)
zonas["lines"].append(linea1)

print("Selecciona línea 2:")
linea2 = select_line(image_path)
zonas["lines"].append(linea2)
```

### **Agregar Múltiples Polígonos**
```python
# Modificar el script para agregar más polígonos
print("Selecciona polígono 1:")
poligono1 = select_polygon(image_path)
zonas["polygons"].append(poligono1)

print("Selecciona polígono 2:")
poligono2 = select_polygon(image_path)
zonas["polygons"].append(poligono2)
```

## 📊 **Uso con el Comando Process**

### **Comando Básico con Zonas**
```bash
uv run src/main.py process \
    --video-path "data/videos/video_2.mp4" \
    --model-path "models/yolov8n.pt" \
    --enable-zones "configs/zonas_ejemplo.json"
```

### **Comando Completo con Zonas**
```bash
uv run src/main.py process \
    --video-path "data/videos/video.mp4" \
    --model-path "models/yolov8n.pt" \
    --enable-stats \
    --enable-zones "configs/zonas.json"
```

## 🎨 **Visualización en el Video**

### **Líneas**
- **Color**: Rojo (0, 0, 255)
- **Grosor**: 2 píxeles
- **Función**: Detectar cruces

### **Polígonos**
- **Color**: Azul (255, 0, 0)
- **Grosor**: 2 píxeles
- **Función**: Detectar entradas

### **Objetos en Zonas**
- **Tracking**: IDs únicos y trayectorias
- **Alertas**: Mensajes en consola cuando se detectan eventos
- **Estadísticas**: Conteo de objetos en zonas y cruces de líneas

## 📈 **Estadísticas de Zonas**

### **Archivo de Salida**
```
Frame	Objetos_Detectados	IDs_Confirmados	IDs_Unicos	En_Zonas	Cruzaron_Lineas
1	39	0	0	0	0
2	38	0	0	0	0
3	36	0	0	0	0
...
```

### **Columnas Específicas**
- **En_Zonas**: Objetos que están dentro de polígonos
- **Cruzaron_Lineas**: Objetos que han cruzado líneas

## 🚨 **Alertas en Tiempo Real**

### **Entrada a Zona**
```
[ALERTA] person ID 15 ha entrado en zona de interés.
```

### **Cruce de Línea**
```
[ALERTA] person ID 23 ha cruzado línea de interés.
```

## 💡 **Consejos de Configuración**

### **Para Líneas**
- **Ubicación estratégica**: Coloca en entradas/salidas importantes
- **Orientación**: Considera la dirección del flujo de personas
- **Longitud**: Ajusta según el área que quieras monitorear

### **Para Polígonos**
- **Forma**: Usa formas simples para mejor rendimiento
- **Tamaño**: No demasiado grandes ni pequeños
- **Puntos**: Mínimo 3, máximo recomendado 8-10

### **Para Imágenes de Referencia**
- **Calidad**: Usa imágenes claras y bien iluminadas
- **Perspectiva**: Asegúrate de que coincida con el video
- **Resolución**: Similar a la resolución del video de entrada

## 🔍 **Depuración y Verificación**

### **Verificar Configuración**
```bash
# Verificar que el archivo JSON se generó correctamente
cat zonas.json

# Verificar formato JSON válido
python -m json.tool zonas.json
```

### **Probar Configuración**
```bash
# Ejecutar con zonas habilitadas
uv run src/main.py process \
    --video-path "data/videos/video.mp4" \
    --model-path "models/yolov8n.pt" \
    --enable-zones "zonas.json" \
    --show
```

### **Reconfigurar Zonas**
```bash
# Si necesitas cambiar las zonas:
# 1. Eliminar el archivo zonas.json existente
# 2. Ejecutar nuevamente el script de configuración
# 3. Seleccionar nuevas zonas
rm zonas.json
python src/utils/ejm_tracking.py
```

## 🎉 **Ejemplo Completo de Flujo**

### **1. Preparar Imagen**
```bash
# Copiar un frame del video como imagen de referencia
cp data/videos/video_2.mp4 frame_reference.png
```

### **2. Configurar Zonas**
```bash
cd src/utils
python ejm_tracking.py
# Seleccionar línea y polígono interactivamente
```

### **3. Mover Archivo de Configuración**
```bash
# Mover el archivo generado a la carpeta configs
mv zonas.json ../../configs/
```

### **4. Ejecutar Análisis**
```bash
cd ../..
uv run src/main.py process \
    --video-path "data/videos/video_2.mp4" \
    --model-path "models/yolov8n.pt" \
    --enable-stats \
    --enable-zones "configs/zonas.json" \
    --show
```

## 🚀 **Ventajas del Sistema de Zonas**

### **✅ Funcionalidades**
- **Detección automática** de eventos de interés
- **Alertas en tiempo real** para monitoreo
- **Estadísticas detalladas** por frame
- **Visualización clara** de zonas en el video

### **✅ Flexibilidad**
- **Configuración interactiva** fácil de usar
- **Múltiples tipos** de zonas (líneas y polígonos)
- **Personalización completa** de ubicaciones
- **Reconfiguración rápida** cuando sea necesario

### **✅ Integración**
- **Compatible** con el sistema unificado
- **Estadísticas integradas** en el archivo de salida
- **Tracking automático** de objetos en zonas
- **Alertas integradas** en el flujo de trabajo

¡El sistema de zonas está listo para configurar y usar! 🎯
