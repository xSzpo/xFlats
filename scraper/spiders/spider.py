import scrapy
from scrapy.exceptions import CloseSpider
import helpers
import re
import logging
import datetime
import json
import bson
from bson.json_util import dumps
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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
        'offer_type': '//div[contains(@class,"css-7hnk9y")]/text()',
        'name': '//h1[contains(@class,"css-18igut2")]/text()',
        'location': '//a[contains(@class,"css-1way1d2-En")]/text()',
        'price': '//div[contains(@class,"css-1vr19r7")]/text()',
        'price_m2': '//div[contains(@class,"css-18q4l99")]/text()',
        'flat_size': "//div[contains(@class,'css-1ci0qpi')]//li[contains(text(),'Powierzchnia')]//strong//text()",
        'rooms': "//div[contains(@class,'css-1ci0qpi')]//li[contains(text(),'Liczba pokoi')]//strong//text()",
        'market': "//div[contains(@class,'css-1ci0qpi')]//li[contains(text(),'Rynek')]//strong//text()",
        'building_type': "//div[contains(@class,'css-1ci0qpi')]//li[contains(text(),'Rodzaj zabudowy')]//strong//text()",
        'floor': "//div[contains(@class,'css-1ci0qpi')]//li[contains(text(),'Piętro')]//strong//text()",
        'number_of_floors': "//div[contains(@class,'css-1ci0qpi')]//li[contains(text(),'Liczba pięter')]//strong//text()",
        'building_material': "//div[contains(@class,'css-1ci0qpi')]//li[contains(text(),'Materiał budynku')]//strong//text()",
        'widows_type': "//div[contains(@class,'css-1ci0qpi')]//li[contains(text(),'Okna')]//strong//text()",
        'heating_type': "//div[contains(@class,'css-1ci0qpi')]//li[contains(text(),'Ogrzewanie')]//strong//text()",
        'year_of_building': "//div[contains(@class,'css-1ci0qpi')]//li[contains(text(),'Rok budowy')]//strong//text()",
        'finishing_stage': "//div[contains(@class,'css-1ci0qpi')]//li[contains(text(),'Stan wykończenia')]//strong//text()",
        'rent_price': "//div[contains(@class,'css-1ci0qpi')]//li[contains(text(),'Czynsz')]//strong//text()",
        'property_form': "//div[contains(@class,'css-1ci0qpi')]//li[contains(text(),'Forma własności')]//strong//text()",
        'available_from': "//div[contains(@class,'css-1ci0qpi')]//li[contains(text(),'Dostępne od')]//strong//text()",
        'description': '//section[@class="section-description"]//div//text()',
        'additional_info': "//div[contains(@class,'css-1bpegon')]//text()",
        'tracking_id': "substring-after(//div[contains(@class,'css-kos6vh')]//text()[position()=1][following-sibling::br],':')",
        'agency_tracking_id': 'substring-after(//div[@class="css-kos6vh"]/div[position()=2]//text()[preceding-sibling::br],":")',
        'add_rel_date': "substring-after(//div[contains(@class,'css-lh1bxu')]//text()[position()=1][following-sibling::br],':')",
        'update_rel_date': 'substring-after(//div[@class="css-lh1bxu"][position()=1]//text()[preceding-sibling::br],":")'
    }

    def parse(self, response):
        """

        :param response:
        :param response:
        :return:
        """
        self.pageCounter += 1

        if self.settings['SAVE_RESULTS'] == 'LOCAL':
            file_list = helpers.scraper.list_local(self.settings['LOCAL_DATA_PATH'])
        elif self.settings['SAVE_RESULTS'] == 'S3':
            file_list = helpers.scraper.list_bucket(self.settings['BUCKET_NAME'],
                                                    self.settings['BUCKET_PREFIX_BSON'])
        else:
            raise Exception("please specify where to save results")

        logger.info("Prepare list of downloaded files")
        logger.debug(file_list[-2:])

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

            if file_name not in file_list:
                logger.info("File {} is NOT in bucket -> download".format(file_name))
                request.meta['file_name'] = file_name
                yield request
            else:
                logger.info('File {} is in bucket -> DO NOT download'.format(file_name))

        # after you crawl each offer in current page go to the next page
        next_page = response.css('li.pager-next a::attr(href)').get()

        if next_page is not None and self.pageCounter < self.settings['MAX_PAGES']:
            yield response.follow(next_page, callback=self.parse)

    def parse_one_article(self, response):

        tmp = response.meta['data']

        for key in self.iter_xpaths_one_article:
            tmp[key] = response.xpath(self.iter_xpaths_one_article[key]).get()

        tmp['additional_info'] = "|".join(response.xpath(self.iter_xpaths_one_article['additional_info']).getall())
        tmp['description'] = "\n".join(response.xpath(self.iter_xpaths_one_article['description']).getall())
        tmp['download_date'] = helpers.scraper.current_timestamp()

        tmp['geo_coordinates'], tmp['geo_address_text'], tmp['geo_address_coordin'] = helpers.scraper.get_geodata(
            response.body)

        tmp['img_gallery_strimg'] = [helpers.scraper.imgurl2str(i['photo']) for i in json.loads(
                                                                    tmp['gallery'])[:self.settings['DOWNLOAD_IMAGES']]]

        check_list = ['flat_size', 'location', 'offer_title', 'url', 'name', 'description']
        for key in check_list:
            if tmp[key] is None:
                dict_temp = helpers.scraper.concat_dict([self.iter_xpaths_list, self.iter_xpaths_one_article])
                text = 'xPaths doesnt work: \n'
                for key2 in check_list:
                    if tmp[key2] is None:
                        text += "{}: {} \n".format(key, dict_temp[key])
                raise Exception(text)
                raise CloseSpider(text)

        data_b_ = dumps(bson.BSON.encode(tmp))

        if self.settings['SAVE_RESULTS'] == 'LOCAL':
            helpers.scraper.write_local(data_b_, self.settings['LOCAL_DATA_PATH'], response.meta['file_name'])
        elif self.settings['SAVE_RESULTS'] == 'S3':
            helpers.scraper.write_s3_bucket(data_b_, response.meta['file_name'],
                                            self.settings['BUCKET_NAME'], prefix=self.settings['BUCKET_PREFIX_BSON'])
        else:
            raise Exception("please specify where to save results")

        yield {"file_name": response.meta['file_name'], "statusCode": 200}
