# Proyecto de Procesamiento de Videos con YOLOv8

Este proyecto utiliza modelos YOLOv8 para realizar tareas de detección de objetos, seguimiento y análisis en imágenes y videos.

## Funcionalidades

El proyecto utiliza `uv` como gestor de entorno y paquetes Python. Los comandos se ejecutan desde la raíz del proyecto y los archivos de salida se generan automáticamente en la carpeta `outputs/`.

1. **Procesar una imagen:**
   Detecta objetos en una imagen y genera una imagen procesada. Por defecto detecta personas.
   ```bash
   # Detectar solo personas (por defecto)
   uv run src/main.py --image data/images/image_1.png --model models/yolov8n.pt

   # Detectar múltiples objetos (ej: personas y carros)
   uv run src/main.py --image data/images/image_1.png --model models/yolov8n.pt --classes "person,chair,motorcycle"
   ```
   La imagen procesada se guardará en `outputs/` con un nombre generado automáticamente.

2. **Procesar un video:**
   Detecta objetos en un video y genera un video procesado. Por defecto detecta personas.
   ```bash
   # Detectar solo personas (por defecto)
   uv run src/main.py video --video-path data/videos/video_1.mp4 --model-path models/yolov8n.pt

   # Detectar múltiples objetos (ej: personas, carros y perros)
   uv run src/main.py video --video-path data/videos/video_1.mp4 --model-path models/yolov8n.pt --classes "person,car,dog"
   ```

3. **Seguimiento de personas:**
   Realiza seguimiento de objetos en un video, mostrando IDs únicos y contadores.
   ```bash
   # Detecta todo (por defecto)
   uv run src/main.py track --video-path data/videos/video_1.mp4 --model-path models/yolov8n.pt

   # Detectar múltiples objetos (ej: personas, carros y perros)
   uv run src/main.py track --video-path data/videos/video_1.mp4 --model-path models/yolov8n.pt
   ```

4. **Análisis con zonas definidas:**
   Analiza un video utilizando zonas de interés definidas en un archivo JSON.
   ```bash
   uv run src/main.py analyze --video-path data/videos/video_1.mp4 --model-path models/yolov8n.pt --zones-json configs/zonas.json
   ```

5. **Opciones adicionales:**
   - El parámetro `--output` o `--output-path` es opcional. Si no se especifica, los archivos se guardan automáticamente en `outputs/` con nombres descriptivos.
   - Los modelos se descargan automáticamente la primera vez que se necesitan.
   - El parámetro `--show/--no-show` controla la visualización en tiempo real (activada por defecto).
   - El parámetro `--classes` permite especificar qué objetos detectar (por defecto: "person").
   - Los videos procesados se pueden cerrar presionando 'q' cuando la visualización está activada.

   Ejemplos:
   ```bash
   # Sin visualización en tiempo real
   uv run src/main.py video --video-path video_1.mp4 --model-path yolov8n.pt --no-show

   # Detectar múltiples objetos específicos
   uv run src/main.py video --video-path video_1.mp4 --model-path yolov8n.pt --classes "car,truck,bus"
   ```

   Clases disponibles: 'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush'.

6. **Generación de zonas:**
   Para crear zonas de interés (líneas y polígonos):
   ```bash
   uv run src/utils/ejm_tracking.py

## Requisitos

- Python 3.8 o superior
- [uv](https://github.com/astral-sh/uv) - Gestor de paquetes Python ultrarrápido

## Instalación

1. Clona el repositorio e ingresa al directorio:
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd videos_yolo
   ```

2. Instala uv si aún no lo tienes:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. Crea un entorno virtual e instala las dependencias:
   ```bash
   uv venv
   source .venv/bin/activate  # En Windows: .venv\Scripts\activate
   uv pip install -e .
   ```

## Estructura del Proyecto

```
videos_yolo/
├── data/                    # Datos de entrada
│   ├── images/             # Imágenes para procesar
│   └── videos/             # Videos para procesar
├── outputs/                # Resultados procesados
│   ├── images/            # Imágenes con detecciones
│   └── videos/            # Videos procesados
├── models/                 # Modelos YOLOv8 (se descargan automáticamente)
├── configs/                # Configuraciones (zonas de interés, etc.)
├── src/                    # Código fuente
│   ├── utils/             # Utilidades comunes
│   ├── detect.py          # Detección en imágenes
│   ├── video_processing.py # Procesamiento de video
│   ├── tracking.py        # Seguimiento de personas
│   └── main.py           # CLI principal
├── tests/                 # Pruebas unitarias
├── pyproject.toml        # Configuración del proyecto
└── README.md            # Esta documentación

```

## Desarrollo

Para mantener el código limpio y consistente:

1. Activa el entorno virtual:
   ```bash
   source .venv/bin/activate  # En Windows: .venv\Scripts\activate
   ```

2. Ejecuta los tests:
   ```bash
   uv run pytest
   ```

3. Verifica el estilo del código:
   ```bash
   uv run ruff check .
   ```

## Licencia

Este proyecto está bajo la licencia MIT.