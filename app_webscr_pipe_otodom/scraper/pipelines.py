# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import json
import numpy as np
import re
import sys
sys.path.append("..")
import helpers


class OtodomListProcess(object):
    def process_item(self, item, spider):

        item['gallery'] = json.loads(item['gallery'])
        item['price'] = float(np.float32(helpers.Scraper.digits_from_str(item['price']))) if item[
                                                                                 'price'] is not None else None
        item['tracking_id'] = int(helpers.Scraper.digits_from_str(item['tracking_id'])) if \
            item['tracking_id'] is not None else None
        item['offer_title'] = item['offer_title'].strip() if item['offer_title'] is not None else None
        price_str = str(int(item['price'])) if item['price'] is not None else ""
        item['file_name'] = str(item["tracking_id"]) + "_" + price_str

        selected_col = ['file_name','offer_title', 'price', 'tracking_id', 'url',
                        'url_offer_list', 'producer_name', 'main_url','gallery']

        tmp = {}
        for key in selected_col:
            tmp[key] = item[key]

        return tmp