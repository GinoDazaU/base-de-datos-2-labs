
# Integrantes: Mikel Bracamonte, Gino Daza

"""
IMPLEMENTACION DE STATIC HASHING CON DESBORDAMIENTO ENCADENADO

Estructura del Bucket:
- Cada bucket contiene:
  * size: entero (4 bytes) - cantidad de registros actuales
  * next_bucket: entero (4 bytes) - indice del siguiente bucket en la cadena (-1 si no hay)
  * prev_bucket: entero (4 bytes) - indice del bucket anterior en la cadena (-1 si es principal)
  * records: 
    - Array de registros de tamaño fijo (block_factor)
    - Por fines practicos, cada registro solo contiene un id entero (4 bytes)
    - [Nota: Gracias al diseño modular enseñada por el profesor en la clase de recuperacion,
       se podria extender fácilmente para añadir mas campos a los registros
       modificando solo la clase Record, sin afectar el resto de la implementación]

Clase StaticHashing:
- Gestiona el archivo binario con la estructura:
  * Metadata (12 bytes): 
    - max_buckets (4 bytes)
    - block_factor (4 bytes)
    - max_overflow (4 bytes)
  * Buckets principales (depende del factor de bloque)
  * Buckets de overflow (depende del usuario)

Algoritmos implementados:
1. Insercion:
   - Calcula posicion con hash (id % max_buckets)
   - Busca espacio en el bucket principal
   - Si esta lleno, recorre la cadena de overflow
   - Si no hay espacio, crea nuevo bucket de overflow
   - Si se alcanza max_overflow, ejecuta rehashing

2. Busqueda:
   - Calcula posicion con hash (id % max_buckets)
   - Busca en el bucket principal
   - Si no esta, recorre la cadena de overflow
   - Retorna None si no se encuentra

3. Eliminacion:
   - Busca el registro igual que en busqueda
   - Si lo encuentra, lo elimina manteniendo la integridad
   - Reorganiza la cadena si quedan buckets vacios
"""



import struct
import os


class Record:

    FORMAT = "i"
    SIZE = struct.calcsize(FORMAT)

    def __init__(self, id = 0):
        self.id = id
    
    def pack(self):
        return struct.pack(self.FORMAT, self.id)

    @staticmethod
    def unpack(data_buffer):
        id = struct.unpack(Record.FORMAT, data_buffer)[0]
        return Record(id)

class Bucket:

    def __init__(self, block_factor):
        self.size = 0
        self.next_bucket = -1
        self.prev_bucket = -1  # se usara para la eliminacion
        self.records = [Record() for _ in range(block_factor)]

    def add_record(self, record: Record):
        if not self.isFull():
            self.records[self.size] = record
            self.size += 1
        else:
            raise Exception("Bucket lleno.")
        
    def isFull(self):
        return self.size == len(self.records)
    
    def pack(self):
        bucket_buffer = struct.pack("i", self.size)
        bucket_buffer += struct.pack("i", self.next_bucket)
        bucket_buffer += struct.pack("i", self.prev_bucket)
        for record in self.records:
            bucket_buffer += record.pack()
        return bucket_buffer
    
    @staticmethod
    def unpack(bucket_buffer, block_factor):
        size, next_bucket, prev_bucket = struct.unpack("iii", bucket_buffer[:12])
        bucket = Bucket(block_factor)
        bucket.size = size
        bucket.next_bucket = next_bucket
        bucket.prev_bucket = prev_bucket
        for i in range(size):
            init = 12 + i * Record.SIZE
            end = init + Record.SIZE
            record_buffer = bucket_buffer[init:end]
            record = Record.unpack(record_buffer)
            bucket.records[i] = record
        return bucket
    
    @staticmethod
    def calcsize(block_factor):
        return struct.calcsize("iii") + Record.SIZE * block_factor

class StaticHashing:

    def __init__(self, filename, max_buckets, block_factor, max_overflow):
        self.filename = filename
        
        # Si el archivo existe se leera la metadata
        if os.path.exists(filename):
            with open(filename, 'rb') as file:
                max_buckets_buffer = file.read(4)
                block_factor_buffer = file.read(4)
                max_overflow_buffer = file.read(4)
                self.max_buckets = struct.unpack("i", max_buckets_buffer)[0]
                self.block_factor = struct.unpack("i", block_factor_buffer)[0]
                self.max_overflow = struct.unpack("i", max_overflow_buffer)[0]
        else:
            if None in (max_buckets, block_factor, max_overflow):
                raise ValueError("Debe proporcionar parametros para crear un nuevo archivo")
            self.max_buckets = max_buckets
            self.block_factor = block_factor
            self.max_overflow = max_overflow
            self.buildFile()
    
    def buildFile(self):
        if os.path.exists(self.filename):
            raise Exception("El archivo ya existe")
        with open(self.filename, "wb") as file:
            metadata_buffer = struct.pack("iii", self.max_buckets, self.block_factor, self.max_overflow)
            file.write(metadata_buffer)
            for _ in range(self.max_buckets):
                bucket = Bucket(self.block_factor)
                file.write(bucket.pack())

    def insertBucket(self, index, bucket: Bucket):
        with open(self.filename, "r+b") as file:
            BUCKET_SIZE = Bucket.calcsize(self.block_factor)
            file.seek(struct.calcsize("iii") + index * BUCKET_SIZE)
            file.write(bucket.pack())

    def readBucket(self, index):
        with open(self.filename, "rb") as file:
            BUCKET_SIZE = Bucket.calcsize(self.block_factor)
            file.seek(struct.calcsize("iii") + index * BUCKET_SIZE)
            bucket_buffer = file.read(BUCKET_SIZE)
            return Bucket.unpack(bucket_buffer, self.block_factor)
        
    #  Metodo usado para saber donde ira un nuevo overflow bucket
    def getLastIndex(self):
        with open(self.filename, "rb") as file:
            BUCKET_SIZE = Bucket.calcsize(self.block_factor)
            file.seek(0, 2)
            file_size = file.tell()
            metadata_size = struct.calcsize("iii")
            
            return (file_size - metadata_size) // BUCKET_SIZE - 1


    def insertRecord(self, record: Record):
        """
        Inserta un registro manteniendo la lista doblemente enlazada:
        1. Busca espacio en el bucket principal
        2. Si esta lleno, recorre la cadena de overflow
        3. Si no hay espacio, crea nuevo bucket de overflow
        4. Mantiene actualizados los punteros next y prev
        """
        if self.searchRecord(record.id) != None:
            print("El registro ya existe")
            return False

        current_index = record.id % self.max_buckets
        bucket = self.readBucket(current_index)
        prev_index = -1  # Para el bucket principal, prev es -1

        # Intentar insertar en el bucket principal
        if not bucket.isFull():
            bucket.add_record(record)
            self.insertBucket(current_index, bucket)
            print(f"Registro insertado correctamente en la posición {current_index}")
            return True

        # Seguir la cadena de overflow si el bucket principal está lleno
        local_overflow = 0
        while bucket.isFull() and bucket.next_bucket != -1:
            prev_index = current_index
            current_index = bucket.next_bucket
            bucket = self.readBucket(current_index)
            local_overflow += 1

        # Si encontramos un bucket con espacio en la cadena
        if not bucket.isFull():
            bucket.add_record(record)
            self.insertBucket(current_index, bucket)
            print(f"Registro insertado correctamente en la posición {current_index}")
            return True
        
        # Si necesitamos crear un nuevo bucket de overflow
        elif local_overflow < self.max_overflow:
            new_bucket = Bucket(self.block_factor)
            new_bucket.add_record(record)
            new_bucket.prev_bucket = current_index  # Establecer puntero al anterior
            new_index = self.getLastIndex() + 1
            
            # Actualizar el último bucket de la cadena
            bucket.next_bucket = new_index
            self.insertBucket(current_index, bucket)
            
            # Escribir el nuevo bucket
            with open(self.filename, "ab") as file:
                file.write(new_bucket.pack())
            
            print(f"Registro insertado correctamente en la posición {new_index}")
            return True
        
        # Si hemos alcanzado el máximo de overflow, hacer rehashing
        else:
            self.rehash()
            return self.insertRecord(record)  # Reintentar la insercion después del rehashing
    
    def rehash(self):
        print("Iniciando rehashing...")
        
        # 1. Leer todos los registros existentes
        all_records = []
        for i in range(self.getLastIndex() + 1):
            bucket = self.readBucket(i)
            all_records.extend(bucket.records[:bucket.size])
        
        # 2. Duplicar el tamaño de la tabla principal
        new_max_buckets = self.max_buckets * 2
        new_max_overflow = self.max_overflow * 2
        
        # 3. Crear un archivo temporal
        temp_filename = self.filename + ".tmp"
        temp_hashing = StaticHashing(temp_filename, new_max_buckets, self.block_factor, new_max_overflow)
        

        # 4. Reinsertar todos los registros
        for record in all_records:
            temp_hashing.insertRecord(record)
        
        # 5. Reemplazar archivos
        os.remove(self.filename)
        os.rename(temp_filename, self.filename)
        
        # 6. Actualizar instancia
        self.__init__(self.filename, new_max_buckets, self.block_factor, new_max_overflow)
        print(f"Rehashing completado. Nuevo tamaño: {new_max_buckets} buckets")

        
    # Busca un registro por su ID.
    # Retorna el Record si lo encuentra, retorna None si no existe.
    def searchRecord(self, id):
        current_index = id % self.max_buckets
        
        # Traer el bucket principal a ram
        bucket = self.readBucket(current_index)
        
        # Buscar en el bucket principal
        for record in bucket.records[:bucket.size]:
            if record.id == id:
                return record
        
        # Si no esta en el principal, buscar en los buckets de overflow
        while bucket.next_bucket != -1:
            current_index = bucket.next_bucket
            bucket = self.readBucket(current_index)
            
            for record in bucket.records[:bucket.size]:
                if record.id == id:
                    return record
        
        return None
    

    """
    Elimina un registro manteniendo la estructura de lista doblemente enlazada:
    1. Busca el registro en la cadena de buckets (principal -> overflows)
    2. Si se encuentra:
       - En buckets normales: elimina moviendo el ultimo registro al hueco
       - Si queda vacio un bucket de overflow:
         a) Si es el ultimo: trunca el archivo
         b) Si está en medio: mueve el ultimo bucket al hueco vacio, 
            actualizando todos los punteros (next/prev) afectados
    3. Los buckets principales nunca se eliminan (solo se vacian)
    """
    def deleteRecord(self, id):
        found = self._findRecordAndBucket(id)
        if not found:
            return False
        
        bucket, index, bucket_index = found
        
        # Eliminar el registro (swap con el ultimo)
        if index != bucket.size - 1:
            bucket.records[index] = bucket.records[bucket.size - 1]
        bucket.size -= 1
        
        # Si el bucket quedo vacio y es de overflow
        if bucket.size == 0 and bucket_index >= self.max_buckets:
            self._removeEmptyBucket(bucket_index)
        else:
            self.insertBucket(bucket_index, bucket)
        
        return True

    # Busca un registro y retorna (bucket, index, bucket_index)
    def _findRecordAndBucket(self, id):
        current_index = id % self.max_buckets
        bucket = self.readBucket(current_index)
        
        while True:
            # Buscar en el bucket actual
            for i in range(bucket.size):
                if bucket.records[i].id == id:
                    return (bucket, i, current_index)
            
            # Seguir la cadena
            if bucket.next_bucket == -1:
                break
            current_index = bucket.next_bucket
            bucket = self.readBucket(current_index)
        
        return None

    # Elimina un bucket de overflow vacio
    def _removeEmptyBucket(self, empty_index):  
        empty_bucket = self.readBucket(empty_index)
        
        # 1. Actualizar el bucket anterior
        if empty_bucket.prev_bucket != -1:
            prev_bucket = self.readBucket(empty_bucket.prev_bucket)
            prev_bucket.next_bucket = empty_bucket.next_bucket
            self.insertBucket(empty_bucket.prev_bucket, prev_bucket)
        
        # 2. Actualizar el bucket siguiente (si existe)
        if empty_bucket.next_bucket != -1:
            next_bucket = self.readBucket(empty_bucket.next_bucket)
            next_bucket.prev_bucket = empty_bucket.prev_bucket
            self.insertBucket(empty_bucket.next_bucket, next_bucket)
        
        # 3. Si es el ultimo bucket, decirle al os que el espacio del ultimo bucket esta libre (truncar)
        if empty_index == self.getLastIndex():
            self._truncateFile()
        else:
            # 4. Si no es el ultimo, mover el ultimo bucket a esta posición
            last_index = self.getLastIndex()
            last_bucket = self.readBucket(last_index)
            
            # Copiar el ultimo bucket al espacio vacio
            self.insertBucket(empty_index, last_bucket)
            
            # Actualizar punteros de los vecinos del bucket movido
            if last_bucket.prev_bucket != -1:
                prev = self.readBucket(last_bucket.prev_bucket)
                prev.next_bucket = empty_index
                self.insertBucket(last_bucket.prev_bucket, prev)
            
            if last_bucket.next_bucket != -1:
                next = self.readBucket(last_bucket.next_bucket)
                next.prev_bucket = empty_index
                self.insertBucket(last_bucket.next_bucket, next)
            
            self._truncateFile()

    # Trunca el archivo eliminando buckets vacios al final
    def _truncateFile(self):
        
        last_index = self.getLastIndex()
        while last_index >= self.max_buckets:
            bucket = self.readBucket(last_index)
            if bucket.size > 0 or bucket.next_bucket != -1:
                break
            last_index -= 1
        
        new_size = struct.calcsize("iii") + (last_index + 1) * Bucket.calcsize(self.block_factor)
        with open(self.filename, 'r+b') as file:
            file.truncate(new_size)

#---------------------------------
#             TESTING
#---------------------------------

# Funcion para imprimir la estructura de los buckets
def printStructure(hashing: StaticHashing):
    print("\n=== Estructura del Archivo ===")
    print(f"Buckets principales: {hashing.max_buckets}")
    print(f"Factor de bloque: {hashing.block_factor}")
    print(f"Máximo overflow: {hashing.max_overflow}")
    
    total_buckets = hashing.getLastIndex() + 1
    print(f"\nTotal buckets (incluyendo overflow): {total_buckets}\n")
    
    # Encabezado de la tabla
    print(f"{'#Bucket':<10}{'IDs':<20}{'Overflow Buckets (IDs)':<30}")
    print("-" * 60)
    
    for i in range(hashing.max_buckets):
        primary_bucket = hashing.readBucket(i)
        overflow_buckets = []
        overflow_ids = []
        
        current_overflow = primary_bucket.next_bucket
        while current_overflow != -1:
            overflow_bucket = hashing.readBucket(current_overflow)
            overflow_buckets.append(str(current_overflow))
            overflow_ids.extend([str(r.id) for r in overflow_bucket.records[:overflow_bucket.size]])
            current_overflow = overflow_bucket.next_bucket
        
        primary_ids = ", ".join([str(r.id) for r in primary_bucket.records[:primary_bucket.size]])
        overflow_info = ""
        
        if overflow_buckets:
            overflow_info = f"→ Buckets: {', '.join(overflow_buckets)} (IDs: {', '.join(overflow_ids)})"
        
        print(f"{i:<10}{primary_ids:<20}{overflow_info:<30}")
    



staticHashing = StaticHashing("data.dat", 8, 2, 3)

# Se insertan 100 id's distintos
# Se debe observar 100 id's del 1 al 100
for i in range(100):
    i += 1
    staticHashing.insertRecord(Record(i))

printStructure(staticHashing)

# Se intentan insertar 3 id's mas repetidos
# Debe salir un mensaje que el id ya existe
staticHashing.insertRecord(Record(3))
staticHashing.insertRecord(Record(4))
staticHashing.insertRecord(Record(5))

printStructure(staticHashing)

# Se eliminan el 3 4 5
# Se debe poder ver que faltan dichos registros (estaban en el bucket 3 4 5)

staticHashing.deleteRecord(3)
staticHashing.deleteRecord(4)
staticHashing.deleteRecord(5)

printStructure(staticHashing)

# Se eliminan todos los elemento de un bucket auxiliar intermedio
# Borramos del bucket 0, los elementos 48 y 64 que pertenecen al bucket 31
# Se debe poder ver como dicho bucket 31 no esta
# Se debe poder ver que el bucket auxiliar final 51 encadenado con el bucket principal 4 paso a la posicion 31
# El bucket 51 fue eliminado por completo truncando el archivo (diciendole al os que esta libre)

staticHashing.deleteRecord(48)
staticHashing.deleteRecord(64)

printStructure(staticHashing)

# Ahora a modo de prueba se intentara eliminar un bucket principal, este sera el bucket 6
# Para ello eliminaremos 6 y 22
# Se debe poder ver que ya no esta

staticHashing.deleteRecord(6)
staticHashing.deleteRecord(22)

printStructure(staticHashing)

# Ahora insertaremos el 6 y 22 otra vez
# Se debe poder ver que se inserto el 6 y 22 en el mismo lugar anterior sin problemas

staticHashing.insertRecord(Record(6))
staticHashing.insertRecord(Record(22))

printStructure(staticHashing)

# Con esto ya estaria los casos de eliminacion probados
