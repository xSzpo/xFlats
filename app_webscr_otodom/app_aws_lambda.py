from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor

import json
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def scraper_otodom(event, context):

    _, _ = event, context
    # overwrite to save results in S3
    settings = get_project_settings()
    settings['SAVE_RESULTS'] = 'S3'

    # run crawler
    process = CrawlerProcess(settings)
    d = process.crawl('otodom')

    # avoid error  ReactorNotRestartable
    # https://doc.scrapy.org/en/latest/topics/practices.html#run-scrapy-from-a-script
    d.addBoth(lambda _: reactor.stop())

    reactor.run()

    return {
        'statusCode': 200,
        'body': json.dumps('scraping successful')
    }
