import pandas as pd
from googleAPI import GoogleAPI


# API logon
class Regex():

    def __init__(self):
        pass

    def get_week(self, df):
        """
        Get those regex with type "Week"
        :param df: DataFrame (SS_LOADING_WEEK)
        :return: dictionary with DataSources as Keys and Regex as Values
        """
        regex_week = df[df['type'] == 'w'].loc[:, ['MM ID', 'regex']]

        rw_dict = regex_week.set_index('MM ID')['regex'].to_dict()

        return rw_dict

    def get_date(self, df):
        """
        Get those regex with type "Date"
        :param df: DataFrame
        :return: dictionary with DataSources as Keys and Regex as Values
        """
        regex_date = df[df['type'] == 'd'].loc[:, ['MM ID', 'regex']]
        rd_dict = regex_date.set_index('MM ID')['regex'].to_dict()

        return rd_dict

    def get_format(self, df):
        """
        For those in "Date" format, an specification of the format (e.g "%Y-%m-%d") is needed to read the dates.
        Therefore it is specified in this dictionary, with keys as DataSources and DateFormats as Value
        :param df: DataFrame
        :return: dictionary with DataSources as Keys and Date Format as values
        """
        regex_format = df[df['type'] == 'd'].loc[:, ['MM ID', 'strptime']]
        rf_dict = regex_format.set_index('MM ID')['strptime'].to_dict()

        return rf_dict
