# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem
from twisted.enterprise import adbapi
#import MySQLdb
#import MySQLdb.cursors
#from scrapy import log

import logging

# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
# Define your item pipelines here
#
from scrapy.conf import settings
from scrapy.exceptions import DropItem


class CleanPipeline(object):

    def __init__(self):
        self.has = set()

    def process_item(self, item, spider):
        if item.keys() >= 6:
            if item in self.has:
                raise DropItem("Duplicate item found: %s" % item)
            else:
                self.has.add(item)
                return item


# class MySQLPipeline(object):
#     def __init__(self, dbpool):
#         self.dbpool = dbpool
#
#     @classmethod
#     def from_settings(cls, settings):
#         dbargs = dict(
#             host=settings['MYSQL_HOST'],
#             db=settings['MYSQL_DBNAME'],
#             user=settings['MYSQL_USER'],
#             passwd=settings['MYSQL_PASSWD'],
#             charset='utf8',
#             cursorclass = MySQLdb.cursors.DictCursor,
#             use_unicode= True,
#         )
#         dbpool = adbapi.ConnectionPool('MySQLdb', **dbargs)
#         return cls(dbpool)
#
#     def process_item(self, item, spider):
#         d = self.dbpool.runInteraction(self.__do__insert, item, spider)
#         d.addBoth(lambda _: item)
#         return d
#
#     def __do__insert(self, conn, item, spider):
#         try:
#             conn.execute("""
#                 insert into 58pbdndb set title = %s, area = %s, price = %s, quality = %s, time = %s
#             """, (item['title'], item['area'], item['price'], item['quality'], item['time']))
#
#         except MySQLdb.Error, e:
#             spider.log("Mysql Error %d: %s" % (e.args[0], e.args[1]), level=log.DEBUG)

class MongoDBPipeline(object):
    def __init__(self):
        connection = pymongo.MongoClient(
            settings['MONGODB_SERVER'],
            settings['MONGODB_PORT']
        )
        self.db = connection[settings['MONGODB_DB']]

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
                self.db[item['item_name']].insert(dict(item))
                logging.debug("add {}".format(item['item_name']))
            except (pymongo.errors.WriteError, KeyError) as err:
                raise DropItem("Duplicated Item: {}".format(item['name']))
        return item

