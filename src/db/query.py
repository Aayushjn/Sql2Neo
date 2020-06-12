import logging
import sys
from typing import List, Optional

import sqlparse


def get_tables(token: sqlparse.sql.Token) -> List[str]:
    """
    Extract table names from the given `token`

    :param token: token containing table names (follows the 'FROM' token)
    :return: list of formatted tables [(n:<table_name>),...]
    """
    if isinstance(token, tuple):
        # normally a `sqlparse.sql.Identifier` is found and the string representation is taken
        tabs = str(token[1]).strip()
    else:
        # in case the table name is also a keyword, simply takes its string representation
        tabs = str(token).strip()

    # comma-separated means that the query runs on multiple tables
    tabs = list(map(lambda x: x.strip(), tabs.split(',')))
    # only one table used and no name given to the table
    if len(tabs) == 1 and len(tabs[0].split(' ')) == 1:
        # use default variable 'n'
        return [f'(n:{tabs[0]})']

    tables = []
    for tab in tabs:
        sp = tab.split(' ')
        if len(sp) == 1:
            # if no name provided, i.e., using 'patient.name' instead' of 'p.name'
            tables.append(f'({tab}:{tab})')
        else:
            tables.append(f'({sp[1]}:{sp[0]})')

    return tables


def get_order_by_attributes(token: sqlparse.sql.Token) -> List[str]:
    """
    Extract attributes used in 'ORDER BY' clause

    :param token: token containing attributes (follows the 'ORDER BY' token)
    :return: list of formatted attributes [n.attr,...]
    """
    order_by = list(filter(lambda x: x != ' ' and x != ',', map(str, token[1])))
    for j, attr in enumerate(order_by):
        if len(attr.split('.')) == 1:
            order_by[j] = f'n.{attr}'

    return order_by


def build_query(tables: List[str],
                where: Optional[List[str]],
                attributes: List[str],
                order_by: Optional[List[str]],
                limit: Optional[str]) -> str:
    """
    Builds a cypher query from the extracted values

    :param tables: tables (labels) to fetch from
    :param where: where clause
    :param attributes: projection attributes
    :param order_by: optional order by attributes
    :param limit: return value limit
    :return: final cypher query
    """
    cql = [f'MATCH {",".join(tables)}']
    if where is not None:
        cql.append(f' WHERE {"".join(where)}')
    cql.append(f' RETURN {",".join(attributes)}')
    if order_by is not None:
        cql.append(f' ORDER BY {",".join(order_by)}')
    if limit is not None:
        cql.append(f' LIMIT {limit}')
    cql.append(';')

    return ''.join(cql)


class QueryTranslator:
    """
    A query translator for converting SQL queries to Cypher queries
    """
    def __init__(self, query: Optional[str], file: Optional[str]):
        if file is None:
            self.sql = query.strip()
        else:
            if not file.endswith('.sql') and not file.endswith('.txt'):
                logging.error('Only .txt or .sql file types supported')
                sys.exit(1)
            try:
                with open(file, 'r') as f:
                    self.sql = f.read().strip()
            except FileNotFoundError as e:
                logging.error(f'{file} not found!')
                sys.exit(e.errno)

    def convert(self) -> List[str]:
        """
        Converts `self.sql` to a list of CQL queries

        :return: converted cypher queries
        """
        queries = sqlparse.split(self.sql)
        converted = []

        for query in queries:
            # all keywords are formatted to UPPER_CASE for uniformity
            query = sqlparse.format(query, keyword_case='upper', strip_comments=True)
            parsed_tokens = sqlparse.parse(query)[0].tokens

            # projection attributes are found between SELECT and FROM tokens
            # first all 'n.*' occurrences are replaced with 'n' (normally occurs when '*' selected from multiple tables)
            # the above could be 'SELECT m.*, n.* FROM table1 m, table2 n' or 'SELECT n.* FROM table n'
            # then any other '*' projections are replaced with default variable 'n'
            # the above is when the query is 'SELECT * FROM table ...;
            # CQL supports aliasing (SELECT n.name AS 'Name'), so attributes are taken directly from `query`
            # magic number '7' because 'SELECT (7th index)... FROM'
            attributes = query[7:query.index('FROM')].strip().replace('.*', '').replace('*', 'n')
            if len(attributes) != 1:
                attributes = list(
                    map(
                        # if n.attr doesn't exist, then prepend n., otherwise let it be
                        lambda x: f'n.{x.strip()}' if len(x.split('.')) == 1 else x,
                        attributes.split(','))
                )

            tables = None
            where = None
            order_by = None
            limit = None

            for i, token in enumerate(parsed_tokens):
                if str(token) == 'FROM':
                    tables = get_tables(sqlparse.sql.TokenList(parsed_tokens[i:]).token_next(1))
                elif str(token) == 'WHERE':
                    where = list(map(str, token.tokens[2:]))
                    if where[-1] == ';':
                        # if last part of query is the WHERE clause, remove the trailing semicolon
                        where = where[:-1]
                elif str(token) == 'ORDER BY':
                    order_by = get_order_by_attributes(sqlparse.sql.TokenList(parsed_tokens[i:]).token_next(1))
                elif str(token) == 'LIMIT':
                    token_list = sqlparse.sql.TokenList(parsed_tokens[i:])
                    limit = token_list.token_next(1)[1]

            converted.append(build_query(tables, where, attributes, order_by, limit))

        return converted
