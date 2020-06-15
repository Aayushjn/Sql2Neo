from unittest import TestCase

from src.db import MySQL, Neo4j

global mysql
global neo4j


def setup_module(module):
    """
    Create all nodes and setup Neo4j for testing
    """
    global mysql
    global neo4j
    mysql = MySQL('hosp', False)
    mysql_rel = mysql.get_tables_and_relationships()
    records = mysql.extract_records(mysql_rel)
    neo4j = Neo4j(False)
    neo4j.create_indices_and_constraints(mysql_rel)
    neo4j.write_records_to_neo(records)
    neo4j.create_relationships(mysql_rel)


def teardown_module(module):
    """
    Delete all data after testing
    """
    global mysql
    global neo4j
    mysql_rel = mysql.get_tables_and_relationships()
    neo4j.destroy_all(mysql_rel)


class MigrationTest(TestCase):
    def test_sql_to_neo_index_count(self):
        global mysql
        global neo4j
        mysql_rel = mysql.get_tables_and_relationships()

        index_count = 0
        for table in mysql_rel:
            for attr in mysql_rel[table]:
                if mysql_rel[table][attr].index:
                    index_count += 1

        self.assertEqual(index_count, neo4j.get_index_count())

    def test_sql_to_neo_record_count(self):
        global mysql
        global neo4j
        mysql_rel = mysql.get_tables_and_relationships()
        records = mysql.extract_records(mysql_rel)

        record_count = 0
        for table in records:
            record_count += len(records[table])

        self.assertEqual(record_count, neo4j.get_node_count())
