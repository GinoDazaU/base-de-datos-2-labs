import struct

class Venta:
    def __init__(self, id, nombre, cantidad_vendida, precio, fecha):
        self.id = id
        self.nombre = nombre
        self.cantidad_vendida = cantidad_vendida
        self.precio = precio
        self.fecha = fecha
        
        self.left = -1
        self.right = -1
    


class BST:
    FORMAT = "i30sif10sii"
    RECORD_SIZE = struct.calcsize(FORMAT)

    def __init__(self, filename):
        self.filename = filename
        with open(filename, "a+b") as file:
            ""

    def insert(self, record):
        with open(self.filename, "a+b") as file:
            file.write(struct.pack(self.FORMAT, record.id, record.nombre.encode(), record.cantidad_vendida, record.precio, record.fecha.encode(), record.left, record.right))
            pos = (int)(file.tell() / self.RECORD_SIZE) + 1
            if pos == 1:
                return
            
            file.seek(0)

            while True:
                id, nombre, cantidad_vendida, precio, fecha, left, right = struct.unpack(self.FORMAT, file.read(self.RECORD_SIZE))

                if record.id > id:
                    if right == -1:
                        file.seek(-4, 1)
                        file.write(struct.pack("i", pos))
                        return
                    else:
                        file.seek((right - 1) * self.RECORD_SIZE)
                elif record.id < id:
                    if left == -1:
                        file.seek(-8, 1)
                        file.write(struct.pack("i", pos))
                        return
                    else:
                        file.seek((left - 1) * self.RECORD_SIZE)
                else:
                    return
                        


    def search(self, key):
        a

    def remove(self, key):
        a

    def rangeSearch(self, init_key, end_key):
        a


bst = BST("data.dat")

venta1 = Venta(0, "item1", 10, 5, "2025-04-03")
venta2 = Venta(4, "item2", 10, 5, "2025-04-03")
venta3 = Venta(2, "item3", 10, 5, "2025-04-03")
venta4 = Venta(3, "item4", 10, 5, "2025-04-03")

bst.insert(venta1)
bst.insert(venta2)
bst.insert(venta3)
bst.insert(venta4)