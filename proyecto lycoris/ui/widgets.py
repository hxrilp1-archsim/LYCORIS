
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.metrics import dp
import os


class MovieCard(ButtonBehavior, BoxLayout):

    def __init__(self, data, path, callback, **kwargs):
        super().__init__(**kwargs)

        self.callback = callback
        self.path = path

        # --- Tamaño tipo poster 9:16 ---
        self.size_hint = (None, None)
        self.width = dp(140)
        poster_height = dp(140 * 16 / 9)
        text_height = dp(48)
        self.height = poster_height + text_height

        self.background_normal = ""
        self.background_color = (0, 0, 0, 0)

        # --- Layout principal ---
        layout = BoxLayout(
            orientation="vertical",
            size_hint=(1, 1)
        )

        # --- Imagen ---
        cover_path = os.path.join(path, data.get("cover", ""))
        if not os.path.exists(cover_path):
            cover_path = "assets/default_cover.png"

        cover = Image(
            source=cover_path,
            fit_mode="fill"
        )

        # --- Caja de texto ---
        text_box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=text_height,
            padding=[dp(8), dp(6)]
        )

        title = Label(
            text=data.get("title", "Desconocido"),
            font_size="13sp",
            bold=True,
            halign="center",
            valign="middle",
            text_size=(self.width - dp(16), None),
            shorten=True,
            shorten_from="right"
        )

        title.bind(size=title.setter("text_size"))

        # --- Ensamble ---
        text_box.add_widget(title)
        layout.add_widget(cover)
        layout.add_widget(text_box)
        self.add_widget(layout)

    def on_release(self):
        if self.callback:
            self.callback(self.path)
