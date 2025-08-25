# 🐳 Guía Completa de TimescaleDB con Docker

## 🚀 Configuración Rápida (5 minutos)

Esta guía te permitirá tener TimescaleDB funcionando en minutos usando Docker.

### **Requisitos Previos**
- Docker instalado en tu sistema
- Docker Compose instalado
- Los archivos `database_schema_timescale.sql` y `remove_unused_tables.sql` en la raíz del proyecto

### **Paso 1: Crear docker-compose.yml**

El archivo `docker-compose.yml` ya está creado en la raíz del proyecto con la configuración optimizada para TimescaleDB.

### **Paso 2: Configurar Variables de Entorno**

```bash
# Copiar archivo de ejemplo
cp env.example .env

# Editar .env con tu editor favorito
nano .env
```

**Configuración recomendada para `.env`:**
```bash
# Configuración para Docker TimescaleDB
DB_HOST=localhost
DB_PORT=5432
DB_NAME=video_analysis
DB_USER=video_user
DB_PASSWORD=change_this_password_123

# Configuración opcional
DB_MIN_CONNECTIONS=1
DB_MAX_CONNECTIONS=10
DB_LOG_LEVEL=INFO
```

⚠️ **IMPORTANTE:** Cambia `change_this_password_123` por una contraseña segura.

### **Paso 3: Iniciar TimescaleDB**

```bash
# Iniciar en background
docker-compose up -d

# Ver logs para verificar inicio correcto
docker-compose logs -f timescaledb

# Verificar que el contenedor esté funcionando
docker-compose ps
```

**Salida esperada:**
```
NAME                 IMAGE                              COMMAND                  SERVICE       CREATED         STATUS                   PORTS
video_analysis_db    timescale/timescaledb:latest-pg16  "docker-entrypoint.s…"   timescaledb   2 minutes ago   Up 2 minutes (healthy)   0.0.0.0:5432->5432/tcp
```

### **Paso 4: Verificar Instalación**

```bash
# Conectar a la base de datos
docker exec -it video_analysis_db psql -U video_user -d video_analysis

# Dentro de psql, ejecutar estas verificaciones:
```

**Comandos SQL de verificación:**
```sql
-- Verificar TimescaleDB
SELECT default_version, installed_version 
FROM pg_available_extensions 
WHERE name = 'timescaledb';

-- Ver hypertables creadas (deberías ver zone_events y line_crossing_events)
SELECT hypertable_name, num_chunks 
FROM timescaledb_information.hypertables;

-- Ver tablas disponibles
\dt

-- Salir de psql
\q
```

**Resultado esperado:**
- TimescaleDB versión 2.x instalada
- 2 hypertables: `zone_events` y `line_crossing_events`
- 4 tablas totales: `video_analyses`, `zones`, `zone_events`, `line_crossing_events`

## 🛠️ Comandos de Gestión Diaria

### **Gestión Básica del Contenedor**

```bash
# Iniciar servicios
docker-compose up -d

# Parar servicios (mantiene datos)
docker-compose stop

# Parar y eliminar contenedores (mantiene datos en volúmenes)
docker-compose down

# Parar y eliminar TODO (incluye datos - ¡CUIDADO!)
docker-compose down -v

# Reiniciar servicios
docker-compose restart

# Ver estado de servicios
docker-compose ps

# Ver logs en tiempo real
docker-compose logs -f timescaledb

# Ver últimas 100 líneas de logs
docker-compose logs --tail=100 timescaledb
```

### **Gestión de Datos**

```bash
# Hacer backup completo
docker-compose exec timescaledb pg_dump -U video_user video_analysis > backup_$(date +%Y%m%d_%H%M%S).sql

# Hacer backup solo de datos (sin esquema)
docker-compose exec timescaledb pg_dump -U video_user --data-only video_analysis > data_backup_$(date +%Y%m%d).sql

# Restaurar desde backup
docker-compose exec -T timescaledb psql -U video_user video_analysis < backup_20250824_123456.sql

# Conectar directamente a la base de datos
docker exec -it video_analysis_db psql -U video_user -d video_analysis

# Ejecutar archivo SQL desde fuera
docker-compose exec -T timescaledb psql -U video_user video_analysis < mi_script.sql
```

### **Monitoreo y Debugging**

```bash
# Ver recursos utilizados por el contenedor
docker stats video_analysis_db

# Ver información detallada del contenedor
docker inspect video_analysis_db

# Verificar salud del contenedor
docker-compose exec timescaledb pg_isready -U video_user -d video_analysis

# Ver procesos dentro del contenedor
docker-compose exec timescaledb ps aux

# Acceder al shell del contenedor
docker-compose exec timescaledb bash
```

## 🔧 Configuración Avanzada

### **Para Entorno de Producción**

Crear `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  timescaledb:
    image: timescale/timescaledb:latest-pg16
    container_name: video_analysis_db_prod
    environment:
      POSTGRES_DB: video_analysis
      POSTGRES_USER: video_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}  # Usar variable de entorno
      POSTGRES_HOST_AUTH_METHOD: scram-sha-256
      # Configuración de rendimiento
      POSTGRES_SHARED_BUFFERS: 256MB
      POSTGRES_EFFECTIVE_CACHE_SIZE: 1GB
      POSTGRES_MAINTENANCE_WORK_MEM: 128MB
      POSTGRES_CHECKPOINT_COMPLETION_TARGET: 0.9
      POSTGRES_WAL_BUFFERS: 16MB
      POSTGRES_DEFAULT_STATISTICS_TARGET: 100
      POSTGRES_RANDOM_PAGE_COST: 1.1
      POSTGRES_WORK_MEM: 8MB
    ports:
      - "5432:5432"
    volumes:
      - timescale_data_prod:/var/lib/postgresql/data
      - ./database_schema_timescale.sql:/docker-entrypoint-initdb.d/01-schema.sql
      - ./remove_unused_tables.sql:/docker-entrypoint-initdb.d/02-cleanup.sql
      - ./postgresql.conf:/etc/postgresql/postgresql.conf
    command: ["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf"]
    restart: always
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U video_user -d video_analysis"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    # Configurar límites de recursos
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 512M
          cpus: '0.25'
    # Red personalizada
    networks:
      - video_network

volumes:
  timescale_data_prod:
    driver: local

networks:
  video_network:
    driver: bridge
```

Usar con:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### **Con SSL/TLS (Seguridad)**

```yaml
# Agregar al servicio timescaledb:
environment:
  POSTGRES_SSL_MODE: require
volumes:
  - ./ssl/server.crt:/var/lib/postgresql/server.crt:ro
  - ./ssl/server.key:/var/lib/postgresql/server.key:ro
  - ./ssl/ca.crt:/var/lib/postgresql/ca.crt:ro
```

### **Con Red Externa**

```yaml
services:
  timescaledb:
    # ... configuración anterior ...
    networks:
      - external_network

networks:
  external_network:
    external: true
    name: my_external_network
```

## 🚨 Solución de Problemas

### **Problemas Comunes y Soluciones**

#### **1. Puerto 5432 ya está en uso**
```bash
# Ver qué proceso usa el puerto
sudo lsof -i :5432

# Cambiar puerto en docker-compose.yml
ports:
  - "5433:5432"  # Usar puerto 5433 externamente

# Actualizar .env
DB_PORT=5433
```

#### **2. Error de permisos en archivos SQL**
```bash
# Dar permisos correctos
chmod 644 database_schema_timescale.sql
chmod 644 remove_unused_tables.sql

# Verificar propietario
ls -la *.sql
```

#### **3. Contenedor no inicia correctamente**
```bash
# Ver logs detallados
docker-compose logs timescaledb

# Reiniciar limpiamente
docker-compose down
docker-compose up -d

# Si persiste, limpiar todo
docker-compose down -v
docker system prune -f
docker-compose up -d
```

#### **4. Error de conexión desde Python**
```bash
# Verificar que el contenedor esté corriendo
docker-compose ps

# Verificar conectividad
docker-compose exec timescaledb pg_isready -U video_user -d video_analysis

# Probar conexión manual
docker exec -it video_analysis_db psql -U video_user -d video_analysis
```

#### **5. Base de datos no se inicializa**
```bash
# Verificar archivos SQL existen
ls -la database_schema_timescale.sql remove_unused_tables.sql

# Ver logs de inicialización
docker-compose logs timescaledb | grep -i "init\|error\|failed"

# Reinicializar completamente
docker-compose down -v
docker-compose up -d
```

#### **6. Rendimiento lento**
```bash
# Verificar recursos del contenedor
docker stats video_analysis_db

# Aumentar memoria en docker-compose.yml
deploy:
  resources:
    limits:
      memory: 4G

# Verificar configuración de PostgreSQL
docker-compose exec timescaledb psql -U video_user -d video_analysis -c "SHOW shared_buffers;"
```

## ✅ Verificación Final

### **Script de Verificación Automática**

El archivo `verify_setup.py` está disponible en la raíz del proyecto para verificación automática.

Ejecutar verificación:
```bash
uv run verify_setup.py
```

### **Probar con el Sistema de Análisis**

```bash
# Probar análisis completo con base de datos
uv run src/main.py \
    --video-path "data/videos/video_2.mp4" \
    --model-path "models/yolov8n.pt" \
    --enable-zones "configs/zonas.json" \
    --enable-database

# Verificar datos guardados
docker exec -it video_analysis_db psql -U video_user -d video_analysis -c "
SELECT 
    COUNT(*) as total_events,
    COUNT(DISTINCT track_id) as unique_tracks,
    MIN(time) as first_event,
    MAX(time) as last_event
FROM zone_events;
"
```

## 🎯 Próximos Pasos

1. ✅ TimescaleDB funcionando con Docker
2. ✅ Conexión desde Python exitosa  
3. ✅ Análisis de video guardando en BD
4. 🔄 Configurar consultas personalizadas
5. 📊 Crear dashboards con Grafana (opcional)
6. 🔍 Configurar alertas automáticas

## 📚 Recursos Adicionales

- [Documentación oficial de TimescaleDB](https://docs.timescale.com/)
- [Docker Hub - TimescaleDB](https://hub.docker.com/r/timescale/timescaledb)
- [Guías de optimización de PostgreSQL](https://wiki.postgresql.org/wiki/Performance_Optimization)

---

🎉 **¡Felicidades! Ahora tienes una base de datos de series de tiempo de clase empresarial funcionando en minutos con Docker.**
