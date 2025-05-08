def search(query, top_k=5):
    pass

test_queries = [
    "¿Cuáles son las últimas innovaciones en la banca digital y la tecnología financiera?",
    "evolución de la inflación y el crecimiento de la economía en los últimos años",
    "avances sobre sostenibilidad y energías renovables para el medio ambiente"
]

for query in test_queries:
    results = search(query, top_k=3)
    print(f"Probando consulta: '{query}'")
    for _, row in results.iterrows():
        print(f"\nID: {row['id']}")
        print(f"Similitud: {row['similarity']:.3f}")
        print(f"Texto: {row['contenido'][:200]}...")
    print("-" * 50)
    