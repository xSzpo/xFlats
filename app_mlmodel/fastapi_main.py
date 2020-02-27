#!/usr/bin/python
# coding: utf-8

from fastapi import FastAPI, Body
import uvicorn
import joblib
import pandas as pd
import numpy as np
import json
import random
import os
import re
import logging
import sys
import warnings
import numpy as np
from helpers import train
from helpers.fastapi_schema import *

LOG = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
                    format="'%(asctime)s - %(name)s - %(levelname)s "
                    "- %(message)s'")


np.random.seed(666)
random.seed(666)
os.environ['PYTHONHASHSEED'] = str(666)


def load_request_data_excample():
    with open('helpers/predict_data_example.json', 'r') as json_file:
        json_data_example = json.load(json_file)
    return json_data_example


def load_model():

    models = os.listdir("model")
    models = list(filter(lambda x: re.findall("model_[\d]", x), models))

    if bool(models):
        model_path = os.path.join('model', max(models))
    else:
        model_path = 'model/model_default.pkl'

    clf = joblib.load(model_path)
    LOG.info("zaladowano model: %s" % model_path)
    return clf, model_path


app = FastAPI()

clf, model_path = load_model()
json_data_example = load_request_data_excample()


@app.get("/healthcheck", tags=['Service check'])
def healthcheck():
    """Heltcheck - returns 'OK' message"""
    msg = (
        "OK"
    )
    return {"msg": msg}


@app.post('/predictone', tags=['Estimate flat price'],
          response_model=RequestBodyOut)
def predictone(body: RequestBodyIn = Body(..., example=json_data_example)):
    """Estimates flat market price given data.
    Designed to handle request with one flats data (single json).
    Takes the newest available pickled model from a direcotry "./model".
    Returns input data plus prediction.
    """

    json_ = body.dict(by_alias=True)
    print(json_)
    LOG.debug("Predict(one) {}".format(json_['_id']))
    prediction = list(clf.predict(json_))
    json_['prediction'] = int(prediction[0])
    json_['model_name'] = model_path.split("/")[-1]
    return json_


@app.post('/predict', tags=['Estimate flat price'],
          response_model=RequestBodyListOut)
def predict(body: RequestBodyListIn = Body(...,
            example={"data": [json_data_example, json_data_example]})):
    """Estimates flats market price given data.
    Designed to handle request with multiople flats data (list of json).
    Takes the newest available pickled model from a direcotry "./model".
    Returns input data plus prediction.
    """

    json_ = [i.dict(by_alias=True) for i in body.data]
    json_ = sorted(json_, key=lambda i: i['_id'])
    LOG.debug("Predict {} record/s".format(len(json_)))
    prediction = list(clf.predict(json_))
    results = list()
    for i, predict in enumerate(prediction):
        json_[i]['prediction'] = int(predict)
        json_[i]['model_name'] = model_path.split("/")[-1]
    return {"data": json_}


@app.get("/train/{mode}", tags=['Retrain model'])
async def train_model(mode: TrainMode):
    """Retrains ML model.
    Takes all available data from DB. Splits it in:

    - **OOT*** - last 3 days of data if its not more then 10% of all data, else
                 last 6 hours of data,
    - **Train** - 85% of data (not includingOOT),
    - **Test** - 15% of data (not includingOOT),

    Avilible mods are:
    - **DEVELOPMENT** - take data from mongoDB that is running as a separate
                        instance,
    - **DOCKER** - take data from mongoDB that is running as a container inside
                   service together with fastApi model service,
    Saves new model in a direcotry "./model" with name
    "model_YYYYmmddHHMMSS.pkl" ex. model_20200227173047.pkl, and model summary
    in txt file with the same name as model.
    """
    score = train.main_train(mode=mode.value)
    return {'score': score}


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8666)
