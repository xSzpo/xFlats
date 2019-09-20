# -*- coding: utf-8 -*-

#FEED_URI = 'wynik.jsonl'
#FEED_FORMAT = 'jsonlines'
#FEED_EXPORT_ENCODING = 'utf-8'
#LOG_FILE = 'scrapy.log'
#FEED_URI = 's3://31b179a9-539e-4d1d-9686-3136fe76b662/%(name)s/%(time)s.jsonlines'

BOT_NAME = 'daniel'

# max following pages
MAX_PAGES = 1

# save results to S3 or local
SAVE_RESULTS = ['MONGODB', 'LOCAL', 'S3'] #['LOCAL','S3','MONGODB']

# SAVE_RESULTS: local
LOCAL_DATA_PATH = '/Users/xszpo/Google Drive/DataScience/DATA/01_otodom_scrapy'
LOCAL_DATA_PATH_PREP = '/Users/xszpo/Google Drive/DataScience/DATA/01_otodom_scrapy_prepred'
LOCAL_DATA_PATH_DICT = '/Users/xszpo/Google Drive/DataScience/DATA/DICT'

# SAVE_RESULTS: S3
BUCKET_NAME = '31b179a9-539e-4d1d-9686-3136fe76b662'
BUCKET_PREFIX_BSON = 'offers_bson_new/'
#FEED_FORMAT = 'jsonlines'

# SAVE_RESULTS: MONGO
#MONGO_ADDRESS = 'localhost'
MONGO_ADDRESS = 'mongo'
MONGO_PORT = 27017
MONGO_DBNAME = 'OFFERS'
MONGO_COLL_OTODOM = 'Otodom'
MONGO_USERNAME = 'xflats'
MONGO_PASSWORD = 'xflats'

# how many images download
DOWNLOAD_IMAGES = 3

SPIDER_MODULES = ['scraper.spiders']
NEWSPIDER_MODULE = 'scraper.spiders'

LOG_ENABLE = True
LOG_LEVEL = 'INFO'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
DOWNLOAD_DELAY = 0.5    # 250 ms of delay
RANDOMIZE_DOWNLOAD_DELAY = True

CONCURRENT_REQUESTS = 2

# https://developers.whatismybrowser.com
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36 OPR/63.0.3368.75"

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

