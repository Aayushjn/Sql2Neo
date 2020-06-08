"""
SQL related DB calls
"""
import logging
import sys
from typing import Dict, List, Iterable

import mysql.connector
from mysql.connector import errorcode

from src.config import MYSQL_CONFIG, ERR_DB_CONN
from src.models import AttributeData


class MySQL:
    """
    A wrapper class around the MySQL connection
    """

    def __init__(self, db_name: str = None):
        try:
            if db_name is not None:
                MYSQL_CONFIG['database'] = db_name
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

    def __del__(self):
        try:
            self.conn.close()
            logging.info('MySQL connection closed')
        except:
            # exception may occur if there was an error in establishing connection
            # quietly suppress exception
            pass

    def get_tables_and_relationships(self) -> Dict[str, Dict[str, AttributeData]]:
        """
        Fetches tables in the database and gets the column names for each table

        :return: dictionary containing
        {
            table_name: {
                col_name: attr_data,...
            },...
        }
        """
        cursor = self.conn.cursor()

        # information_schema.COLUMNS contains information on all columns across all databases
        # ORDINAL_POSITION is used to maintain ordering when fetching relationship information
        query = 'SELECT TABLE_NAME, COLUMN_NAME, COLUMN_KEY, ORDINAL_POSITION FROM information_schema.COLUMNS WHERE ' \
                'TABLE_SCHEMA = %s ORDER BY TABLE_NAME, ORDINAL_POSITION'
        cursor.execute(query, (MYSQL_CONFIG['database'],))

        tables = {}
        logging.info(f'{cursor.rowcount} tables discovered')
        for entry in cursor:
            logging.info(f'Fetching column names of {entry[0]}')
            if tables.get(entry[0]) is None:
                tables[entry[0]] = {}

            # rel defines [ordinal_position, is_pk, is_unique, fk_on]
            data = AttributeData(entry[3])
            if entry[2] == 'PRI':
                data.index = data.unique = True
            elif entry[2] == 'UNI':
                data.unique = True
            tables[entry[0]][entry[1]] = data

        cursor.close()

        cursor = self.conn.cursor()
        # information_schema.KEY_COLUMN_USAGE describes the constraints on columns
        # since COLUMN_KEY is already taken from previous query (for primary key/uniqueness constraint)
        # only foreign keys are taken from this query
        query = 'SELECT TABLE_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME FROM ' \
                'information_schema.KEY_COLUMN_USAGE WHERE TABLE_SCHEMA = %s AND REFERENCED_COLUMN_NAME IS NOT NULL;'
        cursor.execute(query, (MYSQL_CONFIG['database'],))

        for entry in cursor:
            # FKs are stored as REFERENCED_TABLE_NAME.REFERENCED_COLUMN_NAME
            tables[entry[0]][entry[1]].foreign_key = f'{entry[2]}.{entry[3]}'
        cursor.close()

        return tables

    def extract_records(self, table_details: Dict[str, Iterable]) -> Dict[str, List[Dict[str, object]]]:
        """
        Extracts all the records stored in each table

        :return: dictionary containing list of records. Each record is a dictionary with {col_name: value}
        """
        cursor = self.conn.cursor()

        records = {}
        for table in table_details:
            logging.info(f'Extracting records of {table}')
            cursor.execute(f'SELECT * FROM {table}')
            records[table] = []
            for record in cursor:
                # key -> attributes in `table_details[table]`
                # value -> record from SELECT statement
                insert_record = {key: value for (key, value) in zip(table_details[table], record)}
                records[table].append(insert_record)

        cursor.close()
        return records
