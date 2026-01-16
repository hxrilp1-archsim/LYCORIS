#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pantalla principal (Home) del VNDS Reader
Muestra el catálogo de novelas y botón de importar
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from ui.catalog import CatalogView
from ui.importer import open_import_popup
import os


class HomeScreen(Screen):
    """Pantalla principal con catálogo de novelas"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.catalog = None
        self._build_ui()
    
    def _build_ui(self):
        """Construye la interfaz de la pantalla"""
        # Layout principal
        root = BoxLayout(orientation="vertical")
        root.size_hint = (1, 1)
        
        # Fondo con imagen y overlay
        self._setup_background(root)
        
        # Botón de importar
        btn_import = Button(
            text="📥 Importar Novela",
            size_hint_y=None,
            height=dp(56),
            font_size=dp(18),
            background_color=(0.2, 0.6, 0.8, 1)
        )
        btn_import.bind(on_release=self.show_import_dialog)
        
        # Catálogo de novelas
        self.catalog = CatalogView(on_select=self.open_novel)
        self.catalog.size_hint_y = 1
        
        # Añadir widgets
        root.add_widget(btn_import)
        root.add_widget(self.catalog)
        
        self.add_widget(root)
    
    def _setup_background(self, root):
        """Configura el fondo con imagen y overlay oscuro"""
        bg_path = "assets/backgrounds/home_bg.jpg"
        
        # Verificar si existe el fondo
        if not os.path.exists(bg_path):
            bg_path = ""  # Usar color sólido si no existe
        
        with root.canvas.before:
            # Imagen de fondo
            self.bg_image = Rectangle(
                source=bg_path,
                pos=root.pos,
                size=root.size
            )
            # Overlay oscuro semi-transparente
            Color(0, 0, 0, 0.45)
            self.bg_overlay = Rectangle(
                pos=root.pos,
                size=root.size
            )
        
        # Actualizar posición/tamaño cuando cambie el layout
        root.bind(pos=self._update_bg, size=self._update_bg)
    
    def _update_bg(self, *args):
        """Actualiza la posición y tamaño del fondo"""
        root = self.children[0]
        self.bg_image.pos = root.pos
        self.bg_image.size = root.size
        self.bg_overlay.pos = root.pos
        self.bg_overlay.size = root.size
    
    def show_import_dialog(self, *args):
        """Muestra el diálogo de importación"""
        open_import_popup(on_import=self.on_novel_imported)
    
    def on_novel_imported(self, novel_path):
        """
        Callback cuando se importa una novela
        
        Args:
            novel_path: Ruta de la novela importada
        """
        print(f"✓ Novela importada: {novel_path}")
        # Refrescar el catálogo
        self.refresh_novels()
    
    def refresh_novels(self):
        """Refresca la lista de novelas en el catálogo"""
        if self.catalog:
            self.catalog.reload()
    
    def open_novel(self, novel_path):
        """
        Abre una novela en el reproductor
        
        Args:
            novel_path: Ruta de la novela a abrir
        """
        print(f"🎮 Abriendo novela: {novel_path}")
        
        # Obtener la pantalla del reproductor
        player = self.manager.get_screen("player")
        
        # Cargar la novela
        if hasattr(player, 'load_novel'):
            player.load_novel(novel_path)
        
        # Cambiar a la pantalla del reproductor
        self.manager.current = "player"
    
    def on_enter(self):
        """Se ejecuta cuando se entra a esta pantalla"""
        # Refrescar el catálogo cada vez que se muestra la pantalla
        self.refresh_novels()
    
    def on_pre_enter(self):
        """Se ejecuta antes de mostrar la pantalla"""
        pass
    
    def on_leave(self):
        """Se ejecuta al salir de esta pantalla"""
        pass