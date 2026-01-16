#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Vista del catálogo de novelas visuales
Muestra las novelas importadas en una cuadrícula
"""

from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.app import App
from kivy.clock import Clock
import os
import json

from ui.widgets import MovieCard
from ui.importer import list_imported_novels, get_novel_info

class CatalogView(ScrollView):
    """Vista de catálogo con cuadrícula de novelas"""
    
    def __init__(self, on_select=None, **kwargs):
        super().__init__(**kwargs)
        self.on_select = on_select
        self.novels_cache = []
        
        # Grid para las tarjetas de novelas
        self.grid = GridLayout(
            cols=self._get_columns(),
            spacing=dp(10),
            padding=dp(10),
            size_hint_y=None
        )
        self.grid.bind(minimum_height=self.grid.setter("height"))
        
        # Label para estado vacío
        self.empty_label = Label(
            text="📚 No hay novelas importadas\n\nToca 'Importar Novela' para comenzar",
            size_hint_y=None,
            height=dp(200),
            font_size=dp(16),
            halign='center',
            valign='middle',
            color=(0.7, 0.7, 0.7, 1)
        )
        self.empty_label.bind(size=self.empty_label.setter('text_size'))
        
        self.add_widget(self.grid)
        
        # Cargar novelas inicialmente
        Clock.schedule_once(lambda dt: self.reload(), 0.1)
    
    def _get_columns(self):
        """Calcula el número de columnas según el ancho de pantalla"""
        from kivy.core.window import Window
        width = Window.width
        
        if width < dp(600):
            return 2  # Móvil
        elif width < dp(1000):
            return 3  # Tablet
        else:
            return 4  # Desktop
    
    def reload(self, *_):
        """Recarga la lista de novelas desde el sistema de archivos"""
        print("🔄 Recargando catálogo de novelas...")
        
        # Limpiar grid
        self.grid.clear_widgets()
        
        # Obtener novelas usando la función optimizada
        novels = list_imported_novels()
        
        if not novels:
            # Mostrar mensaje de catálogo vacío
            self._show_empty_state()
            return
        
        # Cargar tarjetas de novelas
        loaded_count = 0
        for name, novel_path, metadata in novels:
            try:
                # Si no hay metadata, crear una básica
                if not metadata:
                    metadata = self._create_default_metadata(name, novel_path)
                
                # Validar que tenga los campos necesarios
                metadata = self._ensure_metadata_fields(metadata, name)
                
                # Crear y añadir tarjeta
                card = MovieCard(
                    data=metadata,
                    novel_path=novel_path,
                    on_select=self.on_select
                )
                self.grid.add_widget(card)
                loaded_count += 1
                
            except Exception as e:
                print(f"❌ Error cargando novela '{name}': {e}")
                continue
        
        print(f"✓ Catálogo recargado: {loaded_count} novela(s)")
        
        # Actualizar caché
        self.novels_cache = novels
    
    def _show_empty_state(self):
        """Muestra mensaje cuando no hay novelas"""
        print("📭 Catálogo vacío")
        self.grid.add_widget(self.empty_label)
    
    def _create_default_metadata(self, name, novel_path):
        """Crea metadata por defecto para una novela sin metadata"""
        return {
            "title": self._format_title(name),
            "author": "Desconocido",
            "description": "",
            "cover": "default_cover.png"
        }
    
    def _ensure_metadata_fields(self, metadata, fallback_name):
        """Asegura que la metadata tenga todos los campos necesarios"""
        defaults = {
            "title": self._format_title(fallback_name),
            "author": "Desconocido",
            "description": "",
            "cover": "default_cover.png"
        }
        
        # Combinar con defaults
        for key, default_value in defaults.items():
            if key not in metadata or not metadata[key]:
                metadata[key] = default_value
        
        return metadata
    
    def _format_title(self, name):
        """Formatea el nombre de carpeta a título legible"""
        return name.replace('_', ' ').replace('-', ' ').title()
    
    def get_novels_count(self):
        """Retorna el número de novelas en el catálogo"""
        return len(self.novels_cache)
    
    def find_novel_by_path(self, novel_path):
        """
        Busca una novela por su ruta
        
        Args:
            novel_path: Ruta de la novela
            
        Returns:
            Tupla (nombre, ruta, metadata) o None
        """
        for name, path, metadata in self.novels_cache:
            if path == novel_path:
                return (name, path, metadata)
        return None


# ========== VERSIÓN ALTERNATIVA CON LAZY LOADING ==========

class CatalogViewLazy(CatalogView):
    """
    Versión del catálogo con carga lazy (para muchas novelas)
    Solo carga las tarjetas visibles en pantalla
    """
    
    def __init__(self, **kwargs):
        self.visible_cards = set()
        super().__init__(**kwargs)
    
    def on_scroll_stop(self, touch, check_children=True):
        """Se ejecuta cuando termina el scroll"""
        self._load_visible_cards()
        return super().on_scroll_stop(touch, check_children)
    
    def _load_visible_cards(self):
        """Carga solo las tarjetas visibles en pantalla"""
        # TODO: Implementar lógica de lazy loading
        # Por ahora usa el comportamiento normal
        pass