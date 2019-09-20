import logging
import os
import boto3
import datetime
import bz2
import requests
import xmltodict
import re
import numpy as np
from PIL import Image
import PIL
from io import BytesIO
import bson
from bson.json_util import dumps, loads
from functools import reduce
import codecs
import pymongo
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, WriteError, WriteConcernError, WTimeoutError
import gc

logger = logging.getLogger(__name__)


class FilesMongo:

    @staticmethod
    def set_connection(address, port, database, collection, username='', password=''):
        """
        https://www.programiz.com/python-programming/property
        :return:
            pymongo conetion
        """

        try:
            if username == '':
                conn = pymongo.MongoClient(host=address, port=port, serverSelectionTimeoutMS=5000)
            else:
                conn = pymongo.MongoClient(host=address, port=port, username=username, password=password,
                                           authSource='admin', authMechanism='SCRAM-SHA-256',
                                           serverSelectionTimeoutMS=5000)

            logger.info("Connected to MongoDB {}, address: {}:{}".format(conn.server_info()['version'],
                                                                         address, port))
            return conn[database][collection]

        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error("pymongo.errors, Could not connect to server: %s" % e)

        except BaseException as e:
            logger.error("BaseException, something went wrong: %s" % e)

    @staticmethod
    def list_files(db, id_field='_id', download_date='download_date'):
        db.create_index([(download_date, 1)])
        logger.info("MongoDB: Read list of files")
        list_ = [i[id_field] for i in db.find({}, {id_field: 1})]
        logger.info("MongoDB: Read list of files is done, its {} of files".format(len(list_)))
        gc.collect()
        return list_

    @staticmethod
    def write_file(object_file, db, id_field='_id'):
        try:
            w = db.update_one({id_field: object_file[id_field]}, {"$set": object_file}, upsert=True)
            logger.info("MongoDB: save offer {} to mongodb, {}".format(object_file[id_field],w))
            pass

        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error("pymongo.errors, Could not connect to server: %s" % e)
        except (WriteError, WriteConcernError, WTimeoutError) as e:
            logger.error("pymongo.errors, Write error: %s" % e)
        except BaseException as e:
            logger.error("BaseException, something went wrong: %s" % e)

    @staticmethod
    def read_file(id, db, id_field='_id'):
        file = None
        for i in db.find({id_field: id}):
            file = i
        return file


class FilesS3:

    @staticmethod
    def list_files(bucket_name, prefix='offers_bson/'):
        logger.info("S3: Read list of files")
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(bucket_name)
        list_files_in_offers_list = [i.key[len(prefix):] for i in bucket.objects.filter(Prefix=prefix)]
        logger.info("S3: Read list of files is done, its {} of files".format(len(list_files_in_offers_list)))
        return list_files_in_offers_list

    @staticmethod
    def write_file(object_file, file_name, bucket_name, prefix='offers_bson/'):
        data_b_ = dumps(bson.BSON.encode(object_file))
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(bucket_name)
        w = bucket.put_object(Key=prefix+file_name+".bson", Body=data_b_)
        logger.info("S3: save offer {} to S3, {}".format(file_name, w))
        pass

    @staticmethod
    def read_file(file_name, bucket_name, prefix='offers_bson/'):
        client = boto3.client('s3')
        file = client.get_object(Bucket=bucket_name, Key=prefix+file_name+".bson")['Body'].read()
        return bson.BSON.decode(loads(file))


class FilesLocal:
    @staticmethod
    def list_files(path):
        logger.info("Local: Read list of files")
        list_ = os.listdir(path)
        logger.info("Local: Read list of files is done, its {} of files".format(len(list_)))
        return list_

    @staticmethod
    def write_file(object_file, path, file_name):
        data_b_ = dumps(bson.BSON.encode(object_file))
        with codecs.open(os.path.join(path, file_name+".bson"), 'w', encoding='utf-8') as f:
            f.write(data_b_)
        logger.info("Local: save offer {} to local disk".format(file_name))
        pass

    @staticmethod
    def read_file(path, file_name):
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
    def contains_digit(x):
        return np.any([i.isdigit() for i in x])

    @staticmethod
    def download_img_url(url):
        bytes_first_img=requests.get(url).content
        first_img = Image.open(BytesIO(bytes_first_img))
        return first_img

    @staticmethod
    def resize_img(img, basewidth=300):
        if max(img.size[0], img.size[1]) < basewidth:
            return img
        elif img.size[0] >= img.size[1]:
            hpercent = (basewidth / float(img.size[1]))
            wsize = int((float(img.size[0]) * float(hpercent)))
            return img.resize((wsize, basewidth), PIL.Image.ANTIALIAS)
        else:
            wpercent = (basewidth / float(img.size[0]))
            hsize = int((float(img.size[1]) * float(wpercent)))
            return img.resize((basewidth, hsize), PIL.Image.ANTIALIAS)

    @staticmethod
    def byte_img_to_str(image):
        """take PIL.Image.Image object and converts to string
        helper function to save image in bson
        :param image:
        :return:
        """

        try:
            imgbytearr = BytesIO()
            image.save(imgbytearr, 'JPEG', quality=90)
            imgbytearr = imgbytearr.getvalue()
            return imgbytearr
        except BaseException:
            return None

    @staticmethod
    def imgurl2str(url):
        img = Scraper.download_img_url(url)
        img = Scraper.resize_img(img)
        img = Scraper.byte_img_to_str(img)
        return img

    @staticmethod
    def open_img_from_str(str_img):
        try:
            return Image.open(BytesIO(str_img))
        except BaseException:
            return None

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
    def digits_from_str(txt):
        """return numbers from string
        return numbers from string ex. '523 000 zł' -> 523000,

        :param:
        txt - text that contains number
        :return:
        int
        """
        result = "".join([i for i in txt if ((i.isdigit() and i != '²') or (i in (',', '.')))]).replace(",", ".")
        return float(result) if len(result) > 0 else None

    @staticmethod
    def convert_floor(x):
        if x.isdigit():
            return int(x)
        elif x == 'parter':
            return 0
        elif x == 'suterena':
            return np.NaN
        elif x == '> 10':
            return 11
        elif x == 'poddasze':
            return np.NaN
        else:
            return np.NaN


class Geodata:

    @staticmethod
    def get_geodata(content, compressed=False):
        content = bz2.decompress(content) if compressed else content

        list_geo = re.findall('geo..\{(.*?)\}', content.decode("utf-8"))
        text = [row for row in list_geo if Scraper.contains_digit(row)][0]
        text = text.replace('"', '')

        geocoordinates = dict([i.split(":") for i in text.split(",")])

        address = requests.get(
            "https://nominatim.openstreetmap.org/reverse?format=xml&lat={latitude}&lon={longitude}&zoom=18&addressdetails=1".format(
                **geocoordinates)
        )

        address_text = xmltodict.parse(address.content)['reversegeocode']['addressparts']

        address_coordin = xmltodict.parse(address.content)['reversegeocode']['result']

        return geocoordinates, address_text, address_coordin
