from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import dp
from kivy.app import App
import os, json
from ui.widgets import MovieCard


class CatalogView(ScrollView):
    def __init__(self, on_select=None, **kwargs):
        super().__init__(**kwargs)
        self.on_select = on_select

        # ⚠️ ScrollView solo puede tener UN hijo
        self.grid = GridLayout(
            cols=3,
            spacing=dp(10),
            padding=dp(10),
            size_hint_y=None
        )
        self.grid.bind(minimum_height=self.grid.setter("height"))

        self.add_widget(self.grid)
        self.reload()

    def reload(self, *_):
        self.grid.clear_widgets()

        base = App.get_running_app().user_data_dir
        novels_path = os.path.join(base, "novels")
        os.makedirs(novels_path, exist_ok=True)

        for folder in sorted(os.listdir(novels_path)):
            novel_dir = os.path.join(novels_path, folder)
            meta = os.path.join(novel_dir, "novel.json")
            if not os.path.isfile(meta):
                continue

            try:
                with open(meta, encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = {
                    "title": folder.replace("_", " ").title(),
                    "author": "Desconocido",
                    "cover": "default_cover.png"
                }

            data["cover"] = data.get("cover", "default_cover.png")

            self.grid.add_widget(
                MovieCard(data, novel_dir, self.on_select)
            )

