import logging
import time
import helpers
from scrapy.utils.log import configure_logging

from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor
import urllib.parse
import urllib.request

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

    # https://github.com/scrapy/scrapy/issues/3606
    process = CrawlerProcess(get_project_settings())
    d = process.crawl('test')
    d.addBoth(lambda _: reactor.stop())
    reactor.run()


def test(event={'test': 1}, context={'test': 1}):

    url = 'https://www.otodom.pl/'
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
    values = {'name': 'Michael Foord',
              'location': 'Northampton',
              'language': 'Python' }
    headers = {'User-Agent': user_agent}

    data = urllib.parse.urlencode(values)
    data = data.encode('ascii')
    proxies = {'http': "http://83.12.149.202:8080"}
    req = urllib.request.Request(url, data, headers, proxies)
    with urllib.request.urlopen(req) as response:
       the_page = response.read()

    print(the_page[:500])

if __name__ == "__main__":
    logger.info("start program")
    start = time.time()
    test()
    end = time.time()
    logger.info("time elapsed: %s" % helpers.base.timer(start, end))
    logger.info("end program")

