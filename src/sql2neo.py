import argparse
from pprint import pprint

from src.db import MySQL

parser = argparse.ArgumentParser(description='A command-line tool to convert data between SQL, NoSQL and Neo4j '
                                             'databases')

# Add arguments

args = parser.parse_args()

mysql = MySQL()
pprint(mysql.extract_records_by_table())
mysql.close()
