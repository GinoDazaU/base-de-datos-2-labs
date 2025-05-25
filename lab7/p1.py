from ucimlrepo import fetch_ucirepo 
import numpy as np
import pandas as pd
import heapq

# fetch dataset
dry_bean = fetch_ucirepo(id=602)
data = pd.concat([dry_bean.data.features, dry_bean.data.targets], axis=1)

# Seleccionar las columnas que corresponde a las 16 características
dataFeatures = data.iloc[:, :16]

# Normalizamos las columnas usando el minimo y el maximo
dataFeatures = (dataFeatures - dataFeatures.min()) / (dataFeatures.max() - dataFeatures.min())
dataFeatures.head()

def ED(P, Q):
    return np.sqrt(np.sum((P - Q) ** 2))

# Seleccionar N pares aleatorias de puntos y calcular la distancia entre ellos
N = 5000
data1 = dataFeatures.sample(n=N, random_state=1)
data2 = dataFeatures.sample(n=N, random_state=2)
distancias = np.zeros(N)
for i in range(N):
    distancias[i] = ED(data1.iloc[i], data2.iloc[i])

# Elaborar un histograma de las distancias
import matplotlib.pyplot as plt
plt.hist(distancias, bins = 50)
plt.show()

# Calculando los percentiles:
q1 = np.percentile(distancias, 1)
q5 = np.percentile(distancias, 5)
q10 = np.percentile(distancias, 10)
q25 = np.percentile(distancias, 25)
q50 = np.percentile(distancias, 50)

print(f"q1: {q1}, q5: {q5}, q10: {q10}, q25: {q25}, q50: {q50}")

# El percentil qn deberia devolver aproximadamente un n% de los datos
# Resultado: q1 = 0.12, q5 = 0.21, q10 = 0.27, q25 = 0.42, q50 = 0.66

def rangeSearch(data, query, radio):
    result = []
    for i in range(len(data)):
        if ED(data.iloc[i], query) <= radio:
            result.append(i)
    return result

# Radios seleccionados
radios = [0.12, 0.21, 0.27, 0.42, 0.66]
queries_idx = [15, 2084, 3560]

for qidx in queries_idx:
    query = dataFeatures.iloc[qidx]
    target = data.iloc[qidx, -1]
    for r in radios:
        result = rangeSearch(dataFeatures, query, r)        
        PR = 0
        for i in result:
            if data.iloc[i, -1] == target:
                PR += 1
        PR = PR / len(result)
        print("Query(" + str(qidx) + ") con radio = " + str(r) + ". Resultados: "+ str(len(result)) + " PR = " + str(PR))

def knnSearch(data, query, k):
    result = []
    for i in range(len(data)):
        dist = ED(data.iloc[i], query)
        result.append((i, dist))
    result = [i[0] for i in heapq.nsmallest(k, result, key=lambda x: x[1])]
    return result

Ks = [2, 4, 8, 16, 32]

for k in Ks:
    for qidx in queries_idx:
        target = data.iloc[qidx, -1]
        result = knnSearch(dataFeatures, dataFeatures.iloc[qidx], k)
        PR = 0
        for i in result:
            if data.iloc[i, -1] == target:
                PR += 1
        PR = PR / len(result)
        print(f"Query({qidx}), k = {k}. PR = {PR}")