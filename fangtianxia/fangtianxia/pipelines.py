# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exporters import JsonLinesItemExporter
from fangtianxia.items import FangtianxiaFirstItem
from fangtianxia.items import FangtianxiaSecondItem

class FangtianxiaPipeline(object):
    def __init__(self):
        # 用两个文件和两个写入器来写入信息
        fp1 = open('fang1.json', 'wb')
        fp2 = open('fang2.json', 'wb')
        self.exporter1 = JsonLinesItemExporter(fp1, ensure_ascii=False, encoding='utf-8')
        self.exporter2 = JsonLinesItemExporter(fp2, ensure_ascii=False, encoding='utf-8')

    def process_item(self, item, spider):
        # 用isinstance对item作判断，看具体要保存到哪个文件
        if isinstance(item, FangtianxiaFirstItem):
            self.exporter1.export_item(item)
        if isinstance(item, FangtianxiaSecondItem):
            self.exporter2.export_item(item)
        return item


