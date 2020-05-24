from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

import os

MYSQL_CONFIG = {
    'user': os.getenv('MYSQL_DB_USER'),
    'password': os.getenv('MYSQL_DB_PASS'),
    'database': os.getenv('MYSQL_DB_NAME')
}

MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
MONGO_PORT = os.getenv('MONGO_PORT', 27017)
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME')
