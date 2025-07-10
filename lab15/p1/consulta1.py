from cassandra.cluster import Cluster
from datetime import datetime
import time

start = time.time()

cluster = Cluster(['127.0.0.1'])
session = cluster.connect('iot_keyspace')

# Fecha actual (datos insertados hoy)
today = datetime.now().strftime('%Y-%m-%d')

# Hacemos la consulta solo para SENS001, humedad, y fecha de hoy
rows = session.execute("""
    SELECT event_time, value, TTL(value)
    FROM sensor_measurements
    WHERE sensor_id = %s
      AND date = %s
      AND measurement_type = %s
""", ('SENS001', today, 'humedad'))

print("Mediciones de humedad del ultimo dia (SENS001):")
n = 0
for row in rows:
    print(f"{row.event_time} - {row.value:.2f}% - TTL restante: {row.ttl} segundos")
    n += 1

print(f"⏱ Tiempo de respuesta: {time.time() - start:.3f} segundos")
print(f"Total de registros devueltos: {n}")

cluster.shutdown()
