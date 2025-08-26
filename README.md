# Sistema de Análisis de Video con YOLOv8

## Descripción

Sistema completo de detección y análisis de objetos en videos usando YOLOv8 con funcionalidades avanzadas como tracking de objetos, análisis de zonas de interés, detección de cruces de línea y almacenamiento en base de datos TimescaleDB optimizada para series de tiempo.

## Características Principales

### Detección y Tracking Avanzado
- Detección universal de todos los objetos COCO (80 clases)
- Filtrado opcional por clases específicas
- Tracking persistente con IDs únicos
- Umbral de confianza configurable
- Sistema de confirmación para reducir falsos positivos

### Análisis de Zonas de Interés
- Configuración de polígonos para áreas específicas
- Detección de líneas para cruces direccionales
- Eventos de entrada/salida automáticos
- Alertas en tiempo real
- Visualización interactiva de configuración

### Persistencia de Datos
- Base de datos TimescaleDB optimizada para series de tiempo
- Exportación CSV de eventos significativos
- Compresión automática y políticas de retención
- Consultas optimizadas por tiempo

### Gestión Inteligente de Archivos
- Nombres únicos automáticos con timestamp
- Organización automática de archivos relacionados
- Prevención de sobrescrituras
- Nombres personalizados opcionales

## Instalación

### Requisitos
- Python 3.8+
- uv (gestor de paquetes Python)
- Docker (opcional, para base de datos)

### Configuración del Proyecto

```bash
# Clonar el repositorio
git clone <repository-url>
cd videos_yolo

# Instalar dependencias con uv
uv sync

# Verificar instalación
uv run python --version

# Crear carpetas necesarias (opcional - se crean automáticamente)
mkdir -p models data/videos data/images
```

### Modelos YOLO

Los modelos YOLO deben guardarse en la carpeta `models/` del proyecto:

```bash
# Crear carpeta si no existe
mkdir -p models

# Descargar modelos recomendados
cd models
wget https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.pt
wget https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8m.pt
wget https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8x.pt
cd ..
```

**Modelos disponibles:**
- `yolov8n.pt` (nano - más rápido, ~6MB)
- `yolov8s.pt` (small - balance velocidad/precisión, ~22MB)  
- `yolov8m.pt` (medium - buena precisión, ~52MB)
- `yolov8l.pt` (large - alta precisión, ~87MB)
- `yolov8x.pt` (extra-large - máxima precisión, ~136MB)

**Descarga oficial**: [Ultralytics YOLO Models](https://docs.ultralytics.com/models/)

### Videos de Entrada

Coloca tus videos en la carpeta `data/videos/` para facilitar su acceso:

```bash
# Copiar videos a la carpeta del proyecto
cp /ruta/a/tu/video.mp4 data/videos/

# Listar videos disponibles
ls -la data/videos/
```

**Formatos soportados**: MP4, AVI, MOV, MKV y otros formatos compatibles con OpenCV.

## Organización de Carpetas

El proyecto utiliza una estructura de carpetas específica para organizar diferentes tipos de archivos:

### **Estructura del Proyecto**
```
videos_yolo/
├── models/                     # 📁 Modelos YOLO (.pt)
│   ├── yolov8n.pt             # Modelo nano (rápido)
│   ├── yolov8m.pt             # Modelo medium (balance)
│   └── yolov8x.pt             # Modelo extra-large (preciso)
├── data/                       # 📁 Datos de entrada
│   ├── videos/                # Videos para procesar
│   └── images/                # Imágenes para procesar
├── configs/                    # 📁 Configuraciones de zonas
│   ├── lineas_entrada_20250826_001234/
│   ├── polygonos_areas_20250826_001456/
│   └── completa_configuracion_20250826_001789/
├── outputs/                    # 📁 Resultados de análisis
│   ├── video_procesado.mp4    # Videos con análisis
│   ├── video_procesado_stats.txt  # Estadísticas
│   └── csv_analysis_20250826_001234/  # Datos CSV
└── tools/                      # 📁 Herramientas utilitarias
```

### **¿Dónde van los archivos?**

| Tipo de archivo | Carpeta | Descripción |
|------------------|---------|-------------|
| **Modelos YOLO** | `models/` | Archivos `.pt` descargados de Ultralytics |
| **Videos de entrada** | `data/videos/` | Videos originales para procesar |
| **Configuraciones de zonas** | `configs/` | Archivos JSON con zonas y líneas |
| **Videos procesados** | `outputs/` | Videos con detecciones y tracking |
| **Estadísticas** | `outputs/` | Archivos de texto con métricas |
| **Datos CSV** | `outputs/csv_analysis_*/` | Eventos exportados en formato CSV |
| **Herramientas** | `tools/` | Scripts de utilidad y esquemas de BD |

### **Creación Automática de Carpetas**

El sistema crea automáticamente las carpetas necesarias:

- **Configuraciones**: Se crean con timestamp único en `configs/`
  ```
  configs/lineas_entrada_principal_20250826_143022/
  ├── zonas.json              # Configuración
  ├── zonas_visual.png        # Imagen con zonas dibujadas
  └── frame_original.png      # Frame de referencia
  ```

- **Resultados**: Se guardan con nombres únicos en `outputs/`
  ```
  outputs/
  ├── video_2_yolov8n_stats_zones_20250826_143022.mp4
  ├── video_2_yolov8n_stats_zones_20250826_143022_stats.txt
  └── csv_analysis_20250826_143022/
      ├── zone_events.csv
      ├── line_crossing_events.csv
      └── minute_statistics.csv
  ```

## Inicio Rápido

### **Flujo Completo de Trabajo**

1. **Preparar modelos y datos**:
   ```bash
   # Descargar modelo (se guarda en models/)
   cd models && wget https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.pt && cd ..
   
   # Copiar tu video (se guarda en data/videos/)
   cp /ruta/a/tu/video.mp4 data/videos/mi_video.mp4
   ```

2. **Configurar zonas** (opcional - se guarda en `configs/`):
   ```bash
   # Crear configuración de zonas (resultado en configs/)
   uv run src/utils/configurar_zonas.py --polygons --video "data/videos/mi_video.mp4" --zone-names "entrada,salida"
   ```

3. **Procesar video** (resultado en `outputs/`):
   ```bash
   # Análisis completo (resultado en outputs/)
   uv run src/main.py \
       --video-path "data/videos/mi_video.mp4" \
       --model-path "models/yolov8n.pt" \
       --enable-zones \
       --zones-config "configs/polygonos_entrada_salida_20250826_143022/zonas.json"
   ```

4. **Ver resultados** (en `outputs/`):
   ```bash
   # Listar archivos generados
   ls -la outputs/
   
   # Ver estadísticas
   cat outputs/mi_video_yolov8n_zones_20250826_143022_stats.txt
   ```

## Uso Básico

### Comando Principal

```bash
# Análisis básico con tracking
uv run src/main.py --video-path "data/videos/video.mp4" --model-path "models/yolov8n.pt"

# Detectar solo personas
uv run src/main.py --video-path "data/videos/video.mp4" --model-path "models/yolov8n.pt" --classes "person"

# Con estadísticas por frame
uv run src/main.py --video-path "data/videos/video.mp4" --model-path "models/yolov8n.pt" --enable-stats

# Con análisis de zonas
uv run src/main.py --video-path "data/videos/video.mp4" --model-path "models/yolov8n.pt" --enable-zones --zones-config "configs/zonas.json"

# Análisis completo con base de datos
uv run src/main.py --video-path "data/videos/video.mp4" --model-path "models/yolov8n.pt" --enable-stats --enable-zones --zones-config "configs/zonas.json" --enable-database
```

### Parámetros Disponibles

```bash
# Ver parametros disponibles
uv run src/main.py --help
```

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `--video-path` | str | Sí | Ruta del archivo de video de entrada |
| `--model-path` | str | Sí | Ruta al modelo YOLO |
| `--output-path` | str | No | Ruta para guardar el video de salida |
| `--show` | bool | No | Mostrar visualización en tiempo real |
| `--classes` | str | No | Lista de objetos a detectar separados por coma (ej: person,car,dog). Ver [clases disponibles](https://github.com/ultralytics/ultralytics/blob/main/ultralytics/cfg/datasets/coco.yaml) |
| `--conf-threshold` | float | No | Umbral de confianza (0.0-1.0) |
| `--enable-stats` | bool | No | Habilitar estadísticas por frame |
| `--enable-zones` | bool | No | Habilitar análisis de zonas |
| `--zones-config` | str | No | Ruta al archivo JSON de configuración de zonas |
| `--enable-database` | bool | No | Habilitar almacenamiento en base de datos |

## Configuración de Zonas de Interés

### Herramienta de Configuración Interactiva

#### **Configuración Básica:**
```bash
# Configurar líneas de cruce
uv run src/utils/configurar_zonas.py --lines --video "data/videos/video.mp4" --frame 5

# Configurar polígonos de área
uv run src/utils/configurar_zonas.py --polygons --video "data/videos/video.mp4" --frame 10

# Configurar ambos tipos en una sesión
uv run src/utils/configurar_zonas.py --lines --polygons --video "data/videos/video.mp4" --frame 5
```

#### **Con Nombres Automáticos (usando descripción):**
```bash
# Una línea con nombre automático basado en descripción
uv run src/utils/configurar_zonas.py --lines --video "data/videos/video.mp4" --description "entrada_principal"

# Un polígono con nombre automático
uv run src/utils/configurar_zonas.py --polygons --video "data/videos/video.mp4" --description "zona_segura"
```

#### **Múltiples Zonas con Nombres Personalizados:**
```bash
# Múltiples líneas con nombres específicos
uv run src/utils/configurar_zonas.py --lines --video "data/videos/video.mp4" --line-names "entrada_principal,salida_emergencia,cruce_central"

# Múltiples polígonos con nombres específicos
uv run src/utils/configurar_zonas.py --polygons --video "data/videos/video.mp4" --zone-names "entrada_principal,zona_restriccion,area_vip"

# Configuración completa con múltiples líneas y polígonos
uv run src/utils/configurar_zonas.py --lines --polygons --video "data/videos/video.mp4" --line-names "entrada,salida" --zone-names "area_principal,zona_restriccion"
```

#### **Herramientas de Gestión:**
```bash
# Listar configuraciones existentes
uv run src/utils/listar_configuraciones.py

# Visualizar una configuración específica
uv run src/utils/visualizar_zonas.py --config "configs/mi_configuracion/zonas.json"
```

### Flujo de Trabajo para Múltiples Zonas

#### **¿Cómo funciona `--zone-names` y `--line-names`?**

1. **Especificas los nombres** separados por coma
2. **El sistema configura cada zona en orden** 
3. **Automáticamente asigna nombres** a cada zona que configures
4. **Termina cuando completes todas** las zonas especificadas

**Ejemplo práctico:**
```bash
uv run src/utils/configurar_zonas.py --polygons --video "video.mp4" --zone-names "entrada_principal,zona_restriccion"

# El sistema te guiará:
# 📊 Configurando 2 zonas con nombres personalizados
# 🔄 Configurando zona 1: entrada_principal
# [configuras el primer polígono]
# ✅ Zona 'entrada_principal' configurada
# 🔄 Configurando zona 2: zona_restriccion  
# [configuras el segundo polígono]
# ✅ Zona 'zona_restriccion' configurada
# ✅ Todas las 2 zonas configuradas
```

**Resultado JSON:**
```json
{
  "polygons": [
    {
      "id": "zone_entrada_principal",
      "name": "entrada_principal",
      "coordinates": [...]
    },
    {
      "id": "zone_zona_restriccion", 
      "name": "zona_restriccion",
      "coordinates": [...]
    }
  ]
}
```

### Instrucciones de Uso Interactivo

#### Para Líneas de Cruce:
1. **Clic izquierdo**: Marcar puntos de la línea (mínimo 2 puntos)
2. **Clic derecho**: Finalizar línea actual
3. **Tecla 'n'**: Nueva línea
4. **Tecla 's'**: Guardar configuración
5. **Tecla 'q'**: Salir sin guardar

#### Para Polígonos de Área:
1. **Clic izquierdo**: Marcar vértices del polígono (mínimo 3 puntos)
2. **Clic derecho**: Cerrar polígono actual
3. **Tecla 'n'**: Nuevo polígono
4. **Tecla 's'**: Guardar configuración
5. **Tecla 'q'**: Salir sin guardar

### Estructura de Configuración

Las configuraciones se organizan automáticamente en directorios con timestamp:

```
configs/
├── lineas_entrada_principal_20250825_143022/
│   ├── zonas.json          # Configuración de líneas
│   ├── zonas_visual.png    # Imagen con líneas dibujadas
│   └── frame_original.png  # Frame de referencia original
├── polygonos_area_restringida_20250825_143156/
│   ├── zonas.json          # Configuración de polígonos
│   ├── zonas_visual.png    # Imagen con polígonos dibujados
│   └── frame_original.png  # Frame de referencia original
└── completa_edificio_20250825_143300/
    ├── zonas.json          # Configuración mixta (líneas + polígonos)
    ├── zonas_visual.png    # Imagen con todas las zonas
    └── frame_original.png  # Frame de referencia original
```

### Formato del Archivo de Configuración

```json
{
  "polygons": [
    {
      "name": "area_entrada",
      "coordinates": [[100, 200], [300, 200], [300, 400], [100, 400]]
    }
  ],
  "lines": [
    {
      "name": "linea_entrada",
      "coordinates": [[150, 300], [250, 300]]
    }
  ]
}
```

## 🐳 Base de Datos TimescaleDB

### Por qué TimescaleDB

TimescaleDB es PostgreSQL optimizado para series de tiempo, ideal para análisis de video porque los eventos ocurren en secuencias temporales.

**Beneficios:**
- 10x más rápido para consultas temporales
- Particionado automático (hypertables)
- Compresión inteligente (90% menos espacio)
- Agregaciones continuas en tiempo real

### Configuración con Docker

#### 1. Configurar variables de entorno
```bash
cp env.example .env
# Editar .env y configurar DB_PASSWORD
```

#### 2. Iniciar TimescaleDB
```bash
docker-compose up -d
```

#### 3. Verificar instalación
```bash
# Ver logs
docker-compose logs timescaledb

# Conectar a la base de datos
docker exec -it video_analysis_db psql -U video_user -d video_analysis

# Verificar hypertables
SELECT hypertable_name FROM timescaledb_information.hypertables;
```

#### 4. Aplicar esquema
```bash
# Aplicar esquema optimizado
docker exec -i video_analysis_db psql -U video_user -d video_analysis < tools/database_schema_timescale.sql
```

### Uso con Análisis

```bash
# Análisis con base de datos
uv run src/main.py \
    --video-path "data/videos/video.mp4" \
    --model-path "models/yolov8n.pt" \
    --enable-zones \
    --zones-config "configs/mi_config/zonas.json" \
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

-- Cruces por dirección
SELECT direction, COUNT(*) as cruces
FROM line_crossing_events
WHERE time >= NOW() - INTERVAL '24 hours'
GROUP BY direction;
```

## Sistema de Persistencia CSV

El sistema genera archivos CSV optimizados con solo eventos significativos:

### Archivos Generados
- `zone_events.csv` - Entradas y salidas de zonas
- `line_crossing_events.csv` - Cruces de líneas
- `minute_statistics.csv` - Estadísticas agregadas por minuto

### Estructura de Eventos de Zona
```csv
id,analysis_id,zone_id,zone_name,track_id,event_type,frame_number,timestamp_ms,position_x,position_y,class_name,confidence
event_1_40,uuid,zone_1,area_entrada,1,enter,40,1600,300,200,person,0.85
```

### Estructura de Cruces de Línea
```csv
id,analysis_id,line_id,line_name,track_id,direction,frame_number,timestamp_ms,position_x,position_y,class_name,confidence
crossing_1_25,uuid,line_1,linea_entrada,1,left_to_right,25,1000,250,300,person,0.90
```

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

## Estructura del Proyecto

```
videos_yolo/
├── src/
│   ├── main.py              # CLI principal
│   ├── video_unified.py     # Analizador principal con tracking
│   ├── persistence/         # Sistema de persistencia CSV
│   ├── database/            # Sistema de base de datos
│   └── utils/               # Utilidades de configuración
├── tools/                   # Herramientas de utilidad
│   ├── check_fps.py         # Verificación de video
│   ├── debug_db.py          # Depuración de BD
│   ├── debug_zones.py       # Depuración de zonas
│   └── database_schema_timescale.sql  # Esquema de BD
├── models/                  # Modelos YOLO
├── configs/                 # Configuraciones de zonas
├── data/                    # Datos de entrada
├── outputs/                 # Resultados de análisis
├── examples/                # Ejemplos de salida
├── docker-compose.yml       # Configuración Docker
└── pyproject.toml          # Configuración del proyecto
```

## Gestión de Archivos de Salida

**Ubicación**: Todos los archivos de salida se guardan automáticamente en la carpeta `outputs/`

### Nombres Automáticos
Sin especificar `--output-path`, el sistema genera nombres únicos:

```bash
# Entrada
uv run src/main.py --video-path "data/videos/video_2.mp4" --model-path "models/yolov8n.pt" --enable-stats --enable-zones

# Salida generada automáticamente
outputs/video_2_yolov8n_stats_zones_20250825_143022.mp4
outputs/video_2_yolov8n_stats_zones_20250825_143022_stats.txt
outputs/csv_analysis_20250825_143022/
```

### Nombres Personalizados
Con `--output-path` especificado:

```bash
# Entrada
uv run src/main.py --video-path "data/videos/video_2.mp4" --model-path "models/yolov8n.pt" --output-path "outputs/analisis_entrada.mp4"

# Salida
outputs/analisis_entrada.mp4
outputs/analisis_entrada_stats.txt
```

## Clases COCO Disponibles

El sistema puede detectar **80 clases diferentes** del dataset COCO. Para ver la lista completa y actualizada, consulta el archivo oficial de Ultralytics:

**Referencia oficial**: [COCO Dataset Classes](https://github.com/ultralytics/ultralytics/blob/main/ultralytics/cfg/datasets/coco.yaml)

### Principales categorías:
- **Personas**: person
- **Vehículos**: bicycle, car, motorcycle, airplane, bus, train, truck, boat
- **Animales**: bird, cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe
- **Objetos cotidianos**: backpack, umbrella, handbag, tie, suitcase, bottle, cup, fork, knife, spoon, bowl
- **Alimentos**: banana, apple, sandwich, orange, broccoli, carrot, hot dog, pizza, donut, cake
- **Muebles**: chair, couch, potted plant, bed, dining table, toilet
- **Electrónicos**: tv, laptop, mouse, remote, keyboard, cell phone, microwave, oven, toaster, refrigerator
- **Deportes**: frisbee, skis, snowboard, sports ball, kite, baseball bat, baseball glove, skateboard, surfboard, tennis racket
- **Otros**: book, clock, vase, scissors, teddy bear, hair drier, toothbrush

### Filtrado por Clases
```bash
# Solo personas
--classes "person"

# Personas y vehículos
--classes "person,car,motorcycle,bicycle"

# Animales domésticos
--classes "dog,cat"
```

## Comandos de Gestión Docker

```bash
# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f timescaledb

# Parar servicios
docker-compose down

# Backup de base de datos
docker-compose exec timescaledb pg_dump -U video_user video_analysis > backup.sql

# Conectar a base de datos
docker exec -it video_analysis_db psql -U video_user -d video_analysis

# Reiniciar servicios
docker-compose restart
```

## Solución de Problemas

### Error de Conexión a Base de Datos
1. Verificar que Docker esté ejecutándose
2. Comprobar variables de entorno en `.env`
3. Verificar logs: `docker-compose logs timescaledb`

### Error de FPS Inválido
1. Verificar propiedades del video: `uv run tools/check_fps.py`
2. Usar un video con FPS válido (>0)

### Error en Configuración de Zonas
1. Verificar formato JSON: `uv run tools/debug_zones.py`
2. Asegurar coordenadas dentro del frame del video

## Contribución

1. Fork el proyecto
2. Crear una rama para tu feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit los cambios: `git commit -m 'Agregar nueva funcionalidad'`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Abrir un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## Documentación Adicional

- `tools/README.md` - Documentación de herramientas de utilidad
- `docker-setup.md` - Guía detallada de configuración Docker
- `FASES_PROYECTO.md` - Historial de desarrollo del proyecto
- `examples/` - Ejemplos de archivos CSV y configuraciones