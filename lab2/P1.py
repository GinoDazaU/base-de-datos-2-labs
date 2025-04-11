import struct
import math

class Venta:
    def __init__(self, id, nombre, cantidad_vendida, precio_unitario, fecha):
        self.id = id
        self.nombre = nombre
        self.cantidad_vendida = cantidad_vendida
        self.precio_unitario = precio_unitario
        self.fecha = fecha
        
class SecuentialRegister:
    FORMAT = "i30sif10s"
    RECORD_SIZE = struct.calcsize(FORMAT)

    def __init__(self, filename):
        self.filename = filename

    def insert(self, record: Venta):
        packed_data = struct.pack(
            self.FORMAT,
            record.id,
            record.nombre,
            record.precio_unitario,
            record.cantidad_vendida,
            record.fecha,
            record.next)
        
        with open(self.filename, "r+b") as file:
            file.seek(0,2)
            pos = file.tell()
            if pos == 0: 
                file.write(struct.pack("i", 1))   # cantidad de registros
                file.write(struct.pack("?", 1))   # el primer byte determina si esta activo o no
                file.write(packed_data)
                print("Registro insertado correctamente.")
                return
            
            file.seek(0, 0)
            packed_rows = file.read(4)          # saca el primer entero que indica la cantidad de registros
            
            data_rows = struct.unpack("i", packed_rows)[0]
            aux_rows = math.floor(math.log2(data_rows))

            file.seek(1 + data_rows * (self.RECORD_SIZE + 1), 0)     # posiciona el cursor al comienzo de la zona auxiliar


            while(True):
                packed_isActive = file.read(1)
                isActive = struct.unpack("i", packed_isActive)[0]

                file.seek(self.RECORD_SIZE, 1)

                









            

    

    def search(self, key):
        pass

    def remove(self, key):
        pass

    def rangeSearch(init_key, end_key):
        pass
