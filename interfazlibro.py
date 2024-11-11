import tkinter as tk
from tkinter import ttk, messagebox
import requests

class GestionLibros:
    def __init__(self, usuario, contraseña, parent_window=None):
        self.usuario = usuario
        self.contraseña = contraseña
        
        # Crear ventana
        self.window = tk.Toplevel() if parent_window else tk.Tk()
        self.window.title("Gestión de Libros")
        self.window.geometry("1000x600")
        
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame superior para botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Botones
        ttk.Button(button_frame, text="Agregar Libro", command=self.abrir_ventana_agregar).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Editar Libro", command=self.abrir_ventana_editar).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Eliminar Libro", command=self.eliminar_libro).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Actualizar Lista", command=self.cargar_libros).pack(side=tk.LEFT, padx=5)
        
        # Crear Treeview
        self.tree = ttk.Treeview(main_frame, columns=('ISBN', 'Título', 'Precio Compra', 'Precio Venta', 'Cantidad'), show='headings')
        
        # Configurar columnas
        self.tree.heading('ISBN', text='ISBN')
        self.tree.heading('Título', text='Título')
        self.tree.heading('Precio Compra', text='Precio Compra')
        self.tree.heading('Precio Venta', text='Precio Venta')
        self.tree.heading('Cantidad', text='Cantidad')
        
        # Configurar anchos de columna
        self.tree.column('ISBN', width=120)
        self.tree.column('Título', width=300)
        self.tree.column('Precio Compra', width=100)
        self.tree.column('Precio Venta', width=100)
        self.tree.column('Cantidad', width=100)
        
        # Agregar scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetar Treeview y scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Cargar libros
        self.cargar_libros()
    
    def cargar_libros(self):
        try:
            # Limpiar tabla
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Obtener libros del servidor
            response = requests.get('http://localhost:5000/Libros', auth=(self.usuario, self.contraseña))
            libros = response.json()
            
            # Insertar libros en la tabla
            for libro in libros:
                self.tree.insert('', tk.END, values=(
                    libro['ISBN'],
                    libro['titulo'],
                    f"${libro['precio_compra']:.2f}",
                    f"${libro['precio_venta']:.2f}",
                    libro['cantidad_actual']
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar libros: {str(e)}")
    
    def abrir_ventana_agregar(self):
        VentanaLibro(self, self.usuario, self.contraseña)
    
    def abrir_ventana_editar(self):
        # Obtener el elemento seleccionado
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un libro para editar")
            return
        
        # Obtener datos del libro seleccionado
        libro = self.tree.item(seleccion[0])['values']
        VentanaLibro(self, self.usuario, self.contraseña, libro)
    
    def eliminar_libro(self):
        seleccion = self.tree.selection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor, seleccione un libro para eliminar")
            return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de que desea eliminar este libro?"):
            libro = self.tree.item(seleccion[0])['values']
            try:
                response = requests.delete(
                    f'http://localhost:5000/Libros/{libro[0]}',
                    auth=(self.usuario, self.contraseña)
                )
                response.raise_for_status()
                messagebox.showinfo("Éxito", "Libro eliminado correctamente")
                self.cargar_libros()
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar libro: {str(e)}")

class VentanaLibro:
    def __init__(self, parent, usuario, contraseña, libro=None):
        self.parent = parent
        self.usuario = usuario
        self.contraseña = contraseña
        self.libro = libro
        
        # Crear ventana
        self.window = tk.Toplevel()
        self.window.title("Editar Libro" if libro else "Agregar Libro")
        self.window.geometry("400x300")
        
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Campos del formulario
        ttk.Label(main_frame, text="ISBN:").grid(row=0, column=0, pady=5, sticky=tk.E)
        self.isbn_entry = ttk.Entry(main_frame)
        self.isbn_entry.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(main_frame, text="Título:").grid(row=1, column=0, pady=5, sticky=tk.E)
        self.titulo_entry = ttk.Entry(main_frame)
        self.titulo_entry.grid(row=1, column=1, pady=5, padx=5)
        
        ttk.Label(main_frame, text="Precio Compra:").grid(row=2, column=0, pady=5, sticky=tk.E)
        self.precio_compra_entry = ttk.Entry(main_frame)
        self.precio_compra_entry.grid(row=2, column=1, pady=5, padx=5)
        
        ttk.Label(main_frame, text="Precio Venta:").grid(row=3, column=0, pady=5, sticky=tk.E)
        self.precio_venta_entry = ttk.Entry(main_frame)
        self.precio_venta_entry.grid(row=3, column=1, pady=5, padx=5)
        
        ttk.Label(main_frame, text="Cantidad:").grid(row=4, column=0, pady=5, sticky=tk.E)
        self.cantidad_entry = ttk.Entry(main_frame)
        self.cantidad_entry.grid(row=4, column=1, pady=5, padx=5)
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Guardar", command=self.guardar).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", command=self.window.destroy).pack(side=tk.LEFT, padx=5)
        
        # Si estamos editando, llenar campos con datos existentes
        if libro:
            self.isbn_entry.insert(0, libro[0])
            self.isbn_entry.configure(state='disabled')  # No permitir editar ISBN
            self.titulo_entry.insert(0, libro[1])
            self.precio_compra_entry.insert(0, libro[2].replace('$', ''))
            self.precio_venta_entry.insert(0, libro[3].replace('$', ''))
            self.cantidad_entry.insert(0, libro[4])
    
    def guardar(self):
        # Validar campos
        try:
            precio_compra = float(self.precio_compra_entry.get())
            precio_venta = float(self.precio_venta_entry.get())
            cantidad = int(self.cantidad_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Los precios y la cantidad deben ser números válidos")
            return
        
        # Preparar datos
        data = {
            "ISBN": self.isbn_entry.get(),
            "titulo": self.titulo_entry.get(),
            "precio_compra": precio_compra,
            "precio_venta": precio_venta,
            "cantidad_actual": cantidad
        }
        
        try:
            if self.libro:  # Editar
                response = requests.put(
                    f'http://localhost:5000/Libros/{self.libro[0]}',
                    json=data,
                    auth=(self.usuario, self.contraseña)
                )
            else:  # Agregar
                response = requests.post(
                    'http://localhost:5000/Libros',
                    json=data,
                    auth=(self.usuario, self.contraseña)
                )
            
            response.raise_for_status()
            messagebox.showinfo("Éxito", "Libro guardado correctamente")
            self.parent.cargar_libros()
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar libro: {str(e)}")

if __name__ == "__main__":
    # Para pruebas independientes
    app = GestionLibros("usuario", "contraseña")
    app.window.mainloop()
