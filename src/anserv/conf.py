import os

BASE_URL = os.getenv('BASE_URL', 'http://localhost:8000')


POSTGRES_USER = os.getenv('POSTGRES_USER', 'anserv')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'password')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'anserv')

SQLALCHEMY_URL = f'postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}'
TEST_SQLALCHEMY_URL = f'postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}'

# For tests run we use NullPool to avoid async related problems
SQLALCHEMY_USE_NULLPOOL = os.getenv('SQLALCHEMY_USE_NULLPOOL', '').lower() in ['true', '1']

AUTH_SECRET_KEY = os.getenv('AUTH_SECRET_KEY', 'b06a6d47bac342f9887c7c6594468a57d02e3de26aeb4549a4aa3090c7c81002')
AUTH_ALGORITHM = 'HS256'
AUTH_TOKEN_EXPIRE_MINUTES = 12 * 60
