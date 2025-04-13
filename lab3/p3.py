# Integrantes: Mikel Bracamonte, Gino Daza
import struct
from typing import TextIO, Tuple, Union
import os
import pickle

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

        for i in range(self.fb):
            self.records.append(Alumno())

    def pack(self) -> bytes:
        data = self.records[0].pack()
        for record in self.records[1:]:
            data += record.pack()
        return data + struct.pack(self.HEADER_FORMAT, self.size, self.next)
    
    @staticmethod
    def unpack(packed_data: bytes, fb: int) -> "Bucket":
        bucket = Bucket(fb)

        size, next = struct.unpack(Bucket.HEADER_FORMAT, packed_data[-8:])
        for i in range(size):
            bucket.add_record(Alumno.unpack(packed_data[i * Alumno.SIZE: (i + 1) * Alumno.SIZE]))
        bucket.next = next

        return bucket
    
    def is_full(self) -> bool:
        return self.size == self.fb
    
    def add_record(self, record: Alumno):
        if not self.is_full():
            self.records.append(record)
            self.size += 1

class Node:
    def __init__(self, left = -1, right = -1):
        self.left = left
        self.right = right
        self.left_is_leaf = True
        self.right_is_leaf = True

    def next(self, val: int) -> Tuple[Union[int, "Node"], bool]:
        if(val == 0):
            return self.left, self.left_is_leaf
        else:
            return self.right, self.right_is_leaf        

    def set_left_value(self, val: int):
        self.left = val
        self.left_is_leaf = True

    def set_right_value(self, val: int):
        self.right = val
        self.right_is_leaf = True

    def set_left_node(self, node: "Node"):
        self.left = node
        self.left_is_leaf = False

    def set_right_node(self, node: "Node"):
        self.right = node
        self.right_is_leaf = False

class ExtendibleHash:
    HEADER_FORMAT = "iiii"
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

    def __init__(self, filename: str, D: int, fb: int):
        self.filename = filename
        self.hash_file = filename + "hash_tree.dat"

        if os.path.exists(self.filename): # Leer toda la información
            with open(self.filename, "rb") as file:
                self.D, self.BUCKETS, self.OVERFLOW_BUCKETS, self.fb = struct.unpack(self.HEADER_FORMAT, file.read(self.HEADER_SIZE))
            with open(self.hash_file, "rb") as hfile:
                self.hash_tree = pickle.load(hfile)
            
            self.BUCKET_SIZE = self.fb * Alumno.SIZE + Bucket.HEADER_SIZE
            self.MAX_BUCKETS = 2**self.D
        else: # Inicializar todo
            self.D = D # TODO se elimino CURRENT_DEPTH

            self.hash_tree = Node(0, 1)

            self.BUCKETS = 2
            self.OVERFLOW_BUCKETS = 0
            self.fb = fb
            self.write_hash_index()

            self.BUCKET_SIZE = self.fb * Alumno.SIZE + Bucket.HEADER_SIZE
            self.MAX_BUCKETS = 2**self.D

            with open(filename, "xb") as file:
                self.write_headers(file)
                self.write_bucket(file, 0, Bucket(self.fb))
                self.write_bucket(file, 1, Bucket(self.fb))

    def write_headers(self, file: TextIO):
        file.seek(0)
        file.write(struct.pack(self.HEADER_FORMAT, self.D, self.BUCKETS, self.OVERFLOW_BUCKETS, self.fb))        

    def write_hash_index(self):
        with open(self.hash_file, "wb") as hfile:
            pickle.dump(self.hash_tree, hfile)
    
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

            local_depth = 0

            node = self.hash_tree

            while True:
                local_depth += 1
                next, is_leaf = node.next(int(binary[local_depth - 1], 2))
                if is_leaf:
                    bucket_pos = next
                    break
                else:
                    node = next

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

                        bin1 = binary[:local_depth] + "0"
                        bin2 = binary[:local_depth] + "1"

                        for i in range(size): # Añadir todos los registros a los buckets respectivos
                            current_record = records[i]
                            current_bin = self.binary(self.hash(current_record.id))[:local_depth + 1]
                            if current_bin == bin1: # El registro debe ir al bucket original
                                bucket.add_record(current_record)
                            else: # El registro debe ir al nuevo bucket
                                new_bucket.add_record(current_record)
                        
                        local_depth += 1

                        # Actualizar el hash index
                        new_node = Node(bucket_pos, new_bucket_pos)
                        if binary[local_depth - 1] == "0":
                            node.set_left_node(new_node)
                        else:
                            node.set_right_node(new_node)

                        self.write_hash_index()

                        self.BUCKETS += 1

                        # Escribir el nuevo registro

                        # Encontrar el bucket al que debe ir
                        if binary[:local_depth] == bin1:
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
                                node = new_node

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

    def search(self, key: int) -> Alumno:
        with open(self.filename, "rb") as file:
            binary = self.binary(self.hash(key))

            local_depth = 0

            node = self.hash_tree

            while True:
                local_depth += 1
                next, is_leaf = node.next(int(binary[local_depth - 1], 2))
                if is_leaf:
                    bucket_pos = next
                    break
                else:
                    node = next

            while True:
                bucket = self.read_bucket(file, bucket_pos)
                for i in range(0, bucket.size):
                    if bucket.records[i].id == key: # Record encontrado
                        return bucket.records[i]
                if bucket.next == -1: # No hay overflow bucket -> el record no existe
                    return None
                else: # Revisamos en el overflow bucket
                    bucket_pos = bucket.next

extendible_hash = ExtendibleHash("data.dat", 3, 3)

record1 = Alumno(154, "Gino", "Daza")
record2 = Alumno(358, "Mikel", "Bracamonte")
record3 = Alumno(203, "Eduardo", "Aragon")
record4 = Alumno(260, "Jorge", "Quenta")
record5 = Alumno(528, "Renato", "DaGarcia")

extendible_hash.insert(record1)
extendible_hash.insert(record2)
extendible_hash.insert(record3)
extendible_hash.insert(record4)
extendible_hash.insert(record5)

print(extendible_hash.search(528))