# 🎥 Sistema de Análisis de Video con YOLOv8 (se podria cualquier version de YOLO)

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

## Instalación Completa

### Requisitos del Sistema

| Herramienta | Versión | ¿Por qué? |
|-------------|---------|-----------|
| **Python** | 3.8+ | Lenguaje de programación |
| **uv** | Última | Gestor de paquetes Python (más rápido que pip) |
| **Docker** | Última | Para base de datos TimescaleDB (opcional) |
| **Git** | Última | Para clonar el repositorio |

### Instalar Gestores de Paquetes (Si no los tienes)

#### macOS - Homebrew
```bash
# Instalar Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Verificar instalación
brew --version
```

#### Windows - Chocolatey
```powershell
# Instalar Chocolatey (ejecutar como administrador)
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Verificar instalación
choco --version
```

#### Windows - winget (ya incluido en Windows 10/11)
```powershell
# Verificar que winget esté disponible
winget --version
```

---

## Instalación en macOS

### 1️⃣ Instalar Python

```bash
# Opción A: Con Homebrew (recomendado)
brew install python@3.11

# Opción B: Descargar desde python.org
# https://www.python.org/downloads/macos/
```

### 2️⃣ Instalar uv

```bash
# Instalar uv (gestor de paquetes Python)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Reiniciar terminal o ejecutar:
source ~/.zshrc
```

### 3️⃣ Instalar Docker (Opcional)

```bash
# Con Homebrew
brew install --cask docker

# O descargar Docker Desktop desde:
# https://www.docker.com/products/docker-desktop/
```

### 4️⃣ Verificar Instalación

```bash
# Verificar Python
python3 --version
# Debe mostrar: Python 3.8.x o superior

# Verificar uv
uv --version
# Debe mostrar: uv 0.x.x

# Verificar Docker (opcional)
docker --version
# Debe mostrar: Docker version 24.x.x
```

### ✅ Verificación Rápida

```bash
# Ejecutar este comando para verificar que todo funciona
uv run python -c "import sys; print(f'Python {sys.version}'); import ultralytics; print('YOLO disponible')"
```

---

## Instalación en Windows

### 1️⃣ Instalar Python

```powershell
# Opción A: Con Chocolatey
choco install python

# Opción B: Con winget
winget install Python.Python.3.11

# Opción C: Descargar desde python.org
# https://www.python.org/downloads/windows/
```

### 2️⃣ Instalar uv

```powershell
# Con PowerShell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# O con winget
winget install --id=astral-sh.uv
```

### 3️⃣ Instalar Docker (Opcional)

```powershell
# Con Chocolatey
choco install docker-desktop

# O descargar Docker Desktop desde:
# https://www.docker.com/products/docker-desktop/
```

### 4️⃣ Verificar Instalación

```powershell
# Verificar Python
python --version
# Debe mostrar: Python 3.8.x o superior

# Verificar uv
uv --version
# Debe mostrar: uv 0.x.x

# Verificar Docker (opcional)
docker --version
# Debe mostrar: Docker version 24.x.x
```

### ✅ Verificación Rápida

```powershell
# Ejecutar este comando para verificar que todo funciona
uv run python -c "import sys; print(f'Python {sys.version}'); import ultralytics; print('YOLO disponible')"
```

---

## Instalación en Linux (Ubuntu/Debian)

### 1️⃣ Instalar Python

```bash
# Actualizar paquetes
sudo apt update

# Instalar Python
sudo apt install python3.11 python3.11-venv python3-pip
```

### 2️⃣ Instalar uv

```bash
# Instalar uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Agregar al PATH
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### 3️⃣ Instalar Docker (Opcional)

```bash
# Instalar Docker
sudo apt install docker.io docker-compose

# Agregar usuario al grupo docker
sudo usermod -aG docker $USER

# Reiniciar sesión o ejecutar:
newgrp docker
```

### 4️⃣ Verificar Instalación

```bash
# Verificar Python
python3 --version
# Debe mostrar: Python 3.8.x o superior

# Verificar uv
uv --version
# Debe mostrar: uv 0.x.x

# Verificar Docker (opcional)
docker --version
# Debe mostrar: Docker version 24.x.x
```

### ✅ Verificación Rápida

```bash
# Ejecutar este comando para verificar que todo funciona
uv run python -c "import sys; print(f'Python {sys.version}'); import ultralytics; print('YOLO disponible')"
```

---

## Primeros Pasos (Guía Rápida)

### 1️⃣ Clonar y Configurar

```bash
# 1. Clonar el repositorio
git clone <repository-url>
cd flowsense

# 2. Instalar dependencias
uv sync

# 3. Verificar que funciona
uv run python --version
```

### 2️⃣ Descargar un Modelo YOLO

```bash
# Crear carpeta y descargar modelo básico (recomendado para empezar)
mkdir -p models
cd models
wget https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.pt
cd ..
```

### 3️⃣ Probar con un Video

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

## Requisitos del Sistema

| Requisito | Descripción | Opcional |
|-----------|-------------|----------|
| **Python 3.8+** | Lenguaje de programación | ❌ |
| **uv** | Gestor de paquetes Python | ❌ |
| **Docker** | Para base de datos TimescaleDB | ✅ |
| **Video de prueba** | Para probar el sistema | ❌ |

## Modelos YOLO Disponibles

### ¿Qué modelo elegir?

| Modelo | Tamaño | Velocidad | Precisión | Recomendado para |
|--------|--------|-----------|-----------|------------------|
| **yolov8n.pt** | 6MB | ⚡⚡⚡ | ⭐⭐ | **Principiantes** - Pruebas rápidas |
| **yolov8s.pt** | 22MB | ⚡⚡ | ⭐⭐⭐ | Balance velocidad/precisión |
| **yolov8m.pt** | 52MB | ⚡ | ⭐⭐⭐⭐ | Uso general |
| **yolov8l.pt** | 87MB | 🐌 | ⭐⭐⭐⭐⭐ | Alta precisión |
| **yolov8x.pt** | 136MB | 🐌🐌 | ⭐⭐⭐⭐⭐ | Máxima precisión |

### Descargar Modelos

```bash
# Crear carpeta
mkdir -p models
cd models

# Modelo recomendado para empezar (más rápido)
wget https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.pt

# Modelos adicionales (opcional)
wget https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8s.pt
wget https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8m.pt

cd ..
```

> **💡 Consejo**: Empieza con `yolov8n.pt` para pruebas rápidas. Si necesitas más precisión, usa `yolov8m.pt` o `yolov8l.pt`.

## Preparar Videos

### Formatos Soportados
- **MP4** (recomendado)
- **AVI, MOV, MKV** y otros formatos compatibles con OpenCV

### Organizar Videos

```bash
# Copiar tu video al proyecto
cp /ruta/a/tu/video.mp4 data/videos/

# Ver videos disponibles
ls -la data/videos/
```

---

## Uso Básico

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
├── mi_video_yolov8n_20250825_143022.mp4    # Video con detecciones
├── mi_video_yolov8n_20250825_143022_stats.txt  # Estadísticas
└── csv_analysis_20250825_143022/           # Datos CSV
    ├── frame_detections.csv
    ├── minute_statistics.csv
    └── track_zone_status.csv
```

---

## Organización del Proyecto

### Estructura de Carpetas

```
flowsense/
├── 📁 models/                 # Modelos YOLO (.pt)
├── 📁 data/
│   ├── videos/               # Videos de entrada
│   └── images/               # Imágenes de entrada
├── 📁 configs/               # Configuraciones de zonas
├── 📁 outputs/               # Resultados de análisis
└── 📁 tools/                 # Herramientas utilitarias
```

### ¿Dónde va cada archivo?

| Archivo | Carpeta | ¿Cuándo se crea? |
|---------|---------|------------------|
| **Modelos YOLO** | `models/` | Tú los descargas |
| **Videos originales** | `data/videos/` | Tú los copias |
| **Configuraciones** | `configs/` | Al configurar zonas |
| **Videos procesados** | `outputs/` | Al ejecutar análisis |
| **Datos CSV** | `outputs/csv_*/` | Al ejecutar análisis |
| **Estadísticas** | `outputs/` | Al ejecutar análisis |

> **💡 Nota**: El sistema crea automáticamente las carpetas que necesites. Solo asegúrate de tener `models/` y `data/videos/` para empezar.

---

## Funciones Avanzadas

### Análisis de Zonas

El sistema puede analizar áreas específicas del video:

```bash
# 1. Configurar zonas (interactivo)
uv run src/utils/configurar_zonas.py \
    --polygons \
    --video "data/videos/mi_video.mp4" \
    --zone-names "entrada,salida"

# 2. Analizar con zonas
uv run src/main.py \
    --video-path "data/videos/mi_video.mp4" \
    --model-path "models/yolov8n.pt" \
    --enable-zones \
    --zones-config "configs/polygonos_entrada_salida_20250826_143022/zonas.json"
```

### Base de Datos (Opcional)

Para análisis más avanzados con base de datos:

```bash
# 1. Iniciar base de datos
docker-compose up -d

# 2. Analizar con base de datos
uv run src/main.py \
    --video-path "data/videos/mi_video.mp4" \
    --model-path "models/yolov8n.pt" \
    --enable-database
```

### Ver Resultados

```bash
# Ver archivos generados
ls -la outputs/

# Ver estadísticas
cat outputs/mi_video_yolov8n_20250826_143022_stats.txt

# Ver datos CSV
ls -la outputs/csv_analysis_20250826_143022/
```

---

## Parámetros Disponibles

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

## Configuración de Zonas (Avanzado)

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

### Gestión de Configuraciones

```bash
# Ver configuraciones existentes
uv run src/utils/listar_configuraciones.py

# Visualizar una configuración
uv run src/utils/visualizar_zonas.py \
    --config "configs/mi_configuracion/zonas.json"
```

### Instrucciones de Uso

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

## Base de Datos TimescaleDB (Opcional)

### ¿Por qué TimescaleDB?

- **10x más rápido** para consultas temporales
- **Compresión automática** (90% menos espacio)
- **Particionado inteligente** por tiempo
- **Ideal para análisis de video** (eventos en secuencia temporal)

### Configuración Rápida

```bash
# 1. Configurar variables de entorno
cp env.example .env
# Editar .env y configurar DB_PASSWORD

# 2. Iniciar base de datos
docker-compose up -d

# 3. Verificar instalación
docker-compose logs timescaledb

# 4. Aplicar esquema
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

### Consultas de Ejemplo

```sql
-- Eventos de la última hora
SELECT * FROM zone_events WHERE time >= NOW() - INTERVAL '1 hour';

-- Actividad por intervalos de 5 minutos  
SELECT 
    time_bucket('5 minutes', time) as periodo,
    COUNT(*) as eventos,
    COUNT(DISTINCT track_id) as tracks_unicos
FROM zone_events 
GROUP BY periodo 
ORDER BY periodo;
```

---

## Datos CSV Generados

El sistema genera archivos CSV con eventos significativos:

### Archivos Generados
- `frame_detections.csv` - Detecciones por frame
- `minute_statistics.csv` - Estadísticas agregadas por minuto
- `track_zone_status.csv` - Estado de tracks en zonas
- `zone_events.csv` - Entradas y salidas de zonas
- `line_crossing_events.csv` - Cruces de líneas

### Ejemplo de Datos

```csv
# frame_detections.csv
frame_number,timestamp_ms,track_id,class_name,confidence,bbox_x,bbox_y,bbox_w,bbox_h
40,1600,1,person,0.85,100,200,50,150

# minute_statistics.csv
minute,total_detections,unique_tracks,most_common_class
0,45,12,person
1,52,15,person
```

---

## Herramientas de Utilidad

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

## Clases de Objetos Disponibles

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

## Estructura del Proyecto

```
flowsense/
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
# macOS/Linux
python3 --version
# Si no funciona, instalar con Homebrew: brew install python@3.11

# Windows
python --version
# Si no funciona, reinstalar desde python.org
```

#### uv no encontrado
```bash
# macOS/Linux
source ~/.zshrc  # o ~/.bashrc
uv --version

# Windows
# Reiniciar PowerShell o CMD
uv --version
```

#### Docker no funciona
```bash
# Verificar que Docker Desktop esté ejecutándose
docker --version

# En Linux, verificar permisos
sudo usermod -aG docker $USER
newgrp docker
```

### Problemas de Ejecución

#### Error de Conexión a Base de Datos
1. Verificar que Docker esté ejecutándose
2. Comprobar variables de entorno en `.env`
3. Verificar logs: `docker-compose logs timescaledb`

#### Error de FPS Inválido
1. Verificar propiedades del video: `uv run tools/check_fps.py`
2. Usar un video con FPS válido (>0)

#### Error en Configuración de Zonas
1. Verificar formato JSON: `uv run tools/debug_zones.py`
2. Asegurar coordenadas dentro del frame del video

#### Error de Modelo No Encontrado
1. Verificar que el modelo esté en `models/`
2. Descargar modelo: `wget https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.pt`

---

## 🤝 Contribución

1. Fork el proyecto
2. Crear una rama: `git checkout -b feature/nueva-funcionalidad`
3. Commit los cambios: `git commit -m 'Agregar nueva funcionalidad'`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Abrir un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## Documentación Adicional

- `tools/README.md` - Herramientas de utilidad
- `docker-setup.md` - Configuración Docker
- `FASES_PROYECTO.md` - Historial de desarrollo
- `examples/` - Ejemplos de archivos CSV

---

## 🎉 ¡Listo para empezar!

Ahora tienes todo lo necesario para usar el sistema. Recuerda:

1. **Instalar**: `uv sync`
2. **Descargar modelo**: `wget https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.pt`
3. **Probar**: `uv run src/main.py --video-path "data/videos/tu_video.mp4" --model-path "models/yolov8n.pt"`

¡Disfruta analizando tus videos! 🎥✨