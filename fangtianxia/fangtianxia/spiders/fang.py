# -*- coding: utf-8 -*-
import scrapy
from fangtianxia.items import FangtianxiaFirstItem
from fangtianxia.items import FangtianxiaSecondItem

"""
房天下爬虫练习逻辑链：
1.获取所有省份城市及城市链接
2.修改城市链接为对应房子信息链接并前往爬取
3.items创建不同类分别存放新房信息及二手房信息
4.pipeline接收item并分开写入到json文件中
"""

"""
以上就是一台主机的爬虫工作，如果要用redis作分布式爬虫，则需另外配置、设置一些东西
具体教程可以参考视频或者网上信息，这里大致总结一下思路
1.下载redis、scrapy-redis等
2.修改一些配置文件信息和爬虫文件的一些代码
3.加入说明文件并打包
4.另一台机器（windows或Linux）解压并根据说明文件下载安装好各种包
5.redis服务器（总接口，存储的服务器或主机）开始运行
5.另一台机器在命令控制台中切换到爬虫主文件夹下启动爬虫，等待服务器指令
6.redis服务器切换到命令行输入位置并输入总的开始链接
7.所有在等待的机器都会被启动
"""

"""
一些经验：
1.xpath小心/text()和get()的搭配坑，如果不是一整个的信息容易获取为空
2.某些广告可能会混杂在房子信息中，记得剔除
3.某些时候取某一项多了一些其他内容而网页里又没有，可能是对应那条信息该项为空而其他信息代替了它
4./div/text()能取到同级div下的文字，但如果靠后的div还有嵌套则取不到并且可能会多出杂项
5.列表信息存在杂项替换后元素可能为空，记得清除该元素。一个元素被返回成列表也记得取出
6.多观察网站链接可以大致发现规律，但可能会出现个别网页的链接比较独特，需要单独处理
7.善于使用浏览器上的xpath插件
8.请求之间传递信息可以用自设属性或者meta
9.if a 和 if a.b 的区别在于，a如果没有b属性会直接报错（存疑）
10.scrapy会帮忙补全链接，但是太短或者没有特殊标识的链接可能不行，此时最好手动补全
"""

class FangSpider(scrapy.Spider):
    name = 'fang'
    allowed_domains = ['fang.com']
    # 房天下全国各城市的列表页面
    start_urls = ['https://www.fang.com/SoufunFamily.htm']

    # 获取所有省份城市及城市链接
    def parse(self, response):
        # 城市集合
        trs = response.xpath('//div[@class="outCont"]//tr')
        province = None
        # 一行行省份+城市的集合
        for tr in trs:
            # 省份
            p = tr.xpath('./td[2]//text()').get().strip()
            # 因为是大部分是两行一个省份，因此第二行获取不到省份则默认取上一行的（这个方法挺妙的）
            if p:
                province = p
            # 一行城市名及链接的集合
            td = tr.xpath('./td[last()]/a')
            for a in td:
                # 城市名
                city = a.xpath('./text()').get()
                # 城市链接
                city_url = a.xpath('./@href').get()

                # 将链接重新裁剪替换成去往新房及二手房的链接（房天下的网址的规律是这样的）
                city_url_first_hand = city_url.replace('fang.com/', 'newhouse.fang.com/house/s/')
                city_url_second_hand = city_url.replace('fang.com/', 'esf.fang.com/')
                # 北京城市的住房信息网址比较独特，是不带上城市名的，因而要单独处理
                if 'bj.' in city_url_first_hand:
                    city_url_first_hand = city_url_first_hand.replace('bj.', '')
                    city_url_second_hand = city_url_second_hand.replace('bj.', '')



                # 处理好各城市住房信息网址后返回到调度器中等待处理，因为要记录省份及城市信息，所以用meta传递一个信息元组
                yield scrapy.Request(url=city_url_first_hand, callback=self.parse_house_first, meta={'info': (province, city)})
                yield scrapy.Request(url=city_url_second_hand, callback=self.parse_house_second, meta={'info': (province, city)})
                # 过了澳门后香港台湾等海外地区网址链接规律就不一样了，因此向外查找
                # 这里有个疑问是输出的信息大多在安徽浙江等，可是开头是直辖市那行，不知道是调度的问题还是有什么bug导致直辖市那行返回请求失败，待解决
                if '澳门' == city:
                    return

    # 城市的新房信息筛选
    def parse_house_first(self, response):
        province, city = response.meta['info']
        print(province,city)
        return

        # 各个房区信息的集合（只是大致信息那个页面，不是具体信息）
        divs = response.xpath('//div[@class="nlc_details"]')
        for div in divs:
            # 小区名字
            name = div.xpath('.//div[@class="nlcd_name"]/a/text()').get().strip()
            # 几居室
            rooms = ' | '.join(div.xpath('.//div[@class="house_type clearfix"]/a/text()').extract())
            # 面积
            area = list(map(lambda x: x.replace('/', '').replace('－', '').strip(), div.xpath('.//div[@class="house_type clearfix"]/text()').extract()))
            # 有时处理完列表里面还会有空字符串元素，须去除
            while '' in area:
                area.remove('')
            # 有时候几居室那项不存在的话会取错面积这一项，然后面积就取不到了，因此作个判断，几居室不存在的话则让两项内容互换
            if not area:
                area = rooms
                rooms = ''
            else:
                # 上面的面积取的是一个列表且有大量无关字符，去掉后从列表中去除内容
                area = area[0]
            # 地址
            site = div.xpath('.//div[@class="address"]/a/@title').get()
            # 在售or待售
            sale = div.xpath('.//div[@class="fangyuan"]/span/text()').get()
            # 房子情况
            # 很多杂项，去除后去掉列表空字符串再用|连接
            condition = list(map(lambda x: x.replace('∨', '').strip(), div.xpath('.//div[@class="fangyuan"]/a//text()').extract()))
            while '' in condition:
                condition.remove('')
            condition = ' | '.join(condition)
            # 价格
            price = list(map(lambda x: x.strip(), div.xpath('.//div[@class="nhouse_price"]//text()').extract()))
            price = ''.join(price)
            # 房子具体信息链接
            house_url = response.urljoin(div.xpath('.//div[@class="nlcd_name"]/a/@href').get())

            # 新房和二手房的item是不一样的，分别创建类和实例
            item = FangtianxiaFirstItem(province=province, city=city, name=name, rooms=rooms, area=area, site=site, sale=sale, condition=condition, price=price, house_url=house_url)

            yield item

        # 这里和二手房的写法不一样，但是是必要的：这里以下个链接存在与否作为判断条件，如果不存在是不能作网址拼接的，而下面二手房筛选以别的内容作为判断条件，确定有下一页链接才筛选，因此可以一并完成网址拼接
        next_url = response.xpath('//a[@class="next"]/@href').get()
        if next_url:
            # 继续爬取下一页
            yield scrapy.Request(url=response.urljoin(next_url), callback=self.parse_house_first, meta={'info': (province, city)})

        pass

    # 城市的二手房信息筛选
    def parse_house_second(self, response):
        province, city = response.meta['info']
        print(province,city)
        return

        dls = response.xpath('//div[@class="shop_list shop_list_4"]/dl[@id]')
        for dl in dls:
            # 二手房标题
            title = dl.xpath('.//span[@class="tit_shop"]/text()').get().strip()
            # 房子情况
            condition = list(map(lambda x: x.strip(), dl.xpath('.//p[@class="tel_shop"]//text()').extract()))
            condition = ' '.join(condition)
            # 小区
            community = dl.xpath('.//p[@class="add_shop"]/a/@title').get()
            # 位置
            site = dl.xpath('.//p[@class="add_shop"]/span/text()').get()
            # 标签
            label = ' | '.join(dl.xpath('.//p[@class="clearfix label"]/span/text()').extract())
            # 价格
            price = ''.join(dl.xpath('.//dd[@class="price_right"]/span[1]//text()').extract())
            # 单价
            unit = dl.xpath('.//dd[@class="price_right"]/span[2]/text()').get()
            # 房子具体信息链接
            house_url = response.urljoin(dl.xpath('.//span[@class="tit_shop"]/../@href').get())

            # 二手房item
            item = FangtianxiaSecondItem(province=province, city=city, title=title, condition=condition, community=community, site=site, label=label, price=price, unit=unit, house_url=house_url)

            yield item

        # 如果对应的位置有下一页链接则前往，否则城市该内容爬取完毕
        if response.xpath('//div[@class="page_al"]/p[last()-2]/a/text()').get() != '下一页':
            return
        next_url = response.urljoin(response.xpath('//div[@class="page_al"]/p[last()-2]/a/@href').get())
        yield scrapy.Request(url=next_url, callback=self.parse_house_second, meta={'info': (province, city)})

