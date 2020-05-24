from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

import os

MYSQL_CONFIG = {
    'user': os.getenv('MYSQL_DB_USER'),
    'password': os.getenv('MYSQL_DB_PASS'),
    'database': os.getenv('MYSQL_DB_NAME')
}
