# buscador.py
import tkinter as tk
from tkinter import ttk
import sqlite3
from config import DB_NAME

class BuscadorProductos:
    def __init__(self, root, callback_agregar):
        self.callback = callback_agregar # Función que llamaremos al elegir
        self.window = tk.Toplevel(root)
        self.window.title("Buscar Producto por Nombre")
        self.window.geometry("600x400")
        self.window.configure(bg="#333")
        
        # Para que la ventana quede siempre arriba y bloquee la de atrás
        self.window.transient(root)
        self.window.grab_set()

        tk.Label(self.window, text="Escribe el nombre del producto:", fg="white", bg="#333", font=("Arial", 12)).pack(pady=5)

        self.entry_busqueda = tk.Entry(self.window, font=("Arial", 14))
        self.entry_busqueda.pack(fill=tk.X, padx=20, pady=5)
        self.entry_busqueda.bind("<KeyRelease>", self.filtrar_productos) # Busca mientras escribes
        self.entry_busqueda.bind("<Return>", self.seleccionar_producto)  # Enter para elegir
        self.entry_busqueda.bind("<Down>", self.bajar_foco) # Flecha abajo va a la lista

        # Lista de resultados
        self.tree = ttk.Treeview(self.window, columns=("Codigo", "Nombre", "Precio", "Stock"), show="headings")
        self.tree.heading("Codigo", text="Cód."); self.tree.column("Codigo", width=100)
        self.tree.heading("Nombre", text="Descripción"); self.tree.column("Nombre", width=300)
        self.tree.heading("Precio", text="Precio"); self.tree.column("Precio", width=80)
        self.tree.heading("Stock", text="Stock"); self.tree.column("Stock", width=60)
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        self.tree.bind("<Double-1>", self.seleccionar_producto) # Doble clic elige
        self.tree.bind("<Return>", self.seleccionar_producto)

        self.entry_busqueda.focus_set()
        self.filtrar_productos() # Cargar todos al inicio

    def filtrar_productos(self, event=None):
        texto = self.entry_busqueda.get()
        for item in self.tree.get_children(): self.tree.delete(item)
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        query = "SELECT codigo_barras, descripcion, precio, stock_actual FROM productos WHERE descripcion LIKE ? LIMIT 20"
        cursor.execute(query, (f"%{texto}%",))
        
        for row in cursor.fetchall():
            self.tree.insert("", "end", values=row)
        conn.close()

    def bajar_foco(self, event):
        if self.tree.get_children():
            self.tree.focus_set()
            self.tree.selection_set(self.tree.get_children()[0])

    def seleccionar_producto(self, event=None):
        sel = self.tree.selection()
        if sel:
            item = self.tree.item(sel[0])
            codigo = item['values'][0] 
            self.callback(codigo) # <-- Llama a la función en ventas.py
            self.window.destroy()