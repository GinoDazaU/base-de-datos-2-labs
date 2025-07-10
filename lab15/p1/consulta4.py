from cassandra.cluster import Cluster
from datetime import datetime

cluster = Cluster(['127.0.0.1'])
session = cluster.connect('iot_keyspace')

hoy = datetime.now().strftime('%Y-%m-%d')

# este script encuentra los datos del sensor SENS001 que van a expirar en las proximas 24 horas
# revisa el ttl y muestra solo los que tienen menos de 86400 segundos
# sirve para saber que datos estan por borrarse y si hay que hacer backup o algo antes

rows = session.execute("""
    SELECT sensor_id, event_time, measurement_type, value, TTL(value)
    FROM sensor_measurements
    WHERE sensor_id = 'SENS001'
      AND date = %s
""", (hoy,))

print("Datos que expiran en las proximas 24 horas (SENS001):")
for row in rows:
    if row.ttl is not None and row.ttl < 86400:
        print(f"{row.event_time} - {row.measurement_type} - {row.value} - TTL: {row.ttl}s")
