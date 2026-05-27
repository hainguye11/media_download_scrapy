# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MediaDownloadScrapyItem(scrapy.Item):
    file_urls = scrapy.Field()
    files = scrapy.Field()
    thumbnail_urls = scrapy.Field()
    csv_base = scrapy.Field()
    source_row = scrapy.Field()
