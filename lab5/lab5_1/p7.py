import pandas as pd
import psycopg2
import nltk
import json
import os
from dotenv import load_dotenv
from collections import Counter
from nltk.stem import WordNetLemmatizer
from nltk.stem import SnowballStemmer
import time

nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('wordnet')
nltk.download('omw-1.4')

load_dotenv(dotenv_path='C:/Users/renat/OneDrive/Documentos/2025/UTEC/2025-I/BDII/BDII-Labstrio/base-de-datos-2-labs/lab5/environment.env')

dbname = os.getenv("DBNAME")
dbuser = os.getenv("DBUSER")
dbpass = os.getenv("DBPASS")
dbhost = os.getenv("DBHOST")

print(f"DBNAME: {dbname}, DBUSER: {dbuser}, DBPASS: {dbpass}, DBHOST: {dbhost}")

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

def load_stopwords():
    conn = connect_db()
    query = "SELECT word FROM stopwords;"
    df = pd.read_sql(query, conn)
    conn.close()
    return set(df["word"])

noticias_df = fetch_data()
stopwords_set = load_stopwords()

stemmer = SnowballStemmer("spanish")
lemmatizer = WordNetLemmatizer()

def preprocess_stemming(text: str) -> list:
    text = text.lower()
    tokens = nltk.word_tokenize(text, language='spanish')
    filtered = [t for t in tokens if t.isalpha() and t not in stopwords_set]
    stemmed = [stemmer.stem(t) for t in filtered]
    return stemmed

def preprocess_lemmatization(text: str) -> list:
    text = text.lower()
    tokens = nltk.word_tokenize(text, language='spanish')
    filtered = [t for t in tokens if t.isalpha() and t not in stopwords_set]
    lemmatized = [lemmatizer.lemmatize(t) for t in filtered]
    return lemmatized

def compute_bow(text: str, method: str) -> dict:
    if method == 'stemming':
        tokens = preprocess_stemming(text)
    elif method == 'lemmatization':
        tokens = preprocess_lemmatization(text)
    freq = Counter(tokens)
    return dict(freq)

def update_bow_in_db(news_id: int, bow_data: dict):
    conn = connect_db()
    cur = conn.cursor()
    query = """
        UPDATE noticias
        SET bag_of_words = %s
        WHERE id = %s;
    """
    cur.execute(query, (json.dumps(bow_data), news_id))
    conn.commit()
    cur.close()
    conn.close()


def process_and_save_bow(df: pd.DataFrame, method: str):
    start_time = time.time()

    for index, row in df.iterrows():
        bow = compute_bow(row['contenido'], method)
        update_bow_in_db(row['id'], bow)

    end_time = time.time()
    return end_time - start_time


def compare_and_save():
    print("Procesando y guardando con Stemming...")
    time_stem = process_and_save_bow(noticias_df, "stemming")
    print(f"Stemming completado en {time_stem:.2f} segundos")

    print("Procesando y guardando con Lemmatización...")
    time_lemma = process_and_save_bow(noticias_df, "lemmatization")
    print(f"Lematización completada en {time_lemma:.2f} segundos")

compare_and_save()
