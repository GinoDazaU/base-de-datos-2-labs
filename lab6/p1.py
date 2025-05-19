import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

# Datos
registros = [1000, 10000, 100000, 1000000, 10000000]
labels = ['1k', '10k', '100k', '1m', '10m']
tiempo_sin_indice = [1.23, 12.428, 166.779, 509.202, 5033.666]
tiempo_con_indice = [0.094, 0.377, 2.298, 337.237, 1375.336]

# Crear gráfico
plt.figure(figsize=(10, 6))
plt.plot(registros, tiempo_sin_indice, marker='o', label='No indexado', color='blue')
plt.plot(registros, tiempo_con_indice, marker='o', label='Indexado', color='red')

# Configurar escala logarítmica en X
plt.xscale('log')

# Etiquetas manuales en eje X
plt.xticks(registros, labels)

# Eje Y con formato de miles
plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))

# Títulos y leyenda
plt.title('Comparación de rendimiento: No indexado vs Indexado (pg_trgm)', fontsize=14)
plt.xlabel('Número de registros (escala log)', fontsize=12)
plt.ylabel('Tiempo (ms)', fontsize=12)
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.legend()
plt.tight_layout()
plt.show()
