import struct

class Venta:

    def __init__(self, id, nombre, cantidad_vendida, precio_unitario, fecha):
        self.id = id
        self.nombre = nombre
        self.cantidad_vendida = cantidad_vendida
        self.precio_unitario = precio_unitario
        self.fecha = fecha

        self.left = -1
        self.right = -1


class RecordBST:

    FORMAT = "i30sif10sii"
    RECORD_SIZE = struct.calcsize(FORMAT)

    def __init__(self, filename):
        self.filename = filename

    def insert(self, record: Venta):
        with open(self.filename, "r+b") as file:

            packed_data = struct.pack(
                self.FORMAT, 
                record.id, 
                record.nombre, 
                record.cantidad_vendida, 
                record.precio_unitario, 
                record.fecha, 
                record.left, 
                record.right
            )
            
            file.write(packed_data)

            pos = file.tell() / self.RECORD_SIZE
            if pos == 1:
                return
            
            record_data = file.read(self.RECORD_SIZE)
            unpacked_record_data = struct.unpack(self.FORMAT, record_data)
            
            id, nombre, cantidad_vendida, precio_unitario, fecha, left, right = unpacked_record_data

            while True:
                print("hola")
                return


    def search(self, key):
        pass

    def remove(self, key):
        pass

    def rangeSearch(self, init_key, end_key):
        pass




filename = "Ventas.dat"

bst = RecordBST(filename)

