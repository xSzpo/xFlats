
import feather
import sys
import pymongo
import numpy as np
from datetime import timedelta
from itertools import compress
import os
import logging

sys.path.append('app_mlmodel')
import helpers

seed = 666
logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,
            format="'%(asctime)s - %(name)s - %(levelname)s - %(message)s'")


def main():

    try:
        mongo_adrress = 'localhost'
        mongo_port = 27017
        mongo_username = 'xflats'
        mongo_password = 'xflats'
        dbase = 'OFFERS'

        connection = pymongo.MongoClient(
            host=mongo_adrress,
            port=mongo_port,
            username=mongo_username,
            password=mongo_password,
            authSource='admin',
            authMechanism='SCRAM-SHA-256',
            serverSelectionTimeoutMS=5000)
        db = connection[dbase]
        logger.debug("conected to db")
        raw_data = [i for i in db['morizon'].find({})]
        raw_data += [i for i in db['otodom'].find({})]
        raw_data += [i for i in db['olx'].find({})]
        raw_data += [i for i in db['gratka'].find({})]
        logger.debug("data downloaded from db")

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

        logger.debug("data divided to samples")

        prep_dat = helpers.PrepareData(unicode_text=True)
        pd_sample_train = prep_dat.fit_transform(sample_train)
        pd_sample_test = prep_dat.transform(sample_test)
        pd_sample_oot = prep_dat.transform(sample_oot)

        logger.debug("data transformed")

        # %%
        path_ = "app_mlmodel/DEVELOP_MODEL/data/"
        feather.write_dataframe(pd_sample_train,
                                os.path.join(path_, "df_train.feather"))
        feather.write_dataframe(pd_sample_test,
                                os.path.join(path_, "df_test.feather"))
        feather.write_dataframe(pd_sample_oot,
                                os.path.join(path_, "df_oot.feather"))

        return {'code': 200, "desc": "data samples created and saved to %s"
                % path_}

    except BaseException as e:
        return {'code': 500, "desc": e}


if __name__ == '__main__':
    x = main()
    logger.info(x)
