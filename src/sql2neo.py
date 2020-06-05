import argparse
import logging

from src.db import MySQL, Neo4j

parser = argparse.ArgumentParser(description='A command-line tool to convert data between SQL, NoSQL and Neo4j '
                                             'databases')
subparsers = parser.add_subparsers()

convert_parser = subparsers.add_parser('convert')
convert_parser.add_argument('--src', help='source database', choices=['mysql', 'mongo'])
convert_parser.add_argument('--dest', help='destination database', choices=['neo4j'])

args = parser.parse_args()

if args.src == 'mysql':
    mysql = MySQL()
    relations = mysql.get_tables_and_relationships()
    records = mysql.extract_records(relations)
    neo4j = Neo4j()
    neo4j.create_indices_and_constraints(relations)
    neo4j.write_records_to_neo(records)
    neo4j.create_relationships(relations)
else:
    logging.info('MongoDB currently unsupported')

