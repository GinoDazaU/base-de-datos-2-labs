import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv
from p5 import create_sql_query

load_dotenv()

def export_query_results(query, output_path, file_format='csv'):
    conn = psycopg2.connect(
        dbname=os.getenv("DBNAME"),
        user=os.getenv("DBUSER"),
        password=os.getenv("DBPASS"),
        host=os.getenv("DBHOST")
    )
    
    try:
        sql_query = create_sql_query(query)

        df = pd.read_sql(sql_query, conn)
        if file_format == 'csv':
            df.to_csv(output_path, index=False)
        elif file_format == 'json':
            df.to_json(output_path, orient='records', force_ascii=False)
        else:
            raise ValueError("Formato no soportado. Usa 'csv' o 'json'.")
        print(f"Consulta exportada a {output_path} en formato {file_format}")
    finally:
        conn.close()

query = "((educación OR ciencia) AND gobierno) OR ((México OR Perú) AND-NOT (China OR Chile)) OR (transformación AND sostenible OR startup)"

export_query_results(query, "data.csv", "csv")

export_query_results(query, "data.json", "json")
