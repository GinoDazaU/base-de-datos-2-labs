#include <iostream>
#include <fstream>
#include <vector>

using  namespace std;

// Se debe implementar un programa para leer y escribir registros de longitud variable en un 
// archivo binario usando el tamaño del dato como separador.

class Matricula{
public:
    bool activo = true; // Usado como flag para la eliminacion
    string codigo;
    int ciclo;
    float mensualidad;
    string observaciones;

    Matricula(string _codigo, int _ciclo, float _mensualidad, string _observaciones){
        codigo = _codigo;
        ciclo = _ciclo;
        mensualidad = _mensualidad;
        observaciones = _observaciones;
    }

    Matricula(){}

    void print_data(){
        cout << "Codigo: " << codigo << " | Ciclo: " << ciclo << " | Mensualidad: " << mensualidad << " | Observaciones: " << observaciones << endl;  
    }
};

class RegistroBinario{
private:
    string filename;
    string metadata;

   // Funcion auxiliar para escribir strings con su longitud (primero la longitud)
    void writeString(ofstream& file, const string& str) {
        size_t length = str.size();
        file.write(reinterpret_cast<const char*>(&length), sizeof(length));
        file.write(str.c_str(), length);
    }
    
public:

    RegistroBinario(string _filename, string _metadata){
        filename = _filename;
        metadata = _metadata;
    }

    void add(const Matricula& record) {
        ofstream file(filename, ios::binary | ios::ate | ios::app);
        ofstream meta(metadata, ios::binary | ios::ate | ios::app);
        
        // Guardamos la posicion del cursor en metadatos
        streampos pos = file.tellp();
        meta.write(reinterpret_cast<const char*>(&pos), sizeof(pos));

        // Escribimos cada campo con su tamaño cuando es texto
        file.write(reinterpret_cast<const char*>(&record.activo), sizeof(record.activo));
        writeString(file, record.codigo);
        file.write(reinterpret_cast<const char*>(&record.ciclo), sizeof(record.ciclo));
        file.write(reinterpret_cast<const char*>(&record.mensualidad), sizeof(record.mensualidad));
        writeString(file, record.observaciones);

        // Calculamos el tamaño total del registro
        size_t record_size = sizeof(size_t) + record.codigo.size() + 
                            sizeof(record.ciclo) + 
                            sizeof(record.mensualidad) + 
                            sizeof(size_t) + record.observaciones.size();

        // Guardamos el tamaño en el metadata
        meta.write(reinterpret_cast<const char*>(&record_size), sizeof(record_size));

        file.close();
        meta.close();
    }
    
    // Para leer un registro primero se busca su posicion en la metadata y luego se usa
    // para ubicar el cursor en el archivo de datos, luego se lee cada campo en un orden especifico
    // para los strings primero se lee el tamaño de este.

    Matricula readRecord(int pos){
        // Abrimos el registro junto a su metadata
        ifstream file(filename, ios::binary | ios::in);
        ifstream meta(metadata, ios::binary | ios::in);

        // Buscamos la posicion del registro deseado en la metadata
        meta.seekg((sizeof(streampos) + sizeof(size_t)) * pos, ios::beg);

        streampos record_pos;
        meta.read(reinterpret_cast<char*>(&record_pos), sizeof(record_pos));
        
        // Buscamos el tamaño del registro deseado en la metadata
        size_t record_size;
        meta.read(reinterpret_cast<char*>(&record_size), sizeof(record_size));

        // Buscamos y leemos el registro de acuerdo a su posicion
        // Creamos cada variable dependiendo del tipo de dato y recuperamos sus valores
        string codigo, observaciones;
        int ciclo; float mensualidad;
        size_t string_size;
        bool activo;

        file.seekg(record_pos, ios::beg);

        file.read(reinterpret_cast<char*>(&activo),sizeof(activo));

        if(!activo){
            cout << "Matricula numero " << pos << " eliminada.";
            cout << endl;
            Matricula m1("vacio", 0, 0, "vacio");
            m1.activo = false;
            return m1;
        }

        file.read(reinterpret_cast<char*>(&string_size), sizeof(string_size));
        codigo.resize(string_size);
        file.read(&codigo[0], string_size);

        file.read(reinterpret_cast<char*>(&ciclo), sizeof(ciclo));

        file.read(reinterpret_cast<char*>(&mensualidad), sizeof(mensualidad));

        file.read(reinterpret_cast<char*>(&string_size), sizeof(string_size));
        observaciones.resize(string_size);
        file.read(&observaciones[0], string_size);

        meta.close();
        file.close();

        return Matricula(codigo, ciclo, mensualidad, observaciones);;
    }

    // Usamos el metodo readRecord en un bucle for, el rango sera el numero de registros
    // que se obtendra con un while en la metadata hasta salir del archivo.
    vector<Matricula> load() {
        vector<Matricula> registros;
        ifstream meta(metadata, ios::binary | ios::in);
    
        int totalRegistros = 0;
        streampos record_pos;
        size_t record_size;
    
        // Primer paso: contar la cantidad de registros en la metadata
        while (meta.read(reinterpret_cast<char*>(&record_pos), sizeof(record_pos)) &&
               meta.read(reinterpret_cast<char*>(&record_size), sizeof(record_size))) {
            totalRegistros++;
        }
    
        meta.close();
    
        // Segundo paso: leer registros y filtrar los activos
        for (int i = 0; i < totalRegistros; i++) {
            Matricula record = readRecord(i);
            if (record.activo) { 
                registros.push_back(record);
            }
        }
    
        return registros;
    }

     // Para remover se usara un flag en el registro (primer campo)
     // La eliminacion seria O(1), la desventaja seria que ese espacio quedaria desperdiciado
     // ya que al ser longitud variable no podriamos reemplazarlo con un nuevo registro facilmente.
    void remove(int pos){  
        
        ifstream meta(metadata, ios::binary);
        size_t record_pos;
        meta.seekg((sizeof(streampos) + sizeof(size_t)) * pos, ios::beg);
        meta.read(reinterpret_cast<char*>(&record_pos), sizeof(record_pos));
        meta.close();

        fstream file(filename, ios::binary | ios::in | ios::out);
        file.seekp(record_pos, ios::beg);
        bool activo = false;
        file.write(reinterpret_cast<char*>(&activo), sizeof(activo));
        file.close();
    }
};

int main(){

    Matricula m1("202310505", 4, 2500.1, "abcde");
    Matricula m2("LKJ102345", 5, 2700.5, "qwerty");
    Matricula m3("20251032C", 6, 2800.3, "zxcvbnm");
    Matricula m4("ABC210123", 6, 2800.3, "zxcvbnmasd");

    // Creamos el gestor de registros y le pasamos el archivo a leer o modificar con su metadata.

    RegistroBinario registro("matriculas.dat", "metadata.dat");


    // Añadimos 4 registros con add()

    registro.add(m1);
    registro.add(m2);
    registro.add(m3);
    registro.add(m4);

    // Leemos los primeros tres registro con readRecord() e imprimimos su data

    Matricula r1 = registro.readRecord(0);
    Matricula r2 = registro.readRecord(1);
    Matricula r3 = registro.readRecord(2);

    r1.print_data();
    r2.print_data();
    r3.print_data();

    cout << endl;

    // Cargamos todos los registros con load() e imprimos su data
    // (se imprimiran los 4)
    vector<Matricula> matriculas1 = registro.load();
    for(Matricula m:matriculas1){
        m.print_data();
    }

    // Eliminamos el segundo registro con remove()
    // y mostramos todos los registros otra vez

    registro.remove(1); // avisara que se borro el registro

    // mostrara 3 registros porque se borro uno
    vector<Matricula> matriculas2 = registro.load();
    for(Matricula m:matriculas2){
        m.print_data();
    }

}
