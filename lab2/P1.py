import struct
import math

class Venta:
    def __init__(self, id, nombre, cantidad_vendida, precio_unitario, fecha):
        self.isActive = 1
        self.id = id
        self.nombre = nombre
        self.cantidad_vendida = cantidad_vendida
        self.precio_unitario = precio_unitario
        self.fecha = fecha
        

# el archivo tendra de metadata la cantidad de registros en la zona principal
class SecuentialRegister:
    FORMAT = "i30sif10s"
    RECORD_SIZE = struct.calcsize(FORMAT)

    def __init__(self, filename):
        self.filename = filename

    def insert(self, record: Venta):
        packed_record = struct.pack(
            self.FORMAT,
            record.id,
            record.nombre.encode(),
            record.cantidad_vendida,
            record.precio_unitario,
            record.fecha.encode()
        )

        with open(self.filename, "r+b") as file:
            file.seek(0, 2)
            pos = file.tell()

            # =====================
            # Paso 0: Archivo vacio, insertar el primer registro
            # =====================
            if pos == 0:
                file.write(struct.pack("i", 1))
                file.write(packed_record)
                print("Registro insertado correctamente (primer registro).")
                return

            file.seek(0)
            packed_rows = file.read(4)
            data_rows = struct.unpack("i", packed_rows)[0]
            aux_rows = max(1, math.floor(math.log2(data_rows)))

            # =====================
            # Paso 1: Buscar en zona principal (binaria)
            # =====================
            left, right = 0, data_rows - 1
            found = False
            while left <= right:
                mid = (left + right) // 2
                file.seek(4 + mid * self.RECORD_SIZE)
                packed = file.read(self.RECORD_SIZE)
                id_registro = struct.unpack("i", packed[:4])[0]
                if id_registro == -1:
                    left = mid + 1
                    continue
                if id_registro == record.id:
                    found = True
                    break
                elif id_registro < record.id:
                    left = mid + 1
                else:
                    right = mid - 1

            # =====================
            # Paso 2: Buscar en zona auxiliar (secuencial)
            # =====================
            file.seek(4 + data_rows * self.RECORD_SIZE)
            packed_aux_records = file.read(aux_rows * self.RECORD_SIZE)

            # rellena con ceros si aun no existen en el archivo
            if len(packed_aux_records) < aux_rows * self.RECORD_SIZE:
                packed_aux_records += b'\x00' * (aux_rows * self.RECORD_SIZE - len(packed_aux_records))


            for i in range(aux_rows):
                offset = i * self.RECORD_SIZE
                id_aux = struct.unpack("i", packed_aux_records[offset : offset + 4])[0]
                if id_aux == record.id:
                    found = True
                    break

            if found:
                print("Error: El registro con este ID ya existe.")
                return

            # =====================
            # Paso 3: Insertar en espacio libre de zona auxiliar
            # =====================
            for i in range(aux_rows):
                offset = i * self.RECORD_SIZE
                id_aux = struct.unpack("i", packed_aux_records[offset : offset + 4])[0]
                if id_aux == -1:
                    aux_start = 4 + data_rows * self.RECORD_SIZE
                    file.seek(aux_start + i * self.RECORD_SIZE)
                    file.write(packed_record)
                    print(f"Registro insertado en la zona auxiliar (posicion {i}).")
                    return

            # =====================
            # Paso 4: Zona auxiliar llena -> reorganizar
            # =====================
            print("Zona auxiliar llena. Reorganización requerida (workinprogress).")

    

    def search(self, key):
        pass

    def remove(self, key):
        pass

    def rangeSearch(init_key, end_key):
        pass







import os
import csv

if not os.path.exists("data.dat"):
    with open("data.dat", "wb") as f:
        pass

ventas = []
with open("sales_dataset.csv", "r") as data:
    reader = csv.reader(data)
    next(reader) 
    for row in reader:
        id_venta = int(row[0])
        nombre = row[1].ljust(30)[:30]
        cantidad = int(row[2])
        precio = float(row[3])
        fecha = row[4].ljust(10)[:10]

        venta = Venta(id_venta, nombre, cantidad, precio, fecha)
        ventas.append(venta)

secuentialRegister = SecuentialRegister("data.dat")

for i in range(2):
    secuentialRegister.insert(ventas[i])
