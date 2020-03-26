# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FundItem(scrapy.Item):
    _id = scrapy.Field()
    province = scrapy.Field()
    name = scrapy.Field()
    male_count = scrapy.Field()
    female_count = scrapy.Field()