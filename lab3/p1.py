import struct

# Integrantes: Mikel Bracamonte, Gino Daza

class StaticHashing:

    # i i i i i
    BUCKET_SIZE = 4
    MAIN_BUCKETS = 5
    OVERFLOW_BUCKETS = 0
    RECORD_SIZE = struct.calcsize("iiiii")
    

    def __init__(self, filename: str, BUCKET_SIZE: str, MAIN_BUCKETS: int):
        self.filename = filename


    def insert(self, key):
        packed_key = struct.pack("i", key)
        key_pos = key % self.MAIN_BUCKETS

        with open(self.filename, "r+b") as file:
            # se calcula la posicion en el archivo del bucket principal
            bucket_offset = key_pos * (self.BUCKET_SIZE * 4 + 4)
            file.seek(bucket_offset, 0)

            # se lee el bucket completo incluyendo el puntero al siguiente
            packed_bucket = file.read(self.BUCKET_SIZE * 4 + 4)
            bucket = struct.unpack("i" * self.BUCKET_SIZE + "i", packed_bucket)     # trae todo el bucket a ram (es pequeño)

            # se intenta insertar en el bucket principal
            for i in range(self.BUCKET_SIZE):
                if bucket[i] == -1:
                    file.seek(bucket_offset + i * 4)
                    file.write(packed_key)
                    return

            # si no hay espacio, se verifica el puntero al siguiente bucket
            next_pointer = bucket[self.BUCKET_SIZE]

            # si no hay siguiente bucket, se crea uno nuevo
            if next_pointer == -2:
                new_bucket_pos = self.MAIN_BUCKETS + self.OVERFLOW_BUCKETS
                self.OVERFLOW_BUCKETS += 1

                # actualiza el puntero en el bucket original
                file.seek(bucket_offset + self.BUCKET_SIZE * 4)
                file.write(struct.pack("i", new_bucket_pos))

                # posicion del nuevo bucket
                overflow_offset = new_bucket_pos * (self.BUCKET_SIZE * 4 + 4)
                file.seek(overflow_offset)

                # escribe el nuevo key y llena el resto con -1
                new_bucket_data = [key] + [-1] * (self.BUCKET_SIZE - 1) + [-2]
                file.write(struct.pack("i" * self.BUCKET_SIZE + "i", *new_bucket_data))
                return

            # si ya hay un bucket de overflow, se repite el proceso
            while next_pointer != -2:
                overflow_offset = next_pointer * (self.BUCKET_SIZE * 4 + 4)
                file.seek(overflow_offset)
                packed_bucket = file.read(self.BUCKET_SIZE * 4 + 4)
                bucket = struct.unpack("i" * self.BUCKET_SIZE + "i", packed_bucket)

                for i in range(self.BUCKET_SIZE):
                    if bucket[i] == -1:
                        file.seek(overflow_offset + i * 4)
                        file.write(packed_key)
                        return

                next_pointer = bucket[self.BUCKET_SIZE]         # Se busca el siguiente bucket libre


    def search(self, key: int) -> int:
        key_pos = key % self.MAIN_BUCKETS
        
        with open(self.filename, "r+b") as file:
            while True:
                file.seek(key_pos * self.RECORD_SIZE)

                # Leer todo el bucket
                data = struct.unpack("iiiii", file.read(self.RECORD_SIZE))

                for i in range(self.BUCKET_SIZE):
                    # un -1 significa que no hay ningun registro de ahi en adelante
                    if data[i] == -1:
                        return -1
                    elif data[i] == key:
                        return key
                
                # Si no se encontro nada, y hay un siguiente bucket
                key_pos = data[self.BUCKET_SIZE]

                if key_pos == -1:
                    return -1
                
    def delete(self, key: int):
        pass





keys = [3, 6, 20, 19, 13, 45, 36, 27, 2, 50, 89, 23, 44, 71, 38, 49, 53, 25, 22, 31, 60, 85, 43]


hash = StaticHashing("test.dat", 5)