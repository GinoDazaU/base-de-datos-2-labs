import struct
import os
import random
from typing import TextIO
import csv

class Venta:
    def __init__(self, id: int, nombre: str, cantidad_vendida: int, precio: float, fecha: str, left: int = -1, right: int = -1, height: int  = 0):
        self.id = id
        self.nombre = nombre
        self.cantidad_vendida = cantidad_vendida
        self.precio = precio
        self.fecha = fecha
        
        self.left = left
        self.right = right
        self.height = height
    
class AVL:
    FORMAT = "i30sif10siii"
    RECORD_SIZE = struct.calcsize(FORMAT)
    HEADER_SIZE = 4

    def __init__(self, filename: str):
        self.filename = filename
        if os.path.exists(self.filename):
            with open(self.filename, "rb") as file:
                self.root = struct.unpack("i", file.read(4))
        else:
            self.root = -1
            with open(self.filename, "xb") as file:
                file.write(struct.pack("i", self.root))
    
    def read_register(self, file: TextIO, pos: int) -> Venta:
        file.seek(pos*self.RECORD_SIZE + self.HEADER_SIZE)
        id, nombre, cantidad_vendida, precio, fecha, left, right, height = struct.unpack(self.FORMAT, file.read(self.RECORD_SIZE))
        return Venta(id, nombre.decode(), cantidad_vendida, precio, fecha.decode(), left, right, height)
    
    def write_reg(self, file: TextIO, pos: int, reg: Venta):
        file.seek(pos*self.RECORD_SIZE + self.HEADER_SIZE)
        file.write(struct.pack(self.FORMAT, reg.id, reg.nombre.encode(), reg.cantidad_vendida, reg.precio, reg.fecha.encode(), reg.left, reg.right, reg.height))
            
    def getHeight(self, file: TextIO, pos: int) -> int:
        if pos == -1:
            return -1
        
        record = self.read_register(file, pos)
        return record.height
    
    def getBalance(self, file: TextIO, pos: int) -> int:
        if pos == -1:
            return 0
        
        record = self.read_register(file, pos)
        return self.getHeight(file, record.left) - self.getHeight(file, record.right)
    
    def leftRotate(self, file: TextIO, pos: int) -> int:
        record = self.read_register(file, pos)
        rightRecord = self.read_register(file, record.right)
        
        newPos = record.right
        record.right = rightRecord.left
        rightRecord.left = pos

        self.write_reg(file, pos, record)
        self.write_reg(file, newPos, rightRecord)

        record.height = max(self.getHeight(file, record.left), self.getHeight(file, record.right)) + 1
        self.write_reg(file, pos, record)
        rightRecord.height = max(self.getHeight(file, rightRecord.left), self.getHeight(file, rightRecord.right)) + 1
        self.write_reg(file, newPos, rightRecord)

        return newPos

    def rightRotate(self, file: TextIO, pos: int) -> int:
        record = self.read_register(file, pos)
        leftRecord = self.read_register(file, record.left)
        
        newPos = record.left
        record.left = leftRecord.right
        self.write_reg(file, pos, record)
        leftRecord.right = pos
        self.write_reg(file, newPos, leftRecord)

        record.height = max(self.getHeight(file, record.left), self.getHeight(file, record.right)) + 1
        record.left = leftRecord.right
        leftRecord.height = max(self.getHeight(file, leftRecord.left), self.getHeight(file, leftRecord.right)) + 1
        self.write_reg(file, newPos, leftRecord)

        return newPos

    def minValueNode(self, file: TextIO, pos: int) -> int:
        if pos == -1:
            return -1
        
        record = self.read_register(file, pos)

        while record.left != -1:
            pos = record.left
            record = self.read_register(file, pos)
        
        return pos

    def insert_aux(self, file: TextIO, record: Venta, current: int, newPos: int) -> int:
        if current == -1:
            return newPos

        currentRecord = self.read_register(file, current)

        if record.id < currentRecord.id:
            currentRecord.left = self.insert_aux(file, record, currentRecord.left, newPos)
            self.write_reg(file, current, currentRecord)
        else:
            currentRecord.right = self.insert_aux(file, record, currentRecord.right, newPos)
        self.write_reg(file, current, currentRecord)

        leftHeight = self.getHeight(file, currentRecord.left)
        rightHeight = self.getHeight(file, currentRecord.right)
        currentRecord.height = max(leftHeight, rightHeight) + 1
        self.write_reg(file, current, currentRecord)

        balance = self.getBalance(file, current)
        leftBalance = self.getBalance(file, currentRecord.left)
        rightBalance = self.getBalance(file, currentRecord.right)
        
        # Rotaciones

        # Left-left
        if balance > 1 and leftBalance >= 0:
            return self.rightRotate(file, current)

        # Left-right
        if balance > 1 and leftBalance < 0:
            currentRecord.left = self.leftRotate(file, currentRecord.left)
            self.write_reg(file, current, currentRecord)
            return self.rightRotate(file, current)

        # Right-right
        if balance < -1 and rightBalance <= 0:
            return self.leftRotate(file, current)

        # Right-left
        if balance < -1 and rightBalance > 0:
            currentRecord.right = self.rightRotate(file, currentRecord.right)
            self.write_reg(file, current, currentRecord)
            return self.leftRotate(file, current)
        
        # Ninguna rotacion
        return current

    def remove_aux(self, file: TextIO, key: int, current: int) -> int:
        if current == -1:
            return current
        
        currentRecord = self.read_register(file, current)
        
        if key < currentRecord.id:
            currentRecord.left = self.remove_aux(file, key, currentRecord.left)
            self.write_reg(file, current, currentRecord)
        elif key > currentRecord.id:
            currentRecord.right = self.remove_aux(file, key, currentRecord.right)
            self.write_reg(file, current, currentRecord)
        else:
            if currentRecord.left == -1 or currentRecord.right == -1:
                temp = -1
                if currentRecord.left != -1:
                    temp = currentRecord.left
                else:
                    temp = currentRecord.right

                if temp == -1:
                    temp = current
                    current = -1
                else:
                    self.write_reg(file, current, self.read_register(file, temp))
                # delete temp
            else:
                temp = self.minValueNode(file, currentRecord.right)
                tempRecord = self.read_register(file, temp)

                currentRecord.id = tempRecord.id
                currentRecord.nombre = tempRecord.nombre
                currentRecord.cantidad_vendida = tempRecord.cantidad_vendida
                currentRecord.precio = tempRecord.precio
                currentRecord.fecha = tempRecord.fecha

                currentRecord.right = self.remove_aux(file, tempRecord.id, currentRecord.right)
                self.write_reg(file, current, currentRecord)
            
        if current == -1:
            return current
            
        leftHeight = self.getHeight(file, currentRecord.left)
        rightHeight = self.getHeight(file, currentRecord.right)
        currentRecord.height = max(leftHeight, rightHeight) + 1

        balance = self.getBalance(file, current)
        leftBalance = self.getBalance(file, currentRecord.left)
        rightBalance = self.getBalance(file, currentRecord.right)

        # Rotaciones
        # Left-left
        if balance > 1 and leftBalance >= 0:
            return self.rightRotate(file, current)

        # Left-right
        if balance > 1 and leftBalance < 0:
            currentRecord.left = self.leftRotate(file, currentRecord.left)
            self.write_reg(file, current, currentRecord)
            return self.rightRotate(file, current)

        # Right-right
        if balance < -1 and rightBalance <= 0:
            return self.leftRotate(file, current)

        # Right-left
        if balance < -1 and rightBalance > 0:
            currentRecord.right = self.rightRotate(file, currentRecord.right)
            self.write_reg(file, current, currentRecord)
            return self.leftRotate(file, current)
        
        return current

    def range_search_aux(self, file: TextIO, init_key: int, end_key: int, current: int, result: list[Venta]):
        if current == -1:
            return
        
        currentRecord = self.read_register(file, current)

        if currentRecord.id >= init_key and currentRecord.id <= end_key:
            result.append(currentRecord)

        if currentRecord.id > init_key:
            self.range_search_aux(file, init_key, end_key, currentRecord.left, result)

        if currentRecord.id < end_key:
            self.range_search_aux(file, init_key, end_key, currentRecord.right, result)

    def insert(self, record: Venta):
        with open(self.filename, "r+b") as file:
            file.seek(0, 2)
            pos = (int)((file.tell() - self.HEADER_SIZE) / self.RECORD_SIZE)
            file.write(struct.pack(self.FORMAT, record.id, record.nombre.encode(), record.cantidad_vendida, record.precio, record.fecha.encode(), record.left, record.right, record.height))
            self.root = self.insert_aux(file, record, self.root, pos)
            file.seek(0)
            file.write(struct.pack("i", self.root))

    def remove(self, key: int) -> int:
        with open(self.filename, "r+b") as file:
            self.root = self.remove_aux(file, key, self.root)
            file.seek(0)
            file.write(struct.pack("i", self.root))
        
    def search(self, key: int) -> Venta:
        with open(self.filename, "rb") as file:
            file.seek(0)

            currentPos = self.root

            while True:
                if currentPos == -1:
                    return None
                currentRecord = self.read_register(file, currentPos)

                if key > currentRecord.id:
                    currentPos = currentRecord.right
                elif key < currentRecord.id:
                    currentPos = currentRecord.left
                else:
                    return currentRecord

    def range_search(self, init_key: int, end_key: int) -> list[Venta]:
        list = []
        with open(self.filename, "rb") as file:
            self.range_search_aux(file, init_key, end_key, self.root, list)
        return list

    def load_from_csv(self, csv_filename):
        """Loads and inserts all records from a CSV file"""
        with open(csv_filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                try:
                    # Parse CSV row (assuming format: id,nombre,cantidad,precio,fecha)
                    id = int(row[0])
                    nombre = row[1]
                    cantidad = int(row[2])
                    precio = float(row[3])
                    fecha = row[4]
                    
                    # Create and insert record
                    venta = Venta(id, nombre, cantidad, precio, fecha)
                    self.insert(venta)
                    
                except (ValueError, IndexError) as e:
                    print(f"Error processing row {row}: {e}")
                    continue

def test(avl: AVL):
    # venta1 = Venta(0, "item1", 10, 5, "2025-04-03")
    # venta2 = Venta(4, "item2", 10, 5, "2025-04-03")
    # venta3 = Venta(2, "item3", 10, 5, "2025-04-03")
    # venta4 = Venta(3, "item4", 10, 5, "2025-04-03")

    # avl.insert(venta1)
    # avl.insert(venta2)
    # avl.insert(venta3)
    # avl.insert(venta4)

    # avl.remove(4)

    # print(avl.search(4))

    ids = []

    for i in range(1000):
        id = random.randint(0, 10000)
        while id in ids:
            id = random.randint(0, 10000)
        ids.append(id)
        venta = Venta(id, "item" + str(i), 1, 5.12, "2025-04-03")
        avl.insert(venta)

    for id in ids:
        if avl.search(id) == None:
            print("fue todo")

    sorted_ids = ids.copy()

    sorted_ids.sort()

    new_list = sorted_ids[100:-100]

    ranged_search = avl.range_search(sorted_ids[100], sorted_ids[-101])

    ranged_search_ids = []

    for record in ranged_search:
        ranged_search_ids.append(record.id)

    ranged_search_ids.sort()

    if new_list != ranged_search_ids:
        print("fue todo")

    for id in ids:
        avl.remove(id)
        if avl.search(id) != None:
            print("fue todo")

    print(avl.root)

def main():
    try:
        os.remove("./avl_data.dat")
    finally:
        avl = AVL("avl_data.dat")
        test(avl)
        # avl.load_from_csv("sales_dataset.csv")