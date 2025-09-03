# 🎨 Guía de Temas y Visualización de Zonas

## 🌓 Selector de Temas

### Cómo cambiar el tema
1. **En el panel lateral** encontrarás la sección "🎨 Tema"
2. **Selecciona una opción:**
   - **Automático (sistema)**: Usa la configuración de tu navegador/sistema
   - **Claro**: Fuerza el tema claro (fondo blanco)
   - **Oscuro**: Fuerza el tema oscuro (fondo negro)

### Configuración avanzada
Si quieres personalizar más el tema, puedes editar `.streamlit/config.toml`:

```toml
# Para tema claro:
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"

# Para tema oscuro:
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#262730"
textColor = "#FAFAFA"
```

## 🖼️ Visualización de Zonas

### Vista previa en el panel lateral
Cuando habilites "Análisis de zonas" y selecciones una configuración:
- **Se mostrará automáticamente** la imagen `zonas_visual.png`
- **Información resumida** de líneas y polígonos
- **Lista de zonas** configuradas con sus nombres

### Pestaña dedicada: "🖼️ Configuración de Zonas"
Nueva pestaña que muestra:
- **Imagen grande** de la configuración de zonas
- **Detalles completos** de cada línea y polígono
- **Coordenadas exactas** de todos los puntos
- **Configuración JSON** (opcional)
- **Lista de todas** las configuraciones disponibles

### Estructura de archivos esperada
```
configs/
├── nombre_configuracion_fecha/
│   ├── zonas.json          # Configuración de zonas
│   ├── zonas_visual.png    # Imagen de vista previa
│   └── frame_original.png  # Frame original (opcional)
```

## 📋 Funcionalidades Nuevas

### 1. Vista previa automática
- Al seleccionar una configuración de zonas, se muestra automáticamente la imagen
- Información detallada de líneas y polígonos
- Nombres personalizados de las zonas

### 2. Pestaña de configuración
- Vista completa de la configuración seleccionada
- Detalles técnicos de cada zona
- Explorador de todas las configuraciones disponibles

### 3. Selector de tema dinámico
- Cambio de tema sin reiniciar la aplicación
- Tres opciones: Automático, Claro, Oscuro
- Aplicación inmediata mediante CSS

## 🔧 Uso Recomendado

### Para análisis básico:
1. Selecciona tema "Automático"
2. Habilita "Análisis de zonas"
3. Selecciona configuración deseada
4. Verifica la vista previa en el lateral

### Para análisis detallado:
1. Ve a la pestaña "🖼️ Configuración de Zonas"
2. Revisa la imagen completa y detalles
3. Verifica coordenadas y nombres
4. Confirma la configuración antes del análisis

### Para mejor rendimiento:
1. Usa tema "Automático" o "Oscuro"
2. Deshabilita "Mostrar procesamiento en tiempo real"
3. Mantén habilitado "Guardar video procesado"

## 💡 Consejos

- **Tema oscuro** suele ser mejor para análisis largos (menos fatiga visual)
- **Vista previa** te ayuda a confirmar que estás usando la configuración correcta
- **Pestaña de configuración** es útil para documentar tus análisis
- **Nombres personalizados** hacen más fácil interpretar los resultados

## ⏱️ Control de Tiempo y Interrupción

### Configuración de Timeout
- **Tiempo límite configurable**: De 5 a 120 minutos (por defecto 30 minutos)
- **Slider en el panel lateral**: Ajusta según el tamaño de tu video
- **Recomendaciones**:
  - Videos cortos (< 5 min): 10-15 minutos
  - Videos medianos (5-30 min): 30-60 minutos
  - Videos largos (> 30 min): 60-120 minutos

### Botón de Detener
- **Botón "🛑 Detener"**: Aparece durante el análisis
- **Resultados parciales**: Se muestran automáticamente si se detiene
- **Datos guardados**: CSV y video parcial disponibles
- **Pestañas activas**: Estadísticas y gráficos funcionan con datos parciales

### Manejo de Interrupciones
- **Timeout automático**: Muestra resultados parciales cuando se agota el tiempo
- **Interrupción manual**: Botón para detener cuando quieras
- **Recuperación de datos**: Carga automática de archivos parciales
- **Estado persistente**: Los datos quedan disponibles en las pestañas

## 🔧 Correcciones Técnicas

### Advertencias Corregidas
- ✅ **use_column_width deprecado**: Actualizado a `use_container_width`
- ✅ **Timeout fijo**: Ahora es configurable (5-120 minutos)
- ✅ **Sin control de parada**: Botón de detener implementado

### Mejoras de Rendimiento
- **Límite de carga**: Aumentado a 10GB (configurable)
- **Timeout inteligente**: Basado en el tamaño del video
- **Resultados parciales**: Aprovecha el trabajo ya realizado
- **Estado de sesión**: Mantiene datos entre interacciones

¡Ahora puedes trabajar con temas personalizados, vista previa de zonas, y control completo sobre el tiempo de análisis!
