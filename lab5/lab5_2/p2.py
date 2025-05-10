from load import *
import json
from p1 import preprocess
import math
from collections import Counter

class InvertedIndex:
    def __init__(self):
        self.index = {}
        self.idf = {}
        self.length = {}

    def build_from_db(self):
        noticias_df = fetch_data()
        noticias_id = noticias_df["id"].to_list()
        bag_of_words_list = noticias_df["bag_of_words"].tolist()

        n = len(noticias_id)
        df = {}
        self.index = {}
        self.length = {}

        for doc_id, bow in zip(noticias_id, bag_of_words_list):
            norm = 0
            for word, tf in bow.items():
                if word not in self.index:
                    self.index[word] = []
                self.index[word].append((doc_id, tf))
                df[word] = df.get(word, 0) + 1
                norm += tf ** 2

            self.length[doc_id] = math.sqrt(norm)

        for word, doc_freq in df.items():
            self.idf[word] = math.log(n / doc_freq)
    
    def L(self, word):
        return self.index.get(word, [])
  
    def cosine_search(self, query, top_k=5):  
        score = {}
        # No es necesario usar vectores numericos del tamaño del vocabulario
        # Guiarse del algoritmo visto en clase
        # Se debe calcular el tf-idf de la query y de cada documento
        
        tokens = preprocess(query)

        query_tf = Counter(tokens)

        for token, qtf in query_tf.items():
            if token not in self.index:
                continue
            documents = self.index[token]
            idf = self.idf[token]
            wtq = (1 + math.log2(qtf))*idf
            for doc, tf in documents:
                if doc not in score:
                    score[doc] = 0
                wtd = tf*idf
                # wtd = (1 + math.log2(tf))*idf
                score[doc] += wtd*wtq
        
        for key, value in score.items():
            score[key] = value/self.length(key)
        
        # Ordenar el score resultante de forma descendente
        result = sorted(score.items(), key= lambda tup: tup[1], reverse=True)
        # retornamos los k documentos mas relevantes (de mayor similitud a la query)
        return result[:top_k]
    
    def showDocument(doc_id):
        noticias = fetch_data()
        for noticia in noticias:
            if noticia["id"] == doc_id:
                print(noticia["contenido"])
                break

    
inverted_index = InvertedIndex()
inverted_index.build_from_db()