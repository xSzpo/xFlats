# -*- coding: utf-8 -*-

# Scrapy settings for app_webscr_pipe_otodom project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

# GENERAL INFO
BOT_NAME = 'otodom'
SPIDER_MODULES = ['scraper.spiders']
NEWSPIDER_MODULE = 'scraper.spiders'

# CRAWL SETTING
CONCURRENT_REQUESTS = 2
COOKIES_ENABLED = False
DOWNLOAD_DELAY = 0.5
LOGSTATS_INTERVAL = 0
LOG_LEVEL = 'INFO'
ROBOTSTXT_OBEY = True
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36 OPR/63.0.3368.75'

CRAWL_PAGES = 1

FEED_EXPORT_ENCODING = "UTF-8"

#OUTPUT SETTING

#local
LOCAL_FILE_PATH = "/Users/xszpo/Google Drive/DataScience/Projects/201907_xFlat_AWS_Scrapy/app_webscr_pipe_otodom/data.jsonline"

#kafka
KAFKA_TOPIC = "xflats"
KAFKA_HOST = "0.0.0.0"
KAFKA_PORT = "9092"

#PIELINES

ITEM_PIPELINES = {
    'scraper.pipelines.OtodomListProcess': 300,
    'scraper.pipelines.OutputLocal': 400,
    'scraper.pipelines.OutputKafka': 401,
    #'scraper.pipelines.OutputStdout': 402
}
