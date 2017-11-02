# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Field, Item

class ShopInfo(Item):
    _id = Field()               # 大众点评商店ID  http://www.dianping.com/shop/3891889
    location = Field()          # 所在城市
    shop_name = Field()         # 商店名称
    shop_level = Field()        # 商店星级
    shop_url = Field()          # 商店主页
    comment_num = Field()       # 评论数量
    avg_cost = Field()          # 人均价格
    score_1 = Field()           # 评分1
    score_2 = Field()           # 评分2
    score_3 = Field()           # 评分3
    shop_type = Field()         # 商店大类型  美食，丽人，周边游...
    shop_sub_type = Field()     # 商店子类型  火锅，杭帮菜，鲁菜...
    location_detail = Field()   # 商店详细地址
    pass
class ShopCommon(Item):
    _id = Field()               # 评论ID
    shop_id = Field()           # 评价商店ID
    user_name = Field()         # 用户姓名
    contribution = Field()      # 该用户等级
    avg_cost = Field()          # 人均价格
    score_1 = Field()           # 评分1
    score_2 = Field()           # 评分2
    score_3 = Field()           # 评分3
    content = Field()           # 内容
    support_count = Field()     # 支持数量
class Category(Item):
    name = Field()
    type = Field()
    pass

