import os
# -*- coding: utf-8 -*-

# Scrapy settings for app_webscr_pipe_otodom project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

##################
# GENERAL SETTINGS
##################

SPIDER_MODULES = ['scraper.spiders']
NEWSPIDER_MODULE = 'scraper.spiders'
LOG_LEVEL = 'INFO'
LOG_FORMATTER = 'helpers.base.PoliteLogFormatter'
FEED_EXPORT_ENCODING = "UTF-8"

################
# CRAWL SETTINGS
################

COOKIES_ENABLED = False
ROBOTSTXT_OBEY = True
CONCURRENT_REQUESTS = 1
DOWNLOAD_DELAY = 0.5
LOGSTATS_INTERVAL = 0
CRAWL_LIST_PAGES = 999  # how many pages with links ]to crawl (start pages)

# -----------------------------------------------------------------------------
# USER AGENT
# -----------------------------------------------------------------------------

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy_useragents.downloadermiddlewares.useragents.UserAgentsMiddleware': 500,
}

USER_AGENTS = [
    ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 '
     '(KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36 OPR/63.0.3368.75'),
    ('Mozilla/5.0 (X11; Linux x86_64) '
     'AppleWebKit/537.36 (KHTML, like Gecko) '
     'Chrome/57.0.2987.110 '
     'Safari/537.36'),  # chrome
    ('Mozilla/5.0 (X11; Linux x86_64) '
     'AppleWebKit/537.36 (KHTML, like Gecko) '
     'Chrome/61.0.3163.79 '
     'Safari/537.36'),  # chrome
    ('Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) '
     'Gecko/20100101 '
     'Firefox/55.0'),  # firefox
    ('Mozilla/5.0 (X11; Linux x86_64) '
     'AppleWebKit/537.36 (KHTML, like Gecko) '
     'Chrome/61.0.3163.91 '
     'Safari/537.36'),  # chrome
    ('Mozilla/5.0 (X11; Linux x86_64) '
     'AppleWebKit/537.36 (KHTML, like Gecko) '
     'Chrome/62.0.3202.89 '
     'Safari/537.36'),  # chrome
    ('Mozilla/5.0 (X11; Linux x86_64) '
     'AppleWebKit/537.36 (KHTML, like Gecko) '
     'Chrome/63.0.3239.108 '
     'Safari/537.36'),  # chrome
]

###################
# PRODUCER SETTINGS
###################

BOT_NAME = 'otodom'


#################
# OUTPUT SETTINGS
#################

# SELECT WHERE TO CHECK
SOURCE = 'LOCAL'

# MONGO
MONGO_ADDRESS = 'localhost'
MONGO_PORT = 27017
MONGO_DBNAME = 'OFFERS'
MONGO_USERNAME = os.environ['MONGO_USERNAME']
MONGO_PASSWORD = os.environ['MONGO_PASSWORD']
ID_FIELD = '_id'
DOWNLOAD_DATE = 'download_date'

# S3
BUCKET_NAME = 'mojewiadroxszpo'

# local
LOCAL_FILE_PATH = "/Users/xszpo/GoogleDrive/DataScience/Projects/201907_xFlat_AWS_Scrapy/app_web/data.jsonline"

# kafka
KAFKA_HOST = "0.0.0.0"
KAFKA_PORT = "9092"

##########
# PIELINES
##########

ITEM_PIPELINES = {
    'scraper.pipelines.ProcessItem': 100,
    'scraper.pipelines.CheckIfExistMongo': 105,
    'scraper.pipelines.OutputFilter': 110,
    'scraper.pipelines.ProcessItemGeocode': 115,
    #'scraper.pipelines.OutputLocal': 201,
    'scraper.pipelines.OutputMongo': 202,
    #'scraper.pipelines.OutputS3': 203,
    #'scraper.pipelines.OutputKafka': 401,
    #'scraper.pipelines.OutputStdout': 402
}
