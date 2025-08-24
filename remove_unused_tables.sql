-- =====================================================
-- SCRIPT PARA ELIMINAR TABLAS INNECESARIAS
-- Elimina frame_detections y minute_statistics
-- =====================================================

-- IMPORTANTE: Hacer backup antes de ejecutar si hay datos importantes

-- 1. Eliminar tabla frame_detections
-- Esta tabla se llena masivamente y no aporta valor significativo
-- Los eventos importantes están en zone_events y line_crossing_events
DROP TABLE IF EXISTS frame_detections CASCADE;

-- 2. Eliminar tabla minute_statistics  
-- Esta tabla no se usa activamente en el código actual
-- Las estadísticas se pueden calcular dinámicamente desde otras tablas
DROP TABLE IF EXISTS minute_statistics CASCADE;

-- =====================================================
-- VERIFICACIÓN: Mostrar tablas restantes
-- =====================================================
SELECT table_name, table_type 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_type = 'BASE TABLE'
ORDER BY table_name;

-- =====================================================
-- RESULTADO ESPERADO: Solo estas tablas deben quedar:
-- =====================================================
-- ✅ video_analyses      - Metadata de análisis de video
-- ✅ zones              - Configuración de zonas/líneas  
-- ✅ zone_events        - Eventos de entrada/salida (DATOS VALIOSOS)
-- ✅ line_crossing_events - Cruces de líneas (DATOS VALIOSOS)

COMMENT ON SCHEMA public IS 'Esquema optimizado - Solo tablas con datos valiosos';
