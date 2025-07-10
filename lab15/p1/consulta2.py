from cassandra.cluster import Cluster
from datetime import datetime, timedelta

cluster = Cluster(['127.0.0.1'])
session = cluster.connect('iot_keyspace')

ahora = datetime.now()
hace_una_hora = ahora - timedelta(hours=1)
hoy = ahora.strftime('%Y-%m-%d')

# este script busca valores anómalos (temperatura o humedad fuera de rango) en la ultima hora
# solo analiza los datos del sensor SENS001 y filtra en python los que esten fuera del rango permitido
# se usa para detectar fallos o condiciones raras en tiempo real

rows = session.execute("""
    SELECT sensor_id, event_time, measurement_type, value
    FROM sensor_measurements
    WHERE sensor_id = 'SENS001'
      AND date = %s
""", (hoy,))

print("Valores anómalos en la última hora (SENS001):")
for row in rows:
    if row.event_time >= hace_una_hora:
        if row.measurement_type == 'temperatura' and not (15 <= row.value <= 35):
            print(f"{row.event_time} - TEMPERATURA fuera de rango: {row.value}°C")
        elif row.measurement_type == 'humedad' and not (30 <= row.value <= 80):
            print(f"{row.event_time} - HUMEDAD fuera de rango: {row.value}%")
