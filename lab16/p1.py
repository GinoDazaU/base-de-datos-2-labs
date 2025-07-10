import redis
import struct

# Conectar a Redis
rc = redis.StrictRedis(host='localhost', port=6379, db=0)

# Crear (Insertar un par clave-valor)
rc.set('username:1', 'heider_cs')
rc.set('nombre:1', 'Heider Sanchez')
rc.set('pais:1', 'Perú')
rc.set('rol:1', 'Administrador')

# Leer (Obtener el valor de una clave)
nombre = rc.get('nombre')
print(f"Nombre: {nombre.decode('utf-8')}")

# Actualizar (Modificar el valor de una clave)
rc.set('rol', 'Operador')

# Eliminar (Eliminar un par clave-valor)
rc.delete('pais:1')