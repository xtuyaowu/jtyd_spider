#!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# author:Samray <samrayleung@gmail.com>

import pymongo
from scrapy.conf import settings


def init_mongodb():
    connection = pymongo.MongoClient(
        'mongodb://' + settings['MONGODB_USER_NAME'] + ':' + settings['MONGODB_SERVER_PASSWORD'] + '@' + settings[
            'MONGODB_SERVER'] + ':' + str(settings['MONGODB_PORT']) + '/' + settings['MONGODB_DB'])
    db = connection[settings['MONGODB_DB']]
    return db
