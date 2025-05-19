--p1

-- crear tabla
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE TABLE articles (
	content_lineal text,
	content_gin text
)

-- Inserta 10^7 registros aleatorios
INSERT INTO articles (content_lineal)
SELECT md5(random()::text)
FROM generate_series(1, 10000000) AS id;

-- Copia a la columna indexada
UPDATE articles SET content_gin = content_lineal;

-- crear indice gin con trigramas
CREATE INDEX idx_articles_trgm_gin ON articles
USING GIN (content_gin gin_trgm_ops);

-- crear subconjuntos
CREATE TABLE articles_1k AS SELECT * FROM articles LIMIT 1000;
CREATE TABLE articles_10k AS SELECT * FROM articles LIMIT 10000;
CREATE TABLE articles_100k AS SELECT * FROM articles LIMIT 100000;
CREATE TABLE articles_1m AS SELECT * FROM articles LIMIT 1000000;

-- crear indices
CREATE INDEX idx_trgm_gin_1k ON articles_1k USING GIN (content_gin gin_trgm_ops);
CREATE INDEX idx_trgm_gin_10k ON articles_10k USING GIN (content_gin gin_trgm_ops);
CREATE INDEX idx_trgm_gin_100k ON articles_100k USING GIN (content_gin gin_trgm_ops);
CREATE INDEX idx_trgm_gin_1m ON articles_1m USING GIN (content_gin gin_trgm_ops);

-- consultas
EXPLAIN ANALYZE
SELECT COUNT(*) FROM articles_10k
WHERE content_lineal ILIKE '%abc%';

EXPLAIN ANALYZE
SELECT COUNT(*) FROM articles_10k
WHERE content_gin ILIKE '%abc%';


-- p2

-- crear nuevas columnas e indice gin
ALTER TABLE film ADD COLUMN vector_lineal tsvector;
ALTER TABLE film ADD COLUMN vector_gin tsvector;

UPDATE film SET vector_lineal = to_tsvector('english', title || description);
UPDATE film SET vector_gin = vector_lineal;

CREATE INDEX idx_film_vector ON film USING GIN(vector_gin); --usa keywords

-- consultas
EXPLAIN ANALYZE
SELECT title, description, vector_gin FROM film WHERE vector_gin @@ to_tsquery('english', 'Man & Woman')

EXPLAIN ANALYZE
SELECT title, description, vector_lineal FROM film WHERE vector_lineal @@ to_tsquery('english', 'Man & Woman')

-- duplicar registros
INSERT INTO film (title, description, language_id, vector_lineal, vector_gin) SELECT title, description, language_id, vector_lineal, vector_gin FROM film

-- consulta con rankeo
SELECT title, description, ts_rank_cd(vector_gin, to_tsquery('english', 'Man & Woman')) as simil FROM film order by simil desc limit 10;


-- p3

-- crear tabla e importar csv
CREATE TABLE articles(
	num INT PRIMARY KEY,
	id INT,
	title TEXT,
	publication TEXT,
	author TEXT,
	date DATE,
	year FLOAT,
	month FLOAT,
	url TEXT,
	content TEXT
)

-- crear nueva columna
ALTER TABLE articles ADD COLUMN full_text_idx tsvector;

UPDATE articles
SET full_text_idx = to_tsvector('english', coalesce(title, '') || ' ' || coalesce(content, ''));

-- crear indice gin
CREATE INDEX gin_articles_idx ON articles USING GIN (full_text_idx);

-- consultas
EXPLAIN ANALYZE
SELECT * FROM articles
WHERE to_tsvector('english', title || ' ' || content) @@ plainto_tsquery('english', 'trump');

SELECT * FROM articles
WHERE full_text_idx @@ plainto_tsquery('english', 'trump');

-- crear subconjuntos
CREATE TABLE articles_1k AS SELECT * FROM articles ORDER BY random() LIMIT 1000;
CREATE TABLE articles_10k AS SELECT * FROM articles ORDER BY random() LIMIT 10000;
CREATE TABLE articles_25k AS SELECT * FROM articles ORDER BY random() LIMIT 25000;
CREATE TABLE articles_50k AS SELECT * FROM articles ORDER BY random() LIMIT 50000;

-- consultas
SELECT *, ts_rank(to_tsvector('english', title || ' ' || content), plainto_tsquery('english', 'climate change')) AS rank
FROM articles_50k
WHERE to_tsvector('english', title || ' ' || content) @@ plainto_tsquery('english', 'climate change')
ORDER BY rank DESC
LIMIT 10;

SELECT *, ts_rank(full_text_idx, plainto_tsquery('english', 'climate change')) AS rank
FROM articles_50k
WHERE full_text_idx @@ plainto_tsquery('english', 'climate change')
ORDER BY rank DESC
LIMIT 10;


-- p4

-- crear tablas identicas

CREATE TABLE articles_gin(
	num INT PRIMARY KEY,
	id INT,
	title TEXT,
	publication TEXT,
	author TEXT,
	date DATE,
	year FLOAT,
	month FLOAT,
	url TEXT,
	content TEXT
);

CREATE TABLE articles_gist(
	num INT PRIMARY KEY,
	id INT,
	title TEXT,
	publication TEXT,
	author TEXT,
	date DATE,
	year FLOAT,
	month FLOAT,
	url TEXT,
	content TEXT
);

-- crear nuevas columnas
ALTER TABLE articles_gin ADD COLUMN full_text_idx tsvector;
ALTER TABLE articles_gist ADD COLUMN full_text_idx tsvector;

UPDATE articles_gin
SET full_text_idx = to_tsvector('english', coalesce(title, '') || ' ' || coalesce(content, ''));

INSERT INTO articles_gist SELECT * FROM articles_gin;

-- crear indices
CREATE INDEX gin_articles_idx ON articles_gin USING GIN (full_text_idx);
CREATE INDEX gist_articles_idx ON articles_gist USING GIST (full_text_idx);

-- insercion
INSERT INTO articles_gin
SELECT 100000, id, title, publication, author, date, year, month, url, content, full_text_idx
FROM articles_gin
WHERE num = 1;

INSERT INTO articles_gist
SELECT 100000, id, title, publication, author, date, year, month, url, content, full_text_idx
FROM articles_gist
WHERE num = 1;

-- busqueda
EXPLAIN ANALYZE
SELECT * FROM articles_gin
WHERE full_text_idx @@ plainto_tsquery('english', 'trump');

EXPLAIN ANALYZE
SELECT * FROM articles_gist
WHERE full_text_idx @@ plainto_tsquery('english', 'trump');

-- tamaño en disco
SELECT pg_size_pretty (pg_relation_size('gin_articles_idx')) AS gin,
pg_size_pretty(pg_relation_size('gist_articles_idx')) AS gist;


