"""
NoSQL related DB calls
"""
import logging
import sys
from typing import Dict, List

import pandas as pd
import pymongo
from pymongo.errors import ConnectionFailure

from src.config import MONGO_PORT, MONGO_HOST, MONGO_DB_NAME, MONGO_USER, MONGO_PASS, ERR_DB_CONN
from src.models import AttributeData


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

    def extract_collection_details(self) -> Dict[str, Dict[str, AttributeData]]:
        """
        Fetches collections in the database and gets the keys of the collection

        :return: dictionary containing {collection_name: [key1, key2, ...]}
        """
        collection_names = self.db.list_collection_names()

        details = {}
        logging.info(f'{len(collection_names)} collections discovered')
        for _ in collection_names:
            self.load_records_into_df(details)

        return details

    def extract_records(self, details: Dict[str, Dict[str, AttributeData]]) -> Dict[str, List[Dict[str, object]]]:
        """
        Extracts all records stored in each collection

        :return: dictionary containing list of records. Each record is a dictionary with {key: value}
        """
        records = {}
        for entity in details:
            logging.info(f'Extracting records of {entity}')
            objects = self.db[entity].find()
            records[entity] = []
            for record in objects:
                records[entity].append({key: record.get(key) for key in details[entity]})

        return records

    def load_records_into_df(self, details: Dict[str, Dict[str, AttributeData]]):
        """
        Load collection records into a DataFrame and check for constraints

        :param details: updated details with indices and primary keys
        """
        for entity in details:
            records = self.db[entity].find()
            for item in records:
                details[entity] = {key: AttributeData(i) for i, key in enumerate(item)}
            df = pd.DataFrame(list(records), columns=details[entity].keys())
            for key in details[entity]:
                try:
                    details[entity][key].unique = df[key].is_unique
                except TypeError:
                    details[entity][key].unique = False
            marked = False
            for key in details[entity]:
                if key != '_id' and details[entity][key].unique:
                    details[entity][key].index = True
                    marked = True
            if not marked:
                details[entity]['_id'].index = True
