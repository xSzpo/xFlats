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

    np.random.seed(666)
    random.seed(666)
    os.environ['PYTHONHASHSEED'] = str(666)
    prediction = list(clf.predict(json_))

    for i, predict in enumerate(prediction):
        json_[i]['prediction'] = int(predict)

    return jsonify(json_)


@app.route('/train', methods=['GET'])
def train_model():
    mode = request.args.get('dev')
    score = train.main_train(mode=mode)
    return jsonify({'score': score})


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
