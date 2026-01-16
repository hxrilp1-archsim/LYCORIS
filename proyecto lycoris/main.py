from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from ui.home import HomeScreen
from ui.player import PlayerScreen


class VNDSApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(PlayerScreen(name="player"))
        return sm


if __name__ == "__main__":
    VNDSApp().run()

