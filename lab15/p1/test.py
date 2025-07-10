from cassandra.cluster import Cluster

cluster = Cluster(['127.0.0.1'])
session = cluster.connect('iot_keyspace')

rows = session.execute("""
    SELECT event_time, value, TTL(value)
    FROM sensor_measurements
    WHERE sensor_id = 'SENS001'
      AND date = '2025-07-03'
      AND measurement_type = 'humedad'
    LIMIT 5;
""")

for row in rows:
    data = row._asdict()
    print(f"{row.event_time} - {row.value}% - TTL: {data['ttl(value)']} segundos")

cluster.shutdown()
