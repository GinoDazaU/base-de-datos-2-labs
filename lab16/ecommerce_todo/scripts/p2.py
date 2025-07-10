from app import create_app
from app.models.database import db, DBCart, DBCartItem
from datetime import datetime, timezone
from random import randint

items = [
    {"product_id": 1, "name": "Laptop Lenovo ThinkPad X1", "price": 899.99},
    {"product_id": 2, "name": "Monitor UltraWide LG 34\"", "price": 499.99},
    {"product_id": 3, "name": "Teclado Mecánico RGB", "price": 79.99},
    {"product_id": 4, "name": "Mouse Logitech MX Master 3", "price": 99.99},
    {"product_id": 5, "name": "Audífonos Sony WH-1000XM4", "price": 299.99},
    {"product_id": 6, "name": "Silla Ergonómica para Oficina", "price": 199.99},
    {"product_id": 7, "name": "Docking Station USB-C", "price": 129.99},
    {"product_id": 8, "name": "Memoria USB 128GB", "price": 24.99},
    {"product_id": 9, "name": "Disco SSD 1TB", "price": 119.99},
    {"product_id": 10, "name": "Cámara Web Full HD", "price": 49.99},
    {"product_id": 11, "name": "Micrófono Blue Yeti", "price": 109.99},
    {"product_id": 12, "name": "Cable HDMI 2m", "price": 9.99},
    {"product_id": 13, "name": "Hub USB 4 Puertos", "price": 19.99},
    {"product_id": 14, "name": "Base para Laptop Ajustable", "price": 39.99},
    {"product_id": 15, "name": "Router WiFi 6", "price": 149.99},
    {"product_id": 16, "name": "Impresora Multifunción", "price": 89.99},
    {"product_id": 17, "name": "Tablet Android 10\"", "price": 229.99},
    {"product_id": 18, "name": "Altavoz Bluetooth JBL", "price": 59.99},
    {"product_id": 19, "name": "Power Bank 20,000mAh", "price": 34.99},
    {"product_id": 20, "name": "Cargador Rápido USB-C", "price": 14.99}
]

def seed_database():
    app = create_app()
    
    with app.app_context():
        # Limpiar datos existentes
        DBCartItem.query.delete()
        DBCart.query.delete()

        test_carts = []

        for i in range(20):
            cart = {
                'user_id': f'user{i + 1}',
                'items': []
            }
            selected_items_ids = []
            for j in range(randint(3, 10)):
                selected_item_id = randint(0, 19)
                while selected_item_id in selected_items_ids:
                    selected_item_id = randint(0, 19)
                selected_items_ids.append(selected_item_id)
                selected_item = items[selected_item_id]
                item = {
                    'product_id': selected_item["product_id"],
                    'name': selected_item["name"],
                    'price': selected_item["price"],
                    'quantity': randint(1, 5)
                }
                cart["items"].append(item)
            test_carts.append(cart)
        
        # Insertar datos
        for cart_data in test_carts:
            cart = DBCart(
                user_id=cart_data['user_id'],
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            db.session.add(cart)
            db.session.flush()  # Para obtener el ID del carrito
            
            for item_data in cart_data['items']:
                item = DBCartItem(
                    cart_id=cart.id,
                    product_id=item_data['product_id'],
                    name=item_data['name'],
                    price=item_data['price'],
                    quantity=item_data['quantity'],
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.session.add(item)
        
        db.session.commit()
        print("✅ Datos de prueba insertados correctamente")

if __name__ == '__main__':
    seed_database()