"""
SQL related DB calls
"""
import logging
import sys
from typing import Dict, List

import mysql.connector
from mysql.connector import errorcode

from src.settings import MYSQL_CONFIG, ERR_DB_CONN


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

    def extract_table_details(self) -> Dict[str, List[str]]:
        """
        Fetches tables in the database and gets the column name and datatype for each table
        :return: dictionary containing {table_name: [col1, col2, ...]}
        """
        table_names_cursor = self.conn.cursor(buffered=True)
        table_details_cursor = self.conn.cursor()

        table_names_cursor.execute('SHOW TABLES')

        tables = {}
        logging.info(f'{table_names_cursor.rowcount} tables discovered')
        for table_name in table_names_cursor:
            table_details_cursor.execute(f'DESCRIBE {table_name[0]}')
            tables[table_name[0]] = []
            logging.info(f'Extracting {table_name[0]}\'s attributes and relationships')
            for record in table_details_cursor:
                tables[table_name[0]].append(record[0])

        table_details_cursor.close()
        table_names_cursor.close()

        return tables

    def extract_records(self) -> Dict[str, List[Dict[str, object]]]:
        """
        Extracts all the records stored in each table
        :return: dictionary containing list of records. Each record is a dictionary with {col_name: value}
        """
        table_details = self.extract_table_details()
        cursor = self.conn.cursor()

        records = {}
        for table in table_details:
            logging.info(f'Extracting records of {table}')
            cursor.execute(f'SELECT * FROM {table}')
            records[table] = []
            for record in cursor:
                insert_record = {table_details[table][i]: entry for (i, entry) in enumerate(record)}
                records[table].append(insert_record)

        cursor.close()
        return records

    def close(self):
        """
        Close connection to database
        """
        self.conn.close()
        logging.info('MySQL connection closed')
