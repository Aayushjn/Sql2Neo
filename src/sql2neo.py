import argparse
from pprint import pprint

from src.db import MySQL

parser = argparse.ArgumentParser(description='A command-line tool to convert data between SQL, NoSQL and Neo4j '
                                             'databases')

# Add arguments

args = parser.parse_args()

sql = MySQL()
pprint(sql.extract_table_details())
sql.close()
