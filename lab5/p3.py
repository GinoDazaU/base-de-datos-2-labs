import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv
import nltk

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

def preprocess(text: str):
    text = text.lower()
    tokens = nltk.word_tokenize(text) 
    filtered = [t for t in tokens if t.isalpha() and t not in stopwords_set]
    stemmed = [stemmer.stem(t) for t in filtered]
    return stemmed
