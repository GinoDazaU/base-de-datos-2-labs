import psycopg2
import pandas as pd

import os
from dotenv import load_dotenv
import json

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
    query = "SELECT id, contenido, bag_of_words FROM noticias;"
    df = pd.read_sql(query, conn)
    df['bag_of_words'] = df['bag_of_words'].apply(json.loads)
    conn.close()
    return df

noticias_df = fetch_data()