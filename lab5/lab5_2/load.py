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
    query = "SELECT id, contenido, bag_of_words FROM noticias;"
    df = pd.read_sql(query, conn)
    df['bag_of_words'] = df['bag_of_words'].apply(json.loads)
    conn.close()
    return df

noticias_df = fetch_data()