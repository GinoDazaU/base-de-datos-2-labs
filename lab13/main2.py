from mongo_handler import MongoDBHandler

mongo_handler = MongoDBHandler()
mongo_handler.crear_indice("title")

mongo_handler.crear_producto({"title": "Producto 1", "price": 100})
mongo_handler.crear_producto({"title": "Producto 2", "price": 200})
mongo_handler.crear_producto({"title": "Producto 3", "price": 300})

productos = mongo_handler.obtener_productos()
print("Lista de productos:", productos)

producto = mongo_handler.obtener_producto({"_id": productos[0]['_id']})
print("Producto obtenido:", producto)

mongo_handler.actualizar_producto({"_id": productos[0]['_id']}, {"price": 120})
print("Productos con precio 120:", mongo_handler.obtener_productos_por_precio(120))

mongo_handler.eliminar_producto({"_id": productos[1]['_id']})
producto = mongo_handler.obtener_producto({"_id": productos[1]['_id']})
print("Producto obtenido:", producto)

print("Productos con precio 100:", mongo_handler.obtener_productos_por_precio(100))
print("Productos que contienen '5G' en el nombre:", mongo_handler.obtener_productos_por_nombre("5G"))

print("Precio promedio de productos:", mongo_handler.precio_promedio())
print("Total de productos:", mongo_handler.contar_productos())
print("Producto con mayor stock por categoría:", mongo_handler.mayor_stock_categoria())
