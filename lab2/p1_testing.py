from p1 import SecuentialRecorder
import os
import time
import matplotlib.pyplot as plt

# Configuración inicial
if os.path.exists("p1_testing.dat"):
    os.remove("p1_testing.dat")

secuentialRecorder = SecuentialRecorder("p1_testing.dat")

# 1. Medición de inserción de registros
print("=== MEDICIÓN DE INSERCIÓN ===")
start_time = time.time()
secuentialRecorder.load_from_csv("sales_dataset.csv")
insert_time = time.time() - start_time
print(f"Tiempo total de inserción: {insert_time:.4f} segundos")

# 2. Medición de búsquedas específicas
print("\n=== MEDICIÓN DE BÚSQUEDAS ESPECÍFICAS ===")
search_ids = [1, 50, 100, 150, 200]  # IDs a buscar
search_times = []

for id in search_ids:
    start_time = time.time()
    result = secuentialRecorder.search_record(id)
    search_time = time.time() - start_time
    search_times.append(search_time)
    print(f"Búsqueda ID {id}: {search_time:.6f} segundos | {'Encontrado' if result else 'No encontrado'}")

# 3. Medición de búsqueda por rangos
print("\n=== MEDICIÓN DE BÚSQUEDA POR RANGOS ===")
ranges = [(1, 10), (50, 60), (100, 110), (150, 160), (200, 210)]
range_times = []

for r in ranges:
    start_time = time.time()
    results = secuentialRecorder.search_range(r[0], r[1])
    range_time = time.time() - start_time
    range_times.append(range_time)
    print(f"Rango {r[0]}-{r[1]}: {range_time:.6f} segundos | {len(results)} registros encontrados")

# 4. Medición de eliminación
print("\n=== MEDICIÓN DE ELIMINACIÓN ===")
delete_ids = [2, 51, 101, 151, 201]  # IDs a eliminar
delete_times = []

for id in delete_ids:
    start_time = time.time()
    success = secuentialRecorder.delete_record(id)
    delete_time = time.time() - start_time
    delete_times.append(delete_time)
    print(f"Eliminación ID {id}: {delete_time:.6f} segundos | {'Éxito' if success else 'Fallo'}")

# Generación de gráficas
plt.figure(figsize=(12, 8))

# Gráfica de búsquedas
plt.subplot(2, 2, 1)
plt.plot(search_ids, search_times, 'bo-')
plt.title('Tiempo de Búsqueda por ID')
plt.xlabel('ID')
plt.ylabel('Segundos')
plt.grid(True)

# Gráfica de rangos
plt.subplot(2, 2, 2)
plt.plot([f"{r[0]}-{r[1]}" for r in ranges], range_times, 'go-')
plt.title('Tiempo de Búsqueda por Rango')
plt.xlabel('Rango de IDs')
plt.ylabel('Segundos')
plt.grid(True)

# Gráfica de eliminación
plt.subplot(2, 2, 3)
plt.plot(delete_ids, delete_times, 'ro-')
plt.title('Tiempo de Eliminación por ID')
plt.xlabel('ID')
plt.ylabel('Segundos')
plt.grid(True)

# Gráfica comparativa
plt.subplot(2, 2, 4)
operations = ['Inserción', 'Búsqueda Prom', 'Rango Prom', 'Eliminación Prom']
times = [
    insert_time,
    sum(search_times)/len(search_times),
    sum(range_times)/len(range_times),
    sum(delete_times)/len(delete_times)
]
plt.bar(operations, times, color=['blue', 'green', 'orange', 'red'])
plt.title('Comparación de Operaciones')
plt.ylabel('Segundos promedio')
plt.grid(True)

plt.tight_layout()
plt.savefig('performance_results.png')
plt.show()

print("\n=== RESULTADOS GUARDADOS EN performance_results.png ===")