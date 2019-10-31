# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import json
import numpy as np
import re
import codecs
from pykafka import KafkaClient

import sys
sys.path.append("..")
import helpers


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

    def __init__(self, kafka_topic, kafka_host, kafka_port):
        self.kafka_topic = kafka_topic
        self.kafka_host = kafka_host
        self.kafka_port = kafka_port
        self.client = None
        self.topic = None
        self.producer = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            kafka_topic=crawler.settings.get('KAFKA_TOPIC'),
            kafka_host=crawler.settings.get('KAFKA_HOST'),
            kafka_port=crawler.settings.get('KAFKA_PORT'),
        )

    def open_spider(self, spider):
        self.client = KafkaClient(hosts=self.kafka_host+":"+self.kafka_port)
        self.topic = self.client.topics[self.kafka_topic]
        self.producer = self.topic.get_sync_producer()

    def close_spider(self, spider):
        self.producer.stop()

    def process_item(self, item, spider):
        _ = spider
        data = str.encode(json.dumps(item))
        self.producer.produce(data)
        return item


class OutputStdout:

    def process_item(self, item, spider):
        _ = spider
        line = json.dumps(dict(item), ensure_ascii=False)
        print(line)
        return item
