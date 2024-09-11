import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from backend import *


# Global variables for session management
current_user_id = None
session_start_time = None

# Funciones de interfaz gráfica
def agregar_producto_gui():
    producto_id = entry_producto_id.get()
    nombre = entry_nombre.get()
    descripcion = entry_descripcion.get()
    precio = float(entry_precio.get())
    stock = int(entry_stock.get())

    agregar_producto(producto_id, nombre, descripcion, precio, stock)
    messagebox.showinfo("Información", "Producto agregado exitosamente")

def actualizar_precio_gui():
    producto_id = entry_producto_id.get()
    nuevo_precio = float(entry_precio.get())
    actualizar_precio_producto(producto_id, nuevo_precio)
    messagebox.showinfo("Información", "Precio actualizado exitosamente")

def gestionar_carrito_gui():
    usuario_id = current_user_id
    producto_id = entry_producto_id.get()
    cantidad = int(entry_cantidad.get())
    accion = entry_accion.get()

    gestionar_carrito(usuario_id, producto_id, cantidad, accion)
    messagebox.showinfo("Información", "Carrito gestionado exitosamente")

def registrar_usuario_gui():
    nombre = entry_nombre_usuario.get()
    direccion = entry_direccion.get()
    documento = entry_documento.get()
    usuario_id = registrar_usuario(nombre, direccion, documento)
    if usuario_id:
        messagebox.showinfo("Información", f"Usuario registrado con ID: {usuario_id}")
    else:
        messagebox.showerror("Error", "Usuario ya registrado con este documento")

def iniciar_sesion_gui():
    global current_user_id, session_start_time
    try:
        usuario_id = entry_usuario_id_sesion.get()
        usuario_id = int(usuario_id)
        inicio = iniciar_sesion(usuario_id)
        if inicio:
            current_user_id = usuario_id
            session_start_time = inicio
            messagebox.showinfo("Información", f"Sesión iniciada a las: {inicio}")
            gestionar_carrito_window()
        else:
            messagebox.showerror("Error", "Usuario no encontrado")
    except ValueError:
        messagebox.showerror("Error", "ID de usuario debe ser un número válido")

def finalizar_sesion_gui():
    global current_user_id, session_start_time
    usuario_id = current_user_id
    inicio = session_start_time
    finalizar_sesion(usuario_id, inicio)
    current_user_id = None
    session_start_time = None
    messagebox.showinfo("Información", "Sesión finalizada y actividad registrada")

def mostrar_modo_admin():
    for widget in root.winfo_children():
        widget.destroy()
    modo_admin()

def mostrar_modo_usuario():
    for widget in root.winfo_children():
        widget.destroy()
    modo_usuario_login()

def gestionar_carrito_window():
    for widget in root.winfo_children():
        widget.destroy()
    modo_usuario()

# Configuración de la ventana principal
root = tk.Tk()
root.title("Sistema de Gestión de Pedidos")
root.geometry("400x600")

# Elección de modo
tk.Button(root, text="Modo Admin", command=mostrar_modo_admin).pack()
tk.Button(root, text="Modo Usuario", command=mostrar_modo_usuario).pack()

def modo_admin():
    tk.Label(root, text="ID Producto").pack()
    global entry_producto_id
    entry_producto_id = tk.Entry(root)
    entry_producto_id.pack()

    tk.Label(root, text="Nombre Producto").pack()
    global entry_nombre
    entry_nombre = tk.Entry(root)
    entry_nombre.pack()

    tk.Label(root, text="Descripción Producto").pack()
    global entry_descripcion
    entry_descripcion = tk.Entry(root)
    entry_descripcion.pack()

    tk.Label(root, text="Precio Producto").pack()
    global entry_precio
    entry_precio = tk.Entry(root)
    entry_precio.pack()

    tk.Label(root, text="Stock Producto").pack()
    global entry_stock
    entry_stock = tk.Entry(root)
    entry_stock.pack()

    tk.Button(root, text="Agregar Producto", command=agregar_producto_gui).pack()
    tk.Button(root, text="Actualizar Precio", command=actualizar_precio_gui).pack()

def modo_usuario_login():
    tk.Label(root, text="Nombre Usuario").pack()
    global entry_nombre_usuario
    entry_nombre_usuario = tk.Entry(root)
    entry_nombre_usuario.pack()

    tk.Label(root, text="Dirección Usuario").pack()
    global entry_direccion
    entry_direccion = tk.Entry(root)
    entry_direccion.pack()

    tk.Label(root, text="Documento Usuario").pack()
    global entry_documento
    entry_documento = tk.Entry(root)
    entry_documento.pack()

    tk.Button(root, text="Registrar Usuario", command=registrar_usuario_gui).pack()

    tk.Label(root, text="ID Usuario para Iniciar Sesión").pack()
    global entry_usuario_id_sesion
    entry_usuario_id_sesion = tk.Entry(root)
    entry_usuario_id_sesion.pack()

    tk.Button(root, text="Iniciar Sesión", command=iniciar_sesion_gui).pack()

def modo_usuario():
    tk.Label(root, text="ID Producto").pack()
    global entry_producto_id
    entry_producto_id = tk.Entry(root)
    entry_producto_id.pack()

    tk.Label(root, text="Cantidad Producto").pack()
    global entry_cantidad
    entry_cantidad = tk.Entry(root)
    entry_cantidad.pack()

    tk.Label(root, text="Acción (agregar, eliminar, cambiar)").pack()
    global entry_accion
    entry_accion = tk.Entry(root)
    entry_accion.pack()

    tk.Button(root, text="Gestionar Carrito", command=gestionar_carrito_gui).pack()
    tk.Button(root, text="Finalizar Sesión", command=finalizar_sesion_gui).pack()

# Iniciar la aplicación
root.mainloop()
