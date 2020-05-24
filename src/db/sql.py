"""
SQL related DB calls
"""
from typing import Dict

import mysql.connector
from mysql.connector import errorcode

from src import MYSQL_CONFIG


class MySQL:
    """
    A wrapper class around the MySQL connection
    """
    def __init__(self):
        try:
            self.conn = mysql.connector.connect(**MYSQL_CONFIG)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)

    def extract_table_details(self) -> Dict[str, Dict[str, str]]:
        """
        Fetches tables in the database and gets the column name and datatype for each table
        :return: dictionary containing {table_name: {col_name: d_type,...}}
        """
        table_names_cursor = self.conn.cursor(buffered=True)
        table_details_cursor = self.conn.cursor()

        table_names_cursor.execute('SHOW TABLES')

        tables = {}
        for table_name in table_names_cursor:
            table_details_cursor.execute(f'DESCRIBE {table_name[0]}')
            tables[table_name[0]] = {}
            for record in table_details_cursor:
                tables[table_name[0]][record[0]] = record[1]

        table_details_cursor.close()
        table_names_cursor.close()
        return tables

    def close(self):
        """
        Close connection to database
        """
        self.conn.close()
