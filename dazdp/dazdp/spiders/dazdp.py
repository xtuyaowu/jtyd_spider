# -*- coding: utf-8 -*-
import json
import logging
import random
import uuid
from urllib.parse import urlparse

import scrapy
from dazdp.items import ShopInfo,ShopCommon
from dazdp.spiders.exception import ParseNotSupportedError

logger = logging.getLogger('dazdp')


class Dazdp(scrapy.Spider):
    name = "dazdp"
    rotete_user_agent = True

    def __init__(self):
        # start_urls = [
        #     'http://www.dianping.com/search/category/1/10'
        #     # 'http://www.dianping.com/search/category/1/10'
        #     # 'http://www.dianping.com/search/category/1/10/g3243r9'
        #     # 'http://www.dianping.com/search/category/1/10/g109r5938'
        #     #http://www.dianping.com/search/category/7/10/g117
        # ]
        self.typeDict = {'g110': '火锅', 'g101': '本帮江浙菜', 'g113': '日本菜', 'g117': '面包甜点', 'g132': '咖啡厅', 'g111': '自助餐', 'g112': '小吃快餐', 'g116': '西餐', 'g114': '韩国料理', 'g103': '粤菜', 'g508': '烧烤', 'g115': '东南亚菜', 'g102': '川菜', 'g109': '素菜', 'g106': '东北菜', 'g104': '湘菜', 'g248': '云南菜', 'g3243': '新疆菜', 'g251': '海鲜', 'g26481': '西北菜', 'g203': '蟹宴', 'g107': '台湾菜', 'g105': '贵州菜', 'g215': '面馆', 'g219': '小龙虾', 'g247': '江西菜', 'g1783': '家常菜', 'g118': '其他', '0_%E5%88%BA%E8%BA%AB': '刺身', '0_%E7%BA%A2%E7%83%A7%E8%82%89': '红烧肉', '0_%E7%89%9B%E6%8E%92': '牛排', '0_%E7%83%A4%E9%B1%BC': '烤鱼', '0_%E4%B8%89%E6%96%87%E9%B1%BC': '三文鱼', '0_%E6%84%8F%E5%A4%A7%E5%88%A9%E9%9D%A2': '意大利面', 'g141': '足疗按摩', 'g140': '洗浴/汗蒸', 'g135': 'KTV', 'g133': '酒吧', 'g2754': '密室逃脱', 'g20040': '轰趴馆', 'g134': '茶馆', 'g20041': '私人影院', 'g20042': '网吧网咖', 'g144': 'DIY手工坊', 'g20038': '采摘/农家乐', 'g142': '文化艺术', 'g137': '游乐游艺', 'g33857': 'VR', 'g6694': '桌游', 'g20039': '真人CS', 'g32732': '棋牌室', 'g156': '桌球馆', 'g26490': '更多休闲娱乐', 'g163': '婚纱摄影', '2': '旅拍', 'hunyan?cityId=2': '婚宴', 'g167': '婚礼策划', 'g162': '婚纱礼服', 'g25412': '西服定制', 'g191': '婚戒首饰', 'g166': '彩妆造型', 'g164': '司仪主持', 'g185': '婚礼跟拍', 'g186': '婚车租赁', 'g192': '婚礼小商品', 'g6700': '个性写真', 'g6844': '更多婚礼服务', 'g25410': '婚房装修', 'g136': '电影院', 'playing': '热映影片', 'comingsoon': '即将上映', 'g25461': '演出场馆', 'g33877': '剧场/影院', 'g33878': '音乐厅/礼堂', 'g33879': '艺术中心/文化广场', 'g33880': '热门演出', 'g33881': '赛事展览', 'g33882': '其他电影演出赛事', 'g157': '美发', 'g33761': '美甲美睫', 'g158': '美容／SPA', 'g159': '瘦身纤体', 'g148': '瑜伽', 'g149': '舞蹈', 'g2898': '韩式定妆', 'g2572': '祛痘', 'g493': '纹身', 'g123': '化妆品', 'g2790': '产后塑形', '50_%E6%B0%B4%E5%85%89%E9%92%88': '水光针', '50_%E7%98%A6%E8%84%B8%E9%92%88': '瘦脸针', '50_%E6%8A%97%E8%A1%B0%E8%80%81': '抗衰老', '50_%E7%99%BD%E7%93%B7%E5%A8%83%E5%A8%83': '白瓷娃娃', '50_%E9%9A%86%E9%BC%BB': '隆鼻', '50_%E5%8F%8C%E7%9C%BC%E7%9A%AE': '双眼皮', '50_%E7%8E%BB%E5%B0%BF%E9%85%B8': '玻尿酸', '50_%E7%BE%8E%E7%99%BD%E5%AB%A9%E8%82%A4': '美白嫩肤', 'g3020': '五星级/豪华型', 'g3022': '四星级/高档型', 'g3024': '三星级/舒适型', 'g171': '经济连锁', 'g33840n10': '情侣酒店', 'g172': '青年旅社', 'g25842': '客栈', 'g33841n10': '民宿', 'g27760': '儿童乐园', 'g27767': '婴儿游泳', 'g33776': '运动探险', 'g33806': '亲子DIY', 'g27761': '早教中心', 'g27762': '幼儿外语', 'g27763': '幼儿才艺', 'g189': '幼儿园', 'g20009': '托班/托儿所', 'g27814': '孕妇写真', 'g33793': '满月照', 'g33794': '百天照', 'g33792': '上门拍', 'g2782': '全家福', 'g2784': '月子会所', 'g2786': '月嫂', 'g2996': '开奶催乳', 'g2926': '展馆展览', 'g5672': '温泉', 'g2834': '动植物园', 'g2916': '水上娱乐', 'g27852': '滑雪', 'g33831': '景点', 'g33832': '旅游其他', 'g147': '健身中心', 'g6701': '武术场馆', 'g151': '游泳馆', 'g152': '羽毛球馆', 'g6713': '溜冰场', 'g6709': '射箭馆', 'g146': '篮球场', 'g153': '网球场', 'g6708': '攀岩馆', 'g6712': '乒乓球馆', 'g6702': '足球场', 'g154': '高尔夫场', 'g155': '保龄球馆', 'g150': '体育场馆', 'g6706': '壁球馆', 'g145': '更多运动', 'g119': '综合商场', 'g120': '服饰鞋包', 'g121': '运动户外', 'g122': '珠宝饰品', 'g25475': '装修公司', 'home-tuku': '装修美图', '67': '装修资讯', 'g33866': '橱柜', 'g33870': '地板', 'g33864': '瓷砖石材', 'g33867': '厨卫洁具', 'g33876': '灯饰照明', 'g33863': '油漆涂料', 'g33868': '集成吊顶', 'g33869': '家用五金', 'g33872': '木材板材', 'g6827': '家具', 'g6829': '床上用品/家纺', 'g33887': '家居饰品', 'g33886': '厨具餐具', 'g20023': '智能家居', 'g32705': '家用电器', 'g33891': '建材卖场', 'g33890': '家居卖场', 'g33889': '灯饰卖场', 'g3030': '英语', 'g3032': '日语', 'g3034': '韩语', 'g33946': '雅思托福', 'g33945': '留学申请', 'g3040': '其他外语', 'g33756': '绘画', 'g3041': '钢琴', 'g3042': '吉他', 'g33757': '书法', 'g3048': '声乐', 'g3044': '古筝', 'g33898': '插花', 'g33897': '烘焙', 'g3050': '其他音乐培训', 'g179': '驾校', 'g3057': '美容化妆', 'g3058': '会计', 'g3060': '厨艺', 'g3059': 'IT', 'g3062': '其他职业技术', 'g2876': '全部升学辅导', 'g33828': '艺考', 'g3064': '快照冲印', 'g3066': '文印图文', 'g33986': '搬家运输', 'g2928': '生活配送', 'g195': '家政服务', 'g33762': '洗涤护理', 'g33974': '生活缴费', 'g33975': '社区服务', 'g33976': '家电数码维修', 'g26117': '居家维修', 'g2930': '回收', 'g835': '通信营业厅', 'g980': '售票点', 'g3012': '银行', 'g6823': '交通', 'g836': '房屋地产', 'g3082': '政府机构', 'g33994': '丧葬', 'g33959': '律师服务', 'g33963': '财务服务', 'g34003': '金融', 'g33965': '文化传媒', 'g182': '医院', 'g612': '体检中心', 'g235': '药店', 'g2914': '中医', 'g25148': '宠物医院', 'g183': '整形', 'g257': '妇幼医院', 'g2912': '其他医疗', 'g2828': '洗车', 'g176': '维修保养', 'g20026': '汽车美容', 'g236': '加油站', 'g180': '停车场', 'g178': '汽车租赁', 'g175': '4S店／汽车销售', 'g177': '配件／车饰', 'g33764': '交警队', 'g259': '汽车保险', 'g33763': '年检站', 'g25147': '宠物店'}
        self.types = ['g110', 'g101', 'g113', 'g117', 'g132', 'g111', 'g112', 'g116', 'g114', 'g103', 'g508', 'g115', 'g102', 'g109', 'g106', 'g104', 'g248', 'g3243', 'g251', 'g26481', 'g203', 'g107', 'g105', 'g215', 'g219', 'g247', 'g1783', 'g118', '0_%E5%88%BA%E8%BA%AB', '0_%E7%BA%A2%E7%83%A7%E8%82%89', '0_%E7%89%9B%E6%8E%92', '0_%E7%83%A4%E9%B1%BC', '0_%E4%B8%89%E6%96%87%E9%B1%BC', '0_%E6%84%8F%E5%A4%A7%E5%88%A9%E9%9D%A2', 'g141', 'g140', 'g135', 'g133', 'g2754', 'g20040', 'g134', 'g20041', 'g20042', 'g144', 'g20038', 'g142', 'g137', 'g33857', 'g6694', 'g20039', 'g32732', 'g156', 'g26490', 'g163', '2', 'hunyan?cityId=2', 'g167', 'g162', 'g25412', 'g191', 'g166', 'g164', 'g185', 'g186', 'g192', 'g6700', 'g6844', 'g136', 'playing', 'comingsoon', 'g25461', 'g33877', 'g33878', 'g33879', 'g33880', 'g33881', 'g33882', 'g157', 'g33761', 'g158', 'g159', 'g148', 'g149', 'g2898', 'g2572', 'g493', 'g123', 'g2790', '50_%E6%B0%B4%E5%85%89%E9%92%88', '50_%E7%98%A6%E8%84%B8%E9%92%88', '50_%E6%8A%97%E8%A1%B0%E8%80%81', '50_%E7%99%BD%E7%93%B7%E5%A8%83%E5%A8%83', '50_%E9%9A%86%E9%BC%BB', '50_%E5%8F%8C%E7%9C%BC%E7%9A%AE', '50_%E7%8E%BB%E5%B0%BF%E9%85%B8', '50_%E7%BE%8E%E7%99%BD%E5%AB%A9%E8%82%A4', 'g3020', 'g3022', 'g3024', 'g171', 'g33840n10', 'g172',
                         'g25842', 'g33841n10', 'g27760', 'g27767', 'g33776', 'g33806', 'g27761', 'g27762', 'g27763', 'g189', 'g20009', 'g27814', 'g33793', 'g33794', 'g33792', 'g2782', 'g2784', 'g2786', 'g2996', 'g2926', 'g20038', 'g5672', 'g2834', 'g2916', 'g27852', 'g33831', 'g33832', 'g147', 'g6701', 'g151', 'g152', 'g6713', 'g6709', 'g146', 'g156', 'g153', 'g6708', 'g6712', 'g6702', 'g154', 'g155', 'g150', 'g6706', 'g145', 'g119', 'g120', 'g121', 'g122', 'g25475', 'home-tuku', '67', 'g33866', 'g33870', 'g33864', 'g33867', 'g33876', 'g33863', 'g33868', 'g33869', 'g33872', 'g6827', 'g6829', 'g33887', 'g33886', 'g20023', 'g32705', 'g33891', 'g33890', 'g33889', 'g3030', 'g3032', 'g3034', 'g33946', 'g33945', 'g3040', 'g33756', 'g3041', 'g3042', 'g33757', 'g3048', 'g3044', 'g33898', 'g33897', 'g3050', 'g179', 'g3057', 'g3058', 'g3060', 'g3059', 'g3062', 'g2876', 'g33828', 'g3064', 'g3066', 'g33986', 'g2928', 'g195', 'g33762', 'g33974', 'g33975', 'g33976', 'g26117', 'g2930', 'g835', 'g980', 'g3012', 'g6823', 'g836', 'g3082', 'g33994', 'g33959', 'g33963', 'g34003', 'g33965', 'g182', 'g612', 'g182', 'g235', 'g2914', 'g25148', 'g183', 'g257', 'g2912', 'g2828', 'g176', 'g20026', 'g236', 'g180', 'g178', 'g175', 'g177', 'g33764', 'g259', 'g33763', 'g25147', 'g25148']
        # self.types = ['g101']
    
    def getField(self,node,xpath,default=""):
            arr = node.xpath(xpath).extract()
            if len(arr) > 0 :
                return arr[0]
            else:
                return default
    # 爬取顺序:
    # 1. 获取商店分类主页
    # 2. 获取分类主页页码
    # 3. 获取商店列表页面，获取商店信息和商店评论链接
    # 4. 获取商店评论页码
    # 5. 获取商店评论
    def start_requests(self):
        url = 'http://www.dianping.com/search/category/{0}/10/{1}'
        for i in range(1, 2501):
            for ft in self.types:
                new_url = url.format(i, ft)
                yield scrapy.Request(new_url, callback=self.parse_list_first)
    # 获取商店列表分页
    def parse_list_first(self, response):
        selector = scrapy.Selector(response)
        ################获取分页#################
        pg = 0
        pages = selector.xpath(
            '//div[@class="page"]/a/@data-ga-page').extract()
        if len(pages) > 0:
            pg = pages[len(pages) - 2]
        pg = int(str(pg)) + 1
        url = str(response.url)
        for p in range(1,pg):
            ul = url + 'p' + str(p)
            yield scrapy.Request(ul, callback=self.parse_list)
    # 获取商店列表页面，获取商店信息和商店评论链接
    def parse_list(self, response):
        def getShopId(shopUrl):
                url_items = shopurl.split('/')
                if len(url_items) > 0:
                    return url_items[-1]
                else:
                    return ""
        item = ShopInfo()
        urls = response.xpath('//head/link[@rel="canonical"]/@href').extract()
        shopTypeId = urls[0].split('/')[-1].split('p')[0]
        shopTypeName = self.typeDict[shopTypeId]
        location = response.xpath('//a[@class="city J-city"]/span/text()').extract_first()
        selector = scrapy.Selector(response)
        div = selector.xpath('//div[@id="shop-all-list"]/ul/li')
        for dd in div:         
            item['shop_name'] = self.getField(dd,'div[2]/div[1]/a[1]/h4/text()')
            shopurl = self.getField(dd,'div[2]/div[1]/a[1]/@href')
            item['shop_url'] =  self.getField(dd,'div[2]/div[1]/a[1]/@href','')
            shopId = getShopId(item['shop_url'])
            item['_id'] = shopId
            item['shop_level'] = self.getField(dd,'div[2]/div[2]/span/@title','')
            item['comment_num'] = self.getField(dd,'div[2]/div[2]/a[1]/b/text()','0')
            item['avg_cost'] = self.getField(dd,'div[2]/div[2]/a[2]/b/text()','0')  # self.getField(dd,'','0')
            item['score_1'] = self.getField(dd,'div[2]/span/span[1]/b/text()','0')
            item['score_2'] = self.getField(dd,'div[2]/span/span[2]/b/text()','0')
            item['score_3'] = self.getField(dd,'div[2]/span/span[3]/b/text()','0')
            item['shop_sub_type'] = self.getField(dd,'div[2]/div[3]/a[1]/span/text()','')
            item['location_detail'] = self.getField(dd,'div[2]/div[3]/a[2]/span/text()','')
            item['shop_type'] = shopTypeName
            item['location'] = location
            yield item
            commonUrl = 'http://www.dianping.com/shop/{0}/review_more'
            yield scrapy.Request(commonUrl.format(shopId),callback=self.parse_common_first)
    # 获取评论页码
    def parse_common_first(self,response):
        selector = scrapy.Selector(response)
        pg = 0
        pages = selector.xpath('//a[@class="PageLink"][last()]/@title').extract()
        if len(pages) > 0:
            pg = pages[0]
        pg = int(str(pg)) + 1
        url = str(response.url)
        for p in range(1,pg):
            ul = url + '?pageno=' + str(p)
            yield scrapy.Request(ul, callback=self.parse_common_list)
    # 获取评论信息
    def parse_common_list(self,response): 
        shop_common = ShopCommon()
        selector = scrapy.Selector(response)
        shop_id = response.url.split('/')[-2]
        lis = selector.xpath('//div[@class="comment-list"]/ul/li')
        for li in lis:
            shop_common['_id'] = self.getField(li,'@data-id')
            shop_common['user_name'] = self.getField(li,'div[1]/p[1]/a/text()')
            shop_common['shop_id'] = shop_id
            shop_common['contribution'] = self.getField(li,'div[1]/p[2]/span/@title')
            shop_common['avg_cost'] = self.getField(li,'div[2]/div[1]/span[2]/text()')
            shop_common['score_1'] = self.getField(li,'div[2]/div[1]/div/span[1]/text()')
            shop_common['score_2'] = self.getField(li,'div[2]/div[1]/div/span[2]/text()')
            shop_common['score_3'] = self.getField(li,'div[2]/div[1]/div/span[3]/text()')
            shop_common['content'] = self.getField(li,'div[2]/div[2]/div[1]/text()')  
            shop_common['support_count'] = self.getField(li,'//div[@class="misc-info"]/span[2]/span[1]/a/span[2]/text()')   
            yield shop_common
    