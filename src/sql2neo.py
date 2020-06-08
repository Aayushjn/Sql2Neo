import argparse
import sys

from src.db import MySQL, Neo4j, Mongo

parser = argparse.ArgumentParser(description='A command-line tool to convert data between SQL, NoSQL and Neo4j '
                                             'databases')
parser.add_argument('--delete-all', help='delete all created resources (MySQL and Mongo) in Neo4j', dest='delete_all',
                    action='store_true')
subparsers = parser.add_subparsers()

convert_parser = subparsers.add_parser('convert')
convert_parser.add_argument('--src', help='source database', choices=['mysql', 'mongo'])
convert_parser.add_argument('--dest', help='destination database', choices=['neo4j'])
convert_parser.add_argument('--db', help='source database name', default=None)

args = parser.parse_args()

if args.delete_all:
    mysql = MySQL()
    mysql_rel = mysql.get_tables_and_relationships()
    # mongo = Mongo()
    # mongo_rel = mongo.extract_collection_details()
    neo4j = Neo4j()
    neo4j.destroy_all(mysql_rel)
    sys.exit(0)

if args.src == 'mysql':
    mysql = MySQL(args.db)
    mysql_rel = mysql.get_tables_and_relationships()
    records = mysql.extract_records(mysql_rel)
    neo4j = Neo4j()
    neo4j.create_indices_and_constraints(mysql_rel)
    neo4j.write_records_to_neo(records)
    neo4j.create_relationships(mysql_rel)
else:
    mongo = Mongo(args.db)
    records = mongo.extract_records()
    neo4j = Neo4j()
    neo4j.write_records_to_neo(records)
