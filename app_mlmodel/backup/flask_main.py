#!/usr/bin/python
# coding: utf-8

from flask import Flask, request, jsonify
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
import train


LOG = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
                    format="'%(asctime)s - %(name)s - %(levelname)s "
                    "- %(message)s'")

app = Flask(__name__)

np.random.seed(666)
random.seed(666)
os.environ['PYTHONHASHSEED'] = str(666)


@app.route('/predict', methods=['POST'])
def predict():
    if type(request.data) == bytes:
        request_data = request.data.decode("utf-8")
    else:
        request_data = request.data
    json_ = json.loads(request_data)
    if type(json_) == dict:
        json_ = sorted([json_], key=lambda i: i['_id'])
    else:
        json_ = sorted(json_, key=lambda i: i['_id'])
    LOG.debug("Predict {} record/s".format(len(json_)))
    prediction = list(clf.predict(json_))
    results = list()
    for i, predict in enumerate(prediction):
        json_[i]['prediction'] = int(predict)
        json_[i]['model_name'] = model_path.split("/")[-1]
    return jsonify(json_), 200, {"mimetype": "application/json"}


@app.route('/predictone', methods=['POST'])
def predictone():
    if type(request.data) == bytes:
        request_data = request.data.decode("utf-8")
    else:
        request_data = request.data
    json_ = json.loads(request_data)
    LOG.debug("Predict(one) {}".format(json_['_id']))
    prediction = list(clf.predict(json_))
    json_['prediction'] = int(prediction[0])
    json_['model_name'] = model_path.split("/")[-1]

    return jsonify(json_), 200, {"mimetype": "application/json"}


@app.route('/train', methods=['GET'])
def train_model():
    mode = request.args.get('dev')
    score = train.main_train(mode=mode)
    return jsonify({'score': score}), 200, {"mimetype": "application/json"}


if __name__ == '__main__':
    from waitress import serve

    models = os.listdir("model")
    models = list(filter(lambda x: re.findall("model_[\d]", x), models))
    if bool(models):
        model_path = os.path.join('model', max(models))
    else:
        model_path = 'model/model_default.pkl'

    clf = joblib.load(model_path)
    LOG.info("zaladowano model: %s" % model_path)
    serve(app, host="0.0.0.0", port=8666)
