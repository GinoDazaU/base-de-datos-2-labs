from app.models.cart import Cart, CartItem
from app.models.database import db, DBCart, DBCartItem
from app.config import redis_client  # importa el cliente Redis
import json
from typing import Optional
from sqlalchemy import func

CACHE_TTL_SECONDS = 1800  # 30 minutos

class CartService:
    def get_cart(self, user_id: str) -> Cart:
        # Intenta obtener desde Redis
        cache_key = f"cart:{user_id}"
        cached = redis_client.get(cache_key)
        if cached:
            cart_dict = json.loads(cached)
            items = [CartItem(**item) for item in cart_dict["items"]]
            return Cart(user_id=user_id, items=items)

        # Si no está en Redis, consulta en PostgreSQL
        db_cart = DBCart.query.filter_by(user_id=user_id).first()
        if db_cart:
            items = [
                CartItem(
                    product_id=item.product_id,
                    name=item.name,
                    price=item.price,
                    quantity=item.quantity
                ) for item in db_cart.items
            ]
            cart = Cart(user_id=user_id, items=items)
            # Guardar en Redis
            redis_client.setex(cache_key, CACHE_TTL_SECONDS, json.dumps(cart.to_dict()))
            return cart

        return Cart(user_id=user_id, items=[])

    def save_cart(self, cart: Cart) -> None:
        db_cart = DBCart.query.filter_by(user_id=cart.user_id).first()
        if not db_cart:
            db_cart = DBCart(user_id=cart.user_id)
            db.session.add(db_cart)
            db.session.flush()

        existing_items = {item.product_id: item for item in db_cart.items}
        new_items = {item.product_id: item for item in cart.items}

        for product_id, cart_item in new_items.items():
            if product_id in existing_items:
                db_item = existing_items[product_id]
                db_item.name = cart_item.name
                db_item.price = cart_item.price
                db_item.quantity = cart_item.quantity
            else:
                db_item = DBCartItem(
                    cart_id=db_cart.id,
                    product_id=cart_item.product_id,
                    name=cart_item.name,
                    price=cart_item.price,
                    quantity=cart_item.quantity
                )
                db.session.add(db_item)

        for product_id, db_item in existing_items.items():
            if product_id not in new_items:
                db.session.delete(db_item)

        db.session.commit()

        # Actualizar Redis
        cache_key = f"cart:{cart.user_id}"
        redis_client.setex(cache_key, CACHE_TTL_SECONDS, json.dumps(cart.to_dict()))

    def add_item(self, user_id: str, item_data: dict) -> Cart:
        cart = self.get_cart(user_id)
        new_item = CartItem(**item_data)
        cart.add_item(new_item)
        self.save_cart(cart)
        return cart

    def remove_item(self, user_id: str, product_id: int) -> Cart:
        cart = self.get_cart(user_id)
        cart.remove_item(product_id)
        self.save_cart(cart)
        return cart

    def update_quantity(self, user_id: str, product_id: int, quantity: int) -> Optional[Cart]:
        cart = self.get_cart(user_id)
        if cart.update_quantity(product_id, quantity):
            self.save_cart(cart)
            return cart
        return None

    def clear_cart(self, user_id: str) -> None:
        db_cart = DBCart.query.filter_by(user_id=user_id).first()
        if db_cart:
            db.session.delete(db_cart)
            db.session.commit()
        # Borrar caché también
        redis_client.delete(f"cart:{user_id}")

    def get_top_products(self, limit=10):
        cache_key = "top-products"
        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)

        # Consulta en PostgreSQL: top productos por cantidad comprada
        results = (
            db.session.query(DBCartItem.product_id, DBCartItem.name, func.sum(DBCartItem.quantity).label('total_quantity'))
            .group_by(DBCartItem.product_id, DBCartItem.name)
            .order_by(func.sum(DBCartItem.quantity).desc())
            .limit(limit)
            .all()
        )

        top_products = [
            {
                "product_id": r.product_id,
                "name": r.name,
                "total_quantity": r.total_quantity
            } for r in results
        ]

        # Guardar en Redis por 10 minutos
        redis_client.setex(cache_key, 600, json.dumps(top_products))

        return top_products
