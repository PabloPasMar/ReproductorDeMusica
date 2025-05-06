import tkinter as tk
from tkinter import filedialog, simpledialog, ttk
import pygame
import os
import threading
import time

class NodoCancion:
    def __init__(self, nombre, artista, duracion, ruta):
        self.nombre = nombre
        self.artista = artista
        self.duracion = duracion
        self.ruta = ruta
        self.siguiente = None
        self.anterior = None

class ListaReproduccion:
    def __init__(self):
        self.actual = None

    def agregar_cancion(self, nodo):
        if not self.actual:
            self.actual = nodo
            nodo.siguiente = nodo.anterior = nodo
        else:
            ultimo = self.actual.anterior
            ultimo.siguiente = nodo
            nodo.anterior = ultimo
            nodo.siguiente = self.actual
            self.actual.anterior = nodo

    def eliminar_cancion(self, nombre):
        if not self.actual:
            return False
        temp = self.actual
        while True:
            if temp.nombre == nombre:
                if temp.siguiente == temp:
                    self.actual = None
                else:
                    temp.anterior.siguiente = temp.siguiente
                    temp.siguiente.anterior = temp.anterior
                    if temp == self.actual:
                        self.actual = temp.siguiente
                return True
            temp = temp.siguiente
            if temp == self.actual:
                break
        return False

    def avanzar(self):
        if self.actual:
            self.actual = self.actual.siguiente

    def retroceder(self):
        if self.actual:
            self.actual = self.actual.anterior

    def mostrar_lista(self):
        canciones = []
        if not self.actual:
            return canciones
        temp = self.actual
        while True:
            canciones.append(f"{temp.nombre} - {temp.artista}")
            temp = temp.siguiente
            if temp == self.actual:
                break
        return canciones

class ReproductorMusica:
    def __init__(self, root):
        self.lista_reproduccion = ListaReproduccion()
        self.reproduciendo = False
        self.indice_cancion_actual = -1
        self.duracion_total = 0
        self.tiempo_actual = 0
        pygame.mixer.init()
        self.root = root
        self.root.title("Reproductor de Música")
        self.root.geometry("400x500")
        self.frame_titulo = tk.Frame(root)
        self.frame_titulo.pack(pady=5, fill=tk.X)    
        self.label_reproduciendo = tk.Label(self.frame_titulo, text="No hay canción reproduciéndose")
        self.label_reproduciendo.pack(pady=5)       
        self.barra_progreso = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=300, mode='determinate')
        self.barra_progreso.pack(pady=5)       
        self.tiempo_label = tk.Label(root, text="0:00 / 0:00")
        self.tiempo_label.pack(pady=5)
        self.lista_canciones = tk.Listbox(root, width=60, selectbackground="blue", selectforeground="white")
        self.lista_canciones.pack(pady=10)
        self.boton_cargar = tk.Button(root, text="Cargar Canción", command=self.cargar_cancion)
        self.boton_cargar.pack()
        self.boton_reproducir = tk.Button(root, text="Reproducir", command=self.reproducir)
        self.boton_reproducir.pack()
        self.boton_pausar = tk.Button(root, text="Pausar / Reanudar", command=self.pausar)
        self.boton_pausar.pack()
        self.boton_detener = tk.Button(root, text="Detener", command=self.detener)
        self.boton_detener.pack()
        self.boton_siguiente = tk.Button(root, text="Siguiente", command=self.siguiente)
        self.boton_siguiente.pack()
        self.boton_anterior = tk.Button(root, text="Anterior", command=self.anterior)
        self.boton_anterior.pack()

    def cargar_cancion(self):
        ruta = filedialog.askopenfilename(filetypes=[("Archivos MP3", "*.mp3")])
        if ruta:
            nombre = os.path.basename(ruta)
            artista = simpledialog.askstring("Información", "Ingrese el nombre del artista", parent=self.root)
            if not artista:
                artista = "Desconocido"
            nodo = NodoCancion(nombre, artista, "Desconocida", ruta)
            self.lista_reproduccion.agregar_cancion(nodo)
            self.actualizar_lista()

    def actualizar_lista(self):
        self.lista_canciones.delete(0, tk.END)
        canciones = self.lista_reproduccion.mostrar_lista()
        for i, cancion in enumerate(canciones):
            self.lista_canciones.insert(tk.END, cancion)
        if self.lista_reproduccion.actual:
            if self.indice_cancion_actual == -1:
                self.indice_cancion_actual = 0
            self.lista_canciones.select_set(self.indice_cancion_actual)
            self.lista_canciones.activate(self.indice_cancion_actual)
            self.lista_canciones.see(self.indice_cancion_actual)

    def reproducir(self):
        if self.lista_reproduccion.actual:
            ruta = self.lista_reproduccion.actual.ruta
            if not self.reproduciendo:
                pygame.mixer.music.load(ruta)
                pygame.mixer.music.play()
                self.reproduciendo = True
                cancion_actual = f"Reproduciendo: {self.lista_reproduccion.actual.nombre} - {self.lista_reproduccion.actual.artista}"
                self.label_reproduciendo.config(text=cancion_actual)
                self.duracion_total = pygame.mixer.Sound(ruta).get_length()
                self.barra_progreso["maximum"] = self.duracion_total
                self.tiempo_actual = 0
                threading.Thread(target=self.actualizar_progreso, daemon=True).start()      
                self.actualizar_lista()

    def pausar(self):
        if self.reproduciendo:
            pygame.mixer.music.pause()
            self.reproduciendo = False
            self.label_reproduciendo.config(text="Pausado: " + self.label_reproduciendo.cget("text")[13:])
        else:
            pygame.mixer.music.unpause()
            self.reproduciendo = True
            self.label_reproduciendo.config(text="Reproduciendo: " + self.label_reproduciendo.cget("text")[9:])
            threading.Thread(target=self.actualizar_progreso, daemon=True).start()

    def detener(self):
        pygame.mixer.music.stop()
        self.reproduciendo = False
        self.label_reproduciendo.config(text="No hay canción reproduciéndose")
        self.barra_progreso["value"] = 0
        self.tiempo_label.config(text="0:00 / 0:00")

    def siguiente(self):
        self.detener()
        self.lista_reproduccion.avanzar()
        self.indice_cancion_actual = (self.indice_cancion_actual + 1) % len(self.lista_reproduccion.mostrar_lista()) if self.lista_reproduccion.mostrar_lista() else 0
        self.reproducir()

    def anterior(self):
        self.detener()
        self.lista_reproduccion.retroceder()
        total_canciones = len(self.lista_reproduccion.mostrar_lista())
        if total_canciones > 0:
            self.indice_cancion_actual = (self.indice_cancion_actual - 1) % total_canciones
        self.reproducir()
        
    def actualizar_progreso(self):
        while self.reproduciendo and pygame.mixer.music.get_busy():
            self.tiempo_actual = min(self.tiempo_actual + 0.1, self.duracion_total)
            self.barra_progreso["value"] = self.tiempo_actual
            tiempo_actual_str = self.formatear_tiempo(self.tiempo_actual)
            tiempo_total_str = self.formatear_tiempo(self.duracion_total)
            self.tiempo_label.config(text=f"{tiempo_actual_str} / {tiempo_total_str}")
            time.sleep(0.1)
        if not pygame.mixer.music.get_busy() and self.reproduciendo:
            self.siguiente()
            
    def formatear_tiempo(self, segundos):
        minutos = int(segundos // 60)
        segundos = int(segundos % 60)
        return f"{minutos}:{segundos:02d}"

class Main:
    root = tk.Tk()
    app = ReproductorMusica(root)
    root.mainloop()