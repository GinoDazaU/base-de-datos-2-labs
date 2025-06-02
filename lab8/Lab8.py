import os
import math
import face_recognition
import psycopg2
import time
from psycopg2.extras import execute_values

from dotenv import load_dotenv

load_dotenv()

dbname = os.getenv("DBNAME")
dbuser = os.getenv("DBUSER")
dbpass = os.getenv("DBPASS")
dbhost = os.getenv("DBHOST")

def connect_db():
    conn = psycopg2.connect(
        dbname=dbname,
        user=dbuser,
        password=dbpass,
        host=dbhost,
        port=5432
    )
    return conn

def distance_to_center(location : list[tuple], center_x : int, center_y : int) -> float:
    top, right, bottom, left = location

    if left <= center_x <= right:
        dx = 0
    elif center_x < left:
        dx = left - center_x
    else:
        dx = center_x - right
    
    if top <= center_y <= bottom:
        dy = 0
    elif center_y < top:
        dy = top - center_y
    else:
        dy = center_y - bottom
    
    return math.sqrt(dx*dx + dy*dy)

def generate_face_embeddings(dir, N = -1):
    num = 0
    res = []

    if N == -1:
        N = 0
        for root, dirs, files in os.walk(dir):
            for file in files:
                if file.lower().endswith('.jpg'):
                    N += 1

    print(f"{num} out of {N} images ({round(num/N*100, 2)}%)")
    for root, dirs, files in os.walk(dir):
        if num >= N:
            break
        for file in files:
            if file.lower().endswith('.jpg'):
                if num >= N:
                    break
                
                image_path = os.path.join(root, file)
                image = face_recognition.load_image_file(image_path)
                faces_locations = face_recognition.face_locations(image)
                if len(faces_locations) == 0:
                    continue
                if len(faces_locations) == 1:
                    face_location = faces_locations[0]                    
                if len(faces_locations) > 1:
                    min_dist = -1
                    for i in faces_locations:
                        dist = distance_to_center(i, image.shape[0] // 2, image.shape[1] // 2)
                        if min_dist == -1 or dist < min_dist:
                            min_dist = dist
                            face_location = i
                face_encoding = face_recognition.face_encodings(image, [face_location])[0]
                res.append((file, f"({str(face_encoding.tolist())[1:-1]})"))

                num += 1

                if(num % 100 == 0):
                    print(f"{num} out of {N} images ({round(num/N*100, 2)}%)")
    
    conn = connect_db()
    cur = conn.cursor()
    query = "INSERT INTO face_encodings (filename, encoding) VALUES %s"
    execute_values(cur, query, res)
    conn.commit()
    cur.close()
    conn.close()

def generate_face_embeddings_pgvector(dir, N = -1):
    num = 0
    res = []

    if N == -1:
        N = 0
        for root, dirs, files in os.walk(dir):
            for file in files:
                if file.lower().endswith('.jpg'):
                    N += 1

    print(f"{num} out of {N} images ({round(num/N*100, 2)}%)")
    for root, dirs, files in os.walk(dir):
        if num >= N:
            break
        for file in files:
            if file.lower().endswith('.jpg'):
                if num >= N:
                    break
                
                image_path = os.path.join(root, file)
                image = face_recognition.load_image_file(image_path)
                faces_locations = face_recognition.face_locations(image)
                if len(faces_locations) == 0:
                    continue
                if len(faces_locations) == 1:
                    face_location = faces_locations[0]                    
                if len(faces_locations) > 1:
                    min_dist = -1
                    for i in faces_locations:
                        dist = distance_to_center(i, image.shape[0] // 2, image.shape[1] // 2)
                        if min_dist == -1 or dist < min_dist:
                            min_dist = dist
                            face_location = i
                face_encoding = face_recognition.face_encodings(image, [face_location])[0]
                res.append((file, str(face_encoding.tolist())))

                num += 1

                if(num % 100 == 0):
                    print(f"{num} out of {N} images ({round(num/N*100, 2)}%)")
    
    conn = connect_db()
    cur = conn.cursor()
    query = "INSERT INTO face_encodings (filename, encoding_vector) VALUES %s"
    execute_values(cur, query, res)
    conn.commit()
    cur.close()
    conn.close()

# Para poblar la base de datos (solo correr una vez)

# Poblar la base de datos con cube
# generate_face_embeddings('lfw_funneled')

# Poblar la base de datos con pgvector
# generate_face_embeddings_pgvector('lfw_funneled')

def knn_lineal(image_path, k):
    image = face_recognition.load_image_file(image_path)
    faces_locations = face_recognition.face_locations(image)
    if len(faces_locations) == 0:
        return
    if len(faces_locations) == 1:
        face_location = faces_locations[0]                    
    if len(faces_locations) > 1:
        min_dist = -1
        for i in faces_locations:
            dist = distance_to_center(i, image.shape[0] // 2, image.shape[1] // 2)
            if min_dist == -1 or dist < min_dist:
                min_dist = dist
                face_location = i
    face_encoding = face_recognition.face_encodings(image, [face_location])[0]
    
    conn = connect_db()
    cur = conn.cursor()

    start = time.time()
    query = "SELECT filename, cube_distance(encoding, %s) as D FROM face_encodings ORDER BY encoding <-> %s LIMIT %s"
    vector = f"({str(face_encoding.tolist())[1:-1]})"
    cur.execute(query, (vector, vector, k))
    data = cur.fetchall()
    end = time.time()

    print(f"Execution time: {round(end - start, 4)} seconds")

    cur.close()
    conn.close()

    return data

def knn_gist(image_path, k):
    image = face_recognition.load_image_file(image_path)
    faces_locations = face_recognition.face_locations(image)
    if len(faces_locations) == 0:
        return
    if len(faces_locations) == 1:
        face_location = faces_locations[0]                    
    if len(faces_locations) > 1:
        min_dist = -1
        for i in faces_locations:
            dist = distance_to_center(i, image.shape[0] // 2, image.shape[1] // 2)
            if min_dist == -1 or dist < min_dist:
                min_dist = dist
                face_location = i
    face_encoding = face_recognition.face_encodings(image, [face_location])[0]
    
    conn = connect_db()
    cur = conn.cursor()

    start = time.time()
    query = "SELECT filename, cube_distance(encoding_gist, %s) as D FROM face_encodings ORDER BY encoding_gist <-> %s LIMIT %s"
    vector = f"({str(face_encoding.tolist())[1:-1]})"
    cur.execute(query, (vector, vector, k))
    data = cur.fetchall()
    end = time.time()

    print(f"Execution time: {round(end - start, 4)} seconds")

    cur.close()
    conn.close()

    return data    

def knn_pgvector_eucl(image_path, k):
    image = face_recognition.load_image_file(image_path)
    faces_locations = face_recognition.face_locations(image)
    if len(faces_locations) == 0:
        return
    if len(faces_locations) == 1:
        face_location = faces_locations[0]                    
    if len(faces_locations) > 1:
        min_dist = -1
        for i in faces_locations:
            dist = distance_to_center(i, image.shape[0] // 2, image.shape[1] // 2)
            if min_dist == -1 or dist < min_dist:
                min_dist = dist
                face_location = i
    face_encoding = face_recognition.face_encodings(image, [face_location])[0]
    
    conn = connect_db()
    cur = conn.cursor()

    start = time.time()
    query = "SELECT filename, encoding_vector <-> %s AS distance FROM face_encodings ORDER BY encoding_vector <-> %s LIMIT %s"
    vector = str(face_encoding.tolist())
    cur.execute(query, (vector, vector, k))
    data = cur.fetchall()
    end = time.time()

    print(f"Execution time: {round(end - start, 4)} seconds")

    cur.close()
    conn.close()

    return data

def knn_pgvector_cos(image_path, k):
    image = face_recognition.load_image_file(image_path)
    faces_locations = face_recognition.face_locations(image)
    if len(faces_locations) == 0:
        return
    if len(faces_locations) == 1:
        face_location = faces_locations[0]                    
    if len(faces_locations) > 1:
        min_dist = -1
        for i in faces_locations:
            dist = distance_to_center(i, image.shape[0] // 2, image.shape[1] // 2)
            if min_dist == -1 or dist < min_dist:
                min_dist = dist
                face_location = i
    face_encoding = face_recognition.face_encodings(image, [face_location])[0]
    
    conn = connect_db()
    cur = conn.cursor()

    start = time.time()
    query = "SELECT filename, encoding_vector <=> %s AS distance FROM face_encodings ORDER BY encoding_vector <=> %s LIMIT %s"
    vector = str(face_encoding.tolist())
    cur.execute(query, (vector, vector, k))
    data = cur.fetchall()
    end = time.time()

    print(f"Execution time: {round(end - start, 4)} seconds")

    cur.close()
    conn.close()

    return data

# Para hacer la busqueda knn

# print(knn_lineal('test_images/test1.jpg', 5))
