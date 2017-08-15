# -*- coding: utf-8 -*-


import logging

# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
# Define your item pipelines here
#
from scrapy.conf import settings
from scrapy.exceptions import DropItem
from bson.objectid import ObjectId
from github_spider.db import init_mongodb

class MongoDBPipeline(object):
    def __init__(self):
        self.db = init_mongodb()

    def process_item(self, item, spider):
        valid = True
        for data in item:
            if not data:
                valid = False
                raise DropItem("Missing {0}!".format(data))
        if valid:
            try:
                # key = {}
                # key['sku_id'] = item['sku_id']
                # self.db[item['item_name']].update(key, dict(item), upsert=True)
                self.db['github_user_info'].insert(dict(item))
                github_user = self.db.jtyd_github_user.find({"_id": ObjectId(item['_id'])})
                github_user['grab_flag'] = 1
                self.db.jtyd_github_user.save(github_user)
                logging.debug("add {}".format(item['_id']))
            except (pymongo.errors.WriteError, KeyError) as err:
                raise DropItem("Duplicated Item: {}".format(item['name']))
        return item
