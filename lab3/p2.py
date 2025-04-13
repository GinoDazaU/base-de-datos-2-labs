# Integrantes: Mikel Bracamonte, Gino Daza
import struct
from typing import TextIO
import os

class Alumno:
    FORMAT = "i20s20s"
    SIZE = struct.calcsize(FORMAT)

    def __init__(self, id: int = -1, nombre: str = "", apellido: str = ""):
        self.id = id
        self.nombre = nombre[:20].ljust(20)
        self.apellido = apellido[:20].ljust(20)

    def pack(self) -> bytes:
        return struct.pack(self.FORMAT, self.id, self.nombre.encode(), self.apellido.encode())
    
    @staticmethod
    def unpack(packed_data: bytes) -> "Alumno":
        id, nombre, apellido = struct.unpack(Alumno.FORMAT, packed_data)
        return Alumno(id, nombre.decode().strip(), apellido.decode().strip())

class Bucket:
    HEADER_FORMAT = "ii"
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

    def __init__(self, fb: int):
        self.size = 0
        self.next = -1
        self.records: list[Alumno] = []
        self.fb = fb

        for i in self.fb:
            self.records.append(Alumno())

    def pack(self) -> bytes:
        data: bytes
        for record in self.records:
            data += record.pack()
        return data + struct.pack(self.HEADER_FORMAT, self.size, self.next)
    
    @staticmethod
    def unpack(packed_data: bytes, fb: int) -> "Bucket":
        bucket = Bucket(fb)
        size, next = struct.unpack(Bucket.HEADER_FORMAT, packed_data[-8:])
        for i in range(size):
            bucket.records[i] = Alumno.unpack(packed_data[i * Alumno.SIZE: (i + 1) * Alumno.SIZE])
        bucket.next = next

        return bucket
    
    def is_full(self) -> bool:
        return self.size == self.fb
    
    def add_record(self, record: Alumno):
        if not self.is_full():
            self.records.append(record)
            self.size += 1

class ExtendibleHash:
    HEADER_FORMAT = "iiiii"
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

    def __init__(self, filename: str, D: int, fb: int):
        self.filename = filename

        if os.path.exists(filename): # Leer toda la información
            with open(filename, "rb") as file:
                self.D, self.CURRENT_DEPTH, self.BUCKETS, self.OVERFLOW_BUCKETS, self.fb = struct.unpack(self.HEADER_FORMAT, file.read(self.HEADER_SIZE))
                # TODO leer el hash_index
        else: # Inicializar todo
            self.D = D
            self.CURRENT_DEPTH = 1

            self.hash_index = [] # key -> [bucket, localdepth]
            self.hash_index[0] = [0, 1]
            self.hash_index[1] = [1, 1]
            self.BUCKETS = 2
            self.OVERFLOW_BUCKETS = 0
            self.fb = fb

            with open(filename, "xb") as file:
                self.write_headers(file)
        
        self.BUCKET_SIZE = self.fb * Alumno.SIZE + Bucket.HEADER_SIZE
        self.MAX_BUCKETS = 2**self.D

    def write_headers(self, file: TextIO):
        file.seek(0)
        file.write(struct.pack(self.HEADER_FORMAT, self.D, self.CURRENT_DEPTH, self.BUCKETS, self.OVERFLOW_BUCKETS, self.fb))
        # TODO escribir el hash_index

    def hash(self, num: int) -> int:
        return num % self.MAX_BUCKETS
    
    def binary(self, num: int) -> str:
        return bin(num)[2:]
    
    def read_bucket(self, file: TextIO, bucket_pos: int) -> Bucket:
        file.seek(self.BUCKET_SIZE * bucket_pos + self.HEADER_SIZE)
        return Bucket.unpack(file.read(self.BUCKET_SIZE), self.fb)
    
    def write_bucket(self, file: TextIO, bucket_pos: int, bucket: Bucket):
        file.seek(self.BUCKET_SIZE * bucket_pos + self.HEADER_SIZE)
        file.write(Bucket.pack(bucket))
    
    def insert(self, record: Alumno):
        with open(self.filename, "r+b") as file:
            binary = self.binary(self.hash(record.id))
            binary = binary[-self.CURRENT_DEPTH:]
            while int(binary, 2) not in self.hash_index:
                binary = binary[1:]
                
            bucket_pos, local_depth = self.hash_index[int(binary, 2)]
            bucket = self.read_bucket(file, bucket_pos)

            for i in range(0, bucket.size):
                if bucket.records[i].id == record.id: # La key ya existe
                    return
            
            if bucket.is_full(): # Hay que crear un bucket
                if local_depth == self.D: # Overflow
                    if bucket.next == -1: # Crear nuevo overflow bucket
                        new_bucket_pos = self.BUCKETS + self.OVERFLOW_BUCKETS
                        new_bucket = Bucket(self.fb)
                        new_bucket.add_record(record)
                        bucket.next = new_bucket_pos

                        self.write_bucket(file, bucket_pos, bucket)
                        self.write_bucket(file, new_bucket_pos, new_bucket)

                        self.OVERFLOW_BUCKETS += 1
                        self.write_headers()
                        return

                    while True: # Leer el overflow bucket
                        bucket_pos = bucket.next
                        bucket = self.read_bucket(file, bucket.next)

                        for i in range(0, bucket.size):
                            if bucket.records[i].id == record.id: # La key ya existe
                                return
                        
                        if bucket.next == -1: # No hay overflow bucket
                            if bucket.is_full(): # Crear nuevo overflow bucket
                                new_bucket_pos = self.BUCKETS + self.OVERFLOW_BUCKETS
                                new_bucket = Bucket(self.fb)
                                new_bucket.add_record(record)
                                bucket.next = new_bucket_pos

                                self.write_bucket(file, bucket_pos, bucket)
                                self.write_bucket(file, new_bucket_pos, new_bucket)

                                self.OVERFLOW_BUCKETS += 1
                                self.write_headers()
                            else: # Se inserta al final
                                bucket.add_record(record)
                                self.write_bucket(file, bucket_pos, bucket)
                            return
                else: # Split
                    while True:
                        # Copiar los valores para insertarlos despues
                        records = bucket.records
                        size = bucket.size

                        # Crear nuevo bucket
                        new_bucket = Bucket(self.fb)
                        new_bucket_pos = self.BUCKETS + self.OVERFLOW_BUCKETS

                        # Vaciar bucket original
                        bucket.size = 0

                        bin1 = "0" + binary[-local_depth:]
                        bin2 = "1" + binary[-local_depth:]

                        for i in range(size): # Añadir todos los registros a los buckets respectivos
                            current_record = records[i]
                            current_bin = self.binary(self.hash(current_record.id))[-(local_depth + 1):]
                            if current_bin == bin1: # El registro debe ir al bucket original
                                bucket.add_record(current_record)
                            else: # El registro debe ir al nuevo bucket
                                new_bucket.add_record(current_record)
                        
                        local_depth += 1

                        # Actualizar el hash index
                        self.hash_index[int(bin1, 2)] = [bucket_pos, local_depth]
                        self.hash_index[int(bin2, 2)] = [new_bucket_pos, local_depth]

                        self.BUCKETS += 1
                        self.CURRENT_DEPTH = max(self.CURRENT_DEPTH, local_depth)

                        # Escribir el nuevo registro

                        # Encontrar el bucket al que debe ir
                        if binary[-local_depth:] == bin1:
                            bucket = bucket
                        else:
                            bucket = new_bucket
                        
                        if bucket.is_full(): # Hay que crear un nuevo bucket
                            if local_depth == self.D: # Overflow
                                overflow_bucket_pos = self.BUCKETS + self.OVERFLOW_BUCKETS
                                overflow_bucket = Bucket(self.fb)
                                overflow_bucket.add_record(record)
                                bucket.next = overflow_bucket_pos

                                self.OVERFLOW_BUCKETS += 1

                                self.write_bucket(file, bucket_pos, bucket)
                                self.write_bucket(file, new_bucket_pos, new_bucket)
                                self.write_bucket(file, overflow_bucket_pos, overflow_bucket)
                                self.write_headers()

                                return
                            else: # Split nuevamente (el bucle while se repite)
                                self.write_bucket(file, bucket_pos, bucket)
                                self.write_bucket(file, new_bucket_pos, new_bucket)
                                self.write_headers()
                        else: # Se añade al bucket
                            bucket.add_record(record)
                            self.write_bucket(file, bucket_pos, bucket)
                            self.write_bucket(file, new_bucket_pos, new_bucket)
                            self.write_headers()

                            return
                        
            else: # Se inserta al final
                bucket.add_record(record)
                self.write_bucket(file, bucket_pos, bucket)
                return

    def search(self, key: int) -> int:
        with open(self.filename, "rb") as file:
            binary = self.binary(self.hash(key))
            binary = binary[-self.CURRENT_DEPTH:]
            while int(binary, 2) not in self.hash_index:
                binary = binary[1:]
                
            bucket_pos, local_depth = self.hash_index[int(binary, 2)]

            while True:
                bucket = self.read_bucket(file, bucket_pos)
                for i in range(0, bucket.size):
                    if bucket.records[i].id == key: # Record encontrado
                        return bucket.records[i]
                if bucket.next == -1: # No hay overflow bucket -> el record no existe
                    return None
                else: # Revisamos en el overflow bucket
                    bucket_pos = bucket.next