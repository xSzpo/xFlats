import logging
import time
import helpers
from scrapy.utils.log import configure_logging

from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor

#configure_logging(install_root_handler=False)
#logging.basicConfig(
#    filename='scraper.log',
#    filemode='w',
#    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#    level=logging.ERROR
#)

logger = logging.getLogger(__name__)


def scraper_otodom(event={'test':1}, context= {'test':1}):

    _, _ = event, context

    process = CrawlerProcess(get_project_settings())
    d = process.crawl('otodom')
    d.addBoth(lambda _: reactor.stop())
    reactor.run()

#if __name__ == "__main__":
#    logger.info("start program")
#    start = time.time()
#    scraper_otodom()
#    end = time.time()
#    logger.info("time elapsed: %s" % helpers.base.timer(start, end))
#    logger.info("end program")

