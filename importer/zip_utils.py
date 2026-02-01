import os
import zipfile
import time
from .errors import ZipError


def extract_zip(zip_path, dest_path):
    """
    Extrae un archivo ZIP a un directorio
    
    Args:
        zip_path: Ruta al archivo ZIP
        dest_path: Directorio de destino
        
    Raises:
        ZipError: Si hay error en la extracción
    """
    try:
        if not zipfile.is_zipfile(zip_path):
            raise ZipError(f"'{os.path.basename(zip_path)}' no es un ZIP válido")
        
        os.makedirs(dest_path, exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zf:
            # Verificar rutas peligrosas
            for member in zf.namelist():
                if member.startswith('/') or '..' in member:
                    raise ZipError("ZIP contiene rutas peligrosas")
            
            zf.extractall(dest_path)
            
    except zipfile.BadZipFile as e:
        raise ZipError(f"ZIP corrupto: {e}")
    except Exception as e:
        raise ZipError(f"Error extrayendo ZIP: {e}")


def find_all_zips(directory):
    """
    Encuentra todos los archivos ZIP en un directorio
    
    Args:
        directory: Directorio donde buscar
        
    Returns:
        Lista de rutas a archivos ZIP
    """
    zips = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.zip'):
                zips.append(os.path.join(root, file))
    return zips


def extract_nested_zips(directory, max_iterations=10):
    """
    Extrae recursivamente todos los ZIPs anidados
    
    Args:
        directory: Directorio donde buscar ZIPs
        max_iterations: Número máximo de iteraciones
        
    Returns:
        Número de ZIPs extraídos
    """
    print(f"🔍 Buscando ZIPs anidados en: {os.path.basename(directory)}")
    
    extracted_count = 0
    
    for iteration in range(max_iterations):
        zips = find_all_zips(directory)
        
        if not zips:
            break
        
        print(f"  📦 Iteración {iteration + 1}: {len(zips)} ZIP(s)")
        
        for zip_path in zips:
            try:
                zip_name = os.path.basename(zip_path)
                parent_dir = os.path.dirname(zip_path)
                
                # Determinar carpeta de extracción
                extract_dir = _get_extract_directory(zip_path, parent_dir)
                
                # Extraer
                extract_zip(zip_path, extract_dir)
                extracted_count += 1
                
                print(f"    ✓ {zip_name} → {os.path.basename(extract_dir)}")
                
                # Intentar eliminar el ZIP
                _safe_remove(zip_path)
                
            except ZipError as e:
                print(f"    ⚠️ {os.path.basename(zip_path)}: {e}")
                continue
    
    if extracted_count > 0:
        print(f"✅ Total extraídos: {extracted_count}")
    
    return extracted_count


def _get_extract_directory(zip_path, parent_dir):
    """
    Determina el directorio de extracción según el nombre del ZIP
    
    Args:
        zip_path: Ruta al archivo ZIP
        parent_dir: Directorio padre
        
    Returns:
        Ruta del directorio de extracción
    """
    zip_basename = os.path.splitext(os.path.basename(zip_path))[0].lower()
    
    # Carpetas estándar de VNDS
    standard_folders = ['background', 'foreground', 'script', 'sound', 'music']
    
    if zip_basename in standard_folders:
        return os.path.join(parent_dir, zip_basename)
    
    return parent_dir


def _safe_remove(file_path, retries=3):
    """
    Intenta eliminar un archivo de forma segura
    
    Args:
        file_path: Ruta al archivo
        retries: Número de reintentos
    """
    for attempt in range(retries):
        try:
            time.sleep(0.1)  # Pequeña pausa
            os.remove(file_path)
            return
        except PermissionError:
            if attempt < retries - 1:
                time.sleep(0.2)
            else:
                # No es crítico si no se puede eliminar
                pass
