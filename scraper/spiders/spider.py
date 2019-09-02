import scrapy
import helpers
import re
import logging
import datetime
import json
import bson
from bson.json_util import dumps
logger = logging.getLogger(__name__)


def timeit(method):
    def timed(*args, **kw):
        start_time = datetime.datetime.now()
        result = method(*args, **kw)
        time_elapsed = datetime.datetime.now() - start_time
        logger.info('Function "{}" - time elapsed (hh:mm:ss.ms) {}'.format(
            method.__name__, time_elapsed))
        return result
    return timed


class OtodomListSpider(scrapy.Spider):
    """
     :param max_pages: set max number of pages to crawl
     :param pageCounter: technical field to count how many (next) pages hac been already crawled
    """

    def __init__(self):
        # super().__init__()
        self.pageCounter = 0

    name = "otodom"

    start_urls = [
        'https://www.otodom.pl/sprzedaz/mieszkanie/warszawa',
    ]

    start_xpath = "//div[@class='col-md-content section-listing__row-content']//article[starts-with(@class,'offer-item ad')]"
    iter_xpaths_list = {
        "flat_size":"div[@class='offer-item-details']/ul[starts-with(@class,'params')]/li[@class='hidden-xs offer-item-area']/text()",
        "gallery":"figure/@data-quick-gallery",
        "img_cover_title":"figure/a/span[@class='img-cover lazy']/@title",
        "issued_by":"div[@class='offer-item-details-bottom']/ul[@class='params-small clearfix hidden-xs']/li[starts-with(@class, 'pull')]/text()",
        "location": "div[@class='offer-item-details']/header/p[@class='text-nowrap']/text()",
        "offer_id": "@data-item-id",
        "offer_title": "div[@class='offer-item-details']/header/h3/a//span[@class='offer-item-title']/text()",
        "price": "div[@class='offer-item-details']/ul[starts-with(@class,'params')]/li[@class='offer-item-price']/text()",
        "price_per_square": "div[@class='offer-item-details']/ul[starts-with(@class,'params')]/li[@class='hidden-xs offer-item-price-per-m']/text()",
        "rooms": "div[@class='offer-item-details']/ul[starts-with(@class,'params')]/li[@class='offer-item-rooms hidden-xs']/text()",
        "tracking_id": "@data-tracking-id",
        "type": "@data-featured-name",
        "url":"@data-url"
    }

    iter_xpaths_one_article = {
        'offer_type': '//div[contains(@class,"MobileLabel-className")]/text()',
        'name': '//h1[contains(@class,"AdHeader-className")]/text()',
        'location': '//a[contains(@class,"AdPage-contentStyle")]/text()',
        'price': '//div[@class="css-1hbj9if-AdHeader"]//text()[position()=1]',
        'price_m2': '//div[@class="css-cu1lls-AdHeader"]//text()',
        'flat_size': "//div[contains(@class,'AdOverview-className')]//li[contains(text(),'Powierzchnia')]//strong//text()",
        'rooms': "//div[contains(@class,'AdOverview-className')]//li[contains(text(),'Liczba pokoi')]//strong//text()",
        'market': "//div[contains(@class,'AdOverview-className')]//li[contains(text(),'Rynek')]//strong//text()",
        'building_type': "//div[contains(@class,'AdOverview-className')]//li[contains(text(),'Rodzaj zabudowy')]//strong//text()",
        'floor': "//div[contains(@class,'AdOverview-className')]//li[contains(text(),'Piętro')]//strong//text()",
        'number_of_floors': "//div[contains(@class,'AdOverview-className')]//li[contains(text(),'Liczba pięter')]//strong//text()",
        'building_material': "//div[contains(@class,'AdOverview-className')]//li[contains(text(),'Materiał budynku')]//strong//text()",
        'widows_type': "//div[contains(@class,'AdOverview-className')]//li[contains(text(),'Okna')]//strong//text()",
        'heating_type': "//div[contains(@class,'AdOverview-className')]//li[contains(text(),'Ogrzewanie')]//strong//text()",
        'year_of_building': "//div[contains(@class,'AdOverview-className')]//li[contains(text(),'Rok budowy')]//strong//text()",
        'finishing_stage': "//div[contains(@class,'AdOverview-className')]//li[contains(text(),'Stan wykończenia')]//strong//text()",
        'rent_price': "//div[contains(@class,'AdOverview-className')]//li[contains(text(),'Czynsz')]//strong//text()",
        'property_form': "//div[contains(@class,'AdOverview-className')]//li[contains(text(),'Forma własności')]//strong//text()",
        'available_from': "//div[contains(@class,'AdOverview-className')]//li[contains(text(),'Dostępne od')]//strong//text()",
        'description': '//*[section]//div[contains(@class, "AdDescription-className")]//text()',
        'additional_info': "//div[contains(@class, 'AdFeatures-className')]//text()",
        'tracking_id': 'substring-after(//div[@class="css-97h3nz-AdSignature-className"]/div[position()=1]//text()[following-sibling::br],":")',
        'agency_tracking_id': 'substring-after(//div[@class="css-97h3nz-AdSignature-className"]/div[position()=1]//text()[preceding-sibling::br],":")',
        'add_rel_date': 'substring-after(//div[@class="css-97h3nz-AdSignature-className"]/div[position()=2]//text()[following-sibling::br],":")',
        'update_rel_date': 'substring-after(//div[@class="css-97h3nz-AdSignature-className"]/div[position()=2]//text()[preceding-sibling::br],":")',
    }

    def parse(self, response):
        """

        :param response:
        :return:
        """
        self.pageCounter += 1

        file_list_aws_bucket = helpers.scraper.list_bucket(self.settings['BUCKET_NAME'],
                                                self.settings['BUCKET_PREFIX_BSON'])
        logger.info(file_list_aws_bucket[:2])

        # do something for every offer found in offers list
        for offer in response.xpath(self.start_xpath):
            tmp = {}

            for key in self.iter_xpaths_list:
                tmp[key] = offer.xpath(self.iter_xpaths_list[key]).get()
            tmp['url_offer_list'] = response.url
            tmp['producer_name'] = self.name
            tmp["main_url"] = "otodom.pl"

            request = scrapy.Request(tmp['url'], callback=self.parse_one_article)
            request.meta['data'] = tmp

            price_str = ''.join([i for i in re.sub("[ ]","",tmp["price"]) if i.isdigit()])
            file_name = tmp["tracking_id"]+"_"+price_str+".bson"

            if file_name not in file_list_aws_bucket:
                logger.info("File {} has NOT been in bucket -> download".format(file_name))
                request.meta['file_name'] = file_name
                yield request
            else:
                logger.info('File {} HAS been in bucket -> NO NOT download'.format(file_name))

        # after you crawl each offer in current page go to the next page
        next_page = response.css('li.pager-next a::attr(href)').get()

        if next_page is not None and self.pageCounter < self.settings['MAX_PAGES']:
            yield response.follow(next_page, callback=self.parse)

    def parse_one_article(self, response):

        tmp = response.meta['data']

        for key in self.iter_xpaths_one_article:
            tmp[key] = response.xpath(self.iter_xpaths_one_article[key]).get()
        tmp['download_date'] = helpers.scraper.current_timestamp()

        tmp['geo_coordinates'], tmp['geo_address_text'], tmp['geo_address_coordin'] = helpers.scraper.get_geodata(
            response.body)

        tmp['img_gallery_strimg'] = [helpers.scraper.imgurl2str(i['photo']) for i in json.loads(tmp['gallery'])[:1]]

        data_b_ = dumps(bson.BSON.encode(tmp))

        helpers.scraper.write_S3_bucket(data_b_, response.meta['file_name'],
                                              self.settings['BUCKET_NAME'], prefix=self.settings['BUCKET_PREFIX_BSON'])
        yield {"file_name": response.meta['file_name'], "statusCode": 200}
