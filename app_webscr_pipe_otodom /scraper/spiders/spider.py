import scrapy
from scrapy.exceptions import CloseSpider
import sys
sys.path.append("..")
import helpers
import re
import datetime
import json
import codecs
import numpy as np

import logging
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
        self.mongo_connection = None
        self.write = True

    name = "otodom"

    with codecs.open("./scraper/spiders/xhpats.json", "r") as file:
        xpath_json = json.load(file)

    start_urls = xpath_json['start_urls']
    list_page_start_xpath = xpath_json['list_page_start_xpath']
    list_page_iter_xpaths = xpath_json['list_page_iter_xpaths']
    article_page_iter_xpaths = xpath_json['article_page_iter_xpaths']

    def parse(self, response):
        """

        :param response:
        :param response:
        :return:
        """
        self.pageCounter += 1

        logger.info("Prepare list of downloaded files:")
        #if 'LOCAL' in self.settings['SAVE_RESULTS']:
        #    file_list = helpers.FilesLocal.list_files(self.settings['LOCAL_DATA_PATH'])

        #if 'S3' in self.settings['SAVE_RESULTS']:
        #    file_list = helpers.FilesS3.list_files(self.settings['BUCKET_NAME'],
        #                                           self.settings['BUCKET_PREFIX_BSON'])

        if 'MONGODB' in self.settings['SAVE_RESULTS']:
            self.mongo_connection = helpers.FilesMongo.set_connection(self.settings['MONGO_ADDRESS'],
                                    self.settings['MONGO_PORT'], self.settings['MONGO_DBNAME'],
                                    self.settings['MONGO_COLL_OTODOM'], self.settings['MONGO_USERNAME'],
                                    self.settings['MONGO_PASSWORD'])

            #file_list = helpers.FilesMongo.list_files(self.mongo_connection)

        if len([i for i in ['LOCAL', 'S3', 'MONGODB'] if i in self.settings['SAVE_RESULTS']]) == 0:
            raise Exception("Please specify where to save results")

        logger.info("Get data:")

        # do something for every offer found in offers list
        for offer in response.xpath(self.list_page_start_xpath):
            tmp = {}

            for key in self.list_page_iter_xpaths:
                tmp[key] = offer.xpath(self.list_page_iter_xpaths[key]).get()
                if tmp[key] is None:
                    text = 'LIST - xPaths doesnt work: \n'
                    text += "{}: {} , value:{}\n".format(key, self.list_page_iter_xpaths[key], tmp[key])
                    raise CloseSpider(text)
            tmp['url_offer_list'] = response.url
            tmp['producer_name'] = self.name
            tmp["main_url"] = "otodom.pl"

            request = scrapy.Request(tmp['url'], callback=self.parse_one_article)
            request.meta['data'] = tmp

            price_str = ''.join([i for i in re.sub("[ ]", "", tmp["price"]) if i.isdigit()])
            file_name = tmp["tracking_id"]+"_"+price_str

            found_file = False

            if 'LOCAL' in self.settings['SAVE_RESULTS']:
                if helpers.FilesLocal.check_if_exists(file_name, self.settings['LOCAL_DATA_PATH']):
                    found_file = True

            if 'S3' in self.settings['SAVE_RESULTS']:
                if helpers.FilesS3.check_if_exists(file_name, self.settings['BUCKET_NAME'],
                                                   prefix=self.settings['BUCKET_PREFIX_BSON']):
                    found_file = True

            if 'MONGODB' in self.settings['SAVE_RESULTS']:
                if helpers.FilesMongo.check_if_exists(file_name, self.mongo_connection, id_field='_id'):
                    found_file = True

            if not found_file:
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

        for key in self.article_page_iter_xpaths:
            tmp[key] = response.xpath(self.article_page_iter_xpaths[key]).get()

        tmp['additional_info'] = "|".join(response.xpath(self.article_page_iter_xpaths['additional_info']).getall())
        tmp['description'] = "\n".join(response.xpath(self.article_page_iter_xpaths['description']).getall())
        tmp['download_date'] = helpers.Scraper.current_timestamp()

        tmp['geo_coordinates'], tmp['geo_address_text'], tmp['geo_address_coordin'] = helpers.Geodata.get_geodata(
            response.body)

        tmp['img_gallery_strimg'] = [helpers.Scraper.imgurl2str(i['photo']) for i in json.loads(
                                                                    tmp['gallery'])[:self.settings['DOWNLOAD_IMAGES']]]

        check_list = ['flat_size', 'location', 'offer_title', 'url', 'name', 'description']
        for key in check_list:
            if tmp[key] is None:
                dict_temp = helpers.Scraper.concat_dict([self.list_page_iter_xpaths, self.article_page_iter_xpaths])
                text = 'OFFER - xPaths doesnt work: \n'
                for key2 in check_list:
                    if tmp[key2] is None:
                        text += "{}: {} \n".format(key, dict_temp[key])
                raise CloseSpider(text)

        tmp = self.transform_data(tmp, response.meta['file_name'])

        if 'LOCAL' in self.settings['SAVE_RESULTS'] and self.write:
            helpers.FilesLocal.write_file(tmp, self.settings['LOCAL_DATA_PATH'], response.meta['file_name'])

        if 'S3' in self.settings['SAVE_RESULTS'] and self.write:
            helpers.FilesS3.write_file(tmp, response.meta['file_name'], self.settings['BUCKET_NAME'],
                                       prefix=self.settings['BUCKET_PREFIX_BSON'])

        if 'MONGODB' in self.settings['SAVE_RESULTS'] and self.write:
            helpers.FilesMongo.write_file(tmp, self.mongo_connection)

        if len([i for i in ['LOCAL', 'S3', 'MONGODB'] if i in self.settings['SAVE_RESULTS']]) == 0:
            raise Exception('Please specify where to save results in setting.py!')

        yield {"file_name": response.meta['file_name'], "statusCode": 200}

    @staticmethod
    def transform_data(dict_data, name):
        columns = ['_id', 'name', 'location', 'flat_size', 'rooms', 'floor', 'price',
                   'price_m2', 'market', 'number_of_floors', 'floor_attic', 'floor_basement', 'building_type',
                   'building_material', 'widows_type', 'heating_type', 'year_of_building', 'finishing_stage',
                   'rent_price', 'property_form', 'available_from', 'description', 'additional_info',
                   'GC_latitude', 'GC_longitude', 'GC_boundingbox', 'GC_addr_house_number', 'GC_addr_road',
                   'GC_addr_neighbourhood', 'GC_addr_suburb', 'GC_addr_city', 'GC_addr_county', 'GC_addr_state',
                   'GC_addr_postcode', 'GC_addr_country', 'GC_addr_country_code', 'url', 'main_url', 'gallery',
                   'img_gallery_strimg', 'tracking_id', 'download_date']

        _tmp = dict_data.copy()

        # CHANGE DTYPE
        _tmp['_id'] = name
        _tmp['GC_latitude'] = float(_tmp['geo_coordinates']['latitude'])
        _tmp['GC_longitude'] = float(_tmp['geo_coordinates']['longitude'])
        _tmp['GC_boundingbox'] = _tmp['geo_address_coordin']['@boundingbox']
        _tmp['GC_addr_house_number'] = _tmp['geo_address_text']['house_number'] if 'house_number' in _tmp[
            'geo_address_text'] else None
        _tmp['GC_addr_road'] = _tmp['geo_address_text']['road'] if 'road' in _tmp['geo_address_text'] else None
        _tmp['GC_addr_neighbourhood'] = _tmp['geo_address_text']['neighbourhood'] if 'neighbourhood' in _tmp[
            'geo_address_text'] else None
        _tmp['GC_addr_suburb'] = _tmp['geo_address_text']['suburb'] if 'suburb' in _tmp['geo_address_text'] else None
        _tmp['GC_addr_city'] = _tmp['geo_address_text']['city'] if 'city' in _tmp['geo_address_text'] else None
        _tmp['GC_addr_county'] = _tmp['geo_address_text']['county'] if 'country' in _tmp['geo_address_text'] else None
        _tmp['GC_addr_state'] = _tmp['geo_address_text']['state'] if 'state' in _tmp['geo_address_text'] else None
        _tmp['GC_addr_postcode'] = _tmp['geo_address_text']['postcode'] if 'postcode' in _tmp[
            'geo_address_text'] else None
        _tmp['GC_addr_country'] = _tmp['geo_address_text']['country'] if 'country' in _tmp['geo_address_text'] else None
        _tmp['GC_addr_country_code'] = _tmp['geo_address_text']['country_code'] if 'country_code' in _tmp[
            'geo_address_text'] else None
        _tmp['additional_info'] = _tmp['additional_info'].split("|")
        _ = _tmp.pop('geo_coordinates')
        _ = _tmp.pop('geo_address_coordin')

        # MODIFY DATA
        _tmp['flat_size'] = float(np.float32(helpers.Scraper.digits_from_str(_tmp['flat_size']))) if \
            _tmp['flat_size'] is not None else None
        _tmp['price'] = float(np.float32(helpers.Scraper.digits_from_str(_tmp['price']))) if _tmp[
                                                                                 'price'] is not None else None
        _tmp['price_m2'] = helpers.Scraper.digits_from_str(_tmp['price_m2']) if _tmp['price_m2'] is not None else None
        _tmp['rooms'] = int(helpers.Scraper.digits_from_str(_tmp['rooms'])) if _tmp['rooms'] is not None else None
        _tmp['floor_attic'] = 1 if _tmp['floor'] == 'poddasze' else 0
        _tmp['floor_basement'] = 1 if _tmp['floor'] == 'suterena' else 0
        _tmp['floor'] = float(np.float32(helpers.Scraper.convert_floor(_tmp['floor']))) if isinstance(_tmp['floor'],
                                                                                                      str) else None
        _tmp['number_of_floors'] = float(np.float32(_tmp['number_of_floors'])) if isinstance(_tmp['number_of_floors'],
                                                                                             str) else None
        _tmp['year_of_building'] = float(np.float32(_tmp['year_of_building'])) if isinstance(_tmp['year_of_building'],
                                                                                             str) else None
        _tmp['rent_price'] = helpers.Scraper.digits_from_str(_tmp['rent_price']) if \
            _tmp['rent_price'] is not None else None
        _tmp['gallery'] = json.loads(_tmp['gallery'])
        _tmp['tracking_id'] = int(helpers.Scraper.digits_from_str(_tmp['tracking_id'])) if \
            _tmp['tracking_id'] is not None else None
        _tmp = helpers.Scraper.dict_except(_tmp, [], include_keys=columns)

        return _tmp
