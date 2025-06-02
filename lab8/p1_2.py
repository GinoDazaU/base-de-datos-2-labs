import matplotlib.pyplot as plt

# Datos: búsqueda indexada con GiST
dimensiones = [2, 4, 6, 8, 16, 32, 64]

indexado = {
    '1k': [0.113, 0.187, 0.426, 0.442, 0.871, 0.889, 1.138],
    '10k': [0.205, 0.378, 1.094, 1.567, 5.213, 7.834, 15.850],
    '100k': [0.409, 2.965, 7.070, 19.823, 142.673, 268.317, 515.439],
    '1m': [0.669, 44.927, 331.263, 749.338, 13731.943, 28329.920, 38453.571]
}

plt.figure(figsize=(10, 6))
for label, tiempos in indexado.items():
    plt.plot(dimensiones, tiempos, marker='o', linestyle='-', label=f"{label} puntos")

plt.title("Tiempo de búsqueda KNN con índice GiST")
plt.xlabel("Dimensión del vector")
plt.ylabel("Tiempo (ms)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
