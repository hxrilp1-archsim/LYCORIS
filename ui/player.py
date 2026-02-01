#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pantalla del reproductor VNDS (modo simple)
Muestra fondo + texto leyendo scripts VNDS
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
import os
import re


class PlayerScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.novel_path = None

        root = FloatLayout()

        # Fondo
        self.bg = Image(
            allow_stretch=True,
            keep_ratio=False
        )
        root.add_widget(self.bg)

        # Texto
        self.text = Label(
            text="",
            size_hint=(1, 0.25),
            pos_hint={"x": 0, "y": 0},
            halign="left",
            valign="top"
        )
        self.text.bind(size=self.text.setter("text_size"))
        root.add_widget(self.text)

        self.add_widget(root)

    # ===============================
    # CARGA DE NOVELA
    # ===============================

    def load_novel(self, novel_path):
        self.novel_path = novel_path

        print("🎮 PlayerScreen: Cargando novela desde")
        print("   ", novel_path)

        if not os.path.exists(novel_path):
            print("❌ La ruta no existe")
            return

        self.run_script()

    # ===============================
    # EJECUCIÓN SIMPLE DE SCRIPT
    # ===============================

    def run_script(self):
        script_dir = os.path.join(self.novel_path, "script")
        bg_dir = os.path.join(self.novel_path, "background")

        if not os.path.exists(script_dir):
            print("❌ No existe carpeta script/")
            return

        scripts = sorted(f for f in os.listdir(script_dir) if f.endswith(".scr"))

        if not scripts:
            print("❌ No hay archivos .scr")
            return

        script_path = os.path.join(script_dir, scripts[0])
        print("📜 Ejecutando:", script_path)

        with open(script_path, encoding="shift-jis", errors="ignore") as f:
            for line in f:
                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                # bgload bg_name
                if line.startswith("bgload"):
                    parts = line.split()
                    if len(parts) >= 2:
                        self.load_bg(bg_dir, parts[1])

                # msg "texto"
                elif line.startswith("msg"):
                    text = re.findall(r'"(.*?)"', line)
                    if text:
                        self.text.text = text[0]
                        break  # mostramos solo una línea por ahora

    # ===============================
    # CARGA DE FONDO
    # ===============================

    def load_bg(self, bg_dir, name):
        for ext in (".jpg", ".png"):
            path = os.path.join(bg_dir, name + ext)
            if os.path.exists(path):
                self.bg.source = path
                print("🖼 Fondo cargado:", path)
                return

        print("❌ Fondo no encontrado:", name)
