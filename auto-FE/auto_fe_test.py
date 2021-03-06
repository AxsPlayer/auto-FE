# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
This script is designed for unit test for all the functions in automatic feature engineering.
"""
# Import necessary packages.
import logging
import os
import unittest
import pandas as pd

from progressbar import *

import data_clean
import feature_engineering
import feature_filtering
import step_by_step
import evaluation


def convert_data(combats, features, win_column=None):
    """Convert data into suitable format.

    Combine features and combats data, and convert into data in suitable
    format for training.

    :param combats: Dataframe. The Pandas dataframe which contains combats with
                two players with their id, as well as the winner id.
    :param features: Dataframe. The Pandas dataframe which contains every player's characters.
    :param win_column: String or None. [Default: None]. Whether combats dataframe contains winner
                    column or not. If yes, the column name of winner column.

    :return: Dataframe. The converted dataframe for training or testing.
    """
    # Create new dataframe to store values, and loop through.
    column_name = list(features.columns + '_1') + list(features.columns + '_2') + ['win']
    results = pd.DataFrame(columns=column_name)
    progress = ProgressBar()
    print('Combining data into suitable format for model...')
    for num in progress(xrange(combats.shape[0])):
        # Fetch the features of each player.
        player_1 = features[features['#']==combats['First_pokemon'].loc[num]]
        player_2 = features[features['#'] == combats['Second_pokemon'].loc[num]]
        # Fetch result of combat.
        if not win_column:
            if combats['First_pokemon'].loc[num] == combats[win_column].loc[num]:
                win = [1]
            else:
                win = [0]
        else:
            win = [None]
        # Assign vector combination to result dataframe.
        results.loc[num] = np.array(player_1).tolist()[0] + np.array(player_2).tolist()[0] + list(win)

    return results


def fetch_data(fold_path):
    """Fetch data saving in fold path.

    Convert data into suitable format, using csv files in fold path.

    :param fold_path: String. The fold in which data files are saved.

    :return:
        training_data: Dataframe. Combined dataframe to create training data.
        testing_data: Dataframe. Combined dataframe to create testing data.
    """
    # Read all the data from target fold path.
    pokemon = pd.read_csv(fold_path+'/pokemon.csv')
    combats = pd.read_csv(fold_path+'/combats.csv')
    test_data = pd.read_csv(fold_path+'/tests.csv')

    # Convert data into suitable format for training and testing.
    training_data = convert_data(combats, pokemon, win_column='Winner')
    testing_data = convert_data(test_data, pokemon)

    return training_data, testing_data


class TestFeatureEngineering(unittest.TestCase):
    """Test functions in all the scripts corresponding to feature engineering.

    Test each feature engineering function and the total automatic feature engineering
    script.
    """
    def __init__(self, *args, **kwargs):
        """Init the test class with all the attributes."""
        super(TestFeatureEngineering, self).__init__(*args, **kwargs)
        self.data = fetch_data('data')[0]

    def test_data_clean(self):
        """
        Test functions in data clean part.
        :return: None.
        """


    def test_feature_engineering(self):
        """
        Test functions in feature engineering part.
        :return: None.
        """

    def test_feature_selection(self):
        """
        Test functions in feature selection part.
        :return: None.
        """

    def test_step_by_step(self):
        """
        Test functions in step by step part.
        :return: None.
        """

    def test_evaluation(self):
        """
        Test functions in evaluation part.
        :return: None.
        """


if __name__ == "__main__":
    # Use 'python -m unittest auto_fe_test' in console for unit test.
    unittest.main()
