from kivy.uix.screenmanager import Screen
from ui.vnds_ui import VNDSUI
from vnds_interpreter import VNDSInterpreter


class PlayerScreen(Screen):
    def load_novel(self, novel_path):
        self.clear_widgets()

        self.ui = VNDSUI()
        self.add_widget(self.ui)

        self.interpreter = VNDSInterpreter(novel_path)
        self.interpreter.on_text = self.ui.set_text
        self.interpreter.on_bg = self.ui.set_background

        self.interpreter.start()
