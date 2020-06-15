import argparse
import logging
import sys
from pprint import pprint

from src.db import MySQL, Neo4j, Mongo, QueryTranslator

parser = argparse.ArgumentParser(description='A command-line tool to convert data between SQL, NoSQL and Neo4j '
                                             'databases')
parser.add_argument('--delete-all', help='delete all created resources (MySQL and Mongo) in Neo4j', action='store_true')
parser.add_argument('--test', help='flag for testing local commands', action='store_true')
parser.add_argument('-v', help='verbose mode; prints extra information', action='store_true')
subparsers = parser.add_subparsers(dest='subparser_name')

convert_parser = subparsers.add_parser('convert')
convert_parser.add_argument('--src', help='source database', choices=['mysql', 'mongo'])
convert_parser.add_argument('--db', help='source database name', default=None)

query_parser = subparsers.add_parser('query')
query_parser.add_argument('-q', help='query to run')
query_parser.add_argument('-f', '--file', help='input file holding queries to run')
query_parser.add_argument('--run', help='execute equivalent CQL query on Neo4j', action='store_true')
query_parser.add_argument('--dry-run', help='shows equivalent CQL query', action='store_true')

args = parser.parse_args()

if args.subparser_name is None:
    if args.test:
        mysql = MySQL()
        pprint(mysql.get_tables_and_relationships())
        sys.exit(0)

    if args.delete_all:
        mysql = MySQL(args.v)
        mysql_rel = mysql.get_tables_and_relationships()
        mongo = Mongo(args.v)
        mongo_rel = mongo.extract_collection_details()
        neo4j = Neo4j(args.v)
        neo4j.destroy_all(mysql_rel)
        neo4j.destroy_all(mongo_rel)
        sys.exit(0)
elif args.subparser_name == 'query':
    logging.warning('Provided queries are not validated. Ensure that valid queries have been provided.')
    logging.warning('There may be discrepancies if table or attribute names collide with SQL keywords')
    logging.warning('Only queries beginning with "SELECT" are translated')
    if args.q is None and args.file is None:
        logging.error('Either query or file must be passed')
        sys.exit(1)
    dry_run = True
    if not args.run and not args.dry_run:
        logging.warning('Defaulting to dry run...')
    elif args.run:
        dry_run = False

    if args.q is not None:
        translator = QueryTranslator(args.q, None)
    else:
        translator = QueryTranslator(None, args.file)
    converted = translator.convert()

    if dry_run:
        for cql in converted:
            logging.info(f'Converted query: {cql}')
    else:
        neo4j = Neo4j(args.v)
        for cql in converted:
            neo4j.run_query(cql)


elif args.subparser_name == 'convert':
    if args.src == 'mysql':
        mysql = MySQL(args.dbargs.v)
        mysql_rel = mysql.get_tables_and_relationships()
        records = mysql.extract_records(mysql_rel)
        neo4j = Neo4j(args.v)
        neo4j.create_indices_and_constraints(mysql_rel)
        neo4j.write_records_to_neo(records)
        neo4j.create_relationships(mysql_rel)
        sys.exit(0)
    else:
        mongo = Mongo(args.dbargs.v)
        mongo_rel = mongo.extract_collection_details()
        records = mongo.extract_records(mongo_rel)
        neo4j = Neo4j(args.v)
        neo4j.create_indices_and_constraints(mongo_rel)
        neo4j.write_records_to_neo(records)
        neo4j.create_relationships(mongo_rel)
        sys.exit(0)
