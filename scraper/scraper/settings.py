import os
# -*- coding: utf-8 -*-

# Scrapy settings for app_webscr_pipe_otodom project
#
# You can find more settings consulting the documentation:
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

ID_FIELD = '_id'
DOWNLOAD_DATE = 'download_date'

# REDIS
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB_INDEX = 0

# S3
BUCKET_NAME = 'mojewiadroxszpo'

# GCP Firestore
COLLECTION = 'flats'
SECRETS_PATH = "/Users/xszpo/GoogleDrive/01_Projects/201907_xFlats/secrets/flats-e6f6e1b4b129.json"
FIRESTORE_DROP_KEYS = ['body']
FIRESTORE_STR2DATE = ['download_date', 'date_created', 'date_modified']

# local

LOCAL_FILE_DIR = "/Users/xszpo/GoogleDrive/01_Projects/201907_xFlats/scraper/data/"
LOCAL_FILE_NAME = "data_XX"
ADDDATE2NAME = True

# schema
SCHEMA_FILE_NAME = 'schema.json'

##########
# PIELINES
##########

ITEM_PIPELINES = {
    'scraper.pipelines.ProcessItem': 100,
    #'scraper.pipelines.CheckIfExistRedis': 104,
    #'scraper.pipelines.CheckIfExistGCPFirestore': 108,
    'scraper.pipelines.OutputFilter': 110,
    'scraper.pipelines.ProcessItemGeocode': 115,
    'scraper.pipelines.ValidSchema': 116,
    'scraper.pipelines.OrderbySchema': 117,
    'scraper.pipelines.OutputLocal': 201,
    #'scraper.pipelines.OutputGCPFirestore': 202,
    #'scraper.pipelines.OutputRedis': 204,
    #'scraper.pipelines.OutputStdout': 402
}
