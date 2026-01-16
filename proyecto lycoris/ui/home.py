from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle

from ui.catalog import CatalogView
from ui.importer import open_import_popup


class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = BoxLayout(orientation="vertical")
        root.size_hint = (1, 1)

        bg_path = "assets/backgrounds/home_bg.jpg"

        with root.canvas.before:
            self.bg_image = Rectangle(
                source=bg_path,
                pos=root.pos,
                size=root.size
            )
            Color(0, 0, 0, 0.45)
            self.bg_overlay = Rectangle(
                pos=root.pos,
                size=root.size
            )

        root.bind(pos=self._update_bg, size=self._update_bg)

        btn_import = Button(
            text="Importar novela",
            size_hint_y=None,
            height=48
        )

        catalog = CatalogView(on_select=self.open_novel)
        catalog.size_hint_y = 1

        btn_import.bind(
            on_release=lambda *_: open_import_popup(catalog.reload)
        )

        root.add_widget(btn_import)
        root.add_widget(catalog)

        self.add_widget(root)

    def _update_bg(self, *args):
        root = self.children[0]
        self.bg_image.pos = root.pos
        self.bg_image.size = root.size
        self.bg_overlay.pos = root.pos
        self.bg_overlay.size = root.size

    def open_novel(self, novel_path):
        print("Novels dir:", novel_path)
        player = self.manager.get_screen("player")
        player.load_novel(novel_path)
        self.manager.current = "player"
