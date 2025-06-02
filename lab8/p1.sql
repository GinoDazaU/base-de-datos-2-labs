CREATE EXTENSION IF NOT EXISTS cube;

-- Generación de tablas por dimensión
-- Cada tabla tiene: id, vector_lineal, vector_gist y un índice GiST

-- 2 dimensiones
CREATE TABLE vectors2 (id serial, vector_lineal cube, vector_gist cube);
INSERT INTO vectors2(id, vector_lineal)
SELECT id, cube(ARRAY[random()*1000, random()*1000])
FROM generate_series(1, 1000000) id;
UPDATE vectors2 SET vector_gist = vector_lineal;
CREATE INDEX idx_vectors2 ON vectors2 USING gist(vector_gist);

-- 4 dimensiones
CREATE TABLE vectors4 (id serial, vector_lineal cube, vector_gist cube);
INSERT INTO vectors4(id, vector_lineal)
SELECT id, cube(ARRAY[
  random()*1000, random()*1000, random()*1000, random()*1000
])
FROM generate_series(1, 100000) id;
UPDATE vectors4 SET vector_gist = vector_lineal;
CREATE INDEX idx_vectors4 ON vectors4 USING gist(vector_gist);

-- 6 dimensiones
CREATE TABLE vectors6 (id serial, vector_lineal cube, vector_gist cube);
INSERT INTO vectors6(id, vector_lineal)
SELECT id, cube(ARRAY[
  random()*1000, random()*1000, random()*1000,
  random()*1000, random()*1000, random()*1000
])
FROM generate_series(1, 1000000) id;
UPDATE vectors6 SET vector_gist = vector_lineal;
CREATE INDEX idx_vectors6 ON vectors6 USING gist(vector_gist);

-- 8 dimensiones
CREATE TABLE vectors8 (id serial, vector_lineal cube, vector_gist cube);
INSERT INTO vectors8(id, vector_lineal)
SELECT id, cube(ARRAY[
  random()*1000, random()*1000, random()*1000, random()*1000,
  random()*1000, random()*1000, random()*1000, random()*1000
])
FROM generate_series(1, 1000000) id;
UPDATE vectors8 SET vector_gist = vector_lineal;
CREATE INDEX idx_vectors8 ON vectors8 USING gist(vector_gist);

-- 16 dimensiones
CREATE TABLE vectors16 (id serial, vector_lineal cube, vector_gist cube);
INSERT INTO vectors16(id, vector_lineal)
SELECT id, cube(ARRAY[
  random()*1000, random()*1000, random()*1000, random()*1000,
  random()*1000, random()*1000, random()*1000, random()*1000,
  random()*1000, random()*1000, random()*1000, random()*1000,
  random()*1000, random()*1000, random()*1000, random()*1000
])
FROM generate_series(1, 1000000) id;
UPDATE vectors16 SET vector_gist = vector_lineal;
CREATE INDEX idx_vectors16 ON vectors16 USING gist(vector_gist);

-- 32 dimensiones
CREATE TABLE vectors32 (id serial, vector_lineal cube, vector_gist cube);
INSERT INTO vectors32(id, vector_lineal)
SELECT id, cube(ARRAY[
  random()*1000, random()*1000, random()*1000, random()*1000,
  random()*1000, random()*1000, random()*1000, random()*1000,
  random()*1000, random()*1000, random()*1000, random()*1000,
  random()*1000, random()*1000, random()*1000, random()*1000,
  random()*1000, random()*1000, random()*1000, random()*1000,
  random()*1000, random()*1000, random()*1000, random()*1000,
  random()*1000, random()*1000, random()*1000, random()*1000,
  random()*1000, random()*1000, random()*1000, random()*1000
])
FROM generate_series(1, 1000000) id;
UPDATE vectors32 SET vector_gist = vector_lineal;
CREATE INDEX idx_vectors32 ON vectors32 USING gist(vector_gist);

-- 64 dimensiones
CREATE TABLE vectors64 (id serial, vector_lineal cube, vector_gist cube);
INSERT INTO vectors64(id, vector_lineal)
SELECT id, cube(ARRAY[
  random()*1000, random()*1000, random()*1000, random()*1000,
  random()*1000, random()*1000, random()*1000, random()*1000,
  random()*1000, random()*1000, random()*1000, random()*1000,
  random()*1000, random()*1000, random()*1000, random()*1000,
  random()*1000, random()*1000, random()*1000, random()*1000,
  random()*1000, random()*1000, random()*1000, random()*1000,
  random()*1000, random()*1000, random()*1000, random()*1000,
  random()*1000, random()*1000, random()*1000, random()*1000,
  random()*1000, random()*1000, random()*1000, random()*1000,
  random()*1000, random()*1000, random()*1000, random()*1000,
  random()*1000, random()*1000, random()*1000, random()*1000,
  random()*1000, random()*1000, random()*1000, random()*1000,
  random()*1000, random()*1000, random()*1000, random()*1000,
  random()*1000, random()*1000, random()*1000, random()*1000,
  random()*1000, random()*1000, random()*1000, random()*1000,
  random()*1000, random()*1000, random()*1000, random()*1000
])
FROM generate_series(1, 1000000) id;
UPDATE vectors64 SET vector_gist = vector_lineal;
CREATE INDEX idx_vectors64 ON vectors64 USING gist(vector_gist);


-- D2 KNN using lineal scan
EXPLAIN ANALYZE
SELECT id, vector_lineal,
       cube_distance(vector_lineal, '(100, 200)') AS D
  FROM vectors2
 ORDER BY vector_lineal <-> '(100, 200)'
 LIMIT 3;

-- D2 KNN using the GiST index
EXPLAIN ANALYZE
SELECT id, vector_gist,
       cube_distance(vector_gist, '(100, 200)') AS D
  FROM vectors2
 ORDER BY vector_gist <-> '(100, 200)'
 LIMIT 3;

-- D4 KNN using lineal scan
EXPLAIN ANALYZE
SELECT id, vector_lineal,
       cube_distance(vector_lineal, '(100, 200, 300, 400)') AS D
  FROM vectors4
 ORDER BY vector_lineal <-> '(100, 200, 300, 400)'
 LIMIT 3;

-- D4 KNN using the GiST index
EXPLAIN ANALYZE
SELECT id, vector_gist,
       cube_distance(vector_gist, '(100, 200, 300, 400)') AS D
  FROM vectors4
 ORDER BY vector_gist <-> '(100, 200, 300, 400)'
 LIMIT 3;

-- D6 KNN using lineal scan
EXPLAIN ANALYZE
SELECT id, vector_lineal,
       cube_distance(vector_lineal, '(100, 200, 300, 400, 500, 600)') AS D
  FROM vectors6
 ORDER BY vector_lineal <-> '(100, 200, 300, 400, 500, 600)'
 LIMIT 3;

-- D6 KNN using the GiST index
EXPLAIN ANALYZE
SELECT id, vector_gist,
       cube_distance(vector_gist, '(100, 200, 300, 400, 500, 600)') AS D
  FROM vectors6
 ORDER BY vector_gist <-> '(100, 200, 300, 400, 500, 600)'
 LIMIT 3;

-- D8 KNN using lineal scan
EXPLAIN ANALYZE
SELECT id, vector_lineal,
       cube_distance(vector_lineal, '(100,200,300,400,500,600,700,800)') AS D
  FROM vectors8
 ORDER BY vector_lineal <-> '(100,200,300,400,500,600,700,800)'
 LIMIT 3;

-- D8 KNN using the GiST index
EXPLAIN ANALYZE
SELECT id, vector_gist,
       cube_distance(vector_gist, '(100,200,300,400,500,600,700,800)') AS D
  FROM vectors8
 ORDER BY vector_gist <-> '(100,200,300,400,500,600,700,800)'
 LIMIT 3;

-- D16 KNN using lineal scan
EXPLAIN ANALYZE
SELECT id, vector_lineal,
       cube_distance(vector_lineal, '(100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115)') AS D
  FROM vectors16
 ORDER BY vector_lineal <-> '(100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115)'
 LIMIT 3;

-- D16 KNN using the GiST index
EXPLAIN ANALYZE
SELECT id, vector_gist,
       cube_distance(vector_gist, '(100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115)') AS D
  FROM vectors16
 ORDER BY vector_gist <-> '(100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115)'
 LIMIT 3;

-- D32 KNN using lineal scan
EXPLAIN ANALYZE
SELECT id, vector_lineal,
       cube_distance(vector_lineal, '(
         1,2,3,4,5,6,7,8,9,10,
         11,12,13,14,15,16,17,18,19,20,
         21,22,23,24,25,26,27,28,29,30,31,32
       )') AS D
  FROM vectors32
 ORDER BY vector_lineal <-> '(
         1,2,3,4,5,6,7,8,9,10,
         11,12,13,14,15,16,17,18,19,20,
         21,22,23,24,25,26,27,28,29,30,31,32
       )'
 LIMIT 3;

-- D32 KNN using the GiST index
EXPLAIN ANALYZE
SELECT id, vector_gist,
       cube_distance(vector_gist, '(
         1,2,3,4,5,6,7,8,9,10,
         11,12,13,14,15,16,17,18,19,20,
         21,22,23,24,25,26,27,28,29,30,31,32
       )') AS D
  FROM vectors32
 ORDER BY vector_gist <-> '(
         1,2,3,4,5,6,7,8,9,10,
         11,12,13,14,15,16,17,18,19,20,
         21,22,23,24,25,26,27,28,29,30,31,32
       )'
 LIMIT 3;

-- D64 KNN using lineal scan
EXPLAIN ANALYZE
SELECT id, vector_lineal,
       cube_distance(vector_lineal, '(
         1,2,3,4,5,6,7,8,9,10,
         11,12,13,14,15,16,17,18,19,20,
         21,22,23,24,25,26,27,28,29,30,
         31,32,33,34,35,36,37,38,39,40,
         41,42,43,44,45,46,47,48,49,50,
         51,52,53,54,55,56,57,58,59,60,
         61,62,63,64
       )') AS D
  FROM vectors64
 ORDER BY vector_lineal <-> '(
         1,2,3,4,5,6,7,8,9,10,
         11,12,13,14,15,16,17,18,19,20,
         21,22,23,24,25,26,27,28,29,30,
         31,32,33,34,35,36,37,38,39,40,
         41,42,43,44,45,46,47,48,49,50,
         51,52,53,54,55,56,57,58,59,60,
         61,62,63,64
       )'
 LIMIT 3;

-- D64 KNN using the GiST index
EXPLAIN ANALYZE
SELECT id, vector_gist,
       cube_distance(vector_gist, '(
         1,2,3,4,5,6,7,8,9,10,
         11,12,13,14,15,16,17,18,19,20,
         21,22,23,24,25,26,27,28,29,30,
         31,32,33,34,35,36,37,38,39,40,
         41,42,43,44,45,46,47,48,49,50,
         51,52,53,54,55,56,57,58,59,60,
         61,62,63,64
       )') AS D
  FROM vectors64
 ORDER BY vector_gist <-> '(
         1,2,3,4,5,6,7,8,9,10,
         11,12,13,14,15,16,17,18,19,20,
         21,22,23,24,25,26,27,28,29,30,
         31,32,33,34,35,36,37,38,39,40,
         41,42,43,44,45,46,47,48,49,50,
         51,52,53,54,55,56,57,58,59,60,
         61,62,63,64
       )'
 LIMIT 3;

-- Usar antes de cada consulta
DISCARD PLANS;
DISCARD ALL;
VACUUM FULL vectors4;