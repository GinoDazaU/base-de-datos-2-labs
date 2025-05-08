from P1 import SecuentialRecorder
from P2 import AVL
import os
import time
import random
import matplotlib.pyplot as plt

# Configuración
CSV_FILE = "sales_dataset.csv"
NUM_SEARCHES = 100000
NUM_RANGE_SEARCHES = 100000
NUM_DELETIONS = 500

def generate_test_data(db):
    """Genera datos de prueba comunes para ambas estructuras"""
    test_data = {}
    
    # Obtener todos los IDs existentes
    with open(CSV_FILE, 'r') as f:
        record_count = sum(1 for _ in f)
    test_data['record_count'] = record_count
    test_data['all_ids'] = list(range(1, record_count + 1))
    
    # Generar IDs de búsqueda (los mismos para ambos)
    random.seed(42)  # Fijar semilla para reproducibilidad
    test_data['search_ids'] = random.choices(test_data['all_ids'], k=NUM_SEARCHES)
    
    # Generar rangos de búsqueda (los mismos para ambos)
    test_data['ranges'] = []
    for _ in range(NUM_RANGE_SEARCHES):
        start_id = random.randint(1, record_count // 2)
        end_id = start_id + random.randint(5, 50)
        test_data['ranges'].append((start_id, end_id))
    
    # Generar IDs para eliminación (los mismos para ambos)
    test_data['delete_ids'] = random.sample(test_data['all_ids'], min(NUM_DELETIONS, record_count))
    
    return test_data

def run_sequential_test(test_data):
    print("\n=== ARCHIVO SECUENCIAL ===")
    TEST_FILE = "p1_testing.dat"
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)
    db = SecuentialRecorder(TEST_FILE)

    results = {}

    # Inserción
    print("-> Inserción")
    start = time.perf_counter()
    db.load_from_csv(CSV_FILE)
    total_time = time.perf_counter() - start
    results['insert_total'] = total_time
    print(f"Tiempo total: {total_time:.4f}s")

    # Búsquedas
    print("-> Búsqueda")
    search_times = []
    start = time.perf_counter()
    for target in test_data['search_ids']:
        t0 = time.perf_counter()
        db.search_record(target)
        search_times.append(time.perf_counter() - t0)
    total_search_time = time.perf_counter() - start
    results['search_total'] = total_search_time
    results['search_avg'] = (sum(search_times)/len(search_times)) * 1000
    print(f"Tiempo total: {total_search_time:.4f}s | Avg: {results['search_avg']:.6f}ms")

    # Rango
    print("-> Búsqueda por rango")
    range_times = []
    start = time.perf_counter()
    for start_id, end_id in test_data['ranges']:
        t0 = time.perf_counter()
        db.search_range(start_id, end_id)
        range_times.append(time.perf_counter() - t0)
    total_range_time = time.perf_counter() - start
    results['range_total'] = total_range_time
    results['range_avg'] = (sum(range_times)/len(range_times)) * 1000
    print(f"Tiempo total: {total_range_time:.4f}s | Avg: {results['range_avg']:.6f}ms")

    # Eliminación
    print("-> Eliminación")
    delete_times = []
    start = time.perf_counter()
    for target_id in test_data['delete_ids']:
        t0 = time.perf_counter()
        db.delete_record(target_id)
        delete_times.append(time.perf_counter() - t0)
    total_delete_time = time.perf_counter() - start
    results['delete_total'] = total_delete_time
    results['delete_avg'] = (sum(delete_times)/len(delete_times)) * 1000
    print(f"Tiempo total: {total_delete_time:.4f}s | Avg: {results['delete_avg']:.6f}ms")

    return results

def run_avl_test(test_data):
    print("\n=== ÁRBOL AVL ===")
    TEST_FILE = "p2_testing.dat"
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)
    db = AVL(TEST_FILE)

    results = {}

    # Inserción
    print("-> Inserción")
    start = time.perf_counter()
    db.load_from_csv(CSV_FILE)
    total_time = time.perf_counter() - start
    results['insert_total'] = total_time
    print(f"Tiempo total: {total_time:.4f}s")

    # Búsqueda
    print("-> Búsqueda")
    search_times = []
    start = time.perf_counter()
    for target in test_data['search_ids']:
        t0 = time.perf_counter()
        db.search(target)
        search_times.append(time.perf_counter() - t0)
    total_search_time = time.perf_counter() - start
    results['search_total'] = total_search_time
    results['search_avg'] = (sum(search_times)/len(search_times)) * 1000
    print(f"Tiempo total: {total_search_time:.4f}s | Avg: {results['search_avg']:.6f}ms")

    # Rango
    print("-> Búsqueda por rango")
    range_times = []
    start = time.perf_counter()
    for start_id, end_id in test_data['ranges']:
        t0 = time.perf_counter()
        db.range_search(start_id, end_id)
        range_times.append(time.perf_counter() - t0)
    total_range_time = time.perf_counter() - start
    results['range_total'] = total_range_time
    results['range_avg'] = (sum(range_times)/len(range_times)) * 1000
    print(f"Tiempo total: {total_range_time:.4f}s | Avg: {results['range_avg']:.6f}ms")

    # Eliminación
    print("-> Eliminación")
    delete_times = []
    start = time.perf_counter()
    for target_id in test_data['delete_ids']:
        t0 = time.perf_counter()
        db.remove(target_id)
        delete_times.append(time.perf_counter() - t0)
    total_delete_time = time.perf_counter() - start
    results['delete_total'] = total_delete_time
    results['delete_avg'] = (sum(delete_times)/len(delete_times)) * 1000
    print(f"Tiempo total: {total_delete_time:.4f}s | Avg: {results['delete_avg']:.6f}ms")

    return results

# Generar datos de prueba comunes
test_data = generate_test_data(None)

# Ejecutar pruebas
seq_results = run_sequential_test(test_data)
avl_results = run_avl_test(test_data)

# Gráfico comparativo
operations = ['Inserción', 'Búsqueda', 'Rango', 'Eliminación']
seq_totals = [seq_results['insert_total'], seq_results['search_total'],
              seq_results['range_total'], seq_results['delete_total']]
avl_totals = [avl_results['insert_total'], avl_results['search_total'],
              avl_results['range_total'], avl_results['delete_total']]

x = range(len(operations))
width = 0.35

plt.figure(figsize=(12, 6))
plt.bar([i - width/2 for i in x], seq_totals, width=width, label='Secuencial', color='skyblue')
plt.bar([i + width/2 for i in x], avl_totals, width=width, label='AVL', color='salmon')
plt.xticks(x, operations)
plt.ylabel('Tiempo total (segundos)')
plt.title('Comparación Justa: Tiempo Total por Operación\n(Mismos datos para ambas estructuras)')
plt.legend()
plt.grid(axis='y')

for i in range(len(operations)):
    plt.text(i - width/2, seq_totals[i], f"{seq_totals[i]:.2f}s", ha='center', va='bottom')
    plt.text(i + width/2, avl_totals[i], f"{avl_totals[i]:.2f}s", ha='center', va='bottom')

plt.tight_layout()
plt.savefig('comparacion_justa.png')
print("\nGráfico comparativo guardado como 'comparacion.png'")