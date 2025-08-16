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

## Uso

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

## Mejoras Implementadas

### 🔧 **Sistema de Confirmación**
- Filtra detecciones breves (menos de 5 frames)
- Asigna IDs estables y secuenciales
- Reduce falsos positivos automáticamente

### 🎨 **Visualización Mejorada**
- Colores basados en confianza
- Trayectorias de movimiento
- Etiquetas con fondo negro
- Estadísticas en tiempo real

### ⚡ **Optimizaciones de Rendimiento**
- Tracking persistente habilitado
- Umbral de confianza configurable
- Procesamiento eficiente de frames

## Estructura del Proyecto

```
videos_yolo/
├── src/
│   ├── main.py              # CLI principal
│   ├── detect.py            # Detección en imágenes
│   ├── tracking.py          # Tracking de objetos
│   ├── video_processing.py  # Procesamiento de video
│   ├── video_analysis.py    # Análisis avanzado
│   └── utils/               # Utilidades
├── models/                  # Modelos YOLO
├── configs/                 # Configuraciones
├── data/                    # Datos de entrada
└── outputs/                 # Resultados
```

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