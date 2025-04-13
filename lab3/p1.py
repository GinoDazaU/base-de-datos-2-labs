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
        id = struct.unpack(Record.FORMAT, data_buffer)
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

    def __init__(self, filename, block_factor, total_buckets, max_overflow_buffer):
        self.filename = filename
        
        # Si el archivo existe se leera la metadata
        if os.path.exists(filename):
            with open(filename, 'rb') as file:
                total_buckets_buffer = file.read(4)
                block_factor_buffer = file.read(4)
                max_overflow_buffer = file.read(4)
                self.total_buckets = struct.unpack("i", total_buckets_buffer)
                self.block_factor = struct.unpack("i", block_factor_buffer)
                max_overflow_buffer = struct.unpack("i", max_overflow_buffer)
        else:
            self.block_factor = block_factor
            self.total_buckets = total_buckets
            self.max_overflow_buffer = max_overflow_buffer
            self.buildFile()
    
    def buildFile(self):
        if os.path.exists(self.filename):
            raise Exception("El archivo ya existe.")
        with open(self.filename, "wb") as file:
            for _ in range(self.total_buckets):
                bucket = Bucket()
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
            return Bucket.unpack(bucket_buffer)

    def insertRecord(self, record: Record):
        index = record.id % self.total_buckets
        bucket = self.readBucket(index)
        if not bucket.isFull():
            bucket.add_record(record)
            self.insertBucket(bucket)
            print(f"Registro insertado correctamente en la posicion {index}")
            return True
        
            




