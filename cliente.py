import requests

#Funcion para establecer la autenticación
def establecer_aut(usuario, contraseña):
    global auth 
    auth = (usuario, contraseña)

#Funcion para obtener libros
def obtener_libros():
    try:
        response = requests.get('http://localhost:5000/Libros', auth=auth)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print (f"Error al obtener Libros: {e}")
        return[]

#Funcion para agregar Libros
def agregar_libro(ISBN, titulo, precio_compra, precio_venta, cantidad_actual):
    data = {
        "ISBN": ISBN,
        "titulo": titulo,
        "precio_compra": precio_compra,
        "precio_venta": precio_venta,
        "cantidad_actual": cantidad_actual
    }
    try:
        response = requests.post('http://localhost:5000/Libros', json=data, auth=auth)
        response.raise_for_status()
        print("Libro agregado exitosamente")
    except requests.exceptions.RequestException as e:
        print(f"Error al agregar libro: {e}")

#Funcion para actualizar un libro
def actualizar_libro(ISBN, titulo, precio_compra, precio_venta, cantidad_actual):
    data = {
        "titulo": titulo,
        "precio_compra": precio_compra,
        "precio_venta": precio_venta,
        "cantidad_actual": cantidad_actual
    }
    try:
        response = requests.put(f'http://localhost:5000/Libros/{ISBN}', json=data, auth=auth)
        response.raise_for_status()
        print("Libro actualizado exitosamente")
    except requests.exceptions.RequestException as e:
        print(f"Error al actualizar libro: {e}")

# Función para eliminar un libro
def eliminar_libro(ISBN):
    try:
        response = requests.delete(f'http://localhost:5000/Libros/{ISBN}', auth=auth)
        response.raise_for_status()
        print("Libro eliminado exitosamente")
    except requests.exceptions.RequestException as e:
        print(f"Error al eliminar libro: {e}")

# Función para registrar una transacción
def registrar_transaccion(ISBN, tipo_transaccion, cantidad):
    data = {
        "ISBN": ISBN,
        "tipo_transaccion": tipo_transaccion,
        "cantidad": cantidad
    }
    try:
        response = requests.post('http://localhost:5000/add_transaction', json=data, auth=auth)
        response.raise_for_status()
        print("Transacción registrada exitosamente")
    except requests.exceptions.RequestException as e:
        print(f"Error al registrar transacción: {e}")

# Función para obtener transacciones
def obtener_transacciones():
    try:
        response = requests.get('http://localhost:5000/Transacciones', auth=auth)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener transacciones: {e}")
        return []

# Función para obtener tipos de transacción
def obtener_tipos_transaccion():
    try:
        response = requests.get('http://localhost:5000/TiposTransaccion', auth=auth)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener tipos de transacción: {e}")
        return []

# Función para obtener el estado de la caja
def obtener_estado_caja():
    try:
        response = requests.get('http://localhost:5000/estado_caja', auth=auth)
        response.raise_for_status()
        return response.json().get("estado_caja", "No disponible")
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener el estado de la caja: {e}")
        return "Error al conectar con el servidor"
