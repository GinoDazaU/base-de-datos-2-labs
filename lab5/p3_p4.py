import pandas as pd
import psycopg2
import nltk
import json
import os
from dotenv import load_dotenv
from collections import Counter

nltk.download('punkt')
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

def load_stopwords():
    conn = connect_db()
    query = "SELECT word FROM stopwords;"
    df = pd.read_sql(query, conn)
    conn.close()
    return set(df["word"])

noticias_df = fetch_data()
stopwords_set = load_stopwords()
stemmer = nltk.SnowballStemmer("spanish")

def preprocess(text: str) -> list:
    text = text.lower()
    tokens = nltk.word_tokenize(text) 
    filtered = [t for t in tokens if t.isalpha() and t not in stopwords_set]
    stemmed = [stemmer.stem(t) for t in filtered]
    return stemmed

def compute_bow(text: str) -> dict:
    tokens = preprocess(text)
    freq = Counter(tokens)
    return dict(freq)

def update_bow_in_db(df: pd.DataFrame):
    conn = connect_db()
    cursor = conn.cursor()
    
    for index, row in df.iterrows():
        bow_json = json.dumps(compute_bow(row['contenido']))
        cursor.execute("""
            UPDATE noticias
            SET bag_of_words = %s
            WHERE id = %s;
        """, (bow_json, row['id']))
    
    conn.commit()
    cursor.close()
    conn.close()

update_bow_in_db(noticias_df)
