"""
Neo4j related DB calls
"""
import logging
import sys
from typing import List, Dict

from neobolt.exceptions import ServiceUnavailable
from py2neo import Node
from py2neo.database import Graph
from urllib3.exceptions import MaxRetryError

from src.config import NEO4J_HOST, NEO4J_PORT, NEO4J_USER, NEO4J_PASS, NEO4J_SCHEME, ERR_DB_CONN
from src.models import AttributeData


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
                    self.graph.run(f'CREATE INDEX ON:{table}({attr})')
                    logging.info(f'Index created on {attr} for {table}')
                if relations[table][attr].unique and not relations[table][attr].index:
                    self.graph.run(f'CREATE CONSTRAINT constraint_{table}_{attr} ON (a:{table}) ASSERT a.{attr} IS '
                                   f'UNIQUE')
                    logging.info(f'Uniqueness constraint created on {attr} for {table}')

    def write_records_to_neo(self, records: Dict[str, List[Dict[str, object]]]):
        """
        Records from a MySQL or Mongo database are stored as a graph in Neo4j

        :param records: dictionary of entries as provided by :py:meth:`src.db.MySQL.extract_records or
        :py:meth:`src.db.Mongo.extract_records`
        """
        for table in records:
            tx = self.graph.begin()
            for record in records[table]:
                node = Node(table, **record)
                tx.create(node)
            tx.commit()
            logging.info(f'{len(records[table])} nodes created')

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
                    query.format()
                    self.graph.run(query.format(table, fk_table, attr, fk_attr, table, fk_table))
                    logging.info(f'Relationship {table}_FK_{fk_table} created')
