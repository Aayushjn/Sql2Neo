"""
Neo4j related DB calls
"""
from typing import List, Dict

from py2neo.database import Graph

from src.settings import NEO4J_HOST, NEO4J_PORT, NEO4J_USER, NEO4J_PASS, NEO4J_SCHEME


class Neo4j:
    def __init__(self):
        self.graph = Graph(scheme=NEO4J_SCHEME, host=NEO4J_HOST, port=NEO4J_PORT, auth=(NEO4J_USER, NEO4J_PASS))

    def write_sql_to_neo(self, table: Dict[str, List[str]]):
        pass

    def write_nosql_to_neo(self, collection: Dict[str, Dict]):
        pass
