# -*- coding: utf-8 -*-


import logging

# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
# Define your item pipelines here
#
from bson import ObjectId
from scrapy.conf import settings
from scrapy.exceptions import DropItem


class MongoDBPipeline(object):
    def __init__(self):
        connection = pymongo.MongoClient('mongodb://'+settings['MONGODB_USER_NAME']+':'+settings['MONGODB_SERVER_PASSWORD']+'@'+settings['MONGODB_SERVER']+':'+str(settings['MONGODB_PORT'])+'/'+settings['MONGODB_DB'])
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
                self.db['dazdp_shop_detail'].insert(dict(item))

                dzdp_shops = self.db['dzdp_shop'].find({"_id": ObjectId(item['dzdp_shop_id'])})
                for dzdp_shop in dzdp_shops:
                    dzdp_shop["grab_flag"] = 1
                    self.db['dzdp_shop'].save(dzdp_shop)

                logging.debug("add {}".format('dazdp_shop_detail'))
            except (pymongo.errors.WriteError, KeyError) as err:
                raise DropItem("Duplicated Item: {}".format(item['dzdp_shop_id']))
        return item
