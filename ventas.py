# ventas.py
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from config import DB_NAME, MAPA_TECLAS
from modulos_admin import GestorUsuarios, GestorStock, VisorLogs, ReportesApp
from buscador import BuscadorProductos

class PuntoDeVenta:
    def __init__(self, root, usuario_data):
        self.root = root
        self.usuario_id, self.usuario_nombre, self.usuario_rol = usuario_data
        
        self.root.title(f"POS Kiosco - Atendido por: {self.usuario_nombre} ({self.usuario_rol})")
        self.root.geometry("1024x768")
        
        self.total_venta = 0.0
        self.items_ticket = []

        # -- Panel Superior --
        frame_top = tk.Frame(root, bg="#e1e1e1", bd=5)
        frame_top.pack(side=tk.TOP, fill=tk.X)

        tk.Label(frame_top, text="CÓDIGO:", font=("Arial", 14), bg="#e1e1e1").pack(side=tk.LEFT)
        self.entry_codigo = tk.Entry(frame_top, font=("Arial", 24), width=15)
        self.entry_codigo.pack(side=tk.LEFT, padx=10, pady=10)
        self.entry_codigo.bind('<Return>', self.buscar_y_agregar)

        btn_buscar = tk.Button(frame_top, text="🔍 BUSCAR (F8)", bg="#00BCD4", fg="white", font=("Arial", 10, "bold"), 
                               command=self.abrir_buscador)
        btn_buscar.pack(side=tk.LEFT, padx=5)
        root.bind("<F8>", lambda e: self.abrir_buscador())

        if self.usuario_rol == "ADMIN":
            btn_users = tk.Button(frame_top, text="USUARIOS", bg="blue", fg="white", command=self.abrir_gestion_usuarios)
            btn_users.pack(side=tk.RIGHT, padx=5)
            
            btn_stock = tk.Button(frame_top, text="STOCK (F9)", bg="#FF9800", fg="white", command=self.abrir_stock)
            btn_stock.pack(side=tk.RIGHT, padx=5)
            
            btn_report = tk.Button(frame_top, text="REPORTES", bg="#673AB7", fg="white", command=self.abrir_reportes)
            btn_report.pack(side=tk.RIGHT, padx=5)

            btn_logs = tk.Button(frame_top, text="AUDITORÍA", bg="#5D4037", fg="white", command=self.abrir_logs)
            btn_logs.pack(side=tk.RIGHT, padx=5)
            
            root.bind("<F9>", lambda e: self.abrir_stock())
            root.bind("<F10>", lambda e: self.abrir_logs())

        # -- Panel Izquierdo (Lista) --
        frame_left = tk.Frame(root)
        frame_left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.tree = ttk.Treeview(frame_left, columns=('prod', 'cant', 'precio', 'subtotal'), show='headings')
        self.tree.heading('prod', text='Producto'); self.tree.column('prod', width=300)
        self.tree.heading('cant', text='Cnt'); self.tree.column('cant', width=50)
        self.tree.heading('precio', text='Precio'); self.tree.column('precio', width=80)
        self.tree.heading('subtotal', text='Total'); self.tree.column('subtotal', width=80)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        self.tree.bind("<Delete>", self.eliminar_item)
        root.bind("<Delete>", self.eliminar_item)

        # -- Panel Derecho (Botones Rápidos) --
        frame_right = tk.Frame(root, bg="#333", width=250)
        frame_right.pack(side=tk.RIGHT, fill=tk.Y)
        
        colores = ["#FFCCBC", "#FFE0B2", "#FFF9C4", "#C8E6C9", "#B3E5FC"]
        i = 0
        
        conn_temp = sqlite3.connect(DB_NAME)
        cursor_temp = conn_temp.cursor()
        
        for tecla, codigo in MAPA_TECLAS.items():
            cursor_temp.execute("SELECT descripcion FROM productos WHERE codigo_barras = ?", (codigo,))
            resultado = cursor_temp.fetchone()
            nombre_producto = resultado[0] if resultado else f"Producto {tecla}"
            texto_boton = f"{tecla} - {nombre_producto}"
            
            # Usamos default argument c=codigo para evitar problemas de closure en lambdas
            btn = tk.Button(frame_right, text=texto_boton, bg=colores[i], font=("Arial", 9, "bold"),
                            command=lambda c=codigo: self.agregar_producto_db(c))
            btn.pack(fill=tk.X, pady=3, padx=5)
            root.bind(f"<{tecla}>", lambda event, c=codigo: self.agregar_producto_db(c))
            i += 1
            
        conn_temp.close()

        tk.Button(frame_right, text="BORRAR (Supr)", bg="#D32F2F", fg="white", command=self.eliminar_item).pack(fill=tk.X, padx=5, pady=10)
        tk.Button(frame_right, text="COBRAR (F12)", bg="green", fg="white", font=("Arial", 16), height=2,
                  command=self.procesar_cobro).pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=20)
        root.bind("<F12>", lambda e: self.procesar_cobro())

        # -- Panel Inferior (Total) --
        frame_bottom = tk.Frame(root, bg="black", bd=10)
        frame_bottom.pack(side=tk.BOTTOM, fill=tk.X)
        self.lbl_total = tk.Label(frame_bottom, text="TOTAL: $ 0.00", font=("Arial", 30), bg="black", fg="#00FF00")
        self.lbl_total.pack(side=tk.RIGHT)

        self.entry_codigo.focus_set()

    def registrar_log(self, accion, detalle):
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO logs_audit (usuario, accion, detalle) VALUES (?, ?, ?)", 
                        (self.usuario_nombre, accion, detalle))
            conn.commit()
            conn.close()
        except: pass

    def buscar_y_agregar(self, event):
        codigo = self.entry_codigo.get().strip()
        if codigo: 
            self.agregar_producto_db(codigo)
            self.entry_codigo.delete(0, tk.END)

    def agregar_producto_db(self, codigo):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, descripcion, precio, stock_actual, es_helado FROM productos WHERE codigo_barras=?", (codigo,))
        prod = cursor.fetchone()
        conn.close()

        if prod:
            id_db, descripcion, precio, stock_real, es_helado = prod

            # Cálculo de cantidades
            cantidad_en_carrito = 0
            for item in self.items_ticket:
                if item['id_db'] == id_db:
                    cantidad_en_carrito += item['cantidad']

            cantidad_a_sumar = 1
            total_que_quedaria = cantidad_en_carrito + cantidad_a_sumar
            stock_remanente = stock_real - total_que_quedaria

            # 1. BLOQUEO SI NO HAY STOCK
            if total_que_quedaria > stock_real:
                messagebox.showerror("¡STOCK INSUFICIENTE!", 
                                     f"No puedes vender este producto.\nStock Real: {stock_real}\nIntentas vender: {total_que_quedaria}")
                self.entry_codigo.focus_set()
                return

            # 2. ALERTA DE STOCK BAJO (MEJORADA)
            # Avisa si la venta dejará el stock en zona de peligro (<= 5)
            if stock_remanente <= 5 and stock_remanente >= 0:
                messagebox.showwarning("⚠️ ALERTA DE STOCK ⚠️", 
                                       f"¡Cuidado!\nAl vender este producto, el stock quedará en: {stock_remanente} unidades.\n\nProducto: {descripcion}")

            # 3. AGREGAR AL CARRITO
            subtotal = precio
            iid = self.tree.insert('', 'end', values=(descripcion, 1, f"${precio}", f"${subtotal}"))
            self.items_ticket.append({"iid": iid, "id_db": id_db, "precio": precio, "cantidad": 1, "subtotal": subtotal})
            self.recalcular()
            
        else:
            messagebox.showerror("Error", "Producto no existe")
        
        self.entry_codigo.focus_set()

    def eliminar_item(self, event=None):
        sel = self.tree.selection()
        if not sel and self.tree.get_children(): sel = (self.tree.get_children()[-1],)
        
        for iid in sel:
            try:
                item_values = self.tree.item(iid)['values']
                prod_nombre = item_values[0]
                self.registrar_log("ELIMINAR_ITEM", f"Se borró {prod_nombre} del ticket")
            except: pass

            self.tree.delete(iid)
            self.items_ticket = [x for x in self.items_ticket if x['iid'] != iid]
        
        self.recalcular()
        self.entry_codigo.focus_set()

    def recalcular(self):
        self.total_venta = sum(x['subtotal'] for x in self.items_ticket)
        self.lbl_total.config(text=f"TOTAL: $ {self.total_venta:,.2f}")

    def procesar_cobro(self):
        # --- INICIO BLOQUE DEMO ---
        # Opción A: Límite por cantidad de ventas
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM ventas")
        total_ventas = cursor.fetchone()[0]
        conn.close()

        LIMIT_DEMO = 100 # Solo deja hacer 20 ventas
        
        if total_ventas >= LIMIT_DEMO:
            messagebox.showwarning("Modo Demo", 
                "Has alcanzado el límite de ventas de la versión DEMO.\n\n"
                "Para seguir usando el sistema, contacta al desarrollador:\n"
                "ardeco9091@gmail.com")
            return # Detiene la función, no cobra
        # --- FIN BLOQUE DEMO ---

        if not self.items_ticket: return
        
        if messagebox.askyesno("Cobrar", f"Total: ${self.total_venta}"):
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO ventas (usuario_id, total, metodo_pago) VALUES (?, ?, ?)", 
                               (self.usuario_id, self.total_venta, "EFECTIVO"))
                venta_id = cursor.lastrowid
                for item in self.items_ticket:
                    cursor.execute("INSERT INTO detalle_ventas (venta_id, producto_id, cantidad, precio_unitario, subtotal) VALUES (?,?,?,?,?)",
                                   (venta_id, item['id_db'], item['cantidad'], item['precio'], item['subtotal']))
                    cursor.execute("UPDATE productos SET stock_actual = stock_actual - ? WHERE id=?", (item['cantidad'], item['id_db']))
                
                conn.commit()
                self.registrar_log("VENTA_CERRADA", f"Ticket #{venta_id} por ${self.total_venta}")
                
                self.items_ticket = []
                for x in self.tree.get_children(): self.tree.delete(x)
                self.recalcular()
            except Exception as e:
                conn.rollback()
                messagebox.showerror("Error", str(e))
            finally:
                conn.close()
            self.entry_codigo.focus_set()

    def abrir_gestion_usuarios(self):
        GestorUsuarios(self.root)
    def abrir_stock(self):
        GestorStock(self.root)
    def abrir_logs(self):
        VisorLogs(self.root)
    def abrir_reportes(self):
        ReportesApp(self.root)
    def abrir_buscador(self):
        BuscadorProductos(self.root, self.agregar_producto_db)