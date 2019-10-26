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
from scrapy.utils.serialize import ScrapyJSONEncoder

import sys
sys.path.append("..")
import helpers


class OtodomListProcess(object):
    def process_item(self, item, spider):
        _ = spider
        item['gallery'] = json.loads(item['gallery'])
        price_str = ''.join([i for i in re.sub("[ ]", "", item["price"]) if i.isdigit()])
        item['price'] = float(np.float32(helpers.Scraper.digits_from_str(item['price']))) if item[
                                                                                 'price'] is not None else None
        item['tracking_id'] = int(helpers.Scraper.digits_from_str(item['tracking_id'])) if \
            item['tracking_id'] is not None else None
        item['offer_title'] = item['offer_title'].strip() if item['offer_title'] is not None else None
        item['file_name'] = str(item["tracking_id"]) + "_" + price_str
        selected_col = ['file_name', 'offer_title', 'price', 'tracking_id', 'url',
                        'url_offer_list', 'producer_name', 'main_url','gallery']

        tmp = {}
        for key in selected_col:
            tmp[key] = item[key]

        return tmp


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
        line = json.dumps(dict(item))
        print(line)
        return item


