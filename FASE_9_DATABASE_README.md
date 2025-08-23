# 🎯 FASE 9: BASE DE DATOS DE SERIES DE TIEMPO

## 📋 Resumen Ejecutivo

La **FASE 9** implementa un sistema completo de base de datos PostgreSQL para almacenar y analizar datos de series de tiempo generados por el análisis de video. Este sistema permite:

- ✅ **Almacenamiento persistente** de todas las detecciones y eventos
- ✅ **Análisis temporal** de movimientos y comportamientos
- ✅ **Consultas eficientes** con índices optimizados
- ✅ **Agregación automática** de estadísticas por minuto/hora
- ✅ **Integración completa** con el sistema existente

## 🏗️ Arquitectura del Sistema

### **Esquema de Base de Datos**

```
📊 video_analyses (Análisis principales)
├── 📈 frame_detections (Detecciones por frame)
├── 🎯 zones (Configuración de zonas)
├── 🚪 zone_events (Eventos entrada/salida)
├── ➡️ line_crossing_events (Cruces de líneas)
├── 📊 minute_statistics (Estadísticas por minuto)
└── 📊 hour_statistics (Estadísticas por hora)
```

### **Modelos de Datos**

#### **1. VideoAnalysis**
```python
{
    "id": "UUID",
    "video_path": "ruta/al/video.mp4",
    "model_name": "yolov8n.pt",
    "analysis_config": {"classes": ["person"], "conf_threshold": 0.25},
    "status": "running|completed|failed",
    "total_frames": 1500,
    "fps": 30.0,
    "resolution_width": 1920,
    "resolution_height": 1080
}
```

#### **2. Zone**
```python
{
    "id": "UUID",
    "video_analysis_id": "UUID",
    "zone_name": "entrada_principal",
    "zone_type": "polygon|line",
    "coordinates": [[x1,y1], [x2,y2], ...]
}
```

#### **3. FrameDetection**
```python
{
    "id": "UUID",
    "video_analysis_id": "UUID",
    "frame_number": 150,
    "timestamp_ms": 5000,
    "track_id": 42,
    "class_name": "person",
    "confidence": 0.95,
    "bbox_x1": 100, "bbox_y1": 200,
    "bbox_x2": 150, "bbox_y2": 300,
    "center_x": 125, "center_y": 250
}
```

#### **4. ZoneEvent**
```python
{
    "id": "UUID",
    "video_analysis_id": "UUID",
    "zone_id": "UUID",
    "track_id": 42,
    "event_type": "enter|exit",
    "frame_number": 150,
    "timestamp_ms": 5000,
    "position_x": 125,
    "position_y": 250
}
```

#### **5. LineCrossingEvent**
```python
{
    "id": "UUID",
    "video_analysis_id": "UUID",
    "zone_id": "UUID",
    "track_id": 42,
    "direction": "left_to_right|right_to_left",
    "frame_number": 150,
    "timestamp_ms": 5000,
    "position_x": 125,
    "position_y": 250
}
```

## 🚀 Instalación y Configuración

### **1. Requisitos Previos**

```bash
# Instalar PostgreSQL
brew install postgresql  # macOS
sudo apt-get install postgresql postgresql-contrib  # Ubuntu

# Iniciar PostgreSQL
brew services start postgresql  # macOS
sudo systemctl start postgresql  # Ubuntu
```

### **2. Configurar Variables de Entorno**

```bash
# Crear base de datos
createdb video_analysis

# Configurar variables de entorno
export DB_HOST=localhost
export DB_NAME=video_analysis
export DB_USER=postgres
export DB_PASSWORD=tu_password
export DB_PORT=5432
```

### **3. Instalar Dependencias**

```bash
# Instalar nuevas dependencias
uv add psycopg2-binary pydantic
```

### **4. Inicializar Base de Datos**

```bash
# Ejecutar script de configuración
python setup_database.py
```

## 📊 Funcionalidades Implementadas

### **1. Almacenamiento de Detecciones**

```python
from database.service import get_video_service

service = get_video_service()

# Iniciar análisis
analysis_id = service.start_analysis(
    video_path="data/videos/video_1.mp4",
    model_name="yolov8n.pt",
    config=AnalysisConfig(
        classes=["person"],
        enable_zones="configs/zonas.json",
        enable_stats=True
    )
)

# Procesar detecciones de un frame
detections = [
    {
        "track_id": 42,
        "class_name": "person",
        "confidence": 0.95,
        "bbox": [100, 200, 150, 300],
        "center": [125, 250]
    }
]

service.process_frame_detections(
    frame_number=150,
    timestamp_ms=5000,
    detections=detections
)
```

### **2. Análisis de Zonas**

#### **Eventos de Entrada/Salida**
```python
# Obtener eventos de zona
zone_events = service.get_zone_events(
    analysis_id=analysis_id,
    zone_name="entrada_principal"
)

for event in zone_events:
    print(f"Track {event.track_id} {event.event_type} en {event.timestamp_ms}ms")
```

#### **Cruces de Líneas**
```python
# Obtener cruces de línea
line_crossings = service.get_line_crossings(
    analysis_id=analysis_id,
    zone_name="linea_entrada"
)

for crossing in line_crossings:
    print(f"Track {crossing.track_id} cruzó {crossing.direction}")
```

### **3. Consultas Temporales**

```python
# Estadísticas por minuto
minute_stats = service.get_minute_statistics(
    analysis_id=analysis_id,
    start_time=datetime(2024, 1, 1, 10, 0),  # 10:00 AM
    end_time=datetime(2024, 1, 1, 11, 0)     # 11:00 AM
)

for stat in minute_stats:
    print(f"Minuto {stat['minute_timestamp']}: {stat['total_detections']} detecciones")
```

### **4. Resumen de Análisis**

```python
# Obtener resumen completo
summary = service.get_analysis_summary(analysis_id)

print(f"Video: {summary['video_path']}")
print(f"Tracks únicos: {summary['total_unique_tracks']}")
print(f"Total detecciones: {summary['total_detections']}")
print(f"Eventos de zona: {summary['total_zone_events']}")
print(f"Cruces de línea: {summary['total_line_crossings']}")
```

## 🔍 Consultas SQL Avanzadas

### **1. Tracks en Zona Específica**

```sql
-- Obtener tracks actualmente dentro de una zona
SELECT DISTINCT track_id, zone_name
FROM track_zone_status
WHERE current_status = 'inside' 
AND zone_name = 'entrada_principal';
```

### **2. Análisis de Flujo**

```sql
-- Análisis de flujo por hora
SELECT 
    date_trunc('hour', to_timestamp(timestamp_ms / 1000.0)) as hour,
    COUNT(*) as total_events,
    COUNT(DISTINCT track_id) as unique_tracks
FROM zone_events
WHERE event_type = 'enter'
GROUP BY hour
ORDER BY hour;
```

### **3. Patrones de Movimiento**

```sql
-- Tracks que cruzan líneas en ambas direcciones
SELECT 
    track_id,
    COUNT(CASE WHEN direction = 'left_to_right' THEN 1 END) as ltr_crossings,
    COUNT(CASE WHEN direction = 'right_to_left' THEN 1 END) as rtl_crossings
FROM line_crossing_events
GROUP BY track_id
HAVING COUNT(CASE WHEN direction = 'left_to_right' THEN 1 END) > 0
   AND COUNT(CASE WHEN direction = 'right_to_left' THEN 1 END) > 0;
```

## 📈 Optimizaciones Implementadas

### **1. Índices Optimizados**

```sql
-- Índices para consultas temporales
CREATE INDEX idx_frame_detections_timestamp ON frame_detections(video_analysis_id, timestamp_ms);
CREATE INDEX idx_zone_events_timestamp ON zone_events(video_analysis_id, timestamp_ms);
CREATE INDEX idx_line_crossing_timestamp ON line_crossing_events(video_analysis_id, timestamp_ms);
```

### **2. Agregación Automática**

```sql
-- Trigger para estadísticas por minuto
CREATE TRIGGER trigger_aggregate_minute_stats
    AFTER INSERT ON frame_detections
    FOR EACH ROW
    EXECUTE FUNCTION aggregate_minute_statistics();
```

### **3. Compresión de Datos**

- **Inserción en lote** para detecciones
- **Agregación automática** reduce volumen de datos
- **Índices optimizados** para consultas rápidas

## 🔧 Integración con Sistema Existente

### **Modificación del Procesador Principal**

```python
# En video_unified.py, agregar integración con base de datos
from database.service import get_video_service

def procesar_video_unificado(...):
    # Inicializar servicio de base de datos
    db_service = get_video_service()
    
    # Iniciar análisis en base de datos
    analysis_id = db_service.start_analysis(
        video_path=video_path,
        model_name=model_name,
        config=config
    )
    
    # Durante el procesamiento de frames
    for frame_number, detections in enumerate(frame_detections):
        # Procesar detecciones en base de datos
        db_service.process_frame_detections(
            frame_number=frame_number,
            timestamp_ms=timestamp_ms,
            detections=detections
        )
    
    # Completar análisis
    db_service.complete_analysis(total_frames, fps, width, height)
```

## 📊 Métricas de Rendimiento

### **Capacidad de Almacenamiento**

| Tipo de Datos | Tamaño Estimado | Frecuencia |
|---------------|----------------|------------|
| Frame Detection | ~200 bytes | 30 fps |
| Zone Event | ~100 bytes | Eventual |
| Line Crossing | ~100 bytes | Eventual |
| Minute Stats | ~50 bytes | 1/min |

### **Rendimiento Esperado**

- **Inserción**: 10,000+ detecciones/segundo
- **Consulta**: <100ms para análisis completos
- **Agregación**: Automática en tiempo real
- **Almacenamiento**: 1GB para 1 hora de video HD

## 🎯 Próximos Pasos

### **FASE 10: Interfaz Web y Dashboard**
- Dashboard web para visualizar datos
- Gráficos interactivos de estadísticas
- Consultas en tiempo real

### **FASE 11: Análisis Avanzado**
- Detección de patrones de movimiento
- Análisis de densidad de personas
- Predicción de flujos de tráfico

### **FASE 12: Sistema de Alertas**
- Notificaciones en tiempo real
- Alertas configurables por zona
- Integración con sistemas externos

## 🐛 Solución de Problemas

### **Error de Conexión**
```bash
# Verificar PostgreSQL
psql -h localhost -U postgres -d video_analysis

# Verificar variables de entorno
echo $DB_HOST $DB_NAME $DB_USER
```

### **Error de Esquema**
```bash
# Recrear esquema
python setup_database.py

# Verificar tablas
psql -d video_analysis -c "\dt"
```

### **Error de Permisos**
```bash
# Configurar permisos PostgreSQL
sudo -u postgres createuser --interactive
sudo -u postgres createdb video_analysis
```

## 📚 Referencias

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Psycopg2 Documentation](https://www.psycopg.org/docs/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
- [Series de Tiempo en PostgreSQL](https://www.timescale.com/)

---

**🎉 ¡FASE 9 COMPLETADA!**

El sistema de base de datos de series de tiempo está listo para almacenar y analizar todos los eventos de video de manera eficiente y escalable.
