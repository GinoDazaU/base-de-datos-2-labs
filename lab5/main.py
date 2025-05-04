# Integrantes:
# - Gino Jesús Daza Yalta
# - Renato Garcia Calle
# - Mikel Dan Bracamonte Toguchi

# pip install psycopg2-binary nltk scikit-learn pandas

import nltk
nltk.download('punkt')

"""
CREATE TABLE noticias (
    id SERIAL PRIMARY KEY,
    url TEXT,
    contenido TEXT,
    categoria VARCHAR(50),
    bag_of_words JSONB
);
"""


"""
CREATE TABLE stopwords (
    id SERIAL PRIMARY KEY,
    word TEXT UNIQUE NOT NULL
);
"""

# Luego cargar el dataset de noticias `news_es.csv` y el dataset de stopwords `stoplist_es.txt`

# Pregunta 1

# Para leer los datos desde python
 
import psycopg2
import pandas as pd

def connect_db():
    conn = psycopg2.connect(
        dbname="<DB>",
        user="<USER>",
        password="<PASSWORD>",
        host="<HOST>"
    )
    return conn

def fetch_data():
    conn = connect_db()
    query = "SELECT id, contenido FROM noticias;"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

noticias_df = fetch_data()

# Pregunta 3

def preprocess(text):
    # Implementar la función de preprocesamiento aquí
    pass

def compute_bow(text):
    # Implementar la función de cálculo de BOW aquí
    pass

# Pregunta 4

def update_bow_in_db(dataframe):
    # Implementar la función de actualización en la base de datos aquí
    pass

update_bow_in_db(noticias_df)

# Pregunta 5

# SELECT * FROM noticias WHERE bag_of_words ? 'keyword';

def apply_boolean_query(query):
    # Construir la condición de búsqueda a partir de la query booleana
    # Ejecutar la consulta en la base de datos
    # Retornar un DataFrame con los resultados
    return pd.DataFrame()

test_queries = [
    "transformación AND sostenible", # Consulta con AND
    "México OR Perú",  # Consulta con OR
    "México AND-NOT Perú",  # Consulta con AND-NOT
    "nonexistent term",  # no debería devolver resultados
]

for query in test_queries:
    print(f"Probando consulta: '{query}'")
    results = apply_boolean_query(query)

    if results.empty:
        print("No se encontraron documentos.")
    else:
        print("Resultados encontrados:")
        print(results[['id', 'text_column']].head())
    print("-" * 50)

# Pregunta 7