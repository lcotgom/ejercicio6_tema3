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

        # canvas a la izquierda, panel de controles a la derecha
        self.canvas = tk.Canvas(root, width=CANVAS_W, height=CANVAS_H, bg="lightblue", bd=2, relief='sunken')
        self.canvas.pack(side='left', fill='both', expand=True)

        # Bind click events on canvas for selection and claxon (right-click)
        self.canvas.bind('<Button-1>', self.canvas_left_click)
        self.canvas.bind('<Button-3>', self.canvas_right_click)

        self.camiones = []
        self.camion_activo = None

        # Panel lateral de control (derecha)
        controls = tk.Frame(root, width=260, padx=8, pady=8, bg="#f5f5f5")
        controls.pack(side='right', fill='y')

        # Toolbar (arriba del panel lateral)
        toolbar = tk.Frame(controls, bg="#f5f5f5")
        toolbar.pack(anchor='n', fill='x')

        self.combo = ttk.Combobox(toolbar, state="readonly", width=18)
        self.combo.pack(side="left", padx=4, pady=4)
        self.combo.bind("<<ComboboxSelected>>", self.seleccionar_camion)

        ttk.Button(toolbar, text="Nuevo", command=self.nuevo_camion).pack(side="left", padx=2)
        ttk.Button(toolbar, text="Caja", command=self.nueva_caja).pack(side="left", padx=2)
        ttk.Button(toolbar, text="Claxon", command=self.audio.claxon).pack(side="left", padx=2)
        ttk.Button(toolbar, text="Info", command=self.mostrar_info).pack(side="left", padx=2)

        # Información detallada del camión activo
        info_frame = tk.LabelFrame(controls, text="Camión activo", padx=6, pady=6, bg="#f5f5f5")
        info_frame.pack(fill='x', pady=(8,4))

        self.matricula_var = tk.StringVar(value="-")
        tk.Label(info_frame, text="Matrícula:", anchor='w', bg="#f5f5f5").grid(row=0, column=0, sticky='w')
        tk.Label(info_frame, textvariable=self.matricula_var, anchor='w', bg="#f5f5f5").grid(row=0, column=1, sticky='w')

        self.conductor_var = tk.StringVar(value="-")
        tk.Label(info_frame, text="Conductor:", anchor='w', bg="#f5f5f5").grid(row=1, column=0, sticky='w')
        tk.Label(info_frame, textvariable=self.conductor_var, anchor='w', bg="#f5f5f5").grid(row=1, column=1, sticky='w')

        self.capacidad_var = tk.StringVar(value="-")
        tk.Label(info_frame, text="Capacidad (kg):", anchor='w', bg="#f5f5f5").grid(row=2, column=0, sticky='w')
        tk.Label(info_frame, textvariable=self.capacidad_var, anchor='w', bg="#f5f5f5").grid(row=2, column=1, sticky='w')

        self.peso_var = tk.StringVar(value="0.0")
        tk.Label(info_frame, text="Peso total (kg):", anchor='w', bg="#f5f5f5").grid(row=3, column=0, sticky='w')
        tk.Label(info_frame, textvariable=self.peso_var, anchor='w', bg="#f5f5f5").grid(row=3, column=1, sticky='w')

        # Controles para velocidad y rumbo del camión activo
        ctrl_frame = tk.LabelFrame(controls, text="Controles", padx=6, pady=6, bg="#f5f5f5")
        ctrl_frame.pack(fill='x', pady=(6,4))

        tk.Label(ctrl_frame, text="Velocidad:", bg="#f5f5f5").grid(row=0, column=0, sticky='w')
        self.vel_var = tk.DoubleVar(value=0.0)
        self.vel_spin = tk.Spinbox(ctrl_frame, from_=0, to=180, textvariable=self.vel_var, width=6, command=self.on_speed_change)
        self.vel_spin.grid(row=0, column=1, sticky='w', padx=4)

        tk.Label(ctrl_frame, text="Rumbo:", bg="#f5f5f5").grid(row=1, column=0, sticky='w')
        self.rumbo_var = tk.IntVar(value=1)
        self.rumbo_spin = tk.Spinbox(ctrl_frame, from_=1, to=359, textvariable=self.rumbo_var, width=6, command=self.on_rumbo_change)
        self.rumbo_spin.grid(row=1, column=1, sticky='w', padx=4)

        # trace vars for manual edits (typing)
        try:
            self.vel_var.trace_add('write', lambda *_: self.on_speed_change())
            self.rumbo_var.trace_add('write', lambda *_: self.on_rumbo_change())
        except Exception:
            # older tkinter may use trace
            self.vel_var.trace('w', lambda *_: self.on_speed_change())
            self.rumbo_var.trace('w', lambda *_: self.on_rumbo_change())

        # Lista de cajas del camión
        cajas_frame = tk.LabelFrame(controls, text="Cajas", padx=6, pady=6, bg="#f5f5f5")
        cajas_frame.pack(fill='both', expand=True, pady=(6,4))
        self.cajas_list = tk.Listbox(cajas_frame, height=8)
        self.cajas_list.pack(fill='both', expand=True)

        # barra de estado
        self.status = tk.Label(root, text="Listo", bd=1, relief='sunken', anchor='w')
        self.status.pack(side='bottom', fill='x')

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
        # actualizar controles e interfaz
        self.update_controls()
        self.refresh_cajas_list()
        self.status.config(text=f"Camión {c.matricula} creado")

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
        self.refresh_cajas_list()
        self.peso_var.set(f"{self.camion_activo.peso_total():.1f}")
        self.status.config(text=f"Añadida caja {codigo} a {self.camion_activo.matricula}")

    def seleccionar_camion(self, event=None):
        idx = self.combo.current()
        if idx >= 0:
            self.camion_activo = self.camiones[idx]
            self.update_controls()
            self.refresh_cajas_list()
            self.status.config(text=f"Camión {self.camion_activo.matricula} seleccionado")

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
        self.status.config(text=f"Info mostrada de {c.matricula}")

    def refresh_cajas_list(self):
        self.cajas_list.delete(0, 'end')
        if not self.camion_activo:
            return
        for ca in self.camion_activo.cajas:
            self.cajas_list.insert('end', f"{ca.codigo} - {ca.peso_kg}kg")

    def animar(self):
        now = time.time()
        dt = now - self.last_time
        self.last_time = now

        self.canvas.delete("all")
        for idx, c in enumerate(self.camiones):
            c.mover(dt)
            self.dibujar_camion(idx, c)

        self.root.after(int(1000/FPS), self.animar)

    def dibujar_camion(self, idx, c):
        # Dibujar un rectángulo representando el camión
        w, h = 60, 30
        x1, y1 = c.x - w/2, c.y - h/2
        x2, y2 = c.x + w/2, c.y + h/2
        # cuerpo (resaltado si es el activo)
        tag = f"cam_{idx}"
        fill = "orange" if (self.camion_activo is c) else "yellow"
        outline = "red" if (self.camion_activo is c) else "black"
        width = 3 if (self.camion_activo is c) else 1
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline=outline, width=width, tags=(tag,))
        # matrícula
        self.canvas.create_text(c.x, c.y - 4, text=c.matricula, font=("Arial", 10, "bold"), tags=(tag,))
        # información adicional (nº cajas)
        self.canvas.create_text(c.x, c.y + h/2 + 6, text=f"{len(c.cajas)} cajas", font=("Arial", 8), tags=(tag,))

    def canvas_left_click(self, event):
        # seleccionar camión bajo el cursor si existe
        items = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
        for it in items:
            tags = self.canvas.gettags(it)
            for t in tags:
                if t.startswith('cam_'):
                    try:
                        idx = int(t.split('_')[1])
                        if 0 <= idx < len(self.camiones):
                            self.combo.current(idx)
                            self.camion_activo = self.camiones[idx]
                            self.update_controls()
                            return
                    except:
                        pass

    def canvas_right_click(self, event):
        # tocar claxon del camión bajo el cursor
        items = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
        for it in items:
            tags = self.canvas.gettags(it)
            for t in tags:
                if t.startswith('cam_'):
                    try:
                        idx = int(t.split('_')[1])
                        if 0 <= idx < len(self.camiones):
                            self.camion_activo = self.camiones[idx]
                            self.update_controls()
                            self.audio.claxon()
                            return
                    except:
                        pass

    def update_controls(self):
        # actualizar widgets con valores del camión activo
        if not self.camion_activo:
            return
        try:
            self.vel_var.set(self.camion_activo.velocidad)
            self.rumbo_var.set(self.camion_activo.rumbo)
        except Exception:
            pass

    def on_speed_change(self):
        if not self.camion_activo:
            return
        try:
            v = float(self.vel_var.get())
            self.camion_activo.setVelocidad(v)
        except Exception:
            pass

    def on_rumbo_change(self):
        if not self.camion_activo:
            return
        try:
            r = int(self.rumbo_var.get())
            self.camion_activo.setRumbo(r)
        except Exception:
            pass

    def on_close(self):
        # limpiar audio y salir
        try:
            self.audio.shutdown()
        finally:
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = CamionesApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
