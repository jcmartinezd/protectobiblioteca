-- Crear base de datos y usarla
CREATE DATABASE TiendaLibros;
USE TiendaLibros;

-- Tabla para libros
CREATE TABLE Libros (
    ISBN VARCHAR(13) PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    precio_compra DECIMAL(10, 2) NOT NULL,
    precio_venta DECIMAL(10, 2) NOT NULL,
    cantidad_actual INT NOT NULL DEFAULT 0,
    CONSTRAINT chk_precios CHECK (precio_venta >= precio_compra),
    CONSTRAINT chk_cantidad CHECK (cantidad_actual >= 0)
);

-- Tabla para tipos de transacciones
CREATE TABLE TiposTransaccion (
    id_tipo INT PRIMARY KEY,
    nombre VARCHAR(20) NOT NULL,
    CONSTRAINT chk_tipo CHECK (nombre IN ('VENTA', 'ABASTECIMIENTO'))
);

-- Insertar tipos de transacciones v�lidos
INSERT INTO TiposTransaccion (id_tipo, nombre) VALUES 
(1, 'VENTA'),
(2, 'ABASTECIMIENTO');

-- Tabla para transacciones
CREATE TABLE Transacciones (
    id_transaccion INT IDENTITY(1,1) PRIMARY KEY,
    ISBN VARCHAR(13) NOT NULL,
    tipo_transaccion INT NOT NULL,
    fecha_transaccion DATETIME NOT NULL DEFAULT GETDATE(),
    cantidad INT NOT NULL,
    FOREIGN KEY (ISBN) REFERENCES Libros(ISBN) ON DELETE CASCADE,
    FOREIGN KEY (tipo_transaccion) REFERENCES TiposTransaccion(id_tipo),
    CONSTRAINT chk_cantidad_transaccion CHECK (cantidad > 0)
);

-- Tabla para caja
CREATE TABLE Caja (
    id_movimiento INT IDENTITY(1,1) PRIMARY KEY,
    fecha_movimiento DATETIME NOT NULL DEFAULT GETDATE(),
    tipo_movimiento VARCHAR(20) NOT NULL,
    monto DECIMAL(10, 2) NOT NULL,
    saldo_actual DECIMAL(10, 2) NOT NULL,
    id_transaccion INT,
    FOREIGN KEY (id_transaccion) REFERENCES Transacciones(id_transaccion),
    CONSTRAINT chk_tipo_movimiento CHECK (tipo_movimiento IN ('INGRESO', 'EGRESO'))
);

-- Insertar el saldo inicial en caja
INSERT INTO Caja (tipo_movimiento, monto, saldo_actual) 
VALUES ('INGRESO', 1000000.00, 1000000.00);

-- Trigger para ventas: actualiza el inventario y suma a la caja
CREATE TRIGGER trg_Venta_Transaccion
ON Transacciones
AFTER INSERT
AS
BEGIN
    DECLARE @ISBN VARCHAR(13), @tipo_transaccion INT, @cantidad INT, @precio_venta DECIMAL(10, 2);

    SELECT @ISBN = ISBN, @tipo_transaccion = tipo_transaccion, @cantidad = cantidad FROM inserted;

    IF @tipo_transaccion = 1
    BEGIN
        SELECT @precio_venta = precio_venta FROM Libros WHERE ISBN = @ISBN;
        
        -- Actualizar inventario
        UPDATE Libros
        SET cantidad_actual = cantidad_actual - @cantidad
        WHERE ISBN = @ISBN;
        
        -- Registrar ingreso en caja
        INSERT INTO Caja (tipo_movimiento, monto, saldo_actual, id_transaccion)
        SELECT 'INGRESO', @cantidad * @precio_venta, 
               (SELECT TOP 1 saldo_actual FROM Caja ORDER BY id_movimiento DESC) + (@cantidad * @precio_venta),
                inserted.id_transaccion
        FROM inserted;
    END
END;

-- Trigger para abastecimientos: actualiza inventario y resta de la caja
CREATE TRIGGER trg_Abastecimiento_Transaccion
ON Transacciones
AFTER INSERT
AS
BEGIN
    DECLARE @ISBN VARCHAR(13), @tipo_transaccion INT, @cantidad INT, @precio_compra DECIMAL(10, 2);

    SELECT @ISBN = ISBN, @tipo_transaccion = tipo_transaccion, @cantidad = cantidad FROM inserted;

    IF @tipo_transaccion = 2
    BEGIN
        SELECT @precio_compra = precio_compra FROM Libros WHERE ISBN = @ISBN;
        
        -- Actualizar inventario
        UPDATE Libros
        SET cantidad_actual = cantidad_actual + @cantidad
        WHERE ISBN = @ISBN;

        -- Registrar egreso en caja
        INSERT INTO Caja (tipo_movimiento, monto, saldo_actual, id_transaccion)
        SELECT 'EGRESO', @cantidad * @precio_compra, 
               (SELECT TOP 1 saldo_actual FROM Caja ORDER BY id_movimiento DESC) - (@cantidad * @precio_compra),
                inserted.id_transaccion
        FROM inserted;
    END
END;

-- DATOS DE PRUEBA --

--1. PRUEBAS DE REGISTROS (LIBROS Y TRANSACCIONES)
-- Insertar libros de prueba
INSERT INTO Libros (ISBN, titulo, precio_compra, precio_venta, cantidad_actual) VALUES
('9788498387087', 'Cien a�os de soledad', 25000.00, 45000.00, 10),
('9788420471839', '1984', 20000.00, 35000.00, 15),
('9788420412146', 'El Se�or de los Anillos', 35000.00, 65000.00, 8),
('9788466337991', 'El C�digo Da Vinci', 22000.00, 40000.00, 12);
-- Insertar transacciones de prueba
INSERT INTO Transacciones (ISBN, tipo_transaccion, cantidad) VALUES
('9788498387087', 1, 3),
('9788420471839', 2, 5); 

--2. PRUEBA DE ELIMINAR LIBRO DEL CATALOGO
--eliminar libro 
DELETE FROM Libros WHERE ISBN = '9788498387087';
SELECT * FROM Libros WHERE ISBN = '9788498387087';

--3. PRUEBA DE BUSCAR LIBRO POR TITULO
-- B�squeda por t�tulo
SELECT * FROM Libros WHERE titulo = '1984';

--4. PRUEBA DE BUSCAR LIBRO POR ISBN
-- B�squeda por ISBN 
SELECT * FROM Libros WHERE ISBN = '9788420471839';

--5. PRUEBA DE ABASTECIMIENTO
--abastecimiento de el se�or de los anillos
INSERT INTO Transacciones (ISBN, tipo_transaccion, cantidad) VALUES ('9788420412146', 2, 2);
SELECT * FROM Libros;
SELECT * FROM Caja ORDER BY id_movimiento DESC;

--6 PRUEBA VENTA DE LIBRO
INSERT INTO Transacciones (ISBN, tipo_transaccion, cantidad) VALUES ('9788420412146', 1, 2);
SELECT * FROM Libros;
SELECT * FROM Caja ORDER BY id_movimiento DESC;

--7 Calcular la cantidad de transacciones de abastecimiento de un libro 

DECLARE @ISBN_buscar VARCHAR(20) = '9788420412146';
SELECT COUNT(*) AS cantidad_abastecimientos
FROM Transacciones
WHERE ISBN = @ISBN_buscar AND tipo_transaccion = 2;

--8 Buscar libro mas costoso 

SELECT TOP 1 ISBN, titulo, precio_venta 
FROM Libros 
ORDER BY precio_venta DESC;

--9 buscar libro menos costoso 

SELECT TOP 1 ISBN, titulo, precio_venta 
FROM Libros 
ORDER BY precio_venta ASC;

--10 buscar libro mas vendido 

SELECT TOP 1 l.ISBN, l.titulo, SUM(t.cantidad) AS total_vendidos
FROM Transacciones t
JOIN Libros l ON t.ISBN = l.ISBN
WHERE t.tipo_transaccion = 1
GROUP BY l.ISBN, l.titulo
ORDER BY total_vendidos DESC;
