from flask import Flask, jsonify, request
from flask_httpauth import HTTPBasicAuth
import pyodbc

app = Flask(__name__)
auth = HTTPBasicAuth()

# Configuración de la base de datos
def get_db_connection():
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=DESKTOP-0E1UK80\\SQLNEW;'
        'DATABASE=TiendaLibros;'
        'UID=sa;'
        'PWD=camila2004;'
        'TrustServerCertificate=yes;'
    )
    return conn

# Usuarios y contraseñas
usuarios = {
    "camila": "ca2004",
    "sebastian": "se2003"
}

@auth.verify_password
def verify_password(usuario, contraseña):
    if usuario in usuarios and usuarios[usuario] == contraseña:
        return usuario
    return None

# Ruta para obtener todos los libros
@app.route('/Libros', methods=['GET'])
@auth.login_required
def obtener_libros():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Libros')
    libros = cursor.fetchall()
    conn.close()
    return jsonify([{
        'ISBN': libro[0],
        'titulo': libro[1],
        'precio_compra': float(libro[2]),
        'precio_venta': float(libro[3]),
        'cantidad_actual': libro[4]
    } for libro in libros])

# Ruta para agregar un libro
@app.route('/Libros', methods=['POST'])
@auth.login_required
def agregar_libro():
    nuevo_libro = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO Libros (ISBN, titulo, precio_compra, precio_venta, cantidad_actual) VALUES (?, ?, ?, ?, ?)',
                        nuevo_libro['ISBN'], nuevo_libro['titulo'], nuevo_libro['precio_compra'], nuevo_libro['precio_venta'], nuevo_libro['cantidad_actual'])
        conn.commit()
        return jsonify({'mensaje': 'Libro agregado exitosamente'}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        conn.close()

# Ruta para actualizar un libro
@app.route('/Libros/<string:isbn>', methods=['PUT'])
@auth.login_required
def actualizar_libro(isbn):
    datos_libro = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('UPDATE Libros SET titulo = ?, precio_compra = ?, precio_venta = ?, cantidad_actual = ? WHERE ISBN = ?',
                        datos_libro['titulo'], datos_libro['precio_compra'], datos_libro['precio_venta'], datos_libro['cantidad_actual'], isbn)
        conn.commit()
        return jsonify({'mensaje': 'Libro actualizado exitosamente'})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        conn.close()

# Ruta para eliminar un libro
@app.route('/Libros/<string:isbn>', methods=['DELETE'])
@auth.login_required
def eliminar_libro(isbn):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM Libros WHERE ISBN = ?', isbn)
        conn.commit()
        return jsonify({'mensaje': 'Libro eliminado exitosamente'})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 400
    finally:
        conn.close()

@app.route('/add_transaction', methods=['POST'])
@auth.login_required
def add_transaction():
    data = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("BEGIN TRANSACTION")
        
        # Obtener los datos del libro
        cursor.execute("SELECT cantidad_actual, precio_compra, precio_venta FROM Libros WHERE ISBN = ?", data['ISBN'])
        libro = cursor.fetchone()
        
        if not libro:
            raise Exception("Libro no encontrado")

        cantidad_actual, precio_compra, precio_venta = libro
        
        # Comprobación para tipo de transacción
        if data['tipo_transaccion'] == 1:  # VENTA
            if cantidad_actual < data['cantidad']:
                raise Exception("No hay suficiente stock")
            nueva_cantidad = cantidad_actual - data['cantidad']
            monto = data['cantidad'] * precio_venta
            tipo_movimiento = 'INGRESO'
        else:  # ABASTECIMIENTO
            nueva_cantidad = cantidad_actual + data['cantidad']
            monto = data['cantidad'] * precio_compra
            tipo_movimiento = 'EGRESO'
        
        # Actualización del libro
        cursor.execute("UPDATE Libros SET cantidad_actual = ? WHERE ISBN = ?", nueva_cantidad, data['ISBN'])
        
        # Insertar transacción
        cursor.execute("INSERT INTO Transacciones (ISBN, tipo_transaccion, cantidad) VALUES (?, ?, ?)", 
                        data['ISBN'], data['tipo_transaccion'], data['cantidad'])
        
        # Obtener el ID de la transacción insertada
        cursor.execute("SELECT SCOPE_IDENTITY()")
        id_transaccion = cursor.fetchone()[0]
        
        # Obtener el último saldo de caja
        cursor.execute("SELECT TOP 1 saldo_actual FROM Caja ORDER BY id_movimiento DESC")
        ultimo_saldo = cursor.fetchone()[0]
        
        # Calcular el nuevo saldo
        nuevo_saldo = ultimo_saldo + monto if tipo_movimiento == 'INGRESO' else ultimo_saldo - monto
        
        # Insertar en la caja
        cursor.execute("INSERT INTO Caja (tipo_movimiento, monto, saldo_actual, id_transaccion) VALUES (?, ?, ?, ?)", 
                        tipo_movimiento, monto, nuevo_saldo, id_transaccion)
        
        # Finalizar la transacción
        cursor.execute("COMMIT")
        
        conn.commit()
        return jsonify({'mensaje': 'Transacción registrada exitosamente'}), 201
    
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/Transacciones', methods=['GET'])
@auth.login_required
def obtener_transacciones():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.*, tt.nombre as nombre_tipo
        FROM Transacciones t
        JOIN TiposTransaccion tt ON t.tipo_transaccion = tt.id_tipo
        ORDER BY fecha_transaccion DESC
    """)
    transacciones = cursor.fetchall()
    conn.close()
    transacciones_json = [{'id_transaccion': t.id_transaccion, 
                            'ISBN': t.ISBN,
                            'tipo_transaccion': t.nombre_tipo, 
                            'fecha_transaccion': t.fecha_transaccion,
                            'cantidad': t.cantidad} for t in transacciones]
    return jsonify(transacciones_json)

@app.route('/TiposTransaccion', methods=['GET'])
@auth.login_required
def obtener_tipos_transaccion():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM TiposTransaccion")
    tipos = cursor.fetchall()
    conn.close()
    tipos_json = [{'id_tipo': tipo.id_tipo, 'nombre': tipo.nombre} for tipo in tipos]
    return jsonify(tipos_json)

@app.route('/estado_caja', methods=['GET'])
@auth.login_required
def obtener_estado_caja():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT TOP 1 saldo_actual FROM Caja ORDER BY fecha_movimiento DESC")
    resultado = cursor.fetchone()
    conn.close()

    if resultado:
        estado_caja = resultado[0]  # Extraer el saldo actual
        return jsonify({"estado_caja": estado_caja})
    else:
        return jsonify({"estado_caja": "No disponible"}), 404


if __name__ == '__main__':
    app.run(port=5000)
