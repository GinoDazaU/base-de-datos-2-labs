# Integrantes: Mikel Bracamonte, Gino Daza
import struct

class Bucket:
    size = 0

    def __init__(self, fb):
        self.next = -1
        self.fb = fb

class Hash:
    D = 3
    fb = 3
    hash_index = list()

    FORMAT = "iiii"
    BUCKET_SIZE = struct.calcsize(FORMAT)

    def __init__(self, filename: str):
        self.filename = filename
        self.hash_index[0] = 0
        self.hash_index[1] = 1

    def hash(self, num: int) -> int:
        return num % 2**self.D
    
    def Binary(self, num: int) -> str:
        return bin(num)
    
    def insert(self, key: int):
        binary = self.Binary(self.hash(key))
        bucket = self.hash_index[binary]

        with open(self.filename, "r+b") as file:
            file.seek(self.BUCKET_SIZE * bucket)
            data = struct.unpack(self.FORMAT, file.read)






    def search(self, key: int):
        pass
    
