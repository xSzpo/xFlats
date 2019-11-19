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
import train


LOG = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
                    format="'%(asctime)s - %(name)s - %(levelname)s "
                    "- %(message)s'")


app = Flask(__name__)


@app.route('/predict', methods=['POST'])
def predict():
    json_ = json.loads(request.data)
    np.random.seed(666)
    random.seed(666)
    os.environ['PYTHONHASHSEED'] = str(666)
    prediction = clf.predict(json_)
    prediction = np.expm1(prediction)
    return jsonify({'prediction': list(prediction)})


@app.route('/train', methods=['GET'])
def train_model():
    mode = request.args.get('dev')
    score = train.main_train(mode=mode)
    return jsonify({'score': score})


if __name__ == '__main__':

    models = os.listdir("model")
    models = list(filter(lambda x: re.findall("model_[\d]", x), models))
    if bool(models):
        model_path = os.path.join('model', max(models))
    else:
        model_path = 'model/model_default.pkl'

    clf = joblib.load(model_path)
    LOG.info("zaladowano model: %s" % model_path)
    app.run(host='0.0.0.0', port=8666, debug=True)
