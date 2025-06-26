CREATE OR REPLACE PROCEDURE insertar_paciente(
  p_dni CHAR(8),
  p_nombre VARCHAR,
  p_ciudad VARCHAR,
  p_diagnostico VARCHAR,
  p_peso DECIMAL,
  p_edad INTEGER,
  p_sexo CHAR(1)
)
LANGUAGE plpgsql
AS $$
DECLARE
  nombre_tabla TEXT;
  existe_particion BOOLEAN;
BEGIN
  nombre_tabla := 'paciente_' || replace(lower(p_diagnostico), ' ', '_');

  -- Verificamos si la particion ya existe
  SELECT EXISTS (
    SELECT 1
    FROM information_schema.tables
    WHERE table_name = nombre_tabla
  ) INTO existe_particion;

  -- Si no existe, creamos la particion
  IF NOT existe_particion THEN
    EXECUTE format(
      'CREATE TABLE %I PARTITION OF paciente FOR VALUES IN (%L)',
      nombre_tabla,
      p_diagnostico
    );
  END IF;

  -- Inserta el paciente
  EXECUTE format(
    'INSERT INTO paciente VALUES (%L, %L, %L, %L, %s, %s, %L)',
    p_dni,
    p_nombre,
    p_ciudad,
    p_diagnostico,
    p_peso,
    p_edad,
    p_sexo
  );
END;
$$;
