"""
NoSQL related DB calls
"""
from typing import Dict, List

import pymongo

from src.settings import MONGO_PORT, MONGO_HOST, MONGO_DB_NAME


class Mongo:
    """
    A wrapper class around the MongoClient connection
    """
    def __init__(self):
        self.client = pymongo.MongoClient(f'mongodb://{MONGO_HOST}:{MONGO_PORT}/')

    def extract_collection_details(self) -> Dict[str, List[str]]:
        """
        Fetches collections in the database and gets the keys of the collection
        :return: dictionary containing {collection_name: [key1, key2, ...]}
        """
        db = self.client[MONGO_DB_NAME]
        collection_names = db.list_collection_names()

        details = {}
        for name in collection_names:
            details[name] = []
            item = db[name].find_one()
            for key in item:
                if key != '_id':
                    details[name].append(key)

        return details

    def close(self):
        """
        Close connection to database
        """
        self.client.close()
