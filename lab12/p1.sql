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

INSERT INTO Paciente VALUES
-- Diabetes
('13245768', 'Natalia Estefanía León Castañeda', 'Chiclayo', 'Diabetes', 67.9, 46, 'F'),
('24356879', 'Diego Martín Salinas Bravo', 'Cusco', 'Diabetes', 72.4, 51, 'M'),
('35467980', 'Andrea Lucero Velásquez Poma', 'Tacna', 'Diabetes', 66.2, 39, 'F'),
('12345678', 'Lucía Fernanda Paredes Sánchez', 'Arequipa', 'Diabetes', 68.5, 52, 'F'),
('23456789', 'Carlos Enrique Rojas Peña', 'Trujillo', 'Diabetes', 74.2, 49, 'M'),
('34567890', 'Julieta Noemí Gutiérrez Valle', 'Cusco', 'Diabetes', 69.7, 58, 'F'),
-- Obesidad
('46578091', 'Javier Alonso Cabrera Núñez', 'Iquitos', 'Obesidad', 110.5, 42, 'M'),
('57689102', 'Melissa Karina Reyes Portugal', 'Huánuco', 'Obesidad', 92.8, 36, 'F'),
('68790213', 'Juan Pablo Córdova Fernández', 'Pucallpa', 'Obesidad', 105.7, 48, 'M'),
('45678901', 'Eduardo Daniel Palacios León', 'Piura', 'Obesidad', 102.3, 44, 'M'),
('56789012', 'Camila Antonia Herrera Soto', 'Lima', 'Obesidad', 88.6, 31, 'F'),
('67890123', 'Sofía Milagros Cárdenas Mejía', 'Huancayo', 'Obesidad', 91.0, 37, 'F'),
-- Cardiopatía
('79801324', 'Valeria Antonella Mejía Lozano', 'Trujillo', 'Cardiopatía', 74.6, 53, 'F'),
('80912435', 'Óscar Rafael Guzmán Torres', 'Lima', 'Cardiopatía', 79.3, 60, 'M'),
('91023546', 'Ruth Jimena Palomino Díaz', 'Arequipa', 'Cardiopatía', 73.9, 47, 'F'),
('78901234', 'José Armando Zúñiga Pérez', 'Cusco', 'Cardiopatía', 76.5, 61, 'M'),
('89012345', 'Martina Alejandra Ruiz Ríos', 'Lima', 'Cardiopatía', 70.8, 54, 'F'),
('90123456', 'Ricardo Esteban Torres Salas', 'Arequipa', 'Cardiopatía', 80.1, 59, 'M'),
-- Hipertensión
('92134657', 'Tomás Nicolás Rivas Paredes', 'Chimbote', 'Hipertensión', 88.0, 59, 'M'),
('83245768', 'Flor Mariela Gamarra Silva', 'Cusco', 'Hipertensión', 74.5, 56, 'F'),
('74356879', 'Enrique Alejandro Dueñas Campos', 'Ica', 'Hipertensión', 82.1, 62, 'M');
('91234567', 'Daniela Ruth Flores Chávez', 'Trujillo', 'Hipertensión', 73.0, 50, 'F'),
('82345678', 'Gabriel Joaquín Medina Ortiz', 'Piura', 'Hipertensión', 86.4, 63, 'M'),
('73456789', 'Patricia Elena Ramos Guevara', 'Lima', 'Hipertensión', 78.3, 57, 'F');
