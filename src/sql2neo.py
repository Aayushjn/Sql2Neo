import argparse

from src.db import Neo4j

parser = argparse.ArgumentParser(description='A command-line tool to convert data between SQL, NoSQL and Neo4j '
                                             'databases')

# Add arguments

args = parser.parse_args()

# mysql = MySQL()
# pprint(mysql.extract_records())
# records = mysql.extract_records()
# mysql.close()
neo4j = Neo4j()
neo4j.read_all()
# neo4j.write_records_to_neo(records)
