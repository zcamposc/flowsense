# 🎥 Sistema de Análisis de Video con YOLOv8

> **Sistema completo de detección y análisis de objetos en videos** usando YOLOv8 con tracking, análisis de zonas y almacenamiento en base de datos.

## ¿Qué hace este sistema?

Este sistema te permite:
- **Detectar objetos** en videos (personas, vehículos, animales, etc.)
- **Seguir objetos** a lo largo del tiempo con IDs únicos
- **Analizar zonas específicas** (áreas de entrada, salida, restricción)
- **Detectar cruces de líneas** (entrada/salida direccional)
- **Guardar resultados** en CSV y base de datos
- **Generar videos** con las detecciones marcadas

## ✨ Características Principales

| Característica | Descripción |
|----------------|-------------|
| **Detección Universal** | Detecta 80 tipos de objetos (personas, vehículos, animales, etc.) |
| **Tracking Inteligente** | Sigue objetos con IDs únicos a lo largo del video |
| **Análisis de Zonas** | Configura áreas específicas y detecta entradas/salidas |
| **Estadísticas** | Genera reportes detallados de actividad |
| **Persistencia** | Guarda datos en CSV y base de datos TimescaleDB |
| **Visualización** | Genera videos con detecciones marcadas |

---

## 🚀 Instalación Rápida

### Requisitos del Sistema

| Herramienta | Versión | ¿Por qué? | Obligatorio |
|-------------|---------|-----------|-------------|
| **Python** | 3.8+ | Lenguaje de programación | ✅ |
| **uv** | Última | Gestor de paquetes Python (más rápido que pip) | ✅ |
| **Git** | Última | Para clonar el repositorio | ✅ |
| **Docker** | Última | Para base de datos TimescaleDB | ❌ Opcional |

### Paso 1: Instalar Python y uv

#### macOS
```bash
# Instalar Homebrew si no lo tienes
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Instalar Python y uv
brew install python@3.11
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.zshrc
```

#### Windows
```powershell
# Opción 1: Con winget (recomendado - ya incluido en Windows 10/11)
winget install Python.Python.3.11
winget install --id=astral-sh.uv

# Opción 2: Con Chocolatey
# Instalar Chocolatey primero (como administrador):
# Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
choco install python uv

# Reiniciar PowerShell después de la instalación
```

#### Linux (Ubuntu/Debian)
```bash
# Actualizar e instalar Python
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip curl

# Instalar uv
curl -LsSf https://astral.sh/uv/install.sh | sh
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Paso 2: Verificar Instalación

```bash
# Verificar que todo esté instalado correctamente
python3 --version  # Debe mostrar Python 3.8+
uv --version       # Debe mostrar uv 0.x.x
```

### Paso 3: Clonar y Configurar Proyecto

```bash
# 1. Clonar el repositorio
git clone <repository-url>
cd videos_yolo

# 2. Instalar dependencias automáticamente
uv sync

# 3. Verificar que YOLO funciona
uv run python -c "import ultralytics; print('✅ YOLO disponible')"
```

### Paso 4: Descargar Modelo YOLO

```bash
# Crear carpeta para modelos
mkdir -p models
cd models

# Descargar modelo básico (recomendado para empezar)
# macOS/Linux:
curl -L -o yolov8n.pt https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.pt

# Windows (PowerShell):
Invoke-WebRequest -Uri "https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.pt" -OutFile "yolov8n.pt"

# Volver al directorio raíz
cd ..
```

### Paso 5: Probar con un Video

```bash
# Copiar tu video a la carpeta del proyecto
cp /ruta/a/tu/video.mp4 data/videos/

# Ejecutar análisis básico
uv run src/main.py \
    --video-path "data/videos/tu_video.mp4" \
    --model-path "models/yolov8n.pt"
```

**¡Listo!** 🎉 El sistema procesará tu video y guardará los resultados en `outputs/`

---

## 📋 Modelos YOLO Disponibles

### ¿Qué modelo elegir?

| Modelo | Tamaño | Velocidad | Precisión | Recomendado para |
|--------|--------|-----------|-----------|------------------|
| **yolov8n.pt** | 6MB | ⚡⚡⚡ | ⭐⭐ | **Principiantes** - Pruebas rápidas |
| **yolov8s.pt** | 22MB | ⚡⚡ | ⭐⭐⭐ | Balance velocidad/precisión |
| **yolov8m.pt** | 52MB | ⚡ | ⭐⭐⭐⭐ | Uso general |
| **yolov8l.pt** | 87MB | 🐌 | ⭐⭐⭐⭐⭐ | Alta precisión |
| **yolov8x.pt** | 136MB | 🐌🐌 | ⭐⭐⭐⭐⭐ | Máxima precisión |

### Descargar Modelos Adicionales

```bash
cd models

# macOS/Linux
curl -L -o yolov8s.pt https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8s.pt
curl -L -o yolov8m.pt https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8m.pt

# Windows (PowerShell)
Invoke-WebRequest -Uri "https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8s.pt" -OutFile "yolov8s.pt"
Invoke-WebRequest -Uri "https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8m.pt" -OutFile "yolov8m.pt"

cd ..
```

> **💡 Consejo**: Empieza con `yolov8n.pt` para pruebas rápidas. Si necesitas más precisión, usa `yolov8m.pt` o `yolov8l.pt`.

---

## 🎯 Uso Básico

### Comando Más Simple

```bash
# Análisis básico - solo detección y tracking
uv run src/main.py \
    --video-path "data/videos/mi_video.mp4" \
    --model-path "models/yolov8n.pt"
```

### Comandos Útiles

```bash
# Detectar solo personas
uv run src/main.py \
    --video-path "data/videos/mi_video.mp4" \
    --model-path "models/yolov8n.pt" \
    --classes "person"

# Con estadísticas detalladas
uv run src/main.py \
    --video-path "data/videos/mi_video.mp4" \
    --model-path "models/yolov8n.pt" \
    --enable-stats

# Ver todos los parámetros disponibles
uv run src/main.py --help
```

### ¿Dónde están los resultados?

Todos los archivos se guardan automáticamente en `outputs/`:

```
outputs/
├── mi_video_yolov8n_20250901_143022.mp4         # Video con detecciones
├── mi_video_yolov8n_20250901_143022_stats.txt   # Estadísticas
└── csv_analysis_20250901_143022/                # Datos CSV
    ├── frame_detections.csv
    ├── minute_statistics.csv
    └── track_zone_status.csv
```

---

## 🎛️ Parámetros Disponibles

### Parámetros Principales

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `--video-path` | str | ✅ | Ruta del video de entrada |
| `--model-path` | str | ✅ | Ruta al modelo YOLO |
| `--classes` | str | ❌ | Objetos a detectar (ej: person,car,dog) |
| `--conf-threshold` | float | ❌ | Umbral de confianza (0.0-1.0) |
| `--enable-stats` | bool | ❌ | Habilitar estadísticas detalladas |
| `--enable-zones` | bool | ❌ | Habilitar análisis de zonas |
| `--zones-config` | str | ❌ | Archivo JSON de configuración de zonas |
| `--enable-database` | bool | ❌ | Habilitar base de datos |

### Ver Todos los Parámetros

```bash
uv run src/main.py --help
```

---

## 🎯 Análisis de Zonas (Avanzado)

### ¿Qué son las zonas?

- **Polígonos**: Áreas específicas (entrada, salida, zona restringida)
- **Líneas**: Para detectar cruces direccionales (entrada/salida)

### Configurar Zonas

```bash
# Configurar polígonos (áreas)
uv run src/utils/configurar_zonas.py \
    --polygons \
    --video "data/videos/mi_video.mp4" \
    --zone-names "entrada,salida"

# Configurar líneas (cruces)
uv run src/utils/configurar_zonas.py \
    --lines \
    --video "data/videos/mi_video.mp4" \
    --line-names "entrada_principal"
```

### Usar Zonas en Análisis

```bash
# Analizar con zonas configuradas
uv run src/main.py \
    --video-path "data/videos/mi_video.mp4" \
    --model-path "models/yolov8n.pt" \
    --enable-zones \
    --zones-config "configs/polygonos_entrada_salida_20250901_143022/zonas.json"
```

### Gestión de Configuraciones

```bash
# Ver configuraciones existentes
uv run src/utils/listar_configuraciones.py

# Visualizar una configuración
uv run src/utils/visualizar_zonas.py \
    --config "configs/mi_configuracion/zonas.json"
```

### Instrucciones de Uso Interactivo

#### Para Polígonos:
1. **Clic izquierdo**: Marcar vértices del polígono
2. **Clic derecho**: Cerrar polígono
3. **Tecla 'n'**: Nuevo polígono
4. **Tecla 's'**: Guardar

#### Para Líneas:
1. **Clic izquierdo**: Marcar puntos de la línea
2. **Clic derecho**: Finalizar línea
3. **Tecla 'n'**: Nueva línea
4. **Tecla 's'**: Guardar

---

## 🗄️ Base de Datos TimescaleDB (Opcional)

### ¿Por qué TimescaleDB?

- **10x más rápido** para consultas temporales
- **Compresión automática** (90% menos espacio)
- **Particionado inteligente** por tiempo
- **Ideal para análisis de video** (eventos en secuencia temporal)

### Configuración con Docker

```bash
# 1. Instalar Docker (si no lo tienes)
# macOS: brew install --cask docker
# Windows: winget install Docker.DockerDesktop
# Linux: sudo apt install docker.io docker-compose

# 2. Configurar variables de entorno
cp env.example .env
# Editar .env y configurar DB_PASSWORD

# 3. Iniciar base de datos
docker-compose up -d

# 4. Verificar instalación
docker-compose logs timescaledb

# 5. Aplicar esquema
docker exec -i video_analysis_db psql -U video_user -d video_analysis < tools/database_schema_timescale.sql
```

### Uso con Análisis

```bash
# Análisis con base de datos
uv run src/main.py \
    --video-path "data/videos/mi_video.mp4" \
    --model-path "models/yolov8n.pt" \
    --enable-database
```

---

## 📊 Clases de Objetos Disponibles

El sistema puede detectar **80 clases diferentes** del dataset COCO:

### Principales categorías:
- **Personas**: person
- **Vehículos**: bicycle, car, motorcycle, airplane, bus, train, truck, boat
- **Animales**: bird, cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe
- **Objetos cotidianos**: backpack, umbrella, handbag, tie, suitcase, bottle, cup, fork, knife, spoon, bowl
- **Alimentos**: banana, apple, sandwich, orange, broccoli, carrot, hot dog, pizza, donut, cake
- **Muebles**: chair, couch, potted plant, bed, dining table, toilet
- **Electrónicos**: tv, laptop, mouse, remote, keyboard, cell phone, microwave, oven, toaster, refrigerator
- **Deportes**: frisbee, skis, snowboard, sports ball, kite, baseball bat, baseball glove, skateboard, surfboard, tennis racket

### Filtrado por Clases
```bash
# Solo personas
--classes "person"

# Personas y vehículos
--classes "person,car,motorcycle,bicycle"

# Animales domésticos
--classes "dog,cat"
```

> **Referencia completa**: [COCO Dataset Classes](https://github.com/ultralytics/ultralytics/blob/main/ultralytics/cfg/datasets/coco.yaml)

---

## 🗂️ Estructura del Proyecto

```
videos_yolo/
├── 📁 src/                  # Código fuente
│   ├── main.py              # CLI principal
│   ├── video_unified.py     # Analizador principal
│   ├── persistence/         # Sistema CSV
│   ├── database/            # Sistema de BD
│   └── utils/               # Utilidades
├── 📁 tools/                # Herramientas
├── 📁 models/               # Modelos YOLO
├── 📁 configs/              # Configuraciones
├── 📁 data/                 # Datos de entrada
├── 📁 outputs/              # Resultados
├── 📁 examples/             # Ejemplos
├── docker-compose.yml       # Docker
└── pyproject.toml          # Configuración
```

---

## ❓ Solución de Problemas

### Problemas de Instalación

#### Python no encontrado
```bash
# Verificar instalación
python3 --version  # macOS/Linux
python --version   # Windows

# Si no funciona, reinstalar:
# macOS: brew install python@3.11
# Windows: winget install Python.Python.3.11
# Linux: sudo apt install python3.11
```

#### uv no encontrado
```bash
# Reiniciar terminal y verificar
uv --version

# Si no funciona, reinstalar:
curl -LsSf https://astral.sh/uv/install.sh | sh  # macOS/Linux
winget install --id=astral-sh.uv                # Windows
```

#### Error de descarga de modelos
```bash
# Si curl/Invoke-WebRequest fallan, descargar manualmente:
# 1. Ir a: https://github.com/ultralytics/assets/releases/tag/v8.2.0
# 2. Descargar yolov8n.pt
# 3. Mover a carpeta models/
```

### Problemas de Ejecución

#### Error de Modelo No Encontrado
1. Verificar que el modelo esté en `models/`
2. Usar ruta absoluta: `--model-path "/ruta/completa/models/yolov8n.pt"`

#### Error de FPS Inválido
1. Verificar propiedades del video: `uv run tools/check_fps.py`
2. Usar un video con FPS válido (>0)

#### Error en Configuración de Zonas
1. Verificar formato JSON: `uv run tools/debug_zones.py`
2. Asegurar coordenadas dentro del frame del video

#### Error de Conexión a Base de Datos
1. Verificar que Docker esté ejecutándose
2. Comprobar variables de entorno en `.env`
3. Verificar logs: `docker-compose logs timescaledb`

---

## 🛠️ Herramientas de Utilidad

### Verificación de Video
```bash
# Verificar FPS y propiedades del video
uv run tools/check_fps.py
```

### Depuración
```bash
# Depurar conexión a base de datos
uv run tools/debug_db.py

# Depurar configuración de zonas
uv run tools/debug_zones.py
```

### Gestión Docker
```bash
# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f timescaledb

# Parar servicios
docker-compose down

# Conectar a base de datos
docker exec -it video_analysis_db psql -U video_user -d video_analysis
```

---

## 🤝 Contribución

1. Fork el proyecto
2. Crear una rama: `git checkout -b feature/nueva-funcionalidad`
3. Commit los cambios: `git commit -m 'Agregar nueva funcionalidad'`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Abrir un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📚 Documentación Adicional

- `tools/README.md` - Herramientas de utilidad
- `docker-setup.md` - Configuración Docker
- `uv_guide.md` - Guía completa de uv
- `FASES_PROYECTO.md` - Historial de desarrollo
- `examples/` - Ejemplos de archivos CSV

---

## 🎉 ¡Listo para empezar!

### Resumen de comandos esenciales:

```bash
# 1. Instalar dependencias
uv sync

# 2. Descargar modelo básico
mkdir -p models && cd models
curl -L -o yolov8n.pt https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.pt
cd ..

# 3. Probar con tu video
uv run src/main.py \
    --video-path "data/videos/tu_video.mp4" \
    --model-path "models/yolov8n.pt"
```

¡Disfruta analizando tus videos! 🎥✨