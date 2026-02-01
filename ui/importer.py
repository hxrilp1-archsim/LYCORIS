#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
UI para importar novelas VNDS
Versión optimizada con extracción de ZIPs anidados
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
from kivy.clock import Clock


class ImportNovelPopup(Popup):
    """Popup para importar novelas desde archivos ZIP"""
    
    def __init__(self, on_import=None, **kwargs):
        super().__init__(**kwargs)
        self.title = "Importar novela VNDS"
        self.size_hint = (0.9, 0.9)
        self.on_import = on_import
        
        self._build_ui()
    
    def _build_ui(self):
        """Construye la interfaz"""
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # File chooser
        self.chooser = FileChooserListView(
            filters=['*.zip'],
            path=self._get_initial_path()
        )
        layout.add_widget(self.chooser)
        
        # Status label
        self.status = Label(
            text='Selecciona un archivo ZIP de novela visual',
            size_hint_y=None,
            height=30,
            color=(0.7, 0.7, 0.7, 1)
        )
        layout.add_widget(self.status)
        
        # Botones
        btn_layout = BoxLayout(size_hint_y=None, height=48, spacing=10)
        
        cancel_btn = Button(text='Cancelar')
        cancel_btn.bind(on_release=self.dismiss)
        
        import_btn = Button(
            text='Importar',
            background_color=(0.2, 0.6, 0.2, 1)
        )
        import_btn.bind(on_release=self.import_selected)
        
        btn_layout.add_widget(cancel_btn)
        btn_layout.add_widget(import_btn)
        layout.add_widget(btn_layout)
        
        self.content = layout
    
    def _get_initial_path(self):
        """Obtiene la ruta inicial del file chooser"""
        try:
            from android.storage import primary_external_storage_path  # type: ignore
            downloads = os.path.join(
                primary_external_storage_path(),
                'Download'
            )
            if os.path.exists(downloads):
                return downloads
        except ImportError:
            pass
        
        return os.path.expanduser('~')
    
    def import_selected(self, *_):
        """Importa el archivo ZIP seleccionado"""
        if not self.chooser.selection:
            self._show_error('Selecciona un archivo ZIP')
            return
        
        zip_path = self.chooser.selection[0]
        
        if not zip_path.lower().endswith('.zip'):
            self._show_error('El archivo debe ser un ZIP')
            return
        
        # Mostrar estado de carga
        self.status.text = '⏳ Importando...'
        self.status.color = (1, 1, 0, 1)
        
        # Importar en el siguiente frame
        Clock.schedule_once(lambda dt: self._do_import(zip_path), 0.1)
    
    def _do_import(self, zip_path):
        """Ejecuta la importación"""
        try:
            novel_path = import_novel_zip(zip_path)
            self._show_success(novel_path)
        except Exception as e:
            self._show_error(str(e))
    
    def _show_error(self, message):
        """Muestra un mensaje de error"""
        self.status.text = f'❌ {message}'
        self.status.color = (1, 0.3, 0.3, 1)
    
    def _show_success(self, novel_path):
        """Muestra mensaje de éxito y cierra el popup"""
        self.status.text = '✅ Novela importada correctamente'
        self.status.color = (0.2, 1, 0.2, 1)
        
        if self.on_import:
            self.on_import(novel_path)
        
        # Cerrar después de mostrar el mensaje
        Clock.schedule_once(lambda dt: self.dismiss(), 1.0)


def import_novel_zip(zip_path):
    """
    Importa una novela desde un archivo ZIP
    
    Args:
        zip_path: Ruta al archivo ZIP
        
    Returns:
        Ruta de la novela importada
        
    Raises:
        Exception: Si hay error en la importación
    """
    print("=" * 60)
    print(f"📦 IMPORTANDO: {os.path.basename(zip_path)}")
    print("=" * 60)
    
    app = App.get_running_app()
    base_dir = app.user_data_dir
    novels_dir = os.path.join(base_dir, "novels")
    tmp_dir = os.path.join(base_dir, "tmp")
    
    os.makedirs(novels_dir, exist_ok=True)
    os.makedirs(tmp_dir, exist_ok=True)
    
    # Nombre de la novela
    novel_name = os.path.splitext(os.path.basename(zip_path))[0]
    dest_path = os.path.join(novels_dir, novel_name)
    
    if os.path.exists(dest_path):
        raise Exception(f"La novela '{novel_name}' ya existe")
    
    # Directorio temporal para extracción
    tmp_extract = os.path.join(tmp_dir, f"{novel_name}_import")
    
    if os.path.exists(tmp_extract):
        shutil.rmtree(tmp_extract)
    
    os.makedirs(tmp_extract, exist_ok=True)
    
    try:
        # 1️⃣ Extraer ZIP principal
        print("\n1️⃣ Extrayendo ZIP principal...")
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(tmp_extract)
        
        # 2️⃣ Extraer TODOS los ZIPs anidados
        print("\n2️⃣ Extrayendo ZIPs anidados...")
        extract_all_nested_zips(tmp_extract)
        
        # 🔍 DEBUG: Mostrar contenido después de extraer ZIPs
        print("\n🔍 DEBUG: Contenido del temporal:")
        for root, dirs, files in os.walk(tmp_extract):
            level = root.replace(tmp_extract, '').count(os.sep)
            indent = '  ' * level
            print(f"{indent}📁 {os.path.basename(root)}/")
            subindent = '  ' * (level + 1)
            for d in dirs[:5]:
                print(f"{subindent}📁 {d}/")
            for f in files[:3]:
                print(f"{subindent}📄 {f}")
            if len(files) > 3:
                print(f"{subindent}... +{len(files) - 3} archivos más")
        
        # 3️⃣ Buscar la carpeta con script/main.scr
        print("\n3️⃣ Buscando script/main.scr...")
        novel_root = find_novel_root(tmp_extract)
        
        if not novel_root:
            raise Exception("No se encontró script/main.scr en el ZIP")
        
        # ⚠️ VALIDACIÓN: Asegurarse que NO sea la carpeta "script" misma
        if os.path.basename(novel_root) == 'script':
            print(f"  ⚠️ ERROR: La raíz encontrada ES la carpeta script")
            print(f"  🔧 Buscando carpeta padre...")
            novel_root = os.path.dirname(novel_root)
            print(f"  ✓ Nueva raíz: {os.path.basename(novel_root)}")
        
        print(f"  ✓ Raíz final: {os.path.basename(novel_root)}")
        
        # 🔍 DEBUG: Mostrar contenido de la raíz encontrada
        print(f"\n🔍 DEBUG: Contenido de la raíz ({os.path.basename(novel_root)}):")
        if os.path.exists(novel_root):
            items = os.listdir(novel_root)
            for item in items:
                item_path = os.path.join(novel_root, item)
                if os.path.isdir(item_path):
                    print(f"  📁 {item}/")
                    # Mostrar primeros archivos de cada carpeta
                    try:
                        subitems = os.listdir(item_path)[:3]
                        for subitem in subitems:
                            print(f"      - {subitem}")
                    except:
                        pass
                else:
                    print(f"  📄 {item}")
        
        # 4️⃣ Copiar a destino final
        print("\n4️⃣ Copiando archivos...")
        print(f"  Desde: {novel_root}")
        print(f"  Hacia: {dest_path}")
        shutil.copytree(novel_root, dest_path)
        
        # 🔧 Normalizar estructura VNDS
        normalize_vnds_folders(dest_path)

        # 🔍 DEBUG: Verificar qué se copió
        print(f"\n🔍 DEBUG: Contenido copiado en destino:")
        if os.path.exists(dest_path):
            items = os.listdir(dest_path)
            print(f"  Total de elementos: {len(items)}")
            for item in items:
                item_path = os.path.join(dest_path, item)
                if os.path.isdir(item_path):
                    file_count = len(os.listdir(item_path))
                    print(f"  📁 {item}/ ({file_count} archivos)")
                else:
                    print(f"  📄 {item}")
        
        # 5️⃣ Validar estructura
        if not os.path.exists(os.path.join(dest_path, 'script', 'main.scr')):
            raise Exception("Error: estructura inválida después de importar")
        
        # 6️⃣ Crear metadata
        print("\n5️⃣ Creando metadata...")
        ensure_metadata(dest_path)
        
        print("\n" + "=" * 60)
        print(f"✅ IMPORTACIÓN EXITOSA")
        print(f"📁 {dest_path}")
        print("=" * 60)
        
        return dest_path
        
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
        # Buscar ZIPs
        found_zips = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().endswith('.zip'):
                    found_zips.append(os.path.join(root, file))
        
        if not found_zips:
            break
        
        print(f"  📦 Iteración {iteration + 1}: {len(found_zips)} ZIP(s)")
        
        # Extraer cada ZIP
        for zip_path in found_zips:
            try:
                zip_name = os.path.basename(zip_path)
                parent_dir = os.path.dirname(zip_path)
                zip_basename = os.path.splitext(zip_name)[0].lower()
                
                # Carpetas estándar de VNDS
                standard_folders = ['background', 'foreground', 'script', 'sound', 'music']
                
                # Determinar dónde extraer
                if zip_basename in standard_folders:
                    extract_to = os.path.join(parent_dir, zip_basename)
                else:
                    extract_to = parent_dir
                
                # Verificar que sea ZIP válido
                if not zipfile.is_zipfile(zip_path):
                    continue
                
                # Extraer
                with zipfile.ZipFile(zip_path, 'r') as zf:
                    zf.extractall(extract_to)
                
                print(f"    ✓ {zip_name} → {os.path.basename(extract_to)}")
                
                # Intentar eliminar el ZIP
                try:
                    time.sleep(0.1)
                    os.remove(zip_path)
                except:
                    pass  # No es crítico si no se puede eliminar
                
            except Exception as e:
                print(f"    ⚠️ Error con {os.path.basename(zip_path)}: {e}")


def find_novel_root(directory):
    """
    Busca la carpeta que contiene script/main.scr
    
    Args:
        directory: Directorio donde buscar
        
    Returns:
        Ruta de la carpeta raíz o None
    """
    candidates = []
    
    for root, dirs, files in os.walk(directory):
        # Buscar carpeta 'script' que contenga main.scr
        if 'script' in dirs:
            script_dir = os.path.join(root, 'script')
            main_scr = os.path.join(script_dir, 'main.scr')
            
            if os.path.exists(main_scr):
                # root es la carpeta que CONTIENE script/
                # NO la carpeta script/ misma
                candidates.append(root)
                print(f"  ✓ Candidato: {os.path.basename(root)}")
    
    if not candidates:
        # Buscar main.scr directamente por si acaso
        for root, dirs, files in os.walk(directory):
            if 'main.scr' in files:
                # Si encontramos main.scr y el padre se llama 'script'
                if os.path.basename(root) == 'script':
                    # Retornar el PADRE de script
                    parent = os.path.dirname(root)
                    candidates.append(parent)
                    print(f"  ✓ Candidato (padre de script): {os.path.basename(parent)}")
    
    if not candidates:
        return None
    
    # Elegir el candidato más superficial
    candidates.sort(key=lambda x: x.count(os.sep))
    
    return candidates[0]


def ensure_metadata(novel_dir):
    """Crea metadata si no existe"""
    meta_path = os.path.join(novel_dir, "novel.json")
    
    if os.path.exists(meta_path):
        return
    
    title = os.path.basename(novel_dir).replace("_", " ").replace("-", " ").title()
    
    data = {
        "title": title,
        "author": "Desconocido",
        "description": "",
        "cover": "default_cover.png"
    }
    
    with open(meta_path, "w", encoding="utf-8") as f:
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
            metadata = get_novel_info(novel_path)
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
    """Elimina una novela importada"""
    try:
        if os.path.exists(novel_path):
            shutil.rmtree(novel_path)
            return True
    except Exception as e:
        print(f"Error eliminando novela: {e}")
    
    return False

def normalize_vnds_folders(novel_root):
    """
    Arregla estructuras tipo script/script, background/background, etc
    """
    folders = ['script', 'background', 'foreground', 'sound', 'music']

    for folder in folders:
        outer = os.path.join(novel_root, folder)
        inner = os.path.join(outer, folder)

        if os.path.isdir(inner):
            print(f"🔧 Normalizando carpeta: {folder}")

            for item in os.listdir(inner):
                src = os.path.join(inner, item)
                dst = os.path.join(outer, item)

                if os.path.exists(dst):
                    continue

                shutil.move(src, dst)

            shutil.rmtree(inner, ignore_errors=True)
