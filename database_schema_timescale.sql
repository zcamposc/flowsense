-- =====================================================
-- ESQUEMA OPTIMIZADO PARA TIMESCALEDB
-- FASE 9: Base de Datos de Series de Tiempo
-- =====================================================

-- Habilitar extensión TimescaleDB
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Habilitar extensión UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- TABLA PRINCIPAL: ANÁLISIS DE VIDEO
-- =====================================================
CREATE TABLE IF NOT EXISTS video_analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    video_path TEXT NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    analysis_config JSONB,
    status VARCHAR(50) DEFAULT 'running',
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
-- TABLA PRINCIPAL: DETECCIONES DE FRAMES (HYPERTABLE)
-- =====================================================
CREATE TABLE IF NOT EXISTS frame_detections (
    time TIMESTAMPTZ NOT NULL,  -- Campo de tiempo requerido para TimescaleDB
    video_analysis_id UUID NOT NULL REFERENCES video_analyses(id) ON DELETE CASCADE,
    frame_number INTEGER NOT NULL,
    track_id INTEGER NOT NULL,
    class_name VARCHAR(50) NOT NULL,
    confidence DECIMAL(5,4) NOT NULL,
    bbox_x1 INTEGER NOT NULL,
    bbox_y1 INTEGER NOT NULL,
    bbox_x2 INTEGER NOT NULL,
    bbox_y2 INTEGER NOT NULL,
    center_x INTEGER NOT NULL,
    center_y INTEGER NOT NULL
);

-- Convertir a hypertable (particionado automático por tiempo)
SELECT create_hypertable('frame_detections', 'time', if_not_exists => TRUE);

-- Crear índices optimizados para series de tiempo
CREATE INDEX IF NOT EXISTS idx_frame_detections_time ON frame_detections (time DESC);
CREATE INDEX IF NOT EXISTS idx_frame_detections_track ON frame_detections (track_id, time DESC);
CREATE INDEX IF NOT EXISTS idx_frame_detections_class ON frame_detections (class_name, time DESC);
CREATE INDEX IF NOT EXISTS idx_frame_detections_analysis ON frame_detections (video_analysis_id, time DESC);

-- =====================================================
-- TABLA: ZONAS
-- =====================================================
CREATE TABLE IF NOT EXISTS zones (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    video_analysis_id UUID NOT NULL REFERENCES video_analyses(id) ON DELETE CASCADE,
    zone_name VARCHAR(100) NOT NULL,
    zone_type VARCHAR(50) NOT NULL, -- 'polygon' o 'line'
    coordinates JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- TABLA: EVENTOS DE ZONA (HYPERTABLE)
-- =====================================================
CREATE TABLE IF NOT EXISTS zone_events (
    time TIMESTAMPTZ NOT NULL,  -- Campo de tiempo requerido para TimescaleDB
    video_analysis_id UUID NOT NULL REFERENCES video_analyses(id) ON DELETE CASCADE,
    zone_id UUID NOT NULL REFERENCES zones(id) ON DELETE CASCADE,
    track_id INTEGER NOT NULL,
    event_type VARCHAR(20) NOT NULL, -- 'enter' o 'exit'
    class_name VARCHAR(50) NOT NULL,
    confidence DECIMAL(5,4) NOT NULL,
    position_x INTEGER NOT NULL,
    position_y INTEGER NOT NULL
);

-- Convertir a hypertable
SELECT create_hypertable('zone_events', 'time', if_not_exists => TRUE);

-- Crear índices optimizados
CREATE INDEX IF NOT EXISTS idx_zone_events_time ON zone_events (time DESC);
CREATE INDEX IF NOT EXISTS idx_zone_events_zone ON zone_events (zone_id, time DESC);
CREATE INDEX IF NOT EXISTS idx_zone_events_track ON zone_events (track_id, time DESC);

-- =====================================================
-- TABLA: CRUCES DE LÍNEA (HYPERTABLE)
-- =====================================================
CREATE TABLE IF NOT EXISTS line_crossing_events (
    time TIMESTAMPTZ NOT NULL,  -- Campo de tiempo requerido para TimescaleDB
    video_analysis_id UUID NOT NULL REFERENCES video_analyses(id) ON DELETE CASCADE,
    zone_id UUID NOT NULL REFERENCES zones(id) ON DELETE CASCADE,
    track_id INTEGER NOT NULL,
    direction VARCHAR(20) NOT NULL, -- 'left_to_right' o 'right_to_left'
    class_name VARCHAR(50) NOT NULL,
    confidence DECIMAL(5,4) NOT NULL,
    position_x INTEGER NOT NULL,
    position_y INTEGER NOT NULL
);

-- Convertir a hypertable
SELECT create_hypertable('line_crossing_events', 'time', if_not_exists => TRUE);

-- Crear índices optimizados
CREATE INDEX IF NOT EXISTS idx_line_crossing_time ON line_crossing_events (time DESC);
CREATE INDEX IF NOT EXISTS idx_line_crossing_zone ON line_crossing_events (zone_id, time DESC);
CREATE INDEX IF NOT EXISTS idx_line_crossing_track ON line_crossing_events (track_id, time DESC);

-- =====================================================
-- TABLA: ESTADÍSTICAS POR MINUTO (HYPERTABLE)
-- =====================================================
CREATE TABLE IF NOT EXISTS minute_statistics (
    time TIMESTAMPTZ NOT NULL,  -- Campo de tiempo requerido para TimescaleDB
    video_analysis_id UUID NOT NULL REFERENCES video_analyses(id) ON DELETE CASCADE,
    total_detections INTEGER DEFAULT 0,
    unique_tracks INTEGER DEFAULT 0,
    zone_events INTEGER DEFAULT 0,
    line_crossings INTEGER DEFAULT 0
);

-- Convertir a hypertable
SELECT create_hypertable('minute_statistics', 'time', if_not_exists => TRUE);

-- Crear índices optimizados
CREATE INDEX IF NOT EXISTS idx_minute_stats_time ON minute_statistics (time DESC);
CREATE INDEX IF NOT EXISTS idx_minute_stats_analysis ON minute_statistics (video_analysis_id, time DESC);

-- =====================================================
-- POLÍTICAS DE COMPRESIÓN Y RETENCIÓN
-- =====================================================

-- Comprimir datos de detecciones después de 1 día
SELECT add_compression_policy('frame_detections', INTERVAL '1 day');

-- Comprimir eventos de zona después de 1 día
SELECT add_compression_policy('zone_events', INTERVAL '1 day');

-- Comprimir cruces de línea después de 1 día
SELECT add_compression_policy('line_crossing_events', INTERVAL '1 day');

-- Comprimir estadísticas después de 1 día
SELECT add_compression_policy('minute_statistics', INTERVAL '1 day');

-- Retener datos de detecciones por 90 días
SELECT add_retention_policy('frame_detections', INTERVAL '90 days');

-- Retener eventos por 180 días
SELECT add_retention_policy('zone_events', INTERVAL '180 days');
SELECT add_retention_policy('line_crossing_events', INTERVAL '180 days');

-- Retener estadísticas por 1 año
SELECT add_retention_policy('minute_statistics', INTERVAL '1 year');

-- =====================================================
-- VISTAS OPTIMIZADAS
-- =====================================================

-- Vista de resumen de análisis
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
    COUNT(fd.*) as total_detections,
    COUNT(ze.*) as total_zone_events,
    COUNT(lce.*) as total_line_crossings
FROM video_analyses va
LEFT JOIN frame_detections fd ON va.id = fd.video_analysis_id
LEFT JOIN zone_events ze ON va.id = ze.video_analysis_id
LEFT JOIN line_crossing_events lce ON va.id = lce.video_analysis_id
GROUP BY va.id, va.video_path, va.model_name, va.status, va.total_frames, 
         va.fps, va.resolution_width, va.resolution_height, va.started_at, va.completed_at;

-- Vista de tracks únicos por análisis
CREATE OR REPLACE VIEW unique_tracks_per_analysis AS
SELECT 
    video_analysis_id,
    track_id,
    class_name,
    MIN(time) as first_seen,
    MAX(time) as last_seen,
    COUNT(*) as total_detections
FROM frame_detections
GROUP BY video_analysis_id, track_id, class_name;

-- =====================================================
-- FUNCIONES DE AGREGACIÓN
-- =====================================================

-- Función para obtener estadísticas por hora
CREATE OR REPLACE FUNCTION get_hourly_stats(
    analysis_id UUID,
    hours_back INTEGER DEFAULT 24
)
RETURNS TABLE (
    hour TIMESTAMPTZ,
    total_detections BIGINT,
    unique_tracks BIGINT,
    zone_events BIGINT,
    line_crossings BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        time_bucket('1 hour', fd.time) as hour,
        COUNT(fd.*) as total_detections,
        COUNT(DISTINCT fd.track_id) as unique_tracks,
        COUNT(ze.*) as zone_events,
        COUNT(lce.*) as line_crossings
    FROM frame_detections fd
    LEFT JOIN zone_events ze ON fd.video_analysis_id = ze.video_analysis_id 
        AND time_bucket('1 hour', fd.time) = time_bucket('1 hour', ze.time)
    LEFT JOIN line_crossing_events lce ON fd.video_analysis_id = lce.video_analysis_id 
        AND time_bucket('1 hour', fd.time) = time_bucket('1 hour', lce.time)
    WHERE fd.video_analysis_id = analysis_id
        AND fd.time > NOW() - (hours_back || ' hours')::INTERVAL
    GROUP BY hour
    ORDER BY hour;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- TRIGGERS
-- =====================================================

-- Función para actualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para video_analyses
CREATE TRIGGER update_video_analyses_updated_at
    BEFORE UPDATE ON video_analyses
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- COMENTARIOS
-- =====================================================
COMMENT ON TABLE frame_detections IS 'Detecciones de objetos por frame - Hypertable optimizada para series de tiempo';
COMMENT ON TABLE zone_events IS 'Eventos de entrada/salida de zonas - Hypertable optimizada para series de tiempo';
COMMENT ON TABLE line_crossing_events IS 'Eventos de cruce de líneas - Hypertable optimizada para series de tiempo';
COMMENT ON TABLE minute_statistics IS 'Estadísticas agregadas por minuto - Hypertable optimizada para series de tiempo';

-- =====================================================
-- FIN DEL ESQUEMA
-- =====================================================

