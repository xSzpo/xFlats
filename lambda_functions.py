from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor

import json
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def scraper_otodom(event, context):

    _, _ = event, context
    process = CrawlerProcess(get_project_settings())
    d = process.crawl('otodom')
    d.addBoth(lambda _: reactor.stop())
    reactor.run()
    return {
        'statusCode': 200,
        'body': json.dumps('scraping successful')
    }
