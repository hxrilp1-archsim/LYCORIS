from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.metrics import dp


class VNDSUI(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Fondo
        self.bg = Image(
            allow_stretch=True,
            keep_ratio=False
        )
        self.add_widget(self.bg)

        # Caja de texto
        self.text_box = BoxLayout(
            orientation="vertical",
            size_hint=(1, None),
            height=dp(160),
            pos_hint={"x": 0, "y": 0}
        )

        self.name_label = Label(
            text="",
            size_hint_y=None,
            height=dp(32),
            bold=True
        )

        self.text_label = Label(
            text="",
            text_size=(None, None),
            valign="top"
        )

        self.text_box.add_widget(self.name_label)
        self.text_box.add_widget(self.text_label)

        self.add_widget(self.text_box)

    def set_background(self, path):
        self.bg.source = path

    def set_text(self, text, name=""):
        self.name_label.text = name
        self.text_label.text = text
