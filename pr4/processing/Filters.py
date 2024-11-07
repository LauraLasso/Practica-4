import numpy as np
from scipy.fft import fft, fftfreq
from scipy.signal import butter, lfilter
import matplotlib.pyplot as plt
from scipy.io.wavfile import read, write
import tkinter as tk
from tkinter import filedialog, ttk
import time
import vlc

senal_filtrada = None

def butter_filter(data, cutoff, fs, btype='low', order=5):
    if isinstance(cutoff, list):
        if len(cutoff) != 2 or any(c <= 0 for c in cutoff):
            raise ValueError("Para filtros de pasa-banda y rechazo de banda, se necesita una lista de dos frecuencias de corte positivas.")
        low, high = cutoff
        nyq = 0.5 * fs
        normal_cutoff = [low / nyq, high / nyq]
    else:
        if cutoff <= 0:
            raise ValueError("La frecuencia de corte debe ser mayor que 0")
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq

    b, a = butter(order, normal_cutoff, btype=btype, analog=False)  # Calcula los coeficientes a y b
    y = lfilter(b, a, data)  # Aplica el filtro
    return y


def crear_imagen_de_senal(t, senal_original, senal_filtrada, fs):
    plt.figure(figsize=(10, 5))

    plt.subplot(2, 2, 1)
    plt.plot(t, senal_original, label='Señal Original')
    plt.plot(t, senal_filtrada, label='Señal Filtrada', linestyle='--')
    plt.title('Dominio del Tiempo')
    plt.xlabel('Tiempo [s]')
    plt.ylabel('Amplitud')
    plt.legend()
    plt.grid()

    N = len(t)
    yf_original = fft(senal_original)
    yf_filtrada = fft(senal_filtrada)
    freqs = fftfreq(N, 1/fs)

    plt.subplot(2, 2, 2)
    plt.plot(freqs[:N//2], np.abs(yf_original[:N//2]), label='Original')
    plt.plot(freqs[:N//2], np.abs(yf_filtrada[:N//2]), label='Filtrada', linestyle='--')
    plt.title('Dominio de la Frecuencia')
    plt.xlabel('Frecuencia [Hz]')
    plt.ylabel('Magnitud')
    plt.legend()
    plt.grid()
    plt.xlim(0, 2000)

    plt.tight_layout()
    plt.savefig('processing/resources/senal.png')
    plt.close()


def guardar_y_reproducir(senal, fs, nombre_archivo):
    write(nombre_archivo, fs, senal)

    player = vlc.MediaPlayer(nombre_archivo)
    player.play()


class FiltroDeSenales:
    def __init__(self, t, senal_original, fs):
        self.t = t
        self.senal_original = senal_original
        self.fs = fs
        self.senal_filtrada = None

        self.ventana_filtro = tk.Toplevel()
        self.ventana_filtro.title("Filtro de Señales")

        self.frame_filtros = tk.Frame(self.ventana_filtro)
        self.frame_filtros.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.frame_graficas = tk.Frame(self.ventana_filtro)
        self.frame_graficas.pack(side=tk.RIGHT, padx=10, pady=10)

        self.tipo_filtro = tk.StringVar(value="Pasa-bajo")
        self.umbral = tk.DoubleVar(value=1.0)
        self.umbral_alto = tk.DoubleVar(value=1.0)
        self.umbral_bajo = tk.DoubleVar(value=1.0)

        self._crear_interfaz()

    def _crear_interfaz(self):
        tk.Label(self.frame_filtros, text="Tipo de Filtro:").pack()
        tk.OptionMenu(self.frame_filtros, self.tipo_filtro, "Pasa-bajo", "Pasa-alto", "Pasa-banda", "Rechaza-banda",
                      command=lambda _: self.update_umbral_visibility()).pack()

        self.umbral_label = tk.Label(self.frame_filtros, text="Umbral:")
        self.umbral_slider = tk.Scale(self.frame_filtros, variable=self.umbral, from_=1, to=99, orient=tk.HORIZONTAL)

        self.umbral_alto_label = tk.Label(self.frame_filtros, text="Umbral Alto:")
        self.umbral_alto_slider = tk.Scale(self.frame_filtros, variable=self.umbral_alto, from_=1, to=99, orient=tk.HORIZONTAL)

        self.umbral_bajo_label = tk.Label(self.frame_filtros, text="Umbral Bajo:")
        self.umbral_bajo_slider = tk.Scale(self.frame_filtros, variable=self.umbral_bajo, from_=1, to=99, orient=tk.HORIZONTAL)

        tk.Button(self.frame_filtros, text="Aplicar Filtro", command=self.aplicar_filtro).pack(pady=10)
        tk.Button(self.frame_filtros, text="Reproducir Señal Filtrada", command=lambda: guardar_y_reproducir(self.senal_filtrada, self.fs, "senal_filtrada.wav")).pack()
        tk.Button(self.frame_filtros, text="Reproducir Señal Original", command=lambda: guardar_y_reproducir(self.senal_original, self.fs, "senal_original.wav")).pack()

        self.label_imagen = tk.Label(self.frame_graficas)
        self.label_imagen.pack()

        self.update_umbral_visibility()
        self.aplicar_filtro()

    def update_umbral_visibility(self):
        filtro = self.tipo_filtro.get()
        self.umbral_label.pack_forget()
        self.umbral_slider.pack_forget()
        self.umbral_alto_label.pack_forget()
        self.umbral_alto_slider.pack_forget()
        self.umbral_bajo_label.pack_forget()
        self.umbral_bajo_slider.pack_forget()

        if filtro in ["Pasa-bajo", "Pasa-alto"]:
            self.umbral_label.pack()
            self.umbral_slider.pack()
        elif filtro == "Pasa-banda":
            self.umbral_alto_label.pack()
            self.umbral_alto_slider.pack()
            self.umbral_bajo_label.pack()
            self.umbral_bajo_slider.pack()
        elif filtro == "Rechaza-banda":
            self.umbral_alto_label.pack()
            self.umbral_alto_slider.pack()
            self.umbral_bajo_label.pack()
            self.umbral_bajo_slider.pack()

        self.aplicar_filtro()

    def aplicar_filtro(self):
        umbral_valor = self.umbral.get() / 100.0 * (self.fs / 2) if self.tipo_filtro.get() in ["Pasa-bajo", "Pasa-alto"] else None
        umbral_alto_valor = self.umbral_alto.get() / 100.0 * (self.fs / 2)
        umbral_bajo_valor = self.umbral_bajo.get() / 100.0 * (self.fs / 2)

        if self.tipo_filtro.get() == "Pasa-bajo":
            self.senal_filtrada = butter_filter(self.senal_original, umbral_valor, self.fs, btype='low')
        elif self.tipo_filtro.get() == "Pasa-alto":
            self.senal_filtrada = butter_filter(self.senal_original, umbral_valor, self.fs, btype='high')
        elif self.tipo_filtro.get() == "Pasa-banda" and umbral_bajo_valor < umbral_alto_valor:
            self.senal_filtrada = butter_filter(self.senal_original, [umbral_bajo_valor, umbral_alto_valor], self.fs, btype='band')
        elif self.tipo_filtro.get() == "Rechaza-banda" and umbral_bajo_valor < umbral_alto_valor:
            self.senal_filtrada = butter_filter(self.senal_original, [umbral_bajo_valor, umbral_alto_valor], self.fs, btype='bandstop')

        crear_imagen_de_senal(self.t, self.senal_original, self.senal_filtrada, self.fs)

        img = tk.PhotoImage(file='processing/resources/senal.png')
        self.label_imagen.config(image=img)
        self.label_imagen.image = img