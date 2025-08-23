-- =====================================================
-- ESQUEMA DE BASE DE DATOS - FASE 9: SERIES DE TIEMPO
-- Sistema de almacenamiento optimizado para eventos de video
-- =====================================================

-- Extensión para UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- TABLAS DE CONFIGURACIÓN
-- =====================================================

-- Tabla de análisis de videos
CREATE TABLE video_analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    video_path VARCHAR(500) NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    analysis_config JSONB NOT NULL, -- Configuración completa del análisis
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) DEFAULT 'running', -- running, completed, failed
    total_frames INTEGER,
    fps DECIMAL(5,2),
    resolution_width INTEGER,
    resolution_height INTEGER,
    UNIQUE(video_path, created_at)
);

-- Tabla de zonas configuradas
CREATE TABLE zones (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    video_analysis_id UUID NOT NULL REFERENCES video_analyses(id) ON DELETE CASCADE,
    zone_name VARCHAR(100) NOT NULL,
    zone_type VARCHAR(20) NOT NULL CHECK (zone_type IN ('polygon', 'line')),
    coordinates JSONB NOT NULL, -- Array de puntos para polígonos o 2 puntos para líneas
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(video_analysis_id, zone_name)
);

-- =====================================================
-- TABLAS DE EVENTOS DE SERIES DE TIEMPO
-- =====================================================

-- Tabla de detecciones por frame (alta frecuencia)
CREATE TABLE frame_detections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    video_analysis_id UUID NOT NULL REFERENCES video_analyses(id) ON DELETE CASCADE,
    frame_number INTEGER NOT NULL,
    timestamp_ms BIGINT NOT NULL, -- Timestamp en milisegundos desde inicio del video
    track_id INTEGER NOT NULL,
    class_name VARCHAR(50) NOT NULL,
    confidence DECIMAL(5,4) NOT NULL,
    bbox_x1 INTEGER NOT NULL,
    bbox_y1 INTEGER NOT NULL,
    bbox_x2 INTEGER NOT NULL,
    bbox_y2 INTEGER NOT NULL,
    center_x INTEGER NOT NULL,
    center_y INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Índices para consultas eficientes
    UNIQUE(video_analysis_id, frame_number, track_id)
);

-- Tabla de eventos de entrada/salida de zonas
CREATE TABLE zone_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    video_analysis_id UUID NOT NULL REFERENCES video_analyses(id) ON DELETE CASCADE,
    zone_id UUID NOT NULL REFERENCES zones(id) ON DELETE CASCADE,
    track_id INTEGER NOT NULL,
    event_type VARCHAR(20) NOT NULL CHECK (event_type IN ('enter', 'exit')),
    frame_number INTEGER NOT NULL,
    timestamp_ms BIGINT NOT NULL,
    position_x INTEGER NOT NULL,
    position_y INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Índices para consultas eficientes
    UNIQUE(video_analysis_id, zone_id, track_id, event_type, frame_number)
);

-- Tabla de eventos de cruce de líneas
CREATE TABLE line_crossing_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    video_analysis_id UUID NOT NULL REFERENCES video_analyses(id) ON DELETE CASCADE,
    zone_id UUID NOT NULL REFERENCES zones(id) ON DELETE CASCADE,
    track_id INTEGER NOT NULL,
    direction VARCHAR(20) NOT NULL CHECK (direction IN ('left_to_right', 'right_to_left')),
    frame_number INTEGER NOT NULL,
    timestamp_ms BIGINT NOT NULL,
    position_x INTEGER NOT NULL,
    position_y INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Índices para consultas eficientes
    UNIQUE(video_analysis_id, zone_id, track_id, frame_number)
);

-- =====================================================
-- TABLAS DE AGREGACIÓN (OPTIMIZACIÓN)
-- =====================================================

-- Estadísticas por minuto (agregación automática)
CREATE TABLE minute_statistics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    video_analysis_id UUID NOT NULL REFERENCES video_analyses(id) ON DELETE CASCADE,
    minute_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    total_detections INTEGER NOT NULL DEFAULT 0,
    unique_tracks INTEGER NOT NULL DEFAULT 0,
    zone_entries INTEGER NOT NULL DEFAULT 0,
    zone_exits INTEGER NOT NULL DEFAULT 0,
    line_crossings INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(video_analysis_id, minute_timestamp)
);

-- Estadísticas por hora (agregación automática)
CREATE TABLE hour_statistics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    video_analysis_id UUID NOT NULL REFERENCES video_analyses(id) ON DELETE CASCADE,
    hour_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    total_detections INTEGER NOT NULL DEFAULT 0,
    unique_tracks INTEGER NOT NULL DEFAULT 0,
    zone_entries INTEGER NOT NULL DEFAULT 0,
    zone_exits INTEGER NOT NULL DEFAULT 0,
    line_crossings INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(video_analysis_id, hour_timestamp)
);

-- =====================================================
-- ÍNDICES OPTIMIZADOS PARA CONSULTAS TEMPORALES
-- =====================================================

-- Índices para frame_detections
CREATE INDEX idx_frame_detections_video_frame ON frame_detections(video_analysis_id, frame_number);
CREATE INDEX idx_frame_detections_timestamp ON frame_detections(video_analysis_id, timestamp_ms);
CREATE INDEX idx_frame_detections_track ON frame_detections(video_analysis_id, track_id);
CREATE INDEX idx_frame_detections_class ON frame_detections(video_analysis_id, class_name);

-- Índices para zone_events
CREATE INDEX idx_zone_events_video_zone ON zone_events(video_analysis_id, zone_id);
CREATE INDEX idx_zone_events_timestamp ON zone_events(video_analysis_id, timestamp_ms);
CREATE INDEX idx_zone_events_track ON zone_events(video_analysis_id, track_id);
CREATE INDEX idx_zone_events_type ON zone_events(video_analysis_id, event_type);

-- Índices para line_crossing_events
CREATE INDEX idx_line_crossing_video_zone ON line_crossing_events(video_analysis_id, zone_id);
CREATE INDEX idx_line_crossing_timestamp ON line_crossing_events(video_analysis_id, timestamp_ms);
CREATE INDEX idx_line_crossing_track ON line_crossing_events(video_analysis_id, track_id);
CREATE INDEX idx_line_crossing_direction ON line_crossing_events(video_analysis_id, direction);

-- Índices para estadísticas agregadas
CREATE INDEX idx_minute_stats_video_time ON minute_statistics(video_analysis_id, minute_timestamp);
CREATE INDEX idx_hour_stats_video_time ON hour_statistics(video_analysis_id, hour_timestamp);

-- =====================================================
-- FUNCIONES DE AGREGACIÓN AUTOMÁTICA
-- =====================================================

-- Función para agregar estadísticas por minuto
CREATE OR REPLACE FUNCTION aggregate_minute_statistics()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO minute_statistics (
        video_analysis_id,
        minute_timestamp,
        total_detections,
        unique_tracks,
        zone_entries,
        zone_exits,
        line_crossings
    )
    SELECT 
        video_analysis_id,
        date_trunc('minute', to_timestamp(timestamp_ms / 1000.0)) as minute_timestamp,
        COUNT(*) as total_detections,
        COUNT(DISTINCT track_id) as unique_tracks,
        0 as zone_entries,
        0 as zone_exits,
        0 as line_crossings
    FROM frame_detections
    WHERE video_analysis_id = NEW.video_analysis_id
    AND timestamp_ms >= EXTRACT(EPOCH FROM date_trunc('minute', to_timestamp(NEW.timestamp_ms / 1000.0))) * 1000
    AND timestamp_ms < EXTRACT(EPOCH FROM date_trunc('minute', to_timestamp(NEW.timestamp_ms / 1000.0)) + interval '1 minute') * 1000
    GROUP BY video_analysis_id, minute_timestamp
    ON CONFLICT (video_analysis_id, minute_timestamp) DO UPDATE SET
        total_detections = minute_statistics.total_detections + EXCLUDED.total_detections,
        unique_tracks = GREATEST(minute_statistics.unique_tracks, EXCLUDED.unique_tracks);
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para agregación automática de estadísticas por minuto
CREATE TRIGGER trigger_aggregate_minute_stats
    AFTER INSERT ON frame_detections
    FOR EACH ROW
    EXECUTE FUNCTION aggregate_minute_statistics();

-- =====================================================
-- VISTAS ÚTILES PARA CONSULTAS
-- =====================================================

-- Vista para obtener el estado actual de cada track en cada zona
CREATE VIEW track_zone_status AS
WITH latest_events AS (
    SELECT 
        video_analysis_id,
        zone_id,
        track_id,
        event_type,
        ROW_NUMBER() OVER (PARTITION BY video_analysis_id, zone_id, track_id ORDER BY timestamp_ms DESC) as rn
    FROM zone_events
)
SELECT 
    le.video_analysis_id,
    le.zone_id,
    z.zone_name,
    le.track_id,
    CASE 
        WHEN le.event_type = 'enter' THEN 'inside'
        WHEN le.event_type = 'exit' THEN 'outside'
        ELSE 'unknown'
    END as current_status,
    ze.timestamp_ms as last_event_time
FROM latest_events le
JOIN zones z ON le.zone_id = z.id
JOIN zone_events ze ON le.video_analysis_id = ze.video_analysis_id 
    AND le.zone_id = ze.zone_id 
    AND le.track_id = ze.track_id 
    AND le.event_type = ze.event_type
WHERE le.rn = 1;

-- Vista para estadísticas resumidas por análisis
CREATE VIEW analysis_summary AS
SELECT 
    va.id as video_analysis_id,
    va.video_path,
    va.model_name,
    va.status,
    va.total_frames,
    va.fps,
    COUNT(DISTINCT fd.track_id) as total_unique_tracks,
    COUNT(fd.id) as total_detections,
    COUNT(ze.id) as total_zone_events,
    COUNT(lce.id) as total_line_crossings,
    va.created_at,
    va.completed_at
FROM video_analyses va
LEFT JOIN frame_detections fd ON va.id = fd.video_analysis_id
LEFT JOIN zone_events ze ON va.id = ze.video_analysis_id
LEFT JOIN line_crossing_events lce ON va.id = lce.video_analysis_id
GROUP BY va.id, va.video_path, va.model_name, va.status, va.total_frames, va.fps, va.created_at, va.completed_at;

-- =====================================================
-- COMENTARIOS PARA DOCUMENTACIÓN
-- =====================================================

COMMENT ON TABLE video_analyses IS 'Registro principal de cada análisis de video realizado';
COMMENT ON TABLE zones IS 'Configuración de zonas (polígonos) y líneas para cada análisis';
COMMENT ON TABLE frame_detections IS 'Detecciones individuales por frame - alta frecuencia de datos';
COMMENT ON TABLE zone_events IS 'Eventos de entrada/salida de zonas con timestamp preciso';
COMMENT ON TABLE line_crossing_events IS 'Eventos de cruce de líneas con dirección del movimiento';
COMMENT ON TABLE minute_statistics IS 'Estadísticas agregadas por minuto para consultas rápidas';
COMMENT ON TABLE hour_statistics IS 'Estadísticas agregadas por hora para análisis de tendencias';

COMMENT ON COLUMN frame_detections.timestamp_ms IS 'Timestamp en milisegundos desde el inicio del video';
COMMENT ON COLUMN zone_events.event_type IS 'Tipo de evento: enter (entrada) o exit (salida)';
COMMENT ON COLUMN line_crossing_events.direction IS 'Dirección del cruce: left_to_right o right_to_left';
