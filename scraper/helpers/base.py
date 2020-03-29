import logging
import os
import boto3
import datetime
import requests
import xmltodict
import re
import numpy as np
import bson
from bson.json_util import dumps, loads
from functools import reduce
import codecs
import pytz
import gc
from dateutil.parser import parse
from scrapy import logformatter
from scrapy.exceptions import DropItem

logger = logging.getLogger(__name__)


class PoliteLogFormatter(logformatter.LogFormatter):
    def dropped(self, item, exception, response, spider):
        if '_id' in item.keys():
            return {
                'level': logging.INFO,
                'msg': u"Dropped item %s" % item['_id'],
                'args': {
                    'exception': exception,
                    'item': item,
                }
            }
        else:
            return {
                'level': logging.INFO,
                'msg': u"Dropped item, exception: %s" % exception,
                'args': {
                    'exception': exception,
                    'item': item,
                }
            }


class FilesS3:

    @staticmethod
    def list_files(settings):
        bucket_name = settings['BUCKET_NAME']
        prefix = settings['BUCKET_PREFIX_BSON']

        logger.info("S3: Read list of files")
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(bucket_name)
        list_files_in_offers_list = [i.key[len(prefix):] for i in bucket.objects.filter(Prefix=prefix)]
        logger.info("S3: Read list of files is done, its {} of files".format(len(list_files_in_offers_list)))
        return list_files_in_offers_list

    @staticmethod
    def check_if_exists(offer_id, settings):
        bucket_name = settings['BUCKET_NAME']
        prefix = settings['BUCKET_PREFIX_BSON']
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(bucket_name)
        return True if len([i.key for i in bucket.objects.filter(Prefix=prefix+offer_id)]) > 0 else False

    @staticmethod
    def write_file(object_file, file_name, settings):
        bucket_name = settings['BUCKET_NAME']
        prefix = settings['BUCKET_PREFIX_BSON']
        data_b_ = dumps(bson.BSON.encode(object_file))
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(bucket_name)
        w = bucket.put_object(Key=prefix+file_name+".bson", Body=data_b_)
        logger.info("S3: save offer {} to S3, {}".format(file_name, w))
        pass

    @staticmethod
    def read_file(file_name, settings):
        bucket_name = settings['BUCKET_NAME']
        prefix = settings['BUCKET_PREFIX_BSON']
        client = boto3.client('s3')
        file = client.get_object(Bucket=bucket_name, Key=prefix+file_name+".bson")['Body'].read()
        return bson.BSON.decode(loads(file))


class FilesLocal:

    @staticmethod
    def list_files(settings):
        path = settings['LOCAL_DATA_DIR']
        logger.info("Local: Read list of files")
        list_ = os.listdir(path)
        logger.info("Local: Read list of files is done, its {} of files".format(len(list_)))
        return list_

    @staticmethod
    def check_if_exists(offer_id, settings):
        path = settings['LOCAL_DATA_DIR']
        return os.path.exists(os.path.join(path, offer_id))

    @staticmethod
    def write_file(object_file, file_name, settings):
        path = settings['LOCAL_DATA_DIR']
        data_b_ = dumps(bson.BSON.encode(object_file))
        with codecs.open(os.path.join(path, file_name+".bson"), 'w', encoding='utf-8') as f:
            f.write(data_b_)
        logger.info("Local: save offer {} to local disk".format(file_name))
        pass

    @staticmethod
    def read_file(file_name, settings):
        path = settings['LOCAL_DATA_DIR']
        with codecs.open(os.path.join(path, file_name+".bson"), 'rb', encoding='utf-8') as f:
            x = bson.BSON.decode(loads(f.read()))
        return x


class Time:

    @staticmethod
    def timer(start, end):
        hours, rem = divmod(end-start, 3600)
        minutes, seconds = divmod(rem, 60)
        return "{:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds)


class Scraper:

    @staticmethod
    def current_timestamp():
        return int(datetime.datetime.now().timestamp())

    @staticmethod
    def current_datetime():
        return datetime.datetime.utcnow()
        # return datetime.datetime.now(pytz.timezone("Europe/Warsaw"))

    @staticmethod
    def datetime2str(dt):
        if isinstance(dt, datetime.datetime):
            return dt.__str__()

    @staticmethod
    def timestamp2datetime(timestamp):
        return datetime.datetime.fromtimestamp(timestamp)

    @staticmethod
    def contains_digit(x):
        return np.any([i.isdigit() for i in x])

    @staticmethod
    def dict_except(dictionary, except_keys=[], include_keys=None):
        temp = {}
        for key in dictionary:
            if key not in except_keys:
                if include_keys is None:
                    temp[key] = dictionary[key]
                else:
                    if key in include_keys:
                        temp[key] = dictionary[key]
        return temp

    @staticmethod
    def concat_dict(dict_list):
        return reduce(lambda x, y: dict(x, **y), dict_list)

    @staticmethod
    def digits_from_str(txt, returntype=float):
        """return numbers from string '523 000 zł' -> 523000,

        :param:
        txt - text that contains number
        :return:
        int
        """
        if txt and re.search('[\d., ]{1,}', txt):
            result = re.sub(",", ".", re.sub(r" +", "", re.findall('[\d., ]{1,}', txt)[-1]))
            if len(result) == 0:
                return None
            else:
                if returntype == int:
                    return int(float(result))
                elif returntype == float:
                    return float(result)
        else:
            return None


    @staticmethod
    def convert_floor(x):
        if x:
            if str(x).isdigit():
                return int(x)
            elif x.lower() == 'parter':
                return int(0)
            elif x.lower() == 'suterena':
                return None
            elif x == '> 10':
                return int(11)
            elif x.lower() == 'powyżej 10':
                return int(11)
            elif x.lower() == 'powyżej 30':
                return int(11)
            elif x == 'poddasze':
                return None
            else:
                return None
        else:
            return None

    @staticmethod
    def get_createdate_from_otodom(body):
        daty = re.findall(r'"dateCreated":"20\d\d-[01]\d-[0-3]\d [0-3]\d:[0-5]\d:[0-5]\d","dateModified":"20\d\d-[01]\d-[0-3]\d [0-3]\d:[0-5]\d:[0-5]\d"', str(body))[-1]
        daty = [i.replace(':', '|', 1).split("|") for i in daty.
                replace('"', '').split(",")]
        daty = {daty[0][0]: parse(daty[0][1]), daty[1][0]: parse(daty[1][1])}
        return (Scraper.datetime2str(daty['dateCreated']),
                Scraper.datetime2str(daty['dateModified']))


class Geodata:

    @staticmethod
    def get_geodata_otodom(content):

        list_geo = re.findall('geo..\{(.*?)\}', content.decode("utf-8"))
        text = [row for row in list_geo if Scraper.contains_digit(row)][0]
        text = text.replace('"', '')
        geocoordinates = dict([i.split(":") for i in text.split(",")])

        return geocoordinates

    @staticmethod
    def get_geodata_olx(content):

        data_lat = re.findall("data-lat.{2}[\d]{2}.[\d]{8}.", content.decode("utf-8"))[0]
        data_lat = "".join([i for i in data_lat if i.isdigit() or i == "."])
        data_lon = re.findall("data-lon.{2}[\d]{2}.[\d]{8}.", content.decode("utf-8"))[0]
        data_lon = "".join([i for i in data_lon if i.isdigit() or i == "."])
        geocoordinates = {"latitude": data_lat, "longitude": data_lon}

        return geocoordinates

    @staticmethod
    def get_geodata_gratka(content):

        data_lat = re.findall("szerokosc-geograficzna-y..[\d]{2}\\.[\d]+", content.decode("utf-8"))[0]
        data_lat = "".join([i for i in data_lat if i.isdigit() or i == "."])
        data_lon = re.findall("dlugosc-geograficzna-x..[\d]{2}\\.[\d]+", content.decode("utf-8"))[0]
        data_lon = "".join([i for i in data_lon if i.isdigit() or i == "."])
        geocoordinates = {"latitude": data_lat, "longitude": data_lon}

        return geocoordinates

    @staticmethod
    def get_geocode_openstreet(geocoordinates):

        try:
            address = requests.get(
                "https://nominatim.openstreetmap.org/reverse?format=xml&lat={latitude}&lon={longitude}&zoom=18&addressdetails=1".format(
                    **geocoordinates)
            )

            address_text = xmltodict.parse(address.content)['reversegeocode']['addressparts']

            address_coordin = xmltodict.parse(address.content)['reversegeocode']['result']

            return geocoordinates, address_text, address_coordin
        except BaseException as e:
            raise DropItem("Openstreetmap error, " % e)