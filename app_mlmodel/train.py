#!/usr/bin/python
# coding: utf-8

import configparser
import imp
import os
import sys
import json
import logging
import pymongo
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from pymongo.errors import WriteError, WriteConcernError, WTimeoutError
import numpy as np
import datetime
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
from sklearn.compose import TransformedTargetRegressor
import lightgbm as lgb
import pickle
import argparse
import warnings
import helpers

warnings.simplefilter('always', category=UserWarning)
seed = 666
LOG = logging.getLogger(__name__)


def timeit(method):
    """wraper for time measure"""

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
def load_data(mode='DOCKER'):
    """load data from mongoDB
    If training outside docker, select mode=DEVELOPMENT.
    All credentials to connect do db is in config.ini

    :param mode: select mongoDB config section ['DEVELOPMENT','DOCKER']
                 defaults to 'DEVELOPMENT'
    :type mode: str
    :return: data for training
    :rtype: tuples of dict
    """

    config = configparser.ConfigParser()
    config.read("config.ini")

    MONGO_PORT = config.getint('GENERAL', 'MONGO_PORT')
    MONGO_DBNAME = config.get('GENERAL', 'MONGO_DBNAME')
    MONGO_USERNAME = config.get('GENERAL', 'MONGO_USERNAME')
    MONGO_PASSWORD = config.get('GENERAL', 'MONGO_PASSWORD')
    MONGO_COLLECTIONS = config.get('GENERAL', 'MONGO_COLLECTIONS').split("|")
    if mode == 'DEVELOPMENT':
        MONGO_ADDRESS = config.get('DEVELOPMENT', 'MONGO_ADDRESS')
    elif mode == 'DOCKER':
        MONGO_ADDRESS = config.get('DOCKER', 'MONGO_ADDRESS')
    LOG.info(config.get('DOCKER', 'MONGO_ADDRESS'))
    # set connection
    try:
        connection = pymongo.MongoClient(
            host=MONGO_ADDRESS,
            port=MONGO_PORT,
            username=MONGO_USERNAME,
            password=MONGO_PASSWORD,
            authSource='admin',
            authMechanism='SCRAM-SHA-256',
            serverSelectionTimeoutMS=5000)

        LOG.info("Connected to MongoDB {}, address: {}:{}".format(
            connection.server_info()['version'], MONGO_ADDRESS, MONGO_PORT))

    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        LOG.error("pymongo.errors, Could not connect to server: %s" % e)
        sys.exit(1)

    except BaseException as e:
        LOG.error("BaseException, something went wrong: %s" % e)
        sys.exit(1)

    db = connection[MONGO_DBNAME]
    LOG.debug("conected to db")
    raw_data = []
    for collection in MONGO_COLLECTIONS:
        raw_data += [i for i in db[collection].find(
            {"price": {"$gt": 100000, "$lt": 1500000},
                "flat_size": {"$gt": 6, "$lt": 150},
                "GC_longitude": {"$gt": 20.5, "$lt": 21.5},
                "GC_latitude": {"$gt": 51, "$lt": 52.5}
             })]

    LOG.debug("data downloaded from db: %d records" % len(raw_data))

    outliers = [
        {"key": "price", "min": 100000, "max": 1500000},
        {"key": "flat_size", "min": 6, "max": 150},
        {"key": "year_of_building", "min": 1850, "max": 2050},
        {"key": "GC_longitude", "min": 20.5, "max": 21.5},
        {"key": "GC_latitude", "min": 51, "max": 52.5}
    ]

    np.random.seed(seed)

    download_date = [i['download_date'].date() for i in raw_data]
    oot_date_lim = max(download_date)-timedelta(days=3)
    bool_oot = [i >= oot_date_lim for i in download_date]

    if len(list(compress(raw_data, bool_oot)))/len(raw_data) > 0.1:
        oot_date_lim = max(download_date)-timedelta(hours=6)
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

    y_train = np.array([i['price'] for i in sample_train])
    y_test = np.array([i['price'] for i in sample_test])
    y_oot = np.array([i['price'] for i in sample_oot])

    LOG.debug("data divided to samples")

    return sample_train, sample_test, sample_oot, y_train, y_test, y_oot


@timeit
def get_model(PARAMS):
    """return model for provided params

    :param PARAMS: dictionary with model params
    :type PARAMS: dicr
    :return: model pipeline
    :rtype: sklearn pipeline
    """

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
            helpers.PrepareData(extraxt_year=True, unicode_text=True),
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
            TransformedTargetRegressor(
                regressor=lgb.LGBMRegressor(**PARAMS, random_state=seed),
                func=np.log1p,
                inverse_func=np.expm1
                                      )
        )

        return pipe

    except BaseException as e:
        LOG.error(e)
        return None


@timeit
def get_default_parameters():
    """get model parameters fom json"""

    with codecs.open("model_par.json", 'rb', encoding='utf-8') as f:
        params = json.loads(f.read())
    return params


@timeit
def train(X_train, y_train, model_):
    """Train model"""
    model_.fit(X_train, y_train)
    return model_


@timeit
def report(X_train, y_train, X_test, y_test, X_oot, y_oot, model_,
           model_name_date):
    """Asses model performance"""

    predict_y = model_.predict(X_train)
    r2 = r2_score(y_train, predict_y)
    med_abs_err = median_absolute_error(y_train, predict_y)
    mean_abs_err = mean_absolute_error(y_train, predict_y)
    score_train = ("Train set r2 score {}, median absolute error {}, "
                   "mean absolute error {} \n".format(
                       round(r2, 4), int(med_abs_err), int(mean_abs_err)))
    LOG.debug(score_train)

    predict_y = model_.predict(X_test)
    r2 = r2_score(y_test, predict_y)
    med_abs_err = median_absolute_error(y_test, predict_y)
    mean_abs_err = mean_absolute_error(y_test, predict_y)
    score_test = ("Test set r2 score {}, median absolute error {}, "
                  "mean absolute error {} \n".format(
                      round(r2, 4), int(med_abs_err), int(mean_abs_err)))
    LOG.debug(score_test)

    predict_y = model_.predict(X_oot)
    r2 = r2_score(y_oot, predict_y)
    med_abs_err = median_absolute_error(y_oot, predict_y)
    mean_abs_err = mean_absolute_error(y_oot, predict_y)
    score_oot = ("Out of time set r2 score {}, median absolute error {}, "
                 "mean absolute error {} ".format(
                     round(r2, 4), int(med_abs_err), int(mean_abs_err)))
    LOG.debug(score_oot)

    with codecs.open("model/model_report"+model_name_date+".txt",
                     "w", encoding='utf-8') as f:
        f.write(score_train+score_test+score_oot)

    return score_train+score_test+score_oot


def main_train(mode='DOCKER'):
    X_train, X_test, X_oot, y_train, y_test, y_oot = load_data(mode=mode)
    LOG.debug("Train size: %d " % len(X_train))
    LOG.debug("Test size: %d " % len(X_test))
    LOG.debug("OOT size: %d " % len(X_oot))
    PARAMS = get_default_parameters()
    model = get_model(PARAMS)
    LOG.info(model)
    model_name_date = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
    model = train(X_train, y_train, model)
    score = report(X_train, y_train, X_test, y_test, X_oot, y_oot, model,
                   model_name_date)
    LOG.info(model_name_date + ": " + score)
    name = "model/model_"+model_name_date+".pkl"
    pickle.dump(model, open(name, 'wb'))
    return model_name_date+": "+score


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev", action='store_true')
    args = parser.parse_args()
    if args.dev:
        LOG.debug('mode = DEVELOPMENT')
        main_train(mode='DEVELOPMENT')
    else:
        LOG.debug('mode = DOCKER')
        main_train(mode='DOCKER')
