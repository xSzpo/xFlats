import scrapy
import codecs
import json
import logging
import re
import zlib
import base64
from dateutil.parser import parse
from helpers.base import Scraper
from helpers.base import Geodata

logger = logging.getLogger(__name__)


class Spider1(scrapy.Spider):

    def __init__(self):
        super().__init__()
        self.pageCounter = 1
        self.mongo_connection = None

    name = "otodom"

    xpath_json = None

    with codecs.open("./scraper/spiders/xhpats.json", "r") as file:
        xpath_json = json.load(file)

    start_urls = xpath_json['otodom']['start_urls']
    list_page_start_xpath = xpath_json['otodom']['list_page_start_xpath']
    list_page_iter_xpaths = xpath_json['otodom']['list_page_iter_xpaths']
    next_page_css = xpath_json['otodom']['next_page_css']
    article_page_iter_xpaths = xpath_json['otodom']['article_page_iter_xpaths']

    allowed_domains = ["www.otodom.pl"]

    def parse(self, response):
        for i, offer in enumerate(response.xpath(self.list_page_start_xpath)):
            url = offer.xpath(self.list_page_iter_xpaths['url']).get()
            yield scrapy.Request(url, callback=self.parse_dir_contents)

        # after you crawl each offer in current page go to the next page
        next_page = response.css(self.next_page_css).get()

        if next_page is not None and self.pageCounter < \
                self.settings['CRAWL_LIST_PAGES']:
            if next_page is not None and self.pageCounter >= 1:
                logger.info("OTODOM: next page, iter {}, url: {}".format(
                    self.pageCounter, next_page))
            self.pageCounter += 1
            yield response.follow(next_page, callback=self.parse)

    def parse_dir_contents(self, response):

        tmp = {}

        for key in self.article_page_iter_xpaths:
            tmp[key] = response.xpath(self.article_page_iter_xpaths[key]).get()

        tmp['additional_info'] = " ".join(response.xpath(
            self.article_page_iter_xpaths['additional_info']).getall())
        tmp['description'] = "\n".join(response.xpath(
            self.article_page_iter_xpaths['description']).getall())
        tmp['geo_coordinates'] = Geodata.get_geodata_otodom(response.body)
        tmp['date_created'], tmp['date_modified'] = Scraper.\
            get_createdate_from_otodom(response.body)
        tmp['url'] = response.url
        tmp['producer_name'] = self.name
        tmp['main_url'] = self.start_urls[0]
        # zlib.decompress(base64.b64decode(x))
        tmp['body'] = base64.b64encode(zlib.compress(response.body)).decode()

        yield tmp


class Spider2(scrapy.Spider):

    def __init__(self):
        super().__init__()
        self.pageCounter = 1
        self.mongo_connection = None

    name = "olx"

    xpath_json = None

    with codecs.open("./scraper/spiders/xhpats.json", "r") as file:
        xpath_json = json.load(file)

    start_urls = xpath_json['olx']['start_urls']
    list_page_url = xpath_json['olx']['url']
    next_page_css = xpath_json['olx']['next_page_css']
    article_page_iter_xpaths = xpath_json['olx']['article_page_iter_xpaths']

    allowed_domains = ["www.olx.pl"]

    def parse(self, response):
        for i, url in enumerate(response.xpath(self.list_page_url).getall()):
            yield scrapy.Request(url, callback=self.parse_dir_contents)

        # after you crawl each offer in current page go to the next page
        next_page = response.css(self.next_page_css).get()

        if next_page is not None and self.pageCounter < \
                self.settings['CRAWL_LIST_PAGES']:
            if next_page is not None and self.pageCounter >= 1:
                logger.info("OLX: next page, iter {}, url: {}".format(
                    self.pageCounter, next_page))
            self.pageCounter += 1
            yield response.follow(next_page, callback=self.parse)

    def parse_dir_contents(self, response):

        tmp = {}

        for key in self.article_page_iter_xpaths:
            tmp[key] = response.xpath(self.article_page_iter_xpaths[key]).get()

        tmp['additional_info'] = re.sub(r"\W+", " ", " ".join(response.xpath(
            self.article_page_iter_xpaths['additional_info']).getall()).strip())
        tmp['description'] = "\n".join(response.xpath(
            self.article_page_iter_xpaths['description']).getall())
        tmp['geo_coordinates'] = Geodata.get_geodata_olx(response.body)
        tmp['date_created'] = Scraper.\
            get_createdate_polish_months(tmp['date_created'])
        tmp['date_modified'] = None
        tmp['url'] = response.url
        tmp['producer_name'] = self.name
        tmp['main_url'] = self.start_urls[0]

        tmp['number_of_floors'] = Scraper.searchregex(
            tmp['description'].lower(), r'\d+\W+pi.tr(?:ow|a)', group=0)

        reg = (r"(oddan\w+|inwestyc\w+|odbi.r\w+|rok\s+budow\w+|blok\w+|" +
               r"dom\w+|kamienic\w+|budyn\w+)[\w\S ]*(1[89]\d\d|20\d\d)")
        tmp['year_of_building'] = Scraper.searchregex(
            tmp['description'].lower(), reg, group=2)

        #zlib.decompress(base64.b64decode(x))
        tmp['body'] = base64.b64encode(zlib.compress(response.body)).decode()

        tmp['building_material'] = None

        yield tmp


class Spider3(scrapy.Spider):

    def __init__(self):
        super().__init__()
        self.pageCounter = 1
        self.mongo_connection = None

    name = "gratka"

    xpath_json = None

    with codecs.open("./scraper/spiders/xhpats.json", "r") as file:
        xpath_json = json.load(file)

    start_urls = xpath_json['gratka']['start_urls']
    list_page_url = xpath_json['gratka']['url']
    list_date_modified = xpath_json['gratka']['main_page_date_modified']
    article_page_iter_xpaths = xpath_json['gratka']['article_page_iter_xpaths']

    allowed_domains = ["www.gratka.pl"]

    def parse(self, response):

        urls = response.xpath(self.list_page_url).getall()
        dates_upd = response.xpath(self.list_date_modified).getall()

        for i, url in enumerate([i for i in zip(urls, dates_upd)]):

            yield scrapy.Request(url[0], callback=self.parse_dir_contents,
                                 cb_kwargs=dict(date_modified=url[1]))

        # after you crawl each offer in current page go to the next page
        next_page = response.url.split("?")[0] + \
            "?page={}".format(self.pageCounter+1)

        if next_page is not None and self.pageCounter < \
                self.settings['CRAWL_LIST_PAGES']:
            if next_page is not None and self.pageCounter >= 1:
                logger.info("GRATKA: next page, iter {}, url: {}".format(
                    self.pageCounter, next_page))
            self.pageCounter += 1
            yield response.follow(next_page, callback=self.parse)

    def parse_dir_contents(self, response, date_modified):

        tmp = {}

        for key in self.article_page_iter_xpaths:
            tmp[key] = response.xpath(self.article_page_iter_xpaths[key]).get()

        tmp['tracking_id'] = re.findall(r"\d+", response.url.split("/")[-1])[0]
        tmp['location'] = ", ".join(response.xpath(
            self.article_page_iter_xpaths['location']).getall())
        tmp['description'] = "\n".join(response.xpath(
            self.article_page_iter_xpaths['description']).getall())
        tmp['additional_info'] = re.sub(r"\W+", " ", " ".join(response.xpath(
            self.article_page_iter_xpaths['additional_info']).getall()).strip())
        tmp['geo_coordinates'] = Geodata.get_geodata_gratka(response.body)
        tmp['market'] = Scraper.searchregex(
            response.body.decode(), r"('rynek', .(\w+).)", group=2)
        tmp['offeror'] = None

        tmp['date_created'] = None
        tmp['date_modified'] = Scraper.searchregex(
            date_modified, r"20\d\d-[01]\d-\d\d", group=0, func=parse)

        tmp['url'] = response.url
        tmp['producer_name'] = self.name
        tmp['main_url'] = self.start_urls[0]

        #zlib.decompress(base64.b64decode(x))
        tmp['body'] = base64.b64encode(zlib.compress(response.body)).decode()

        yield tmp


class Spider4(scrapy.Spider):

    def __init__(self):
        super().__init__()
        self.pageCounter = 1
        self.mongo_connection = None

    name = "morizon"

    xpath_json = None

    with codecs.open("./scraper/spiders/xhpats.json", "r") as file:
        xpath_json = json.load(file)

    start_urls = xpath_json['morizon']['start_urls']
    list_page_url = xpath_json['morizon']['url']
    next_page = xpath_json['morizon']['next_page']
    article_page_iter_xpaths = xpath_json['morizon']['article_page_iter_xpaths']

    allowed_domains = ["www.morizon.pl"]

    def parse(self, response):

        for i, url in enumerate(response.xpath(self.list_page_url).getall()):
            yield scrapy.Request(url, callback=self.parse_dir_contents)

        # after you crawl each offer in current page go to the next page
        next_page = response.xpath(self.next_page).get()

        if next_page is not None and self.pageCounter < \
                self.settings['CRAWL_LIST_PAGES']:
            if next_page is not None and self.pageCounter >= 1:
                logger.info("MORIZON: next page, iter {}, url: {}".format(
                    self.pageCounter, next_page))
            self.pageCounter += 1
            yield response.follow(next_page, callback=self.parse)

    def parse_dir_contents(self, response):

        tmp = {}

        for key in self.article_page_iter_xpaths:
            tmp[key] = response.xpath(self.article_page_iter_xpaths[key]).get()

        tmp['name'] = " ".join(response.xpath(
            self.article_page_iter_xpaths['name']).getall())
        tmp['location'] = " ".join(response.xpath(
            self.article_page_iter_xpaths['location']).getall())
        tmp['geo_coordinates'] = {
            "latitude": tmp['data_lat'], "longitude": tmp['data_lon']}
        tmp['tracking_id'] = re.findall(r"\d+", response.url.split("-")[-1])[0]
        tmp['description'] = "\n".join(response.xpath(
            self.article_page_iter_xpaths['description']).getall())
        tmp['url'] = response.url
        tmp['producer_name'] = self.name
        tmp['main_url'] = self.start_urls[0]

        tmp['offeror'] = Scraper.searchregex(response.body.decode(),
                                             r"oferent=(\w+);", group=1)
        tmp['floor'] = Scraper.searchregex(tmp['floor'], r"(\d+).+", group=1)

        tmp['date_created'] = Scraper.searchregex(
            tmp['date_created'], r"\d\d-[01]\d-20\d\d", group=0, func=parse)

        tmp['date_modified'] = Scraper.\
            get_createdate_polish_months(tmp['date_modified'])

        #zlib.decompress(base64.b64decode(x))
        tmp['body'] = base64.b64encode(zlib.compress(response.body)).decode()

        yield tmp
