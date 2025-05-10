import pandas as pd
import psycopg2
import nltk
import os
from dotenv import load_dotenv
from collections import Counter
import numpy as np

nltk.download('punkt')
nltk.download('punkt_tab')
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

def fetch_data(query):
    conn = connect_db()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def load_stopwords():
    conn = connect_db()
    query = "SELECT word FROM stopwords;"
    df = pd.read_sql(query, conn)
    conn.close()
    return set(df["word"])

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

def bow_to_vector(bow: dict, vocab: list) -> list:
    return [bow.get(word, 0) for word in vocab]

def cosine_similarity(vec1, vec2):
    a = np.array(vec1)
    b = np.array(vec2)
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

######################################################################

test_queries = [
    "¿Cuáles son las últimas innovaciones en la banca digital y la tecnología financiera?",
    "evolución de la inflación y el crecimiento de la economía en los últimos años",
    "avances sobre sostenibilidad y energías renovables para el medio ambiente"
]

def search(query, top_k=5):
    # --- Etapa 1: Filtrado inicial ---
    consulta_bow = compute_bow(query)
    if not consulta_bow:
        return pd.DataFrame(columns=["id", "contenido", "similarity"])
    
    # Palabras clave
    palabras_clave = list(consulta_bow.keys())
    condiciones_sql = " OR ".join([f"contenido ILIKE '%{pal}%'" for pal in palabras_clave])

    # Usando operadores OR para buscar documentos con alguna de estas palabras clave
    sql = f"""
        SELECT id, contenido FROM noticias 
        WHERE {condiciones_sql}
    """
    df = fetch_data(sql)

    if df.empty:
        return pd.DataFrame(columns=["id", "contenido", "similarity"])

    # --- Etapa 2: Ordenamiento por relevancia ---
    document_bows = [compute_bow(texto) for texto in df["contenido"]]

    vocab = set(consulta_bow.keys())
    for bow in document_bows:
        vocab.update(bow.keys())
    vocab = sorted(list(vocab))

    consulta_vector = bow_to_vector(consulta_bow, vocab)
    document_vectors = [bow_to_vector(bow, vocab) for bow in document_bows]

    # Similitud de coseno
    similitudes = [cosine_similarity(consulta_vector, doc_vector) for doc_vector in document_vectors]

    #Ordenando y resultado final
    df["similarity"] = similitudes
    df_ordenado = df.sort_values(by="similarity", ascending=False).head(top_k)

    return df_ordenado

for query in test_queries:
    results = search(query, top_k=3)
    print(f"Probando consulta: '{query}'")
    for _, row in results.iterrows():
        print(f"\nID: {row['id']}")
        print(f"Similitud: {row['similarity']:.3f}")
        print(f"Texto: {row['contenido'][:200]}...")
    print("-" * 50)
