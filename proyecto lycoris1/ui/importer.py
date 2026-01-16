#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Importador de novelas VNDS - Versión Simple y Funcional
Extrae ZIPs anidados y organiza la estructura automáticamente
"""

import os
import zipfile
import shutil
import json
import time
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooserListView
from kivy.app import App


class ImportNovelPopup(Popup):
    """Popup para importar novelas desde archivos ZIP"""
    
    def __init__(self, on_import=None, **kwargs):
        super().__init__(**kwargs)
        self.title = "Importar novela"
        self.size_hint = (0.9, 0.9)
        self.on_import = on_import
        
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        self.chooser = FileChooserListView(
            filters=['*.zip'],
            path=self._get_initial_path()
        )
        
        btns = BoxLayout(size_hint_y=None, height=48, spacing=10)
        cancel = Button(text='Cancelar')
        import_btn = Button(text='Importar')
        
        cancel.bind(on_release=lambda *_: self.dismiss())
        import_btn.bind(on_release=self.import_selected)
        
        btns.add_widget(cancel)
        btns.add_widget(import_btn)
        
        self.status = Label(text='', size_hint_y=None, height=30)
        
        layout.add_widget(self.chooser)
        layout.add_widget(self.status)
        layout.add_widget(btns)
        
        self.add_widget(layout)
    
    def _get_initial_path(self):
        """Obtiene la ruta inicial"""
        try:
            from android.storage import primary_external_storage_path  # type: ignore
            downloads = os.path.join(primary_external_storage_path(), 'Download')
            if os.path.exists(downloads):
                return downloads
        except:
            pass
        return os.path.expanduser('~')
    
    def import_selected(self, *_):
        if not self.chooser.selection:
            self.status.text = 'Selecciona un archivo ZIP'
            return
        
        zip_path = self.chooser.selection[0]
        self.status.text = 'Importando...'
        
        try:
            novel_path = import_novel_zip(zip_path)
            self.status.text = 'Novela importada correctamente'
            if self.on_import:
                self.on_import(novel_path)
            self.dismiss()
        except Exception as e:
            self.status.text = f'Error: {str(e)}'


def import_novel_zip(zip_path):
    """
    Importa una novela desde un ZIP
    
    Args:
        zip_path: Ruta al archivo ZIP
        
    Returns:
        Ruta de la novela importada
    """
    print(f"📦 Importando: {zip_path}")
    
    app = App.get_running_app()
    base = app.user_data_dir
    novels_path = os.path.join(base, "novels")
    tmp_path = os.path.join(base, "tmp")
    
    os.makedirs(novels_path, exist_ok=True)
    os.makedirs(tmp_path, exist_ok=True)
    
    # Nombre de la novela
    name = os.path.splitext(os.path.basename(zip_path))[0]
    dest = os.path.join(novels_path, name)
    
    if os.path.exists(dest):
        raise Exception("La novela ya existe")
    
    # Extraer a temporal
    tmp_extract = os.path.join(tmp_path, f"{name}_tmp")
    if os.path.exists(tmp_extract):
        shutil.rmtree(tmp_extract)
    
    os.makedirs(tmp_extract, exist_ok=True)
    
    try:
        # 1. Extraer ZIP principal
        print("📂 Extrayendo ZIP principal...")
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(tmp_extract)
        
        # 2. Extraer TODOS los ZIPs anidados
        print("🔍 Buscando y extrayendo ZIPs anidados...")
        extract_all_nested_zips(tmp_extract)
        
        # 3. Buscar la carpeta con script/main.scr
        print("🔍 Buscando script/main.scr...")
        novel_root = find_novel_root(tmp_extract)
        
        if not novel_root:
            raise Exception("No se encontró script/main.scr en el ZIP")
        
        print(f"✓ Raíz encontrada: {novel_root}")
        
        # 4. Copiar a destino final
        print(f"📁 Copiando a: {dest}")
        shutil.copytree(novel_root, dest)
        
        # 5. Validar
        if not os.path.exists(os.path.join(dest, 'script', 'main.scr')):
            raise Exception("Error en la estructura después de importar")
        
        # 6. Crear metadata
        ensure_metadata(dest)
        
        print(f"✅ Novela importada: {dest}")
        return dest
        
    finally:
        # Limpiar temporal
        if os.path.exists(tmp_extract):
            try:
                shutil.rmtree(tmp_extract)
            except:
                pass


def extract_all_nested_zips(directory, max_iterations=10):
    """
    Extrae recursivamente TODOS los ZIPs encontrados
    
    Args:
        directory: Directorio donde buscar
        max_iterations: Máximo de iteraciones
    """
    for iteration in range(max_iterations):
        found_zips = []
        
        # Buscar ZIPs
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().endswith('.zip'):
                    found_zips.append(os.path.join(root, file))
        
        if not found_zips:
            break
        
        print(f"  Iteración {iteration + 1}: {len(found_zips)} ZIP(s)")
        
        # Extraer cada ZIP
        for zip_path in found_zips:
            try:
                zip_name = os.path.basename(zip_path)
                parent_dir = os.path.dirname(zip_path)
                
                # Determinar carpeta de extracción
                zip_basename = os.path.splitext(zip_name)[0].lower()
                standard_folders = ['background', 'foreground', 'script', 'sound', 'music']
                
                if zip_basename in standard_folders:
                    # Extraer en carpeta con nombre del ZIP
                    extract_to = os.path.join(parent_dir, zip_basename)
                else:
                    # Extraer en el mismo directorio
                    extract_to = parent_dir
                
                if not zipfile.is_zipfile(zip_path):
                    continue
                
                # Extraer
                with zipfile.ZipFile(zip_path, 'r') as zf:
                    zf.extractall(extract_to)
                
                print(f"    ✓ {zip_name} → {os.path.basename(extract_to)}")
                
                # Intentar eliminar el ZIP
                try:
                    time.sleep(0.1)  # Pequeña pausa
                    os.remove(zip_path)
                except:
                    pass  # No importa si no se puede eliminar
                
            except Exception as e:
                print(f"    ⚠️ Error con {os.path.basename(zip_path)}: {e}")


def find_novel_root(extract_path):
    """
    Busca la carpeta que contiene script/main.scr
    
    Args:
        extract_path: Directorio donde buscar
        
    Returns:
        Ruta de la carpeta raíz o None
    """
    for root, dirs, files in os.walk(extract_path):
        # Buscar carpeta 'script' que contenga main.scr
        if 'script' in dirs:
            script_dir = os.path.join(root, 'script')
            if os.path.exists(os.path.join(script_dir, 'main.scr')):
                print(f"  ✓ Encontrado en: {root}")
                return root
    
    return None


def ensure_metadata(novel_dir):
    """Crea metadata si no existe"""
    meta = os.path.join(novel_dir, "novel.json")
    
    if os.path.exists(meta):
        return
    
    title = os.path.basename(novel_dir).replace("_", " ").replace("-", " ").title()
    
    data = {
        "title": title,
        "author": "Desconocido",
        "description": "",
        "cover": "default_cover.png"
    }
    
    with open(meta, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def open_import_popup(on_import=None):
    """Abre el popup de importación"""
    ImportNovelPopup(on_import=on_import).open()


# ========== FUNCIONES AUXILIARES ==========

def list_imported_novels():
    """Lista todas las novelas importadas"""
    app = App.get_running_app()
    novels_dir = os.path.join(app.user_data_dir, "novels")
    
    if not os.path.exists(novels_dir):
        return []
    
    novels = []
    for name in os.listdir(novels_dir):
        novel_path = os.path.join(novels_dir, name)
        if os.path.isdir(novel_path):
            # Leer metadata
            meta_path = os.path.join(novel_path, "novel.json")
            metadata = None
            
            if os.path.exists(meta_path):
                try:
                    with open(meta_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                except:
                    pass
            
            novels.append((name, novel_path, metadata))
    
    return novels


def get_novel_info(novel_path):
    """Obtiene información de una novela"""
    meta_path = os.path.join(novel_path, "novel.json")
    
    if os.path.exists(meta_path):
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    
    return None


def delete_novel(novel_path):
    """Elimina una novela"""
    try:
        if os.path.exists(novel_path):
            shutil.rmtree(novel_path)
            return True
    except Exception as e:
        print(f"Error eliminando novela: {e}")
    
    return False