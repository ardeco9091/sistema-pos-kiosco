# modulos_admin.py
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import datetime
from config import DB_NAME

# --- GESTOR DE USUARIOS ---
class GestorUsuarios:
    def __init__(self, root):
        self.window = tk.Toplevel(root)
        self.window.title("Gestión de Cajeros")
        self.window.geometry("500x400")
        
        frame_form = tk.LabelFrame(self.window, text="Nuevo Usuario")
        frame_form.pack(pady=10, padx=10, fill=tk.X)
        
        tk.Label(frame_form, text="Nombre:").grid(row=0, column=0, padx=5)
        self.entry_nombre = tk.Entry(frame_form)
        self.entry_nombre.grid(row=0, column=1, padx=5)
        
        tk.Label(frame_form, text="Clave:").grid(row=0, column=2, padx=5)
        self.entry_clave = tk.Entry(frame_form)
        self.entry_clave.grid(row=0, column=3, padx=5)
        
        tk.Label(frame_form, text="Rol:").grid(row=1, column=0, padx=5)
        self.combo_rol = ttk.Combobox(frame_form, values=["CAJERO", "ADMIN"], state="readonly")
        self.combo_rol.current(0)
        self.combo_rol.grid(row=1, column=1, padx=5)
        
        tk.Button(frame_form, text="CREAR", bg="blue", fg="white", command=self.crear_usuario).grid(row=1, column=3, padx=5, pady=5)

        self.tree = ttk.Treeview(self.window, columns=("ID", "Nombre", "Rol"), show="headings")
        self.tree.heading("ID", text="ID"); self.tree.heading("Nombre", text="Nombre"); self.tree.heading("Rol", text="Rol")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.cargar_usuarios()

    def crear_usuario(self):
        nombre = self.entry_nombre.get()
        clave = self.entry_clave.get()
        rol = self.combo_rol.get()
        
        if nombre and clave:
            try:
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute("INSERT INTO usuarios (nombre, clave, rol) VALUES (?, ?, ?)", (nombre, clave, rol))
                conn.commit()
                conn.close()
                messagebox.showinfo("Éxito", "Usuario creado")
                self.entry_nombre.delete(0, tk.END)
                self.entry_clave.delete(0, tk.END)
                self.cargar_usuarios()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "El nombre de usuario ya existe")
        else:
            messagebox.showwarning("Faltan datos", "Complete todos los campos")

    def cargar_usuarios(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, rol FROM usuarios")
        for row in cursor.fetchall():
            self.tree.insert("", "end", values=row)
        conn.close()

# --- GESTOR DE STOCK ---
class GestorStock:
    def __init__(self, root):
        self.window = tk.Toplevel(root)
        self.window.title("Gestión de Inventario (Admin)")
        self.window.geometry("900x650")
        
        # SECCIÓN AGREGAR
        frame_nuevo = tk.LabelFrame(self.window, text="Crear Nuevo Producto", bg="#BBDEFB", bd=2)
        frame_nuevo.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        tk.Label(frame_nuevo, text="Código (Pistola):", bg="#BBDEFB").grid(row=0, column=0, padx=5)
        self.entry_new_codigo = tk.Entry(frame_nuevo, width=20)
        self.entry_new_codigo.grid(row=0, column=1, padx=5, pady=5)
        self.entry_new_codigo.bind('<Return>', lambda e: self.entry_new_nombre.focus())

        tk.Label(frame_nuevo, text="Nombre:", bg="#BBDEFB").grid(row=0, column=2, padx=5)
        self.entry_new_nombre = tk.Entry(frame_nuevo, width=25)
        self.entry_new_nombre.grid(row=0, column=3, padx=5)

        tk.Label(frame_nuevo, text="Precio:", bg="#BBDEFB").grid(row=0, column=4, padx=5)
        self.entry_new_precio = tk.Entry(frame_nuevo, width=10)
        self.entry_new_precio.grid(row=0, column=5, padx=5)

        tk.Label(frame_nuevo, text="Stock Inicial:", bg="#BBDEFB").grid(row=0, column=6, padx=5)
        self.entry_new_stock = tk.Entry(frame_nuevo, width=8)
        self.entry_new_stock.grid(row=0, column=7, padx=5)
        
        btn_crear = tk.Button(frame_nuevo, text="CREAR PRODUCTO", bg="#1976D2", fg="white", font=("Arial", 9, "bold"), command=self.crear_producto)
        btn_crear.grid(row=0, column=8, padx=15)

        # SECCIÓN EDITAR
        frame_edit = tk.LabelFrame(self.window, text="Reponer Stock Existente", bg="#E0E0E0")
        frame_edit.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        tk.Label(frame_edit, text="Producto Seleccionado:", bg="#E0E0E0").grid(row=0, column=0, padx=5, pady=10)
        self.lbl_producto_sel = tk.Label(frame_edit, text="--- Seleccione de la lista ---", font=("Arial", 11, "bold"), fg="blue", bg="#E0E0E0")
        self.lbl_producto_sel.grid(row=0, column=1, padx=5)
        
        tk.Label(frame_edit, text="Cantidad a SUMAR:", bg="#E0E0E0").grid(row=0, column=2, padx=5)
        self.entry_sumar_stock = tk.Entry(frame_edit, width=10)
        self.entry_sumar_stock.grid(row=0, column=3, padx=5)
        self.entry_sumar_stock.bind('<Return>', lambda e: self.sumar_stock())
        
        btn_actualizar = tk.Button(frame_edit, text="SUMAR STOCK", bg="#388E3C", fg="white", font=("Arial", 9, "bold"), command=self.sumar_stock)
        btn_actualizar.grid(row=0, column=4, padx=20)

        # LISTA
        self.tree = ttk.Treeview(self.window, columns=("ID", "Codigo", "Descripcion", "Stock", "Precio"), show="headings")
        self.tree.heading("ID", text="ID"); self.tree.column("ID", width=40)
        self.tree.heading("Codigo", text="Cód. Barras"); self.tree.column("Codigo", width=120)
        self.tree.heading("Descripcion", text="Producto"); self.tree.column("Descripcion", width=300)
        self.tree.heading("Stock", text="Stock"); self.tree.column("Stock", width=80)
        self.tree.heading("Precio", text="Precio"); self.tree.column("Precio", width=80)
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar = ttk.Scrollbar(self.window, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<<TreeviewSelect>>", self.seleccionar_producto)
        self.cargar_datos()

    def cargar_datos(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, codigo_barras, descripcion, stock_actual, precio FROM productos ORDER BY id DESC")
        for row in cursor.fetchall():
            self.tree.insert("", "end", values=row)
        conn.close()

    def crear_producto(self):
        cod = self.entry_new_codigo.get().strip()
        nom = self.entry_new_nombre.get().strip()
        pre = self.entry_new_precio.get().strip()
        stk = self.entry_new_stock.get().strip()

        if not (cod and nom and pre):
            messagebox.showwarning("Faltan Datos", "Complete Código, Nombre y Precio.")
            return
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO productos (codigo_barras, descripcion, precio, stock_actual) VALUES (?, ?, ?, ?)",
                           (cod, nom, float(pre), float(stk) if stk else 0))
            conn.commit()
            conn.close()
            self.entry_new_codigo.delete(0, tk.END); self.entry_new_nombre.delete(0, tk.END)
            self.entry_new_precio.delete(0, tk.END); self.entry_new_stock.delete(0, tk.END)
            self.cargar_datos()
            self.entry_new_codigo.focus_set()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def seleccionar_producto(self, event):
        sel = self.tree.selection()
        if sel:
            item = self.tree.item(sel[0])
            vals = item['values']
            self.id_seleccionado = vals[0]
            self.lbl_producto_sel.config(text=f"{vals[2]} (Actual: {vals[3]})")
            self.entry_sumar_stock.focus_set()

    def sumar_stock(self):
        try:
            cant = float(self.entry_sumar_stock.get())
            if not hasattr(self, 'id_seleccionado'): return
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("UPDATE productos SET stock_actual = stock_actual + ? WHERE id = ?", (cant, self.id_seleccionado))
            conn.commit()
            conn.close()
            self.entry_sumar_stock.delete(0, tk.END)
            self.lbl_producto_sel.config(text="--- Seleccione de la lista ---")
            del self.id_seleccionado
            self.cargar_datos()
        except ValueError:
            messagebox.showerror("Error", "Ingrese un número válido.")

# --- VISOR DE LOGS ---
class VisorLogs:
    def __init__(self, root):
        self.window = tk.Toplevel(root)
        self.window.title("Registros de Auditoría y Seguridad")
        self.window.geometry("1000x600")
        
        tk.Label(self.window, text="HISTORIAL DE MOVIMIENTOS", font=("Arial", 16, "bold"), fg="#333").pack(pady=10)

        self.tree = ttk.Treeview(self.window, columns=("Fecha", "Usuario", "Accion", "Detalle"), show="headings")
        self.tree.heading("Fecha", text="Fecha y Hora"); self.tree.column("Fecha", width=150)
        self.tree.heading("Usuario", text="Usuario"); self.tree.column("Usuario", width=100)
        self.tree.heading("Accion", text="Tipo Acción"); self.tree.column("Accion", width=150)
        self.tree.heading("Detalle", text="Detalle del Evento"); self.tree.column("Detalle", width=500)
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        scrollbar = ttk.Scrollbar(self.window, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.place(relx=0.98, rely=0.1, relheight=0.85, anchor="ne")
        self.cargar_logs()

    def cargar_logs(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT fecha_hora, usuario, accion, detalle FROM logs_audit ORDER BY id DESC")
        for row in cursor.fetchall():
            self.tree.insert("", "end", values=row)
        conn.close()

# --- REPORTES ---
class ReportesApp:
    def __init__(self, root):
        self.window = tk.Toplevel(root)
        self.window.title("Tablero de Control Gerencial")
        self.window.geometry("1000x700")
        self.window.configure(bg="#f0f0f0")

        hoy = datetime.datetime.now().strftime("%d/%m/%Y")
        tk.Label(self.window, text=f"REPORTE DEL DÍA: {hoy}", font=("Arial", 20, "bold"), bg="#f0f0f0", fg="#333").pack(pady=15)

        frame_kpis = tk.Frame(self.window, bg="#f0f0f0")
        frame_kpis.pack(fill=tk.X, padx=20, pady=10)

        self.card_total = self.crear_tarjeta(frame_kpis, "TOTAL VENDIDO HOY", "$ 0.00", "#4CAF50")
        self.card_total.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

        self.card_cant = self.crear_tarjeta(frame_kpis, "TICKETS EMITIDOS", "0", "#2196F3")
        self.card_cant.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

        self.card_prom = self.crear_tarjeta(frame_kpis, "TICKET PROMEDIO", "$ 0.00", "#FF9800")
        self.card_prom.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

        frame_tablas = tk.Frame(self.window, bg="#f0f0f0")
        frame_tablas.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        frame_top = tk.LabelFrame(frame_tablas, text="🏆 Top 5 Más Vendidos (Histórico)", font=("Arial", 12, "bold"), bg="#f0f0f0")
        frame_top.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        self.tree_top = ttk.Treeview(frame_top, columns=("Prod", "Cant"), show="headings", height=10)
        self.tree_top.heading("Prod", text="Producto"); self.tree_top.column("Prod", width=250)
        self.tree_top.heading("Cant", text="Vendidos"); self.tree_top.column("Cant", width=80, anchor="center")
        self.tree_top.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        frame_stock = tk.LabelFrame(frame_tablas, text="⚠️ Alertas de Stock Bajo (< 5 un.)", font=("Arial", 12, "bold"), fg="red", bg="#f0f0f0")
        frame_stock.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)

        self.tree_stock = ttk.Treeview(frame_stock, columns=("Prod", "Stock"), show="headings", height=10)
        self.tree_stock.heading("Prod", text="Producto"); self.tree_stock.column("Prod", width=250)
        self.tree_stock.heading("Stock", text="Queda"); self.tree_stock.column("Stock", width=80, anchor="center")
        self.tree_stock.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        tk.Button(self.window, text="ACTUALIZAR DATOS", bg="#333", fg="white", command=self.calcular_metricas).pack(pady=10)
        self.calcular_metricas()

    def crear_tarjeta(self, parent, titulo, valor, color_borde):
        frame = tk.Frame(parent, bg="white", bd=2, relief=tk.RAISED)
        tk.Frame(frame, bg=color_borde, height=5).pack(fill=tk.X)
        tk.Label(frame, text=titulo, font=("Arial", 10, "bold"), fg="#666", bg="white").pack(pady=(10,5))
        lbl_valor = tk.Label(frame, text=valor, font=("Arial", 22, "bold"), fg="#333", bg="white")
        lbl_valor.pack(pady=(0,15))
        return frame

    def actualizar_tarjeta(self, frame_tarjeta, nuevo_valor):
        lbl = frame_tarjeta.winfo_children()[2]
        lbl.config(text=nuevo_valor)

    def calcular_metricas(self):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("SELECT SUM(total), COUNT(*) FROM ventas WHERE date(fecha_hora, 'localtime') = date('now', 'localtime')")
        row = cursor.fetchone()
        total_hoy = row[0] if row[0] else 0.0
        cant_hoy = row[1] if row[1] else 0
        promedio = (total_hoy / cant_hoy) if cant_hoy > 0 else 0.0

        self.actualizar_tarjeta(self.card_total, f"$ {total_hoy:,.2f}")
        self.actualizar_tarjeta(self.card_cant, str(cant_hoy))
        self.actualizar_tarjeta(self.card_prom, f"$ {promedio:,.2f}")

        for i in self.tree_top.get_children(): self.tree_top.delete(i)
        cursor.execute('''SELECT p.descripcion, SUM(d.cantidad) as total_vendido FROM detalle_ventas d 
                          JOIN productos p ON d.producto_id = p.id GROUP BY p.id ORDER BY total_vendido DESC LIMIT 5''')
        for row in cursor.fetchall():
            self.tree_top.insert("", "end", values=row)

        for i in self.tree_stock.get_children(): self.tree_stock.delete(i)
        cursor.execute("SELECT descripcion, stock_actual FROM productos WHERE stock_actual <= 5 AND es_helado = 0 ORDER BY stock_actual ASC")
        for row in cursor.fetchall():
            self.tree_stock.insert("", "end", values=row)

        conn.close()