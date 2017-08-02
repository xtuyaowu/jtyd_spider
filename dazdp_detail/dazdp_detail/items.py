# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Field, Item

class DianpingDetailItem(Item):
    _id = Field()

    location = Field()
    loc = Field()
    sq = Field()
    foodtype = Field()
    cx = Field()
    cxzfl = Field()
    grab_datetime = Field()
    shopurl = Field()
    shop_id = Field()
    shopname = Field()
    shopGlat = Field()
    shopGlng = Field()
    cityGlat = Field()
    cityGlng = Field()
    sub_shop_num = Field()
    shoplevel = Field()
    plcount = Field()
    ave_money = Field()
    taste = Field()
    envir = Field()
    serv = Field()
    add = Field()
    tel = Field()
    sp_info = Field()
    chuxiao = Field()
    tuan_info = Field()
    ding_info = Field()
    cu_info = Field()
    operateTime = Field()
    brief_info = Field()
    j_park = Field()
    dzcount = Field()
    recommend_food = Field()
    comment = Field()
    content = Field()
    shop_config_str = Field()
    dzdp_shop_id = Field()


