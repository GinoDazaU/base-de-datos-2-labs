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
        # Leer desde PostgreSQL todos los bag of words
        # Construir el índice invertido, el idf y la norma (longitud) de cada documento

        noticias_df = fetch_data()
        noticias_id = noticias_df["id"].to_list()

        bag_of_words = noticias_df["bag_of_words"].tolist()
        bag_of_words = json.dumps(bag_of_words, ensure_ascii=False, indent=2)


        print(bag_of_words)
        print(noticias_id)
        
        """
        indice  = {
            "word1": [("doc1", tf1), ("doc2", tf2), ("doc3", tf3)],
            "word2": [("doc2", tf2), ("doc4", tf4)],
            "word3": [("doc3", tf3), ("doc5", tf5)],
        } 
        idf  = {
            "word1": 3,
            "word2": 2,
            "word3": 2,
        } 
        length = {
            "doc1": 15.5236,
            "doc2": 10.5236,
            "doc3": 5.5236,
        }
        """
        pass
    
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