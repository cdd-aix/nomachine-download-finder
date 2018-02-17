# -*- coding: utf-8 -*-
import re
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor


class DownloadsSpider(CrawlSpider):
    name = 'downloads'
    allowed_domains = ['www.nomachine.com']
    start_urls = [
        'https://www.nomachine.com/download',
    ]

    rules = (
        Rule(
            LinkExtractor(
                allow=(re.compile('/download/'),),
            ),
            callback='parse_item',
            follow=True
        ),
    )

    def parse_item(self, response):
        print('Processing..' + response.url)
