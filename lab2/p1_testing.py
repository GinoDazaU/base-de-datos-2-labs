from p1 import SecuentialRecorder
import os
import time
import random
import matplotlib.pyplot as plt

# Configuración
TEST_FILE = "p1_testing.dat"
CSV_FILE = "sales_dataset.csv"
NUM_SEARCHES = 10000
NUM_RANGE_SEARCHES = 10000
NUM_DELETIONS = 500

# Preparación
if os.path.exists(TEST_FILE):
    os.remove(TEST_FILE)

db = SecuentialRecorder(TEST_FILE)

# 1. Prueba de inserción (todo el CSV)
print("=== PRUEBA DE INSERCIÓN ===")
start_time = time.perf_counter()
db.load_from_csv(CSV_FILE)
total_insert_time = time.perf_counter() - start_time
print(f"Tiempo total: {total_insert_time:.4f}s")
print(f"Registros insertados: {db.main_size + db.aux_size}")
print(f"Tiempo promedio por inserción: {total_insert_time/(db.main_size + db.aux_size):.6f}s\n")

# 2. Prueba de búsquedas (1000 aleatorias)
print(f"=== PRUEBA DE BÚSQUEDAS ({NUM_SEARCHES}) ===")
search_times = []
existing_ids = [i for i in range(1, db.main_size + 1)]  # IDs existentes

for _ in range(NUM_SEARCHES):
    target_id = random.choice(existing_ids)
    start_time = time.perf_counter()
    db.search_record(target_id)
    search_times.append(time.perf_counter() - start_time)

print(f"Tiempo promedio: {sum(search_times)/len(search_times):.6f}s")
print(f"Tiempo máximo: {max(search_times):.6f}s")
print(f"Tiempo mínimo: {min(search_times):.6f}s\n")

# 3. Prueba de rangos (100 búsquedas)
print(f"=== PRUEBA DE RANGOS ({NUM_RANGE_SEARCHES}) ===")
range_times = []

for _ in range(NUM_RANGE_SEARCHES):
    start_id = random.randint(1, db.main_size//2)
    end_id = start_id + random.randint(5, 50)
    start_time = time.perf_counter()
    db.search_range(start_id, end_id)
    range_times.append(time.perf_counter() - start_time)

print(f"Tiempo promedio: {sum(range_times)/len(range_times):.6f}s\n")

# 4. Prueba de eliminación (300 registros)
print(f"=== PRUEBA DE ELIMINACIÓN ({NUM_DELETIONS}) ===")
delete_times = []
delete_candidates = random.sample(existing_ids, min(NUM_DELETIONS, len(existing_ids)))

for target_id in delete_candidates:
    start_time = time.perf_counter()
    db.delete_record(target_id)
    delete_times.append(time.perf_counter() - start_time)

print(f"Tiempo promedio: {sum(delete_times)/len(delete_times):.6f}s")
print(f"Registros eliminados: {len(delete_times)}\n")

# Gráfico comparativo
operations = ['Inserción', 'Búsqueda', 'Rango', 'Eliminación']
avg_times = [
    total_insert_time/(db.main_size + db.aux_size),
    sum(search_times)/len(search_times),
    sum(range_times)/len(range_times),
    sum(delete_times)/len(delete_times)
]

plt.figure(figsize=(10, 6))
bars = plt.bar(operations, avg_times, color=['blue', 'green', 'orange', 'red'])
plt.title('Comparación de Operaciones (Tiempos Promedio)')
plt.ylabel('Segundos')
plt.grid(axis='y')

# Añadir valores en las barras
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height,
             f'{height:.6f}s',
             ha='center', va='bottom')

plt.tight_layout()
plt.savefig('performance_comparison.png')
print("Gráfico guardado como 'performance_comparison.png'")