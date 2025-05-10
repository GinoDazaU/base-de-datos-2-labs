from load import *
import math

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
        
        # TODO
        
        # Ordenar el score resultante de forma descendente
        result = sorted(score.items(), key= lambda tup: tup[1], reverse=True)
        # retornamos los k documentos mas relevantes (de mayor similitud a la query)
        return result[:top_k] 
    