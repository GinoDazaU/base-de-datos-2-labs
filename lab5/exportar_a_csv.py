import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv('C:/Users/renat/OneDrive/Documentos/2025/UTEC/2025-I/BDII/BDII-Labstrio/base-de-datos-2-labs/lab5/environment.env')

def export_query_to_csv(query, output_path):
    conn = psycopg2.connect(
        dbname=os.getenv("DBNAME"),
        user=os.getenv("DBUSER"),
        password=os.getenv("DBPASS"),
        host=os.getenv("DBHOST")
    )
    
    try:
        df = pd.read_sql(query, conn)
        df.to_csv(output_path, index=False)
        print(f"Consulta exportada a {output_path}")
    finally:
        conn.close()

query = "SELECT * FROM noticias_mitad;"
export_query_to_csv(query, "noticias_mitad.csv")
