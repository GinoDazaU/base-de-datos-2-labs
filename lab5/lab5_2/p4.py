from p3 import idx

test_queries = [
    "¿Cuáles son las últimas innovaciones en la banca digital y la tecnología financiera?",
    "evolución de la inflación y el crecimiento de la economía en los últimos años",
    "avances sobre sostenibilidad y energías renovables para el medio ambiente"
]

for test in test_queries:    
    results = idx.cosine_search(test['query'], test['top_k'])
    print(f"Top {test['top_k']} documentos más similares:") 
    for doc_id, score in results:
        print(f"Doc {doc_id}: {score:.3f}: ", idx.showDocument(doc_id))