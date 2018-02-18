# -*- coding: utf-8 -*-
import re
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy_splash import SplashRequest

class DownloadItem(scrapy.Item):
    title = scrapy.Field()
    version = scrapy.Field()
    package_type = scrapy.Field()
    supported_os = scrapy.Field()
    md5 = scrapy.Field()
    url = scrapy.Field()
    transform = {
        'Package type:': 'package_type',
        'MD5 signature:': 'md5',
        'For:': 'supported_os',
        'Version:': 'version',
    }

class DownloadsSpider(CrawlSpider):
    name = 'downloads'
    allowed_domains = ['www.nomachine.com']
    start_urls = [
        'https://www.nomachine.com/download',
        'https://www.nomachine.com/download-enterprise'
    ]

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse_item,
                                endpoint='render.html',
                                args={'wait': 10},
            )

    rules = (
        Rule(
            LinkExtractor(allow=(re.compile('/download/.*&id='))),
            callback='parse_item',
            follow=True
        ),
    )
    download='//%s[contains(@onclick, "/download.nomachine.com/")]/@onclick'
    download_a = download % ('a',)
    download_div = download % ('div',)
    link='//%s[contains(@onclick, "&id=")]/@onclick'
    link_a = link % ('a', )
    link_div = link % ('div',)

    def parse_item(self, response):
        print('Processing ' + response.url)
        # item_links = response.css('.linux_sub > .detailsLink::attr(onclick)').extract()
        download_onclicks = response.xpath(self.download_a).extract()
        download_onclicks += response.xpath(self.download_div).extract()
        download_links = [a.split("'")[1] for a in download_onclicks]
        for item in self.parse_downloads(response, download_links):
            yield item

        item_onclicks = response.xpath(self.link_a).extract()
        item_onclicks += response.xpath(self.link_div).extract()
        item_links = [a.split("'")[1] for a in item_onclicks]
        # print(item_links)
        # print(response.headers)
        for a in item_links:
            yield response.follow(a, callback=self.parse_item)

    def parse_downloads(self, response, downloads):
        if downloads:
            title = response.xpath('//h1[contains(@id, "titleH2")]/text()').extract()[0].strip()
            attrs = dict(
                zip(
                    response.xpath('//div[@class="first_cell dis_cell"]/p/text()').extract(),
                    response.xpath('//div[@class="sec_cell dis_cell"]/p/text()').extract()
                )
            )
        for url in downloads:
            item = DownloadItem(title=title, url=url)
            item.update((item.transform[k],v) for k,v in attrs.items() if item.transform.get(k))
            yield item
