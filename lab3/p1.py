import struct

# Integrantes: Mikel Bracamonte, Gino Daza

class StaticHashing:

    # i i i i i
    BUCKET_SIZE = 4
    MAIN_BUCKETS = 5
    

    def __init__(self, filename: str, BUCKET_SIZE: str, MAIN_BUCKETS: int):
        self.filename = filename


    def insert(self, key):
        packed_key = struct.pack("i", key)
        key_pos = key % self.TABLE_SIZE

        with open(self.filename, "r+b") as file:
            file.seek(key_pos, 0)
            packed_next_key = file.read(4)
            next_key = struct.unpack("i", packed_next_key)[0]
            for i in range(self.BUCKET_SIZE):
                file.seek(i * 4, 1)
                if(next_key == -1):
                    file.write(packed_key)
            










keys = [3, 6, 20, 19, 13, 45, 36, 27, 2, 50, 89, 23, 44, 71, 38, 49, 53, 25, 22, 31, 60, 85, 43]


hash = StaticHashing("test.dat", 5)