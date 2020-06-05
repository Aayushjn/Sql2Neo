from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

import os

LOG_CONFIG = {
    'version': 1,
    'formatters': {
        'default': {
            'format': '%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'default',
            'stream': 'ext://sys.stdout'
        },
    },
    'loggers': {
        'main': {
            'level': 'INFO',
            'handlers': ['console'],
            'propagate': False
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console']
    }
}

MYSQL_CONFIG = {
    'user': os.getenv('MYSQL_DB_USER'),
    'password': os.getenv('MYSQL_DB_PASS'),
    'database': os.getenv('MYSQL_DB_NAME')
}

MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
MONGO_PORT = os.getenv('MONGO_PORT', 27017)
MONGO_USER = os.getenv('MONGO_USER', None)
MONGO_PASS = os.getenv('MONGO_PASS', None)
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME')

NEO4J_HOST = os.getenv('NEO4J_HOST', 'localhost')
NEO4J_PORT = os.getenv('NEO4J_PORT', 7474)
NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
NEO4J_PASS = os.getenv('NEO4J_PASS', 'neo4j')
NEO4J_SCHEME = os.getenv('NEO4J_SCHEME', 'http')

# Constant definitions
ERR_DB_CONN = 100
