from unittest import TestCase

from src.db import QueryTranslator

INPUT_QUERIES = [
    'SELECT p.* FROM physician p LIMIT 3;',
    'SELECT phy.name AS \'Physician\', pat.name AS \'Patient\' FROM physician phy, patient pat WHERE phy.employeeid = pat.pcp;',
    'SELECT phy.name, pat.name FROM physician phy INNER JOIN patient pat ON phy.employeeid = pat.pcp;',
    'SELECT * FROM block;',
    'SELECT DISTINCT pcp FROM patient;',
    'SELECT name, employeeid, ssn FROM nurse WHERE registered=\'t\' or position = \'Nurse\' ORDER BY name, employeeid;',
    'INSERT INTO patient VALUES(10, \'AJ\', \'Somewhere\', \'1234567890\', 1, 2);'
]

EXPECTED_QUERIES = [
    'MATCH (p:physician) RETURN p LIMIT 3;',
    'MATCH (phy:physician), (pat:patient) WHERE phy.employeeid = pat.pcp RETURN phy.name AS \'Physician\', pat.name AS \'Patient\';',
    'UNSUPPORTED',
    'MATCH (n:BLOCK) RETURN n;',
    'MATCH (n:patient) RETURN DISTINCT n.pcp;',
    'MATCH (n:nurse) WHERE registered=\'t\' OR POSITION = \'Nurse\' RETURN n.name, n.employeeid, n.ssn ORDER BY n.name, n.employeeid;',
    'UNSUPPORTED'
]


class TranslationTest(TestCase):
    def test_translates_as_expected(self):
        for i, query in enumerate(INPUT_QUERIES):
            translator = QueryTranslator(query, None)
            self.assertEqual(EXPECTED_QUERIES[i], translator.convert()[0])
