import os
from .errors import StructureError


def find_novel_root(directory):
    """
    Busca la carpeta raíz que contiene script/main.scr
    
    Args:
        directory: Directorio donde buscar
        
    Returns:
        Ruta de la carpeta raíz o None
        
    Raises:
        StructureError: Si no se encuentra o hay estructura inválida
    """
    print(f"🔍 Buscando script/main.scr...")
    
    candidates = []
    
    for root, dirs, files in os.walk(directory):
        # Buscar carpeta 'script' que contenga 'main.scr'
        if 'script' in dirs:
            script_dir = os.path.join(root, 'script')
            main_scr = os.path.join(script_dir, 'main.scr')
            
            if os.path.exists(main_scr):
                candidates.append(root)
                print(f"  ✓ Candidato: {os.path.basename(root)}")
    
    if not candidates:
        raise StructureError("No se encontró script/main.scr en el ZIP")
    
    # Si hay múltiples candidatos, elegir el más superficial
    if len(candidates) > 1:
        candidates.sort(key=lambda x: x.count(os.sep))
        print(f"  ⚠️ Múltiples raíces, eligiendo: {os.path.basename(candidates[0])}")
    
    selected = candidates[0]
    print(f"✓ Raíz encontrada: {os.path.basename(selected)}")
    
    return selected


def validate_novel_structure(novel_path):
    """
    Valida que una carpeta tenga estructura VNDS válida
    
    Args:
        novel_path: Ruta a la novela
        
    Returns:
        True si es válida
        
    Raises:
        StructureError: Si la estructura es inválida
    """
    # Verificar script/main.scr
    main_scr = os.path.join(novel_path, 'script', 'main.scr')
    
    if not os.path.exists(main_scr):
        raise StructureError(f"No existe script/main.scr en {novel_path}")
    
    # Verificar que main.scr no esté vacío
    if os.path.getsize(main_scr) == 0:
        raise StructureError("script/main.scr está vacío")
    
    print(f"✓ Estructura validada")
    return True


def get_novel_folders(novel_path):
    """
    Obtiene información sobre las carpetas de la novela
    
    Args:
        novel_path: Ruta a la novela
        
    Returns:
        Dict con información de carpetas
    """
    info = {
        'has_background': os.path.isdir(os.path.join(novel_path, 'background')),
        'has_foreground': os.path.isdir(os.path.join(novel_path, 'foreground')),
        'has_script': os.path.isdir(os.path.join(novel_path, 'script')),
        'has_sound': os.path.isdir(os.path.join(novel_path, 'sound')),
        'has_music': os.path.isdir(os.path.join(novel_path, 'music'))
    }
    
    return info