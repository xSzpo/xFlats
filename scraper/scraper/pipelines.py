# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# utc epoch to time - time.gmtime(0)

import logging
import sys
import json
import re
import codecs
import time
import numpy as np
import boto3
from scrapy.exceptions import DropItem
import redis
from google.cloud import storage
from scrapy.utils.conf import closest_scrapy_cfg
import os
import helpers

from jsonschema import validate, Draft3Validator, SchemaError, ValidationError
import jsonschema

logger = logging.getLogger(__name__)


class ProcessItem:

    def process_item(self, item, spider):
        _ = spider
        if item['producer_name'] == 'otodom':
            item = self.process_item_ototdom(item)
        elif item['producer_name'] == 'olx':
            item = self.process_item_olx(item)
        elif item['producer_name'] == 'gratka':
            item = self.process_item_gratka(item)
        elif item['producer_name'] == 'morizon':
            item = self.process_item_morizon(item)
        else:
            raise ValueError
        return item

    def process_item_ototdom(self, item):

        item['tracking_id'] = item['tracking_id'].strip()
        item['price'] = helpers.Scraper.digits_from_str(item['price'], returntype=int)
        item['_id'] = ("oto_"+str(item["tracking_id"]) + "_" + str(item['price'])).strip()
        item['flat_size'] = helpers.Scraper.digits_from_str(item['flat_size'], returntype=int)
        item['rooms'] = helpers.Scraper.digits_from_str(item['rooms'], returntype=int)
        item['floor'] = helpers.Scraper.convert_floor(item['floor'])
        item['price_m2'] = helpers.Scraper.digits_from_str(item['price_m2'], returntype=int)
        item['number_of_floors'] = helpers.Scraper.convert_floor(item['number_of_floors'])
        item['year_of_building'] = helpers.Scraper.digits_from_str(item['year_of_building'], returntype=int)

        item['download_date'] = helpers.Scraper.datetime2str(helpers.Scraper.current_datetime())
        item['download_date_utc'] = time.time()
        return item

    def process_item_olx(self, item):

        item['tracking_id'] = item['tracking_id'].strip()
        item['price'] = helpers.Scraper.digits_from_str(item['price'], returntype=int)
        item['_id'] = ("olx_"+str(item["tracking_id"]) + "_" + str(item['price'])).strip()
        item['flat_size'] = helpers.Scraper.digits_from_str(item['flat_size'], returntype=int)
        item['rooms'] = helpers.Scraper.digits_from_str(item['rooms'], returntype=int)
        item['floor'] = helpers.Scraper.convert_floor(item['floor'])
        item['price_m2'] = helpers.Scraper.digits_from_str(item['price_m2'], returntype=int)
        item['number_of_floors'] = helpers.Scraper.digits_from_str(item['number_of_floors'], returntype=int)
        item['year_of_building'] = helpers.Scraper.digits_from_str(item['year_of_building'], returntype=int)

        item['download_date'] = helpers.Scraper.datetime2str(helpers.Scraper.current_datetime())
        item['download_date_utc'] = time.time()
        return item


    def process_item_gratka(self, item):

        for key in ["price", "tracking_id", "name", "location", "flat_size",
                    "description", "producer_name", "geo_coordinates", "name",
                    "location"]:
            if item[key] == "" or item[key] is None:
                raise DropItem("Missing >>%s<< value" % key)

        if not any([i.isdigit() for i in item["price"]]):
            raise DropItem("Missing >>%s<< value" % "price")

        item['download_date'] = helpers.Scraper.current_datetime()
        item['download_date_utc'] = time.time()
        price_str = ''.join([i for i in re.sub("[ ]", "", item["price"])
                             if i.isdigit()])

        #item['tracking_id'] = item['tracking_id'].strip()
        item['tracking_id'] = int(np.float32(helpers.Scraper.digits_from_str(
            item['tracking_id']))) if item['tracking_id'] is not None else None

        item['_id'] = "gra_"+str(item["tracking_id"]) + "_" + price_str

        # MODIFY DATA
        item['flat_size'] = int(np.float32(helpers.Scraper.digits_from_str(
            item['flat_size']))) if item['flat_size'] is not None else None

        item['price'] = int(np.float32(helpers.Scraper.digits_from_str(
            item['price']))) if item['price'] is not None else None
        item['price_m2'] = helpers.Scraper.digits_from_str(item['price_m2']) \
            if item['price_m2'] is not None else None
        item['rent_price'] = helpers.Scraper.digits_from_str(
            item['rent_price']) if item['rent_price'] is not None else None
        item['rooms'] = int(helpers.Scraper.digits_from_str(item['rooms'])) \
            if item['rooms'] is not None else None
        item['floor'] = item['floor'].strip() if item['floor'] is not None \
            else None
        item['floor_attic'] = 1 if item['floor'] == 'poddasze' else 0
        item['floor_basement'] = 1 if item['floor'] == 'suterena' else 0
        item['floor'] = helpers.Scraper.convert_floor(item['floor']) \
            if isinstance(item['floor'], str) else None
        item['number_of_floors'] = int(np.float32(item['number_of_floors'])) \
            if isinstance(item['number_of_floors'], str) else None
        item['name'] = item['name'].strip() if item['name'] is not None \
            else None
        item['location'] = item['location'].strip() if item['location'] \
            is not None else None
        item['description'] = item['description'].strip() \
            if item['description'] is not None else None
        item['building_type'] = item['building_type'].strip() \
            if item['building_type'] is not None else None
        item['year_of_building'] = int(np.float32(item['year_of_building'])) \
            if isinstance(item['year_of_building'], str) else None
        item['parking'] = item['parking'].strip() if item['parking'] \
            is not None else None
        item['kitchen'] = item['kitchen'].strip() if item['kitchen'] \
            is not None else None
        item['condition'] = item['condition'].strip() if item['condition'] \
            is not None else None
        item['condition_electric_wires'] = item['condition_electric_wires'] \
            .strip() if item['condition_electric_wires'] is not None else None
        item['windows'] = item['windows'].strip() if item['windows'] \
            is not None else None
        item['loudness'] = item['loudness'].strip() if item['loudness'] \
            is not None else None
        item['bathroom_equip'] = item['bathroom_equip'].strip() \
            if item['bathroom_equip'] is not None else None
        item['available_from'] = item['available_from'].strip() \
            if item['available_from'] is not None else None
        item['bathroom'] = item['bathroom'].strip() if item['bathroom'] \
            is not None else None
        item['additional_space'] = item['additional_space'].strip() \
            if item['additional_space'] is not None else None
        item['world_direction'] = item['world_direction'].strip() \
            if item['world_direction'] is not None else None

        selected_col = ['_id', 'name', 'location', 'flat_size', 'rooms',
                        'floor', 'price', 'tracking_id', 'url', 'producer_name',
                        'main_url', 'price_m2', 'floor_attic', 'floor_basement',
                        'building_type', 'description', 'number_of_floors',
                        'building_material', 'year_of_building', 'rent_price',
                        'property_form', 'ref_number', 'comute',
                        'health_beauty', 'education', 'other', 'url',
                        'main_url', 'tracking_id', 'geo_coordinates',
                        'ref_number', 'comute', 'health_beauty', 'education',
                        'other', 'parking', 'kitchen', 'condition',
                        'condition_electric_wires', 'windows', 'loudness',
                        'bathroom_equip', 'available_from', 'bathroom',
                        'additional_space', 'world_direction', 'download_date',
                        "download_date_utc"]

        tmp = {}
        for key in selected_col:
            tmp[key] = item[key]
        return tmp

    def process_item_morizon(self, item):

        for key in ["price", "tracking_id", "name", "location", "flat_size",
                    "description", "producer_name", "geo_coordinates", "name",
                    "location"]:
            if item[key] == "" or item[key] is None:
                raise DropItem("Missing >>%s<< value" % key)

        if not any([i.isdigit() for i in item["price"]]):
            raise DropItem("Missing >>%s<< value" % "price")

        item['download_date'] = helpers.Scraper.current_datetime()
        item['download_date_utc'] = time.time()
        price_str = ''.join([i for i in re.sub("[ ]", "", item["price"]) \
                             if i.isdigit()])
        item['tracking_id'] = item['tracking_id'].strip()
        item['_id'] = "mor_"+str(item["tracking_id"]) + "_" + price_str
        item['_id'] = item['_id'].strip()
        item['flat_size'] = int(np.float32(helpers.Scraper.digits_from_str(
            item['flat_size']))) if item['flat_size'] is not None else None
        item['flat_living_size'] = int(np.float32(
            helpers.Scraper.digits_from_str(item['flat_living_size']))) \
            if item['flat_living_size'] is not None else None
        item['price'] = int(np.float32(helpers.Scraper.digits_from_str(
            item['price']))) if item['price'] is not None else None
        item['price_m2'] = helpers.Scraper.digits_from_str(item['price_m2']) \
            if item['price_m2'] is not None else None
        item['rooms'] = int(helpers.Scraper.digits_from_str(item['rooms'])) \
            if item['rooms'] is not None else None
        item['floor'] = re.findall("\d+", item['floor'])[0] \
            if item['floor'] is not None and np.any(
                [i.isdigit() for i in item['floor']]) else None
        item['floor'] = helpers.Scraper.convert_floor(item['floor']) \
            if isinstance(item['floor'], str) else None
        item['number_of_floors'] = int(np.float32(item['number_of_floors'])) \
            if isinstance(item['number_of_floors'], str) else None
        item['year_of_building'] = int(np.float32(item['year_of_building'])) \
            if isinstance(item['year_of_building'], str) else None
        item['tracking_id'] = int(helpers.Scraper.digits_from_str(
            item['tracking_id'])) if item['tracking_id'] is not None else None

        selected_col = ['_id', 'name', 'location', 'flat_size', 'rooms',
                        'floor', 'price', 'tracking_id', 'url',
                        'producer_name', 'main_url', 'price_m2', 'market',
                        'number_of_floors', 'building_type',
                        'building_material', 'year_of_building',
                        'property_form', 'description', 'url', 'main_url',
                        'tracking_id', 'geo_coordinates', 'heating_type',
                        'other', "kitchen", "condition", "bathroom_number",
                        "terrace", "terrece_size", "for_office",
                        "offer_number", "flat_living_size", "flat_height",
                        "offer_updated", "offer_added", 'download_date',
                        "download_date_utc"]

        tmp = {}
        for key in selected_col:
            tmp[key] = item[key]
        return tmp


class ProcessItemGeocode:

    def process_item(self, item, spider):
        _ = spider

        item['geo_coordinates'], \
            item['geo_address_text'], item['geo_address_coordin'] = \
            helpers.Geodata.get_geocode_openstreet(item['geo_coordinates'])
        item['GC_latitude'] = float(item['geo_coordinates']['latitude'])
        item['GC_longitude'] = float(item['geo_coordinates']['longitude'])
        item['GC_boundingbox'] = item['geo_address_coordin']['@boundingbox']
        item['GC_addr_house_number'] = \
            item['geo_address_text']['house_number'] if 'house_number' \
            in item['geo_address_text'] else None
        item['GC_addr_road'] = item['geo_address_text']['road'] if 'road' \
            in item['geo_address_text'] else None
        item['GC_addr_neighbourhood'] = \
            item['geo_address_text']['neighbourhood'] if 'neighbourhood' \
            in item['geo_address_text'] else None
        item['GC_addr_suburb'] = item['geo_address_text']['suburb'] \
            if 'suburb' in item['geo_address_text'] else None
        item['GC_addr_city'] = item['geo_address_text']['city'] \
            if 'city' in item['geo_address_text'] else None
        item['GC_addr_state'] = item['geo_address_text']['state'] \
            if 'state' in item['geo_address_text'] else None
        item['GC_addr_postcode'] = item['geo_address_text']['postcode'] \
            if 'postcode' in item['geo_address_text'] else None
        item['GC_addr_country'] = item['geo_address_text']['country'] \
            if 'country' in item['geo_address_text'] else None
        item['GC_addr_country_code'] = \
            item['geo_address_text']['country_code'] if 'country_code' \
            in item['geo_address_text'] else None
        _ = item.pop('geo_coordinates')
        _ = item.pop('geo_address_coordin')
        _ = item.pop('geo_address_text')

        return item


class OutputLocal:

    def __init__(self, encoding, file_path, **kwargs):
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
        _tmp = item.copy()
        _tmp['download_date'] = helpers.Scraper.datetime2str(
            item['download_date'])
        logger.info("Local jsonline: save offer {}".format(item['_id']))
        line = json.dumps(dict(_tmp), ensure_ascii=False) + "\n"
        self.file.write(line)
        return item


class OutputStdout:

    def process_item(self, item, spider):
        _ = spider
        _tmp = item.copy()
        _tmp['download_date'] = helpers.Scraper.datetime2str(
            item['download_date'])
        line = json.dumps(dict(_tmp), ensure_ascii=False)
        print(line)
        return item


class OutputRedis():

    def __init__(self, host, port, db, id_field):
        self.host = host
        self.port = port
        self.db = db
        self.id_field = id_field
        self.r = redis.Redis(host=self.host, port=self.port, db=self.db)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host=crawler.settings.get('REDIS_HOST'),
            port=crawler.settings.get('REDIS_PORT'),
            db=crawler.settings.get('REDIS_DB_INDEX'),
            id_field=crawler.settings.get('ID_FIELD')
        )

    def process_item(self, item, spider):

        _ = spider

        try:
            self.r.set(item[self.id_field], 1)
            logger.info("Redis: add to cache {}".format(
                item[self.id_field]))
        except (redis.ConnectionError) as e:
            logger.error("Could not connect to server: %s" % e)
        except BaseException as e:
            logger.error(item[self.id_field])
            logger.error("BaseException at Redis, something went wrong: %s" %
                         e)
        return item


class CheckIfExistRedis(OutputRedis):

    def process_item(self, item, spider):

        _ = spider

        try:
            if ("found" in item) and ("cache" not in item):
                self.r.set(item[self.id_field], 1)
                logger.info("Redis: add to cache {}".format(
                    item[self.id_field]))
            elif self.r.exists(item[self.id_field]) and ("cache" not in item):
                item["found"] = True
                item["cache"] = True
                logger.info("Redis: found {} ".format(
                    item[self.id_field]))
        except (redis.ConnectionError) as e:
            logger.error("Could not connect to server: %s" % e)
        except BaseException as e:
            logger.error(item[self.id_field])
            logger.error("BaseException at Redis, something went wrong: %s" % e)
        return item


class UpdateExistRedis(CheckIfExistRedis):
    pass


class OutputS3:

    def __init__(self, bucket_name):
        self.bucket_name = bucket_name

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            bucket_name=crawler.settings.get('BUCKET_NAME')
        )

    def process_item(self, item, spider):
        _ = spider
        _tmp = item.copy()
        _tmp['download_date'] = helpers.Scraper.datetime2str(
            item['download_date'])
        data = json.dumps(dict(_tmp), ensure_ascii=False)
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(self.bucket_name)
        if len([i.key for i
                in bucket.objects.filter(
                    Prefix=_tmp['producer_name']+"/"+_tmp['_id'])]) > 0:
            logger.info("S3: don't save offer {} to S3, already there".format(
                _tmp['_id']))
            item["found"] = True
        else:
            w = bucket.put_object(
                Key=_tmp['producer_name']+"/"+_tmp['_id']+".bson", Body=data)
            logger.info("S3: save offer {} to S3, {}".format(_tmp['_id'], w))
        return item


class OutputGCP:

    def __init__(self, bucket_name):
        self.bucket_name = bucket_name

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            bucket_name=crawler.settings.get('BUCKET_NAME')
        )

    def process_item(self, item, spider):
        _ = spider
        _tmp = item.copy()
        _tmp['download_date'] = helpers.Scraper.datetime2str(
            item['download_date'])
        data = json.dumps(dict(_tmp), ensure_ascii=False)
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(self.bucket_name)
        if len([i.key for i
                in bucket.objects.filter(
                    Prefix=_tmp['producer_name']+"/"+_tmp['_id'])]) > 0:
            logger.info("S3: don't save offer {} to S3, already there".format(
                _tmp['_id']))
            item["found"] = True
        else:
            w = bucket.put_object(
                Key=_tmp['producer_name']+"/"+_tmp['_id']+".bson", Body=data)
            logger.info("S3: save offer {} to S3, {}".format(_tmp['_id'], w))
        return item


class OutputFilter:

    def __init__(self, schema_file_name):
        self.schema_file_name = schema_file_name
        self.file_path = os.path.join(
            os.path.dirname(closest_scrapy_cfg()), "helpers", schema_file_name)
        self.schema = self._load_schema()
        self.valid = Draft3Validator(self.schema)

    def _load_schema(self):
        with open(self.file_path, "r") as file:
            schema = json.load(file)
        _ = schema['properties'].pop('GC_latitude')
        _ = schema['properties'].pop('GC_longitude')
        _ = schema['properties'].pop('GC_boundingbox')
        _ = schema['properties'].pop('GC_addr_road')
        _ = schema['properties'].pop('GC_addr_neighbourhood')
        _ = schema['properties'].pop('GC_addr_suburb')
        _ = schema['properties'].pop('GC_addr_city')
        _ = schema['properties'].pop('GC_addr_state')
        _ = schema['properties'].pop('GC_addr_postcode')
        _ = schema['properties'].pop('GC_addr_country')
        _ = schema['properties'].pop('GC_addr_country_code')

        return schema

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            schema_file_name=crawler.settings.get('SCHEMA_FILE_NAME')
        )

    def process_item(self, item, spider):
        if "found" in item:
            raise DropItem("Found Drop {}!".format(item['_id']))

        if not self.valid.is_valid(item):
            errors = sorted(self.valid.iter_errors(item),
                            key=lambda e: e.absolute_path)
            errors_plain = "\n".join([(e.relative_path[-1]+" -> "+e.message)
                                      for e in errors])
            logger.info(errors_plain)
            raise DropItem("Invalid schema Drop {}!".format(item['_id']))
        else:
            return item


class ValidSchema(OutputFilter):

    def _load_schema(self):
        with open(self.file_path, "r") as file:
            schema = json.load(file)
        return schema
