# Estadísticas de Tracking por Frame

## Descripción

Se ha agregado una nueva funcionalidad al módulo de tracking que permite guardar estadísticas detalladas de cada frame en un archivo de texto. Esto es útil para análisis posteriores y para entender el comportamiento del tracking a lo largo del tiempo.

## Funcionalidad

### Nuevo Parámetro: `save_stats`

La función `realizar_tracking` ahora incluye un parámetro opcional `save_stats` que controla si se guardan las estadísticas:

```python
def realizar_tracking(
    video_path: str,
    model_path: str,
    output_path: Optional[str] = None,
    show: bool = True,
    classes: Optional[list[str]] = None,
    conf_threshold: float = 0.25,
    save_stats: bool = True  # NUEVO PARÁMETRO
) -> None:
```

### Archivo de Estadísticas

Cuando `save_stats=True`, se genera un archivo de texto con el siguiente formato:

```
Frame	Objetos_Detectados	IDs_Confirmados	IDs_Unicos
1	3	0	0
2	3	0	0
3	3	0	0
4	3	0	0
5	3	3	3
6	3	3	3
7	2	2	3
8	2	2	3
...
```

### Columnas del Archivo

- **Frame**: Número de frame del video (1, 2, 3, ...)
- **Objetos_Detectados**: Total de objetos detectados en ese frame
- **IDs_Confirmados**: Objetos que han sido confirmados (aparecen en 5+ frames consecutivos)
- **IDs_Unicos**: Total de IDs únicos confirmados hasta ese frame

### Ubicación del Archivo

El archivo se guarda en el directorio `outputs/` con el nombre:
```
{nombre_video}_{nombre_modelo}_tracking_stats.txt
```

Ejemplo: `video_1_yolov8n_tracking_stats.txt`

## Uso

### Desde el CLI

```bash
# Tracking con estadísticas habilitadas (por defecto)
python -m src.main track data/videos/video_1.mp4 models/yolov8n.pt

# Tracking con estadísticas deshabilitadas
python -m src.main track data/videos/video_1.mp4 models/yolov8n.pt --no-save-stats

# Tracking con parámetros personalizados
python -m src.main track \
    data/videos/video_1.mp4 \
    models/yolov8n.pt \
    --output-path outputs/mi_video_tracking.mp4 \
    --classes person,car \
    --conf-threshold 0.3 \
    --save-stats
```

### Desde Python

```python
from src.tracking import realizar_tracking

# Ejecutar tracking con estadísticas
realizar_tracking(
    video_path="data/videos/video_1.mp4",
    model_path="models/yolov8n.pt",
    output_path="outputs/salida.mp4",
    show=True,
    classes=["person"],
    conf_threshold=0.25,
    save_stats=True  # Habilitar estadísticas
)
```

## Análisis de las Estadísticas

### Interpretación de los Datos

1. **Objetos_Detectados vs IDs_Confirmados**: 
   - Los objetos detectados son todos los que YOLO identifica en cada frame
   - Los IDs confirmados son solo aquellos que han aparecido en 5+ frames consecutivos
   - La diferencia indica objetos que aparecen brevemente y luego desaparecen

2. **IDs_Unicos**:
   - Esta columna muestra el total acumulado de objetos únicos confirmados
   - Es útil para entender cuántas personas diferentes han pasado por la escena

3. **Patrones de Comportamiento**:
   - Frames con muchos objetos detectados pero pocos confirmados indican detecciones inestables
   - Frames con números estables sugieren tracking robusto

### Ejemplo de Análisis

```python
import pandas as pd

# Cargar estadísticas
stats = pd.read_csv('outputs/video_1_yolov8n_tracking_stats.txt', sep='\t')

# Análisis básico
print(f"Total de frames: {len(stats)}")
print(f"Máximo objetos detectados: {stats['Objetos_Detectados'].max()}")
print(f"Promedio de objetos confirmados: {stats['IDs_Confirmados'].mean():.2f}")

# Frames con más detecciones
max_detections = stats.loc[stats['Objetos_Detectados'].idxmax()]
print(f"Frame con más detecciones: {max_detections['Frame']}")
```

## Ventajas

1. **Análisis Post-Procesamiento**: Permite analizar el comportamiento del tracking sin ejecutar el video completo
2. **Debugging**: Facilita identificar frames problemáticos o inestables
3. **Métricas**: Proporciona datos cuantitativos para evaluar la calidad del tracking
4. **Investigación**: Útil para estudios sobre comportamiento de objetos en videos

## Consideraciones

- El archivo se crea automáticamente en el directorio `outputs/`
- Si el directorio no existe, se crea automáticamente
- El archivo se sobrescribe en cada ejecución
- El formato es compatible con herramientas de análisis como pandas, Excel, etc.
- Las estadísticas se escriben en tiempo real durante el procesamiento

## Compatibilidad

Esta funcionalidad es completamente compatible con la funcionalidad existente:
- No afecta el rendimiento del tracking
- No modifica la salida del video
- Mantiene todos los parámetros existentes
- Es opcional y se puede deshabilitar
