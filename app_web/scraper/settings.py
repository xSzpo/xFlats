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

BOT_NAME = 'otodom'
SPIDER_MODULES = ['scraper.spiders']
NEWSPIDER_MODULE = 'scraper.spiders'
LOG_LEVEL = 'INFO'
FEED_EXPORT_ENCODING = "UTF-8"

################
# CRAWL SETTINGS
################

COOKIES_ENABLED = False
ROBOTSTXT_OBEY = True
CONCURRENT_REQUESTS = 2
DOWNLOAD_DELAY = 0.5
LOGSTATS_INTERVAL = 0
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36 OPR/63.0.3368.75'
CRAWL_LIST_PAGES = 2 #how many pages with links you want to crawl (start pages)
DOWNLOAD_IMAGES = 3

#################
# OUTPUT SETTINGS
#################

# SELECT WHERE TO CHECK
SOURCE = 'LOCAL'

# MONGO
MONGO_ADDRESS = 'localhost'
#MONGO_ADDRESS = 'mongo'
MONGO_PORT = 27017
MONGO_DBNAME = 'OFFERS'
MONGO_COLL_OTODOM = 'Otodom'
MONGO_USERNAME = 'xflats'
MONGO_PASSWORD = 'xflats'
ID_FIELD = '_id'
DOWNLOAD_DATE = 'download_date'

# S3
BUCKET_NAME = 'mojewiadroxszpo'
BUCKET_PREFIX_BSON = 'offers_bson/'

# local
LOCAL_DATA_DIR = '/Users/xszpo/Google Drive/DataScience/DATA/01_otodom_scrapy'
LOCAL_FILE_PATH = "/Users/xszpo/Google Drive/DataScience/Projects/201907_xFlat_AWS_Scrapy/app_web/data.jsonline"

# kafka
KAFKA_TOPIC = "xflats"
KAFKA_HOST = "0.0.0.0"
KAFKA_PORT = "9092"

##########
# PIELINES
##########

SOURCE = 'MONGO'

ITEM_PIPELINES = {
    'scraper.pipelines.ProcessListOtodom': 300,
    #'scraper.pipelines.OutputLocal': 400,
    #'scraper.pipelines.OutputKafka': 401,
    'scraper.pipelines.OutputStdout': 402
}
