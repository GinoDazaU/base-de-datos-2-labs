import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv('C:/Users/renat/OneDrive/Documentos/2025/UTEC/2025-I/BDII/BDII-Labstrio/base-de-datos-2-labs/lab5/environment.env')

def export_query_results(query, output_path, file_format='csv'):
    conn = psycopg2.connect(
        dbname=os.getenv("DBNAME"),
        user=os.getenv("DBUSER"),
        password=os.getenv("DBPASS"),
        host=os.getenv("DBHOST")
    )
    
    try:
        df = pd.read_sql(query, conn)
        if file_format == 'csv':
            df.to_csv(output_path, index=False)
        elif file_format == 'json':
            df.to_json(output_path, orient='records', lines=True, force_ascii=False)
        else:
            raise ValueError("Formato no soportado. Usa 'csv' o 'json'.")
        print(f"Consulta exportada a {output_path} en formato {file_format}")
    finally:
        conn.close()

export_query_results("SELECT * FROM noticias;", "noticias.csv", "csv")

export_query_results("SELECT * FROM noticias;", "noticias.json", "json")
