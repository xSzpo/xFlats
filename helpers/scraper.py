import logging

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


logger = logging.getLogger(__name__)


def list_bucket(bucket_name, prefix='offers_bson/'):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    list_files_in_offers_list = [i.key[len(prefix):] for i in bucket.objects.filter(Prefix=prefix)]
    return list_files_in_offers_list


def write_S3_bucket(object, file_name, bucket_name, prefix='offers_bson/'):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    return bucket.put_object(Key=prefix+file_name, Body=object)


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


def write_bson(file_path_, data_):
    data_b_ = bson.BSON.encode(data_)
    with open(file_path_,'w') as f:
        f.write(dumps(data_b_))


def read_bson(file_path_):
    with open(file_path_,'r') as f:
        d=bson.BSON.decode(loads(f.read()))
    return d