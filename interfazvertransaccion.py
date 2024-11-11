import tkinter as tk
from tkinter import ttk, messagebox
import requests

class GestionTransacciones:
    def __init__(self, usuario, contraseña):
        self.usuario = usuario
        self.contraseña = contraseña

        # Crear ventana principal
        self.window = tk.Tk()
        self.window.title("Gestión de Transacciones")
        self.window.geometry("1200x700")

        # Frame de registro de transacciones
        frame_registro = ttk.Frame(self.window, padding="10")
        frame_registro.pack(side=tk.TOP, fill=tk.X, pady=10)

        # Tipo de transacción (modificado a Entry)
        ttk.Label(frame_registro, text="Tipo de Transacción (1 para Venta, 2 para Abastecimiento):").grid(row=0, column=0, sticky=tk.W)
        self.tipo_transaccion_entry = ttk.Entry(frame_registro)
        self.tipo_transaccion_entry.grid(row=0, column=1, columnspan=2, sticky=tk.W + tk.E)

        # Campos de entrada
        ttk.Label(frame_registro, text="ISBN:").grid(row=1, column=0, sticky=tk.W)
        self.isbn_entry = ttk.Entry(frame_registro)
        self.isbn_entry.grid(row=1, column=1, columnspan=2, sticky=tk.W + tk.E)

        ttk.Label(frame_registro, text="Cantidad:").grid(row=2, column=0, sticky=tk.W)
        self.cantidad_entry = ttk.Entry(frame_registro)
        self.cantidad_entry.grid(row=2, column=1, columnspan=2, sticky=tk.W + tk.E)

        # Botón de registrar
        ttk.Button(frame_registro, text="Registrar Transacción", command=self.registrar_transaccion).grid(row=3, column=0, columnspan=3, pady=10)

        # Frame de visualización de transacciones
        frame_transacciones = ttk.Frame(self.window, padding="10")
        frame_transacciones.pack(fill=tk.BOTH, expand=True)

        # Treeview para mostrar transacciones
        self.tree = ttk.Treeview(frame_transacciones, columns=('ISBN', 'Tipo Transacción', 'Fecha', 'Cantidad'), show='headings')
        self.tree.heading('ISBN', text='ISBN')
        self.tree.heading('Tipo Transacción', text='Tipo Transacción')
        self.tree.heading('Fecha', text='Fecha')
        self.tree.heading('Cantidad', text='Cantidad')
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_transacciones, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Cargar transacciones al iniciar
        self.mostrar_transacciones()

    def registrar_transaccion(self):
        isbn = self.isbn_entry.get()
        cantidad = self.cantidad_entry.get()
        tipo_transaccion_str = self.tipo_transaccion_entry.get()

        if not isbn or not cantidad.isdigit() or int(cantidad) <= 0:
            messagebox.showerror("Error", "Ingrese un ISBN válido y una cantidad positiva.")
            return

        # Validar tipo de transacción (debe ser 1 o 2)
        if tipo_transaccion_str not in ['1', '2']:
            messagebox.showerror("Error", "Ingrese '1' para Venta o '2' para Abastecimiento.")
            return

        tipo_transaccion = int(tipo_transaccion_str)

        # Datos a enviar
        data = {
            "ISBN": isbn,
            "cantidad": int(cantidad),
            "tipo_transaccion": tipo_transaccion,
        }

        # Mostrar los datos antes de enviarlos para depurar
        print("Datos a enviar:", data)

        try:
            response = requests.post("http://localhost:5000/add_transaction", json=data, auth=(self.usuario, self.contraseña))

            # Imprimir la respuesta de la API para depurar
            print("Respuesta de la API:", response.status_code, response.text)

            if response.status_code == 201:
                messagebox.showinfo("Éxito", f"Transacción registrada exitosamente.")
                self.mostrar_transacciones()
            else:
                # Mostrar el error que devuelve la API
                messagebox.showerror("Error", f"No se pudo registrar la transacción: {response.json().get('error', 'Error desconocido')}")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"No se pudo conectar con el servidor: {str(e)}")

    def mostrar_transacciones(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            response = requests.get("http://localhost:5000/Transacciones", auth=(self.usuario, self.contraseña))
            if response.status_code == 200:
                transacciones = response.json()
                for transaccion in transacciones:
                    self.tree.insert("", tk.END, values=(
                        transaccion['ISBN'],
                        transaccion['tipo_transaccion'],
                        transaccion['fecha_transaccion'],
                        transaccion['cantidad']
                    ))
            else:
                messagebox.showerror("Error", "No se pudieron obtener las transacciones.")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"No se pudo conectar con el servidor: {str(e)}")

# Ejecutar la aplicación
if __name__ == "__main__": 
    app = GestionTransacciones("usuario", "contraseña")
    app.window.mainloop()
