# UI para importar novelas (ZIP o carpeta) en VNDS
# Añade esto a ui/importer.py

import os
import zipfile
import shutil
import json
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooserListView
from kivy.app import App


class ImportNovelPopup(Popup):
    def __init__(self, on_import=None, **kwargs):
        super().__init__(**kwargs)
        self.title = "Importar novela"
        self.size_hint = (0.9, 0.9)
        self.on_import = on_import

        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        self.chooser = FileChooserListView(
            filters=['*.zip'],
            path='/'
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

    def import_selected(self, *_):
        if not self.chooser.selection:
            self.status.text = 'Selecciona un archivo ZIP'
            return

        zip_path = self.chooser.selection[0]

        try:
            novel_path = import_novel_zip(zip_path)
            self.status.text = 'Novela importada correctamente'
            if self.on_import:
                self.on_import(novel_path)
            self.dismiss()
        except Exception as e:
            self.status.text = str(e)


# --------- LÓGICA DE IMPORTACIÓN ---------

def import_novel_zip(zip_path):
    app = App.get_running_app()
    base = app.user_data_dir

    novels_path = os.path.join(base, "novels")
    tmp_path = os.path.join(base, "tmp")

    os.makedirs(novels_path, exist_ok=True)
    os.makedirs(tmp_path, exist_ok=True)

    name = os.path.splitext(os.path.basename(zip_path))[0]
    dest = os.path.join(novels_path, name)

    if os.path.exists(dest):
        raise Exception("La novela ya existe")

    # 🔑 COPIAR EL ZIP A ZONA SEGURA
    local_zip = os.path.join(tmp_path, name + ".zip")
    shutil.copy(zip_path, local_zip)

    os.makedirs(dest, exist_ok=True)

    # 🔓 EXTRAER DESDE STORAGE INTERNO
    with zipfile.ZipFile(local_zip, "r") as z:
        z.extractall(dest)

    os.remove(local_zip)

    # 🧠 METADATA
    ensure_metadata(dest)

    return dest



# --------- BOTÓN DE IMPORTAR PARA EL CATÁLOGO ---------

def open_import_popup(on_import=None):
    ImportNovelPopup(on_import=on_import).open()


def ensure_metadata(novel_dir):
    meta = os.path.join(novel_dir, "novel.json")

    if os.path.exists(meta):
        return

    title = os.path.basename(novel_dir).replace("_", " ").title()

    data = {
        "title": title,
        "author": "Desconocido",
        "cover": "default_cover.png"
    }

    with open(meta, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

