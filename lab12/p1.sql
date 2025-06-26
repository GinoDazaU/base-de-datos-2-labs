CREATE TABLE Paciente (
  DNI CHAR(8),
  Nombre VARCHAR(100) NOT NULL,
  Ciudad VARCHAR(50) NOT NULL,
  Diagnóstico VARCHAR(50) NOT NULL,
  Peso DECIMAL(5,2) NOT NULL,
  Edad INTEGER NOT NULL CHECK (Edad >= 0),
  Sexo CHAR(1) NOT NULL CHECK (Sexo IN ('M', 'F'))
) PARTITION BY LIST (Diagnóstico);


CREATE TABLE Paciente_Diabetes PARTITION OF Paciente
  FOR VALUES IN ('Diabetes');

CREATE TABLE Paciente_Obesidad PARTITION OF Paciente
  FOR VALUES IN ('Obesidad');

CREATE TABLE Paciente_Cardiopatia PARTITION OF Paciente
  FOR VALUES IN ('Cardiopatía');

CREATE TABLE Paciente_Hipertension PARTITION OF Paciente
  FOR VALUES IN ('Hipertensión');


INSERT INTO Paciente VALUES
('45781236', 'Carla María Romero Díaz', 'Lima', 'Diabetes', 70, 45, 'F'),
('08569321', 'Luis Alberto Díaz Mendoza', 'Lima', 'Hipertensión', 85, 60, 'M'),
('72103654', 'Ana Paula Torres Castro', 'Callao', 'Obesidad', 90, 35, 'F'),
('25963147', 'Jorge Luis Ramírez Vargas', 'Callao', 'Cardiopatía', 78, 50, 'M'),
('15478962', 'María Carmen Suárez López', 'Lima', 'Diabetes', 65, 42, 'F'),
('36987412', 'Pedro José Quispe Huamán', 'Lima', 'Obesidad', 95, 38, 'M'),
('65412398', 'Rosa Isabel Valle García', 'Lima', 'Hipertensión', 72, 55, 'F'),
('89632147', 'Miguel Ángel Castro Rivas', 'Callao', 'Cardiopatía', 82, 48, 'M');


-- nueva info
CREATE TABLE Paciente_Asma PARTITION OF Paciente
  FOR VALUES IN ('Asma');
INSERT INTO Paciente VALUES
('78451236', 'Diana López Rivera', 'Cusco', 'Asma', 60, 30, 'F');
CREATE TABLE Paciente_Covid PARTITION OF Paciente FOR VALUES IN ('Covid-19');
INSERT INTO Paciente VALUES
('78562314', 'Juan Pérez Valdez', 'Cusco', 'Covid-19', 68, 52, 'M'),
('89562374', 'Lucía Gutiérrez Solís', 'Trujillo', 'Covid-19', 70, 43, 'F');
