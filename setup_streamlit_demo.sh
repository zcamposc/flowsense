#!/bin/bash

# Script de configuración para el demo de Streamlit de FlowSense
# Este script instala las dependencias y configura el entorno

echo "🎥 Configurando demo de Streamlit para FlowSense..."

# Verificar que Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no está instalado. Por favor, instala Python3 primero."
    exit 1
fi

# Verificar que uv está instalado
if ! command -v uv &> /dev/null; then
    echo "❌ uv no está instalado. Por favor, instala uv primero."
    echo "💡 Instala uv con: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Crear directorio de modelos si no existe
echo "📁 Creando directorio de modelos..."
mkdir -p models

# Verificar si hay modelos YOLO
if [ ! -f "models/yolov8n.pt" ]; then
    echo "📥 Descargando modelo YOLOv8n..."
    wget -O models/yolov8n.pt https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.pt
    if [ $? -eq 0 ]; then
        echo "✅ Modelo YOLOv8n descargado exitosamente"
    else
        echo "❌ Error descargando modelo YOLOv8n"
        echo "💡 Puedes descargarlo manualmente desde:"
        echo "   https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.pt"
    fi
else
    echo "✅ Modelo YOLOv8n ya existe"
fi

# Crear directorio de salidas si no existe
echo "📁 Creando directorio de salidas..."
mkdir -p outputs

# Instalar dependencias de Streamlit
echo "📦 Instalando dependencias de Streamlit con uv..."
uv pip install -r requirements_streamlit.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencias instaladas exitosamente"
else
    echo "❌ Error instalando dependencias"
    exit 1
fi

# Verificar que Streamlit está instalado
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit no se instaló correctamente"
    exit 1
fi

echo ""
echo "🎉 ¡Configuración completada!"
echo ""
echo "🚀 Para ejecutar el demo:"
echo "   uv run streamlit run streamlit_demo.py"
echo "   # O en modo headless:"
echo "   uv run streamlit run streamlit_demo.py --server.headless true"
echo ""
echo "📖 Para más información, consulta README_streamlit.md"
echo ""
echo "💡 Consejos:"
echo "   - Asegúrate de tener videos de prueba en formato MP4, AVI, MOV o MKV"
echo "   - Puedes configurar zonas de análisis usando archivos JSON en configs/"
echo "   - El demo se abrirá automáticamente en tu navegador"
