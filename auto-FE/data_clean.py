# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
This package is used for data cleaning, containing several kind of data cleaning methods.
"""
# Import necessary libraries.
import numpy as np
import pandas as pd

from imblearn import over_sampling
from sklearn import preprocessing as pp
from sklearn.ensemble import IsolationForest

import feature_engineering as fe


class OutlierDetector(object):
    """
    The class of several methods to detect outliers.
    """
    def __init__(self, data, target_column, id_columns):
        """Initialize outlier detector with dataframe.

        :param data: Dataframe. Input Pandas dataframe, without target column.
        :param target_column: String. The target column name.
        :param id_columns: List. The list of ID column names.
        """
        self.data = data
        self.target_column = target_column
        self.id_columns = id_columns

    @staticmethod
    def median_detection(values):
        """Detect outlier in one variable using median method.

        :param values: List. List of variable values, to be processed.

        :return: List. The list of index of outliers.
        """
        # Compute median of list.
        median = np.median(values)

        # Set lower limit and upper limit.
        b = 1.4826  # Assign the range of normality.
        mad = b * np.median(np.abs(values - median))
        lower_limit = median - (3 * mad)
        upper_limit = median + (3 * mad)

        # Filter out outliers, out of the normal range.
        lower_index = values.index(values < lower_limit)
        upper_index = values.index(values > upper_limit)
        result_index = lower_index + upper_index

        return result_index

    @staticmethod
    def mean_detection(values):
        """Detect outlier in one variable using mean method.

        :param values: List. List of variable values, to be processed.

        :return: List. The list of index of outliers.
        """
        # Calculate standard deviation and mean of the variable.
        std = np.std(values)
        mean = np.mean(values)

        # Set lower limit and upper limit.
        b = 3  # Assign normal range.
        lower_limit = mean - b * std
        upper_limit = mean + b * std

        # Filter out outliers, out of the normal range.
        lower_index = [num for num in xrange(len(values)) if values[num] < lower_limit]
        upper_index = [num for num in xrange(len(values)) if values[num] > upper_limit]
        result_index = lower_index + upper_index

        return result_index

    @staticmethod
    def preprocess(data, cate_columns):
        """Preprocess data before feeding into model.

        Convert category data into numeric data, for model.

        :param data: Dataframe. The target Pandas dataframe to be processed.
        :param cate_columns: List. The list consisting of category column names.

        :return: Dataframe. Converted data which can be fed into model.
        """
        # Category column feature engineering.
        cate_fe = fe.CategoryFeatureEngineer(cate_columns)
        data = cate_fe.fit_transform(data)

        return data

    def isolation_forest(self):
        """Outlier detection using IsolationForest.

        Firstly, use IsolationForest to assign score for each data point, the smaller
        the score, the more anomaly the data point. Secondly, apply one feature outlier
        detection to find the outlier automatically without parameters.

        :return: List. The list of row index of outliers.
        """
        # Fill 'NA' with mean for numeric column.
        na_filler = NaFiller()
        data = na_filler.fit_transform(self.data, self.data.columns)

        # Create instance class of IsolationForest.
        clf = IsolationForest(max_samples=0.5, random_state=1021)

        # Filter target column.
        feature_column = data.columns.tolist()
        feature_column.remove(self.target_column)
        for element in self.id_columns:
            if element in feature_column:
                feature_column.remove(element)
        features = data[feature_column]

        # Preprocess data.
        num_columns, cate_columns = fe.column_type_detection(data, self.id_columns, self.target_column)
        features = self.preprocess(features, cate_columns)

        # Fit data and assign score for each data point.
        clf.fit(features)
        feature_score = clf.decision_function(features)

        # Detect outliers using one-variable method.
        outlier_index = self.mean_detection(feature_score)
        print('The ratio of outliers is %f' % (len(outlier_index) / float(len(feature_score))))

        return outlier_index


class OverSampler(object):
    """
    The class of several methods for oversampling.
    """
    def __init__(self, data, target_column, id_columns):
        """Initialize sampler with dataframe, as well as target column name.

        :param data: Dataframe. Input Pandas dataframe, with target column.
        :param target_column: String. The target column name.
        :param id_columns: String. The id column name.
        """
        self.data = data
        self.target_column = target_column
        self.id_columns = id_columns

    def smote_sample(self):
        """Over-sampling with SMOTE method.

        :return: Dataframe. The Pandas dataframe with over-sampled minority data.
        """
        # Create SMOTE class and over-sample minority data.
        smoter = over_sampling.SMOTE(ratio='minority', random_state=1021)
        feature_column = self.data.columns.tolist()
        feature_column.remove(self.target_column)
        for element in self.id_columns:
            if element in feature_column:
                feature_column.remove(element)
        feature, target = smoter.fit_sample(X=self.data[feature_column], y=self.data[self.target_column])

        # Combine re-sample results into dataframe.
        feature_df = pd.DataFrame(columns=feature_column, data=feature)
        feature_df[self.target_column] = target

        return feature_df


class UnderSampler(object):
    """
    The class of several methods for under-sampling.
    """

    def __init__(self, data, target_column):
        """Initialize sampler with dataframe, as well as target column name.

        :param data: Dataframe. Input Pandas dataframe, with target column.
        :param target_column: String. The target column name.
        """
        self.data = data
        self.target_column = target_column

    def random_sample(self, current_ratio, target_ratio):
        """Under-sampling with random method.

        :param current_ratio: The current_ratio of majority data to minority data.
        :param target_ratio: The target_ratio of two classes after re-sampling.

        :return: Dataframe. The Pandas dataframe after applying random choosing.
        """
        # Sample majority data using random method.
        data = self.data.sample(frac=(current_ratio/target_ratio), random_state=1021)

        return data


class NaFiller(object):
    """The class created to fill NA.

    """
    def __init__(self, numeric_method='mean'):
        """Initialize class with given parameters.

        :param numeric_method: String. The method to calculate values to fill na in
                            numeric columns.
        """
        # Assign parameters.
        self.numeric_method = numeric_method
        # Create dictionary to store imputer of each numeric column.
        self.num_imputer_dic = {}

    def fit_transform(self, data, column_list):
        """Fill 'NA' in columns.

        Fill 'NA' in category columns with 'missing' value, and fill 'NA' in numeric columns
        with mean or median, as well as creating flag column recording whether the value is
        'NA' or not.

        :param data: Dataframe. The Pandas dataframe to be analyzed.
        :param column_list: List. The list contains column names which would be converted in function.

        :return: Dataframe: The converted Pandas dataframe.
        """
        # Loop through column list.
        for column in column_list:
            # If contain 'NA', check the type of column, category or numeric.
            if data.dtypes[column] not in ['float', 'int']:
                # Fill 'NA' with 'missing' value in category column.
                data[column] = data[column].fillna('missing')
            else:
                # Create flag column, '1' for missing value, '0' for not.
                data[column + '_flag'] = np.zeros(shape=len(data[column]))
                data[column + '_flag'][np.where(data[column].isnull().values == True)[0].tolist()] = 1

                # Fill 'NA' with mean value in numeric column.
                imp = pp.Imputer(missing_values='NaN', strategy=self.numeric_method, axis=0)
                data[column] = imp.fit_transform(data[[column]])
                self.num_imputer_dic[column] = imp

        return data

    def transform(self, data, column_list):
        """Transform test data.

        Transform data according to method in fit_transform() function.

        :param data: Dataframe. The Pandas dataframe to be processed.
        :param column_list: List. The list contains column names which would be converted in function.

        :return: Dataframe. The processed dataframe.
        """
        # Loop through column list.
        for column in column_list:
            # If contain 'NA', check the type of column, category or numeric.
            if data.dtypes[column] not in ['float', 'int']:
                # Fill 'NA' with 'missing' value in category column.
                data[column] = data[column].fillna('missing')
            else:
                # Create flag column, '1' for missing value, '0' for not.
                data[column + '_flag'] = np.zeros(shape=len(data[column]))
                data[column + '_flag'][data[column][data[column].isnull().values is True].index.tolist()] = 1

                # Fill 'NA' using method in fit_transform() function.
                imp = self.num_imputer_dic[column]
                data[column] = imp.transform(data[column])

        return data


def wash_data(data, target_column, id_columns, outlier=False):
    """Clean unusual data rows.

    Remove repetitive rows, rows with too many missing values, and report rows which
    should be considered as outliers.

    :param data: Dataframe. The Pandas dataframe to be washed.
    :param target_column: String. The target column name.
    :param id_columns: List. The list of ID column names.
    :param outlier: Boolean value. [default: False]. Whether to discard or not.

    :return: Dataframe. The converted Pandas dataframe.
    """
    # Remove repetitive data.
    data = data.drop_duplicates(keep='first')

    # Remove rows with too many missing values.
    percent = 0.6
    data = data.dropna(thresh=int(data.shape[1]*percent))

    # Detect outliers and report or remove.
    outlier_detector = OutlierDetector(data.copy(), target_column, id_columns)
    outlier_index = outlier_detector.isolation_forest()
    # Check the action on outliers.
    if not outlier:
        # Report outliers.
        print('The row index of outliers is as follows: %s' % (str(outlier_index)))
    else:
        # Drop the outliers.
        data.drop(outlier_index, axis=0, inplace=True)

    # Drop index column.
    feature_column = data.columns.tolist()
    for element in id_columns:
        feature_column.remove(element)
    data = data[feature_column]

    return data


def sample_data(data, target_column, id_columns, method='both'):
    """Sample the data to be balanced.

    Under-sampling majority class and over-sampling minority class to have the ratio of 1:1.
    This version only supports for binary classification.

    :param data: Dataframe. The Pandas dataframe to be sampled.
    :param target_column: String. The target column name.
    :param id_columns: String. The id column name.
    :param method: String. [default: 'both']. Choose from list ['both', 'under-sampling', 'over-sampling']. When
                set to 'both', both methods will be applied to dataframe, or when set to ether
                of other two methods, the corresponding method will be applied to dataframe alone.

    :return: Dataframe. The converted Pandas dataframe.
    """
    # Check the target column to decide which are majority label and minority label.
    major_label = data[target_column].value_counts().keys()[0]
    minor_label = data[target_column].value_counts().keys()[1]
    major_data = data[data[target_column] == major_label]
    minor_data = data[data[target_column] == minor_label]
    current_ratio = major_data.shape[0] / float(minor_data.shape[0])
    target_ratio = 1.5

    # Down-sampling the majority class data.
    if method in ['both', 'under-sampling']:
        under_sampler = UnderSampler(major_data, target_column)
        # Choose random method as default method.
        major_data = under_sampler.random_sample(current_ratio, target_ratio)

        # Combine majority data and minority data.
        data = pd.concat([major_data, minor_data], ignore_index=True)

    # Over-sampling the minority class data.
    if method in ['both', 'over-sampling']:
        # Create over-sampler and over sample minority using SMOTE method.
        over_sampler = OverSampler(data, target_column, id_columns)
        data = over_sampler.smote_sample()

    return data
