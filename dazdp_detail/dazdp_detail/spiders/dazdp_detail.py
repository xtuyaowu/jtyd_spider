import json
import logging
import random
import traceback
import uuid
from dazdp_detail.db import init_mongodb
from bs4 import BeautifulSoup
import re
import scrapy

from dazdp_detail.items import DianpingDetailItem
from dazdp_detail.spiders.exception import ParseNotSupportedError

logger = logging.getLogger('dazdp_detail')


class Dazdp(scrapy.Spider):
    name = "dazdp_detail"
    rotete_user_agent = True

    def __init__(self):
        self.db = init_mongodb()

    def start_requests(self):
        dzdp_shops = self.db.dzdp_shop.find({})
        for dzdp_shop in dzdp_shops:
            yield scrapy.Request(url=dzdp_shop['shopurl'],callback=self.detail_parse,
                                 meta={'shopurl': dzdp_shop['shopurl'],
                                       'location': dzdp_shop['location'],
                                       'loc': dzdp_shop['loc'],
                                       'foodtype': dzdp_shop['foodtype'],
                                       'shopname': dzdp_shop['shopname'],
                                       'shoplevel': dzdp_shop['shoplevel'],
                                       '_id': str(dzdp_shop['_id'])
                                       }
                                 )

    def detail_parse(self, response):
        shopInfoDict = DianpingDetailItem()
        shopurl = response.meta['shopurl']
        location = response.meta['location']
        loc = response.meta['loc']
        foodtype = response.meta['foodtype']
        shopname = response.meta['shopname']
        shoplevel = response.meta['shoplevel']
        dzdp_shop_id = response.meta['_id']
        try:
            # 获取网页html
            html = response.text
            soup = BeautifulSoup(html)

            # 获取商店名，城市，商圈，食物类型，商店id
            shop_info = soup.select('#body > div.body-content.clearfix > div.breadcrumb')[0].text.split('>')
            sq = ''
            cx = ''
            cxzfl = ''
            dpmc = ''
            if len(shop_info) >= 1:
                sq = shop_info[1].replace('\n', '').replace(' ', '')  # 商圈
            if len(shop_info) >= 2:
                cx = shop_info[2].replace('\n', '').replace(' ', '')  # 菜系
            if len(shop_info) >= 3:
                cxzfl = shop_info[3].replace('\n', '').replace(' ', '')  # 菜系子分类
            # if len(shop_info) >= 4:
            #     dpmc = shop_info[4].replace('\n','').replace(' ','') # 店铺名称
            shop_id = re.findall('[0-9]{1,}', shopurl)[0]  # 店铺ID

            # 经纬度
            shopGlat = ''
            shopGlng = ''
            cityGlat = ''
            cityGlng = ''
            categoryName = ''  # 商户类型
            shop_config_value = ''
            shop_config_list = re.findall('window.shop_config={(.*)loadUserDomain', str(html), re.S)
            if len(shop_config_list) > 0:
                try:
                    shop_config = shop_config_list[0].replace('\n', '').replace(' ', '')
                    shop_config_str = shop_config[0:len(shop_config) - 1].replace(':', '":').replace(',', ',"')
                    shop_config_json = json.loads('{"' + shop_config_str + '}')
                    shopGlat = shop_config_json['shopGlat']
                    shopGlng = shop_config_json['shopGlng']
                    cityGlat = shop_config_json['cityGlat']
                    cityGlng = shop_config_json['cityGlng']
                    categoryName = shop_config_json['categoryName']
                except:
                    shop_config_value = shop_config_str

            # 获取分店数，若无分店，则为0
            s_shop_num = soup.find_all(class_="branch J-branch")
            if s_shop_num:
                s_shop_num = re.findall('>(.*?)<', str(s_shop_num))
                s_shop_num = s_shop_num[0]
                sub_shop_num = str(s_shop_num)[2:-3]
            else:
                sub_shop_num = 0

            # 获取星级
            rankele = soup.find_all("span", class_="mid-rank-stars")
            rank = re.findall('title="(.*?)"', str(rankele))[0]

            # 获取评论数
            plcount = ''  # 评论数
            content = soup.find_all(id='reviewCount')
            plcount = re.findall('id="reviewCount">(.*)</span>', str(content))
            plcount = plcount[0][0:-3]

            # 获取人均价格
            ave_money = ''  # 人均价格
            info = soup.find_all(id='avgPriceTitle')
            pattern = re.compile('[0-9]{1,}')
            result = pattern.findall(str(info))
            if len(result) > 0:
                ave_money = result[0] + u'元'

            # 获取口味，环境，服务评分
            taste = ''  # 口味
            envir = ''  # 环境
            serv = ''  # 服务评分
            results = soup.select('#comment_score > span')
            taste = results[0].text
            taste = taste[3:]

            envir = results[1].text
            envir = envir[3:]

            serv = results[2].text
            serv = serv[3:]

            # 获取电话
            tel = ''
            telelem = soup.find_all(itemprop='tel')
            tellist = re.findall('>(.*?)<', str(telelem))
            if len(tellist) > 0:
                tel = tellist[0]

            # 获取地址
            add = soup.find_all(itemprop="street-address")[0]
            add = re.findall('title="(.*?)">', str(add))[0]

            # 获取特色服务
            promosearch = soup.find_all(class_="promosearch-wrapper")[0]
            info_sp = re.findall('a class="tag tag-(.*?)-b', str(promosearch))
            sp_info = ""
            for ele in info_sp:
                sp_info = sp_info + ele + ","
                # if ele == "tuan":
                #     sp_info = sp_info + u"团、"
                # elif ele == "wai":
                #     sp_info = sp_info + u"外、"
                # elif ele == "cu":
                #     sp_info = sp_info + u"促、"
                # elif ele == "ding":
                #     sp_info = sp_info + u"订、"
            # sp_info = sp_info[0:-1]

            # 获取评价
            comment_good = soup.find_all(class_="good J-summary")
            elements = re.findall('1">(.*?)</a></span>', str(comment_good))
            comment = str()  # 大家认为
            for ele in elements:
                comment = comment + str(ele)
            comment_bad = soup.find_all(class_="bad J-summary")
            elements = re.findall('0">(.*?)</a></span>', str(comment_bad))
            for ele in elements:
                comment = comment + str(ele)

            # 获取商店简介，若无，则显示无
            info_indent_list = soup.select('#basic-info > div.other.J-other > p.info.info-indent')
            brief_info = ''
            operateTime = ''
            j_park = ''
            for info_indent in info_indent_list:
                info_indent_text = info_indent.text
                if '营业时间' in info_indent_text:
                    operateTime = info_indent_text
                elif '餐厅简介' in info_indent_text:
                    brief_info = info_indent_text
                elif '停车信息' in info_indent_text:
                    j_park = info_indent_text
            # try:
            #     brief_info = soup.find_all("p", class_="info info-indent") # 餐厅简介
            #     soup4 = bs(str(brief_info), "html.parser")
            #     namelist = soup4.find_all("p")
            #     brief_info = namelist[1].get_text().strip()[5:]
            # except:
            #     brief_info = u"无"
            #
            # operateTime = soup.select('#basic-info > div.other.J-other > p:nth-child(1) > span.item')

            dzcountlist = soup.select('#reservation')
            dzcount = ''
            if dzcountlist and len(dzcountlist) > 0:
                dzcount = dzcountlist[0].text.replace(' ', '')

            # 获取推荐菜
            food_list = soup.find_all("p", class_="recommend-name")
            # print(type(food_list))
            recommend_food = ''  # 推荐菜
            for ele in food_list:
                recommend_food = ele.get_text().replace(' ', '')

            # 获取团购活动和促销活动
            chuxiao = ''
            tuan = []
            cu = []
            ding = []
            tuan_info = str()
            cu_info = str()
            ding_info = str()
            chuxiaolist = soup.select('#sales > div')
            if len(chuxiaolist) > 0:
                chuxiao = chuxiaolist[0].text

                item_b = soup.find_all('div', class_='item big')
                for ele in item_b:
                    info = ele.get_text()
                    if u'团' in info:
                        tuan.append(info)
                    if u'促' in info:
                        cu.append(info)

                item_s = soup.find_all('a', class_="item small ")
                for ele in item_s:
                    info = ele.get_text()
                    if u'团' in info:
                        tuan.append(info)
                    if u'促' in info:
                        cu.append(info)

                item_sj = soup.find_all('a', class_="item small J_short-promo")
                for ele in item_sj:
                    info = ele.get_text()
                    if u'团' in info:
                        tuan.append(info)
                    if u'促' in info:
                        cu.append(info)

                item_ding = soup.find_all('a', class_="item small small-double")
                for ele in item_ding:
                    info = ele.get_text()
                    if u'订' in info:
                        ding.append(info)

                for i, ele in enumerate(tuan):
                    ele = ele.split()
                    ele[1] = u'现价:' + ele[1]
                    ele[2] = u'原价:' + ele[2]
                    tuan_info = tuan_info + str(i + 1) + '、'
                    for e in ele:
                        tuan_info = tuan_info + str(e) + ' '
                    tuan_info = tuan_info

                for i, ele in enumerate(cu):
                    ele = ele.split()
                    cu_info = cu_info + str(i + 1) + '、'
                    for e in ele:
                        cu_info = cu_info + str(e) + ' '
                    cu_info = cu_info

                for i, ele in enumerate(ding):
                    ele = ele.split()
                    ding_info = ding_info + str(i + 1) + '、'
                    for e in ele:
                        ding_info = ding_info + str(e) + ' '
                    ding_info = ding_info

            shopInfoDict = {}
            shopInfoDict["location"] = location
            shopInfoDict["loc"] = loc
            shopInfoDict["sq"] = sq
            shopInfoDict["foodtype"] = foodtype
            shopInfoDict["cx"] = cx
            shopInfoDict["cxzfl"] = cxzfl
            shopInfoDict["grab_datetime"] = ''
            shopInfoDict["shopurl"] = shopurl
            shopInfoDict["shop_id"] = shop_id
            shopInfoDict["shopname"] = shopname
            shopInfoDict["shopGlat"] = shopGlat
            shopInfoDict["shopGlng"] = shopGlng
            shopInfoDict["cityGlat"] = cityGlat
            shopInfoDict["cityGlng"] = cityGlng
            shopInfoDict["sub_shop_num"] = sub_shop_num
            shopInfoDict["shoplevel"] = shoplevel
            shopInfoDict["plcount"] = plcount
            shopInfoDict["ave_money"] = ave_money
            shopInfoDict["taste"] = taste
            shopInfoDict["envir"] = envir
            shopInfoDict["serv"] = serv
            shopInfoDict["add"] = add
            shopInfoDict["tel"] = tel
            shopInfoDict["sp_info"] = sp_info
            shopInfoDict["chuxiao"] = chuxiao
            shopInfoDict["tuan_info"] = tuan_info
            shopInfoDict["ding_info"] = ding_info
            shopInfoDict["cu_info"] = cu_info
            shopInfoDict["operateTime"] = operateTime.replace('\n', '').replace(' ', '')
            shopInfoDict["brief_info"] = brief_info
            shopInfoDict["j_park"] = j_park
            shopInfoDict["dzcount"] = dzcount
            shopInfoDict["recommend_food"] = recommend_food
            shopInfoDict["comment"] = comment
            shopInfoDict["content"] = html
            shopInfoDict["shop_config_str"] = shop_config_value.replace('\n', '').replace(' ', '')
            shopInfoDict["dzdp_shop_id"] = dzdp_shop_id
        except:
            exstr = traceback.format_exc()
            print(exstr)

        yield shopInfoDict

