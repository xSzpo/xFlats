# %%
# %load_ext autoreload
# %autoreload 2
from sklearn.metrics import mean_absolute_error, mean_squared_log_error
from sklearn.metrics import r2_score, median_absolute_error
from category_encoders import *
from sklearn.base import BaseEstimator, TransformerMixin
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import make_pipeline
from sklearn.metrics import r2_score, median_absolute_error
from sklearn.metrics import mean_absolute_error

import lightgbm as lgb

import pandas as pd
import numpy as np
import pymongo
import gc
from datetime import timedelta
from itertools import compress
import unicodedata

import feather

import codecs
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns

import sys
sys.path.append('/Users/xszpo/Google Drive/DataScience/Projects/'
                '201907_xFlat_AWS_Scrapy/app_mlmodel')

# %%
import helpers

seed = 666

# %%
mongo_adrress = 'localhost'
mongo_port = 27017
mongo_username = 'xflats'
mongo_password = 'xflats'
dbase = 'OFFERS'

connection = pymongo.MongoClient(
    host=mongo_adrress, port=mongo_port, username=mongo_username,
    password=mongo_password, authSource='admin', authMechanism='SCRAM-SHA-256',
    serverSelectionTimeoutMS=5000)
db = connection[dbase]

# %%
raw_data = [i for i in db['morizon'].find({})]
raw_data += [i for i in db['otodom'].find({})]
raw_data += [i for i in db['olx'].find({})]
raw_data += [i for i in db['gratka'].find({})]

raw_data = [i for i in raw_data if i['price'] < 2000000]

# %%
target = [i['price'] for i in raw_data]
download_date = [i['download_date'].date() for i in raw_data]

# %%
download_date_plot = [i['download_date'].date().strftime('%Y-%m-%d') for i in
                      raw_data]
sns.set(style="whitegrid")
fig, ax1 = plt.subplots(figsize=(10, 6))
sns.countplot(download_date, order=sorted(set(download_date_plot)))
plt.xticks(rotation=45)
ax1.set(xlabel='date', ylabel='frequency')


# %%
np.random.seed(seed)

oot_date_lim = max(download_date)-timedelta(days=3)
bool_oot = [i >= oot_date_lim for i in download_date]
bool_train_test = [i < oot_date_lim for i in download_date]
fold_train_test = np.random.choice(['train', 'test'], len(bool_train_test),
                                   p=[0.85, 0.15]).tolist()
bool_train = [i == 'train' for i in fold_train_test]
bool_test = [i == 'test' for i in fold_train_test]

sample_oot = list(compress(raw_data, bool_oot))
sample_oot_target = list(compress(target, bool_oot))

sample_train_test = list(compress(raw_data, bool_train_test))
sample_train_test_target = list(compress(target, bool_train_test))

sample_train = list(compress(sample_train_test, bool_train))
sample_train_target = list(compress(sample_train_test_target, bool_train))

sample_test = list(compress(sample_train_test, bool_test))
sample_test_target = list(compress(sample_train_test_target, bool_test))

del(oot_date_lim, bool_oot, bool_train_test, fold_train_test, bool_train,
    bool_test, sample_train_test, sample_train_test_target)

# %%
sns.set(style="whitegrid")

fig, ax1 = plt.subplots(figsize=(10, 6))
#plt.xlim(50000, 2000000)

sns.distplot(sample_train_target, rug=False, hist=False, ax=ax1,
             label='Train - {} offers'.format(len(sample_train_target)))
sns.distplot(sample_test_target, rug=False, hist=False, ax=ax1,
             label='Test - {} offers'.format(len(sample_test_target)))
sns.distplot(sample_oot_target, rug=False, hist=False, ax=ax1,
             label='Out of Time (last 3 days - {} offers'.format(
                 len(sample_oot_target)))

plt.title('Warsaw: Flats price distribution by SET: Train, Test, Out of Time',
          y=1.05, fontsize=16)
ax1.set(xlabel='price in pln', ylabel='frequency')


# %%
flds_id = ['_id']
flds_target = ['price']
flds_num = ['flat_size', 'rooms', 'floor', 'number_of_floors',
            'year_of_building']
flds_num_geo = ['GC_latitude', 'GC_longitude']
flds_cat = ['producer_name']
flds_cat_geo = ['GC_addr_road', 'GC_addr_neighbourhood', 'GC_addr_suburb',
                'GC_addr_city', 'GC_addr_state', 'GC_addr_postcode',
                'GC_addr_country']
flds_text = ['description', 'name']
drop = ['location']
download_date = ['download_date']
new_fields = ['info']
all_fields = flds_id + flds_target + flds_num + flds_num_geo + flds_cat +\
    flds_cat_geo + flds_text + download_date + new_fields

# %%
with codecs.open("app_mlmodel/DEVELOP_MODEL/polish.stopwords.txt", "r") as file:
    stopwords = file.read().split('\n')


def norm(x): return unicodedata.normalize(
    'NFKD', x).encode('ASCII', 'ignore').decode('ASCII')


stopwords = [norm(i) for i in stopwords]


with codecs.open("app_mlmodel/DEVELOP_MODEL/stopwords_uni.txt", "w") as file:
    file.write(", ".join(stopwords)[:-2])


# %%
prep_dat = helpers.PrepareData()
pd_sample_train = prep_dat.fit_transform(sample_train)
pd_sample_test = prep_dat.transform(sample_test)
pd_sample_oot = prep_dat.transform(sample_oot)

feather.write_dataframe(pd_sample_train,
                        "app_mlmodel/DEVELOP_MODEL/data/df_train.feather")
feather.write_dataframe(pd_sample_test,
                        "app_mlmodel/DEVELOP_MODEL/data/df_test.feather")
feather.write_dataframe(pd_sample_oot,
                        "app_mlmodel/DEVELOP_MODEL/data/df_toot.feather")

del(pd_sample_train, pd_sample_test, pd_sample_oot)

# %%
params = {'colsample_bytree': 0.6624318354159208,  # feature_fraction
          'learning_rate': 0.15990411055449805,
          'max_bin': 38712,
          'max_depth': 7,
          'min_child_samples': 84,  # min_data_in_leaf
          'min_child_weight': 6,  # min_sum_hessian_in_leaf
          'n_estimators': 206,  # num_iterations
          'num_leaves': 159,
          'reg_alpha': 3.960667919705787e-06,  # lambda_l1
          'reg_lambda': 499.85995495490215,  # lambda_l2
          'subsample': 0.9022680042341511,  # bagging_fraction
          'subsample_for_bin': 144116,  # bin_construct_sample_cnt
          'subsample_freq': 0  # bagging_freq
          }

pipe = make_pipeline(
    helpers.PrepareData(),
    ColumnTransformer([
        ('num', helpers.PassThroughOrReplace(), ['flat_size', 'rooms', 'floor',
                                                 'number_of_floors',
                                                 'year_of_building',
                                                 'GC_latitude',
                                                 'GC_longitude']),
        ('cat', helpers.transformColList(), ['producer_name',
                                             'GC_addr_suburb']),
        ('postcodeCAT', CatBoostEncoder(), 'GC_addr_postcode'),
        ('txt_dscr', TfidfVectorizer(lowercase=True,
                                     stop_words=stopwords,
                                     ngram_range=(1, 3),
                                     max_features=3000,
                                     dtype=np.float32,
                                     use_idf=True), 'description'),
        ('txt_info', TfidfVectorizer(lowercase=True,
                                     stop_words=stopwords,
                                     ngram_range=(1, 3),
                                     max_features=1000,
                                     dtype=np.float32,
                                     use_idf=True), 'info'),
    ]),
    lgb.LGBMRegressor(**params, objective='regression_l2', random_state=seed)
)

# %%
pipe.fit(sample_train, sample_train_target)

# %%
y_pred = pipe.predict(sample_train)

r2 = r2_score(sample_train_target, y_pred)
med_abs_err = median_absolute_error(sample_train_target, y_pred)
mean_abs_err = mean_absolute_error(sample_train_target, y_pred)
print("Train set r2 score {}, median absolute error {}, "
      "mean absolute error {}".format(round(r2, 4), int(med_abs_err),
                                      int(mean_abs_err)))

y_pred = pipe.predict(sample_test)

r2 = r2_score(sample_test_target, y_pred)
med_abs_err = median_absolute_error(sample_test_target, y_pred)
mean_abs_err = mean_absolute_error(sample_test_target, y_pred)

print("Test set r2 score {}, median absolute error {}, mean absolute error {}".format(
    round(r2, 4), int(med_abs_err), int(mean_abs_err)))

y_pred = pipe.predict(sample_oot)

r2 = r2_score(sample_oot_target, y_pred)
med_abs_err = median_absolute_error(sample_oot_target, y_pred)
mean_abs_err = mean_absolute_error(sample_oot_target, y_pred)

print("Out of time set -  r2 score {}, median absolute error {}, mean absolute error {}".format(
    round(r2, 4), int(med_abs_err), int(mean_abs_err)))


# %%
print('Plotting feature importances...')


def names(): return pipe.named_steps['columntransformer'].get_feature_names()


pipe.named_steps['lgbmregressor'].booster_.feature_name = names
fig, ax = plt.subplots(figsize=(10, 20))
fig.subplots_adjust(left=0.4)
lgb.plot_importance(pipe.named_steps['lgbmregressor'],
                    max_num_features=50, ax=ax, importance_type='gain')
plt.yticks(fontsize=10)
plt.show()


# %%
