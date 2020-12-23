import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from settings import *

class GoogleAPI:

    def __init__(self):
        pass

    @staticmethod
    def connect():
        """
        Establishes connection with the Google API
        :return: gc - credentials
        """

        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            keySettings.key, scope)
        gc = gspread.authorize(credentials)

        return gc

    def worksheet_access(self, gc, ggss, sheet):
        """

        :param gc: Credentials from connect()
        :param ggss: The name of the spreadsheet we want to retrieve
        :param sheet: name of the sheet
        :return: Spreadsheet under the "Worksheet" format. This will be used to update records LIVE on the GGSS
        """

        ss_source_tracker = gc.open(ggss)
        worksheet = ss_source_tracker.worksheet(sheet)

        return worksheet

    def get_df(self, gc, ggss, sheet):
        """

        :param gc: Credentials from connect()
        :param ggss: The name of the spreadsheet we want to retrieve
        :param sheet: name of the sheet
        :return: Sheet in Data Frame Pandas format. This will be used to read information about missing records.
        """
        # Access to spreadsheets
        ss_source_tracker = gc.open(ggss)
        worksheet = ss_source_tracker.worksheet(sheet)
        # Retrieve data
        data = worksheet.get_all_values()
        headers = data.pop(0)

        # Turn into dataFrame to work on pandas
        df = pd.DataFrame(data, columns=headers)

        return df

    def get_missing_week(self, df, last_row, datasource_id, last_week):
        """
        This method will read over the spreadsheet and obtain those DataSources Ids that are missing some week/s
        of data, and the corresponding weeks in a dictionary.

        :param df: dataFrame (Data tracker)
        :return: dictionary with datasource id as keys, and YearWeek code as values (of the missing weeks)
        """


        # TODO: refactor this function

        df_weekly = pd.concat([df.iloc[0:last_row, datasource_id], df.iloc[0:last_row, last_week:]], axis=1)
        df_test = df_weekly.copy()

        df_test = df_test.set_index(df_test.columns[0])
        df_test = df_test.stack().reset_index()
        df_test = df_test[df_test[df_test.columns[2]] == '-']
        df_test = df_test.drop(df_test.columns[2], axis=1).reset_index(drop=True)

        for i, year in enumerate(df_test[df_test.columns[1]].tolist()):
            if year[:4] != '2020': # Only looking for missing sources in 2020 toggle on. Will eliminate for escalation later on
                df_test = df_test.drop(i, axis=0)

        df_test = df_test.reset_index(drop=True)

        for i, week in enumerate(df_test[df_test.columns[1]].tolist()):
            df_test.loc[i, df_test.columns[1]] = str(week[:4]) + str(week[-2:])  # week[-2:]

        missing_week = {k: g[df_test.columns[1]].tolist() for k, g in df_test.groupby(df_test.columns[0])}

        return missing_week

    def get_status(self, df, last_row, datasource_id, last_week):
        """
        This method will read over the spreadsheet and obtain DataSources Ids (of those that are in "?" or "L" status)
        in some week/s of data, and the corresponding weeks in a dictionary.

        This dictionary will be used to run the automatic queries on Postgres.

        :param df: DataFrame previously retrieved
        :return: dictionary with DataSource Id as Key and YearWeek code as values
        """

        # TODO: refactor this function

        df_weekly = pd.concat([df.iloc[0:last_row, datasource_id], df.iloc[0:last_row, last_week:]], axis=1)
        df_test = df_weekly.copy()

        df_test = df_test.set_index(df_test.columns[0])
        df_test = df_test.stack().reset_index()

        negative = ['?', 'L', "l"]
        df_test = df_test[df_test[df_test.columns[2]].isin(negative)]
        df_test = df_test.drop(df_test.columns[2], axis=1).reset_index(drop=True)

        for i, year in enumerate(df_test[df_test.columns[1]].tolist()):
            if year[:4] != '2020': # Only looking for missing sources in 2020 toggle on. Will eliminate for escalation later on
                df_test = df_test.drop(i, axis=0)

        df_test = df_test.reset_index(drop=True)

        for i, week in enumerate(df_test[df_test.columns[1]].tolist()):
            df_test.loc[i, df_test.columns[1]] = str(week[:4]) + str(week[-2:])  # week[-2:]

        loading_status = {k: g[df_test.columns[1]].tolist() for k, g in df_test.groupby(df_test.columns[0])}

        return loading_status

    def get_directories(self, missing_week, df, last_row, datasource_id, ftp_dir):
        """

        :param missing_week: Dictionary obtained with get_missing_week.
        :param df: DataFrame
        :return: dictionary with DataSource Id as Keys and ftp paths as values
        """
        missing_dir = dict()

        df = df.iloc[0:last_row, [datasource_id, ftp_dir]]
        for k in missing_week.keys():
            df_dir = df[df[df.columns[0]] == str(k)]
            missing_dir[k] = df_dir.loc[:, df_dir.columns[1]].tolist()[0]

        return missing_dir

    # Helpers
    def get_column(self, df, header):
        i = df.columns.get_loc(header)
        return i

    def get_row(self, df, key):
        i = df[df[df.columns[4]] == str(key)].index.to_list()[0]
        return i

    def source_name(self, df, datasource):
        """
        :param datasource: String of data source id
        :param df: Data Tracker in dataframe

        @:return source_name: name of the source in column "Source"
        """

        df = df.iloc[:, [0,4]]
        source_name = df[df[df.columns[1]] == str(datasource)].loc[:,df.columns[0]].to_list()[0]
        return source_name
