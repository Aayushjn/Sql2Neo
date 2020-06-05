"""
SQL related DB calls
"""
import logging
import sys
from typing import Dict, List, Union

import mysql.connector
from mysql.connector import errorcode

from src.config import MYSQL_CONFIG, ERR_DB_CONN


class MySQL:
    """
    A wrapper class around the MySQL connection
    """
    def __init__(self):
        try:
            self.conn = mysql.connector.connect(**MYSQL_CONFIG)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                msg = "Something is wrong with your user name or password"
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                msg = "Database does not exist"
            else:
                msg = err.msg
            logging.error(msg)
            sys.exit(ERR_DB_CONN)
        logging.info('Connection established to MySQL database')

    def get_tables_and_relationships(self) -> Dict[str, Dict[str, List[Union[bool, str, None]]]]:
        """
        Fetches tables in the database and gets the column names for each table
        :return: dictionary containing
        {
            table_name: {
                col_name: {
                    'PK': True/False,
                    'UNI': True/False,
                    'FK': None/'<ref_table.ref_col>'
                },...
            },...
        }
        """
        cursor = self.conn.cursor()
        query = 'SELECT TABLE_NAME, COLUMN_NAME, COLUMN_KEY, ORDINAL_POSITION FROM information_schema.COLUMNS WHERE ' \
                'TABLE_SCHEMA = %s ORDER BY TABLE_NAME, ORDINAL_POSITION'
        cursor.execute(query, (MYSQL_CONFIG['database'],))

        tables = {}
        logging.info(f'{cursor.rowcount} tables discovered')
        for entry in cursor:
            logging.info(f'Fetching column names of {entry[0]}')
            if tables.get(entry[0]) is None:
                tables[entry[0]] = {}

            rel = [entry[3], False, False, None]
            if entry[2] == 'PRI':
                rel[1] = rel[2] = True
            elif entry[2] == 'UNI':
                rel[2] = True
            tables[entry[0]][entry[1]] = rel

        cursor.close()

        cursor = self.conn.cursor()
        query = 'SELECT TABLE_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME FROM ' \
                'information_schema.KEY_COLUMN_USAGE WHERE TABLE_SCHEMA = %s AND REFERENCED_COLUMN_NAME IS NOT NULL;'
        cursor.execute(query, (MYSQL_CONFIG['database'],))

        for entry in cursor:
            tables[entry[0]][entry[1]][3] = f'{entry[2]}.{entry[3]}'
        cursor.close()

        return tables

    def extract_records(self) -> Dict[str, List[Dict[str, object]]]:
        """
        Extracts all the records stored in each table
        :return: dictionary containing list of records. Each record is a dictionary with {col_name: value}
        """
        table_details = self.get_tables_and_relationships()
        cursor = self.conn.cursor()

        records = {}
        for table in table_details:
            logging.info(f'Extracting records of {table}')
            cursor.execute(f'SELECT * FROM {table}')
            records[table] = []
            for record in cursor:
                insert_record = {key: value for (key, value) in zip(table_details[table], record)}
                records[table].append(insert_record)

        cursor.close()
        return records

    def close(self):
        """
        Close connection to database
        """
        self.conn.close()
        logging.info('MySQL connection closed')
