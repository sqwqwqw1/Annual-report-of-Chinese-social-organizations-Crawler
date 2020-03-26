# -*- coding: utf-8 -*-
# @Author: Yaodo
# @Website: https://www.imtrq.com
# @Time: 2020/03/26

# 关于本爬虫
# 本爬虫已经遍历所有报告的列表，但没有将所有的年份纳入处理
# 本爬虫只采集了理事的性别比例，没有采集其他的信息
# 请修改 parse_list 以处理所有列表
# 请修改 parse_年份 以采集定制的信息

import scrapy
import re
from fund.items import FundItem


class FundCrawlerSpider(scrapy.Spider):
    name = 'fund_crawler'
    allowed_domains = ['chinanpo.gov.cn']

    # 请求访问各民政局的首页列表
    def start_requests(self):
        url = 'http://www.chinanpo.gov.cn/bgsindex.html'
        web_list = [('1000001', '中华人民共和国民政部'), ('1100001', '北京市民政局'), ('1200001', '天津市民政局'), ('1300001', '河北省民政厅'), 
                    ('1400001', '山西省民政厅'), ('1500001', '内蒙古自治区'), ('2100001', '辽宁省民政厅'), ('2200001', '吉林省民政厅'), 
                    ('2300001', '黑龙江省民政厅'), ('3100001', '上海市民政局'), ('3200001', '江苏省民政厅'), ('3300001', '浙江省民政厅'), 
                    ('3400001', '安徽省民政厅'), ('3500001', '福建省民政厅'), ('3600001', '江西省民政厅'), ('3700001', '山东省民政厅'), 
                    ('3706001', '青岛市民政厅'), ('4100001', '河南省民政厅'), ('4200001', '湖北省民政厅'), ('4300001', '湖南省民政厅'), 
                    ('4400001', '广东省民政厅'), ('4500001', '广西壮族自治区民政厅'), ('4600001', '海南省民政厅'), ('5000001', '重庆市民政局'), 
                    ('5100001', '四川省民政厅'), ('5200001', '贵州省民政厅'), ('5300001', '云南省民政厅'), ('5400001', '西藏自治区民政厅'), 
                    ('6100001', '陕西省民政厅'), ('6200001', '甘肃省民政厅'), ('6300001', '青海省民政厅'), ('6400001', '宁夏回族自治区民政厅'), 
                    ('6500001', '新疆维吾尔自治区民政厅')]
        for web in web_list:
            websitId = web[0]
            province = web[1]
            form_data = {
                        'websitId': websitId,
                        'page_flag': 'true',
                        'goto_page': 'next',
                        'current_page': '0',
                        }
            yield scrapy.FormRequest(url, formdata=form_data, meta={'province': province}, callback=self.parse_first_page)

    # 从首页列表获取总页数、总条数等信息，发起请求遍历所有列表页
    def parse_first_page(self, response):
        province = response.meta['province']
        url = 'http://www.chinanpo.gov.cn/bgsindex.html'
        if re.search('当前第(.*?)页',response.text):
            page_info = re.search('当前第(.*?)页',response.text).group(1)
            total_pages = int(page_info.split('/')[1])
            websitId = response.xpath('//input[@name="websitId"]/@value').get()
            total_count = response.xpath('//input[@name="total_count"]/@value').get()
            for page in range(1, total_pages+1):
                form_data = { 
                     'websitId': websitId, 
                     'page_flag': 'true', 
                     'goto_page': 'next', 
                     'current_page': str(page), 
                     'total_count': total_count, 
                     'to_page': '' 
                    }
                yield scrapy.FormRequest(url, formdata=form_data, meta={'province': province}, callback=self.parse_list)

    # 处理列表页的每一条报告，根据年份回调不同的解析方法
    def parse_list(self, response):
        province = response.meta['province']
        url = 'http://www.chinanpo.gov.cn/viewbgs.html'
        websitId = response.xpath('//input[@name="websitId"]/@value').get()
        report_list = response.xpath('//table[@class="table-1"]//tr//a')
        for report in report_list:
            name = report.xpath('./text()').get()
            id_list = re.search('\((\d+,\d+)\)',report.xpath('./@href').get()).group(1).split(',')
            report_id = id_list[0]
            dictionid = id_list[1]
            form_data = {
                            'id': report_id,
                            'dictionid': dictionid,
                            'websitId': websitId,
                            'netTypeId': '2',
                            'topid': ''
                        }
            if '2018年' in name: 
                yield scrapy.FormRequest(url, formdata=form_data, meta={'province': province, 'name': name}, callback=self.parse_2018)
            if '2017年' in name: 
                yield scrapy.FormRequest(url, formdata=form_data, meta={'province': province, 'name': name}, callback=self.parse_2017)
            if '2016年' in name: 
                yield scrapy.FormRequest(url, formdata=form_data, meta={'province': province, 'name': name}, callback=self.parse_2016)
            if '2015年' in name: 
                yield scrapy.FormRequest(url, formdata=form_data, meta={'province': province, 'name': name}, callback=self.parse_2015)
            # if '2014年' in name: 
            #     yield scrapy.FormRequest(url, formdata=form_data, meta={'province': province, 'name': name}, callback=self.parse_2014)
            if '2013年' in name: 
                yield scrapy.FormRequest(url, formdata=form_data, meta={'province': province, 'name': name}, callback=self.parse_2013)

    # 分年份处理数据（每一年的格式不一样）
    def parse_2018(self, response):
        province = response.meta['province']
        name = response.meta['name']
        text = re.search('<h3>（二）理事会成员情况</h3>(.*?)<h3>（三）监事情况</h3>', response.text).group(1)
        male_count = text.count('<TD>男</TD>')
        female_count = text.count('<TD>女</TD>')
        item = FundItem(province=province, name=name, male_count=male_count, female_count=female_count)
        yield item


    def parse_2017(self, response):
        province = response.meta['province']
        name = response.meta['name']
        text = re.search('<h3>（二）理事会成员情况</h3>(.*?)<h3>（三）监事情况</h3>', response.text).group(1)
        male_count = text.count('<TD>男</TD>')
        female_count = text.count('<TD>女</TD>')
        item = FundItem(province=province, name=name, male_count=male_count, female_count=female_count)
        yield item

    def parse_2016(self, response):
        province = response.meta['province']
        name = response.meta['name']
        text = re.search('理事会成员情况</STRONG>(.*?)<STRONG>（三）监事情况</STRONG>', response.text).group(1)
        male_count = text.count('男</TD>')
        female_count = text.count('女</TD>')
        item = FundItem(province=province, name=name, male_count=male_count, female_count=female_count)
        yield item

    def parse_2015(self, response):
        province = response.meta['province']
        name = response.meta['name']
        text = re.search('理事会成员情况</STRONG>(.*?)<STRONG>（三）监事情况</STRONG>', response.text).group(1)
        male_count = text.count('男</TD>')
        female_count = text.count('女</TD>')
        item = FundItem(province=province, name=name, male_count=male_count, female_count=female_count)
        yield item

    def parse_2014(self, response):
        pass

    def parse_2013(self, response):
        province = response.meta['province']
        name = response.meta['name']
        text = re.search('理事会成员情况</STRONG>(.*?)<STRONG>（三）监事情况</STRONG>', response.text).group(1)
        male_count = text.count('男</TD>')
        female_count = text.count('女</TD>')
        item = FundItem(province=province, name=name, male_count=male_count, female_count=female_count)
        yield item