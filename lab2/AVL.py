import struct
import os
from typing import TextIO

class Venta:
    def __init__(self, id: int, nombre: str, cantidad_vendida: int, precio: float, fecha: str):
        self.id = id
        self.nombre = nombre
        self.cantidad_vendida = cantidad_vendida
        self.precio = precio
        self.fecha = fecha
        
        self.left = -1
        self.right = -1
        self.height = 0
    
class AVL:
    FORMAT = "i30sif10siii"
    RECORD_SIZE = struct.calcsize(FORMAT)

    root = -1
    HEADER_SIZE = 4

    def __init__(self, filename: str):
        self.filename = filename
        with open(self.filename, "a") as file: # TODO si no existe el archivo, crear y escribir -1 en el header. Si existe, leer el header y guardarlo en self.root
            pass
    
    def read_register(self, file: TextIO, pos: int):
        file.seek(pos*self.RECORD_SIZE + self.HEADER_SIZE)
        return struct.unpack(self.FORMAT, file.read(self.RECORD_SIZE))
    
    def getHeight(self, file: TextIO, pos: int) -> int:
        if pos == -1:
            return -1
        
        id, nombre, cantidad_vendida, precio, fecha, left, right, height = self.read_register(file, pos)
        return height
    
    def getBalance(self, file: TextIO, pos: int) -> int:
        if pos == -1:
            return 0
        
        id, nombre, cantidad_vendida, precio, fecha, left, right, height = self.read_register(file, pos)
        return self.getHeight(left) - self.getHeight(right)
    
    def leftRotate(self, file: TextIO, pos: int) -> int:
        id, nombre, cantidad_vendida, precio, fecha, left, right, height = self.read_register(file, pos)
        rightId, rightNombre, rightCantidad_vendida, rightPrecio, rightFecha, rightLeft, rightRight, rightHeight = self.read_register(file, right)
        
        newPos = right
        right = rightLeft # TODO escribir right
        rightLeft = pos # TODO escribir rightLeft

        height = max(self.getHeight(file, left), self.getHeight(file, left)) + 1 # TODO escribir height
        rightHeight = max(self.getHeight(file, rightLeft), self.getHeight(file, rightRight)) + 1 # TODO escribir rightHeight

        return newPos

    def rightRotate(self, file: TextIO, pos: int) -> int:
        id, nombre, cantidad_vendida, precio, fecha, left, right, height = self.read_register(file, pos)
        leftId, leftNombre, leftCantidad_vendida, leftPrecio, leftFecha, leftLeft, leftRight, leftHeight = self.read_register(file, left)
        
        newPos = left
        left = leftRight # TODO escribir left
        leftRight = pos # TODO escribir leftRight

        height = max(self.getHeight(file, left), self.getHeight(file, left)) + 1 # TODO escribir height
        leftHeight = max(self.getHeight(file, leftLeft), self.getHeight(file, leftRight)) + 1 # TODO escribir leftHeight

        return newPos

    def insert_aux(self, file: TextIO, record: Venta, current: int, newPos: int) -> int:
        if current == -1:
            return newPos

        id, nombre, cantidad_vendida, precio, fecha, left, right, height = self.read_register(file, current)

        if record.id < id:
            left = self.insert_aux(file, record, left, newPos) # TODO escribir left
        else:
            right = self.insert_aux(file, record, right, newPos) # TODO escribir right

        leftHeight = self.getHeight(file, left)
        rightHeight = self.getHeight(file, right)
        height = max(leftHeight, rightHeight) + 1 # TODO escribir height

        balance = self.getBalance(current)
        leftBalance = self.getBalance(left)
        rightBalance = self.getBalance(right)
        
        # Rotaciones

        # Left-left
        if balance > 1 and leftBalance >= 0:
            return self.rightRotate(file, current)

        # Left-right
        if balance > 1 and leftBalance < 0:
            left = self.leftRotate(file, current) # TODO escribir left
            return self.rightRotate(file, current)

        # Right-right
        if balance < -1 and rightBalance <= 0:
            return self.leftRotate(file, current)

        # Right-left
        if balance < -1 and rightBalance > 0:
            right = self.rightRotate(file, current) # TODO escribir right
            return self.leftRotate(file, current)
        
        # Ninguna rotacion
        return current

    def insert(self, record: Venta):
        with open(self.filename, "r+b") as file:
            file.seek(0, 2)
            pos = (int)((file.tell() - self.HEADER_SIZE) / self.RECORD_SIZE)
            file.write(struct.pack(self.FORMAT, record.id, record.nombre.encode(), record.cantidad_vendida, record.precio, record.fecha.encode(), record.left, record.right))
            
            self.root = self.insert_aux(file, record, self.root, pos) # TODO escribir self.root

    def search(self, key: int) -> Venta:
        with open(self.filename, "rb") as file:
            file.seek(0)
            while True:
                id, nombre, cantidad_vendida, precio, fecha, left, right, height = struct.unpack(self.FORMAT, file.read(self.RECORD_SIZE))

                if key > id:
                    if right == -1:
                        return None
                    else:
                        file.seek((right) * self.RECORD_SIZE + self.HEADER_SIZE)
                elif key < id:
                    if left == -1:
                        return None
                    else:
                        file.seek((left) * self.RECORD_SIZE + self.HEADER_SIZE)
                else:
                    return Venta(id, nombre.decode(), cantidad_vendida, precio, fecha.decode())


    def remove(self, key: int) -> int: # ta complicao
        pass

    def rangeSearch(self, init_key: int, end_key: int):
        pass




    



def main(): 
    try:
        os.remove("./data.dat")
    finally:
        avl = AVL("data.dat")

        venta1 = Venta(0, "item1", 10, 5, "2025-04-03")
        venta2 = Venta(4, "item2", 10, 5, "2025-04-03")
        venta3 = Venta(2, "item3", 10, 5, "2025-04-03")
        venta4 = Venta(3, "item4", 10, 5, "2025-04-03")

        avl.insert(venta1)
        avl.insert(venta2)
        avl.insert(venta3)
        avl.insert(venta4)

        print(avl.search(3).nombre)