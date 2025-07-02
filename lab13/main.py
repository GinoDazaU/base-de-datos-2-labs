from mongo_handler import MongoDBHandler

# Crear instancia
mongo_handler = MongoDBHandler()

# URLs
categories_url = "https://dummyjson.com/products/categories"

# 1. Cargar categorías
mongo_handler.fetch_all_categories(categories_url)

# 2. Cargar productos
mongo_handler.fetch_all_products()
