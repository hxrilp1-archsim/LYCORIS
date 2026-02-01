#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
UI Component para VNDS (Visual Novel Dual Screen)
Componente reutilizable para mostrar escenas de novelas visuales
"""

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window


class VNDSUI(FloatLayout):
    """
    Componente UI para mostrar escenas de novelas visuales VNDS
    
    Características:
    - Fondo de pantalla adaptable
    - Caja de texto con nombre de personaje
    - Soporte para texto con markup
    - Fondo semi-transparente en la caja de texto
    """
    
    # Configuración por defecto
    DEFAULT_TEXT_BOX_HEIGHT = dp(160)
    DEFAULT_NAME_HEIGHT = dp(32)
    DEFAULT_TEXT_BOX_COLOR = (0.1, 0.1, 0.1, 0.85)
    DEFAULT_TEXT_PADDING = dp(20)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self._build_background()
        self._build_text_box()
    
    def _build_background(self):
        """Construye el fondo de la pantalla"""
        self.bg = Image(
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(1, 1)
        )
        self.add_widget(self.bg)
    
    def _build_text_box(self):
        """Construye la caja de texto con fondo semi-transparente"""
        # Layout principal de la caja de texto
        self.text_box = BoxLayout(
            orientation="vertical",
            size_hint=(1, None),
            height=self.DEFAULT_TEXT_BOX_HEIGHT,
            pos_hint={"x": 0, "y": 0},
            padding=(self.DEFAULT_TEXT_PADDING, dp(10))
        )
        
        # Fondo semi-transparente
        with self.text_box.canvas.before:
            Color(*self.DEFAULT_TEXT_BOX_COLOR)
            self.text_box_bg = Rectangle()
        
        self.text_box.bind(
            size=self._update_text_box_bg,
            pos=self._update_text_box_bg
        )
        
        # Label para el nombre del personaje
        self.name_label = Label(
            text="",
            size_hint_y=None,
            height=self.DEFAULT_NAME_HEIGHT,
            bold=True,
            font_size=dp(18),
            color=(1, 1, 0.8, 1),  # Color dorado/amarillo claro
            halign="left",
            valign="middle",
            markup=True
        )
        self.name_label.bind(size=self.name_label.setter('text_size'))
        
        # Label para el texto principal
        self.text_label = Label(
            text="",
            halign="left",
            valign="top",
            markup=True,
            font_size=dp(16),
            color=(1, 1, 1, 1),
            text_size=(None, None)
        )
        
        # Actualizar text_size cuando cambie el tamaño
        self.text_label.bind(size=self._update_text_size)
        
        self.text_box.add_widget(self.name_label)
        self.text_box.add_widget(self.text_label)
        self.add_widget(self.text_box)
    
    def _update_text_box_bg(self, instance, value):
        """Actualiza el rectángulo de fondo de la caja de texto"""
        self.text_box_bg.pos = instance.pos
        self.text_box_bg.size = instance.size
    
    def _update_text_size(self, instance, value):
        """Actualiza el text_size del label de texto"""
        # Restar padding para evitar desbordamiento
        width = instance.width - (self.DEFAULT_TEXT_PADDING * 2)
        height = instance.height - dp(10)
        instance.text_size = (width, height)
    
    def set_background(self, path):
        """
        Establece la imagen de fondo
        
        Args:
            path: Ruta a la imagen de fondo
        """
        if path:
            self.bg.source = path
    
    def set_text(self, text, name=""):
        """
        Establece el texto y nombre del personaje
        
        Args:
            text: Texto del diálogo
            name: Nombre del personaje (opcional)
        """
        self.name_label.text = name if name else ""
        self.text_label.text = text if text else ""
        
        # Ocultar label de nombre si está vacío
        if name:
            self.name_label.opacity = 1
            self.name_label.height = self.DEFAULT_NAME_HEIGHT
        else:
            self.name_label.opacity = 0
            self.name_label.height = 0
    
    def clear_text(self):
        """Limpia el texto y el nombre"""
        self.set_text("", "")
    
    def hide_text_box(self):
        """Oculta la caja de texto"""
        self.text_box.opacity = 0
    
    def show_text_box(self):
        """Muestra la caja de texto"""
        self.text_box.opacity = 1
    
    def set_text_box_color(self, color):
        """
        Cambia el color de fondo de la caja de texto
        
        Args:
            color: Tupla RGBA (r, g, b, a)
        """
        with self.text_box.canvas.before:
            Color(*color)
            self.text_box_bg = Rectangle(
                pos=self.text_box.pos,
                size=self.text_box.size
            )
    
    def set_text_box_height(self, height):
        """
        Cambia la altura de la caja de texto
        
        Args:
            height: Nueva altura en píxeles (puede usar dp())
        """
        self.text_box.height = height


class VNDSUIAdvanced(VNDSUI):
    """
    Versión avanzada del UI con características adicionales
    
    Añade:
    - Soporte para múltiples estilos de texto
    - Animaciones de aparición
    - Soporte para sprites/imágenes superpuestas
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sprites = {}
    
    def add_sprite(self, sprite_id, image_path, pos=(0, 0), size=(100, 100)):
        """
        Añade un sprite/imagen a la escena
        
        Args:
            sprite_id: Identificador único del sprite
            image_path: Ruta a la imagen
            pos: Posición (x, y)
            size: Tamaño (width, height)
        """
        if sprite_id in self.sprites:
            self.remove_widget(self.sprites[sprite_id])
        
        sprite = Image(
            source=image_path,
            pos=pos,
            size=size,
            size_hint=(None, None),
            allow_stretch=True,
            keep_ratio=True
        )
        
        # Insertar antes de la caja de texto
        self.add_widget(sprite, index=len(self.children) - 1)
        self.sprites[sprite_id] = sprite
    
    def remove_sprite(self, sprite_id):
        """
        Elimina un sprite de la escena
        
        Args:
            sprite_id: Identificador del sprite a eliminar
        """
        if sprite_id in self.sprites:
            self.remove_widget(self.sprites[sprite_id])
            del self.sprites[sprite_id]
    
    def clear_sprites(self):
        """Elimina todos los sprites"""
        for sprite in list(self.sprites.values()):
            self.remove_widget(sprite)
        self.sprites.clear()
    
    def set_text_with_effect(self, text, name="", effect="fade"):
        """
        Establece el texto con efecto de aparición
        
        Args:
            text: Texto del diálogo
            name: Nombre del personaje
            effect: Tipo de efecto ('fade', 'instant')
        """
        if effect == "fade":
            from kivy.animation import Animation
            self.text_box.opacity = 0
            self.set_text(text, name)
            anim = Animation(opacity=1, duration=0.3)
            anim.start(self.text_box)
        else:
            self.set_text(text, name)


# ========== FUNCIONES DE UTILIDAD ==========

def create_vnds_ui(advanced=False):
    """
    Factory function para crear instancias de VNDSUI
    
    Args:
        advanced: Si True, retorna VNDSUIAdvanced
        
    Returns:
        Instancia de VNDSUI o VNDSUIAdvanced
    """
    if advanced:
        return VNDSUIAdvanced()
    return VNDSUI()


# ========== EJEMPLO DE USO ==========

if __name__ == "__main__":
    from kivy.app import App
    
    class TestApp(App):
        def build(self):
            ui = VNDSUIAdvanced()
            
            # Configurar escena de ejemplo
            ui.set_background("background.png")
            ui.set_text(
                "Este es un ejemplo de texto largo que se mostrará "
                "en la caja de diálogo de la novela visual.",
                "Personaje Principal"
            )
            
            # Añadir sprite de personaje (opcional)
            # ui.add_sprite("char1", "character.png", pos=(100, 200))
            
            return ui
    
    TestApp().run()