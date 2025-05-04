import csv

def dividir_csv(archivo_entrada, tamaños, carpeta_salida="."):
    with open(archivo_entrada, newline='', encoding='utf-8') as f:
        lector = list(csv.reader(f))
        encabezado = lector[0]
        filas = lector[1:]

    for tamaño in tamaños:
        archivo_salida = f"{carpeta_salida}/cities_{tamaño}k.csv"
        with open(archivo_salida, mode='w', newline='', encoding='utf-8') as f_out:
            escritor = csv.writer(f_out)
            escritor.writerow(encabezado)
            escritor.writerows(filas[:tamaño])
        print(f"{archivo_salida} creado con {tamaño} registros.")

# Uso
tamaños_deseados = [20000, 40000, 60000, 100000]
dividir_csv("cities.csv", tamaños_deseados)
