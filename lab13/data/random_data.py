import json
import random
from datetime import datetime, timedelta

# Cargar los datos originales como base
with open("clientes_base.json", "r", encoding="utf-8") as f:
    clientes_base = json.load(f)

with open("productos_base.json", "r", encoding="utf-8") as f:
    productos_base = json.load(f)

with open("pedidos_base.json", "r", encoding="utf-8") as f:
    pedidos_base = json.load(f)

# Generar 100 clientes
clientes = []
for i in range(100):
    base = random.choice(clientes_base)
    nuevo = base.copy()
    nuevo["id_cliente"] = i + 1
    nuevo["nombre"] = f"{base['nombre'].split()[0]} {base['nombre'].split()[1]} {i+1}"
    nuevo["email"] = f"user{i+1}@mail.com"
    nuevo["telefono"] = f"555-{1000+i}"
    clientes.append(nuevo)

# Guardar clientes
with open("clientes.json", "w", encoding="utf-8") as f:
    json.dump(clientes, f, indent=4, ensure_ascii=False)

# Generar 100 productos
productos = []
for i in range(100):
    base = random.choice(productos_base)
    nuevo = base.copy()
    nuevo["id_producto"] = i + 1
    nuevo["nombre"] = f"{base['nombre']} Modelo {i+1}"
    nuevo["precio"] = round(base["precio"] * random.uniform(0.8, 1.2), 2)
    nuevo["stock"] = random.randint(10, 100)
    productos.append(nuevo)

# Guardar productos
with open("productos.json", "w", encoding="utf-8") as f:
    json.dump(productos, f, indent=4, ensure_ascii=False)

# Generar 100 pedidos
pedidos = []
for i in range(100):
    pedido = {
        "id_pedido": 100 + i,
        "id_cliente": random.randint(1, 100),
        "productos": [],
        "fecha_pedido": (datetime(2024, 1, 1) + timedelta(days=random.randint(0, 180))).strftime("%Y-%m-%d"),
        "estado": random.choice(["Enviado", "Procesando", "Entregado", "Cancelado"])
    }

    total = 0
    for _ in range(random.randint(1, 3)):  # De 1 a 3 productos por pedido
        prod = random.choice(productos)
        cantidad = random.randint(1, 3)
        precio = prod["precio"]
        total += precio * cantidad
        pedido["productos"].append({
            "id_producto": prod["id_producto"],
            "nombre": prod["nombre"],
            "cantidad": cantidad,
            "precio_unitario": precio
        })

    pedido["total_pedido"] = round(total, 2)
    pedidos.append(pedido)

# Guardar pedidos
with open("pedidos.json", "w", encoding="utf-8") as f:
    json.dump(pedidos, f, indent=4, ensure_ascii=False)

print("✅ Archivos generados con 100 registros cada uno.")
