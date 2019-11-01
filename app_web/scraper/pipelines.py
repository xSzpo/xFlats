# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import logging
import sys
import json
import re
import codecs

import numpy as np
from scrapy.exceptions import DropItem
import kafka
import pymongo
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, WriteError, WriteConcernError, WTimeoutError

sys.path.append("..")
import helpers
logger = logging.getLogger(__name__)

class ProcessListOtodom(object):

    def process_item(self, item, spider):
        _ = spider
        price_str = ''.join([i for i in re.sub("[ ]", "", item["price"]) if i.isdigit()])

        item['_id'] = str(item["tracking_id"]) + "_" + price_str
        item['GC_latitude'] = float(item['geo_coordinates']['latitude'])
        item['GC_longitude'] = float(item['geo_coordinates']['longitude'])
        item['GC_boundingbox'] = item['geo_address_coordin']['@boundingbox']
        item['GC_addr_house_number'] = item['geo_address_text']['house_number'] if 'house_number' in item[
            'geo_address_text'] else None
        item['GC_addr_road'] = item['geo_address_text']['road'] if 'road' in item['geo_address_text'] else None
        item['GC_addr_neighbourhood'] = item['geo_address_text']['neighbourhood'] if 'neighbourhood' in item[
            'geo_address_text'] else None
        item['GC_addr_suburb'] = item['geo_address_text']['suburb'] if 'suburb' in item['geo_address_text'] else None
        item['GC_addr_city'] = item['geo_address_text']['city'] if 'city' in item['geo_address_text'] else None
        item['GC_addr_county'] = item['geo_address_text']['county'] if 'country' in item['geo_address_text'] else None
        item['GC_addr_state'] = item['geo_address_text']['state'] if 'state' in item['geo_address_text'] else None
        item['GC_addr_postcode'] = item['geo_address_text']['postcode'] if 'postcode' in item[
            'geo_address_text'] else None
        item['GC_addr_country'] = item['geo_address_text']['country'] if 'country' in item['geo_address_text'] else None
        item['GC_addr_country_code'] = item['geo_address_text']['country_code'] if 'country_code' in item[
            'geo_address_text'] else None
        item['additional_info'] = item['additional_info'].split("|")
        _ = item.pop('geo_coordinates')
        _ = item.pop('geo_address_coordin')

        # MODIFY DATA
        item['flat_size'] = float(np.float32(helpers.Scraper.digits_from_str(item['flat_size']))) if \
            item['flat_size'] is not None else None
        item['price'] = float(np.float32(helpers.Scraper.digits_from_str(item['price']))) if item[
                                                                                 'price'] is not None else None
        item['price_m2'] = helpers.Scraper.digits_from_str(item['price_m2']) if item['price_m2'] is not None else None
        item['rooms'] = int(helpers.Scraper.digits_from_str(item['rooms'])) if item['rooms'] is not None else None
        item['floor_attic'] = 1 if item['floor'] == 'poddasze' else 0
        item['floor_basement'] = 1 if item['floor'] == 'suterena' else 0
        item['floor'] = float(np.float32(helpers.Scraper.convert_floor(item['floor']))) if isinstance(item['floor'],
                                                                                                      str) else None
        item['number_of_floors'] = float(np.float32(item['number_of_floors'])) if isinstance(item['number_of_floors'],
                                                                                             str) else None
        item['year_of_building'] = float(np.float32(item['year_of_building'])) if isinstance(item['year_of_building'],
                                                                                             str) else None
        item['rent_price'] = helpers.Scraper.digits_from_str(item['rent_price']) if \
            item['rent_price'] is not None else None
        item['tracking_id'] = int(helpers.Scraper.digits_from_str(item['tracking_id'])) if \
            item['tracking_id'] is not None else None

        selected_col = ['_id', 'name', 'location', 'flat_size', 'rooms', 'floor', 'price', 'tracking_id',
                   'url', 'producer_name', 'main_url',
                   'price_m2', 'market', 'number_of_floors', 'floor_attic', 'floor_basement', 'building_type',
                   'building_material', 'widows_type', 'heating_type', 'year_of_building', 'finishing_stage',
                   'rent_price', 'property_form', 'available_from', 'description', 'additional_info',
                   'GC_latitude', 'GC_longitude', 'GC_boundingbox', 'GC_addr_house_number', 'GC_addr_road',
                   'GC_addr_neighbourhood', 'GC_addr_suburb', 'GC_addr_city', 'GC_addr_county', 'GC_addr_state',
                   'GC_addr_postcode', 'GC_addr_country', 'GC_addr_country_code', 'url', 'main_url','tracking_id',
                   'download_date']

        tmp = {}
        for key in selected_col:
            tmp[key] = item[key]
        return item


class OutputLocal:

    def __init__(self, encoding, file_path,**kwargs):
        self.encoding = encoding
        self.file_path = file_path
        self.file = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            encoding=crawler.settings.get('FEED_EXPORT_ENCODING'),
            file_path=crawler.settings.get('LOCAL_FILE_PATH')
        )

    def open_spider(self, spider):
        _ = spider
        self.file = codecs.open(self.file_path, 'a', encoding=self.encoding)

    def close_spider(self, spider):
        _ = spider
        self.file.close()

    def process_item(self, item, spider):
        _ = spider
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(line)
        return item


class OutputKafka:

    def __init__(self, kafka_host, kafka_port):
        self.kafka_host = kafka_host
        self.kafka_port = kafka_port
        self.client = None
        self.producer = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            kafka_host=crawler.settings.get('KAFKA_HOST'),
            kafka_port=crawler.settings.get('KAFKA_PORT'),
        )

    def open_spider(self, spider):
        self.producer = kafka.KafkaProducer(hosts=self.kafka_host+":"+self.kafka_port)

    def close_spider(self, spider):
        self.producer.stop()

    def process_item(self, item, spider):
        _ = spider
        data = str.encode(json.dumps(item))
        self.producer.send(item['producer_name'], data)
        return item


class OutputStdout:

    def process_item(self, item, spider):
        _ = spider
        line = json.dumps(dict(item), ensure_ascii=False)
        print(line)
        return item


class OutputMongo(object):

    def __init__(self, mongo_adrress, mongo_port, mongo_dbname, mongo_username, mongo_password,
                 id_field, download_date):

        connection = pymongo.MongoClient(host=mongo_adrress, port=mongo_port, username=mongo_username,
                                         password=mongo_password, authSource='admin', authMechanism='SCRAM-SHA-256',
                                         serverSelectionTimeoutMS=5000)
        self.db = connection[mongo_dbname]
        self.id_field = id_field
        self.download_date = download_date

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_adrress=crawler.settings.get('MONGO_ADDRESS'),
            mongo_port=crawler.settings.get('MONGO_PORT'),
            mongo_dbname=crawler.settings.get('MONGO_DBNAME'),
            mongo_username=crawler.settings.get('MONGO_USERNAME'),
            mongo_password=crawler.settings.get('MONGO_PASSWORD'),
            id_field=crawler.settings.get('ID_FIELD'),
            download_date=crawler.settings.get('DOWNLOAD_DATE')
        )

    def process_item(self, item, spider):

        _ = spider
        valid = True
        for data in item:
            if not data:
                valid = False
                raise DropItem("Missing {0}!".format(data))
        if valid:
            try:
                w = self.db[item['producer_name']].update_one({self.id_field: item[self.id_field]}, item, upsert=True)
                logger.info("MongoDB: save offer {} to mongodb, {}".format(item[self.id_field], w))
                pass
            except (ConnectionFailure, ServerSelectionTimeoutError) as e:
                logger.error("pymongo.errors, Could not connect to server: %s" % e)
            except (WriteError, WriteConcernError, WTimeoutError) as e:
                logger.error("pymongo.errors, Write error: %s" % e)
            except BaseException as e:
                logger.error("BaseException, something went wrong: %s" % e)
