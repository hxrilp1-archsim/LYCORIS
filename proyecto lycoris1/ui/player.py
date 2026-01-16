#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pantalla del reproductor VNDS
Ejecuta y muestra las novelas visuales
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.metrics import dp
from vnds_interpreter import VNDSInterpreter
from kivy.app import App


class PlayerScreen(Screen):
    """Pantalla del reproductor de novelas visuales"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.interpreter = None
        self.current_novel_path = None
        self._build_ui()
    
    def _build_ui(self):
        """Construye la interfaz base del reproductor"""
        # Layout principal
        self.main_layout = BoxLayout(orientation='vertical')
        
        # Barra superior con botón de volver
        top_bar = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(48),
            padding=dp(5),
            spacing=dp(5)
        )
        
        # Botón de volver al menú
        self.btn_back = Button(
            text='← Volver al Menú',
            size_hint_x=0.3,
            background_color=(0.3, 0.3, 0.3, 1)
        )
        self.btn_back.bind(on_release=self.go_back_to_menu)
        
        # Botón de reiniciar novela
        self.btn_restart = Button(
            text='🔄 Reiniciar',
            size_hint_x=0.2,
            background_color=(0.5, 0.3, 0.3, 1)
        )
        self.btn_restart.bind(on_release=self.restart_novel)
        
        # Espacio vacío (para futuras opciones)
        spacer = BoxLayout()
        
        top_bar.add_widget(self.btn_back)
        top_bar.add_widget(self.btn_restart)
        top_bar.add_widget(spacer)
        
        # Inicialmente ocultar la barra
        top_bar.opacity = 0
        top_bar.height = 0
        self.top_bar = top_bar
        
        # Área del intérprete (se llenará al cargar novela)
        self.interpreter_area = BoxLayout()
        
        self.main_layout.add_widget(top_bar)
        self.main_layout.add_widget(self.interpreter_area)
        self.add_widget(self.main_layout)
    
    def load_novel(self, novel_path):
        """
        Carga y ejecuta una novela visual
        
        Args:
            novel_path: Ruta completa a la novela
        """
        print(f"🎮 PlayerScreen: Cargando novela desde {novel_path}")
        
        # Guardar ruta actual
        self.current_novel_path = novel_path
        
        # Limpiar intérprete anterior si existe
        if self.interpreter:
            self.interpreter_area.clear_widgets()
            self.interpreter = None
        
        try:
            # Crear nuevo intérprete
            self.interpreter = VNDSInterpreter(novel_path)
            self.interpreter_area.add_widget(self.interpreter)
            
            # Mostrar barra superior
            self.top_bar.opacity = 1
            self.top_bar.height = dp(48)
            
            print(f"✓ Novela cargada correctamente")
            
        except Exception as e:
            print(f"❌ Error cargando novela: {e}")
            # Volver al menú si hay error
            self.go_back_to_menu()
    
    def restart_novel(self, *args):
        """Reinicia la novela actual desde el principio"""
        if self.current_novel_path:
            print("🔄 Reiniciando novela...")
            self.load_novel(self.current_novel_path)
    
    def go_back_to_menu(self, *args):
        """Vuelve al menú principal"""
        print("← Volviendo al menú principal")
        
        # Limpiar intérprete
        if self.interpreter:
            # Detener música/sonidos si existen
            if hasattr(self.interpreter, 'stop_music'):
                self.interpreter.stop_music()
            if hasattr(self.interpreter, 'stop_sound'):
                self.interpreter.stop_sound()
            
            self.interpreter_area.clear_widgets()
            self.interpreter = None
        
        # Ocultar barra superior
        self.top_bar.opacity = 0
        self.top_bar.height = 0
        
        # Volver a la pantalla home
        if self.manager:
            self.manager.current = "home"
            
            # Refrescar la lista de novelas
            home = self.manager.get_screen("home")
            if hasattr(home, 'refresh_novels'):
                home.refresh_novels()
    
    def on_enter(self):
        """Se ejecuta al entrar a esta pantalla"""
        pass
    
    def on_leave(self):
        """Se ejecuta al salir de esta pantalla"""
        # Pausar música/sonidos al salir
        if self.interpreter:
            if hasattr(self.interpreter, 'current_music') and self.interpreter.current_music:
                # No detener, solo pausar por si vuelve
                pass
    
    def on_pause(self):
        """Se ejecuta cuando la app pasa a segundo plano"""
        if self.interpreter:
            if hasattr(self.interpreter, 'current_music') and self.interpreter.current_music:
                self.interpreter.current_music.stop()
        return True
    
    def on_resume(self):
        """Se ejecuta cuando la app vuelve del segundo plano"""
        pass