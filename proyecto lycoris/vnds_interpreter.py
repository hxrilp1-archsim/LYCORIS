#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Intérprete VNDS (Visual Novel Dual Screen) para Android
Compatible con Kivy para portabilidad a Android
Con sistema de guardado/carga y comandos extendidos
"""

from kivy.utils import platform 
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
import os
import json
import re
from datetime import datetime

class VNDSScript:
    """Parser para scripts VNDS (.scr)"""
  
    def __init__(self, script_path):
        self.script_path = script_path
        self.commands = []
        self.current_line = 0
        self.labels = {}  # Almacena posiciones de etiquetas
        self.load_script()
    
    def load_script(self):
        """Carga y parsea el archivo de script"""
        try:
            with open(self.script_path, 'r', encoding='utf-8') as f:
                line_num = 0
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Detectar etiquetas
                        if line.startswith('~'):
                            label_name = line[1:].strip()
                            self.labels[label_name] = line_num
                        self.commands.append(line)
                    line_num += 1
        except Exception as e:
            print(f"Error cargando script: {e}")
    
    def get_next_command(self):
        """Obtiene el siguiente comando del script"""
        if self.current_line < len(self.commands):
            cmd = self.commands[self.current_line]
            self.current_line += 1
            return cmd
        return None
    
    def jump_to_label(self, label):
        """Salta a una etiqueta específica"""
        if label in self.labels:
            self.current_line = self.labels[label]
            return True
        return False
    
    def reset(self):
        """Reinicia el script"""
        self.current_line = 0

class SpriteLayer(FloatLayout):
    """Capa para manejar sprites con posiciones"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sprites = {}
    
    def add_sprite(self, sprite_id, image_path, x=0, y=0):
        """Añade un sprite en una posición específica"""
        if sprite_id in self.sprites:
            self.remove_widget(self.sprites[sprite_id])
        
        sprite = Image(source=image_path, 
                      size_hint=(None, None),
                      allow_stretch=True,
                      keep_ratio=True)
        
        sprite.pos = (x, y)
        self.sprites[sprite_id] = sprite
        self.add_widget(sprite)
    
    def remove_sprite(self, sprite_id):
        """Elimina un sprite"""
        if sprite_id in self.sprites:
            self.remove_widget(self.sprites[sprite_id])
            del self.sprites[sprite_id]
    
    def clear_sprites(self):
        """Elimina todos los sprites"""
        for sprite in list(self.sprites.values()):
            self.remove_widget(sprite)
        self.sprites.clear()

class SaveLoadPopup(Popup):
    """Popup para guardar/cargar partidas"""
    
    def __init__(self, interpreter, mode='save', **kwargs):
        super().__init__(**kwargs)
        self.interpreter = interpreter
        self.mode = mode
        
        self.title = 'Guardar Partida' if mode == 'save' else 'Cargar Partida'
        self.size_hint = (0.9, 0.8)
        
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Área de slots
        scroll = ScrollView()
        self.slot_grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.slot_grid.bind(minimum_height=self.slot_grid.setter('height'))
        
        # Crear 10 slots
        for i in range(10):
            self.create_slot_button(i)
        
        scroll.add_widget(self.slot_grid)
        layout.add_widget(scroll)
        
        # Botón cerrar
        close_btn = Button(text='Cerrar', size_hint_y=None, height=50)
        close_btn.bind(on_press=self.dismiss)
        layout.add_widget(close_btn)
        
        self.content = layout
    
    def create_slot_button(self, slot_num):
        """Crea un botón de slot de guardado"""
        save_info = self.interpreter.get_save_info(slot_num)
        
        if save_info:
            text = f"Slot {slot_num + 1}: {save_info['date']}\n{save_info['text'][:50]}..."
        else:
            text = f"Slot {slot_num + 1}: [Vacío]"
        
        btn = Button(
            text=text,
            size_hint_y=None,
            height=80,
            halign='left',
            valign='middle'
        )
        btn.bind(size=btn.setter('text_size'))
        
        if self.mode == 'save':
            btn.bind(on_press=lambda x, s=slot_num: self.save_slot(s))
        else:
            if save_info:
                btn.bind(on_press=lambda x, s=slot_num: self.load_slot(s))
            else:
                btn.disabled = True
        
        self.slot_grid.add_widget(btn)
    
    def save_slot(self, slot_num):
        """Guarda en un slot"""
        self.interpreter.save_game(slot_num)
        self.dismiss()
    
    def load_slot(self, slot_num):
        """Carga desde un slot"""
        self.interpreter.load_game(slot_num)
        self.dismiss()

class ChoicePopup(Popup):
    """Popup para mostrar opciones de elección"""
    
    def __init__(self, choices, callback, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        
        self.title = 'Elige una opción'
        self.size_hint = (0.8, None)
        self.height = min(len(choices) * 80 + 100, Window.height * 0.7)
        
        layout = GridLayout(cols=1, spacing=10, padding=10, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        
        for i, choice in enumerate(choices):
            btn = Button(
                text=choice,
                size_hint_y=None,
                height=70
            )
            btn.bind(on_press=lambda x, idx=i: self.select_choice(idx))
            layout.add_widget(btn)
        
        self.content = layout
    
    def select_choice(self, index):
        """Selecciona una opción"""
        self.callback(index)
        self.dismiss()

class VNDSInterpreter(BoxLayout):
    """Intérprete principal VNDS"""
    
class VNDSInterpreter(BoxLayout):


    def __init__(self, novel_path, **kwargs):
        super().__init__(orientation='vertical', **kwargs)

        # 1️⃣ PRIMERO: guardar la ruta
        self.novel_path = novel_path

        # 2️⃣ rutas internas
        self.save_path = os.path.join(self.novel_path, "saves")
        os.makedirs(self.save_path, exist_ok=True)

        # 3️⃣ estado interno
        self.text_buffer = ""
        self.waiting_for_input = False
        self.pending_choices = []
        self.choice_labels = []
        self.variables = {}
        self.current_sound = None
        self.current_music = None

        # 4️⃣ UI
        self.create_ui()

        # 5️⃣ script (DESPUÉS de todo lo anterior)
        self.load_novel()


        

    
    def create_ui(self):
        """Crea la interfaz de usuario"""
        # Pantalla superior (imágenes y sprites)
        self.upper_screen = FloatLayout(size_hint=(1, 0.6))
        
        # Fondo
        self.background = Image(size_hint=(1, 1), allow_stretch=True)
        self.upper_screen.add_widget(self.background)
        
        # Capa de sprites
        self.sprite_layer = SpriteLayer(size_hint=(1, 1))
        self.upper_screen.add_widget(self.sprite_layer)
        
        # Pantalla inferior (texto y controles)
        self.lower_screen = BoxLayout(orientation='vertical', size_hint=(1, 0.4))
        
        # Barra de menú
        menu_bar = BoxLayout(size_hint=(1, None), height=40, spacing=5)
        
        save_btn = Button(text='💾 Guardar', size_hint_x=0.25)
        save_btn.bind(on_press=self.show_save_menu)
        
        load_btn = Button(text='📁 Cargar', size_hint_x=0.25)
        load_btn.bind(on_press=self.show_load_menu)
        
        auto_btn = Button(text='⏩ Auto', size_hint_x=0.25)
        auto_btn.bind(on_press=self.toggle_auto)
        
        skip_btn = Button(text='⏭ Skip', size_hint_x=0.25)
        skip_btn.bind(on_press=self.toggle_skip)
        
        menu_bar.add_widget(save_btn)
        menu_bar.add_widget(load_btn)
        menu_bar.add_widget(auto_btn)
        menu_bar.add_widget(skip_btn)
        
        # Área de texto
        self.text_area = Label(
            text='',
            size_hint=(1, 1),
            halign='left',
            valign='top',
            text_size=(Window.width - 40, None),
            markup=True,
            padding=(20, 20)
        )
        
        with self.lower_screen.canvas.before:
            Color(0.1, 0.1, 0.1, 0.9)
            self.lower_screen_rect = Rectangle(size=self.lower_screen.size, 
                                              pos=self.lower_screen.pos)
        
        self.lower_screen.bind(size=self._update_rect, pos=self._update_rect)
        self.lower_screen.add_widget(menu_bar)
        self.lower_screen.add_widget(self.text_area)
        
        # Botón para continuar
        self.continue_btn = Button(
            text='▼ Continuar',
            size_hint=(1, None),
            height=50,
            background_color=(0.2, 0.5, 0.8, 1)
        )
        self.continue_btn.bind(on_press=self.on_continue)
        self.lower_screen.add_widget(self.continue_btn)
        
        # Añadir pantallas
        self.add_widget(self.upper_screen)
        self.add_widget(self.lower_screen)
        
        # Estados de auto y skip
        self.auto_mode = False
        self.skip_mode = False
    
    def _update_rect(self, instance, value):
        """Actualiza el rectángulo de fondo"""
        self.lower_screen_rect.size = instance.size
        self.lower_screen_rect.pos = instance.pos
    
    def load_novel(self):
        """Carga la novela visual"""
        script_file = os.path.join(self.novel_path, 'script', 'main.scr')
        if os.path.exists(script_file):
            self.script = VNDSScript(
                os.path.join(self.novel_path, "script", "main.scr")
            )
            self.process_next_command()
        else:
            self.text_area.text = "Error: No se encontró main.scr"
    
    def process_next_command(self):
        """Procesa el siguiente comando del script"""
        if self.waiting_for_input and not self.skip_mode:
            return
        
        command = self.script.get_next_command()
        if command is None:
            self.text_area.text += "\n\n[color=00ff00][FIN DE LA NOVELA][/color]"
            self.waiting_for_input = True
            return
        
        self.execute_command(command)
    
    def execute_command(self, command):
        """Ejecuta un comando VNDS"""
        # Ignorar etiquetas
        if command.startswith('~'):
            self.process_next_command()
            return
        
        parts = command.split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        # Comandos de imagen
        if cmd == 'bgload':
            bg_path = os.path.join(self.novel_path, args)
            if os.path.exists(bg_path):
                self.background.source = bg_path
        
        elif cmd == 'setimg':
            parts = args.split()
            if len(parts) >= 4:
                sprite_id, img_file, x, y = parts[0], parts[1], int(parts[2]), int(parts[3])
                img_path = os.path.join(self.novel_path, img_file)
                if os.path.exists(img_path):
                    self.sprite_layer.add_sprite(sprite_id, img_path, x, y)
        
        elif cmd == 'removeimg':
            self.sprite_layer.remove_sprite(args)
        
        elif cmd == 'clearimg':
            self.sprite_layer.clear_sprites()
        
        # Comandos de texto
        elif cmd == 'cleartext':
            self.text_buffer = ""
            self.text_area.text = ""
        
        elif cmd == 'text':
            # Procesar variables en el texto
            processed_text = self.process_variables(args)
            self.text_buffer += processed_text + "\n"
            self.text_area.text = self.text_buffer
            self.waiting_for_input = True
            
            if self.auto_mode:
                Clock.schedule_once(lambda dt: self.on_continue(None), 2.0)
            return
        
        # Comandos de elección
        elif cmd == 'choice':
            self.pending_choices.append(args)
        
        elif cmd == 'goto':
            if self.pending_choices:
                # Último goto asociado a la última choice
                self.choice_labels.append(args)
        
        elif cmd == 'endchoice':
            if self.pending_choices:
                self.show_choices()
                return
        
        # Comandos de flujo
        elif cmd == 'jump':
            if self.script.jump_to_label(args):
                self.process_next_command()
                return
        
        elif cmd == 'delay':
            delay_ms = int(args)
            Clock.schedule_once(lambda dt: self.process_next_command(), delay_ms / 1000.0)
            return
        
        # Comandos de variables
        elif cmd == 'setvar':
            parts = args.split(maxsplit=1)
            if len(parts) == 2:
                var_name, value = parts
                try:
                    self.variables[var_name] = int(value)
                except ValueError:
                    self.variables[var_name] = value
        
        elif cmd == 'if':
            # Simplificado: if varname == value
            if not self.evaluate_condition(args):
                # Saltar hasta fi
                self.skip_until_fi()
        
        elif cmd == 'fi' or cmd == 'endif':
            pass
        
        # Comandos de audio
        elif cmd == 'sound':
            self.play_sound(args)
        
        elif cmd == 'music':
            self.play_music(args)
        
        elif cmd == 'stopsound':
            self.stop_sound()
        
        elif cmd == 'stopmusic':
            self.stop_music()
        
        # Comandos adicionales
        elif cmd == 'random':
            # random varname min max
            parts = args.split()
            if len(parts) == 3:
                import random
                var_name, min_val, max_val = parts[0], int(parts[1]), int(parts[2])
                self.variables[var_name] = random.randint(min_val, max_val)
        
        # Procesar siguiente comando automáticamente
        self.process_next_command()
    
    def show_choices(self):
        """Muestra el popup de elecciones"""
        def on_choice_selected(index):
            if index < len(self.choice_labels):
                label = self.choice_labels[index]
                self.script.jump_to_label(label)
            self.pending_choices = []
            self.choice_labels = []
            self.waiting_for_input = False
            self.process_next_command()
        
        ChoicePopup(self.pending_choices, on_choice_selected).open()
    
    def process_variables(self, text):
        """Procesa variables en el texto usando formato $varname"""
        for var_name, value in self.variables.items():
            text = text.replace(f'${var_name}', str(value))
        return text
    
    def evaluate_condition(self, condition):
        """Evalúa una condición simple"""
        # Formato: varname == value o varname > value, etc.
        for op in ['==', '!=', '>', '<', '>=', '<=']:
            if op in condition:
                parts = condition.split(op)
                if len(parts) == 2:
                    var_name = parts[0].strip()
                    value = parts[1].strip()
                    
                    var_val = self.variables.get(var_name, 0)
                    try:
                        value = int(value)
                    except ValueError:
                        pass
                    
                    if op == '==':
                        return var_val == value
                    elif op == '!=':
                        return var_val != value
                    elif op == '>':
                        return var_val > value
                    elif op == '<':
                        return var_val < value
                    elif op == '>=':
                        return var_val >= value
                    elif op == '<=':
                        return var_val <= value
        return True
    
    def skip_until_fi(self):
        """Salta comandos hasta encontrar fi"""
        depth = 1
        while depth > 0:
            cmd = self.script.get_next_command()
            if cmd:
                cmd_name = cmd.split()[0].lower()
                if cmd_name == 'if':
                    depth += 1
                elif cmd_name in ['fi', 'endif']:
                    depth -= 1
            else:
                break
    
    def play_sound(self, sound_file):
        """Reproduce un efecto de sonido"""
        sound_path = os.path.join(self.novel_path, 'sound', sound_file)
        if os.path.exists(sound_path):
            self.current_sound = SoundLoader.load(sound_path)
            if self.current_sound:
                self.current_sound.play()
    
    def play_music(self, music_file):
        """Reproduce música de fondo"""
        music_path = os.path.join(self.novel_path, 'sound', music_file)
        if os.path.exists(music_path):
            if self.current_music:
                self.current_music.stop()
            self.current_music = SoundLoader.load(music_path)
            if self.current_music:
                self.current_music.loop = True
                self.current_music.play()
    
    def stop_sound(self):
        """Detiene el sonido actual"""
        if self.current_sound:
            self.current_sound.stop()
    
    def stop_music(self):
        """Detiene la música actual"""
        if self.current_music:
            self.current_music.stop()
    
    def on_continue(self, instance):
        """Maneja el click en continuar"""
        if self.waiting_for_input:
            self.waiting_for_input = False
            self.process_next_command()
    
    def toggle_auto(self, instance):
        """Activa/desactiva modo automático"""
        self.auto_mode = not self.auto_mode
        instance.text = '⏸ Auto' if self.auto_mode else '⏩ Auto'
    
    def toggle_skip(self, instance):
        """Activa/desactiva modo skip"""
        self.skip_mode = not self.skip_mode
        instance.text = '⏸ Skip' if self.skip_mode else '⏭ Skip'
        
        if self.skip_mode and self.waiting_for_input:
            self.on_continue(None)
    
    def show_save_menu(self, instance):
        """Muestra el menú de guardado"""
        SaveLoadPopup(self, mode='save').open()
    
    def show_load_menu(self, instance):
        """Muestra el menú de carga"""
        SaveLoadPopup(self, mode='load').open()
    
    def save_game(self, slot_num):
        """Guarda el estado del juego"""
        save_data = {
            'script_line': self.script.current_line,
            'text_buffer': self.text_buffer,
            'variables': self.variables,
            'background': self.background.source,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'text': self.text_buffer[-100:] if self.text_buffer else "Guardado nuevo"
        }
        
        save_file = os.path.join(self.save_path, f'save_{slot_num}.json')
        with open(save_file, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        # Mostrar confirmación
        popup = Popup(
            title='Guardado',
            content=Label(text=f'Partida guardada en Slot {slot_num + 1}'),
            size_hint=(0.6, 0.3)
        )
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 1.5)
    
    def load_game(self, slot_num):
        """Carga el estado del juego"""
        save_file = os.path.join(self.save_path, f'save_{slot_num}.json')
        
        if os.path.exists(save_file):
            with open(save_file, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            self.script.current_line = save_data['script_line']
            self.text_buffer = save_data['text_buffer']
            self.variables = save_data['variables']
            self.text_area.text = self.text_buffer
            
            if save_data['background']:
                self.background.source = save_data['background']
            
            self.waiting_for_input = False
            
            # Mostrar confirmación
            popup = Popup(
                title='Cargado',
                content=Label(text=f'Partida cargada desde Slot {slot_num + 1}'),
                size_hint=(0.6, 0.3)
            )
            popup.open()
            Clock.schedule_once(lambda dt: popup.dismiss(), 1.5)
    
    def get_save_info(self, slot_num):
        """Obtiene información de un guardado"""
        save_file = os.path.join(self.save_path, f'save_{slot_num}.json')
        
        if os.path.exists(save_file):
            with open(save_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

