import struct

class Venta:
    def __init__(self, id, nombre, cantidad_vendida, precio_unitario, fecha):
        self.id = id
        self.nombre = nombre
        self.cantidad_vendida = cantidad_vendida
        self.precio_unitario = precio_unitario
        self.fecha = fecha
        
        self.next = -1

class SecuentialRegister:
    FORMAT = "ii30sif10si"
    RECORD_SIZE = struct.calcsize(FORMAT)

    def __init__(self, filename):
        self.filename = filename

    

    def insert(self, record: Venta):
        with open(self.filename, "r+b") as file:
            packed_data = struct.pack(
                self.FORMAT,
                record.id,
                record.nombre,
                record.precio_unitario,
                record.cantidad_vendida,
                record.fecha,
                record.next)

            pos = file.tell()
            if pos == 0:
                file.write("1")
                file.write(packed_data)
                print("Registro insertado correctamente.")
                return
            


    # Como tengo que buscar si el registro ya esta primero hare el search
    # Vere si puedo hardcodear un archivo para probarlo

    def search(self, key):
        with open(self.filename, 'rb') as file:
            if file.tell() == 0:
                print("Archivo vacio")
                return
            
            header = file.read(4)
            records_number = struct.unpack("i", header)[0]

            low = 0
            high = records_number - 1
            found_record = None

            while low <= high:
                mid = (low + high) // 2
                offset = 4 + mid * self.RECORD_SIZE
                file.seek(offset)
                record_pack_data = file.read(self.RECORD_SIZE)
                record_data = struct.unpack(self.FORMAT, record_pack_data)
                record_id = record_data[0]
                if record_id == key:
                    found_record = record_data
                    return
                elif key > record_id:
                    low = mid + 1
                elif key < record_id:
                    high = mid - 1
            
            if found_record is not None:
                record_id, record_nombre, record_cantidad_vendida, record_precio_unitario, record_fecha = found_record
                venta = Venta(record_id, record_nombre, record_cantidad_vendida, record_precio_unitario, record_fecha)
                return venta
            
            # Aca tendria que buscar en el la data auxiliar
            

    def remove(self, key):
        pass

    def rangeSearch(init_key, end_key):
        pass
