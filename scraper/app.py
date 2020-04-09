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


def env2pipe(val):
    x = os.getenv(val)
    if x == "None":
        return None
    else:
        return int(x)


def scraper(event={}, context={}):

    _, _ = event, context

    settings = get_project_settings()
    settings['REDIS_HOST'] = os.getenv('REDIS_HOST')
    settings['REDIS_PORT'] = int(os.getenv('REDIS_PORT'))
    settings['REDIS_DB_INDEX'] = 0

    # GCP Firestore
    settings['COLLECTION'] = os.getenv("GCP_FIRESTORE_COLLECTION")
    settings['SECRETS_PATH'] = os.getenv("GCP_FIRESTORE_SECRETS_PATH")

    # local
    settings['LOCAL_FILE_DIR'] = os.getenv("JSONLINE_FILE_DIR")
    settings['LOCAL_FILE_NAME'] = os.getenv("JSONLINE_FILE_NAME")
    settings['ADDDATE2NAME'] = bool(os.getenv("JSONLINE_ADDDATE2NAME")=="True")

    # scraper config
    settings['CRAWL_LIST_PAGES'] = int(os.getenv("SCRAPER_CRAWL_LIST_PAGES"))
    settings['CONCURRENT_REQUESTS'] = int(os.getenv("SCRAPER_CONCURRENT_REQUESTS"))

    settings['ITEM_PIPELINES'] = {
        'scraper.pipelines.ProcessItem': env2pipe("SCRAPER_START_DELAY_SEC"),
        'scraper.pipelines.CheckIfExistRedis': env2pipe("scr_pipe_CheckIfExistRedis"),
        'scraper.pipelines.CheckIfExistGCPFirestore': env2pipe("scr_pipe_CheckIfExistGCPFirestore"),
        'scraper.pipelines.OutputFilter': env2pipe("scr_pipe_OutputFilter"),
        'scraper.pipelines.ProcessItemGeocode': env2pipe("scr_pipe_ProcessItemGeocode"),
        'scraper.pipelines.ValidSchema': env2pipe("scr_pipe_ValidSchema"),
        'scraper.pipelines.OrderbySchema': env2pipe("scr_pipe_OrderbySchema"),
        'scraper.pipelines.OutputLocal': env2pipe("scr_pipe_OutputLocal"),
        'scraper.pipelines.OutputGCPFirestore': env2pipe("scr_pipe_OutputGCPFirestore"),
        'scraper.pipelines.OutputRedis': env2pipe("scr_pipe_OutputRedis"),
        'scraper.pipelines.OutputStdout': env2pipe("scr_pipe_OutputStdout"),
    }

    # wait until other ysstems are ready
    sleep_time = int(os.getenv('SCRAPER_START_DELAY_SEC')) if \
        'SCRAPER_START_DELAY_SEC' in os.environ.keys() else 30
    time.sleep(sleep_time)

    scrapy_del = int(os.getenv('SCRAPER_DELAY_AFTER_EACH_RUN_SEC')) if \
        'SCRAPER_DELAY_AFTER_EACH_RUN_SEC' in os.environ.keys() else 60

    ScrapyLoop(settings=settings, success_interval=scrapy_del). \
        loop_crawl(os.getenv("SCRAPER_CRAWLER_NAME"))

    return {
        'statusCode': 200,
        'body': json.dumps('scraping successful')
    }


if __name__ == "__main__":

    scraper()
