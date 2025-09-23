import os
import re
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import mysql.connector
from mysql.connector import Error
import bcrypt


DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "arroyolorenzo04*A"),  # <-- cambia/usa ENV
    "database": os.getenv("DB_NAME", "barberia"),
    "autocommit": False,
}


NUMERIC_PATTERN = re.compile(r"^\d+(\.\d{1,2})?$")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")     # YYYY-MM-DD
TIME_PATTERN = re.compile(r"^\d{2}:\d{2}:\d{2}$")     # HH:MM:SS

def is_bcrypt_hash(value: str) -> bool:
    return isinstance(value, str) and value.startswith("$2")

def safe_float(text: str):
    if text and NUMERIC_PATTERN.match(text.strip()):
        return float(text)
    return None

def configure_styles():
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure("TButton", font=("Segoe UI", 11, "bold"), padding=8)
    style.map("TButton",
              relief=[("pressed", "sunken"), ("!pressed", "flat")])
    style.configure("TLabel", font=("Segoe UI", 11))
    style.configure("TEntry", font=("Segoe UI", 11), padding=5)
    style.configure("TCombobox", font=("Segoe UI", 11), padding=5)
    style.configure("Treeview", font=("Segoe UI", 10), rowheight=25)
    style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))

def show_info(msg): messagebox.showinfo("Información", msg)
def show_error(msg): messagebox.showerror("Error", msg)
def ask_yes_no(msg): return messagebox.askyesno("Confirmar", msg)


class DB:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self):
        try:
            self.conn = mysql.connector.connect(**DB_CONFIG)
            self.cursor = self.conn.cursor()
        except Error as e:
            show_error(f"No se pudo conectar a la BD: {e}")
            raise

    def execute(self, query, params=None, commit=False, many=False):
        try:
            if many:
                self.cursor.executemany(query, params or [])
            else:
                self.cursor.execute(query, params or ())
            if commit:
                self.conn.commit()
        except Error as e:
            if self.conn:
                self.conn.rollback()
            show_error(f"Error de BD: {e}")
            raise

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    def close(self):
        try:
            if self.cursor: self.cursor.close()
            if self.conn: self.conn.close()
        except:
            pass

z
class LoginView(ttk.Frame):
    def __init__(self, master, db: DB, on_success):
        super().__init__(master, padding=20)
        self.db = db
        self.on_success = on_success

        tk.Label(self, text="🔑 Iniciar Sesión",
                 font=("Segoe UI", 18, "bold")).pack(pady=10)

        ttk.Label(self, text="Usuario:").pack(anchor="w")
        self.entry_user = ttk.Entry(self, width=30)
        self.entry_user.pack(pady=5)

        ttk.Label(self, text="Contraseña:").pack(anchor="w")
        self.entry_pass = ttk.Entry(self, show="*", width=30)
        self.entry_pass.pack(pady=5)

        ttk.Button(self, text="Ingresar", command=self.login).pack(pady=15)

    def login(self):
        usuario = self.entry_user.get().strip()
        contrasena = self.entry_pass.get()

        if not usuario or not contrasena:
            show_error("Debe llenar todos los campos.")
            return

        try:
            self.db.execute("SELECT username, password FROM usuarios WHERE username=%s", (usuario,))
            row = self.db.fetchone()
            if not row:
                show_error("Usuario o contraseña incorrectos.")
                return

            _, stored = row
            ok = False
            if is_bcrypt_hash(stored):
                try:
                    ok = bcrypt.checkpw(contrasena.encode("utf-8"), stored.encode("utf-8"))
                except Exception:
                    ok = False
            else:
                ok = (contrasena == stored)

            if ok:
                show_info(f"Bienvenido {usuario}")
                self.on_success()
            else:
                show_error("Usuario o contraseña incorrectos.")
        except Exception:
            pass

class MenuView(tk.Toplevel):
    def __init__(self, master, db: DB):
        super().__init__(master)
        self.db = db
        self.title("Barbería El Mapache Bigotón - Menú Principal")
        self.geometry("460x420")
        self.configure(padx=20, pady=20)

        tk.Label(self, text="Menú Principal", font=("Segoe UI", 20, "bold")).pack(pady=12)
        ttk.Button(self, text="😎 Clientes", command=self.open_clientes, width=30).pack(pady=8)
        ttk.Button(self, text="💈 Servicios", command=self.open_servicios, width=30).pack(pady=8)
        ttk.Button(self, text="✂️ Cortes", command=self.open_cortes, width=30).pack(pady=8)
        ttk.Button(self, text="📅 Citas", command=self.open_citas, width=30).pack(pady=8)

    def open_clientes(self): ClientesView(self, self.db)
    def open_servicios(self): ServiciosView(self, self.db)
    def open_cortes(self): CortesView(self, self.db)
    def open_citas(self): CitasView(self, self.db)

class BaseCRUDWindow(tk.Toplevel):
    def __init__(self, master, db: DB, title):
        super().__init__(master)
        self.db = db
        self.title(title)
        self.configure(padx=16, pady=16)
        self.grid_columnconfigure(1, weight=1)

        # Tree + scrollbar
        self.tree = None
        self._add_tree_area()

    def _add_tree_area(self):
        frame = ttk.Frame(self)
        frame.grid(row=99, column=0, columnspan=3, sticky="nsew", pady=(10,0))
        self.grid_rowconfigure(99, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

        self.tree = ttk.Treeview(frame, show="headings", selectmode="browse")
        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscroll=vsb.set, xscroll=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

class ClientesView(BaseCRUDWindow):
    def __init__(self, master, db: DB):
        super().__init__(master, db, "Gestión de Clientes")

        ttk.Label(self, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_nombre = ttk.Entry(self)
        self.entry_nombre.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(self, text="Teléfono:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_telefono = ttk.Entry(self)
        self.entry_telefono.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Button(self, text="Agregar", command=self.agregar).grid(row=2, column=0, pady=8)
        ttk.Button(self, text="Actualizar", command=self.actualizar).grid(row=2, column=1, pady=8)
        ttk.Button(self, text="Eliminar", command=self.eliminar).grid(row=2, column=2, pady=8)

        self.tree["columns"] = ("ID", "Nombre", "Teléfono")
        for col, w in [("ID", 60), ("Nombre", 180), ("Teléfono", 140)]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        self.cargar()

    def cargar(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        try:
            self.db.execute("SELECT id, nombre, telefono FROM clientes")
            for row in self.db.fetchall():
                self.tree.insert("", tk.END, values=row)
        except Exception:
            pass

    def on_select(self, _):
        sel = self.tree.selection()
        if not sel: return
        v = self.tree.item(sel[0])["values"]
        self.entry_nombre.delete(0, tk.END)
        self.entry_nombre.insert(0, v[1])
        self.entry_telefono.delete(0, tk.END)
        self.entry_telefono.insert(0, v[2])

    def agregar(self):
        nombre = self.entry_nombre.get().strip()
        tel = self.entry_telefono.get().strip()
        if not nombre or not tel:
            show_error("Nombre y teléfono son obligatorios.")
            return
        try:
            self.db.execute("INSERT INTO clientes (nombre, telefono) VALUES (%s, %s)", (nombre, tel), commit=True)
            show_info("Cliente agregado.")
            self.cargar()
        except Exception:
            pass

    def actualizar(self):
        sel = self.tree.selection()
        if not sel:
            show_error("Seleccione un cliente.")
            return
        cid = self.tree.item(sel[0])["values"][0]
        nombre = self.entry_nombre.get().strip()
        tel = self.entry_telefono.get().strip()
        if not nombre or not tel:
            show_error("Nombre y teléfono son obligatorios.")
            return
        try:
            self.db.execute("UPDATE clientes SET nombre=%s, telefono=%s WHERE id=%s", (nombre, tel, cid), commit=True)
            show_info("Cliente actualizado.")
            self.cargar()
        except Exception:
            pass

    def eliminar(self):
        sel = self.tree.selection()
        if not sel:
            show_error("Seleccione un cliente.")
            return
        cid = self.tree.item(sel[0])["values"][0]
        if not ask_yes_no("¿Eliminar cliente seleccionado?"):
            return
        try:
            self.db.execute("DELETE FROM clientes WHERE id=%s", (cid,), commit=True)
            show_info("Cliente eliminado.")
            self.cargar()
        except Exception:
            pass

class ServiciosView(BaseCRUDWindow):
    def __init__(self, master, db: DB):
        super().__init__(master, db, "Gestión de Servicios")

        ttk.Label(self, text="Descripción:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_desc = ttk.Entry(self)
        self.entry_desc.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(self, text="Costo:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_costo = ttk.Entry(self)
        self.entry_costo.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Button(self, text="Agregar", command=self.agregar).grid(row=2, column=0, pady=8)
        ttk.Button(self, text="Actualizar", command=self.actualizar).grid(row=2, column=1, pady=8)
        ttk.Button(self, text="Eliminar", command=self.eliminar).grid(row=2, column=2, pady=8)

        self.tree["columns"] = ("ID", "Descripción", "Costo")
        for col, w in [("ID", 60), ("Descripción", 200), ("Costo", 100)]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        self.cargar()

    def cargar(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        try:
            self.db.execute("SELECT id, descripcion, costo FROM servicios")
            for row in self.db.fetchall():
                self.tree.insert("", tk.END, values=row)
        except Exception:
            pass

    def on_select(self, _):
        sel = self.tree.selection()
        if not sel: return
        v = self.tree.item(sel[0])["values"]
        self.entry_desc.delete(0, tk.END)
        self.entry_desc.insert(0, v[1])
        self.entry_costo.delete(0, tk.END)
        self.entry_costo.insert(0, v[2])

    def agregar(self):
        desc = self.entry_desc.get().strip()
        costo = self.entry_costo.get().strip()
        val = safe_float(costo)
        if not desc or val is None:
            show_error("Descripción obligatoria y costo numérico válido (ej. 120 o 120.50).")
            return
        try:
            self.db.execute("INSERT INTO servicios (descripcion, costo) VALUES (%s, %s)", (desc, val), commit=True)
            show_info("Servicio agregado.")
            self.cargar()
        except Exception:
            pass

    def actualizar(self):
        sel = self.tree.selection()
        if not sel:
            show_error("Seleccione un servicio.")
            return
        sid = self.tree.item(sel[0])["values"][0]
        desc = self.entry_desc.get().strip()
        costo = self.entry_costo.get().strip()
        val = safe_float(costo)
        if not desc or val is None:
            show_error("Descripción obligatoria y costo numérico válido.")
            return
        try:
            self.db.execute("UPDATE servicios SET descripcion=%s, costo=%s WHERE id=%s", (desc, val, sid), commit=True)
            show_info("Servicio actualizado.")
            self.cargar()
        except Exception:
            pass

    def eliminar(self):
        sel = self.tree.selection()
        if not sel:
            show_error("Seleccione un servicio.")
            return
        sid = self.tree.item(sel[0])["values"][0]
        if not ask_yes_no("¿Eliminar servicio seleccionado?"):
            return
        try:
            self.db.execute("DELETE FROM servicios WHERE id=%s", (sid,), commit=True)
            show_info("Servicio eliminado.")
            self.cargar()
        except Exception:
            pass

class CortesView(BaseCRUDWindow):
    def __init__(self, master, db: DB):
        super().__init__(master, db, "Catálogo de Cortes")

        ttk.Label(self, text="Nombre del Corte:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_nombre = ttk.Entry(self)
        self.entry_nombre.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(self, text="Precio:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_precio = ttk.Entry(self)
        self.entry_precio.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.img_label = tk.Label(self)
        self.img_label.grid(row=0, column=2, rowspan=3, padx=10, pady=5)
        self.img_path = tk.StringVar()

        ttk.Button(self, text="Seleccionar Foto", command=self.seleccionar_imagen).grid(row=2, column=1, pady=5, sticky="w")

        ttk.Button(self, text="Agregar", command=self.agregar).grid(row=3, column=0, pady=8)
        ttk.Button(self, text="Actualizar", command=self.actualizar).grid(row=3, column=1, pady=8)
        ttk.Button(self, text="Eliminar", command=self.eliminar).grid(row=3, column=2, pady=8)

        self.tree["columns"] = ("ID", "Nombre", "Precio", "Foto")
        for col, w in [("ID", 60), ("Nombre", 160), ("Precio", 100), ("Foto", 240)]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        self.cargar()

    def seleccionar_imagen(self):
        path = filedialog.askopenfilename(filetypes=[("Imágenes", "*.jpg *.jpeg *.png")])
        if path:
            self.img_path.set(path)
            try:
                img = Image.open(path).resize((120, 120))
                self.img_label.image = ImageTk.PhotoImage(img)
                self.img_label.config(image=self.img_label.image)
            except Exception as e:
                show_error(f"No se pudo cargar la imagen: {e}")

    def cargar(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        try:
            self.db.execute("SELECT id, nombre, precio, foto FROM cortes")
            for row in self.db.fetchall():
                self.tree.insert("", tk.END, values=row)
        except Exception:
            pass

    def on_select(self, _):
        sel = self.tree.selection()
        if not sel: return
        v = self.tree.item(sel[0])["values"]
        self.entry_nombre.delete(0, tk.END)
        self.entry_nombre.insert(0, v[1])
        self.entry_precio.delete(0, tk.END)
        self.entry_precio.insert(0, v[2])
        foto_path = v[3]
        self.img_path.set(foto_path)
        if foto_path and os.path.exists(foto_path):
            try:
                img = Image.open(foto_path).resize((120, 120))
                self.img_label.image = ImageTk.PhotoImage(img)
                self.img_label.config(image=self.img_label.image)
            except Exception:
                self.img_label.config(image="")
                self.img_label.image = None
        else:
            self.img_label.config(image="")
            self.img_label.image = None

    def agregar(self):
        nombre = self.entry_nombre.get().strip()
        precio = self.entry_precio.get().strip()
        val = safe_float(precio)
        foto = self.img_path.get().strip()
        if not nombre or val is None or not foto:
            show_error("Nombre, precio numérico y foto son obligatorios.")
            return
        try:
            self.db.execute("INSERT INTO cortes (nombre, precio, foto) VALUES (%s, %s, %s)", (nombre, val, foto), commit=True)
            show_info("Corte agregado.")
            self.cargar()
        except Exception:
            pass

    def actualizar(self):
        sel = self.tree.selection()
        if not sel:
            show_error("Seleccione un corte.")
            return
        cid = self.tree.item(sel[0])["values"][0]
        nombre = self.entry_nombre.get().strip()
        precio = self.entry_precio.get().strip()
        val = safe_float(precio)
        foto = self.img_path.get().strip()
        if not nombre or val is None or not foto:
            show_error("Nombre, precio numérico y foto son obligatorios.")
            return
        try:
            self.db.execute("UPDATE cortes SET nombre=%s, precio=%s, foto=%s WHERE id=%s", (nombre, val, foto, cid), commit=True)
            show_info("Corte actualizado.")
            self.cargar()
        except Exception:
            pass

    def eliminar(self):
        sel = self.tree.selection()
        if not sel:
            show_error("Seleccione un corte.")
            return
        cid = self.tree.item(sel[0])["values"][0]
        if not ask_yes_no("¿Eliminar corte seleccionado?"):
            return
        try:
            self.db.execute("DELETE FROM cortes WHERE id=%s", (cid,), commit=True)
            show_info("Corte eliminado.")
            self.cargar()
        except Exception:
            pass

class CitasView(BaseCRUDWindow):
    def __init__(self, master, db: DB):
        super().__init__(master, db, "Gestión de Citas")

        ttk.Label(self, text="Cliente:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.combo_cliente = ttk.Combobox(self, state="readonly")
        self.combo_cliente.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(self, text="Servicio:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.combo_servicio = ttk.Combobox(self, state="readonly")
        self.combo_servicio.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(self, text="Fecha (aaaa-mm-dd):").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.entry_fecha = ttk.Entry(self)
        self.entry_fecha.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(self, text="Hora (hh:mm:ss):").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.entry_hora = ttk.Entry(self)
        self.entry_hora.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        ttk.Button(self, text="Agendar", command=self.agendar).grid(row=4, column=0, pady=8)
        ttk.Button(self, text="Actualizar", command=self.actualizar).grid(row=4, column=1, pady=8)
        ttk.Button(self, text="Eliminar", command=self.eliminar).grid(row=4, column=2, pady=8)

        self.tree["columns"] = ("ID", "Cliente", "Servicio", "Fecha", "Hora")
        for col, w in [("ID", 60), ("Cliente", 160), ("Servicio", 180), ("Fecha", 100), ("Hora", 90)]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center")
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        self.recargar_combos()
        self.cargar()

    def recargar_combos(self):
        try:
            self.db.execute("SELECT nombre FROM clientes")
            clientes = [r[0] for r in self.db.fetchall()]
            self.combo_cliente["values"] = clientes

            self.db.execute("SELECT descripcion FROM servicios")
            servicios = [r[0] for r in self.db.fetchall()]
            self.combo_servicio["values"] = servicios
        except Exception:
            self.combo_cliente["values"] = []
            self.combo_servicio["values"] = []

    def cargar(self):
        for r in self.tree.get_children():
            self.tree.delete(r)
        try:
            self.db.execute("""
                SELECT c.id, cl.nombre, s.descripcion, c.fecha, c.hora
                FROM citas c
                JOIN clientes cl ON c.cliente_id = cl.id
                JOIN servicios s ON c.servicio_id = s.id
                ORDER BY c.fecha DESC, c.hora DESC
            """)
            for row in self.db.fetchall():
                self.tree.insert("", tk.END, values=row)
        except Exception:
            pass

    def _resolve_cliente_id(self, nombre: str):
        self.db.execute("SELECT id FROM clientes WHERE nombre=%s", (nombre,))
        row = self.db.fetchone()
        return row[0] if row else None

    def _resolve_servicio_id(self, desc: str):
        self.db.execute("SELECT id FROM servicios WHERE descripcion=%s", (desc,))
        row = self.db.fetchone()
        return row[0] if row else None

    def agendar(self):
        cliente = self.combo_cliente.get().strip()
        servicio = self.combo_servicio.get().strip()
        fecha = self.entry_fecha.get().strip()
        hora = self.entry_hora.get().strip()

        if not cliente or not servicio or not DATE_PATTERN.match(fecha) or not TIME_PATTERN.match(hora):
            show_error("Complete Cliente, Servicio, Fecha (AAAA-MM-DD) y Hora (HH:MM:SS).")
            return

        try:
            cid = self._resolve_cliente_id(cliente)
            sid = self._resolve_servicio_id(servicio)
            if not cid or not sid:
                show_error("Cliente o servicio inválido.")
                return
            self.db.execute(
                "INSERT INTO citas (cliente_id, servicio_id, fecha, hora) VALUES (%s, %s, %s, %s)",
                (cid, sid, fecha, hora), commit=True
            )
            show_info("Cita agendada.")
            self.cargar()
        except Exception:
            pass

    def actualizar(self):
        sel = self.tree.selection()
        if not sel:
            show_error("Seleccione una cita.")
            return
        cita_id = self.tree.item(sel[0])["values"][0]
        cliente = self.combo_cliente.get().strip()
        servicio = self.combo_servicio.get().strip()
        fecha = self.entry_fecha.get().strip()
        hora = self.entry_hora.get().strip()

        if not cliente or not servicio or not DATE_PATTERN.match(fecha) or not TIME_PATTERN.match(hora):
            show_error("Complete Cliente, Servicio, Fecha (AAAA-MM-DD) y Hora (HH:MM:SS).")
            return

        try:
            cid = self._resolve_cliente_id(cliente)
            sid = self._resolve_servicio_id(servicio)
            if not cid or not sid:
                show_error("Cliente o servicio inválido.")
                return
            self.db.execute(
                "UPDATE citas SET cliente_id=%s, servicio_id=%s, fecha=%s, hora=%s WHERE id=%s",
                (cid, sid, fecha, hora, cita_id), commit=True
            )
            show_info("Cita actualizada.")
            self.cargar()
        except Exception:
            pass

    def eliminar(self):
        sel = self.tree.selection()
        if not sel:
            show_error("Seleccione una cita.")
            return
        cita_id = self.tree.item(sel[0])["values"][0]
        if not ask_yes_no("¿Eliminar cita seleccionada?"):
            return
        try:
            self.db.execute("DELETE FROM citas WHERE id=%s", (cita_id,), commit=True)
            show_info("Cita eliminada.")
            self.cargar()
        except Exception:
            pass

    def on_select(self, _):
        sel = self.tree.selection()
        if not sel: return
        v = self.tree.item(sel[0])["values"]
        self.combo_cliente.set(v[1])
        self.combo_servicio.set(v[2])
        self.entry_fecha.delete(0, tk.END); self.entry_fecha.insert(0, v[3])
        self.entry_hora.delete(0, tk.END); self.entry_hora.insert(0, v[4])


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Login - Barbería El Mapache Bigotón")
        self.geometry("420x260")
        configure_styles()

        self.db = DB()

        self.login_frame = LoginView(self, self.db, on_success=self.open_menu)
        self.login_frame.pack(expand=True, fill="both")

    def open_menu(self):
        # Destruye el frame de login y abre el menú como Toplevel
        self.login_frame.destroy()
        MenuView(self, self.db)

    def on_closing(self):
        try:
            self.db.close()
        finally:
            self.destroy()

if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
