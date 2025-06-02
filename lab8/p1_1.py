import matplotlib.pyplot as plt

# Datos: búsqueda secuencial
dimensiones = [2, 4, 6, 8, 16, 32, 64]

secuencial = {
    '1k': [0.595, 1.241, 0.730, 0.976, 1.063, 1.246, 2.018],
    '10k': [7.141, 7.979, 8.830, 10.792, 11.671, 16.541, 16.854],
    '100k': [116.254, 104.227, 118.178, 128.300, 115.304, 135.735, 180.050],
    '1m': [314.686, 638.626, 731.028, 1125.836, 2226.859, 4399.862, 5198.966]
}

plt.figure(figsize=(10, 6))
for label, tiempos in secuencial.items():
    plt.plot(dimensiones, tiempos, marker='o', linestyle='--', label=f"{label} puntos")

plt.title("Tiempo de búsqueda KNN Secuencial")
plt.xlabel("Dimensión del vector")
plt.ylabel("Tiempo (ms)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
