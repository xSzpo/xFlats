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

    settings = get_project_settings()
    settings['REDIS_HOST'] = 'localhost'
    settings['REDIS_PORT'] = 6379
    settings['REDIS_DB_INDEX'] = 0

    # GCP Firestore
    settings['COLLECTION'] = 'flats'
    settings['SECRETS_PATH'] = "/etc/gcpfirestore/gcpfirestore_key.json"
    settings['FIRESTORE_DROP_KEYS'] = ['body']
    settings['FIRESTORE_STR2DATE'] = ['download_date', 'date_created', 'date_modified']

    # local
    settings['LOCAL_FILE_DIR'] = "/app/data/"
    settings['LOCAL_FILE_NAME'] = "flatsdata"
    settings['ADDDATE2NAME'] = True

    settings['CRAWL_LIST_PAGES'] = 1
    settings['CONCURRENT_REQUESTS'] = 1

    settings['ITEM_PIPELINES'] = {
        'scraper.pipelines.ProcessItem': 100,
        'scraper.pipelines.CheckIfExistRedis': 104,
        'scraper.pipelines.CheckIfExistGCPFirestore': 108,
        'scraper.pipelines.OutputFilter': 110,
        'scraper.pipelines.ProcessItemGeocode': 115,
        'scraper.pipelines.ValidSchema': 116,
        'scraper.pipelines.OrderbySchema': 117,
        'scraper.pipelines.OutputLocal': 201,
        'scraper.pipelines.OutputGCPFirestore': 202,
        'scraper.pipelines.OutputRedis': 204,
        #'scraper.pipelines.OutputStdout': 402
    }

    # wait until other ysstems are ready
    sleep_time = int(os.environ['SCRAPER_START_DELAY_SEC']) if \
        'SCRAPER_START_DELAY_SEC' in os.environ.keys() else 30
    time.sleep(sleep_time)

    scrapy_del = int(os.environ['SCRAPER_DELAY_AFTER_EACH_RUN_SEC']) if \
        'SCRAPER_DELAY_AFTER_EACH_RUN_SEC' in os.environ.keys() else 60

    ScrapyLoop(settings=settings, success_interval=scrapy_del). \
        loop_crawl('otodom')

    return {
        'statusCode': 200,
        'body': json.dumps('scraping successful')
    }


if __name__ == "__main__":

    scraper()
