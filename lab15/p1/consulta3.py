from cassandra.cluster import Cluster
from datetime import datetime

cluster = Cluster(['127.0.0.1'])
session = cluster.connect('iot_keyspace')

hoy = datetime.now().strftime('%Y-%m-%d')

# este script muestra cuanto tiempo le queda a cada dato del sensor SENS001 de hoy
# convierte el TTL (que viene en segundos) a horas y dias para que sea mas facil de entender
# ayuda a saber cuanto falta para que cada dato se elimine solo

rows = session.execute("""
    SELECT sensor_id, event_time, measurement_type, value, TTL(value)
    FROM sensor_measurements
    WHERE sensor_id = 'SENS001'
      AND date = %s
""", (hoy,))

print("TTL en diferentes unidades (SENS001):")
for row in rows:
    ttl = row.ttl
    if ttl is not None:
        print(f"{row.measurement_type} | {row.event_time} | {row.value} | {ttl}s | {ttl/3600:.2f}h | {ttl/86400:.2f}d")
