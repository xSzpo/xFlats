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
import pandas as pd
#import geopandas
import json

logger = logging.getLogger(__name__)

def timer(start,end):
    hours, rem = divmod(end-start, 3600)
    minutes, seconds = divmod(rem, 60)
    return "{:0>2}:{:0>2}:{:05.2f}".format(int(hours),int(minutes),seconds)

def list_bucket(bucket_name, prefix='offers_bson/'):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    list_files_in_offers_list = [i.key[len(prefix):] for i in bucket.objects.filter(Prefix=prefix)]
    return list_files_in_offers_list


def list_local(path):
    return os.listdir(path)


def write_s3_bucket(object_file, file_name, bucket_name, prefix='offers_bson/'):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    return bucket.put_object(Key=prefix+file_name, Body=object_file)


def write_local(object_file, path, file_name):
    with open(os.path.join(path, file_name), 'w') as f:
        f.write(object_file)


def read_bson_local(path, file_name):
    with open(os.path.join(path, file_name), 'rb') as f:
        x = bson.BSON.decode(loads(f.read()))
    return x


def load_bson_s3(file_name, bucket_name, prefix='offers_bson/'):
    client = boto3.client('s3')
    file = client.get_object(Bucket=bucket_name, Key = prefix+file_name)['Body'].read()
    return bson.BSON.decode(loads(file))


def current_timestamp():
    return int(datetime.datetime.now().timestamp())


def contains_digit(x):
    return np.any([i.isdigit() for i in x])


#def get_geodata(content, compressed=False):
#    content = bz2.decompress(content) if compressed else content
#
#    list_geo = re.findall('geo..\{(.*?)\}', content.decode("utf-8"))
#    text = [row for row in list_geo if contains_digit(row)][0]
#    text = text.replace('"', '')
#
#    geocoordinates = dict([i.split(":") for i in text.split(",")])

    address = requests.get(
        "https://nominatim.openstreetmap.org/reverse?format=xml&lat={latitude}&lon={longitude}&zoom=18&addressdetails=1".format(
            **geocoordinates)
    )

    address_text = xmltodict.parse(address.content)['reversegeocode']['addressparts']

    address_coordin = xmltodict.parse(address.content)['reversegeocode']['result']

    return geocoordinates, address_text, address_coordin


def download_img_url(url):
    bytes_first_img=requests.get(url).content
    first_img = Image.open(BytesIO(bytes_first_img))
    return first_img


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


def byte_img_to_str(image):
    """take PIL.Image.Image object and converts to string
    helper function to save image in bson
    :param image:
    :return:
    """

    try:
        imgbytearr = BytesIO()
        image.save(imgbytearr,'JPEG', quality=90)
        imgbytearr = imgbytearr.getvalue()
        return imgbytearr
    except BaseException:
        return None


def imgurl2str(url):
    img = download_img_url(url)
    img = resize_img(img)
    img = byte_img_to_str(img)
    return img


def open_img_from_str(str_img):
    try:
        return Image.open(BytesIO(str_img))
    except BaseException:
        return None


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


def concat_dict(dict_list):
    return reduce(lambda x, y: dict(x, **y), dict_list)


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


def read_bus_gpd(path, file, X = "X", Y="Y"):
    with codecs.open(os.path.join(path,file), "r", "utf-8") as file:
        bus_stops_json = json.loads(file.read())
    bus_stops_df = pd.DataFrame(bus_stops_json)
    bus_stops_gdf = geopandas.GeoDataFrame(
        bus_stops_df, geometry=geopandas.points_from_xy(bus_stops_df[X], bus_stops_df[Y]))
    return bus_stops_gdf


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

