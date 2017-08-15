import json
import logging
import random
import traceback
import uuid
from bs4 import BeautifulSoup
import re
import scrapy


from github_spider.db import init_mongodb
from github_spider.items import GithubUserItem

logger = logging.getLogger('dazdp_detail')


class GithubSpider(scrapy.Spider):
    name = "github_spider"
    rotete_user_agent = True

    def __init__(self):
        self.db = init_mongodb()

    def start_requests(self):
        for i in range(114895):
            dzdp_shops = self.db.jtyd_github_user.find({"grab_flag": 0}).limit(100).skip(100 * i)
            for dzdp_shop in dzdp_shops:
                yield scrapy.Request(url='https://github.com/'+dzdp_shop['login'], callback=self.detail_parse,
                                     meta={'id': dzdp_shop['id'],
                                           'login': dzdp_shop['login'],
                                           '_id': dzdp_shop['_id']
                                           }
                                     )

    def detail_parse(self, response):

        githubUserDict = GithubUserItem()

        id = response.meta['id']
        login = response.meta['login']
        githubUserDict['_id'] = str(response.meta['_id'])

        try:
            # 获取网页html
            html = response.text
            soup = BeautifulSoup(html)

            # 获取商店名，城市，商圈，食物类型，商店id
            underline_s = soup.find_all('a', class_="underline-nav-item")
            githubUserDict['repositories'] = underline_s[1].text
            githubUserDict['stars'] = underline_s[2].text
            githubUserDict['followers'] = underline_s[3].text
            githubUserDict['following'] = underline_s[4].text

            githubUserDict['vcard_details_html'] = soup.select('#js-pjax-container > div > div.h-card.col-3.float-left.pr-3 > ul')[0].prettify()
            p_org = soup.find_all('span', class_="p-org")
            if len(p_org) > 0:
                githubUserDict['company'] = p_org[0].prettify()

            p_label = soup.find_all('span', class_="p-label")
            if len(p_label) > 0:
                githubUserDict['location'] = p_label[0].prettify()

            u_email = soup.find_all('a', class_="u-email")
            if len(u_email) > 0:
                githubUserDict['email'] = u_email[0].prettify()

            u_url = soup.find_all('a', class_="u-url")
            if len(u_url) > 0:
                githubUserDict['blog'] = u_url[0].prettify()

            githubUserDict['id'] = id
            githubUserDict['name'] = login
        except:
            exstr = traceback.format_exc()
            print(exstr)

        yield githubUserDict

