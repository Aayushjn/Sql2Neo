"""
Neo4j related DB calls
"""
from typing import List, Dict

from py2neo.database import Graph

from src.settings import NEO4J_HOST, NEO4J_PORT, NEO4J_USER, NEO4J_PASS, NEO4J_SCHEME


class Neo4j:
    def __init__(self):
        self.graph = Graph(scheme=NEO4J_SCHEME, host=NEO4J_HOST, port=NEO4J_PORT, auth=(NEO4J_USER, NEO4J_PASS))

    def write_records_to_neo(self, records: Dict[str, List[Dict[str, object]]]):
        """
        Records from a MySQL or Mongo database are stored as a graph in Neo4j
        :param records: dictionary of entries as provided by :py:meth:`src.db.MySQL.extract_records_by_table or
        :py:meth:`src.db.Mongo.extract_collections`
        """
        pass
