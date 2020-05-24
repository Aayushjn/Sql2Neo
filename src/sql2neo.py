import argparse
from pprint import pprint

from src.db import Mongo

parser = argparse.ArgumentParser(description='A command-line tool to convert data between SQL, NoSQL and Neo4j '
                                             'databases')

# Add arguments

args = parser.parse_args()

mongo = Mongo()
pprint(mongo.extract_collection_details())
mongo.close()
