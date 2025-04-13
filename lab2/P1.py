import struct
import math
import os

class Venta:
    def __init__(self, id, nombre, cantidad_vendida, precio_unitario, fecha):
        self.isActive = 1
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
        packed_record = struct.pack(
            self.FORMAT,
            record.id,
            record.nombre.encode(),
            record.cantidad_vendida,
            record.precio_unitario,
            record.fecha.encode()
        )

        reorganize_needed = False

        with open(self.filename, "r+b") as file:
            file.seek(0, 2)
            pos = file.tell()

            # --------------------------------------------------
            # Paso 0: Archivo vacio, insertar el primer registro
            # ---------------------------------------------------
            if pos == 0:
                file.write(struct.pack("i", 1))
                file.write(packed_record)
                aux_rows = max(1, math.floor(math.log2(1)))
                empty_record = struct.pack(
                    self.FORMAT,
                    -1, b'\x00' * 30, 0, 0.0, b'\x00' * 10
                )
                for _ in range(aux_rows):
                    file.write(empty_record)
                print(f"Registro insertado correctamente (primer registro). ID: {record.id}")
                return

            file.seek(0)
            packed_rows = file.read(4)
            data_rows = struct.unpack("i", packed_rows)[0]
            aux_rows = max(1, math.floor(math.log2(data_rows)))

            # ------------------------------------------
            # Paso 1: Buscar en zona principal (binaria)
            # ------------------------------------------
            left, right = 0, data_rows - 1
            found = False
            while left <= right:
                mid = (left + right) // 2
                file.seek(4 + mid * self.RECORD_SIZE)
                packed = file.read(self.RECORD_SIZE)
                if len(packed) < self.RECORD_SIZE:
                    break
                id_registro = struct.unpack("i", packed[:4])[0]
                
                if id_registro == -1:
                    # Buscar el siguiente registro no vacio hacia la derecha
                    temp_pos = mid + 1
                    while temp_pos <= right:
                        file.seek(4 + temp_pos * self.RECORD_SIZE)
                        temp_packed = file.read(self.RECORD_SIZE)
                        if len(temp_packed) < self.RECORD_SIZE:
                            break
                        temp_id = struct.unpack("i", temp_packed[:4])[0]
                        if temp_id != -1:
                            if temp_id == record.id:
                                found = True
                                break
                            elif temp_id < record.id:
                                left = temp_pos + 1
                            else:
                                right = mid - 1
                            break
                        temp_pos += 1
                    else:
                        # Todos los registros a la derecha estan vacios
                        right = mid - 1
                    if found:
                        break
                    continue
                
                if id_registro == record.id:
                    found = True
                    break
                elif id_registro < record.id:
                    left = mid + 1
                else:
                    right = mid - 1

            # --------------------------------------------
            # Paso 2: Buscar en zona auxiliar (secuencial)
            # --------------------------------------------
            if not found:
                file.seek(4 + data_rows * self.RECORD_SIZE)
                packed_aux_records = file.read(aux_rows * self.RECORD_SIZE)
                if len(packed_aux_records) < aux_rows * self.RECORD_SIZE:
                    packed_aux_records += b'\x00' * (aux_rows * self.RECORD_SIZE - len(packed_aux_records))

                for i in range(aux_rows):
                    offset = i * self.RECORD_SIZE
                    if offset + 4 > len(packed_aux_records):
                        continue
                    id_aux = struct.unpack("i", packed_aux_records[offset : offset + 4])[0]
                    if id_aux == record.id:
                        found = True
                        break

            if found:
                print(f"Error: El registro con ID {record.id} ya existe.")
                return

            # --------------------------------------------------
            # Paso 3: Insertar en espacio libre de zona auxiliar
            # --------------------------------------------------
            inserted = False
            if not found:
                file.seek(4 + data_rows * self.RECORD_SIZE)
                packed_aux_records = file.read(aux_rows * self.RECORD_SIZE)
                if len(packed_aux_records) < aux_rows * self.RECORD_SIZE:
                    packed_aux_records += b'\x00' * (aux_rows * self.RECORD_SIZE - len(packed_aux_records))

                for i in range(aux_rows):
                    offset = i * self.RECORD_SIZE
                    if offset + 4 > len(packed_aux_records):
                        continue
                    id_aux = struct.unpack("i", packed_aux_records[offset : offset + 4])[0]
                    if id_aux == -1:
                        aux_start = 4 + data_rows * self.RECORD_SIZE
                        file.seek(aux_start + i * self.RECORD_SIZE)
                        file.write(packed_record)
                        print(f"Registro insertado en la zona auxiliar (posición {i}). ID: {record.id}")
                        inserted = True
                        break

            # ------------------------------------------
            # Paso 4: Zona auxiliar llena -> reorganizar
            # ------------------------------------------
            if not inserted and not found:
                print(f"Zona auxiliar llena. Se requiere reorganizacion para ID: {record.id}")
                reorganize_needed = True

        # En caso sea necesario se reorganiza
        if reorganize_needed:
            self.reorganize()
            # Despues de reorganizar, intentar insertar de nuevo (se llama al mismo metodo)
            self.insert(record)

    def reorganize(self):
        with open(self.filename, "r+b") as file:
            file.seek(0)
            data_rows = struct.unpack("i", file.read(4))[0]

            # Leer zona principal (todos los registros, no solo los activos)
            main_records = []
            for i in range(data_rows):
                file.seek(4 + i * self.RECORD_SIZE)
                rec = file.read(self.RECORD_SIZE)
                if len(rec) < self.RECORD_SIZE:
                    break
                id_reg = struct.unpack("i", rec[:4])[0]
                main_records.append((id_reg, rec))

            # Filtrar solo registros activos de la zona principal
            active_main_records = [rec for id_reg, rec in main_records if id_reg != -1]

            # Leer zona auxiliar
            aux_rows = max(1, math.floor(math.log2(data_rows)))
            aux_records = []
            file.seek(4 + data_rows * self.RECORD_SIZE)
            aux_zone_bytes = file.read(aux_rows * self.RECORD_SIZE)
            for i in range(aux_rows):
                offset = i * self.RECORD_SIZE
                if offset + self.RECORD_SIZE > len(aux_zone_bytes):
                    break
                rec = aux_zone_bytes[offset : offset + self.RECORD_SIZE]
                id_aux = struct.unpack("i", rec[:4])[0]
                if id_aux != -1:
                    aux_records.append(rec)

        # Ordenar la zona auxiliar con insertion sort
        for j in range(1, len(aux_records)):
            key = aux_records[j]
            key_id = struct.unpack("i", key[:4])[0]
            i = j - 1
            while i >= 0 and struct.unpack("i", aux_records[i][:4])[0] > key_id:
                aux_records[i + 1] = aux_records[i]
                i -= 1
            aux_records[i + 1] = key

        # Fusionar las listas ordenadas
        merged = []
        i = j = 0
        main_records_sorted = sorted(active_main_records, key=lambda x: struct.unpack("i", x[:4])[0])
        
        while i < len(main_records_sorted) and j < len(aux_records):
            main_id = struct.unpack("i", main_records_sorted[i][:4])[0]
            aux_id = struct.unpack("i", aux_records[j][:4])[0]
            if main_id < aux_id:
                merged.append(main_records_sorted[i])
                i += 1
            else:
                merged.append(aux_records[j])
                j += 1
        while i < len(main_records_sorted):
            merged.append(main_records_sorted[i])
            i += 1
        while j < len(aux_records):
            merged.append(aux_records[j])
            j += 1

        new_data_rows = len(merged)
        temp_filename = self.filename + ".tmp"
        with open(temp_filename, "wb") as temp_file:
            temp_file.write(struct.pack("i", new_data_rows))
            for rec in merged:
                temp_file.write(rec)

            aux_rows = max(1, math.floor(math.log2(new_data_rows)))
            empty_record = struct.pack(
                self.FORMAT,
                -1, b'\x00' * 30, 0, 0.0, b'\x00' * 10
            )
            for _ in range(aux_rows):
                temp_file.write(empty_record)

        try:
            os.remove(self.filename)
            os.rename(temp_filename, self.filename)
            print(f"Reorganizacion completada. Nueva zona principal con {new_data_rows} registros.")
        except PermissionError as e:
            print(f"Error al intentar eliminar el archivo: {e}")


    def load(self):
        with open(self.filename, "rb") as file:
            data = file.read(4)
            if len(data) < 4:
                print("Archivo vacio o corrupto.")
                return
            data_rows = struct.unpack("i", data)[0]
            print(f"\nCantidad de registros en zona principal: {data_rows}")

            print("\nZona Principal:")
            for i in range(data_rows):
                record_bytes = file.read(self.RECORD_SIZE)
                if len(record_bytes) < self.RECORD_SIZE:
                    break
                id_, nombre, cantidad, precio, fecha = struct.unpack(self.FORMAT, record_bytes)
                if id_ != -1:
                    print(f"ID: {id_}, Nombre: {nombre.decode().strip()}, Cantidad: {cantidad}, Precio: {precio}, Fecha: {fecha.decode().strip()}")

            aux_rows = max(1, math.floor(math.log2(data_rows)))

            print("\nZona Auxiliar:")
            for _ in range(aux_rows):
                record_bytes = file.read(self.RECORD_SIZE)
                if len(record_bytes) < self.RECORD_SIZE:
                    break
                id_, nombre, cantidad, precio, fecha = struct.unpack(self.FORMAT, record_bytes)
                if id_ != -1:
                    print(f"ID: {id_}, Nombre: {nombre.decode().strip()}, Cantidad: {cantidad}, Precio: {precio}, Fecha: {fecha.decode().strip()}")




# prueba

import csv

if not os.path.exists("data.dat"):
    with open("data.dat", "wb") as f:
        pass

ventas = []
with open("sales_dataset_copy.csv", "r", encoding="utf-8") as data:
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

for i in range(300):
    secuentialRegister.insert(ventas[i])

secuentialRegister.load()