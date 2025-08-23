#!/usr/bin/env python3
"""
Script para corregir el problema de tracking de zonas.
"""

def fix_zone_tracking():
    """
    Corrige el problema de tracking de zonas en video_unified.py
    """
    
    # Leer el archivo original
    with open('src/video_unified.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar la línea problemática
    problematic_line = "                        # Solo procesar objetos confirmados"
    replacement_line = "                        # Procesar objetos confirmados Y objetos en zonas"
    
    if problematic_line in content:
        content = content.replace(problematic_line, replacement_line)
        print("✅ Línea problemática reemplazada")
    else:
        print("❌ No se encontró la línea problemática")
        return
    
    # Buscar la condición restrictiva
    old_condition = "                        if oid in id_map:"
    new_condition = """                        # Verificar si el objeto está confirmado O ya está en una zona
                        is_confirmed = oid in id_map
                        is_in_zone = any(oid in id_map.values())
                        
                        if is_confirmed or is_in_zone:"""
    
    if old_condition in content:
        content = content.replace(old_condition, new_condition)
        print("✅ Condición de tracking corregida")
    else:
        print("❌ No se encontró la condición restrictiva")
        return
    
    # Guardar el archivo corregido
    with open('src/video_unified.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("📁 Archivo src/video_unified.py corregido")
    print("\n🔧 CAMBIOS REALIZADOS:")
    print("   1. Comentario actualizado")
    print("   2. Lógica de tracking corregida para incluir objetos en zonas")
    print("\n💡 EXPLICACIÓN:")
    print("   • ANTES: Solo procesaba objetos confirmados (5+ frames)")
    print("   • AHORA: Procesa objetos confirmados Y objetos que ya están en zonas")
    print("   • RESULTADO: Se detectarán tanto entradas como salidas")


if __name__ == "__main__":
    fix_zone_tracking()
