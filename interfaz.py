import tkinter as tk
from tkinter import ttk, messagebox
import requests
from PIL import Image, ImageTk
from interfazlibro import GestionLibros
from interfazvertransaccion import GestionTransacciones
from interfazvercaja import EstadoCaja

class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Login - Sistema de Librería")
        self.root.geometry("400x300")
        self.root.configure(bg='#f0f0f0')
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Título
        title_label = ttk.Label(main_frame, text="Iniciar Sesión", font=('Helvetica', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=20)
        
        # Usuario
        ttk.Label(main_frame, text="Usuario:").grid(row=1, column=0, pady=5, sticky="e")
        self.username_entry = ttk.Entry(main_frame)
        self.username_entry.grid(row=1, column=1, pady=5, padx=5)
        
        # Contraseña
        ttk.Label(main_frame, text="Contraseña:").grid(row=2, column=0, pady=5, sticky="e")
        self.password_entry = ttk.Entry(main_frame, show="*")
        self.password_entry.grid(row=2, column=1, pady=5, padx=5)
        
        # Botón de login
        login_button = ttk.Button(main_frame, text="Ingresar", command=self.login)
        login_button.grid(row=3, column=0, columnspan=2, pady=20)
        
        self.root.mainloop()
    
    def login(self):
        usuario = self.username_entry.get()
        contraseña = self.password_entry.get()
        
        try:
            # Intentar hacer una petición de prueba para verificar credenciales
            response = requests.get('http://localhost:5000/Libros', 
                                    auth=(usuario, contraseña))
            
            if response.status_code == 200:
                self.root.destroy()  # Cerrar ventana de login
                MenuPrincipal(usuario, contraseña)  # Pasar credenciales al menú principal
            else:
                messagebox.showerror("Error", "Credenciales inválidas")
                
        except requests.exceptions.RequestException:
            messagebox.showerror("Error", "No se pudo conectar al servidor")

class MenuPrincipal:
    def __init__(self, usuario, contraseña):
        self.root = tk.Tk()
        self.root.title("Sistema de Librería")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Guardar credenciales
        self.usuario = usuario
        self.contraseña = contraseña
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(expand=True, fill="both")
        
        # Título
        title_label = ttk.Label(main_frame, 
                                text="Sistema de Gestión de Librería", 
                                font=('Helvetica', 18, 'bold'))
        title_label.pack(pady=20)
        
        # Frame para botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(expand=True)
        
        # Botones del menú
        buttons = [
            ("Gestión de Libros", self.abrir_gestion_libros),
            ("Ver Transacciones", self.ver_transacciones),
            ("Estado de Caja", self.estado_caja),
            ("Salir", self.root.destroy)
        ]
        
        for text, command in buttons:
            btn = ttk.Button(button_frame, text=text, command=command)
            btn.pack(pady=10, padx=20, fill="x")
        
        self.root.mainloop()
    
    def abrir_gestion_libros(self):
        gestion_libros_window = GestionLibros(self.usuario, self.contraseña)

    def ver_transacciones(self):
        gestion_vertransaccion_window = GestionTransacciones(self.usuario, self.contraseña)

    def estado_caja(self):
        gestion_caja_window = EstadoCaja(self.usuario, self.contraseña)

if __name__ == "__main__":
    LoginWindow()
