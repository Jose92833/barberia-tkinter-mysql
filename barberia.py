import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import mysql.connector
import os

conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="arroyolorenzo04*A",
    database="barberia"
)
cursor = conexion.cursor()

def configurar_estilos():
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TButton", font=("Segoe UI", 11, "bold"), padding=8, relief="flat", background="#1976D2", foreground="white")
    style.map("TButton", background=[("active", "#1565C0")])
    style.configure("TLabel", font=("Segoe UI", 11), background="#ECEFF1", foreground="#212121")
    style.configure("TEntry", font=("Segoe UI", 11), padding=5)
    style.configure("TCombobox", font=("Segoe UI", 11), padding=5)
    style.configure("Treeview", font=("Segoe UI", 10), background="white", fieldbackground="white", rowheight=25)
    style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"), background="#1976D2", foreground="white")

def login():
    usuario = entry_user.get()
    contrasena = entry_pass.get()
    if usuario and contrasena:
        cursor.execute("SELECT * FROM usuarios WHERE username=%s AND password=%s", (usuario, contrasena))
        result = cursor.fetchone()
        if result:
            messagebox.showinfo("Éxito", f"Bienvenido {usuario}")
            abrir_menu()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")
    else:
        messagebox.showwarning("Error", "Debe llenar todos los campos")

def abrir_menu():
    login_win.destroy()
    menu_win = tk.Tk()
    menu_win.title("Barbería El Mapache Bigotón - Menú Principal")
    menu_win.geometry("500x450")
    menu_win.configure(bg="#ECEFF1")
    lbl_title = tk.Label(menu_win, text="Menú Principal", font=("Segoe UI", 20, "bold"), bg="#ECEFF1", fg="#0D47A1")
    lbl_title.pack(pady=20)
    ttk.Button(menu_win, text="😎 Clientes", command=abrir_clientes, width=30).pack(pady=12)
    ttk.Button(menu_win, text="💈 Servicios", command=abrir_servicios, width=30).pack(pady=12)
    ttk.Button(menu_win, text="✂️ Cortes", command=abrir_cortes, width=30).pack(pady=12)
    ttk.Button(menu_win, text="📅 Citas", command=abrir_citas, width=30).pack(pady=12)
    menu_win.mainloop()

def abrir_clientes():
    win = tk.Toplevel()
    win.title("Gestión de Clientes")
    win.configure(bg="#ECEFF1")
    ttk.Label(win, text="Nombre:").grid(row=0, column=0, padx=5, pady=5)
    entry_nombre = ttk.Entry(win)
    entry_nombre.grid(row=0, column=1, padx=5, pady=5)
    ttk.Label(win, text="Teléfono:").grid(row=1, column=0, padx=5, pady=5)
    entry_telefono = ttk.Entry(win)
    entry_telefono.grid(row=1, column=1, padx=5, pady=5)

    def agregar_cliente():
        nombre = entry_nombre.get()
        telefono = entry_telefono.get()
        if nombre and telefono:
            cursor.execute("INSERT INTO clientes (nombre, telefono) VALUES (%s, %s)", (nombre, telefono))
            conexion.commit()
            cargar_clientes()

    def actualizar_cliente():
        selected = tree.selection()
        if selected:
            cliente_id = tree.item(selected[0])['values'][0]
            nombre = entry_nombre.get()
            telefono = entry_telefono.get()
            if nombre and telefono:
                cursor.execute("UPDATE clientes SET nombre=%s, telefono=%s WHERE id=%s", (nombre, telefono, cliente_id))
                conexion.commit()
                cargar_clientes()

    def eliminar_cliente():
        selected = tree.selection()
        if selected:
            cliente_id = tree.item(selected[0])['values'][0]
            cursor.execute("DELETE FROM clientes WHERE id=%s", (cliente_id,))
            conexion.commit()
            cargar_clientes()

    ttk.Button(win, text="Agregar", command=agregar_cliente).grid(row=2, column=0, pady=10)
    ttk.Button(win, text="Actualizar", command=actualizar_cliente).grid(row=2, column=1, pady=10)
    ttk.Button(win, text="Eliminar", command=eliminar_cliente).grid(row=2, column=2, pady=10)

    tree = ttk.Treeview(win, columns=("ID", "Nombre", "Teléfono"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Nombre", text="Nombre")
    tree.heading("Teléfono", text="Teléfono")
    tree.grid(row=3, column=0, columnspan=3, padx=5, pady=10)

    def cargar_clientes():
        for row in tree.get_children():
            tree.delete(row)
        cursor.execute("SELECT * FROM clientes")
        for row in cursor.fetchall():
            tree.insert("", tk.END, values=row)

    def seleccionar_cliente(event):
        selected = tree.selection()
        if selected:
            item = tree.item(selected[0])
            entry_nombre.delete(0, tk.END)
            entry_nombre.insert(0, item['values'][1])
            entry_telefono.delete(0, tk.END)
            entry_telefono.insert(0, item['values'][2])

    tree.bind("<<TreeviewSelect>>", seleccionar_cliente)
    cargar_clientes()

def abrir_servicios():
    win = tk.Toplevel()
    win.title("Gestión de Servicios")
    win.configure(bg="#344149")
    ttk.Label(win, text="Descripción:").grid(row=0, column=0, padx=5, pady=5)
    entry_servicio = ttk.Entry(win)
    entry_servicio.grid(row=0, column=1, padx=5, pady=5)
    ttk.Label(win, text="Costo:").grid(row=1, column=0, padx=5, pady=5)
    entry_costo = ttk.Entry(win)
    entry_costo.grid(row=1, column=1, padx=5, pady=5)

    def agregar_servicio():
        descripcion = entry_servicio.get()
        costo = entry_costo.get()
        if descripcion and costo:
            cursor.execute("INSERT INTO servicios (descripcion, costo) VALUES (%s, %s)", (descripcion, costo))
            conexion.commit()
            cargar_servicios()

    def actualizar_servicio():
        selected = tree.selection()
        if selected:
            servicio_id = tree.item(selected[0])['values'][0]
            descripcion = entry_servicio.get()
            costo = entry_costo.get()
            if descripcion and costo:
                cursor.execute("UPDATE servicios SET descripcion=%s, costo=%s WHERE id=%s", (descripcion, costo, servicio_id))
                conexion.commit()
                cargar_servicios()

    def eliminar_servicio():
        selected = tree.selection()
        if selected:
            servicio_id = tree.item(selected[0])['values'][0]
            cursor.execute("DELETE FROM servicios WHERE id=%s", (servicio_id,))
            conexion.commit()
            cargar_servicios()

    ttk.Button(win, text="Agregar", command=agregar_servicio).grid(row=2, column=0, pady=10)
    ttk.Button(win, text="Actualizar", command=actualizar_servicio).grid(row=2, column=1, pady=10)
    ttk.Button(win, text="Eliminar", command=eliminar_servicio).grid(row=2, column=2, pady=10)

    tree = ttk.Treeview(win, columns=("ID", "Descripción", "Costo"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Descripción", text="Descripción")
    tree.heading("Costo", text="Costo")
    tree.grid(row=3, column=0, columnspan=3, padx=5, pady=10)

    def cargar_servicios():
        for row in tree.get_children():
            tree.delete(row)
        cursor.execute("SELECT * FROM servicios")
        for row in cursor.fetchall():
            tree.insert("", tk.END, values=row)

    def seleccionar_servicio(event):
        selected = tree.selection()
        if selected:
            item = tree.item(selected[0])
            entry_servicio.delete(0, tk.END)
            entry_servicio.insert(0, item['values'][1])
            entry_costo.delete(0, tk.END)
            entry_costo.insert(0, item['values'][2])

    tree.bind("<<TreeviewSelect>>", seleccionar_servicio)
    cargar_servicios()

def abrir_cortes():
    win = tk.Toplevel()
    win.title("Catálogo de Cortes")
    win.configure(bg="#ECEFF1")

    ttk.Label(win, text="Nombre del Corte:").grid(row=0, column=0, padx=5, pady=5)
    entry_corte = ttk.Entry(win)
    entry_corte.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(win, text="Precio:").grid(row=1, column=0, padx=5, pady=5)
    entry_precio = ttk.Entry(win)
    entry_precio.grid(row=1, column=1, padx=5, pady=5)

    img_label = tk.Label(win, bg="#ECEFF1")
    img_label.grid(row=0, column=2, rowspan=3, padx=10, pady=5)
    img_path_var = tk.StringVar()

    def seleccionar_imagen():
        path = filedialog.askopenfilename(filetypes=[("Archivos de imagen", "*.jpg *.png *.jpeg")])
        if path:
            img_path_var.set(path)
            img = Image.open(path).resize((100,100))
            img = ImageTk.PhotoImage(img)
            img_label.config(image=img)
            img_label.image = img

    ttk.Button(win, text="Seleccionar Foto", command=seleccionar_imagen).grid(row=2, column=1, pady=5)

    def agregar_corte():
        nombre = entry_corte.get()
        precio = entry_precio.get()
        foto = img_path_var.get()
        if nombre and precio and foto:
            cursor.execute("INSERT INTO cortes (nombre, precio, foto) VALUES (%s, %s, %s)", (nombre, precio, foto))
            conexion.commit()
            cargar_cortes()

    def actualizar_corte():
        selected = tree.selection()
        if selected:
            corte_id = tree.item(selected[0])['values'][0]
            nombre = entry_corte.get()
            precio = entry_precio.get()
            foto = img_path_var.get()
            if nombre and precio and foto:
                cursor.execute("UPDATE cortes SET nombre=%s, precio=%s, foto=%s WHERE id=%s", (nombre, precio, foto, corte_id))
                conexion.commit()
                cargar_cortes()

    def eliminar_corte():
        selected = tree.selection()
        if selected:
            corte_id = tree.item(selected[0])['values'][0]
            cursor.execute("DELETE FROM cortes WHERE id=%s", (corte_id,))
            conexion.commit()
            cargar_cortes()

    ttk.Button(win, text="Agregar", command=agregar_corte).grid(row=3, column=0, pady=10)
    ttk.Button(win, text="Actualizar", command=actualizar_corte).grid(row=3, column=1, pady=10)
    ttk.Button(win, text="Eliminar", command=eliminar_corte).grid(row=3, column=2, pady=10)

    tree = ttk.Treeview(win, columns=("ID", "Nombre", "Precio", "Foto"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Nombre", text="Nombre")
    tree.heading("Precio", text="Precio")
    tree.heading("Foto", text="Foto")
    tree.grid(row=4, column=0, columnspan=3, padx=5, pady=10)

    def cargar_cortes():
        for row in tree.get_children():
            tree.delete(row)
        cursor.execute("SELECT * FROM cortes")
        for row in cursor.fetchall():
            tree.insert("", tk.END, values=row)

    def seleccionar_corte(event):
        selected = tree.selection()
        if selected:
            item = tree.item(selected[0])
            entry_corte.delete(0, tk.END)
            entry_corte.insert(0, item['values'][1])
            entry_precio.delete(0, tk.END)
            entry_precio.insert(0, item['values'][2])
            foto_path = item['values'][3]
            img_path_var.set(foto_path)
            if foto_path and os.path.exists(foto_path):
                img = Image.open(foto_path).resize((100,100))
                img = ImageTk.PhotoImage(img)
                img_label.config(image=img)
                img_label.image = img

    tree.bind("<<TreeviewSelect>>", seleccionar_corte)
    cargar_cortes()

def abrir_citas():
    win = tk.Toplevel()
    win.title("Gestión de Citas")
    win.configure(bg="#ECEFF1")

    ttk.Label(win, text="Cliente:").grid(row=0, column=0, padx=5, pady=5)
    combo_cliente = ttk.Combobox(win)
    combo_cliente.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(win, text="Servicio:").grid(row=1, column=0, padx=5, pady=5)
    combo_servicio = ttk.Combobox(win)
    combo_servicio.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(win, text="Fecha (aaaa-mm-dd):").grid(row=2, column=0, padx=5, pady=5)
    entry_fecha = ttk.Entry(win)
    entry_fecha.grid(row=2, column=1, padx=5, pady=5)

    ttk.Label(win, text="Hora (hh:mm:ss):").grid(row=3, column=0, padx=5, pady=5)
    entry_hora = ttk.Entry(win)
    entry_hora.grid(row=3, column=1, padx=5, pady=5)

    def agendar_cita():
        cliente = combo_cliente.get()
        servicio = combo_servicio.get()
        fecha = entry_fecha.get()
        hora = entry_hora.get()
        if cliente and servicio and fecha and hora:
            cursor.execute("SELECT id FROM clientes WHERE nombre=%s", (cliente,))
            cliente_id = cursor.fetchone()[0]
            cursor.execute("SELECT id FROM servicios WHERE descripcion=%s", (servicio,))
            servicio_id = cursor.fetchone()[0]
            cursor.execute("INSERT INTO citas (cliente_id, servicio_id, fecha, hora) VALUES (%s,%s,%s,%s)", (cliente_id, servicio_id, fecha, hora))
            conexion.commit()
            cargar_citas()

    def eliminar_cita():
        selected = tree.selection()
        if selected:
            cita_id = tree.item(selected[0])['values'][0]
            cursor.execute("DELETE FROM citas WHERE id=%s", (cita_id,))
            conexion.commit()
            cargar_citas()

    def actualizar_cita():
        selected = tree.selection()
        if selected:
            cita_id = tree.item(selected[0])['values'][0]
            cliente = combo_cliente.get()
            servicio = combo_servicio.get()
            fecha = entry_fecha.get()
            hora = entry_hora.get()
            cursor.execute("SELECT id FROM clientes WHERE nombre=%s", (cliente,))
            cliente_id = cursor.fetchone()[0]
            cursor.execute("SELECT id FROM servicios WHERE descripcion=%s", (servicio,))
            servicio_id = cursor.fetchone()[0]
            cursor.execute("UPDATE citas SET cliente_id=%s, servicio_id=%s, fecha=%s, hora=%s WHERE id=%s",
                           (cliente_id, servicio_id, fecha, hora, cita_id))
            conexion.commit()
            cargar_citas()

    ttk.Button(win, text="Agendar", command=agendar_cita).grid(row=4, column=0, pady=10)
    ttk.Button(win, text="Actualizar", command=actualizar_cita).grid(row=4, column=1, pady=10)
    ttk.Button(win, text="Eliminar", command=eliminar_cita).grid(row=4, column=2, pady=10)

    tree = ttk.Treeview(win, columns=("ID", "Cliente", "Servicio", "Fecha", "Hora"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Cliente", text="Cliente")
    tree.heading("Servicio", text="Servicio")
    tree.heading("Fecha", text="Fecha")
    tree.heading("Hora", text="Hora")
    tree.grid(row=5, column=0, columnspan=3, padx=5, pady=10)

    def cargar_citas():
        for row in tree.get_children():
            tree.delete(row)
        cursor.execute("""
            SELECT c.id, cl.nombre, s.descripcion, c.fecha, c.hora
            FROM citas c
            JOIN clientes cl ON c.cliente_id = cl.id
            JOIN servicios s ON c.servicio_id = s.id
        """)
        for row in cursor.fetchall():
            tree.insert("", tk.END, values=row)

    def seleccionar_cita(event):
        selected = tree.selection()
        if selected:
            item = tree.item(selected[0])
            combo_cliente.set(item['values'][1])
            combo_servicio.set(item['values'][2])
            entry_fecha.delete(0, tk.END)
            entry_fecha.insert(0, item['values'][3])
            entry_hora.delete(0, tk.END)
            entry_hora.insert(0, item['values'][4])

    tree.bind("<<TreeviewSelect>>", seleccionar_cita)
    cursor.execute("SELECT nombre FROM clientes")
    combo_cliente["values"] = [row[0] for row in cursor.fetchall()]
    cursor.execute("SELECT descripcion FROM servicios")
    combo_servicio["values"] = [row[0] for row in cursor.fetchall()]
    cargar_citas()

login_win = tk.Tk()
login_win.title("Login - Barbería El Mapache Bigotón")
login_win.geometry("380x250")
login_win.configure(bg="#ECEFF1")
configurar_estilos()
tk.Label(login_win, text="🔑 Iniciar Sesión", font=("Segoe UI", 18, "bold"), bg="#ECEFF1", fg="#0D47A1").pack(pady=15)
ttk.Label(login_win, text="Usuario:").pack()
entry_user = ttk.Entry(login_win)
entry_user.pack(pady=5)
ttk.Label(login_win, text="Contraseña:").pack()
entry_pass = ttk.Entry(login_win, show="*")
entry_pass.pack(pady=5)
ttk.Button(login_win, text="Ingresar", command=login).pack(pady=20)
login_win.mainloop()
