# -*- coding: utf-8 -*-

#FEED_URI = 'wynik.jsonl'
#FEED_FORMAT = 'jsonlines'
#FEED_EXPORT_ENCODING = 'utf-8'
#LOG_FILE = 'scrapy.log'
#FEED_URI = 's3://31b179a9-539e-4d1d-9686-3136fe76b662/%(name)s/%(time)s.jsonlines'

BOT_NAME = 'daniel'

# max following pages
MAX_PAGES = 1


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

# otodom doesnt accept fake USER-AGENT, better set nothing

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# S3

BUCKET_NAME = '31b179a9-539e-4d1d-9686-3136fe76b662'
BUCKET_PREFIX_BSON = 'offers_bson_new/'
FEED_FORMAT = 'jsonlines'

#CUSTOM_PROXY = "http://83.12.149.202:8080"
