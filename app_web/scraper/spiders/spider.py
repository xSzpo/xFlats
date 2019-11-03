import scrapy
import codecs
import json
import helpers
import logging
import re
logger = logging.getLogger(__name__)


class Spider1(scrapy.Spider):

    def __init__(self):
        super().__init__()
        self.pageCounter = 1
        self.mongo_connection = None

    name = "otodom"

    with codecs.open("./scraper/spiders/xhpats.json", "r") as file:
        xpath_json = json.load(file)

    start_urls = xpath_json['otodom']['start_urls']
    list_page_start_xpath = xpath_json['otodom']['list_page_start_xpath']
    list_page_iter_xpaths = xpath_json['otodom']['list_page_iter_xpaths']
    article_page_iter_xpaths = xpath_json['otodom']['article_page_iter_xpaths']

    allowed_domains = ["www.otodom.pl"]

    def parse(self, response):
        for i, offer in enumerate(response.xpath(self.list_page_start_xpath)):
            url = offer.xpath(self.list_page_iter_xpaths['url']).get()
            yield scrapy.Request(url, callback=self.parse_dir_contents)

        # after you crawl each offer in current page go to the next page
        next_page = response.css('li.pager-next a::attr(href)').get()
        if next_page is None and self.pageCounter > 1:
            logger.info("OTODOM: next page, iter {}".format(self.pageCounter))

        if next_page is not None and self.pageCounter <= self.settings['CRAWL_LIST_PAGES']:
            self.pageCounter += 1
            yield response.follow(next_page, callback=self.parse)

    def parse_dir_contents(self, response):

        tmp = {}

        for key in self.article_page_iter_xpaths:
            tmp[key] = response.xpath(self.article_page_iter_xpaths[key]).get()

        tmp['additional_info'] = "|".join(response.xpath(self.article_page_iter_xpaths['additional_info']).getall())
        tmp['description'] = "\n".join(response.xpath(self.article_page_iter_xpaths['description']).getall())
        tmp['download_date'] = helpers.Scraper.current_datetime()
        tmp['geo_coordinates'] = helpers.Geodata.get_geodata_otodom(response.body)
        tmp['url'] = response.url
        tmp['producer_name'] = self.name
        tmp['main_url'] = self.start_urls[0]

        yield tmp


class Spider2(scrapy.Spider):

    def __init__(self):
        super().__init__()
        self.pageCounter = 1
        self.mongo_connection = None

    name = "olx"

    with codecs.open("./scraper/spiders/xhpats.json", "r") as file:
        xpath_json = json.load(file)

    start_urls = xpath_json['olx']['start_urls']
    list_page_url = xpath_json['olx']['url']
    article_page_iter_xpaths = xpath_json['olx']['article_page_iter_xpaths']

    allowed_domains = ["www.olx.pl"]

    def parse(self, response):
        for i, url in enumerate(response.xpath(self.list_page_url).getall()):
            yield scrapy.Request(url, callback=self.parse_dir_contents)

        # after you crawl each offer in current page go to the next page
        next_page = response.css("span.fbold.next.abs.large a::attr(href)").get()
        if next_page is None and self.pageCounter > 1:
            logger.info("OLX: next page, iter {}".format(self.pageCounter))

        if next_page is not None and self.pageCounter <= self.settings['CRAWL_LIST_PAGES']:
            self.pageCounter += 1
            yield response.follow(next_page, callback=self.parse)

    def parse_dir_contents(self, response):

        tmp = {}

        for key in self.article_page_iter_xpaths:
            tmp[key] = response.xpath(self.article_page_iter_xpaths[key]).get()

        tmp['description'] = "\n".join(response.xpath(self.article_page_iter_xpaths['description']).getall())
        tmp['download_date'] = helpers.Scraper.current_datetime()
        tmp['geo_coordinates'] = helpers.Geodata.get_geodata_olx(response.body)
        tmp['url'] = response.url
        tmp['producer_name'] = self.name
        tmp['main_url'] = self.start_urls[0]

        yield tmp


class Spider3(scrapy.Spider):

    def __init__(self):
        super().__init__()
        self.pageCounter = 1
        self.mongo_connection = None

    name = "gratka"

    with codecs.open("./scraper/spiders/xhpats.json", "r") as file:
        xpath_json = json.load(file)

    start_urls = xpath_json['gratka']['start_urls']
    list_page_url = xpath_json['gratka']['url']
    article_page_iter_xpaths = xpath_json['gratka']['article_page_iter_xpaths']

    #allowed_domains = ["www.gratka.pl"]

    def parse(self, response):

        for i, url in enumerate(response.xpath(self.list_page_url).getall()):
            yield scrapy.Request(url, callback=self.parse_dir_contents)

        # after you crawl each offer in current page go to the next page
        next_page = response.url+"?page={}".format(self.pageCounter+1)
        if next_page is None and self.pageCounter > 1:
            logger.info("GRATKA: next page, iter {}".format(self.pageCounter))

        if next_page is not None and self.pageCounter <= self.settings['CRAWL_LIST_PAGES']:
            self.pageCounter += 1
            yield response.follow(next_page, callback=self.parse)

    def parse_dir_contents(self, response):

        tmp = {}

        for key in self.article_page_iter_xpaths:
            tmp[key] = response.xpath(self.article_page_iter_xpaths[key]).get()

        tmp['tracking_id'] = re.findall(r"\d+", response.url.split("/")[-1])[0]
        tmp['location'] = ", ".join(response.xpath(self.article_page_iter_xpaths['location']).getall())
        tmp['description'] = "\n".join(response.xpath(self.article_page_iter_xpaths['description']).getall())
        tmp['download_date'] = helpers.Scraper.current_datetime()
        tmp['geo_coordinates'] = helpers.Geodata.get_geodata_gratka(response.body)
        tmp['url'] = response.url
        tmp['producer_name'] = self.name
        tmp['main_url'] = self.start_urls[0]

        yield tmp