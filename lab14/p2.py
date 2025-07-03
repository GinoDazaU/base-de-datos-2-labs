import json, os
import pandas as pd
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/?directConnection=false")
db = client["text_analysis"]

def cargar_datos():
    coleccion = db["drake_lyrics"]

    path = "drake_lyrics/drake_data.json"

    with open(path, "r") as f:
        datos = json.load(f)

    coleccion.insert_many(datos)

    coleccion = db["milei_news"]

    path = "milei_news/"

    for root, dirs, files in os.walk(path):
        for filename in files:
            if filename.endswith(".json"):
                filepath = os.path.join(root, filename)
                try:
                    with open(filepath, "r") as f:
                        datos = json.load(f)

                        if isinstance(datos, list):
                            if datos:
                                coleccion.insert_many(datos)
                        elif isinstance(datos, dict):
                            coleccion.insert_one(datos)
                except Exception as e:
                    pass

# cargar_datos()

pd.set_option('display.max_colwidth', None)

def buscar_milei(input: str):
    coleccion = db["milei_news"]

    resultado = coleccion.find({
        "$text": {
            "$search": input
        }
    })

    docs = list(resultado)
    df = pd.DataFrame(docs)
    df = df.drop(columns=["_id", "title", "news_paper", "section", "credit", "tags", "published", "summary"])

    print(df.head())

def buscar_drake(input: str):
    coleccion = db["drake_lyrics"]

    resultado = coleccion.find({
        "$text": {
            "$search": input
        }
    })

    docs = list(resultado)
    df = pd.DataFrame(docs)
    df = df.drop(columns=["_id", "album", "lyrics_title", "track_views", "lyrics"])

    print(df.head())

buscar_milei("messi milei peron")