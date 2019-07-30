import logging

import boto3
import datetime
import bz2
import requests
import xmltodict
import re
import numpy as np

logger = logging.getLogger(__name__)


def list_bucket(bucket_name, prefix='offers_bson/'):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    list_files_in_offers_list = [i.key[len(prefix):] for i in bucket.objects.filter(Prefix=prefix)]
    return list_files_in_offers_list


def current_timestamp():
    return int(datetime.datetime.now().timestamp())


def contains_digit(x):
    return np.any([i.isdigit() for i in x])


def get_geodata(content, compressed=False):
    content = bz2.decompress(content) if compressed else content

    list_geo = re.findall('geo..\{(.*?)\}', content.decode("utf-8"))
    text = [row for row in list_geo if contains_digit(row)][0]
    text = text.replace('"', '')

    geocoordinates = dict([i.split(":") for i in text.split(",")])

    address = requests.get(
        "https://nominatim.openstreetmap.org/reverse?format=xml&lat={latitude}&lon={longitude}&zoom=18&addressdetails=1".format(
            **geocoordinates)
    )

    address_text = xmltodict.parse(address.content)['reversegeocode']['addressparts']

    address_coordin = xmltodict.parse(address.content)['reversegeocode']['result']

    return geocoordinates, address_text, address_coordin
