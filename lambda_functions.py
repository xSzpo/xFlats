import logging
import time
import helpers
from scrapy.utils.log import configure_logging

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


configure_logging(install_root_handler=False)
logging.basicConfig(
    filename='scraper.log',
    filemode='w',
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.ERROR
)

logger = logging.getLogger(__name__)


def scraper_otodom():

    process = CrawlerProcess(get_project_settings())
    process.crawl('otodom')
    process.start()


if __name__ == "__main__":
    logger.info("start program")
    start = time.time()
    scraper_otodom()
    end = time.time()
    logger.info("time elapsed: %s" % helpers.base.timer(start, end))
    logger.info("end program")

