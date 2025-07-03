from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
import random
from datetime import datetime, timedelta

# Conexión a Cassandra
cluster = Cluster(['127.0.0.1'])  # Cambia si usas otro host o puerto
session = cluster.connect('my_keyspace')  # Reemplaza con tu keyspace

# Lista de sensores
sensors = [f"sensor_{i:03}" for i in range(1, 11)]
measurement_types = ['temperatura', 'humedad']

# Número total de registros
total_records = 10000

# Tiempo base: hace 7 días
now = datetime.utcnow()
start_time = now - timedelta(days=7)

# Tiempo entre muestras (30 segundos)
interval = timedelta(seconds=30)

# Preparar la consulta de inserción
query = """
INSERT INTO sensor_measurements (sensor_id, measurement_type, event_time, value)
VALUES (%s, %s, %s, %s)
USING TTL %s
"""

# Generar e insertar datos
for i in range(total_records):
    sensor_id = random.choice(sensors)
    measurement_type = random.choice(measurement_types)

    # Tiempo de la muestra: incremental desde start_time
    offset_seconds = i * 30
    event_time = start_time + timedelta(seconds=offset_seconds)

    # Valor según tipo
    if measurement_type == 'temperatura':
        value = round(random.uniform(15, 35), 2)
    else:  # humedad
        value = round(random.uniform(30, 80), 2)

    # TTL entre 7 y 30 días (en segundos)
    ttl_days = random.choice([7, 15, 30])
    ttl_seconds = ttl_days * 86400

    session.execute(query, (sensor_id, measurement_type, event_time, value, ttl_seconds))

    if i % 1000 == 0:
        print(f"{i} registros insertados...")

print("Inserción funciona.")
