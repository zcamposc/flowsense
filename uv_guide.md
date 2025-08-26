# 🚀 Guía Completa de UV para Videos YOLO

## 🎯 ¿Qué es UV?

**UV** es un gestor de dependencias y herramientas Python extremadamente rápido, escrito en Rust. Es una alternativa moderna a pip, virtualenv, pipenv, poetry, y otras herramientas.

### **⚡ Ventajas de UV**
- **10-100x más rápido** que pip
- **Gestión automática** de entornos virtuales
- **Lockfile automático** para reproducibilidad
- **Sin configuración** - funciona out-of-the-box
- **Compatibilidad total** con pyproject.toml

## 🛠️ Instalación de UV

### **macOS y Linux**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### **Windows**
```bash
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### **Con pip (alternativa)**
```bash
pip install uv
```

### **Verificar instalación**
```bash
uv --version
```

## 🚀 Uso en el Proyecto Videos YOLO

### **1. Primer Uso**
```bash
# Clonar el proyecto
git clone <repository-url>
cd videos_yolo

# UV detecta automáticamente pyproject.toml y uv.lock
# Ejecutar directamente (instala dependencias automáticamente)
uv run src/main.py --help
```

### **2. Comandos Esenciales**

#### **Ejecutar Scripts**
```bash
# Ejecutar comando principal
uv run src/main.py --video-path "data/videos/video.mp4" --model-path "models/yolov8n.pt"

# Ejecutar herramientas
uv run tools/verify_setup.py
uv run tools/check_fps.py

# Ejecutar utilidades
uv run src/utils/configurar_zonas.py --lines --video "video.mp4"
```

#### **Gestión de Dependencias**
```bash
# Instalar dependencias (manual)
uv sync

# Instalar con actualizaciones
uv sync --upgrade

# Ver dependencias instaladas
uv pip list

# Ver árbol de dependencias
uv pip show ultralytics
```

#### **Agregar/Remover Dependencias**
```bash
# Agregar dependencia de producción
uv add requests
uv add "opencv-python>=4.8.0"

# Agregar dependencia de desarrollo
uv add --dev pytest
uv add --dev black

# Remover dependencia
uv remove requests
```

### **3. Comandos Avanzados**

#### **Gestión de Python**
```bash
# Ver versiones Python disponibles
uv python list

# Instalar versión específica de Python
uv python install 3.11

# Usar versión específica
uv python pin 3.11
```

#### **Información del Entorno**
```bash
# Ver información del proyecto
uv pip show videos-yolo

# Ver ubicación del entorno virtual
uv venv --show-path

# Activar shell (opcional - no necesario normalmente)
source $(uv venv --show-path)/bin/activate
```

#### **Cache y Limpieza**
```bash
# Ver tamaño del cache
uv cache dir

# Limpiar cache
uv cache clean

# Limpiar cache específico
uv cache clean ultralytics
```

## 📋 Flujos de Trabajo Comunes

### **🔄 Desarrollo Diario**
```bash
# Ejecutar análisis de video
uv run src/main.py \
    --video-path "data/videos/video_2.mp4" \
    --model-path "models/yolov8n.pt" \
    --enable-zones "configs/zonas.json"

# Configurar nuevas zonas
uv run src/utils/configurar_zonas.py --polygons --video "video.mp4"

# Verificar setup de base de datos
uv run tools/verify_setup.py
```

### **🧪 Testing y Desarrollo**
```bash
# Ejecutar tests (cuando estén implementados)
uv run pytest

# Formatear código
uv run black src/

# Linter
uv run flake8 src/
```

### **🚀 Despliegue**
```bash
# Crear lockfile actualizado
uv sync --upgrade

# Verificar que todo funciona
uv run src/main.py --help

# Build (si es necesario)
uv build
```

## 🆚 UV vs Otras Herramientas

| Aspecto | UV | pip + venv | Poetry | Pipenv |
|---------|----|-----------|---------|---------| 
| **Velocidad** | ⚡ Extrema | 🐌 Lenta | 🚶 Media | 🚶 Media |
| **Configuración** | ✅ Automática | ❌ Manual | ⚙️ Compleja | ⚙️ Media |
| **Lockfile** | ✅ Automático | ❌ Manual | ✅ Sí | ✅ Sí |
| **Python Versions** | ✅ Automático | ❌ Manual | ❌ Manual | ❌ Manual |
| **Compatibilidad** | ✅ Total | ✅ Total | ⚠️ Parcial | ⚠️ Parcial |

## 🔧 Solución de Problemas

### **Problema: UV no encuentra Python**
```bash
# Instalar Python con UV
uv python install 3.11

# Verificar versión
uv python list
```

### **Problema: Dependencias no se instalan**
```bash
# Forzar reinstalación
uv sync --reinstall

# Limpiar cache
uv cache clean
```

### **Problema: Comando no funciona**
```bash
# Verificar que UV está en PATH
echo $PATH | grep uv

# Reinstalar UV
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### **Problema: Conflicto con pip/conda**
```bash
# UV es independiente, pero si hay conflictos:
# Desactivar entornos existentes
conda deactivate

# Usar UV limpiamente
uv run src/main.py --help
```

## 📚 Recursos Adicionales

- **[Documentación Oficial UV](https://docs.astral.sh/uv/)**
- **[GitHub UV](https://github.com/astral-sh/uv)**
- **[Comparación con otras herramientas](https://docs.astral.sh/uv/pip/compatibility/)**

## 🎯 Próximos Pasos

1. ✅ Instalar UV
2. ✅ Ejecutar `uv run src/main.py --help`
3. ✅ Probar análisis de video
4. ✅ Configurar base de datos con Docker
5. 🔄 Empezar a usar UV para todo el desarrollo

---

💡 **Tip**: Una vez que uses UV, nunca más querrás volver a pip! Es simplemente mucho más rápido y fácil de usar.