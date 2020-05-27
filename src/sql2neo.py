import argparse

from src.db import MySQL, Neo4j

parser = argparse.ArgumentParser(description='A command-line tool to convert data between SQL, NoSQL and Neo4j '
                                             'databases')

# Add arguments

args = parser.parse_args()

mysql = MySQL()
records = mysql.extract_records()
mysql.close()
neo4j = Neo4j()
neo4j.write_records_to_neo(records)
