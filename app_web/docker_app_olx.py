#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This is a awesome
        python script thats scraps otodom"""

from scrapy.utils.project import get_project_settings
from helpers.scrapyloop import ScrapyLoop
import json
import time
import os

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def scraper(event={}, context={}):

    _, _ = event, context

    # overwrite to save results in S3
    settings = get_project_settings()
    settings['MONGO_ADDRESS'] = 'mongo'
    settings['KAFKA_HOST'] = 'kafka'
    settings['CRAWL_LIST_PAGES'] = 1

    settings['ITEM_PIPELINES'] = {
        'scraper.pipelines.ProcessItem': 100, #transform data
        'scraper.pipelines.OutputMongo': 202, #save to mongo
        'scraper.pipelines.OutputFilter': 301, #filter that are already in db
        'scraper.pipelines.OutputKafka': 401 #put to kafka
        }

    # wait until mongodb is ready
    sleep_time = int(os.environ['SCRAPER_START_DELAY_SEC']) if 'SCRAPER_START_DELAY_SEC' in os.environ.keys() else 30
    time.sleep(sleep_time)

    scrapy_del = int(os.environ['SCRAPER_DELAY_AFTER_EACH_RUN_SEC']) if \
        'SCRAPER_DELAY_AFTER_EACH_RUN_SEC' in os.environ.keys() else 60

    ScrapyLoop(settings=settings, success_interval=scrapy_del).loop_crawl('olx')

    return {
        'statusCode': 200,
        'body': json.dumps('scraping successful')
    }

if __name__ == "__main__":

    scraper()
