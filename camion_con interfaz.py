#!/usr/bin/env python3
"""
camiones_app.py
Simulador gráfico de camiones con Tkinter + pygame para claxon.
"""

import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import math
import time
import os

# Intento de cargar pygame para el sonido
try:
    import pygame as pg
    PYGAME_AVAILABLE = True
except:
    PYGAME_AVAILABLE = False

CANVAS_W = 900
CANVAS_H = 600
FPS = 60

# ---------------------------
# AUDIO
# ---------------------------

AUDIO_CLAXON = "claxon"
AUDIO_EXTS = [".mp3", ".wav", ".ogg"]

def find_audio_file(base):
    """Busca automáticamente claxon.mp3, claxon.wav, claxon.ogg."""
    if os.path.isfile(base):
        return base
    for ext in AUDIO_EXTS:
        if os.path.isfile(base + ext):
            return base + ext
    return None

class AudioManager:
    def __init__(self):
        self.enabled = False
        self.claxon_path = find_audio_file(AUDIO_CLAXON)
        self.claxon_sound = None

        if not PYGAME_AVAILABLE:
            print("pygame no disponible: sin sonido.")
            return

        try:
            pg.mixer.init()
            self.enabled = True

            if self.claxon_path:
                try:
                    self.claxon_sound = pg.mixer.Sound(self.claxon_path)
                except:
                    print("Error cargando sonido claxon.")

        except Exception as e:
            print("Error inicializando pygame:", e)
            self.enabled = False

    def claxon(self):
        if self.enabled and self.claxon_sound:
            try:
                self.claxon_sound.play()
            except:
                pass

    def shutdown(self):
        if not self.enabled:
            return
        try:
            pg.mixer.quit()
        except:
            pass

# ---------------------------
# CLASES
# ---------------------------

class Caja:
    def __init__(self, codigo, peso_kg, descripcion_carga, largo, ancho, altura):
        self.codigo = codigo
        self.peso_kg = float(peso_kg)
        self.descripcion_carga = descripcion_carga
        self.largo = float(largo)
        self.ancho = float(ancho)
        self.altura = float(altura)

    def __str__(self):
        return (f"Caja {self.codigo} | Peso: {self.peso_kg} kg\n"
                f"Desc: {self.descripcion_carga}\n"
                f"Dim: {self.largo}x{self.ancho}x{self.altura}\n")

class Camion:
    def __init__(self, matricula, conductor, capacidad_kg, descripcion_carga, rumbo, velocidad, x, y):
        self.matricula = matricula
        self.conductor = conductor
        self.capacidad_kg = float(capacidad_kg)
        self.descripcion_carga = descripcion_carga
        self.rumbo = int(rumbo)
        self.velocidad = float(velocidad)
        self.x = float(x)
        self.y = float(y)
        self.cajas = []

    def peso_total(self):
        return sum(c.peso_kg for c in self.cajas)

    def add_caja(self, caja):
        if self.peso_total() + caja.peso_kg <= self.capacidad_kg:
            self.cajas.append(caja)
        else:
            messagebox.showwarning("Capacidad superada",
                                   "No se puede añadir la caja: supera la capacidad máxima.")

    def setVelocidad(self, v):
        v = float(v)
        if v < 0 or v > 180:
            raise ValueError("Velocidad fuera de rango (0..180)")
        self.velocidad = v

    def setRumbo(self, r):
        r = int(r)
        if r < 1 or r > 359:
            raise ValueError("Rumbo fuera de 1..359")
        self.rumbo = r

    def mover(self, dt):
        rad = math.radians(self.rumbo)
        self.x += math.cos(rad) * self.velocidad * dt
        self.y += math.sin(rad) * self.velocidad * dt

        # Teletransporte a los bordes
        if self.x < 0: self.x += CANVAS_W
        if self.x > CANVAS_W: self.x -= CANVAS_W
        if self.y < 0: self.y += CANVAS_H
        if self.y > CANVAS_H: self.y -= CANVAS_H

# ---------------------------
# APP PRINCIPAL
# ---------------------------

class CamionesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Camiones 🚚")
        self.audio = AudioManager()

        self.canvas = tk.Canvas(root, width=CANVAS_W, height=CANVAS_H, bg="lightblue")
        self.canvas.pack()

        self.camiones = []
        self.camion_activo = None

        # Panel de control
        frame = tk.Frame(root)
        frame.pack(fill="x")

        self.combo = ttk.Combobox(frame, state="readonly")
        self.combo.pack(side="left", padx=5)
        self.combo.bind("<<ComboboxSelected>>", self.seleccionar_camion)

        tk.Button(frame, text="Nuevo Camión", command=self.nuevo_camion).pack(side="left", padx=5)
        tk.Button(frame, text="Añadir Caja", command=self.nueva_caja).pack(side="left", padx=5)
        tk.Button(frame, text="Claxon", command=self.audio.claxon).pack(side="left", padx=5)
        tk.Button(frame, text="Info", command=self.mostrar_info).pack(side="left", padx=5)

        self.last_time = time.time()
        self.animar()

    def nuevo_camion(self):
        matricula = simpledialog.askstring("Nuevo Camión", "Matrícula:")
        if not matricula: return
        conductor = simpledialog.askstring("Nuevo Camión", "Conductor:")
        capacidad = simpledialog.askfloat("Nuevo Camión", "Capacidad máxima (kg):", minvalue=100)
        rumbo = simpledialog.askinteger("Nuevo Camión", "Rumbo (1..359):", minvalue=1, maxvalue=359)
        velocidad = simpledialog.askfloat("Nuevo Camión", "Velocidad (0..180):", minvalue=0, maxvalue=180)

        c = Camion(matricula, conductor, capacidad, "General", rumbo, velocidad,
                   CANVAS_W/2, CANVAS_H/2)
        self.camiones.append(c)
        self.combo["values"] = [cam.matricula for cam in self.camiones]
        self.combo.current(len(self.camiones)-1)
        self.camion_activo = c

    def nueva_caja(self):
        if not self.camion_activo:
            messagebox.showinfo("Aviso", "Primero crea un camión.")
            return
        codigo = simpledialog.askstring("Nueva Caja", "Código:")
        peso = simpledialog.askfloat("Nueva Caja", "Peso (kg):")
        desc = simpledialog.askstring("Nueva Caja", "Descripción:")
        largo = simpledialog.askfloat("Nueva Caja", "Largo:")
        ancho = simpledialog.askfloat("Nueva Caja", "Ancho:")
        altura = simpledialog.askfloat("Nueva Caja", "Altura:")
        caja = Caja(codigo, peso, desc, largo, ancho, altura)
        self.camion_activo.add_caja(caja)

    def seleccionar_camion(self, event=None):
        idx = self.combo.current()
        if idx >= 0:
            self.camion_activo = self.camiones[idx]

    def mostrar_info(self):
        if not self.camion_activo:
            messagebox.showinfo("Info", "No hay camión activo.")
            return
        c = self.camion_activo
        info = (f"Camión {c.matricula}\nConductor: {c.conductor}\n"
                f"Capacidad: {c.capacidad_kg} kg\n"
                f"Velocidad: {c.velocidad}\nRumbo: {c.rumbo}\n"
                f"Posición: ({c.x:.1f}, {c.y:.1f})\n"
                f"Cajas: {len(c.cajas)}\nPeso total: {c.peso_total()} kg")
        messagebox.showinfo("Información", info)

    def animar(self):
        now = time.time()
        dt = now - self.last_time
        self.last_time = now

        self.canvas.delete("all")
        for c in self.camiones:
            c.mover(dt)
            self.dibujar_camion(c)

        self.root.after(int(1000/FPS), self.animar)

    def dibujar_camion(self, c):
        # Dibujar un rectángulo representando el camión
        w, h = 60, 30
        x1, y1 = c.x - w/2, c.y - h/2
        x2, y2 = c.x + w/2, c.y + h/2
        self.canvas