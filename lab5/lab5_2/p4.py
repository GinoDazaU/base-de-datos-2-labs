from p2 import InvertedIndex

idx = InvertedIndex()
idx.build_from_db()

test_queries = [
    {
        "query": "¿Cuáles son las últimas innovaciones en la banca digital y la tecnología financiera?",
        "top_k": 10
    },
    {
        "query": "evolución de la inflación y el crecimiento de la economía en los últimos años",
        "top_k": 20
    },
    {
        "query": "avances sobre sostenibilidad y energías renovables para el medio ambiente",
        "top_k": 15
    }
]

for test in test_queries:    
    results = idx.cosine_search(test['query'], test['top_k'])
    print(f"Consulta: {test['query']}")
    print(f"Top {test['top_k']} documentos más similares:") 
    for doc_id, score in results:
        print(f"Doc {doc_id}, Score: {score:.3f}:")
        print(idx.showDocument(doc_id))