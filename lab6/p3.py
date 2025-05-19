import matplotlib.pyplot as plt

# Datos del primer gráfico: tiempo vs cantidad de datos
datos = ['1k', '10k', '25k', '50k']
tiempo_sin_indice = [1.553, 5.250, 15.213, 23.004]
tiempo_con_indice = [0.0168, 0.0217, 0.892, 1.201]

plt.figure(figsize=(8, 5))
plt.plot(datos, tiempo_sin_indice, marker='o', label='Sin índice')
plt.plot(datos, tiempo_con_indice, marker='o', label='Con índice')
plt.title('Tiempo de ejecución según tamaño de datos')
plt.xlabel('Cantidad de datos')
plt.ylabel('Tiempo (segundos)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Datos del segundo gráfico: tiempo vs top-k
top_k = ['top 1', 'top 100', 'top 250', 'top 500']
tiempo_topk = [1.097, 1.241, 1.315, 1.392]

plt.figure(figsize=(8, 5))
plt.plot(top_k, tiempo_topk, marker='o', color='green')
plt.title('Tiempo de ejecución según top-k (50k registros, con índice)')
plt.xlabel('top-k')
plt.ylabel('Tiempo (segundos)')
plt.grid(True)
plt.tight_layout()
plt.show()
