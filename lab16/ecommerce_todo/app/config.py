import redis

class Config:   
    # PostgreSQL config
    POSTGRES_USER = 'postgres'
    POSTGRES_PASSWORD = 'password'
    POSTGRES_HOST = 'localhost'
    POSTGRES_PORT = '5432'
    POSTGRES_DB = 'ecommerce'
    
    SQLALCHEMY_DATABASE_URI = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    redis_client = redis.Redis(
    host='redis-master',  # si usas Docker y están en la misma red
    port=6379,
    decode_responses=True
)