# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Field, Item

class GithubUserItem(Item):
    id = Field()
    name = Field()
    _id = Field()

    repositories = Field()
    stars = Field()
    followers = Field()
    following = Field()

    company = Field()
    blog = Field()
    location = Field()
    email = Field()

    vcard_details_html = Field()

