from pymongo import MongoClient
import redis
from datetime import datetime
from bson.objectid import ObjectId

# Conexión a MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['ingenieria_datos']

# Conexión a Redis
r = redis.Redis(host='localhost', port=6379, db=0)

def registrar_usuario_backend(nombre, correo, contrasena, dni, direccion):
    if db.usuarios.find_one({"correo": correo}):
        return None
    usuario_id = db.usuarios.insert_one({
        "nombre": nombre,
        "correo": correo,
        "contrasena": contrasena,
        "dni": dni,
        "direccion": direccion,
        "fecha_registro": datetime.now()
    }).inserted_id
    return str(usuario_id)

def iniciar_sesion_backend(correo, contrasena):
    usuario = db.usuarios.find_one({"correo": correo, "contrasena": contrasena})
    if not usuario:
        return None
    usuario_id = str(usuario["_id"])
    db.sesiones.insert_one({
        "usuario_id": usuario_id,
        "inicio": datetime.now(),
        "fin": None
    })
    registrar_actividad_usuario(usuario_id)  # Llama a la función aquí
    return usuario_id

def finalizar_sesion_backend(usuario_id):
    result = db.sesiones.update_one(
        {"usuario_id": usuario_id, "fin": None},
        {"$set": {"fin": datetime.now()}}
    )
    if result.matched_count == 0:
        print("No se encontró una sesión activa para finalizar.")
    else:
        print("Sesión finalizada correctamente.")
    registrar_actividad_usuario(usuario_id)  # Llama a la función aquí

def agregar_producto_backend(producto_id, nombre, descripcion, precio, stock):
    r.hset(producto_id, mapping={
        "nombre": nombre,
        "descripcion": descripcion,
        "precio": str(precio),
        "stock": str(stock),
        "ultima_actualizacion": datetime.now().strftime("%Y-%m-%d")
    })
    registrar_actividad_catalogo(producto_id, "", f"Nuevo producto: {nombre}", "admin")

def actualizar_precio_producto_backend(producto_id, nuevo_precio):
    producto = recuperar_producto(producto_id)
    valor_anterior = producto[b'precio'].decode('utf-8')
    r.hset(producto_id, "precio", str(nuevo_precio))
    r.hset(producto_id, "ultima_actualizacion", datetime.now().strftime("%Y-%m-%d"))
    registrar_actividad_catalogo(producto_id, valor_anterior, nuevo_precio, "admin")

def eliminar_producto_backend(producto_id):
    producto = recuperar_producto(producto_id)
    r.delete(producto_id)
    registrar_actividad_catalogo(producto_id, producto[b'nombre'].decode('utf-8'), "Producto eliminado", "admin")

def recuperar_producto(producto_id):
    return r.hgetall(producto_id)

def registrar_actividad_catalogo(producto_id, valor_anterior, nuevo_valor, operador):
    db.actividades_catalogo.insert_one({
        "producto_id": producto_id,
        "valor_anterior": valor_anterior,
        "nuevo_valor": nuevo_valor,
        "operador": operador,
        "fecha": datetime.now()
    })

def gestionar_carrito(usuario_id, producto_id, cantidad, accion):
    carrito = db.carritos.find_one({"usuario_id": usuario_id, "estado": "activo"})
    if not carrito:
        carrito_id = db.carritos.insert_one({"usuario_id": usuario_id, "productos": [], "estado": "activo"}).inserted_id
    else:
        carrito_id = carrito['_id']
    
    if accion == 'agregar':
        db.carritos.update_one(
            {"_id": carrito_id, "productos.producto_id": {"$ne": producto_id}},
            {"$push": {"productos": {"producto_id": producto_id, "cantidad": cantidad}}}
        )
    elif accion == 'eliminar':
        db.carritos.update_one(
            {"_id": carrito_id},
            {"$pull": {"productos": {"producto_id": producto_id}}}
        )
    elif accion == 'cambiar':
        db.carritos.update_one(
            {"_id": carrito_id, "productos.producto_id": producto_id},
            {"$set": {"productos.$.cantidad": cantidad}}
        )

def convertir_carrito(usuario_id):
    carrito = db.carritos.find_one({"usuario_id": usuario_id, "estado": "activo"})
    if carrito:
        pedido_id = db.pedidos.insert_one({
            "usuario_id": usuario_id,
            "carrito_id": carrito['_id'],
            "fecha_pedido": datetime.now(),
            "estado": "pendiente"
        }).inserted_id
        db.carritos.update_one({"_id": carrito['_id']}, {"$set": {"estado": "convertido"}})
        factura_id = registrar_factura(pedido_id, carrito['productos'])
        print(f"Factura creada con ID: {factura_id}")  # Mensaje de depuración
        db.carritos.update_one({"_id": carrito['_id']}, {"$set": {"productos": []}})  # Vaciar el carrito en la base de datos
        return str(pedido_id)
    return None



def registrar_factura(pedido_id, productos):
    total_sin_impuestos = 0
    detalle = []

    for item in productos:
        producto = recuperar_producto(item['producto_id'])
        precio = float(producto[b'precio'])
        total_sin_impuestos += precio * item['cantidad']
        detalle.append({
            "producto_id": item['producto_id'],
            "cantidad": item['cantidad'],
            "precio": precio
        })

    impuestos = total_sin_impuestos * 0.21  # IVA del 21%
    total_con_impuestos = total_sin_impuestos + impuestos

    factura_id = db.facturas.insert_one({
        "pedido_id": pedido_id,
        "usuario_id": db.pedidos.find_one({"_id": pedido_id})["usuario_id"],  # Añadir usuario_id a la factura
        "fecha_factura": datetime.now(),
        "total_sin_impuestos": total_sin_impuestos,
        "impuestos": impuestos,
        "total_con_impuestos": total_con_impuestos,
        "detalle": detalle,
        "pagada": False
    }).inserted_id

    print(f"Detalles de la factura: {detalle}")  # Mensaje de depuración
    return str(factura_id)


def obtener_carrito_usuario(usuario_id):
    carrito = db.carritos.find_one({"usuario_id": usuario_id, "estado": "activo"})
    if carrito:
        productos = []
        for item in carrito['productos']:
            producto = recuperar_producto(item['producto_id'])
            producto = {k.decode('utf-8'): v.decode('utf-8') for k, v in producto.items()}
            producto['cantidad'] = item['cantidad']
            productos.append(producto)
        return productos
    return []

def facturar_pedido_backend(pedido_id, metodo_pago):
    pedido = db.pedidos.find_one({"_id": ObjectId(pedido_id)})
    carrito = db.carritos.find_one({"_id": pedido['carrito_id']})
    total_sin_impuestos = 0
    detalle = []
    
    for item in carrito['productos']:
        producto = recuperar_producto(item['producto_id'])
        precio = float(producto[b'precio'])
        total_sin_impuestos += precio * item['cantidad']
        detalle.append({
            "producto_id": item['producto_id'],
            "cantidad": item['cantidad'],
            "precio": precio
        })

    if metodo_pago == "Efectivo":
        impuestos = 0
    else:
        impuestos = total_sin_impuestos * 0.21  # IVA del 21%

    total_con_impuestos = total_sin_impuestos + impuestos
    
    factura_id = db.facturas.insert_one({
        "pedido_id": pedido_id,
        "fecha_factura": datetime.now(),
        "total_sin_impuestos": total_sin_impuestos,
        "impuestos": impuestos,
        "total_con_impuestos": total_con_impuestos,
        "detalle": detalle,
        "pagada": False  # Marcado como no pagada
    }).inserted_id
    
    db.pedidos.update_one({"_id": ObjectId(pedido_id)}, {"$set": {"estado": "completado"}})
    
    return str(factura_id)

def obtener_facturas_pendientes(usuario_id):
    facturas = db.facturas.find({"usuario_id": usuario_id, "pagada": False})
    facturas_pendientes = []
    for factura in facturas:
        facturas_pendientes.append({
            "_id": factura["_id"],
            "factura_id": str(factura["_id"]),
            "fecha": factura["fecha_factura"],
            "total_con_impuestos": factura["total_con_impuestos"]
        })
    print(f"Facturas pendientes para usuario {usuario_id}: {facturas_pendientes}")  # Mensaje de depuración
    return facturas_pendientes



def obtener_id_producto_por_nombre(nombre):
    for key in r.keys():
        producto = recuperar_producto(key)
        if producto[b'nombre'].decode('utf-8') == nombre:
            return key.decode('utf-8')
    return None

def obtener_historial_compras(usuario_id):
    historial = db.facturas.find({"usuario_id": usuario_id, "pagada": True})
    compras = []

    for factura in historial:
        detalle = factura.get("detalle", [])
        total_sin_impuestos = factura.get("total_sin_impuestos", 0)
        impuestos = factura.get("impuestos", 0)
        total_con_impuestos = factura.get("total_con_impuestos", 0)

        compras.append({
            "fecha": factura["fecha_factura"],
            "total_sin_impuestos": total_sin_impuestos,
            "impuestos": impuestos,
            "total_con_impuestos": total_con_impuestos,
            "detalle": detalle
        })

    return compras

def registrar_actividad_usuario(usuario_id):
    sesiones = db.sesiones.find({"usuario_id": usuario_id, "fin": {"$ne": None}})
    tiempo_total = sum((sesion["fin"] - sesion["inicio"]).total_seconds() for sesion in sesiones) / 60  # Tiempo total en minutos

    if tiempo_total > 240:
        categoria = "TOP"
    elif 120 <= tiempo_total <= 240:
        categoria = "MEDIUM"
    else:
        categoria = "LOW"

    db.usuarios.update_one({"_id": ObjectId(usuario_id)}, {"$set": {"categoria": categoria}})