import unidecode
import re
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

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

            if len(self.f_numeric) > 0 and type(new_x) == pd.core.frame.DataFrame:
                for col in self.f_numeric:
                    new_x[col] = new_x[col].fillna(self.means[col]["mean"])

            if len(self.f_numeric) > 0 and type(new_x) == pd.core.series.Series:
                new_x = new_x.fillna(self.means[x.name]["mean"]).to_frame()

        return new_x



class transformColList(BaseEstimator, TransformerMixin):
    """
    Transform columns of Data Frame
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
                        [(item, col + "_" + self.__correct_names(item)) for sublist in x[col].values for item in sublist
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
