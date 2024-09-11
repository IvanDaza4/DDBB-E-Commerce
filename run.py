import tkinter as tk
from tkinter import font, messagebox, simpledialog
from datetime import datetime
import redis
import customtkinter as ctk 

from backend import (
    registrar_usuario_backend,
    iniciar_sesion_backend,
    finalizar_sesion_backend,
    agregar_producto_backend,
    actualizar_precio_producto_backend,
    gestionar_carrito,
    convertir_carrito,
    facturar_pedido_backend,
    recuperar_producto,
    registrar_actividad_catalogo,
    obtener_carrito_usuario,
    obtener_id_producto_por_nombre,
    obtener_historial_compras,
    obtener_facturas_pendientes,  # Nueva función para obtener facturas pendientes
    db  # Importar 'db' desde el backend
)

from bson.objectid import ObjectId

# Conexión a Redis
try:
    r = redis.Redis(host='localhost', port=6379, db=0)
    r.ping()
    print("Connected to Redis!")
except redis.ConnectionError as e:
    print(f"Could not connect to Redis: {e}")
    exit(1)

def main():
    global carrito, usuario_id
    carrito = []
    usuario_id = None
    
    # Crear la ventana principal
    root = tk.Tk()
    root.title("Interfaz Figma con Tkinter")
    root.geometry("1000x1000")
    root.configure(bg="#f0f0f0")
    
    # Llamar a la función de pantalla principal
    pantalla_inicio_sesion(root)
    
    # Iniciar el bucle principal de la aplicación
    root.mainloop()

def pantalla_inicio_sesion(root):
    # Limpiar la ventana
    for widget in root.winfo_children():
        widget.destroy()

    # Configuración inicial
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("green")

    # Fuente personalizada
    fuente_titulo = ctk.CTkFont(family='Helvetica', size=28, weight='bold')
    fuente_boton = ctk.CTkFont(family='Helvetica', size=18, weight='bold')
    fuente_texto = ctk.CTkFont(family='Helvetica', size=14)

    # Crear un frame para centrar los widgets
    frame = ctk.CTkFrame(root, fg_color="#f9f9f9", corner_radius=15, width=400, height=500)
    frame.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

    # Crear etiqueta de título
    label_titulo = ctk.CTkLabel(frame, text="Iniciar sesión", font=fuente_titulo)
    label_titulo.pack(pady=(30, 20))

    # Crear enlace de crear cuenta
    def crear_cuenta_click():
        pantalla_registro(root)

    label_crear_cuenta = ctk.CTkLabel(frame, text="¿O crear una cuenta?", font=fuente_texto, text_color="#4caf50", cursor="hand2")
    label_crear_cuenta.pack(pady=(0, 30))
    label_crear_cuenta.bind("<Button-1>", lambda e: crear_cuenta_click())

    # Crear campo de correo electrónico
    entry_correo = ctk.CTkEntry(frame, placeholder_text="Correo electrónico", font=fuente_texto, width=300, height=40)
    entry_correo.pack(pady=(0, 20), padx=20)

    # Crear campo de contraseña
    entry_contrasena = ctk.CTkEntry(frame, placeholder_text="Contraseña", font=fuente_texto, show="*", width=300, height=40)
    entry_contrasena.pack(pady=(0, 30), padx=20)

    # Crear botón de iniciar sesión
    button_login = ctk.CTkButton(frame, text="Iniciar sesión", font=fuente_boton, fg_color="#4caf50", hover_color="#388e3c",
                                 width=300, height=40,
                                 command=lambda: iniciar_sesion(root, entry_correo.get(), entry_contrasena.get()))
    button_login.pack(pady=20)

def iniciar_sesion(root, correo, contrasena):
    global usuario_id, carrito  # Asegúrate de declarar 'carrito' y 'usuario_id' como global

    if correo == "admin" and contrasena == "admin":
        pantalla_administracion(root)
        return
    
    usuario_id = iniciar_sesion_backend(correo, contrasena)
    if usuario_id:
        carrito = obtener_carrito_usuario(usuario_id)  # Recuperar el carrito del usuario
        if carrito:
            respuesta = messagebox.askyesno("Recuperar Carrito", "¿Quieres recuperar el carrito anterior?")
            if respuesta:
                print(f"Carrito recuperado: {carrito}")  # Añadir un mensaje de depuración
            else:
                carrito = []
        else:
            carrito = []
        messagebox.showinfo("Éxito", "Sesión iniciada correctamente.")
        pantalla_catalogo(root)
    else:
        messagebox.showerror("Error", "Correo o contraseña incorrectos.")

def cerrar_sesion(root):
    global usuario_id, carrito
    if usuario_id:
        finalizar_sesion_backend(usuario_id)  # Llamar a la función para finalizar la sesión
    usuario_id = None
    carrito = []
    pantalla_inicio_sesion(root)

def pantalla_registro(root):
    # Limpiar la ventana
    for widget in root.winfo_children():
        widget.destroy()
    
    # Configuración inicial
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("green")

    # Fuente personalizada
    fuente_titulo = ctk.CTkFont(family='Helvetica', size=28, weight='bold')
    fuente_boton = ctk.CTkFont(family='Helvetica', size=18, weight='bold')
    fuente_texto = ctk.CTkFont(family='Helvetica', size=14)

    # Crear un frame para centrar los widgets
    frame = ctk.CTkFrame(root, fg_color="#f9f9f9", corner_radius=15, width=400, height=600)
    frame.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

    # Crear etiqueta de título
    label_titulo = ctk.CTkLabel(frame, text="Registrarse", font=fuente_titulo)
    label_titulo.pack(pady=(30, 10))

    # Crear enlace de iniciar sesión
    def iniciar_sesion_click():
        pantalla_inicio_sesion(root)
    
    label_iniciar_sesion = ctk.CTkLabel(frame, text="¿O iniciar sesión?", font=fuente_texto, text_color="#4caf50", cursor="hand2")
    label_iniciar_sesion.pack(pady=(0, 20))
    label_iniciar_sesion.bind("<Button-1>", lambda e: iniciar_sesion_click())

    # Crear campo de nombre
    entry_nombre = ctk.CTkEntry(frame, placeholder_text="Nombre", font=fuente_texto, width=300, height=40)
    entry_nombre.pack(pady=(0, 10), padx=20)

    # Crear campo de correo electrónico
    entry_correo = ctk.CTkEntry(frame, placeholder_text="Correo electrónico", font=fuente_texto, width=300, height=40)
    entry_correo.pack(pady=(0, 10), padx=20)

    # Crear campo de contraseña
    entry_contrasena = ctk.CTkEntry(frame, placeholder_text="Contraseña", font=fuente_texto, show="*", width=300, height=40)
    entry_contrasena.pack(pady=(0, 10), padx=20)

    # Crear campo de confirmar contraseña
    entry_confirmar_contrasena = ctk.CTkEntry(frame, placeholder_text="Confirmar contraseña", font=fuente_texto, show="*", width=300, height=40)
    entry_confirmar_contrasena.pack(pady=(0, 10), padx=20)
    
    # Crear campo de DNI
    entry_dni = ctk.CTkEntry(frame, placeholder_text="DNI", font=fuente_texto, width=300, height=40)
    entry_dni.pack(pady=(0, 10), padx=20)
    
    # Crear campo de dirección
    entry_direccion = ctk.CTkEntry(frame, placeholder_text="Dirección", font=fuente_texto, width=300, height=40)
    entry_direccion.pack(pady=(0, 20), padx=20)

    # Crear botón de registrarse
    button_registrarse = ctk.CTkButton(frame, text="Registrarse", font=fuente_boton, fg_color="#4caf50", hover_color="#388e3c", width=300, height=40,
                                       command=lambda: registrar_usuario(root, entry_nombre.get(), entry_correo.get(), entry_contrasena.get(), entry_confirmar_contrasena.get(), entry_dni.get(), entry_direccion.get()))
    button_registrarse.pack(pady=20)

def registrar_usuario(root, nombre, correo, contrasena, confirmar_contrasena, dni, direccion):
    if contrasena != confirmar_contrasena:
        messagebox.showerror("Error", "Las contraseñas no coinciden.")
        return

    usuario_id = registrar_usuario_backend(nombre, correo, contrasena, dni, direccion)
    if usuario_id:
        messagebox.showinfo("Registro exitoso", "Usuario registrado correctamente.")
        pantalla_inicio_sesion(root)
    else:
        messagebox.showerror("Error", "El usuario ya está registrado.")

def pantalla_catalogo(root):
    # Limpiar la ventana
    for widget in root.winfo_children():
        widget.destroy()

    # Configuración inicial
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("green")

    # Fuente personalizada
    fuente_titulo = ctk.CTkFont(family='Helvetica', size=24, weight='bold')
    fuente_texto = ctk.CTkFont(family='Helvetica', size=14)

    # Crear navbar
    navbar = ctk.CTkFrame(root, fg_color="#333333", height=50)
    navbar.pack(fill='x')

    # Función para cerrar sesión
    btn_cerrar_sesion = ctk.CTkButton(navbar, text="Cerrar sesión", font=fuente_texto, fg_color="#555555", text_color="white", command=lambda: cerrar_sesion(root))
    btn_cerrar_sesion.pack(side=tk.RIGHT, padx=10, pady=10)

    # Función para mostrar perfil
    def mostrar_perfil():
        pantalla_perfil(root, usuario_id)

    # Crear botón de perfil
    btn_perfil = ctk.CTkButton(navbar, text="Perfil", font=fuente_texto, fg_color="#555555", text_color="white", command=mostrar_perfil)
    btn_perfil.pack(side=tk.RIGHT, padx=10, pady=10)

    # Crear botón de carrito
    btn_carrito = ctk.CTkButton(navbar, text="Carrito", font=fuente_texto, fg_color="#555555", text_color="white", command=lambda: pantalla_carrito(root, carrito))
    btn_carrito.pack(side=tk.RIGHT, padx=10, pady=10)

    # Crear botón de facturas pendientes
    btn_facturas_pendientes = ctk.CTkButton(navbar, text="Facturas Pendientes", font=fuente_texto, fg_color="#555555", text_color="white", command=lambda: pantalla_facturas_pendientes(root))
    btn_facturas_pendientes.pack(side=tk.RIGHT, padx=10, pady=10)

    # Crear un frame para el contenido principal
    frame = ctk.CTkFrame(root, fg_color="#ffffff")
    frame.pack(fill='both', expand=True, padx=10, pady=10)

    # Crear etiqueta de título
    label_titulo = ctk.CTkLabel(frame, text="Catálogo de Productos", font=fuente_titulo)
    label_titulo.pack(pady=(10, 20))

    # Crear un frame para los productos
    frame_productos = ctk.CTkFrame(frame, fg_color="#ffffff")
    frame_productos.pack(pady=(0, 20))

    # Función para crear tarjetas de producto
    def crear_tarjeta_producto(parent, nombre, precio, descripcion, fecha):
        card_frame = ctk.CTkFrame(parent, fg_color="#f9f9f9", corner_radius=10)
        card_frame.pack(side=tk.LEFT, padx=20, pady=10)

        label_nombre = ctk.CTkLabel(card_frame, text=nombre, font=fuente_texto, fg_color="#f9f9f9")
        label_nombre.pack(pady=(10, 5))

        label_precio = ctk.CTkLabel(card_frame, text=f"${precio}", font=fuente_texto, text_color="#333333", fg_color="#f9f9f9")
        label_precio.pack(pady=(0, 5))

        label_descripcion = ctk.CTkLabel(card_frame, text=descripcion, font=fuente_texto, fg_color="#f9f9f9")
        label_descripcion.pack(pady=(0, 5))

        label_fecha = ctk.CTkLabel(card_frame, text=f"Actualizado el {fecha}", font=fuente_texto, text_color="#777777", fg_color="#f9f9f9")
        label_fecha.pack(pady=(0, 10))

        # Botón para agregar al carrito
        button_agregar = ctk.CTkButton(card_frame, text="Agregar al Carrito", font=fuente_texto, fg_color="#4caf50", text_color="white", command=lambda: agregar_al_carrito(nombre, precio))
        button_agregar.pack(pady=(5, 10))

    # Recuperar productos desde Redis
    productos = []
    for key in r.keys():
        producto = recuperar_producto(key)
        producto = {k.decode('utf-8'): v.decode('utf-8') for k, v in producto.items()}
        producto.setdefault('ultima_actualizacion', 'N/A')
        productos.append(producto)

    for producto in productos:
        crear_tarjeta_producto(frame_productos, producto['nombre'], producto['precio'], producto['descripcion'], producto['ultima_actualizacion'])

    # Crear tabla de lista de precios
    frame_lista_precios = ctk.CTkFrame(frame, fg_color="#ffffff")
    frame_lista_precios.pack(pady=(20, 0))

    label_lista_precios = ctk.CTkLabel(frame_lista_precios, text="Lista de Precios", font=fuente_titulo)
    label_lista_precios.pack(pady=(0, 10))

    tabla_precios = ctk.CTkFrame(frame_lista_precios, fg_color="#ffffff")
    tabla_precios.pack()

    # Crear encabezados de tabla
    headers = ["Producto", "Precio", "Fecha de Actualización"]
    for col, header in enumerate(headers):
        label = ctk.CTkLabel(tabla_precios, text=header, font=fuente_texto, fg_color="#4caf50", text_color="white", width=20)
        label.grid(row=0, column=col, padx=5, pady=5, sticky="nsew")

    # Crear filas de tabla
    for idx, producto in enumerate(productos):
        for col, key in enumerate(["nombre", "precio", "ultima_actualizacion"]):
            text = producto[key]
            label = ctk.CTkLabel(tabla_precios, text=text, font=fuente_texto, fg_color="#ffffff", width=20)
            label.grid(row=idx + 1, column=col, padx=5, pady=5, sticky="nsew")

    # Añadir líneas de separación manualmente
    for widget in tabla_precios.winfo_children():
        widget.grid_configure(sticky="ew")

    for row in range(len(productos) + 1):
        tabla_precios.grid_rowconfigure(row, minsize=40)
        for col in range(len(headers)):
            tabla_precios.grid_columnconfigure(col, weight=1, minsize=100)

def pantalla_administracion(root):
    # Limpiar la ventana
    for widget in root.winfo_children():
        widget.destroy()

    # Configuración inicial
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("green")

    # Fuente personalizada
    fuente_titulo = ctk.CTkFont(family='Helvetica', size=24, weight='bold')
    fuente_texto = ctk.CTkFont(family='Helvetica', size=16)

    # Crear navbar
    navbar = ctk.CTkFrame(root, fg_color="#333333", height=50)
    navbar.pack(fill='x')

    # Función para volver a la pantalla de inicio de sesión
    def volver_inicio_sesion():
        pantalla_inicio_sesion(root)

    # Crear botón de volver
    btn_volver = ctk.CTkButton(navbar, text="Volver", font=fuente_texto, fg_color="#555555", text_color="white", command=volver_inicio_sesion)
    btn_volver.pack(side=tk.LEFT, padx=10, pady=10)
    
    def ver_facturas_clientes():
        pantalla_facturas_clientes(root)
    
    btn_facturas = ctk.CTkButton(navbar, text="Facturas Clientes", font=fuente_texto, fg_color="#555555", text_color="white", command=ver_facturas_clientes)
    btn_facturas.pack(side=tk.RIGHT, padx=10, pady=10)
    
    def ver_acciones():
        pantalla_acciones(root)

    btn_acciones = ctk.CTkButton(navbar, text="Acciones", font=fuente_texto, fg_color="#555555", text_color="white", command=ver_acciones)
    btn_acciones.pack(side=tk.RIGHT, padx=10, pady=10)

    # Crear un frame para el contenido principal
    frame = ctk.CTkFrame(root, fg_color="#ffffff")
    frame.pack(fill='both', expand=True, padx=10, pady=10)

    # Crear etiqueta de título
    label_titulo = ctk.CTkLabel(frame, text="Administración de Productos", font=fuente_titulo)
    label_titulo.pack(pady=(10, 20))

    # Crear un contenedor para la tabla de productos
    tabla_container = ctk.CTkFrame(frame, fg_color="#ffffff")
    tabla_container.pack(fill='both', expand=True)

    def actualizar_tabla():
        # Limpiar el contenedor de la tabla de productos
        for widget in tabla_container.winfo_children():
            widget.destroy()

        # Crear tabla de productos
        tabla_productos = ctk.CTkFrame(tabla_container, fg_color="#ffffff")
        tabla_productos.pack()

        # Crear encabezado de la tabla
        headers = ["Nombre", "Descripción", "Precio", "Stock", "Fecha", "Acciones"]
        for col, header in enumerate(headers):
            label = ctk.CTkLabel(tabla_productos, text=header, font=fuente_texto, fg_color="#4caf50", text_color="white", width=20)
            label.grid(row=0, column=col, padx=5, pady=5, sticky="nsew")

        # Recuperar productos desde Redis
        productos = []
        for key in r.keys():
            producto = recuperar_producto(key)
            producto = {k.decode('utf-8'): v.decode('utf-8') for k, v in producto.items()}
            producto['producto_id'] = key.decode('utf-8')
            producto.setdefault('ultima_actualizacion', 'N/A')
            productos.append(producto)

        def crear_fila_producto(producto, idx):
            for col, key in enumerate(["nombre", "descripcion", "precio", "stock", "ultima_actualizacion"]):
                text = producto.get(key, 'N/A')
                label = ctk.CTkLabel(tabla_productos, text=text, font=fuente_texto, fg_color="#ffffff", width=20)
                label.grid(row=idx+1, column=col, padx=5, pady=5, sticky="nsew")
            # Acciones
            actions_frame = ctk.CTkFrame(tabla_productos, fg_color="#ffffff")
            actions_frame.grid(row=idx+1, column=5, padx=5, pady=5)
            ctk.CTkButton(actions_frame, text="Editar", font=fuente_texto, fg_color="#6c63ff", text_color="white", command=lambda p=producto: editar_producto_form(p)).pack(side=tk.LEFT)
            ctk.CTkButton(actions_frame, text="Eliminar", font=fuente_texto, fg_color="#ff4444", text_color="white", command=lambda p=producto: eliminar_producto(p,productos)).pack(side=tk.LEFT)
            ctk.CTkButton(actions_frame, text="Agregar Stock", font=fuente_texto, fg_color="#6c63ff", text_color="white", command=lambda p=producto: agregar_stock(p)).pack(side=tk.LEFT)

        for idx, producto in enumerate(productos):
            crear_fila_producto(producto, idx)

        # Añadir líneas de separación manualmente
        for widget in tabla_productos.winfo_children():
            widget.grid_configure(sticky="ew")

        for row in range(len(productos) + 1):
            tabla_productos.grid_rowconfigure(row, minsize=40)
            for col in range(len(headers)):
                tabla_productos.grid_columnconfigure(col, weight=1, minsize=100)

    def eliminar_producto(producto, productos):
        r.delete(producto['producto_id'])
        productos.remove(producto)
        registrar_actividad_catalogo(producto['producto_id'], "Eliminado", "", "admin")
        actualizar_tabla()

    def editar_producto(producto, nuevo_precio):
        producto_id = producto['producto_id']
        valor_anterior = producto['precio']
        actualizar_precio_producto_backend(producto_id, nuevo_precio)
        registrar_actividad_catalogo(producto_id, valor_anterior, nuevo_precio, "admin")
        producto['precio'] = nuevo_precio
        producto['ultima_actualizacion'] = datetime.now().strftime("%Y-%m-%d")
        actualizar_tabla()

    def editar_producto_form(producto):
        pantalla_editar_producto(root, producto, editar_producto)
        
    def pantalla_editar_producto(root, producto, actualizar_producto_callback):
        # Limpiar la ventana
        for widget in root.winfo_children():
            widget.destroy()

        # Fuente personalizada
        fuente_titulo = ctk.CTkFont(family='Helvetica', size=24, weight='bold')
        fuente_texto = ctk.CTkFont(family='Helvetica', size=14)
        fuente_boton = ctk.CTkFont(family='Helvetica', size=16, weight='bold')

        # Crear un frame para centrar los widgets
        frame = ctk.CTkFrame(root, fg_color="#ffffff", width=400, height=400, corner_radius=15)
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Crear etiqueta de título
        label_titulo = ctk.CTkLabel(frame, text="EDITAR PRODUCTO", font=fuente_titulo)
        label_titulo.pack(pady=(10, 20))

        # Crear campo de precio antiguo (no editable)
        label_precio_antiguo = ctk.CTkLabel(frame, text="Precio Antiguo", font=fuente_texto)
        label_precio_antiguo.pack(anchor='w', padx=20)
        entry_precio_antiguo = ctk.CTkEntry(frame, width=300, font=fuente_texto)
        entry_precio_antiguo.pack(pady=(0, 10), padx=20)
        entry_precio_antiguo.insert(0, producto["precio"])
        entry_precio_antiguo.configure(state='readonly')

        # Crear campo de nuevo precio
        label_nuevo_precio = ctk.CTkLabel(frame, text="Nuevo Precio", font=fuente_texto)
        label_nuevo_precio.pack(anchor='w', padx=20)
        entry_nuevo_precio = ctk.CTkEntry(frame, width=300, font=fuente_texto)
        entry_nuevo_precio.pack(pady=(0, 20), padx=20)

        def actualizar_precio():
            nuevo_precio = entry_nuevo_precio.get()
            if nuevo_precio:
                actualizar_producto_callback(producto, nuevo_precio)
                messagebox.showinfo("Éxito", "El precio ha sido actualizado correctamente")
                pantalla_administracion(root)
            else:
                messagebox.showerror("Error", "El campo de nuevo precio no puede estar vacío")

        # Crear botón de actualizar precio
        button_actualizar = ctk.CTkButton(frame, text="Actualizar Precio", font=fuente_boton, fg_color="#6c63ff", text_color="white", command=actualizar_precio)
        button_actualizar.pack(pady=10)

        # Crear botón para volver a la pantalla de administración sin actualizar
        def volver():
            pantalla_administracion(root)

        button_volver = ctk.CTkButton(frame, text="Volver", font=fuente_boton, fg_color="#ff4444", text_color="white", command=volver)
        button_volver.pack(pady=10)

    def agregar_stock(producto):
        cantidad = simpledialog.askinteger("Agregar Stock", "Cantidad a agregar:")
        if cantidad is not None:
            producto["stock"] = str(int(producto["stock"]) + cantidad)
            producto["ultima_actualizacion"] = datetime.now().strftime("%Y-%m-%d")
            r.hset(producto["producto_id"], mapping=producto)
            actualizar_tabla()

    actualizar_tabla()

    # Crear sección de agregar nuevo producto
    frame_agregar = ctk.CTkFrame(frame, fg_color="#ffffff")
    frame_agregar.pack(pady=(20, 0))

    label_agregar = ctk.CTkLabel(frame_agregar, text="Agregar Nuevo Producto", font=fuente_titulo)
    label_agregar.pack(pady=(0, 10))

    label_id_prod = ctk.CTkLabel(frame_agregar, text="ID del Producto", font=fuente_texto)
    label_id_prod.pack(pady=(0, 10))
    entry_id = ctk.CTkEntry(frame_agregar, width=300, font=fuente_texto)
    entry_id.pack(pady=(5, 10), padx=20)
    
    label_nombre_prod = ctk.CTkLabel(frame_agregar, text="Nombre del Producto", font=fuente_texto)
    label_nombre_prod.pack(pady=(0, 10))
    entry_nombre = ctk.CTkEntry(frame_agregar, width=300, font=fuente_texto)
    entry_nombre.pack(pady=(5, 10), padx=20)
     
    label_descripcion_prod = ctk.CTkLabel(frame_agregar, text="Descripción del Producto", font=fuente_texto)
    label_descripcion_prod.pack(pady=(0, 10))
    entry_descripcion = ctk.CTkEntry(frame_agregar, width=300, font=fuente_texto)
    entry_descripcion.pack(pady=(5, 10), padx=20)
    
    label_precio_prod = ctk.CTkLabel(frame_agregar, text="Precio", font=fuente_texto)
    label_precio_prod.pack(pady=(0, 10))
    entry_precio = ctk.CTkEntry(frame_agregar, width=300, font=fuente_texto)
    entry_precio.pack(pady=(5, 10), padx=20)

    label_stock_prod = ctk.CTkLabel(frame_agregar, text="Stock", font=fuente_texto)
    label_stock_prod.pack(pady=(0, 10))
    entry_stock = ctk.CTkEntry(frame_agregar, width=300, font=fuente_texto)
    entry_stock.pack(pady=(5, 10), padx=20)
    
    def agregar_producto():
        producto_id = entry_id.get()
        nombre = entry_nombre.get()
        descripcion = entry_descripcion.get()
        precio = entry_precio.get()
        stock = entry_stock.get()
        if producto_id and nombre and descripcion and precio and stock:
            agregar_producto_backend(producto_id, nombre, descripcion, precio, int(stock))
            registrar_actividad_catalogo(producto_id, "", f"Nuevo producto: {nombre}", "admin")
            actualizar_tabla()
            # Limpiar los campos de entrada
            entry_id.delete(0, tk.END)
            entry_nombre.delete(0, tk.END)
            entry_descripcion.delete(0, tk.END)
            entry_precio.delete(0, tk.END)
            entry_stock.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Todos los campos son obligatorios.")

    btn_agregar = ctk.CTkButton(frame_agregar, text="Agregar Producto", font=fuente_texto, fg_color="#4caf50", text_color="white", command=agregar_producto)
    btn_agregar.pack(pady=(10, 20))


# Nueva función para mostrar todas las facturas pagadas
def pantalla_facturas_clientes(root):
    # Limpiar la ventana
    for widget in root.winfo_children():
        widget.destroy()

    # Configuración inicial
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("green")

    # Fuente personalizada
    fuente_titulo = ctk.CTkFont(family='Helvetica', size=24, weight='bold')
    fuente_texto = ctk.CTkFont(family='Helvetica', size=14)
    fuente_datos = ctk.CTkFont(family='Helvetica', size=12)

    # Crear navbar
    navbar = ctk.CTkFrame(root, fg_color="#333333", height=50)
    navbar.pack(fill='x')

    # Función para volver a la administración
    def volver_administracion():
        pantalla_administracion(root)

    # Crear botón para volver atrás
    btn_volver = ctk.CTkButton(navbar, text="Volver", font=fuente_texto, fg_color="#555555", text_color="white", command=volver_administracion)
    btn_volver.pack(side=tk.LEFT, padx=10, pady=10)

    # Crear un frame para el contenido principal
    frame = ctk.CTkFrame(root, fg_color="#ffffff", corner_radius=15)
    frame.pack(fill='both', expand=True, padx=20, pady=20)
    
    sub_frame = ctk.CTkFrame(frame, fg_color="#ffffff", corner_radius=15)
    sub_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    # Crear etiqueta de título
    label_titulo = ctk.CTkLabel(sub_frame, text="Facturas Pagadas de Clientes", font=fuente_titulo, text_color='#4CAF50')
    label_titulo.pack(pady=(10, 20))

    # Crear tabla de facturas
    tabla_facturas = ctk.CTkFrame(sub_frame, fg_color="#f0f0f0")
    tabla_facturas.pack(fill='both', expand=True)

    encabezados = ["Cliente", "Factura ID", "Fecha", "Total sin Impuestos", "Impuestos", "Total con Impuestos"]
    for col, encabezado in enumerate(encabezados):
        label = ctk.CTkLabel(tabla_facturas, text=encabezado, font=fuente_texto, fg_color="#4caf50", text_color="white", width=20)
        label.grid(row=0, column=col, padx=5, pady=5, sticky="nsew")

    facturas = db.facturas.find({"pagada": True})
    for idx, factura in enumerate(facturas):
        usuario = db.usuarios.find_one({"_id": ObjectId(factura["usuario_id"])})
        cliente = usuario["nombre"] if usuario else "Desconocido"
        fila_color = "#ffffff" if idx % 2 == 0 else "#f2f2f2"
        datos = [
            cliente,
            str(factura["_id"]),
            factura["fecha_factura"].strftime("%d/%m/%Y %H:%M"),
            f"${factura['total_sin_impuestos']:.2f}",
            f"${factura['impuestos']:.2f}",
            f"${factura['total_con_impuestos']:.2f}"
        ]
        for col, dato in enumerate(datos):
            label = ctk.CTkLabel(tabla_facturas, text=dato, font=fuente_datos, fg_color=fila_color, width=20)
            label.grid(row=idx+1, column=col, padx=5, pady=5, sticky="nsew")

    for row in range(len(facturas) + 1):
        tabla_facturas.grid_rowconfigure(row, weight=1)
        for col in range(len(encabezados)):
            tabla_facturas.grid_columnconfigure(col, weight=1)



# Define iniciar_sesion after pantalla_administracion is defined
def iniciar_sesion(root, correo, contrasena):
    global usuario_id, carrito  # Asegúrate de declarar 'carrito' y 'usuario_id' como global

    if correo == "admin" and contrasena == "admin":
        pantalla_administracion(root)
        return
    
    usuario_id = iniciar_sesion_backend(correo, contrasena)
    if usuario_id:
        carrito = obtener_carrito_usuario(usuario_id)  # Recuperar el carrito del usuario
        if carrito:
            respuesta = messagebox.askyesno("Recuperar Carrito", "¿Quieres recuperar el carrito anterior?")
            if respuesta:
                print(f"Carrito recuperado: {carrito}")  # Añadir un mensaje de depuración
            else:
                carrito = []
        else:
            carrito = []
        messagebox.showinfo("Éxito", "Sesión iniciada correctamente.")
        pantalla_catalogo(root)
    else:
        messagebox.showerror("Error", "Correo o contraseña incorrectos.")

# Asegúrate de que la función pantalla_administracion esté definida antes de su uso en iniciar_sesion

def pantalla_perfil(root, usuario_id):
    # Limpiar la ventana
    for widget in root.winfo_children():
        widget.destroy()

    # Configuración inicial
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("green")

    # Fuente personalizada
    fuente_titulo = ctk.CTkFont(family='Helvetica', size=28, weight='bold')
    fuente_texto = ctk.CTkFont(family='Helvetica', size=18)
    fuente_info = ctk.CTkFont(family='Helvetica', size=20)

    # Crear navbar
    navbar = ctk.CTkFrame(root, fg_color="#333333", height=50)
    navbar.pack(fill='x')

    # Función para cerrar sesión
    btn_cerrar_sesion = ctk.CTkButton(navbar, text="Cerrar sesión", font=fuente_texto, fg_color="#555555", text_color="white", command=lambda: cerrar_sesion(root))
    btn_cerrar_sesion.pack(side=tk.RIGHT, padx=10, pady=10)

    # Función para volver al catálogo
    def volver_catalogo():
        pantalla_catalogo(root)

    # Crear botón para volver atrás
    btn_volver = ctk.CTkButton(navbar, text="Volver", font=fuente_texto, fg_color="#555555", text_color="white", command=volver_catalogo)
    btn_volver.pack(side=tk.LEFT, padx=10, pady=10)

    # Crear un frame para el contenido principal
    frame = ctk.CTkFrame(root, fg_color="#ffffff", corner_radius=15)
    frame.pack(fill='both', expand=True, padx=10, pady=10)

    # Crear etiqueta de título
    label_titulo = ctk.CTkLabel(frame, text="Perfil", font=fuente_titulo, text_color="#4CAF50")
    label_titulo.pack(pady=(10, 20))

    # Obtener datos del usuario
    usuario = db.usuarios.find_one({"_id": ObjectId(usuario_id)})
    if usuario:
        datos_personales = {
            "Nombre": usuario["nombre"],
            "Correo": usuario["correo"],
            "Dirección": usuario["direccion"],
            "DNI": usuario["dni"],
            "Categoría": usuario.get("categoria", "No categorizado")
        }

        # Imagen de perfil
        imagen_perfil = ctk.CTkLabel(frame, text="100 x 100", width=100, height=100, fg_color="#e0e0e0", corner_radius=50)
        imagen_perfil.pack(pady=(0, 10))

        # Nombre y correo
        label_nombre = ctk.CTkLabel(frame, text=usuario["nombre"], font=fuente_info)
        label_nombre.pack(pady=(0, 5))
        label_correo = ctk.CTkLabel(frame, text=usuario["correo"], font=fuente_info, text_color="#777777")
        label_correo.pack(pady=(0, 10))

        for key, value in datos_personales.items():
            label_key = ctk.CTkLabel(frame, text=f"{key}:", font=fuente_info)
            label_key.pack(anchor='w', padx=20)
            label_value = ctk.CTkLabel(frame, text=value, font=fuente_info, text_color="#555555")
            label_value.pack(anchor='w', padx=20, pady=(0, 10))

        # Crear botón para ver el historial de compras
        btn_historial_compras = ctk.CTkButton(frame, text="Ver Historial de Compras", font=fuente_texto, fg_color="#4caf50", text_color="white", command=lambda: pantalla_historial_compras(root, usuario_id))
        btn_historial_compras.pack( padx=20, pady=(20, 10))

    
        # Información adicional
        info_adicional_frame = ctk.CTkFrame(frame, fg_color="#ffffff", corner_radius=10)
        info_adicional_frame.pack(fill='x', pady=(20, 0), padx=20)

        label_info_adicional = ctk.CTkLabel(info_adicional_frame, text="Información Adicional", font=fuente_titulo, text_color="#4CAF50")
        label_info_adicional.pack(pady=(10, 10))

        info_adicional = {
            "Fecha de Registro": "01/01/2020",
            "Última Conexión": "10/06/2024"
        }

        for key, value in info_adicional.items():
            label_info_key = ctk.CTkLabel(info_adicional_frame, text=f"{key}: {value}", font=fuente_info)
            label_info_key.pack(anchor='w', padx=20, pady=(0, 10))

def pantalla_historial_compras(root, usuario_id):
    # Limpiar la ventana
    for widget in root.winfo_children():
        widget.destroy()

    # Fuente personalizada
    fuente_titulo = ctk.CTkFont(family='Helvetica', size=20, weight='bold')
    fuente_texto = font.Font(family='Helvetica', size=12)

    # Crear navbar
    navbar = tk.Frame(root, bg="#333333", height=50)
    navbar.pack(fill='x')

    # Función para volver al catálogo
    def volver_catalogo():
        pantalla_catalogo(root)

    # Crear botón para volver atrás
    btn_volver = tk.Button(navbar, text="Volver", font=fuente_texto, bg="#555555", fg="white", command=volver_catalogo)
    btn_volver.pack(side=tk.LEFT, padx=10, pady=10)

    # Crear un frame para el contenido principal
    frame = tk.Frame(root, bg="#ffffff")
    frame.pack(fill='both', expand=True, padx=10, pady=10)

    # Crear etiqueta de título
    label_titulo = ctk.CTkLabel(frame, text="Historial de Compras", font=fuente_titulo, text_color="#4CAF50")
    label_titulo.pack(pady=(10, 20))

    # Obtener el historial de compras del usuario
    historial_compras = obtener_historial_compras(usuario_id)

    for compra in historial_compras:
        frame_compra = tk.Frame(frame, bg="#F6F6F6", bd=1, relief=tk.SOLID)
        frame_compra.pack(fill='x', pady=5)

        fecha = compra["fecha"].strftime("%d/%m/%Y %H:%M")
        label_fecha = tk.Label(frame_compra, text=f"Fecha: {fecha}", font=fuente_texto, bg="#f9f9f9")
        label_fecha.pack(anchor='w', padx=10, pady=5)

        total_con_impuestos = f"Total con impuestos: ${compra['total_con_impuestos']:.2f}"
        total_sin_impuestos = f"Total sin impuestos: ${compra['total_sin_impuestos']:.2f}"

        label_total_con_impuestos = tk.Label(frame_compra, text=total_con_impuestos, font=fuente_texto, bg="#f9f9f9")
        label_total_con_impuestos.pack(anchor='w', padx=10, pady=5)

        label_total_sin_impuestos = tk.Label(frame_compra, text=total_sin_impuestos, font=fuente_texto, bg="#f9f9f9")
        label_total_sin_impuestos.pack(anchor='w', padx=10, pady=5)

        label_productos = tk.Label(frame_compra, text="Productos:", font=fuente_texto, bg="#f9f9f9")
        label_productos.pack(anchor='w', padx=10, pady=5)

        for producto in compra["detalle"]:
            nombre_producto = producto["producto_id"]  # Aquí puedes agregar lógica para recuperar el nombre del producto si es necesario
            cantidad = producto["cantidad"]
            precio = producto["precio"]
            label_producto = tk.Label(frame_compra, text=f"{nombre_producto} - Cantidad: {cantidad}, Precio: ${precio:.2f}", font=fuente_texto, bg="#f9f9f9")
            label_producto.pack(anchor='w', padx=20, pady=2)



def pantalla_actividad_usuario(root):
    # Limpiar la ventana
    for widget in root.winfo_children():
        widget.destroy()

    # Fuente personalizada
    fuente_titulo = font.Font(family='Helvetica', size=20, weight='bold')
    fuente_texto = font.Font(family='Helvetica', size=12)
    fuente_datos = font.Font(family='Helvetica', size=10)  # Más pequeña para los datos

    # Crear un frame para el contenido principal
    frame = tk.Frame(root, bg="#ffffff")
    frame.pack(fill='both', expand=True, padx=20, pady=20)  # Aumentar el padding para mejor visualización

    # Crear etiqueta de título
    label_titulo = tk.Label(frame, text="Actividad de Usuarios", font=fuente_titulo, bg="#ffffff")
    label_titulo.pack(pady=(10, 20))

    # Crear tabla de actividad de usuario   
    tabla_actividad = tk.Frame(frame, bg="#f0f0f0")  # Un fondo gris claro para la tabla
    tabla_actividad.pack()

    encabezados = ["Nombre", "Productos", "Método de Pago", "Fecha", "Hora", "Monto"]
    # Colores de fondo para los encabezados y ajuste de la fuente
    color_encabezado = "#404040"  # Un gris oscuro para contraste
    for encabezado in encabezados:
        label = tk.Label(tabla_actividad, text=encabezado, font=fuente_texto, fg="white", bg=color_encabezado, bd=1, relief=tk.SOLID, width=20)
        label.grid(row=0, column=encabezados.index(encabezado), sticky="ew", padx=1, pady=1)  # Uso de sticky para ajuste en la celda

    # Datos simulados de actividad de usuario
    actividades_usuarios = [
     ]

    # Aplicar un estilo alterno para las filas para mejorar la legibilidad
    color_fila = "#ffffff"
    color_fila_alternativa = "#e8e8e8"
    for idx, actividad in enumerate(actividades_usuarios):
        fila_color = color_fila if idx % 2 == 0 else color_fila_alternativa
        for col, clave in enumerate(actividad):
            texto = actividad[clave]
            label = tk.Label(tabla_actividad, text=texto, font=fuente_datos, bg=fila_color, bd=1, relief=tk.SOLID, width=20)
            label.grid(row=idx+1, column=col, sticky="ew", padx=1, pady=1)  # Ajuste de sticky para que el contenido ocupe toda la celda

    def volver_tabla():
        pantalla_administracion(root)
            
    # Crear botón de volver al inicio
    button_volver = tk.Button(frame, text="Volver al Inicio", font=fuente_texto, bg="#404040", fg="white", command=volver_tabla)
    button_volver.pack(pady=10)


def agregar_al_carrito(nombre, precio):
    global carrito, usuario_id  # Asegúrate de declarar 'carrito' y 'usuario_id' como global
    
    # Buscar el producto en el carrito
    for item in carrito:
        if item['nombre'] == nombre:
            item['cantidad'] += 1
            gestionar_carrito(usuario_id, obtener_id_producto_por_nombre(nombre), item['cantidad'], 'cambiar')
            break
    else:
        carrito.append({'nombre': nombre, 'precio': float(precio), 'cantidad': 1})
        gestionar_carrito(usuario_id, obtener_id_producto_por_nombre(nombre), 1, 'agregar')
    
    messagebox.showinfo("Éxito", f"{nombre} ha sido agregado al carrito.")

def pantalla_carrito(root, carrito):
    global headers, tabla_carrito  # Declarar headers y tabla_carrito como global

    # Limpiar la ventana
    for widget in root.winfo_children():
        widget.destroy()

    # Configuración inicial
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("green")

    # Fuente personalizada
    fuente_titulo = ctk.CTkFont(family='Helvetica', size=24, weight='bold')
    fuente_texto = ctk.CTkFont(family='Helvetica', size=14)
    fuente_datos = ctk.CTkFont(family='Helvetica', size=12)

    # Crear navbar
    navbar = ctk.CTkFrame(root, fg_color="#333333", height=50)
    navbar.pack(fill='x')

    # Función para cerrar sesión
    btn_cerrar_sesion = ctk.CTkButton(navbar, text="Cerrar sesión", font=fuente_texto, fg_color="#555555", text_color="white", command=lambda: cerrar_sesion(root))
    btn_cerrar_sesion.pack(side=tk.RIGHT, padx=10, pady=10)

    # Función para volver al catálogo
    def volver_catalogo():
        pantalla_catalogo(root)

    # Crear botón para volver atrás
    btn_volver = ctk.CTkButton(navbar, text="Volver", font=fuente_texto, fg_color="#555555", text_color="white", command=volver_catalogo)
    btn_volver.pack(side=tk.LEFT, padx=10, pady=10)

    # Crear un frame para el contenido principal
    frame = ctk.CTkFrame(root, fg_color="#ffffff", corner_radius=15)
    frame.pack(fill='both', expand=True, padx=20, pady=20)

    # Crear etiqueta de título
    label_titulo = ctk.CTkLabel(frame, text="Carrito", font=fuente_titulo)
    label_titulo.pack(pady=(10, 20))

    # Crear tabla de productos en el carrito
    tabla_carrito = ctk.CTkFrame(frame, fg_color="#f0f0f0")
    tabla_carrito.pack(pady=20)

    headers = ["Producto", "Cantidad", "Total", "Accion"]
    
    for col, header in enumerate(headers):
        label = ctk.CTkLabel(tabla_carrito, text=header, font=fuente_texto, fg_color="#4caf50", text_color="white", width=20)
        label.grid(row=0, column=col, padx=5, pady=5, sticky="nsew")

    def actualizar_total():
        total = sum(float(item['precio']) * item['cantidad'] for item in carrito)
        label_total.config(text=f"Total: ${total:.2f}")

    def aumentar_cantidad(item):
        item['cantidad'] += 1
        gestionar_carrito(usuario_id, obtener_id_producto_por_nombre(item['nombre']), item['cantidad'], 'cambiar')
        actualizar_carrito()
        actualizar_total()

    def disminuir_cantidad(item):
        if item['cantidad'] > 1:
            item['cantidad'] -= 1
            gestionar_carrito(usuario_id, obtener_id_producto_por_nombre(item['nombre']), item['cantidad'], 'cambiar')
            actualizar_carrito()
            actualizar_total()

    def quitar_producto(item):
        carrito.remove(item)
        gestionar_carrito(usuario_id, obtener_id_producto_por_nombre(item['nombre']), 0, 'eliminar')
        actualizar_carrito()
        actualizar_total()

    def actualizar_carrito():
        print(f"Actualizando carrito con los siguientes elementos: {carrito}")
        for widget in tabla_carrito.winfo_children():
            widget.destroy()

        for col, header in enumerate(headers):
            label = ctk.CTkLabel(tabla_carrito, text=header, font=fuente_texto, fg_color="#4caf50", text_color="white", width=20)
            label.grid(row=0, column=col, padx=5, pady=5, sticky="nsew")

        for idx, item in enumerate(carrito):
            ctk.CTkLabel(tabla_carrito, text=item['nombre'], font=fuente_texto, fg_color="#ffffff", width=20).grid(row=idx+1, column=0, padx=5, pady=5)
            cantidad_frame = ctk.CTkFrame(tabla_carrito, fg_color="#ffffff")
            cantidad_frame.grid(row=idx+1, column=1, padx=5, pady=5)
            ctk.CTkButton(cantidad_frame, text="-", width=20, height=20, font=fuente_datos, command=lambda item=item: disminuir_cantidad(item)).pack(side=tk.LEFT, padx=2)
            ctk.CTkLabel(cantidad_frame, text=item['cantidad'], font=fuente_texto, fg_color="#ffffff", width=5).pack(side=tk.LEFT, padx=2)
            ctk.CTkButton(cantidad_frame, text="+", width=20, height=20, font=fuente_datos, command=lambda item=item: aumentar_cantidad(item)).pack(side=tk.LEFT, padx=2)
            ctk.CTkLabel(tabla_carrito, text=f"${float(item['precio']) * item['cantidad']:.2f}", font=fuente_texto, fg_color="#ffffff", width=20).grid(row=idx+1, column=2, padx=5, pady=5)
            ctk.CTkButton(tabla_carrito, text="Quitar", font=fuente_texto, fg_color="#ff4444", text_color="white", command=lambda item=item: quitar_producto(item)).grid(row=idx+1, column=3, padx=5, pady=5)

    actualizar_carrito()

    label_total = tk.Label(frame, text=f"Total: $0.00", font=fuente_titulo, bg="#ffffff")
    label_total.pack(pady=(20, 10))

    actualizar_total()

    btn_finalizar = tk.Button(frame, text="Finalizar Pedido", font=fuente_texto, bg="#000000", fg="white", command=lambda: finalizar_pedido(root))
    btn_finalizar.pack(pady=(10, 20))


def pantalla_pago(root, carrito, usuario_id):
    global entry_correo, entry_nombre, entry_apellido, entry_documento, metodo_pago_var

    # Limpiar la ventana
    for widget in root.winfo_children():
        widget.destroy()

    # Fuente personalizada
    fuente_titulo = font.Font(family='Helvetica', size=20, weight='bold')
    fuente_texto = font.Font(family='Helvetica', size=12)
    fuente_boton = font.Font(family='Helvetica', size=14, weight='bold')

    # Crear un frame principal para dividir en dos secciones
    frame_principal = tk.Frame(root, bg="#ffffff")
    frame_principal.pack(fill='both', expand=True, padx=20, pady=20)

    # Crear un frame para la sección de contacto y métodos de pago
    frame_contacto_pago = tk.Frame(frame_principal, bg="#ffffff")
    frame_contacto_pago.pack(side=tk.LEFT, fill='y', expand=True, padx=10, pady=10)

    # Crear un frame para el resumen de productos
    frame_resumen_productos = tk.Frame(frame_principal, bg="#f9f9f9")
    frame_resumen_productos.pack(side=tk.RIGHT, fill='both', expand=True, padx=10, pady=10)

    # Sección de contacto y métodos de pago
    label_contacto = ctk.CTkLabel(frame_contacto_pago, text="Contacto", font=fuente_titulo, bg="#ffffff", text_color='#4CAF50')
    label_contacto.grid(row=0, column=0, columnspan=2, pady=(10, 5), sticky="w")

    label_correo = tk.Label(frame_contacto_pago, text="Correo electrónico", font=fuente_texto, bg="#ffffff")
    label_correo.grid(row=1, column=0, padx=5, pady=5, sticky="w")
    entry_correo = tk.Entry(frame_contacto_pago, width=30, font=fuente_texto)
    entry_correo.grid(row=1, column=1, padx=5, pady=5)

    label_entrega = ctk.CTkLabel(frame_contacto_pago, text="Entrega", font=fuente_titulo, bg="#ffffff", text_color='#4CAF50')
    label_entrega.grid(row=2, column=0, columnspan=2, pady=(10, 5), sticky="w")

    label_nombre = tk.Label(frame_contacto_pago, text="Nombre", font=fuente_texto, bg="#ffffff")
    label_nombre.grid(row=3, column=0, padx=5, pady=5, sticky="w")
    entry_nombre = tk.Entry(frame_contacto_pago, width=30, font=fuente_texto)
    entry_nombre.grid(row=3, column=1, padx=5, pady=5)

    label_apellido = tk.Label(frame_contacto_pago, text="Apellido", font=fuente_texto, bg="#ffffff")
    label_apellido.grid(row=4, column=0, padx=5, pady=5, sticky="w")
    entry_apellido = tk.Entry(frame_contacto_pago, width=30, font=fuente_texto)
    entry_apellido.grid(row=4, column=1, padx=5, pady=5)

    label_documento = tk.Label(frame_contacto_pago, text="Nº de Documento", font=fuente_texto, bg="#ffffff")
    label_documento.grid(row=5, column=0, padx=5, pady=5, sticky="w")
    entry_documento = tk.Entry(frame_contacto_pago, width=30, font=fuente_texto)
    entry_documento.grid(row=5, column=1, padx=5, pady=5)

    label_metodos_pago = ctk.CTkLabel(frame_contacto_pago, text="Métodos de Pago", font=fuente_titulo, bg="#ffffff", text_color='#4CAF50')
    label_metodos_pago.grid(row=6, column=0, columnspan=2, pady=(10, 5), sticky="w")

    metodo_pago_var = tk.StringVar(value="Efectivo")
    rb_efectivo = tk.Radiobutton(frame_contacto_pago, text="Efectivo", variable=metodo_pago_var, value="Efectivo", font=fuente_texto, bg="#ffffff")
    rb_efectivo.grid(row=7, column=0, columnspan=2, padx=5, pady=5, sticky="w")

    rb_tarjeta = tk.Radiobutton(frame_contacto_pago, text="Tarjeta de Débito", variable=metodo_pago_var, value="Tarjeta de Débito", font=fuente_texto, bg="#ffffff")
    rb_tarjeta.grid(row=8, column=0, columnspan=2, padx=5, pady=5, sticky="w")
    
    rb_tarjeta_credito = tk.Radiobutton(frame_contacto_pago, text="Tarjeta de Crédito", variable=metodo_pago_var, value="Tarjeta de Crédito", font=fuente_texto, bg="#ffffff")
    rb_tarjeta_credito.grid(row=9, column=0, columnspan=2, padx=5, pady=5, sticky="w")

    def verificar_campos_y_procesar_pago():
        if not entry_correo.get() or not entry_nombre.get() or not entry_apellido.get() or not entry_documento.get():
            messagebox.showerror("Error", "Todos los campos de contacto deben ser completados.")
            return
        procesar_pago(root, carrito, metodo_pago_var.get(), usuario_id, entry_correo.get(), entry_nombre.get(), entry_apellido.get(), entry_documento.get())

    btn_pagar = ctk.CTkButton(frame_contacto_pago, text="Pagar Ahora", font=fuente_boton, fg_color="#4CAF50", text_color="white", corner_radius=10, command=verificar_campos_y_procesar_pago)
    btn_pagar.grid(row=10, column=0, columnspan=2, padx=5, pady=20)

    # Sección de resumen de productos
    label_resumen = ctk.CTkLabel(frame_resumen_productos, text="Resumen de Productos", font=fuente_titulo, bg="#f9f9f9", text_color='#4CAF50')
    label_resumen.pack(pady=10)

    for item in carrito:
        frame_producto = tk.Frame(frame_resumen_productos, bg="#ffffff", bd=1, relief=tk.SOLID)
        frame_producto.pack(pady=5, padx=5, fill='x')

        label_nombre_producto = tk.Label(frame_producto, text=item['nombre'], font=fuente_texto, bg="#ffffff")
        label_nombre_producto.pack(pady=5, padx=5, anchor='w')

        label_cantidad = tk.Label(frame_producto, text=f"Cantidad: {item['cantidad']}", font=fuente_texto, bg="#ffffff")
        label_cantidad.pack(pady=5, padx=5, anchor='w')

        label_precio = tk.Label(frame_producto, text=f"Precio: ${item['precio']}", font=fuente_texto, bg="#ffffff")
        label_precio.pack(pady=5, padx=5, anchor='w')

def procesar_pago(root, carrito, metodo_pago, usuario_id, correo, nombre, apellido, documento):
    pedido_id = convertir_carrito(usuario_id)
    if pedido_id:
        facturar_pedido_backend(pedido_id, metodo_pago)
        messagebox.showinfo("Éxito", "Pago procesado correctamente.")
        pantalla_gracias(root, correo, nombre, apellido, documento, carrito)
    else:
        messagebox.showerror("Error", "No se pudo procesar el pago.")

def pantalla_gracias(root, correo, nombre, apellido, documento, carrito):
    # Limpiar la ventana
    for widget in root.winfo_children():
        widget.destroy()

    # Fuente personalizada
    fuente_titulo = ctk.CTkFont(family='Helvetica', size=20, weight='bold')
    fuente_texto = font.Font(family='Helvetica', size=12)

    # Crear un frame para el contenido principal
    frame = tk.Frame(root, bg="#ffffff")
    frame.pack(fill='both', expand=True, padx=10, pady=10)

    label_titulo = ctk.CTkLabel(frame, text="¡Muchas gracias por tu compra!", font=fuente_titulo, text_color="#4CAF50")
    label_titulo.pack(pady=(10, 20))

    label_resumen = tk.Label(frame, text=f"Nombre: {nombre} {apellido}\nCorreo: {correo}\nDocumento: {documento}", font=fuente_texto, bg="#ffffff")
    label_resumen.pack(pady=(10, 20))

    label_facturas = tk.Label(frame, text="Productos comprados:", font=fuente_titulo, bg="#ffffff")
    label_facturas.pack(pady=(10, 20))

    total = 0
    for item in carrito:
        total += item['precio'] * item['cantidad']
        label_item = tk.Label(frame, text=f"{item['nombre']} - Cantidad: {item['cantidad']} - Total: ${item['precio'] * item['cantidad']:.2f}", font=fuente_texto, bg="#ffffff")
        label_item.pack(anchor='center', padx=20, pady=2)

    label_total = tk.Label(frame, text=f"Total pagado: ${total:.2f}", font=fuente_titulo, bg="#ffffff")
    label_total.pack(pady=(20, 10))

    # Botón de volver al catálogo
    btn_volver = tk.Button(frame, text="Volver al Catálogo", font=fuente_texto, bg="#000000", fg="white", command=lambda: pantalla_catalogo(root))
    btn_volver.pack(pady=(20, 10))

def pantalla_pago_facturas(root, facturas_seleccionadas):
    # Limpiar la ventana
    for widget in root.winfo_children():
        widget.destroy()

    # Fuente personalizada
    fuente_titulo = ctk.CTkFont(family='Helvetica', size=20, weight='bold')
    fuente_texto = font.Font(family='Helvetica', size=12)
    fuente_boton = font.Font(family='Helvetica', size=14, weight='bold')

    # Crear un frame principal para dividir en dos secciones
    frame_principal = tk.Frame(root, bg="#ffffff")
    frame_principal.pack(fill='both', expand=True, padx=20, pady=20)

    # Crear un frame para la sección de contacto y métodos de pago
    frame_contacto_pago = tk.Frame(frame_principal, bg="#ffffff")
    frame_contacto_pago.pack(side=tk.LEFT, fill='y', expand=True, padx=10, pady=10)

    # Crear un frame para el resumen de facturas
    frame_resumen_facturas = tk.Frame(frame_principal, bg="#f9f9f9")
    frame_resumen_facturas.pack(side=tk.RIGHT, fill='both', expand=True, padx=10, pady=10)

    # Sección de contacto y métodos de pago
    label_contacto = ctk.CTkLabel(frame_contacto_pago, text="Contacto", font=fuente_titulo, text_color="#4CAF50")
    label_contacto.grid(row=0, column=0, columnspan=2, pady=(10, 5), sticky="w")

    label_correo = tk.Label(frame_contacto_pago, text="Correo electrónico", font=fuente_texto, bg="#ffffff")
    label_correo.grid(row=1, column=0, padx=5, pady=5, sticky="w")
    entry_correo = tk.Entry(frame_contacto_pago, width=30, font=fuente_texto)
    entry_correo.grid(row=1, column=1, padx=5, pady=5)

    label_entrega = ctk.CTkLabel(frame_contacto_pago, text="Entrega", font=fuente_titulo, text_color="#4CAF50")
    label_entrega.grid(row=2, column=0, columnspan=2, pady=(10, 5), sticky="w")

    label_nombre = tk.Label(frame_contacto_pago, text="Nombre", font=fuente_texto, bg="#ffffff")
    label_nombre.grid(row=3, column=0, padx=5, pady=5, sticky="w")
    entry_nombre = tk.Entry(frame_contacto_pago, width=30, font=fuente_texto)
    entry_nombre.grid(row=3, column=1, padx=5, pady=5)

    label_apellido = tk.Label(frame_contacto_pago, text="Apellido", font=fuente_texto, bg="#ffffff")
    label_apellido.grid(row=4, column=0, padx=5, pady=5, sticky="w")
    entry_apellido = tk.Entry(frame_contacto_pago, width=30, font=fuente_texto)
    entry_apellido.grid(row=4, column=1, padx=5, pady=5)

    label_documento = tk.Label(frame_contacto_pago, text="Nº de Documento", font=fuente_texto, bg="#ffffff")
    label_documento.grid(row=5, column=0, padx=5, pady=5, sticky="w")
    entry_documento = tk.Entry(frame_contacto_pago, width=30, font=fuente_texto)
    entry_documento.grid(row=5, column=1, padx=5, pady=5)

    label_metodos_pago = ctk.CTkLabel(frame_contacto_pago, text="Métodos de Pago", font=fuente_titulo, text_color="#4CAF50")
    label_metodos_pago.grid(row=6, column=0, columnspan=2, pady=(10, 5), sticky="w")

    metodo_pago_var = tk.StringVar(value="Efectivo")
    rb_efectivo = tk.Radiobutton(frame_contacto_pago, text="Efectivo", variable=metodo_pago_var, value="Efectivo", font=fuente_texto, bg="#ffffff")
    rb_efectivo.grid(row=7, column=0, columnspan=2, padx=5, pady=5, sticky="w")

    rb_tarjeta = tk.Radiobutton(frame_contacto_pago, text="Tarjeta de Débito", variable=metodo_pago_var, value="Tarjeta de Débito", font=fuente_texto, bg="#ffffff")
    rb_tarjeta.grid(row=8, column=0, columnspan=2, padx=5, pady=5, sticky="w")

    def verificar_campos_y_procesar_pago():
        if not entry_correo.get() or not entry_nombre.get() or not entry_apellido.get() or not entry_documento.get():
            messagebox.showerror("Error", "Todos los campos de contacto deben ser completados.")
            return
        procesar_pago(root, facturas_seleccionadas, metodo_pago_var.get(), usuario_id, entry_correo.get(), entry_nombre.get(), entry_apellido.get(), entry_documento.get())

    btn_pagar = tk.Button(frame_contacto_pago, text="Pagar Ahora", font=fuente_boton, bg="#4CAF50", fg="white", command=verificar_campos_y_procesar_pago)
    btn_pagar.grid(row=9, column=0, columnspan=2, padx=5, pady=20)

    # Sección de resumen de facturas
    label_resumen = ctk.CTkLabel(frame_resumen_facturas, text="Resumen de Facturas", font=fuente_titulo, text_color="#4CAF50")
    label_resumen.pack(pady=10)

    for factura in facturas_seleccionadas:
        frame_factura = tk.Frame(frame_resumen_facturas, bg="#ffffff", bd=1, relief=tk.SOLID)
        frame_factura.pack(pady=5, padx=5, fill='x')

        label_factura_id = tk.Label(frame_factura, text=f"Factura ID: {factura['factura_id']}", font=fuente_texto, bg="#ffffff")
        label_factura_id.pack(pady=5, padx=5, anchor='w')

        label_fecha = tk.Label(frame_factura, text=f"Fecha: {factura['fecha'].strftime('%d/%m/%Y %H:%M')}", font=fuente_texto, bg="#ffffff")
        label_fecha.pack(pady=5, padx=5, anchor='w')

        label_total = tk.Label(frame_factura, text=f"Total con Impuestos: ${factura['total_con_impuestos']:.2f}", font=fuente_texto, bg="#ffffff")
        label_total.pack(pady=5, padx=5, anchor='w')

def procesar_pago(root, facturas_seleccionadas, metodo_pago, usuario_id, correo, nombre, apellido, documento):
    for factura in facturas_seleccionadas:
        db.facturas.update_one({"_id": factura['_id']}, {"$set": {"pagada": True}})
    messagebox.showinfo("Éxito", "Pago procesado correctamente.")
    pantalla_gracias(root, correo, nombre, apellido, documento, facturas_seleccionadas)

def pantalla_facturas_pendientes(root):
    # Limpiar la ventana
    for widget in root.winfo_children():
        widget.destroy()

    # Fuente personalizada
    fuente_titulo = ctk.CTkFont(family='Helvetica', size=20, weight='bold')
    fuente_texto = font.Font(family='Helvetica', size=12)

    # Crear navbar
    navbar = tk.Frame(root, bg="#333333", height=50)
    navbar.pack(fill='x')

    # Función para volver al catálogo
    def volver_catalogo():
        pantalla_catalogo(root)

    # Crear botón para volver atrás
    btn_volver = tk.Button(navbar, text="Volver", font=fuente_texto, bg="#555555", fg="white", command=volver_catalogo)
    btn_volver.pack(side=tk.LEFT, padx=10, pady=10)

    # Crear un frame para el contenido principal
    frame = tk.Frame(root, bg="#ffffff")
    frame.pack(fill='both', expand=True, padx=10, pady=10)

    # Crear etiqueta de título
    label_titulo = ctk.CTkLabel(frame, text="Facturas Pendientes", font=fuente_titulo, text_color="#4CAF50")
    label_titulo.pack(pady=(10, 20))

    # Obtener las facturas pendientes del usuario
    facturas = obtener_facturas_pendientes(usuario_id)

    # Crear tabla de facturas pendientes
    tabla_facturas = tk.Frame(frame, bg="#ffffff")
    tabla_facturas.pack()

    headers = ["Seleccionar", "Factura ID", "Fecha", "Total con Impuestos"]
    for header in headers:
        label = tk.Label(tabla_facturas, text=header, font=fuente_texto, bg="#ffffff", bd=1, relief=tk.SOLID, width=20)
        label.grid(row=0, column=headers.index(header), padx=5, pady=5)

    seleccionadas = []
    def seleccionar_factura(factura, var):
        if var.get() == 1:
            seleccionadas.append(factura)
        else:
            seleccionadas.remove(factura)
        actualizar_total()

    for idx, factura in enumerate(facturas):
        var = tk.IntVar()
        chk = tk.Checkbutton(tabla_facturas, variable=var, onvalue=1, offvalue=0, command=lambda f=factura, v=var: seleccionar_factura(f, v))
        chk.grid(row=idx+1, column=0, padx=5, pady=5)
        tk.Label(tabla_facturas, text=factura['factura_id'], font=fuente_texto, bg="#ffffff", bd=1, relief=tk.SOLID, width=20).grid(row=idx+1, column=1, padx=5, pady=5)
        tk.Label(tabla_facturas, text=factura['fecha'].strftime("%d/%m/%Y %H:%M"), font=fuente_texto, bg="#ffffff", bd=1, relief=tk.SOLID, width=20).grid(row=idx+1, column=2, padx=5, pady=5)
        tk.Label(tabla_facturas, text=f"${factura['total_con_impuestos']:.2f}", font=fuente_texto, bg="#ffffff", bd=1, relief=tk.SOLID, width=20).grid(row=idx+1, column=3, padx=5, pady=5)

    def actualizar_total():
        total = sum(factura['total_con_impuestos'] for factura in seleccionadas)
        label_total.config(text=f"Total a Pagar: ${total:.2f}")

    def pagar_facturas():
        if seleccionadas:
            pantalla_pago_facturas(root, seleccionadas)
        else:
            messagebox.showerror("Error", "No has seleccionado ninguna factura para pagar.")

    label_total = tk.Label(frame, text=f"Total a Pagar: $0.00", font=fuente_titulo, bg="#ffffff")
    label_total.pack(pady=(20, 10))

    btn_pagar = tk.Button(frame, text="Pagar Facturas Seleccionadas", font=fuente_texto, bg="#4CAF50", fg="white", command=pagar_facturas)
    btn_pagar.pack(pady=(10, 20))



def finalizar_pedido(root):
    global carrito
    pedido_id = convertir_carrito(usuario_id)
    if pedido_id:
        carrito = []  # Vaciar el carrito en la variable global
        messagebox.showinfo("Pedido", "Pedido creado exitosamente. Carrito vacío.")
        pantalla_catalogo(root)
    else:
        messagebox.showerror("Error", "No se pudo crear el pedido.")


def procesar_pago(root, facturas_seleccionadas, metodo_pago, usuario_id, correo, nombre, apellido, documento):
    for factura in facturas_seleccionadas:
        db.facturas.update_one({"_id": factura['_id']}, {"$set": {"pagada": True}})
    messagebox.showinfo("Éxito", "Pago procesado correctamente.")
    pantalla_gracias(root, correo, nombre, apellido, documento, facturas_seleccionadas)

def pantalla_acciones(root):
    # Limpiar la ventana
    for widget in root.winfo_children():
        widget.destroy()

    # Configuración inicial
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("green")

    # Fuente personalizada
    fuente_titulo = ctk.CTkFont(family='Helvetica', size=24, weight='bold')
    fuente_texto = ctk.CTkFont(family='Helvetica', size=14)
    fuente_datos = ctk.CTkFont(family='Helvetica', size=12)

    # Crear navbar
    navbar = ctk.CTkFrame(root, fg_color="#333333", height=50)
    navbar.pack(fill='x')

    # Función para volver a la pantalla de administración
    def volver_admin():
        pantalla_administracion(root)

    # Crear botón para volver atrás
    btn_volver = ctk.CTkButton(navbar, text="Volver", font=fuente_texto, fg_color="#555555", text_color="white", command=volver_admin)
    btn_volver.pack(side=tk.LEFT, padx=10, pady=10)

    # Crear un frame para el contenido principal
    frame = ctk.CTkFrame(root, fg_color="#ffffff", corner_radius=15)
    frame.pack(fill='both', expand=True, padx=20, pady=20)

    # Crear etiqueta de título
    label_titulo = ctk.CTkLabel(frame, text="Registro de Acciones en Productos", font=fuente_titulo)
    label_titulo.pack(pady=(10, 20))

    # Crear contenedor para centrar la tabla
    table_container = ctk.CTkFrame(frame, fg_color="#ffffff")
    table_container.pack(expand=True)

    # Crear tabla de acciones
    tabla_acciones = ctk.CTkFrame(table_container, fg_color="#f0f0f0")
    tabla_acciones.pack(pady=20)

    headers = ["Fecha", "Producto ID", "Acción", "Valor Anterior", "Nuevo Valor", "Operador"]
    for col, header in enumerate(headers):
        label = ctk.CTkLabel(tabla_acciones, text=header, font=fuente_texto, fg_color="#4caf50", text_color="white", width=20)
        label.grid(row=0, column=col, padx=5, pady=5, sticky="nsew")

    # Asegurarse de que no haya duplicados en los datos recuperados
    acciones = list(db.actividades_catalogo.find().sort("fecha", -1))

    for idx, accion in enumerate(acciones):
        fecha = accion['fecha'].strftime("%Y-%m-%d %H:%M:%S")
        producto_id = accion['producto_id']
        accion_tipo = "Nuevo Producto" if accion['valor_anterior'] == "" else "Cambio" if accion['nuevo_valor'] != "" else "Eliminado"
        valor_anterior = accion['valor_anterior'] if accion['valor_anterior'] else "N/A"
        nuevo_valor = accion['nuevo_valor'] if accion['nuevo_valor'] else "N/A"
        operador = accion['operador']
        fila_color = "#ffffff" if idx % 2 == 0 else "#f2f2f2"

        datos = [fecha, producto_id, accion_tipo, valor_anterior, nuevo_valor, operador]
        for col, dato in enumerate(datos):
            label = ctk.CTkLabel(tabla_acciones, text=dato, font=fuente_datos, fg_color=fila_color, width=20)
            label.grid(row=idx+1, column=col, padx=5, pady=5, sticky="nsew")

    for row in range(len(acciones) + 1):
        tabla_acciones.grid_rowconfigure(row, weight=1)
        for col in range(len(headers)):
            tabla_acciones.grid_columnconfigure(col, weight=1)



def procesar_pago(root, carrito, metodo_pago, usuario_id, correo, nombre, apellido, documento):
    pedido_id = convertir_carrito(usuario_id)
    if pedido_id:
        factura_id = facturar_pedido_backend(pedido_id, metodo_pago)
        if factura_id:
            # Actualizar el stock de los productos en Redis
            for item in carrito:
                producto_id = obtener_id_producto_por_nombre(item['nombre'])
                producto = recuperar_producto(producto_id)
                stock_actual = int(producto[b'stock'].decode('utf-8'))
                nuevo_stock = stock_actual - item['cantidad']
                r.hset(producto_id, "stock", str(nuevo_stock))
                # Registrar actividad en MongoDB (opcional)
                registrar_actividad_catalogo(producto_id, str(stock_actual), str(nuevo_stock), "Sistema")

            messagebox.showinfo("Éxito", "Pago procesado correctamente.")
            pantalla_gracias(root, correo, nombre, apellido, documento, carrito)
        else:
            messagebox.showerror("Error", "No se pudo procesar el pago.")
    else:
        messagebox.showerror("Error", "No se pudo procesar el pago.")
        
        
if __name__ == "__main__":
    main()
