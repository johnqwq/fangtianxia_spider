# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class FangtianxiaItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

# 因为有新房和二手房两类信息，因此创建两个类分别保存
class FangtianxiaFirstItem(scrapy.Item):
    province = scrapy.Field()
    city = scrapy.Field()
    name = scrapy.Field()
    rooms = scrapy.Field()
    area = scrapy.Field()
    site = scrapy.Field()
    sale = scrapy.Field()
    condition = scrapy.Field()
    price = scrapy.Field()
    house_url = scrapy.Field()

class FangtianxiaSecondItem(scrapy.Item):
    province = scrapy.Field()
    city = scrapy.Field()
    title = scrapy.Field()
    condition = scrapy.Field()
    community = scrapy.Field()
    site = scrapy.Field()
    label = scrapy.Field()
    price = scrapy.Field()
    unit = scrapy.Field()
    house_url = scrapy.Field()


