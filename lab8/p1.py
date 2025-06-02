import matplotlib.pyplot as plt
import pandas as pd

# Datos del experimento corregidos
data = {
    "Dimensiones": [2, 4, 6, 8, 16, 32, 64],
    "KNN Sequential (ms)": [314.686, 638.626, 731.028, 1125.836, 2226.859, 4399.862, 5198.966],
    "KNN Indexed (ms)": [0.669, 44.927, 331.263, 749.338, 13731.943, 28329.920, 38453.571]
}

# Crear DataFrame
df = pd.DataFrame(data)

# Crear el gráfico
plt.figure(figsize=(10, 6))
plt.plot(df["Dimensiones"], df["KNN Sequential (ms)"], marker='o', label="KNN Secuencial", color='orange')
plt.plot(df["Dimensiones"], df["KNN Indexed (ms)"], marker='o', label="KNN con GiST (Indexado)", color='orangered')

# Título y etiquetas
plt.title("Comparación de tiempo de búsqueda KNN (Datos corregidos)")
plt.xlabel("Dimensión del vector")
plt.ylabel("Tiempo (ms)")
plt.grid(True)
plt.legend()
plt.tight_layout()

# Mostrar
plt.show()
