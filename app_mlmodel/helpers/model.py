from sklearn.base import BaseEstimator, TransformerMixin
import re
import pandas as pd
import numpy as np
import unicodedata
import unidecode


class PrepareData(BaseEstimator, TransformerMixin):

    def __init__(self, stemmer=None, extraxt_year=True, **kwargs):

        self.stemmer = stemmer
        self.extraxt_year = extraxt_year
        self.unicode_text = False

    flds_id = ['_id']
    flds_target = ['price']
    flds_num = ['flat_size', 'rooms', 'floor', 'number_of_floors',
                'year_of_building', 'price_m2']
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

    def clean_str(self, value):
        """Remove white spaces

        :param value: string to clean
        :type value: str
        :return: cleaned string or other object - with no transformation
        :rtype: str
        """
        if type(value) == str:
            pattern = re.compile(r'\s+')
            return re.sub(pattern, ' ', value).strip()
        else:
            return value

    def normalize_text(self, txt):
        if txt is not None:
            return unicodedata.normalize('NFKD', txt.replace(u"ł", "l")).encode(
                'ASCII', 'ignore').decode('ASCII')
        else:
            return ""

    def extraxt_year(self, txt):
        """extraxt year from text
        Any extracted date is assumed to be a year of building

        :param txt: text with offer description
        :type txt: str
        :return: year
        :rtype: np.int
        """
        pattern = re.compile(r'[2][0][\d]{2} +|[1][89][\d]{2} +')
        wynik = re.findall(pattern, txt)
        if wynik is None:
            return None
        elif len(wynik) == 1:
            return np.int32(wynik[0])
        elif len(wynik) > 1:
            return np.int32(min(wynik))
        else:
            return None

    def clean_description(self, txt):
        """clean description text
        Removes solo digits and special signs.
        If self.stemmer is provided, stemm the text

        :param txt: [description]
        :type txt: [type]
        :return: [description]
        :rtype: [type]
        """
        if len(txt) > 0:
            tmp = re.findall(r'(?=\D)\w+', txt)
            if self.stemmer:
                tmp = [self.stemmer(i.lower()) for i in tmp]
            tmp = " ".join([i for i in tmp if i is not None])
            return tmp
        else:
            return ""

    def insert_field_if_not_exist(self, dict_, field):
        """Check if dictionary contains specific field and insert
        None value if not.

        :param dict_: dictionary with offer data - one record
        :type dict_: dict
        :param field: name of the field to check
        :type field: str
        :return: input dictionar with new field if inserted
        :rtype: dict
        """
        if field not in dict_.keys():
            dict_[field] = None
        return dict_[field]

    def add_text_field_2_descr(self, dict_, txt_field,
                               desc_field='description'):
        """Add text from selected field to offer description text

        :param dict_: dictionary with offer data - one record
        :type dict_: dict
        :param txt_field: name of the field to add to description text
        :type txt_field: str
        :param desc_field: name of the field with description text, defaults
                           to 'description'
        :type desc_field: str, optional
        :return: dictionary with offer data - one record + new description
        :rtype: dict
        """
        if txt_field in dict_.keys():
            if dict_[txt_field] is not None and type(dict_[txt_field]) != list:
                return dict_[desc_field]+" "+txt_field+" "+dict_[txt_field]
            if dict_[txt_field] is not None and type(dict_[txt_field]) == list:
                return dict_[desc_field]+" "+txt_field+" "+" ".join(
                    dict_[txt_field])
            else:
                return dict_[desc_field]
        else:
            return dict_[desc_field]

    def clean_data(self, data):
        """Clean and unify data from many websites.
        * adds text from selected fields to offer description text,
        * insert fields with empty values if not exists in dictionary,
        * insert 'no_value' to name field if is None,

        :param data: dictionary with offers data
        :type data: dict
        :return: dictionary with offfer data after cleaning and transformations
        :rtype: dict
        """

        list_ = []

        if type(data) == dict:
            data_ = [data.copy()]
        elif type(data) == list:
            data_ = data.copy()
        else:
            data_ = None

        for rec in data_:
            tmp_ = {}

            for i in rec.keys():
                tmp_[i] = self.clean_str(rec[i])

            if tmp_['name'] is None:
                tmp_['name'] = 'no_value'

            tmp_['info'] = ""

            for key in ['additional_info',
                        'building_type',
                        'building_material',
                        'property_form',
                        'market',
                        'widows_type',
                        'heating_type',
                        'finishing_stage',
                        'property_form',
                        'comute',
                        'health_beauty',
                        'education',
                        'other',
                        'parking',
                        'kitchen',
                        'umeblowane',
                        'condition',
                        'condition_electric_wires',
                        'windows',
                        'loudness',
                        'bathroom_equip',
                        'bathroom',
                        'bathroom_number',
                        'additional_space',
                        'world_direction',
                        'terrace',
                        'for_office']:
                tmp_['info'] = self.add_text_field_2_descr(
                    tmp_, key,  'info')

            tmp_['info'] = self.clean_str(tmp_['info'])

            for key in ['year_of_building', 'number_of_floors',
                        'terrece_size', ' flat_height']:
                tmp_[key] = self.insert_field_if_not_exist(tmp_, key)

            if self.extraxt_year:
                tmp_['year_of_building'] = self.extraxt_year(
                    tmp_['description']) if \
                    tmp_['year_of_building'] != tmp_['year_of_building'] \
                    else tmp_['year_of_building']

            tmp_['description'] = self.clean_description(tmp_['description'])

            if self.unicode_text:
                tmp_['description'] = self.normalize_text(tmp_['description'])
                tmp_['info'] = self.normalize_text(tmp_['info'])

            list_ += [tmp_]

        return list_

    def get_feature_names(self):
        return self.feature_names

    def fit(self, x, y=None):
        tmp = self.transform(x[:100] if len(x) > 100 else x)
        self.feature_names = list(tmp.columns)
        return self

    def transform(self, x):
        tmp = self.clean_data(x)
        tmp = pd.DataFrame(tmp)[self.all_fields]
        return tmp


class PassThroughOrReplace(BaseEstimator, TransformerMixin):
    """
    Just pass data throught, !Rememeber to reset DF index before:
    * It will replace text or numeric values if dictionary is provided
      ex. replace_dict = {'column name':{'old value':'new value'}}
    * It will fill na if fillna is True, text with 'novalue', numeric with mean
    """

    def __init__(self, replace_dict=None, fillna=False, **kwargs):
        self.replace_dict = replace_dict
        self.fillna = fillna
        self.kwargs = kwargs

    def fit(self, x, y=None):

        new_x = x.copy()

        if type(new_x) == pd.core.frame.DataFrame:

            self.f_category = list(new_x.select_dtypes(
                include=['object']).columns)
            self.f_numeric = list(new_x.select_dtypes(
                exclude=['object']).columns)
            self.f_date = list(new_x.select_dtypes(
                include=['datetime64[ns]']).columns)

        if type(new_x) == pd.core.series.Series:

            self.f_category = list(new_x.to_frame().select_dtypes(
                include=['object']).columns)
            self.f_numeric = list(new_x.to_frame().select_dtypes(
                exclude=['object']).columns)
            self.f_date = list(new_x.to_frame().select_dtypes(
                include=['datetime64[ns]']).columns)

        if self.replace_dict:
            if type(new_x) == pd.core.frame.DataFrame:
                new_x.replace(self.replace_dict, inplace=True)

            if type(new_x) == pd.core.series.Series:
                new_x = new_x.to_frame().replace(self.replace_dict).iloc[:, 0]

        if type(new_x) == pd.core.frame.DataFrame:
            self.columnNames = new_x.columns
            self.means = pd.DataFrame.from_dict(
                {"column": new_x[self.f_numeric].mean().index,
                 "mean": new_x[self.f_numeric].mean()}).to_dict(orient='index')

        if type(new_x) == pd.core.series.Series:
            self.columnNames = [new_x.name]
            self.means = {new_x.name: {"column": new_x.name,
                                       "mean": new_x.mean()}}

        return self

    def get_feature_names(self):
        if hasattr(self, "columnNames"):
            return self.columnNames
        else:
            return None

    def transform(self, x):

        new_x = x.copy()

        if self.replace_dict:
            if type(new_x) == pd.core.frame.DataFrame:
                new_x.replace(self.replace_dict, inplace=True)

            if type(new_x) == pd.core.series.Series:
                new_x = new_x.to_frame().replace(self.replace_dict).iloc[:, 0]

        if self.fillna:
            if len(self.f_category) > 0:
                #new_x.replace({'': np.nan}, inplace=True)
                new_x.fillna('novalue', inplace=True)

            if len(self.f_numeric) > 0 and type(new_x) == \
                    pd.core.frame.DataFrame:
                for col in self.f_numeric:
                    new_x[col] = new_x[col].fillna(self.means[col]["mean"])

            if len(self.f_numeric) > 0 and type(new_x) == \
                    pd.core.series.Series:
                new_x = new_x.fillna(self.means[x.name]["mean"]).to_frame()

        return new_x


class transformColList(BaseEstimator, TransformerMixin):
    """
    Transform columns of Data Frame - OneHot
    """

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __correct_names(self, x):
        x = unidecode.unidecode(x)
        x = re.sub("[_.,/ ~!@#$%^&*()-+]", "_", x)
        x = re.sub("_+", "_", x)
        x = x.lower()
        return x

    def fit(self, x, y=None):

        if type(x) == pd.core.frame.DataFrame:
            self.columns = x.columns
            self.cor_values = {}
            self.columnNames = []
            # df
            for col in self.columns:
                if type(x[col][0]) == list:
                    self.cor_values[col] = set(
                        [(item, col + "_" + self.__correct_names(item)) for
                            sublist in x[col].values for item in sublist
                         if item != ''])
                    self.columnNames += [i[1] for i in self.cor_values[col]]
                else:
                    self.cor_values[col] = [(item, col + "_" + self.__correct_names(item)) for item in
                                            list(x[col].unique()) if item is not None]
                    self.columnNames += [i[1] for i in self.cor_values[col]]

        if type(x) == pd.core.series.Series:
            self.columns = [x.name]
            self.cor_values = {}
            # ser

            for col in self.columns:
                if type(x.to_list()[0]) == list:
                    self.cor_values[col] = set(
                        [(item, col + "_" + self.__correct_names(item)) for sublist in x.values for item in sublist if
                         item != ''])
                    self.columnNames = [i[1] for i in self.cor_values[col]]
                else:
                    self.cor_values[col] = [(item, col + "_" + self.__correct_names(item)) for item in list(x.unique())
                                            if item is not None]
                    self.columnNames = [i[1] for i in self.cor_values[col]]

        return self

    def get_feature_names(self):
        if hasattr(self, "columnNames"):
            return self.columnNames
        else:
            return None

    def transform(self, x):

        data = {}
        for i in self.columns:
            data[i] = []

        if type(x) == pd.core.frame.DataFrame:
            # df
            for col in self.columns:
                if type(x[col][0]) == list:

                    _dict = {}

                    for i in self.cor_values[col]:
                        _dict[i[1]] = 0

                    for i, row in enumerate(x[col].tolist()):
                        _dict_tmp = _dict.copy()
                        for val in self.cor_values[col]:
                            if val[0] in row:
                                _dict_tmp[val[1]] = 1
                            else:
                                _dict_tmp[val[1]] = 0
                        data[col] += [_dict_tmp]

                else:

                    _dict = {}

                    for i in self.cor_values[col]:
                        _dict[i[1]] = 0

                    for row in x[col].tolist():
                        _dict_tmp = _dict.copy()
                        for val in self.cor_values[col]:
                            if val[0] == row:
                                _dict_tmp[val[1]] = 1
                            else:
                                _dict_tmp[val[1]] = 0
                        data[col] += [_dict_tmp]

            return pd.concat([pd.DataFrame(data[i]) for i in data], axis=1)

        if type(x) == pd.core.series.Series:
            # series
            for col in self.columns:
                if type(x[0]) == list:

                    _dict = {}

                    for i in self.cor_values[col]:
                        _dict[i[1]] = 0

                    for i, row in enumerate(x.tolist()):
                        _dict_tmp = _dict.copy()
                        for val in self.cor_values[col]:
                            if val[0] in row:
                                _dict_tmp[val[1]] = 1
                            else:
                                _dict_tmp[val[1]] = 0
                        data[col] += [_dict_tmp]

                else:

                    _dict = {}

                    for i in self.cor_values[col]:
                        _dict[i[1]] = 0

                    for row in x.tolist():
                        _dict_tmp = _dict.copy()
                        for val in self.cor_values[col]:
                            if val[0] == row:
                                _dict_tmp[val[1]] = 1
                            else:
                                _dict_tmp[val[1]] = 0
                        data[col] += [_dict_tmp]

            return pd.concat([pd.DataFrame(data[i]) for i in data], axis=1)
