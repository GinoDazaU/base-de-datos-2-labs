from load import *
import json
from p1 import preprocess, stemmer
import math
from collections import Counter

def fetch_query(query):
    conn = connect_db()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

class InvertedIndex:
    def __init__(self):
        self.index = {}
        self.idf = {}
        self.length = {}

    def build_from_db(self):
        # leer los datos desde la base de datos
        noticias_df = fetch_data()
        noticias_id = noticias_df["id"].to_list()
        bag_of_words_list = noticias_df["bag_of_words"].tolist()

        n = len(noticias_id) # total de documentos
        
        df = {} # cantidad de documentos donde aparece cada palabr
        # inicializar los diccionarios del indice invertido y de las normas (vacios)
        self.index = {}
        self.length = {}

        # recorrer cada documento con su bag of words
        for doc_id, bow in zip(noticias_id, bag_of_words_list):
            norm = 0 # acumulador para la norma del documento
            for word, tf in bow.items(): # recorrer cada palabra y su frecuencia en el documento
                tf = 1 + math.log10(tf)
                if word not in self.index: # si la palabra no estaen el indice, se agrega
                    self.index[word] = [] 
                self.index[word].append((doc_id, tf)) # agregar el documento y su frecuencia al indice invertido
                df[word] = df.get(word, 0) + 1 #contar que esta palabra aparece en este documento
                norm += tf ** 2 # acumular el cuadrado del tf para calcular la norma

            self.length[doc_id] = math.sqrt(norm) # guardar la norma del documento

        for word, doc_freq in df.items(): # calcular el idf para cada palabra
            self.idf[word] = math.log10(n / doc_freq) #idf
    
    def L(self, word):
        word = stemmer.stem(word)
        return self.index.get(word, [])
  
    def cosine_search(self, query, top_k=5):  
        score = {}
        
        tokens = preprocess(query)

        query_tf = Counter(tokens)

        for token, qtf in query_tf.items():
            if token not in self.index:
                continue
            documents = self.index[token]
            idf = self.idf[token]
            wtq = (1 + math.log10(qtf))*idf
            for doc, tf in documents:
                if doc not in score:
                    score[doc] = 0
                wtd = tf*idf
                score[doc] += wtd*wtq
        
        for key, value in score.items():
            score[key] = value/self.length[key]
        
        # Ordenar el score resultante de forma descendente
        result = sorted(score.items(), key= lambda tup: tup[1], reverse=True)
        # retornamos los k documentos mas relevantes (de mayor similitud a la query)
        return result[:top_k]
    
    def showDocument(self, doc_id):
        noticia = fetch_query(f"SELECT id, contenido FROM noticias WHERE id = {doc_id}")
        return noticia

    def showDocuments(self, doc_ids):
        if not doc_ids:
            return ""
        condition = " OR ".join([f"id = {id[0]}" for id in doc_ids])
        noticias = fetch_query(f"SELECT id, contenido FROM noticias WHERE {condition}")
        return noticias
    
inverted_index = InvertedIndex()
inverted_index.build_from_db()
