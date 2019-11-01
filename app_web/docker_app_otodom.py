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


def scraper_otodom(event={}, context={}):

    _, _ = event, context

    # overwrite to save results in S3
    settings = get_project_settings()
    settings['MONGO_ADDRESS'] = 'mongo'
    settings['KAFKA_HOST'] = 'kafka'

    settings['ITEM_PIPELINES'] = {
        'scraper.pipelines.ProcessListOtodom': 300,
        #'scraper.pipelines.OutputLocal': 400,
        #'scraper.pipelines.OutputKafka': 401,
        #'scraper.pipelines.OutputStdout': 402,
        #'scraper.pipelines.OutputMongo': 403
    }

    # wait until mongodb is ready
    if 'SCRAPER_START_DELAY_SEC' in os.environ.keys():
        time.sleep(int(os.environ['SCRAPER_START_DELAY_SEC']))
    else:
        time.sleep(30)

    if 'SCRAPER_DELAY_AFTER_EACH_RUN_SEC' in os.environ.keys():
        ScrapyLoop(settings=settings,
                   success_interval=int(os.environ['SCRAPER_DELAY_AFTER_EACH_RUN_SEC'])).loop_crawl('otodom')
    else:
        ScrapyLoop(settings=settings, success_interval=60).loop_crawl('Otodom')

    return {
        'statusCode': 200,
        'body': json.dumps('scraping successful')
    }

if __name__ == "__main__":

    scraper_otodom()
