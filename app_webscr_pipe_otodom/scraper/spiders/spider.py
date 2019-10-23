import scrapy
import codecs
import json

import logging
logger = logging.getLogger(__name__)


class QuotesSpider(scrapy.Spider):

    def __init__(self):
        super().__init__()
        self.pageCounter = 0

    name = "otodom"

    with codecs.open("./scraper/spiders/xhpats.json", "r") as file:
        xpath_json = json.load(file)

    start_urls = xpath_json['start_urls']
    list_page_start_xpath = xpath_json['list_page_start_xpath']
    list_page_iter_xpaths = xpath_json['list_page_iter_xpaths']

    def parse(self, response):

        for offer in response.xpath(self.list_page_start_xpath):
            tmp = {}

            for key in self.list_page_iter_xpaths:
                tmp[key] = offer.xpath(self.list_page_iter_xpaths[key]).get()

            tmp['url_offer_list'] = response.url
            tmp['producer_name'] = self.name
            tmp["main_url"] = "otodom.pl"

            yield tmp

        # after you crawl each offer in current page go to the next page
        next_page = response.css('li.pager-next a::attr(href)').get()

        self.pageCounter += 1
        if next_page is not None and self.pageCounter <= self.settings['CRAWL_PAGES']:

            yield response.follow(next_page, callback=self.parse)
