# Integrantes: Mikel Bracamonte, Gino Daza
import struct
from typing import TextIO

class Bucket:
    size = 0

    def __init__(self, fb):
        self.next = -1
        self.fb = fb

class Hash:
    D = 3
    MAX_BUCKETS = 2**D
    BUCKETS = 0
    OVERFLOW_BUCKETS = 0
    fb = 3
    hash_index = dict()

    FORMAT = "i" * (fb + 2)
    BUCKET_SIZE = struct.calcsize(FORMAT)

    HEADER_FORMAT = "i"
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

    def __init__(self, filename: str): # TODO si el archivo ya existe, leer el header, si no existe, inicializar todo
        self.filename = filename
        self.hash_index["0"] = 0
        self.hash_index["1"] = 1
        self.BUCKETS = 2

    def hash(self, num: int) -> int:
        return num % self.MAX_BUCKETS
    
    def Binary(self, num: int) -> str:
        return bin(num)
    
    def create_bucket(self, file: TextIO):
        file.seek(0, 2)
        empty = struct.pack("i", -1)
        data = struct.pack("ii", 0, -1)

        for i in range(self.fb):
            file.write(empty)
        file.write(data)
    
    def insert(self, key: int):
        binary = self.Binary(self.hash(key))
        while binary not in self.hash_index:
            binary = binary[1:]
            
        bucket = self.hash_index[binary]

        with open(self.filename, "r+b") as file:
            file.seek(self.BUCKET_SIZE * bucket + self.HEADER_SIZE)
            data = struct.unpack(self.FORMAT, file.read(self.BUCKET_SIZE))
            num_reg = data[self.fb]

            for i in range(0, num_reg):
                if data[i] == key: # La key ya existe
                    return
            
            if num_reg == self.fb: # Hay que splitear
                if len(binary) == self.D: # Overflow
                    next_bucket = data[self.fb + 1]

                    if next_bucket == -1: # Crear nuevo overflow bucket
                        new_bucket = self.BUCKETS + self.OVERFLOW_BUCKETS
                        self.create_bucket(file)
                        file.seek(self.BUCKET_SIZE * (bucket + 1) - 4 + self.HEADER_SIZE) # Escribir puntero al nuevo bucket
                        file.write(struct.pack("i", new_bucket))

                        file.seek(self.BUCKET_SIZE * new_bucket + self.HEADER_SIZE) # Escribir la key en el nuevo bucket
                        file.write(struct.pack("i", key))

                        file.seek(self.BUCKET_SIZE * (new_bucket + 1) - 8 + self.HEADER_SIZE) # Escribir tamaño del nuevo bucket en 1
                        file.write(struct.pack("i", 1))
                        return
                    
                    file.seek(self.BUCKET_SIZE * next_bucket + self.HEADER_SIZE)
                    data = struct.unpack(self.FORMAT, file.read(self.BUCKET_SIZE))
                    num_reg = data[self.fb]
                    bucket = next_bucket
                    next_bucket = data[self.fb + 1]

                    while True:
                        for i in range(0, num_reg):
                            if data[i] == key: # La key ya existe
                                return
                        
                        if next_bucket == -1:
                            if num_reg == self.fb: # Crear nuevo overflow bucket
                                new_bucket = self.BUCKETS + self.OVERFLOW_BUCKETS
                                self.create_bucket(file)
                                file.seek(self.BUCKET_SIZE * (bucket + 1) - 4 + self.HEADER_SIZE) # Escribir puntero al nuevo bucket
                                file.write(struct.pack("i", new_bucket))

                                file.seek(self.BUCKET_SIZE * new_bucket + self.HEADER_SIZE) # Escribir la key en el nuevo bucket
                                file.write(struct.pack("i", key))

                                file.seek(self.BUCKET_SIZE * (new_bucket + 1) - 8 + self.HEADER_SIZE) # Escribir tamaño del nuevo bucket en 1
                                file.write(struct.pack("i", 1))
                                return
                            else: # Se inserta al final
                                file.seek(self.BUCKET_SIZE * bucket + (num_reg * 4) + self.HEADER_SIZE)
                                file.write(struct.pack("i", key))

                                num_reg += 1
                                file.seek(self.BUCKET_SIZE * (bucket + 1) - 8 + self.HEADER_SIZE)
                                file.write(struct.pack("i", num_reg))
                            return
                        else:
                            file.seek(self.BUCKET_SIZE * next_bucket + self.HEADER_SIZE)
                            data = struct.unpack(self.FORMAT, file.read(self.BUCKET_SIZE))
                            num_reg = data[self.fb]
                            bucket = next_bucket
                            next_bucket = data[self.fb + 1]
                        
                else:
                    # TODO Split
                    pass
            else: # Se inserta al final
                file.seek(self.BUCKET_SIZE * bucket + (num_reg * 4) + self.HEADER_SIZE)
                file.write(struct.pack("i", key))

                num_reg += 1
                file.seek(self.BUCKET_SIZE * (bucket + 1) - 8 + self.HEADER_SIZE)
                file.write(struct.pack("i", num_reg))

    def search(self, key: int) -> int:
        pass
    
