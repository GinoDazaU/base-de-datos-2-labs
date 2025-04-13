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
        for record in self.records:
            bucket_buffer += record.pack()
        return bucket_buffer
    
    @staticmethod
    def unpack(bucket_buffer, block_factor):
        size, next_bucket = struct.unpack("ii", bucket_buffer[:8])
        bucket = Bucket(block_factor)
        bucket.size = size
        bucket.next_bucket = next_bucket
        for i in range(size):
            init = 8 + i * Record.SIZE
            end = init + Record.SIZE
            record_buffer = bucket_buffer[init:end]
            record = Record.unpack(record_buffer)
            bucket.records[i] = record
        return bucket
    
    @staticmethod
    def calcsize(block_factor):
        return struct.calcsize("ii") + Record.SIZE * block_factor

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
        current_index = record.id % self.max_buckets
        bucket = self.readBucket(current_index)

        # Intentar insertar en el bucket principal
        if not bucket.isFull():
            bucket.add_record(record)
            self.insertBucket(current_index, bucket)
            print(f"Registro insertado correctamente en la posición {current_index}")
            return True

        # Seguir la cadena de overflow si el bucket principal esta lleno
        local_overflow = 0
        while bucket.isFull() and bucket.next_bucket != -1:
            current_index = bucket.next_bucket
            bucket = self.readBucket(current_index)
            local_overflow += 1

        # Si encontramos un bucket con espacio en la cadena
        if not bucket.isFull():
            bucket.add_record(record)
            self.insertBucket(current_index, bucket)
            return True
        
        # Si necesitamos crear un nuevo bucket de overflow
        elif local_overflow < self.max_overflow:
            new_bucket = Bucket(self.block_factor)
            new_bucket.add_record(record)
            new_index = self.getLastIndex() + 1
            
            # Actualizar el último bucket de la cadena
            bucket.next_bucket = new_index
            self.insertBucket(current_index, bucket)
            
            # Escribir el nuevo bucket
            with open(self.filename, "ab") as file:
                file.write(new_bucket.pack())
            
            print(f"Nuevo bucket overflow creado en posición {new_index}")
            return True
        
        # Si hemos alcanzado el maximo de overflow, hacer rehashing
        else:
            self.rehash()
            return self.insertRecord(record)   # Reintentar la insercion despues del rehashing

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
        
        try:
            # 4. Reinsertar todos los registros
            for record in all_records:
                temp_hashing.insertRecord(record)
            
            # 5. Reemplazar archivos
            os.remove(self.filename)
            os.rename(temp_filename, self.filename)
            
            # 6. Actualizar instancia
            self.__init__(self.filename, new_max_buckets, self.block_factor, new_max_overflow)
            print(f"Rehashing completado. Nuevo tamaño: {new_max_buckets} buckets")
        except Exception as e:
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
            raise RuntimeError(f"Error durante rehashing: {str(e)}")
        
    def searchRecord(self, id):
        # Busca un registro por su ID.
        # Retorna el Record si lo encuentra, None si no existe.

        current_index = id % self.max_buckets
        
        # Traer el bucket principal a ram
        bucket = self.readBucket(current_index)
        
        # Buscar en el bucket principal
        for record in bucket.records[:bucket.size]:
            if record.id == id:
                return record
        
        # Si no esta en el principal, buscar en la cadena de overflow
        while bucket.next_bucket != -1:
            current_index = bucket.next_bucket
            bucket = self.readBucket(current_index)
            
            for record in bucket.records[:bucket.size]:
                if record.id == id:
                    return record
        
        # No encontrado
        return None
    




def printStructure(hashing: StaticHashing):
    """
    Muestra la estructura del StaticHashing en formato de tabla
    Args:
        hashing: Objeto StaticHashing a visualizar
    """
    print("\n=== Estructura del Archivo ===")
    print(f"Buckets principales: {hashing.max_buckets}")
    print(f"Factor de bloque: {hashing.block_factor}")
    print(f"Máximo overflow: {hashing.max_overflow}")
    
    total_buckets = hashing.getLastIndex() + 1
    print(f"\nTotal buckets (incluyendo overflow): {total_buckets}\n")
    
    # Encabezado de la tabla
    print(f"{'#Bucket':<10}{'IDs':<20}{'Overflow Buckets (IDs)':<30}")
    print("-" * 60)
    
    # Recorrer todos los buckets principales
    for i in range(hashing.max_buckets):
        primary_bucket = hashing.readBucket(i)
        overflow_buckets = []
        overflow_ids = []
        
        # Obtener la cadena de overflow si existe
        current_overflow = primary_bucket.next_bucket
        while current_overflow != -1:
            overflow_bucket = hashing.readBucket(current_overflow)
            overflow_buckets.append(str(current_overflow))
            overflow_ids.extend([str(r.id) for r in overflow_bucket.records[:overflow_bucket.size]])
            current_overflow = overflow_bucket.next_bucket
        
        # Construir las cadenas para mostrar
        primary_ids = ", ".join([str(r.id) for r in primary_bucket.records[:primary_bucket.size]])
        overflow_info = ""
        
        if overflow_buckets:
            overflow_info = f"→ Buckets: {', '.join(overflow_buckets)} (IDs: {', '.join(overflow_ids)})"
        
        # Imprimir la fila
        print(f"{i:<10}{primary_ids:<20}{overflow_info:<30}")
    

staticHashing = StaticHashing("data.dat", 16, 4, 2)

for i in range(50):
    staticHashing.insertRecord(Record(i))

printStructure(staticHashing)