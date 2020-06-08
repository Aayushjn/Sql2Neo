"""
NoSQL related DB calls
"""
import logging
import sys
from typing import Dict, List

import pymongo
from pymongo.errors import ConnectionFailure

from src.config import MONGO_PORT, MONGO_HOST, MONGO_DB_NAME, MONGO_USER, MONGO_PASS, ERR_DB_CONN


class Mongo:
    """
    A wrapper class around the MongoClient connection
    """

    def __init__(self, db_name: str = None):
        self.client = pymongo.MongoClient(MONGO_HOST, int(MONGO_PORT), username=MONGO_USER, password=MONGO_PASS)
        try:
            # 'ismaster' admin command is an inexpensive command to verify if connection to MongoDB is established
            self.client.admin.command('ismaster')
        except ConnectionFailure:
            logging.error(f'Check whether MongoDB is running on {MONGO_HOST}:{MONGO_PORT}')
            sys.exit(ERR_DB_CONN)
        logging.info('Connection established to Mongo DB')
        self.db = self.client[db_name or MONGO_DB_NAME]

    def __del__(self):
        try:
            self.client.close()
            logging.info('MongoDB connection closed')
        except:
            # exception may occur if there was an error in establishing connection
            # quietly suppress exception
            pass

    def extract_collection_details(self) -> Dict[str, List[str]]:
        """
        Fetches collections in the database and gets the keys of the collection

        :return: dictionary containing {collection_name: [key1, key2, ...]}
        """
        collection_names = self.db.list_collection_names()

        details = {}
        logging.info(f'{len(collection_names)} collections discovered')
        for name in collection_names:
            details[name] = []
            item = self.db[name].find_one()
            logging.info(f'Extracting {name}\'s attributes')
            for key in item:
                details[name].append(key)

        return details

    def extract_records(self) -> Dict[str, List[Dict[str, object]]]:
        """
        Extracts all records stored in each collection

        :return: dictionary containing list of records. Each record is a dictionary with {key: value}
        """
        details = self.extract_collection_details()

        records = {}
        for key in details:
            logging.info(f'Extracting records of {key}')
            objects = self.db[key].find()
            records[key] = []
            for record in objects:
                records[key].append(record)

        return records
