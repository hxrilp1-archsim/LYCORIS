#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
VNDS Reader - Aplicación principal
Lector de novelas visuales en formato VNDS
"""

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from ui.home import HomeScreen
from ui.player import PlayerScreen
from ui.importer import list_imported_novels
import os


class VNDSApp(App):
    """Aplicación principal de VNDS Reader"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.novels_path = None
        self.screen_manager = None
    
    def build(self):
        """Construye la interfaz de la aplicación"""
        # Configurar rutas
        self._setup_paths()
        
        # Listar novelas importadas (debug)
        self._list_novels_debug()
        
        # Crear ScreenManager
        self.screen_manager = ScreenManager(transition=SlideTransition())
        
        # Añadir pantallas
        self.screen_manager.add_widget(HomeScreen(name="home"))
        self.screen_manager.add_widget(PlayerScreen(name="player"))
        
        return self.screen_manager
    
    def _setup_paths(self):
        """Configura las rutas de la aplicación"""
        self.novels_path = os.path.join(self.user_data_dir, "novels")
        os.makedirs(self.novels_path, exist_ok=True)
    
    def _list_novels_debug(self):
        """Lista las novelas importadas (modo debug)"""
        novels = list_imported_novels()
        
        if novels:
            print("=" * 50)
            print("📚 NOVELAS IMPORTADAS:")
            print("=" * 50)
            for name, path, metadata in novels:
                title = metadata.get('title', name) if metadata else name
                author = metadata.get('author', 'Desconocido') if metadata else 'Desconocido'
                print(f"✓ {title}")
                print(f"  Autor: {author}")
                print(f"  Carpeta: {name}")
                print(f"  Ruta: {path}")
                print("-" * 50)
        else:
            print("=" * 50)
            print("📭 No hay novelas importadas aún")
            print("=" * 50)
            print(f"Carpeta de novelas: {self.novels_path}")
    
    def get_novels_path(self):
        """Retorna la ruta donde se guardan las novelas"""
        return self.novels_path
    
    def go_to_home(self):
        """Navega a la pantalla principal"""
        if self.screen_manager:
            self.screen_manager.current = "home"
            # Refrescar la lista de novelas
            home_screen = self.screen_manager.get_screen("home")
            if hasattr(home_screen, 'refresh_novels'):
                home_screen.refresh_novels()
    
    def go_to_player(self, novel_path):
        """
        Navega a la pantalla del reproductor
        
        Args:
            novel_path: Ruta de la novela a reproducir
        """
        if self.screen_manager:
            player_screen = self.screen_manager.get_screen("player")
            if hasattr(player_screen, 'load_novel'):
                player_screen.load_novel(novel_path)
            self.screen_manager.current = "player"
    
    def on_pause(self):
        """Maneja cuando la app pasa a segundo plano (Android)"""
        return True
    
    def on_resume(self):
        """Maneja cuando la app vuelve del segundo plano (Android)"""
        pass


if __name__ == "__main__":
    VNDSApp().run()