# -*- coding: utf-8 -*-
import pymongo

class FundPipeline(object):
    def __init__(self):
        self.client = pymongo.MongoClient('mongodb://localhost:27017')
        self.db = self.client['fund']
        self.table = self.db['gender_count']

    def process_item(self, item, spider):
        self.table.insert_one(item)
        return item
