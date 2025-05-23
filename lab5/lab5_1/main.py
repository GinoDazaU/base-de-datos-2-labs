# Integrantes:
# - Gino Jesús Daza Yalta
# - Renato Garcia Calle
# - Mikel Dan Bracamonte Toguchi

# pip install psycopg2-binary nltk scikit-learn pandas

# import nltk
# nltk.download('punkt')

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
import os
from dotenv import load_dotenv
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='pandas')

load_dotenv()

dbname = os.getenv("DBNAME")
dbuser = os.getenv("DBUSER")
dbpass = os.getenv("DBPASS")
dbhost = os.getenv("DBHOST")

def connect_db():
    conn = psycopg2.connect(
        dbname=dbname,
        user=dbuser,
        password=dbpass,
        host=dbhost
    )
    return conn

def fetch_data():
    conn = connect_db()
    query = "SELECT id, contenido FROM noticias;"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

noticias_df = fetch_data()

print(noticias_df)

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

from p5 import test as p5test

p5test(connect_db())

# Pregunta 7