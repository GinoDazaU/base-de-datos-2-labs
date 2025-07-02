import requests
from pymongo import MongoClient

class MongoDBHandler:
    def __init__(self):
        self.mongo_uri = "mongodb://localhost:27017/"  # puerto default
        self.db_name = "pucp_store"
        self.categories_name = "categorias"
        self.productos_name = "productos"
        self.connect_mongo()

    def connect_mongo(self):
        try:
            client = MongoClient(self.mongo_uri)
            self.db = client[self.db_name]
            print(f"Conectado a la base de datos '{self.db_name}' en MongoDB.")
        except Exception as e:
            print(f"Error al conectar a MongoDB: {e}")

    def fetch_json_data(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error al obtener datos: {e}")
            return None
        
    def fetch_all_categories(self, base_url):
        data = self.fetch_json_data(base_url)
        if data:
            self.db[self.categories_name].delete_many({})
            docs = [{"nombre": cat["name"], "slug": cat["slug"], "url": cat["url"]} for cat in data]
            self.db[self.categories_name].insert_many(docs)
            print(f"{len(docs)} categorías insertadas.")
        else:
            print("No se cargaron categorías.")

    def fetch_all_products(self):
        categorias = self.db[self.categories_name].find()
        total = 0
        self.db[self.productos_name].delete_many({})  # Limpia antes de insertar

        for categoria in categorias:
            nombre_cat = categoria.get("slug") or categoria.get("nombre")
            url = f"https://dummyjson.com/products/category/{nombre_cat}?limit=0"
            json_data = self.fetch_json_data(url)

            if json_data and "products" in json_data and len(json_data["products"]) > 0:
                for prod in json_data["products"]:
                    prod["categoria"] = nombre_cat  # Añade la categoría al producto
                self.db[self.productos_name].insert_many(json_data["products"])
                total += len(json_data["products"])
                print(f"Productos cargados para {nombre_cat}: {len(json_data['products'])}")
            else:
                print(f"[!] Sin productos en la categoría {nombre_cat}")
        print(f"Total de productos insertados: {total}")

    # Parte 2: Metodos CRUD

    def crear_indice(self, campo):
        self.db[self.productos_name].create_index(campo)
        print(f"Índice creado en el campo '{campo}'")

    def crear_producto(self, producto):
        result = self.db[self.productos_name].insert_one(producto)
        print(f"Producto insertado con ID: {result.inserted_id}")

    def obtener_productos(self):
        return list(self.db[self.productos_name].find())

    def obtener_producto(self, filtro):
        return self.db[self.productos_name].find_one(filtro)

    def actualizar_producto(self, filtro, nuevos_datos):
        result = self.db[self.productos_name].update_one(filtro, {"$set": nuevos_datos})
        print(f"{result.modified_count} documento(s) actualizado(s).")

    def eliminar_producto(self, filtro):
        result = self.db[self.productos_name].delete_one(filtro)
        print(f"{result.deleted_count} documento(s) eliminado(s).")

    # consultas basicas

    def obtener_productos_por_precio(self, precio):
        return list(self.db[self.productos_name].find({"price": precio}))

    def obtener_productos_por_nombre(self, texto):
        return list(self.db[self.productos_name].find({"title": {"$regex": texto, "$options": "i"}}))

    # consultas agregadas

    def precio_promedio(self):
        pipeline = [
            {"$group": {"_id": None, "promedio": {"$avg": "$price"}}}
        ]
        result = list(self.db[self.productos_name].aggregate(pipeline))
        return result[0]["promedio"] if result else None

    def contar_productos(self):
        return self.db[self.productos_name].count_documents({})

    def mayor_stock_categoria(self):
        pipeline = [
            {"$sort": {"stock": -1}},
            {"$group": {
                "_id": "$categoria",
                "producto": {"$first": "$title"},
                "stock": {"$first": "$stock"}
            }}
        ]
        return list(self.db[self.productos_name].aggregate(pipeline))
