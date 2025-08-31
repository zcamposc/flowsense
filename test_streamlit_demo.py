#!/usr/bin/env python3
"""
Script de prueba para el demo de Streamlit de FlowSense.

Este script verifica que todas las dependencias estén instaladas y que
el entorno esté configurado correctamente antes de ejecutar el demo.
"""

import sys
import os
import subprocess
from pathlib import Path
from typing import List, Tuple

def check_python_version() -> bool:
    """Verifica que la versión de Python sea compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 o superior es requerido")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detectado")
    return True

def check_dependencies() -> Tuple[bool, List[str]]:
    """Verifica que las dependencias estén instaladas."""
    required_packages = [
        'streamlit',
        'pandas', 
        'numpy',
        'cv2',
        'plotly'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'cv2':
                import cv2
            else:
                __import__(package)
            print(f"✅ {package} instalado")
        except ImportError:
            print(f"❌ {package} no instalado")
            missing_packages.append(package)
    
    return len(missing_packages) == 0, missing_packages

def check_project_structure() -> bool:
    """Verifica que la estructura del proyecto sea correcta."""
    required_paths = [
        'src/main.py',
        'models/',
        'outputs/',
        'streamlit_demo.py'
    ]
    
    missing_paths = []
    
    for path in required_paths:
        if not os.path.exists(path):
            missing_paths.append(path)
            print(f"❌ {path} no encontrado")
        else:
            print(f"✅ {path} encontrado")
    
    return len(missing_paths) == 0

def check_models() -> bool:
    """Verifica que haya al menos un modelo YOLO disponible."""
    models_dir = Path("models")
    if not models_dir.exists():
        print("❌ Directorio 'models/' no encontrado")
        return False
    
    model_files = list(models_dir.glob("*.pt"))
    if not model_files:
        print("❌ No se encontraron modelos YOLO (.pt) en 'models/'")
        return False
    
    print(f"✅ {len(model_files)} modelo(s) YOLO encontrado(s):")
    for model in model_files:
        print(f"   • {model.name}")
    
    return True

def install_missing_packages(packages: List[str]) -> bool:
    """Instala los paquetes faltantes usando uv."""
    if not packages:
        return True
    
    print(f"\n📦 Instalando paquetes faltantes: {', '.join(packages)}")
    
    try:
        # Intentar con uv primero
        result = subprocess.run(
            ['uv', 'pip', 'install'] + packages,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Paquetes instalados exitosamente con uv")
            return True
        else:
            print("❌ Error con uv, intentando con pip...")
            
    except FileNotFoundError:
        print("⚠️  uv no encontrado, usando pip...")
    
    # Fallback a pip
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install'] + packages,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Paquetes instalados exitosamente con pip")
            return True
        else:
            print(f"❌ Error instalando paquetes: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error ejecutando pip: {e}")
        return False

def main():
    """Función principal de verificación."""
    print("🔍 Verificando entorno para el demo de Streamlit...")
    print("=" * 50)
    
    # Verificar versión de Python
    if not check_python_version():
        sys.exit(1)
    
    print("\n📦 Verificando dependencias...")
    deps_ok, missing = check_dependencies()
    
    if not deps_ok:
        print(f"\n⚠️  Dependencias faltantes: {', '.join(missing)}")
        if not install_missing_packages(missing):
            print("❌ No se pudieron instalar las dependencias faltantes")
            sys.exit(1)
    
    print("\n📁 Verificando estructura del proyecto...")
    if not check_project_structure():
        print("❌ Estructura del proyecto incompleta")
        print("💡 Asegúrate de estar en el directorio raíz del proyecto FlowSense")
        sys.exit(1)
    
    print("\n🤖 Verificando modelos YOLO...")
    if not check_models():
        print("❌ No hay modelos YOLO disponibles")
        print("💡 Descarga un modelo con:")
        print("   wget https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.pt -P models/")
        sys.exit(1)
    
    print("\n🎉 ¡Verificación completada exitosamente!")
    print("🚀 Puedes ejecutar el demo con:")
    print("   uv run streamlit run streamlit_demo.py")
    print("   # O en modo headless:")
    print("   uv run streamlit run streamlit_demo.py --server.headless true")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
