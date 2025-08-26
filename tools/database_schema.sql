-- =====================================================
-- ESQUEMA DE BASE DE DATOS PARA ANÁLISIS DE VIDEO
-- FASE 9: Base de Datos de Series de Tiempo
-- =====================================================

-- Extensión para UUIDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- TABLA PRINCIPAL DE ANÁLISIS DE VIDEO
-- =====================================================
CREATE TABLE IF NOT EXISTS video_analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    video_path TEXT NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    analysis_config JSONB, -- Configuración del análisis
    status VARCHAR(20) DEFAULT 'running' CHECK (status IN ('running', 'completed', 'failed')),
    total_frames INTEGER DEFAULT 0,
    fps DECIMAL(5,2),
    resolution_width INTEGER,
    resolution_height INTEGER,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- TABLA DE CONFIGURACIÓN DE ZONAS
-- =====================================================
CREATE TABLE IF NOT EXISTS zones (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    video_analysis_id UUID NOT NULL REFERENCES video_analyses(id) ON DELETE CASCADE,
    zone_name VARCHAR(100) NOT NULL,
    zone_type VARCHAR(20) NOT NULL CHECK (zone_type IN ('polygon', 'line')),
    coordinates JSONB NOT NULL, -- Array de coordenadas [[x1,y1], [x2,y2], ...]
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Índices para consultas eficientes
    UNIQUE(video_analysis_id, zone_name)
);

-- =====================================================
-- TABLA DE DETECCIONES POR FRAME (ALTA FRECUENCIA)
-- =====================================================
CREATE TABLE IF NOT EXISTS frame_detections (
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

-- =====================================================
-- TABLA DE EVENTOS DE ENTRADA/SALIDA DE ZONAS
-- =====================================================
CREATE TABLE IF NOT EXISTS zone_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    video_analysis_id UUID NOT NULL REFERENCES video_analyses(id) ON DELETE CASCADE,
    zone_id UUID NOT NULL REFERENCES zones(id) ON DELETE CASCADE,
    track_id INTEGER NOT NULL,
    event_type VARCHAR(20) NOT NULL CHECK (event_type IN ('enter', 'exit')),
    frame_number INTEGER NOT NULL,
    timestamp_ms BIGINT NOT NULL,
    position_x INTEGER NOT NULL,
    position_y INTEGER NOT NULL,
    class_name VARCHAR(50) NOT NULL,
    confidence DECIMAL(5,4) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Índices para consultas eficientes
    UNIQUE(video_analysis_id, zone_id, track_id, event_type, frame_number)
);

-- =====================================================
-- TABLA DE EVENTOS DE CRUCE DE LÍNEAS
-- =====================================================
CREATE TABLE IF NOT EXISTS line_crossing_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    video_analysis_id UUID NOT NULL REFERENCES video_analyses(id) ON DELETE CASCADE,
    zone_id UUID NOT NULL REFERENCES zones(id) ON DELETE CASCADE,
    track_id INTEGER NOT NULL,
    direction VARCHAR(20) NOT NULL CHECK (direction IN ('left_to_right', 'right_to_left')),
    frame_number INTEGER NOT NULL,
    timestamp_ms BIGINT NOT NULL,
    position_x INTEGER NOT NULL,
    position_y INTEGER NOT NULL,
    class_name VARCHAR(50) NOT NULL,
    confidence DECIMAL(5,4) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Índices para consultas eficientes
    UNIQUE(video_analysis_id, zone_id, track_id, frame_number)
);

-- =====================================================
-- TABLA DE ESTADÍSTICAS POR MINUTO (AGREGACIÓN)
-- =====================================================
CREATE TABLE IF NOT EXISTS minute_statistics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    video_analysis_id UUID NOT NULL REFERENCES video_analyses(id) ON DELETE CASCADE,
    minute_timestamp TIMESTAMP WITH TIME ZONE NOT NULL, -- Timestamp redondeado al minuto
    total_detections INTEGER DEFAULT 0,
    unique_tracks INTEGER DEFAULT 0,
    zone_entries INTEGER DEFAULT 0,
    zone_exits INTEGER DEFAULT 0,
    line_crossings INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Índices para consultas eficientes
    UNIQUE(video_analysis_id, minute_timestamp)
);

-- =====================================================
-- ÍNDICES OPTIMIZADOS PARA CONSULTAS TEMPORALES
-- =====================================================

-- Índices para frame_detections
CREATE INDEX IF NOT EXISTS idx_frame_detections_video_timestamp 
ON frame_detections(video_analysis_id, timestamp_ms);

CREATE INDEX IF NOT EXISTS idx_frame_detections_track 
ON frame_detections(video_analysis_id, track_id);

CREATE INDEX IF NOT EXISTS idx_frame_detections_class 
ON frame_detections(video_analysis_id, class_name);

-- Índices para zone_events
CREATE INDEX IF NOT EXISTS idx_zone_events_video_timestamp 
ON zone_events(video_analysis_id, timestamp_ms);

CREATE INDEX IF NOT EXISTS idx_zone_events_zone_track 
ON zone_events(zone_id, track_id);

-- Índices para line_crossing_events
CREATE INDEX IF NOT EXISTS idx_line_crossing_video_timestamp 
ON line_crossing_events(video_analysis_id, timestamp_ms);

CREATE INDEX IF NOT EXISTS idx_line_crossing_zone_track 
ON line_crossing_events(zone_id, track_id);

-- Índices para minute_statistics
CREATE INDEX IF NOT EXISTS idx_minute_stats_video_timestamp 
ON minute_statistics(video_analysis_id, minute_timestamp);

-- =====================================================
-- FUNCIÓN PARA ACTUALIZAR TIMESTAMP DE ACTUALIZACIÓN
-- =====================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para actualizar updated_at
CREATE TRIGGER update_video_analyses_updated_at 
    BEFORE UPDATE ON video_analyses 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- FUNCIÓN PARA AGREGAR ESTADÍSTICAS POR MINUTO
-- =====================================================
CREATE OR REPLACE FUNCTION aggregate_minute_statistics()
RETURNS TRIGGER AS $$
DECLARE
    minute_ts TIMESTAMP WITH TIME ZONE;
BEGIN
    -- Calcular timestamp del minuto
    minute_ts := date_trunc('minute', to_timestamp(NEW.timestamp_ms / 1000.0));
    
    -- Insertar o actualizar estadísticas del minuto
    INSERT INTO minute_statistics (
        video_analysis_id, 
        minute_timestamp, 
        total_detections, 
        unique_tracks
    ) VALUES (
        NEW.video_analysis_id, 
        minute_ts, 
        1, 
        1
    )
    ON CONFLICT (video_analysis_id, minute_timestamp)
    DO UPDATE SET
        total_detections = minute_statistics.total_detections + 1,
        unique_tracks = GREATEST(
            minute_statistics.unique_tracks,
            (SELECT COUNT(DISTINCT track_id) 
             FROM frame_detections 
             WHERE video_analysis_id = NEW.video_analysis_id 
             AND timestamp_ms >= EXTRACT(EPOCH FROM minute_ts) * 1000
             AND timestamp_ms < EXTRACT(EPOCH FROM minute_ts + INTERVAL '1 minute') * 1000)
        );
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para agregar estadísticas automáticamente
CREATE TRIGGER trigger_aggregate_minute_stats
    AFTER INSERT ON frame_detections
    FOR EACH ROW EXECUTE FUNCTION aggregate_minute_statistics();

-- =====================================================
-- VISTAS ÚTILES PARA CONSULTAS COMUNES
-- =====================================================

-- Vista para resumen de análisis
CREATE OR REPLACE VIEW analysis_summary AS
SELECT 
    va.id,
    va.video_path,
    va.model_name,
    va.status,
    va.total_frames,
    va.fps,
    va.resolution_width,
    va.resolution_height,
    va.started_at,
    va.completed_at,
    COUNT(DISTINCT fd.track_id) as unique_tracks,
    COUNT(fd.id) as total_detections,
    COUNT(ze.id) as total_zone_events,
    COUNT(lce.id) as total_line_crossings
FROM video_analyses va
LEFT JOIN frame_detections fd ON va.id = fd.video_analysis_id
LEFT JOIN zone_events ze ON va.id = ze.video_analysis_id
LEFT JOIN line_crossing_events lce ON va.id = lce.video_analysis_id
GROUP BY va.id, va.video_path, va.model_name, va.status, va.total_frames, 
         va.fps, va.resolution_width, va.resolution_height, va.started_at, va.completed_at;

-- Vista para tracks únicos por análisis
CREATE OR REPLACE VIEW unique_tracks_per_analysis AS
SELECT 
    video_analysis_id,
    track_id,
    MIN(timestamp_ms) as first_seen,
    MAX(timestamp_ms) as last_seen,
    COUNT(*) as total_frames,
    MIN(class_name) as class_name
FROM frame_detections
GROUP BY video_analysis_id, track_id;

-- =====================================================
-- COMENTARIOS DE TABLAS
-- =====================================================
COMMENT ON TABLE video_analyses IS 'Análisis principales de videos';
COMMENT ON TABLE zones IS 'Configuración de zonas de interés (polígonos y líneas)';
COMMENT ON TABLE frame_detections IS 'Detecciones individuales por frame (alta frecuencia)';
COMMENT ON TABLE zone_events IS 'Eventos de entrada/salida de zonas';
COMMENT ON TABLE line_crossing_events IS 'Eventos de cruce de líneas';
COMMENT ON TABLE minute_statistics IS 'Estadísticas agregadas por minuto';

-- =====================================================
-- FIN DEL ESQUEMA
-- =====================================================
