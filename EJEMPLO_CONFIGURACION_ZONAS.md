# 🎯 Ejemplo Práctico: Configuración de Zonas

## 📋 **Paso a Paso para Configurar Zonas**

### **1. Preparar Imagen de Referencia**

Primero, necesitas una imagen del video donde quieras definir las zonas:

```bash
# Opción 1: Extraer un frame del video
ffmpeg -i data/videos/video_2.mp4 -ss 00:00:05 -vframes 1 frame_reference.png

# Opción 2: Usar una imagen existente
cp data/images/image_1.png frame_reference.png

# Opción 3: Capturar pantalla del video en pausa
# (Usar cualquier herramienta de captura de pantalla)
```

### **2. Ejecutar Script de Configuración**

```bash
# Navegar al directorio del script
cd src/utils

# Ejecutar el script (asegúrate de que frame_reference.png esté en el directorio raíz)
python ejm_tracking.py
```

### **3. Configurar Línea de Cruce**

El script te mostrará la imagen y te pedirá:

1. **Haz clic en el primer punto** de la línea (ej: entrada de una puerta)
2. **Haz clic en el segundo punto** de la línea (ej: salida de la puerta)
3. **Presiona cualquier tecla** para continuar

**Ejemplo visual:**
```
    🚪 ENTRADA
       |
       | ← Línea de cruce (roja)
       |
    🚪 SALIDA
```

### **4. Configurar Polígono de Zona**

Después de la línea, el script te pedirá:

1. **Haz clic en múltiples puntos** para crear el polígono
2. **Los puntos se conectan automáticamente** en azul
3. **Presiona ENTER** cuando hayas terminado (mínimo 3 puntos)

**Ejemplo visual:**
```
    •──────• ← Punto 1
   /        \
  /          \ ← Polígono de zona (azul)
 •            •
  \          /
   \        /
    •──────• ← Punto final
```

### **5. Verificar Archivo Generado**

```bash
# Verificar que se generó el archivo
ls -la zonas.json

# Ver el contenido del archivo
cat zonas.json

# Verificar formato JSON válido
python -m json.tool zonas.json
```

### **6. Mover a Carpeta de Configuración**

```bash
# Mover el archivo a la carpeta configs
mv zonas.json ../../configs/

# Verificar que esté en su lugar
ls -la ../../configs/zonas.json
```

## 🎬 **Ejemplo Completo de Uso**

### **Escenario: Monitoreo de Entrada de Edificio**

Imagina que quieres monitorear:
- **Línea de cruce**: Entrada principal del edificio
- **Zona de interés**: Área de recepción

### **Configuración Visual**

```
    🏢 EDIFICIO
       |
    ┌───┴───┐ ← Zona de recepción (polígono azul)
    │       │
    │  📍   │ ← Punto de entrada
    │   |   │
    │   |   │ ← Línea de cruce (roja)
    │   |   │
    │  📍   │ ← Punto de salida
    └───────┘
```

### **Archivo de Configuración Resultante**

```json
{
  "lines": [
    [
      [150, 200],  # Punto de entrada
      [150, 400]   # Punto de salida
    ]
  ],
  "polygons": [
    [
      [100, 100],  # Esquina superior izquierda
      [300, 100],  # Esquina superior derecha
      [300, 500],  # Esquina inferior derecha
      [100, 500],  # Esquina inferior izquierda
      [100, 100]   # Cerrar polígono
    ]
  ]
}
```

## 🚀 **Uso con el Comando Process**

### **Comando Básico con Zonas**

```bash
# Navegar al directorio raíz
cd ../..

# Ejecutar análisis con zonas
uv run src/main.py process \
    --video-path "data/videos/video_2.mp4" \
    --model-path "models/yolov8n.pt" \
    --enable-zones "configs/zonas.json" \
    --show
```

### **Comando Completo con Zonas y Estadísticas**

```bash
uv run src/main.py process \
    --video-path "data/videos/video_2.mp4" \
    --model-path "models/yolov8n.pt" \
    --enable-stats \
    --enable-zones "configs/zonas.json" \
    --show
```

## 📊 **Resultados Esperados**

### **Alertas en Tiempo Real**

```
[ALERTA] person ID 15 ha entrado en zona de interés.
[ALERTA] person ID 23 ha cruzado línea de interés.
[ALERTA] person ID 7 ha entrado en zona de interés.
```

### **Estadísticas por Frame**

```
Frame	Objetos_Detectados	IDs_Confirmados	IDs_Unicos	En_Zonas	Cruzaron_Lineas
1	39	0	0	0	0
2	38	0	0	0	0
3	36	0	0	0	0
4	35	35	35	2	1
5	35	34	35	3	1
...
```

### **Visualización en Video**

- **Líneas rojas**: Zonas de cruce
- **Polígonos azules**: Zonas de interés
- **IDs únicos**: Tracking de objetos
- **Trayectorias**: Movimiento de personas

## 🔧 **Solución de Problemas**

### **Error: "can't open/read file"**

```bash
# Verificar que la imagen existe
ls -la frame_reference.png

# Verificar ruta en el script
cat src/utils/ejm_tracking.py | grep "image_path"
```

### **Error: "NoneType object has no attribute 'copy'"**

```bash
# La imagen no se pudo cargar
# Verificar formato de imagen
file frame_reference.png

# Convertir a formato compatible si es necesario
convert frame_reference.jpg frame_reference.png
```

### **Zonas No Se Muestran en el Video**

```bash
# Verificar que el archivo zonas.json existe
ls -la configs/zonas.json

# Verificar formato JSON válido
python -m json.tool configs/zonas.json

# Verificar que el comando incluye --enable-zones
uv run src/main.py process --help | grep zones
```

## 💡 **Consejos de Configuración**

### **Para Líneas de Cruce**
- **Ubicación estratégica**: Coloca en entradas/salidas importantes
- **Orientación**: Considera la dirección del flujo de personas
- **Longitud**: Ajusta según el área que quieras monitorear

### **Para Polígonos de Zona**
- **Forma simple**: Usa rectángulos o formas básicas
- **Tamaño apropiado**: No demasiado grandes ni pequeños
- **Puntos mínimos**: 3 puntos, máximo recomendado 8-10

### **Para Imágenes de Referencia**
- **Calidad**: Usa imágenes claras y bien iluminadas
- **Perspectiva**: Asegúrate de que coincida con el video
- **Resolución**: Similar a la resolución del video de entrada

## 🎉 **Resultado Final**

Después de seguir estos pasos, tendrás:

✅ **Archivo de configuración** `configs/zonas.json`  
✅ **Líneas de cruce** configuradas  
✅ **Polígonos de zona** definidos  
✅ **Sistema de alertas** funcionando  
✅ **Estadísticas detalladas** por frame  
✅ **Visualización clara** en el video  

¡Tu sistema de monitoreo de zonas está listo para usar! 🚀
