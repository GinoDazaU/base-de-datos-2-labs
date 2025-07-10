from cassandra.cluster import Cluster

cluster = Cluster(['127.0.0.1'])
session = cluster.connect('iot_keyspace')

rows = session.execute("""
    SELECT DISTINCT date FROM sensor_measurements
    WHERE sensor_id = 'SENS001'
      AND measurement_type = 'humedad';
""")

print("Fechas disponibles para 'SENS001' (humedad):")
for row in rows:
    print(row.date)


cluster.shutdown()