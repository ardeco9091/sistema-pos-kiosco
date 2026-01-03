import sqlite3

def inicializar():
    conn = sqlite3.connect("negocio.db")
    cursor = conn.cursor()

    # --- 1. Crear Tabla de USUARIOS ---
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT UNIQUE NOT NULL,
        clave TEXT NOT NULL,
        rol TEXT NOT NULL,
        activo INTEGER DEFAULT 1
    )
    ''')

    # --- 2. Crear Tabla PRODUCTOS ---
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo_barras TEXT UNIQUE,
        descripcion TEXT NOT NULL,
        precio REAL NOT NULL,
        stock_actual REAL DEFAULT 0,
        es_helado INTEGER DEFAULT 0
    )
    ''')

    # --- 3. Crear Tablas de VENTAS ---
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ventas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
        usuario_id INTEGER,
        total REAL NOT NULL,
        metodo_pago TEXT,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS detalle_ventas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        venta_id INTEGER,
        producto_id INTEGER,
        cantidad REAL,
        precio_unitario REAL,
        subtotal REAL,
        FOREIGN KEY(venta_id) REFERENCES ventas(id)
    )
    ''')

    # --- 4. NUEVA TABLA: LOGS DE AUDITORÍA (Lo que agregamos ahora) ---
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS logs_audit (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
        usuario TEXT,
        accion TEXT,
        detalle TEXT
    )
    ''')

    # --- 5. Crear usuario ADMIN por defecto (Solo si no existe nadie) ---
    cursor.execute("SELECT count(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        print("Creando usuario Administrador por defecto...")
        cursor.execute("INSERT INTO usuarios (nombre, clave, rol) VALUES (?, ?, ?)", ("admin", "1234", "ADMIN"))
        conn.commit()
    
    conn.close()
    print("Base de datos actualizada. Tabla 'logs_audit' lista para usar.")

if __name__ == "__main__":
    inicializar()