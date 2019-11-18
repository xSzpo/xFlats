#!/usr/bin/env python

import configparser
import os
import sys
import json
import logging
import pymongo
import numpy as np
from datetime import timedelta
from itertools import compress
import time
import codecs

import category_encoders as ce
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import make_pipeline
from sklearn.metrics import r2_score, median_absolute_error
from sklearn.metrics import mean_absolute_error
import lightgbm as lgb
import pickle

scrip_path = os.path.dirname(sys.argv[0])
# scrip_path = 'app_mlmodel'
sys.path.append(scrip_path)

import helpers

seed = 666
LOG = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
                    format="'%(asctime)s - %(name)s - %(levelname)s "
                    "- %(message)s'")


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts))
        else:
            LOG.info('%r  %2.2f s' % (
                method.__name__, (te - ts)))
        return result
    return timed


@timeit
def load_data():
    '''Load dataset'''
    # load settings
    mode = 'DEVELOPMENT'
    # scrip_path = os.path.dirname(sys.argv[0])

    config = configparser.ConfigParser()
    config.read(os.path.join(scrip_path, "config.ini"))

    MONGO_PORT = config.getint('GENERAL', 'MONGO_PORT')
    MONGO_DBNAME = config.get('GENERAL', 'MONGO_DBNAME')
    MONGO_USERNAME = config.get('GENERAL', 'MONGO_USERNAME')
    MONGO_PASSWORD = config.get('GENERAL', 'MONGO_PASSWORD')
    MONGO_COLLECTIONS = config.get('GENERAL', 'MONGO_COLLECTIONS').split("|")
    if mode == 'DEVELOPMENT':
        MONGO_ADDRESS = config.get('DEVELOPMENT', 'MONGO_ADDRESS')
    elif mode == 'DOCKER':
        MONGO_ADDRESS = config.get('DOCKER', 'MONGO_ADDRESS')

    # set connection
    connection = pymongo.MongoClient(
        host=MONGO_ADDRESS,
        port=MONGO_PORT,
        username=MONGO_USERNAME,
        password=MONGO_PASSWORD,
        authSource='admin',
        authMechanism='SCRAM-SHA-256',
        serverSelectionTimeoutMS=5000)

    db = connection[MONGO_DBNAME]
    LOG.debug("conected to db")
    raw_data = []
    for collection in MONGO_COLLECTIONS:
        raw_data += [i for i in db[collection].find({})]

    LOG.debug("data downloaded from db: %d records" % len(raw_data))

    # %%

    np.random.seed(seed)

    download_date = [i['download_date'].date() for i in raw_data]
    oot_date_lim = max(download_date)-timedelta(days=3)
    bool_oot = [i >= oot_date_lim for i in download_date]
    bool_train_test = [i < oot_date_lim for i in download_date]
    fold_train_test = np.random.choice(['train', 'test'],
                                       len(bool_train_test),
                                       p=[0.85, 0.15]).tolist()
    bool_train = [i == 'train' for i in fold_train_test]
    bool_test = [i == 'test' for i in fold_train_test]

    sample_oot = list(compress(raw_data, bool_oot))
    sample_train_test = list(compress(raw_data, bool_train_test))
    sample_train = list(compress(sample_train_test, bool_train))
    sample_test = list(compress(sample_train_test, bool_test))

    LOG.debug("data divided to samples")

    prep_dat = helpers.PrepareData(extraxt_year=True, unicode_text=True)

    X_train = prep_dat.fit_transform(sample_train)
    X_test = prep_dat.transform(sample_test)
    X_oot = prep_dat.transform(sample_oot)

    LOG.debug("sample_train size %d" % X_train.shape[0])
    LOG.debug("sample_test size %d" % X_test.shape[0])
    LOG.debug("sample_oot size %d" % X_oot.shape[0])

    outliers = [
        {"key": "price", "min": 100000, "max": 1500000},
        {"key": "flat_size", "min": 6, "max": 150},
        {"key": "year_of_building", "min": 1850, "max": 2050},
        {"key": "GC_longitude", "min": 20.5, "max": 21.5},
        {"key": "GC_latitude", "min": 51, "max": 52.5}
    ]

    for val in outliers:
        X_train = X_train.query("{key} != {key} or ({key}>{min} and "
                                "{key}<{max})".format(**val))
    y_train = X_train.price.tolist()

    for val in outliers:
        X_test = X_test.query("{key} != {key} or ({key}>{min} and "
                              "{key}<{max})".format(**val))
    y_test = X_test.price.tolist()

    for val in outliers:
        X_oot = X_oot.query("{key} != {key} or ({key}>{min} and "
                            "{key}<{max})".format(**val))
    y_oot = X_oot.price.tolist()

    return X_train, X_test, X_oot, y_train, y_test, y_oot


@timeit
def get_model(PARAMS):

    try:
        te_dict = {
            'CatBoostEncoder': ce.CatBoostEncoder(),
            'HashingEncoder': ce.HashingEncoder(),
            'HelmertEncoder': ce.HelmertEncoder(),
            'LeaveOneOutEncoder': ce.LeaveOneOutEncoder(),
            'OneHotEncoder': ce.OneHotEncoder(),
            'TargetEncoder': ce.TargetEncoder(),
            'WOEEncoder': ce.WOEEncoder(),
            'BackwardDifferenceEncoder': ce.BackwardDifferenceEncoder(),
            'BaseNEncoder': ce.BaseNEncoder(),
            'BinaryEncoder': ce.BinaryEncoder(),
            'CountEncoder': ce.CountEncoder(),
            'JamesSteinEncoder': ce.JamesSteinEncoder(),
            'MEstimateEncoder': ce.MEstimateEncoder(),
            'PolynomialEncoder': ce.PolynomialEncoder(),
            'SumEncoder': ce.SumEncoder()
        }

        pipe = make_pipeline(
            ColumnTransformer([
                ('num', helpers.PassThroughOrReplace(),
                 ['flat_size', 'rooms', 'floor', 'number_of_floors',
                  'year_of_building', 'GC_latitude', 'GC_longitude']),
                ('te_producer', te_dict.get(PARAMS['te_producer']),
                    'producer_name'),
                ('te_road', te_dict.get(PARAMS['te_road']),
                    'GC_addr_road'),
                ('te_neighbourhood', te_dict.get(PARAMS['te_neighbourhood']),
                    'GC_addr_neighbourhood'),
                ('te_suburb', te_dict.get(PARAMS['te_suburb']),
                    'GC_addr_suburb'),
                ('te_postcode', te_dict.get(PARAMS['te_postcode']),
                    'GC_addr_postcode'),
                ('txt_name',
                    TfidfVectorizer(
                        lowercase=True,
                        ngram_range=(1, PARAMS['txt_name__ngram_range']),
                        max_features=PARAMS['txt_name__max_features'],
                        dtype=np.float32,
                        binary=PARAMS['txt_name__binary'],
                        use_idf=PARAMS['txt_name__use_idf']),
                 'name'),
                ('txt_dscr',
                    TfidfVectorizer(
                        lowercase=True,
                        ngram_range=(1, PARAMS['txt_dscr__ngram_range']),
                        max_features=PARAMS['txt_dscr__max_features'],
                        dtype=np.float32,
                        binary=PARAMS['txt_dscr__binary'],
                        use_idf=PARAMS['txt_dscr__use_idf']),
                 'description'),
            ]),
            lgb.LGBMRegressor(**PARAMS,
                              random_state=seed)
        )

        return pipe

    except BaseException as e:
        LOG.error(e)
        return None


@timeit
def get_default_parameters():
    '''get default parameters'''

    with codecs.open(os.path.join(scrip_path, "model_par.json"),
                     'rb', encoding='utf-8') as f:
        params = json.loads(f.read())
    return params


@timeit
def train(X_train, y_train, model_):
    '''Train model and predict result'''
    y_train_log = np.log1p(y_train)
    model_.fit(X_train, y_train_log)
    return model_


@timeit
def report(X_train, y_train, X_test, y_test, X_oot, y_oot, model_):
    predict_y = model_.predict(X_train)
    predict_y = np.expm1(predict_y)
    r2 = r2_score(y_train, predict_y)
    med_abs_err = median_absolute_error(y_train, predict_y)
    mean_abs_err = mean_absolute_error(y_train, predict_y)
    score_train = ("Train set r2 score {}, median absolute error {}, "
                   "mean absolute error {} \n".format(
                       round(r2, 4), int(med_abs_err), int(mean_abs_err)))
    LOG.debug(score_train)

    predict_y = model_.predict(X_test)
    predict_y = np.expm1(predict_y)
    r2 = r2_score(y_test, predict_y)
    med_abs_err = median_absolute_error(y_test, predict_y)
    mean_abs_err = mean_absolute_error(y_test, predict_y)
    score_test = ("Test set r2 score {}, median absolute error {}, "
                  "mean absolute error {} \n".format(
                   round(r2, 4), int(med_abs_err), int(mean_abs_err)))
    LOG.debug(score_test)

    predict_y = model_.predict(X_oot)
    predict_y = np.expm1(predict_y)
    r2 = r2_score(y_oot, predict_y)
    med_abs_err = median_absolute_error(y_oot, predict_y)
    mean_abs_err = mean_absolute_error(y_oot, predict_y)
    score_oot = ("Out of time set r2 score {}, median absolute error {}, "
                 "mean absolute error {} ".format(
                     round(r2, 4), int(med_abs_err), int(mean_abs_err)))
    LOG.debug(score_oot)

    with codecs.open(os.path.join(scrip_path, "model_report.txt"),
                     'w', encoding='utf-8') as f:
        f.write(score_train+score_test+score_oot)

    return score_train+score_test+score_oot


def main_train():
    X_train, X_test, X_oot, y_train, y_test, y_oot = load_data()
    PARAMS = get_default_parameters()
    model = get_model(PARAMS)
    LOG.info(model)
    model = train(X_train, y_train, model)
    score = report(X_train, y_train, X_test, y_test, X_oot, y_oot, model)
    LOG.info(score)
    pickle.dump(model, open(os.path.join(scrip_path,
                                         'model_default.pkl'), 'wb'))


if __name__ == '__main__':
    main_train()
