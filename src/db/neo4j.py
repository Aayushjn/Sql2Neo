"""
Neo4j related DB calls
"""
import sys
from typing import List, Dict

from py2neo import Node
from py2neo.database import Graph
from urllib3.exceptions import MaxRetryError

from src.settings import NEO4J_HOST, NEO4J_PORT, NEO4J_USER, NEO4J_PASS, NEO4J_SCHEME, ERR_DB_CONN


class Neo4j:
    def __init__(self):
        self.graph = Graph(scheme=NEO4J_SCHEME, host=NEO4J_HOST, port=NEO4J_PORT, auth=(NEO4J_USER, NEO4J_PASS))

    def write_records_to_neo(self, records: Dict[str, List[Dict[str, object]]]):
        """
        Records from a MySQL or Mongo database are stored as a graph in Neo4j
        :param records: dictionary of entries as provided by :py:meth:`src.db.MySQL.extract_records or
        :py:meth:`src.db.Mongo.extract_records`
        """
        try:
            tx = self.graph.begin()
            for table in records:
                print(f'Creating nodes for {table}')
                for record in records[table]:
                    node = Node(table, **record)
                    tx.create(node)
                print(f'{len(records[table])} nodes created')
            tx.commit()
        except MaxRetryError:
            print(f'Check whether Neo4j is running on {NEO4J_SCHEME}://{NEO4J_HOST}:{NEO4J_PORT}/')
            sys.exit(ERR_DB_CONN)
        except RuntimeError:
            print('Verify Neo4j credentials')
            sys.exit(1)
