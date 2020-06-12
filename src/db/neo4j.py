"""
Neo4j related DB calls
"""
import calendar
import datetime
import logging
import sys
from typing import List, Dict

from neobolt.exceptions import ServiceUnavailable
from py2neo import Node
from py2neo.database import Graph, DatabaseError, ClientError
from urllib3.exceptions import MaxRetryError

from src.config import NEO4J_HOST, NEO4J_PORT, NEO4J_USER, NEO4J_PASS, NEO4J_SCHEME, ERR_DB_CONN
from src.models import AttributeData

SUPPORTED_TYPES = [int, float, str]
CONVERTED_TYPES = [datetime.date, datetime.datetime, datetime.time, datetime.timedelta, type(None)]


def get_compatible_record(record: Dict[str, object]) -> Dict[str, object]:
    """
    Convert existing record to Neo4j compatible data types
    Neo4j supports only `SUPPORTED_TYPES`
    All datetime types and NoneType are converted to Neo4j compatible strings

    :param record: single record of the table
    :return: record with Neo4j compatible data types
    """
    modified_record = record
    for attr in record:
        t = type(record[attr])
        if t not in SUPPORTED_TYPES and t not in CONVERTED_TYPES:
            logging.warning(f'{t} is not supported in Neo4j. Converting to string')
            modified_record[attr] = str(modified_record[attr])
        if t in CONVERTED_TYPES:
            if t == datetime.time or t == datetime.timedelta:
                modified_record[attr] = str(record[attr])
            elif t == datetime.datetime or t == datetime.date:
                # convert to UTC UNIX timestamp
                modified_record[attr] = calendar.timegm(record[attr].timetuple())
            else:
                # NoneType
                modified_record[attr] = ''

    return modified_record


class Neo4j:
    """
    A wrapper around Neo4j Graph connection
    """
    def __init__(self):
        self.graph = Graph(scheme=NEO4J_SCHEME, host=NEO4J_HOST, port=NEO4J_PORT, auth=(NEO4J_USER, NEO4J_PASS))
        try:
            # run a test query to verify connection
            self.graph.run('RETURN 1')
        except MaxRetryError:
            logging.error(f'Check whether Neo4j is running on {NEO4J_SCHEME}://{NEO4J_HOST}:{NEO4J_PORT}/')
            sys.exit(ERR_DB_CONN)
        except ServiceUnavailable:
            logging.error(f'Service unavailable on {NEO4J_SCHEME}://{NEO4J_HOST}:{NEO4J_PORT}/')
            sys.exit(ERR_DB_CONN)
        except AssertionError:
            logging.error('Verify Neo4j credentials', exc_info=True)
            sys.exit(ERR_DB_CONN)
        except RuntimeError:
            logging.error('Verify Neo4j credentials', exc_info=True)
            sys.exit(ERR_DB_CONN)

    def create_indices_and_constraints(self, relations: Dict[str, Dict[str, AttributeData]]):
        """
        Create indices and constraints on all "tables"
        Indices are currently built on PK attributes only

        :param relations: dictionary of relations as provided by `MySQL.get_tables_and_relationships()`
        """
        for table in relations:
            for attr in relations[table]:
                if relations[table][attr].index:
                    try:
                        self.graph.run(f'CREATE INDEX ON:{table}({attr})')
                        logging.info(f'Index created on {attr} for {table}')
                    except ClientError as err:
                        # if index on `attr` already exists, `ClientError` is raised
                        logging.warning(err.message)
                if relations[table][attr].unique and not relations[table][attr].index:
                    try:
                        self.graph.run(f'CREATE CONSTRAINT constraint_{table}_{attr} ON (a:{table}) ASSERT a.{attr} IS '
                                       f'UNIQUE')
                        logging.info(f'Uniqueness constraint created on {attr} for {table}')
                    except ClientError as err:
                        # if constraint on `attr` already exists, `ClientError` is raised
                        logging.warning(err.message)

    def write_records_to_neo(self, records: Dict[str, List[Dict[str, object]]]):
        """
        Records from a MySQL or Mongo database are stored as a graph in Neo4j

        :param records: dictionary of entries as provided by :py:meth:`src.db.MySQL.extract_records or
        :py:meth:`src.db.Mongo.extract_records`
        """
        for table in records:
            try:
                for record in records[table]:
                    tx = self.graph.begin()
                    # if record does not have name attribute, set it with table name
                    # this is useful during visualization, since the node has a name label
                    record['name'] = record.get('name', table)
                    node = Node(table, **get_compatible_record(record))
                    tx.create(node)
                    tx.commit()
                logging.info(f'{len(records[table])} nodes created for {table}')
            except ClientError as err:
                # if node already exists (and the node has constraint on a property), `ClientError` is raised
                logging.warning(err.message)

    def create_relationships(self, relations: Dict[str, Dict[str, AttributeData]]):
        """
        Create relationships between all nodes (performed after `write_records_to_neo`
        Only FK relations are translated to relationships

        :param relations: dictionary of relations as provided by `MySQL.get_tables_and_relationships()`
        """
        # match all nodes 'a' of table to all nodes 'b' of referenced_table
        # where 'a.attribute' == 'b.referenced_attribute'
        # create relationship named 'table_FK_referenced_table' from a to b
        query = 'MATCH (a:{}), (b:{}) WHERE a.{} = b.{} CREATE (a) -[r:{}_FK_{}]->(b)'
        for table in relations:
            for attr in relations[table]:
                if (rel := relations[table][attr].foreign_key) is not None:
                    fk_table, fk_attr = rel.split('.')
                    self.graph.run(query.format(table, fk_table, attr, fk_attr, table, fk_table))
                    logging.info(f'Relationship {table}_FK_{fk_table} created')

    def destroy_all(self, relations: Dict[str, Dict[str, AttributeData]]):
        """
        Destroy all indices, constraints, nodes and relationships from the source database

        :param relations: dictionary of relations as provided by `MySQL.get_tables_and_relationships()`
        """
        for table in relations:
            self.graph.run(f'MATCH (n:{table}) DETACH DELETE n')
            logging.info(f'All nodes and relationships of {table} deleted')
            for attr in relations[table]:
                if relations[table][attr].index:
                    try:
                        self.graph.run(f'DROP INDEX ON:{table}({attr})')
                        logging.info(f'Index on {table}.{attr} dropped')
                    except DatabaseError as err:
                        # may occur if the index doesn't exist
                        logging.warning(err.message)
                if relations[table][attr].unique and not relations[table][attr].index:
                    try:
                        self.graph.run(f'DROP CONSTRAINT ON (n:{table}) ASSERT n.{attr} IS UNIQUE')
                        logging.info(f'Uniqueness constraint on {table}.{attr} dropped')
                    except DatabaseError as err:
                        # may occur if the constraint doesn't exist
                        logging.warning(err.message)

    def run_query(self, cql: str):
        """
        Run a cypher query on the converted data

        :param cql: query to run
        """
        logging.info(f'Executing {cql}')
        cursor = self.graph.run(cql)
        for res in cursor:
            print(res)
        cursor.close()
