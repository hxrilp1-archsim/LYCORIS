import os
import shutil
from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooserListView

from .zip_utils import extract_zip, extract_nested_zips
from .scan_utils import find_novel_root, validate_novel_structure
from .normalize import copy_novel_structure, create_metadata
from .errors import ImportError, ZipError, StructureError


class ImportNovelPopup(Popup):
    """Popup para importar novelas VNDS"""
    
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
        
        # Status
        self.status = Label(
            text='Selecciona un archivo ZIP',
            size_hint_y=None,
            height=30
        )
        
        # Botones
        btns = BoxLayout(size_hint_y=None, height=48, spacing=10)
        
        cancel_btn = Button(text='Cancelar')
        cancel_btn.bind(on_release=self.dismiss)
        
        import_btn = Button(text='Importar', background_color=(0.2, 0.6, 0.2, 1))
        import_btn.bind(on_release=self._on_import)
        
        btns.add_widget(cancel_btn)
        btns.add_widget(import_btn)
        
        layout.add_widget(self.chooser)
        layout.add_widget(self.status)
        layout.add_widget(btns)
        
        self.content = layout
    
    def _get_initial_path(self):
        """Obtiene ruta inicial del file chooser"""
        try:
            from android.storage import primary_external_storage_path  # type: ignore
            downloads = os.path.join(primary_external_storage_path(), 'Download')
            if os.path.exists(downloads):
                return downloads
        except:
            pass
        return os.path.expanduser('~')
    
    def _on_import(self, *args):
        """Maneja el clic en importar"""
        if not self.chooser.selection:
            self.status.text = '⚠️ Selecciona un archivo ZIP'
            return
        
        zip_path = self.chooser.selection[0]
        self.status.text = '⏳ Importando...'
        
        try:
            novel_path = import_novel_zip(zip_path)
            self.status.text = '✅ Novela importada'
            
            if self.on_import:
                self.on_import(novel_path)
            
            self.dismiss()
            
        except ImportError as e:
            self.status.text = f'❌ {str(e)}'
        except Exception as e:
            self.status.text = f'❌ Error inesperado: {str(e)}'


def import_novel_zip(zip_path):
    """
    Importa una novela desde un archivo ZIP
    
    Args:
        zip_path: Ruta al archivo ZIP
        
    Returns:
        Ruta de la novela importada
        
    Raises:
        ImportError: Si hay error en la importación
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
        raise ImportError(f"La novela '{novel_name}' ya existe")
    
    # Directorio temporal
    tmp_extract = os.path.join(tmp_dir, f"{novel_name}_import")
    
    if os.path.exists(tmp_extract):
        shutil.rmtree(tmp_extract)
    
    try:
        # Paso 1: Extraer ZIP principal
        print("\n1️⃣ Extrayendo ZIP principal...")
        extract_zip(zip_path, tmp_extract)
        
        # Paso 2: Extraer ZIPs anidados
        print("\n2️⃣ Extrayendo ZIPs anidados...")
        extract_nested_zips(tmp_extract)
        
        # Paso 3: Buscar raíz de la novela
        print("\n3️⃣ Buscando estructura VNDS...")
        novel_root = find_novel_root(tmp_extract)
        
        # Paso 4: Validar estructura
        print("\n4️⃣ Validando estructura...")
        validate_novel_structure(novel_root)
        
        # Paso 5: Copiar al destino final
        print("\n5️⃣ Copiando archivos...")
        copy_novel_structure(novel_root, dest_path)
        
        # Paso 6: Crear metadata
        print("\n6️⃣ Creando metadata...")
        create_metadata(dest_path, novel_name)
        
        print("\n" + "=" * 60)
        print(f"✅ IMPORTACIÓN EXITOSA")
        print(f"📁 Ubicación: {dest_path}")
        print("=" * 60)
        
        return dest_path
        
    except (ZipError, StructureError) as e:
        print(f"\n❌ ERROR: {e}")
        raise ImportError(str(e))
        
    finally:
        # Limpiar temporal
        if os.path.exists(tmp_extract):
            try:
                shutil.rmtree(tmp_extract)
            except:
                pass


def open_import_popup(on_import=None):
    """
    Abre el popup de importación
    
    Args:
        on_import: Callback cuando se importa una novela
    """
    ImportNovelPopup(on_import=on_import).open()


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
            metadata = _read_metadata(novel_path)
            novels.append((name, novel_path, metadata))
    
    return novels


def _read_metadata(novel_path):
    """Lee metadata de una novela"""
    import json
    meta_path = os.path.join(novel_path, "novel.json")
    
    if os.path.exists(meta_path):
        try:
            with open(meta_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    
    return None