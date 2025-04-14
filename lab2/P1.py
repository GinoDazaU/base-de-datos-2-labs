import struct
import math
import os

class Record:

    FORMAT = "i30sif10s"
    SIZE = struct.calcsize(FORMAT)

    def __init__(self, id: int, nombre: str, cantidad_vendida: int, precio_unitario: float, fecha: str):
        self.id = id
        self.nombre = nombre
        self.cantidad_vendida = cantidad_vendida
        self.precio_unitario = precio_unitario
        self.fecha = fecha

    def pack(self):
        nombre = self.nombre[:30].ljust(30, '\x00')
        fecha = self.fecha[:10].ljust(10, '\x00')
        
        return struct.pack(
            self.FORMAT,
            self.id,
            nombre.encode('utf-8'),
            self.cantidad_vendida,
            self.precio_unitario,
            fecha.encode('utf-8')
        )
    
    @staticmethod
    def unpack(record_buffer):
        id, nombre, cantidad_vendida, precio_unitario, fecha = struct.unpack(Record.FORMAT, record_buffer)
        return Record(
            id,
            nombre.decode('utf-8').rstrip('\x00'),
            cantidad_vendida,
            precio_unitario,
            fecha.decode('utf-8').rstrip('\x00')
        )
    
    def print(self):
        print(f"Id: {self.id} | Nombre: {self.nombre} | Cantidad Vendida: {self.cantidad_vendida} | Precio unitario: {self.precio_unitario} | Fecha: {self.fecha}")
    
class SecuentialRecorder:

    METADATA_FORMAT = ("iii")
    METADATA_SIZE = struct.calcsize(METADATA_FORMAT)

    def __init__(self, filename):
        self.filename = filename

        if os.path.exists(filename):
            with open(filename, "rb") as file:
                metadata_buffer = file.read(self.METADATA_SIZE)
                self.main_size, self.aux_size, self.max_aux_size = struct.unpack(self.METADATA_FORMAT, metadata_buffer)
        else:
            with open(filename, "wb") as file:
                self.main_size = 0
                self.aux_size = 0
                self.max_aux_size = 1
                metadata_buffer = struct.pack(self.METADATA_FORMAT, self.main_size, self.aux_size, self.max_aux_size)
                file.write(metadata_buffer)


    def update_metadata(self):
        with open(self.filename, "r+b") as file:
            metadata_buffer = struct.pack(self.METADATA_FORMAT, self.main_size, self.aux_size, self.max_aux_size)
            file.write(metadata_buffer)

    def insert_record(self, record: Record):
        """Inserta un registro en el area auxiliar y reconstruye si es necesario"""

        # 0. Verificar que el registro no exista
        if self.search_record(record.id) != None:
            print(f"El registro con id: {record.id} ya existe")
            return False

        # 1. Escribir en área auxiliar
        with open(self.filename, "r+b") as file:
            # Posicionarse al final del área auxiliar
            file.seek(self.METADATA_SIZE + self.main_size * Record.SIZE + self.aux_size * Record.SIZE)
            file.write(record.pack())
            self.aux_size += 1
            self.update_metadata()
            print("Registro insertado correctamente")
        
        # 2. Reconstruir si se excede el límite
        if self.aux_size > self.max_aux_size:
            print("Zona auxiliar llena, reconstruyendo archivo...")
            self.rebuild_file()

    def rebuild_file(self):
        """Reconstruye el archivo fusionando areas principal y auxiliar"""
        # 1. Leer todos los registros activos
        active_records = []
        
        # Leer área principal
        with open(self.filename, "rb") as file:
            file.seek(self.METADATA_SIZE)
            for _ in range(self.main_size):
                buffer = file.read(Record.SIZE)
                if not buffer: break
                record = Record.unpack(buffer)
                if record.id != -1:
                    active_records.append(record)
        
        # Leer área auxiliar
        with open(self.filename, "rb") as file:
            file.seek(self.METADATA_SIZE + self.main_size * Record.SIZE)
            for _ in range(self.aux_size):
                buffer = file.read(Record.SIZE)
                if not buffer: break
                record = Record.unpack(buffer)
                if record.id != -1:
                    active_records.append(record)
        
        # 2. Ordenar por ID (insertion sort)
        for i in range(1, len(active_records)):
            key = active_records[i]
            j = i - 1
            while j >= 0 and active_records[j].id > key.id:
                active_records[j + 1] = active_records[j]
                j -= 1
            active_records[j + 1] = key
        
        # 3. Calcular nuevo tamaño auxiliar (nunca menor a 1)
        new_main_size = len(active_records)
        new_max_aux = max(1, math.floor(math.log2(new_main_size))) if new_main_size > 0 else 1

        
        # 4. Escribir el nuevo archivo
        temp_filename = self.filename + ".tmp"
        with open(temp_filename, "wb") as file:
            # Escribir metadata
            metadata = struct.pack(self.METADATA_FORMAT, new_main_size, 0, new_max_aux)
            file.write(metadata)
            
            # Escribir registros principales
            for record in active_records:
                file.write(record.pack())
            
            # Escribir área auxiliar vacía
            empty_record = Record(-1, "", 0, 0.0, "").pack()
            for _ in range(new_max_aux):
                file.write(empty_record)
        
        # 5. Reemplazar archivo
        os.replace(temp_filename, self.filename)
        
        # 6. Actualizar metadatos
        self.main_size = new_main_size
        self.aux_size = 0
        self.max_aux_size = new_max_aux

    def search_record(self, id: int):
        """Busca un registro por ID usando búsqueda binaria (principal) + secuencial (auxiliar)"""
        # 1. Busqueda binaria en area principal
        with open(self.filename, "rb") as file:
            file.seek(self.METADATA_SIZE)
            left, right = 0, self.main_size - 1
            
            while left <= right:
                mid = (left + right) // 2
                file.seek(self.METADATA_SIZE + mid * Record.SIZE)
                buffer = file.read(Record.SIZE)
                record = Record.unpack(buffer)
                
                if record.id == id:
                    return record
                elif record.id < id:
                    left = mid + 1
                else:
                    right = mid - 1
        
        # 2. Busqueda secuencial en area auxiliar (cargada en RAM)
        with open(self.filename, "rb") as file:
            file.seek(self.METADATA_SIZE + self.main_size * Record.SIZE)
            for _ in range(self.aux_size):
                buffer = file.read(Record.SIZE)
                record = Record.unpack(buffer)
                if record.id == id:
                    return record
        
        return None

    def load(self):
        with open(self.filename, 'rb') as file:
            metadata_buffer = file.read(self.METADATA_SIZE)
            main_size, aux_size, max_aux_size = struct.unpack(self.METADATA_FORMAT, metadata_buffer)
            records = []
            for i in range(main_size + aux_size):
                record_buffer = file.read(Record.SIZE)
                records.append(Record.unpack(record_buffer))

            print("\nMetadata:")
            print(f"Tamaño de la zona principal: {main_size}")
            print(f"Tamaño de la zona auxiliar: {aux_size}")
            print(f"Tamaño maximo de la zona auxiliar: {max_aux_size}")
            print("Registros:")
            for i in range(main_size + aux_size):
                records[i].print()





# Crear archivo
registrador = SecuentialRecorder("test.dat")

# Insertar 2 registros
registrador.insert_record(Record(1, "A", 10, 1.0, "2023-01-01"))
registrador.insert_record(Record(2, "B", 20, 2.0, "2023-01-02"))

registrador.load()