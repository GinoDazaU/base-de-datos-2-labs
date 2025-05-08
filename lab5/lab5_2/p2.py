class InvertedIndex:
    def __init__(self):
        self.index = {}
        self.idf = {}
        self.length = {}

    def build_from_db(self):
        # Leer desde PostgreSQL todos los bag of words
        # Construir el índice invertido, el idf y la norma (longitud) de cada documento
        
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
        
        # TODO
        
        # Ordenar el score resultante de forma descendente
        result = sorted(score.items(), key= lambda tup: tup[1], reverse=True)
        # retornamos los k documentos mas relevantes (de mayor similitud a la query)
        return result[:top_k] 