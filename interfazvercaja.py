import tkinter as tk
from tkinter import ttk, messagebox
import requests

class EstadoCaja:
    def __init__(self, usuario, contraseña, parent_window=None):
        self.usuario = usuario
        self.contraseña = contraseña
        
        # Crear ventana
        self.window = tk.Toplevel() if parent_window else tk.Tk()
        self.window.title("Estado de Caja")
        self.window.geometry("400x200")

        # Frame principal
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título de estado de caja
        ttk.Label(main_frame, text="Estado Actual de Caja", font=("Arial", 14)).pack(pady=10)

        # Etiqueta para mostrar el valor de caja
        self.caja_label = ttk.Label(main_frame, text="Consultando...", font=("Arial", 12))
        self.caja_label.pack(pady=20)

        # Botón para refrescar estado de caja
        self.refresh_btn = ttk.Button(main_frame, text="Actualizar Estado de Caja", command=self.mostrar_estado_caja)
        self.refresh_btn.pack(pady=10)

        # Llamada inicial para mostrar el estado de caja
        self.mostrar_estado_caja()

    def mostrar_estado_caja(self):
        # Realiza una solicitud al servidor para obtener el estado de caja
        try:
            response = requests.get("http://localhost:5000/estado_caja", auth=(self.usuario, self.contraseña))
            if response.status_code == 200:
                estado_caja = response.json().get("estado_caja", "Error al obtener el estado")
                self.caja_label.config(text=f"Estado de Caja: ${estado_caja}")
            else:
                messagebox.showerror("Error", "No se pudo obtener el estado de caja.")
        except requests.exceptions.RequestException:
            messagebox.showerror("Error", "No se pudo conectar con el servidor.")
