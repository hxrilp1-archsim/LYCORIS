#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Widgets personalizados para la UI de VNDS Reader
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp
from kivy.animation import Animation
import os


class MovieCard(ButtonBehavior, BoxLayout):
    """Tarjeta de novela visual con estilo poster"""
    
    # Configuración de tamaño (proporción 9:16 estilo poster)
    CARD_WIDTH = dp(140)
    ASPECT_RATIO = 16 / 9
    TEXT_HEIGHT = dp(48)
    
    def __init__(self, data, novel_path, on_select, **kwargs):
        super().__init__(**kwargs)
        
        self.on_select = on_select
        self.novel_path = novel_path
        self.data = data
        
        # Configuración del botón
        self.orientation = "vertical"
        self.size_hint = (None, None)
        self.width = self.CARD_WIDTH
        self.height = (self.CARD_WIDTH * self.ASPECT_RATIO) + self.TEXT_HEIGHT
        
        self._build_card()
        self._setup_effects()
    
    def _build_card(self):
        """Construye la estructura de la tarjeta"""
        # Container con fondo y bordes redondeados
        with self.canvas.before:
            Color(0.15, 0.15, 0.15, 1)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(8)]
            )
        
        self.bind(pos=self._update_rect, size=self._update_rect)
        
        # Imagen de portada
        self.cover = self._create_cover_image()
        self.add_widget(self.cover)
        
        # Caja de texto con título
        text_box = self._create_text_box()
        self.add_widget(text_box)
    
    def _create_cover_image(self):
        """Crea la imagen de portada"""
        cover_path = self._get_cover_path()
        
        # Container para la imagen con bordes redondeados superiores
        cover_container = BoxLayout(
            size_hint=(1, None),
            height=self.CARD_WIDTH * self.ASPECT_RATIO
        )
        
        cover = Image(
            source=cover_path,
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(1, 1)
        )
        
        cover_container.add_widget(cover)
        return cover_container
    
    def _get_cover_path(self):
        """Obtiene la ruta de la imagen de portada"""
        cover_name = self.data.get("cover", "default_cover.png")
        
        # Intentar cargar portada de la novela
        cover_path = os.path.join(self.novel_path, cover_name)
        
        if os.path.exists(cover_path):
            return cover_path
        
        # Intentar portada en carpeta foreground
        cover_path_fg = os.path.join(self.novel_path, "foreground", cover_name)
        if os.path.exists(cover_path_fg):
            return cover_path_fg
        
        # Intentar portada en carpeta background
        cover_path_bg = os.path.join(self.novel_path, "background", cover_name)
        if os.path.exists(cover_path_bg):
            return cover_path_bg
        
        # Fallback a portada por defecto
        default_path = "assets/default_cover.png"
        if os.path.exists(default_path):
            return default_path
        
        # Si no existe ninguna, retornar string vacío
        return ""
    
    def _create_text_box(self):
        """Crea la caja de texto con título y autor"""
        text_box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=self.TEXT_HEIGHT,
            padding=[dp(8), dp(6)],
            spacing=dp(2)
        )
        
        # Título de la novela
        title = Label(
            text=self.data.get("title", "Sin título"),
            font_size=dp(13),
            bold=True,
            halign="center",
            valign="middle",
            shorten=True,
            shorten_from="right",
            color=(1, 1, 1, 1)
        )
        title.bind(
            size=lambda instance, value: setattr(
                instance, 'text_size', 
                (instance.width, None)
            )
        )
        
        # Autor (opcional, más pequeño)
        author = self.data.get("author", "")
        if author and author != "Desconocido":
            author_label = Label(
                text=author,
                font_size=dp(10),
                halign="center",
                valign="top",
                color=(0.7, 0.7, 0.7, 1),
                shorten=True,
                shorten_from="right"
            )
            author_label.bind(
                size=lambda instance, value: setattr(
                    instance, 'text_size', 
                    (instance.width, None)
                )
            )
            text_box.add_widget(title)
            text_box.add_widget(author_label)
        else:
            text_box.add_widget(title)
        
        return text_box
    
    def _setup_effects(self):
        """Configura efectos visuales (hover, press)"""
        # Estado normal
        self.scale_value = 1.0
    
    def _update_rect(self, *args):
        """Actualiza el rectángulo de fondo"""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def on_press(self):
        """Efecto visual al presionar"""
        # Animación de escala al presionar
        anim = Animation(
            scale_value=0.95,
            duration=0.1
        )
        anim.bind(on_complete=lambda *args: setattr(self, 'scale_value', 0.95))
        
        # Oscurecer fondo
        with self.canvas.before:
            Color(0.1, 0.1, 0.1, 1)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(8)]
            )
    
    def on_release(self):
        """Maneja el click en la tarjeta"""
        # Restaurar escala
        with self.canvas.before:
            Color(0.15, 0.15, 0.15, 1)
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(8)]
            )
        
        # Ejecutar callback
        if self.on_select:
            print(f"🎮 Seleccionada novela: {self.data.get('title', 'Sin título')}")
            self.on_select(self.novel_path)


class NovelDetailCard(BoxLayout):
    """Tarjeta expandida con detalles completos de la novela"""
    
    def __init__(self, data, novel_path, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.data = data
        self.novel_path = novel_path
        self.padding = dp(20)
        self.spacing = dp(15)
        
        self._build_detail_card()
    
    def _build_detail_card(self):
        """Construye la tarjeta de detalles"""
        # Portada más grande
        cover_container = BoxLayout(
            size_hint=(1, None),
            height=dp(300)
        )
        
        cover_path = self._get_cover_path()
        cover = Image(
            source=cover_path,
            allow_stretch=True,
            keep_ratio=True
        )
        cover_container.add_widget(cover)
        self.add_widget(cover_container)
        
        # Título
        title = Label(
            text=self.data.get("title", "Sin título"),
            font_size=dp(24),
            bold=True,
            size_hint_y=None,
            height=dp(40)
        )
        self.add_widget(title)
        
        # Autor
        author = Label(
            text=f"Por: {self.data.get('author', 'Desconocido')}",
            font_size=dp(16),
            color=(0.7, 0.7, 0.7, 1),
            size_hint_y=None,
            height=dp(30)
        )
        self.add_widget(author)
        
        # Descripción
        description = self.data.get("description", "Sin descripción disponible")
        desc_label = Label(
            text=description,
            font_size=dp(14),
            halign="left",
            valign="top"
        )
        desc_label.bind(
            size=lambda instance, value: setattr(
                instance, 'text_size',
                (instance.width, None)
            )
        )
        self.add_widget(desc_label)
    
    def _get_cover_path(self):
        """Obtiene la ruta de la portada"""
        cover_name = self.data.get("cover", "default_cover.png")
        cover_path = os.path.join(self.novel_path, cover_name)
        
        if os.path.exists(cover_path):
            return cover_path
        
        return "assets/default_cover.png"


class EmptyStateWidget(BoxLayout):
    """Widget para mostrar cuando no hay contenido"""
    
    def __init__(self, message="No hay contenido disponible", icon="📚", **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(40)
        self.spacing = dp(20)
        
        # Icono
        icon_label = Label(
            text=icon,
            font_size=dp(64),
            size_hint_y=None,
            height=dp(80)
        )
        
        # Mensaje
        message_label = Label(
            text=message,
            font_size=dp(16),
            color=(0.6, 0.6, 0.6, 1),
            halign="center",
            valign="middle"
        )
        message_label.bind(
            size=lambda instance, value: setattr(
                instance, 'text_size',
                (instance.width, None)
            )
        )
        
        self.add_widget(icon_label)
        self.add_widget(message_label)