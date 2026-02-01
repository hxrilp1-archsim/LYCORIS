import os
import shutil
import json
from datetime import datetime


def copy_novel_structure(source_path, dest_path):
    """
    Copia la estructura de la novela al destino final
    
    Args:
        source_path: Ruta origen
        dest_path: Ruta destino
        
    Raises:
        IOError: Si hay error en la copia
    """
    print(f"📁 Copiando estructura...")
    print(f"  Desde: {os.path.basename(source_path)}")
    print(f"  Hacia: {os.path.basename(dest_path)}")
    
    try:
        if os.path.exists(dest_path):
            shutil.rmtree(dest_path)
        
        shutil.copytree(source_path, dest_path)
        
        # Verificar contenido copiado
        copied_items = os.listdir(dest_path)
        print(f"  ✓ Elementos copiados: {len(copied_items)}")
        
    except Exception as e:
        raise IOError(f"Error copiando estructura: {e}")


def create_metadata(novel_path, novel_name):
    """
    Crea archivo de metadata para la novela
    
    Args:
        novel_path: Ruta de la novela
        novel_name: Nombre de la novela
    """
    meta_path = os.path.join(novel_path, "novel.json")
    
    if os.path.exists(meta_path):
        print("  ℹ️ Metadata ya existe")
        return
    
    # Formatear título
    title = novel_name.replace("_", " ").replace("-", " ").title()
    
    metadata = {
        "title": title,
        "author": "Desconocido",
        "description": "",
        "cover": "default_cover.png",
        "version": "1.0",
        "imported_date": datetime.now().isoformat()
    }
    
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"  ✓ Metadata creada")