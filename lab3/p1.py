import struct

# Integrantes: Mikel Bracamonte, Gino Daza

class StaticHashing:

    # i i i i i
    BUCKET_SIZE = 4
    MAIN_BUCKETS = 5
    RECORD_SIZE = struct.calcsize("iiiii")
    

    def __init__(self, filename: str, BUCKET_SIZE: str, MAIN_BUCKETS: int):
        self.filename = filename


    def insert(self, key):
        packed_key = struct.pack("i", key)
        key_pos = key % self.TABLE_SIZE

        with open(self.filename, "r+b") as file:
            file.seek(key_pos * (self.BUCKET_SIZE * 4 + 4), 0)
            packed_bucket = file.read(self.BUCKET_SIZE * 4 + 4)
            bucket = struct.unpack("i" * self.BUCKET_SIZE + "i", packed_bucket)

            for i in bucket:
                if i == -1:
                    file.write(packed_key)

    def search(self, key: int) -> bool:
        key_pos = key % self.MAIN_BUCKETS
        
        with open(self.filename, "r+b") as file:
            while True:
                file.seek(key_pos * self.RECORD_SIZE)
                data = struct.unpack("iiiii", file.read(self.RECORD_SIZE))

                for i in range(self.BUCKET_SIZE):
                    if data[i] == -1:
                        return -1
                    elif data[i] == key:
                        return key
                
                key_pos = data[self.BUCKET_SIZE]

                if key_pos == -1:
                    return -1





keys = [3, 6, 20, 19, 13, 45, 36, 27, 2, 50, 89, 23, 44, 71, 38, 49, 53, 25, 22, 31, 60, 85, 43]


hash = StaticHashing("test.dat", 5)