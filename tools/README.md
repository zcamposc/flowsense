# Herramientas y Utilidades

Esta carpeta contiene archivos utilitarios y herramientas de desarrollo para el proyecto de análisis de video con YOLO.

## Archivos Incluidos

### Esquemas de Base de Datos
- `database_schema_timescale.sql` - Esquema optimizado para TimescaleDB con hypertables
- `database_schema.sql` - Esquema básico de PostgreSQL
- `backup_video_analysis.sql` - Respaldo de datos de análisis

### Herramientas de Verificación
- `check_fps.py` - Script para verificar FPS y propiedades de videos
- `debug_db.py` - Herramientas para depurar conexiones de base de datos
- `debug_zones.py` - Herramientas para depurar configuración de zonas

## Uso

### Verificar FPS de un Video
```bash
uv run tools/check_fps.py
```

### Depurar Base de Datos
```bash
uv run tools/debug_db.py
```

### Depurar Configuración de Zonas
```bash
uv run tools/debug_zones.py
```

### Aplicar Esquema de Base de Datos
```bash
# Para TimescaleDB (recomendado)
psql -h localhost -U postgres -d video_analysis -f tools/database_schema_timescale.sql

# Para PostgreSQL básico
psql -h localhost -U postgres -d video_analysis -f tools/database_schema.sql
```
