import nni
import logging
import numpy as np
import time
import os
import sys
import feather

import category_encoders as ce
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import make_pipeline
from sklearn.metrics import r2_score, median_absolute_error
from sklearn.metrics import mean_absolute_error
import lightgbm as lgb
import helpers

LOG = logging.getLogger(__name__)
#logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
#            format="'%(asctime)s - %(name)s - %(levelname)s - %(message)s'")

seed = 666


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
    X_train = feather.read_dataframe("df_train.feather")
    X_test = feather.read_dataframe("df_test.feather")
    X_oot = feather.read_dataframe("df_oot.feather")

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

    return X_train, X_test, y_train, y_test


@timeit
def get_default_parameters():
    '''get default parameters'''
    params = {
        'te_postcode': 'TargetEncoder',
        'te_suburb': 'TargetEncoder',
        'te_neighbourhood': 'HelmertEncoder',
        'te_producer': 'TargetEncoder',
        'te_road': 'OneHotEncoder',
        'txt_name__ngram_range': 2,
        'txt_name__max_features': 8000,
        'txt_name__binary': False,
        'txt_name__use_idf': False,
        'txt_dscr__ngram_range': 3,
        'txt_dscr__max_features': 7000,
        'txt_dscr__binary': False,
        'txt_dscr__use_idf': True,
        'boosting_type': 'gbdt',
        'feature_fraction': 0.8,  # colsample_bytree
        'learning_rate': 0.14,
        'max_bin': 42000,
        'max_depth': 10,
        'min_data_in_leaf': 69,  # min_data_in_leaf
        'min_child_weight': 2.8,  # min_sum_hessian_in_leaf
        'n_estimators': 719,  # num_iterations
        'num_leaves': 266,
        'reg_alpha': 0.11155937478115154,  # lambda_l1
        'reg_lambda': 0.13961503702849154,  # lambda_l2
        'bagging_fraction': 0.868559891110829,  # bagging_fraction
        'subsample_for_bin': 33732,  # bin_construct_sample_cnt
        'bagging_freq': 2,  # subsample_freq
        'objective': 'regression_l2'
    }

    return params


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
def run(X_train, X_test, y_train, y_test, model_):
    '''Train model and predict result'''
    y_train_log = np.log1p(y_train)
    model_.fit(X_train, y_train_log)

    predict_y_train = model_.predict(X_train)
    predict_y_train = np.expm1(predict_y_train)

    predict_y_test = model_.predict(X_test)
    predict_y_test = np.expm1(predict_y_test)

    score_train = np.int(mean_absolute_error(y_train, predict_y_train))
    r2_train = r2_score(y_train, predict_y_train)
    LOG.info('mean_absolute_error on train : %s' % score_train)
    LOG.info('r2 on train : %s' % r2_train)

    score_test = np.int(mean_absolute_error(y_test, predict_y_test))
    r2_test = r2_score(y_test, predict_y_test)
    LOG.info('mean_absolute_error on test : %s' % score_test)
    LOG.info('r2 on test : %s' % r2_test)

    # add penalty if r2 train score is larger then r2 test score
    if r2_train/r2_test > 1:
        score_rate = (r2_train/r2_test)**2
    else:
        score_rate = 1

    LOG.info('score rate: %s' % score_rate)

    score = score_test * score_rate

    LOG.info('corrected mean_absolute_error on test score: %s' % score)
    nni.report_final_result(score)


if __name__ == '__main__':
    X_train, X_test, y_train, y_test = load_data()

    try:
        # get parameters from tuner
        RECEIVED_PARAMS = nni.get_next_parameter()
        LOG.debug(RECEIVED_PARAMS)
        PARAMS = get_default_parameters()
        PARAMS.update(RECEIVED_PARAMS)
        LOG.debug(PARAMS)
        model = get_model(PARAMS)
        LOG.info(model)
        if model:
            run(X_train, X_test, y_train, y_test, model)
    except Exception as exception:
        LOG.exception(exception)
        raise
