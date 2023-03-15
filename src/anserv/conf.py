import os

SQLALCHEMY_DATABASE_URL = os.getenv('SQLALCHEMY_DATABASE_URL', 'postgresql+asyncpg://nik:qwe123@localhost/anserv')
TEST_SQLALCHEMY_DATABASE_URL = 'postgresql+psycopg2://nik:qwe123@localhost/anserv_test'


AUTH_SECRET_KEY = os.getenv('AUTH_SECRET_KEY', '09d25e094faa6ca2556c818166b7c1563b93f7099f6f0f4caa6cf63b88e8d3e7')
AUTH_ALGORITHM = 'HS256'
AUTH_TOKEN_EXPIRE_MINUTES = 12 * 60

BASE_URL = os.getenv('BASE_URL', 'http://localhost:8000')
