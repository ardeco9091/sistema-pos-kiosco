# main.py
import tkinter as tk
from tkinter import messagebox
import sqlite3
from config import DB_NAME
from ventas import PuntoDeVenta

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ingreso al Sistema")
        self.root.geometry("400x300")
        self.root.configure(bg="#333")

        frame = tk.Frame(root, bg="#eee", bd=5)
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        tk.Label(frame, text="Usuario:", font=("Arial", 12)).pack(pady=5)
        self.entry_user = tk.Entry(frame, font=("Arial", 12))
        self.entry_user.pack(pady=5)
        self.entry_user.focus()

        tk.Label(frame, text="Contraseña:", font=("Arial", 12)).pack(pady=5)
        self.entry_pass = tk.Entry(frame, font=("Arial", 12), show="*")
        self.entry_pass.pack(pady=5)
        self.entry_pass.bind('<Return>', self.validar_login)

        btn_ingresar = tk.Button(frame, text="INGRESAR", bg="#2E7D32", fg="white", font=("Arial", 12, "bold"), command=self.validar_login)
        btn_ingresar.pack(pady=20, fill=tk.X)

    def validar_login(self, event=None):
        usuario = self.entry_user.get()
        clave = self.entry_pass.get()

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, rol FROM usuarios WHERE nombre=? AND clave=? AND activo=1", (usuario, clave))
        user_data = cursor.fetchone()
        conn.close()

        if user_data:
            self.root.destroy()
            root_pos = tk.Tk()
            app = PuntoDeVenta(root_pos, user_data)
            root_pos.mainloop()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")

if __name__ == "__main__":
    # Verificación rápida de la DB
    import os
    if not os.path.exists(DB_NAME):
        print(f"ATENCIÓN: No se encontró {DB_NAME}. Asegúrate de ejecutar inicializar_db.py primero.")
    
    root_login = tk.Tk()
    app = LoginApp(root_login)
    root_login.mainloop()