from psql import Psql
from googleAPI import GoogleAPI
from helpers import *


class WorksheetMark:

    def __init__(self):
        pass

    def ftp_arrival(self, arrivals, worksheet, df):

        """
        This method will take the arrival dict, worksheet and dataframe and mark those that Arrived

        :param arrivals: Dict that contains {DataSources:YearWeek code} of new arrivals
        :param worksheet: to update fields
        :param df: DataFrame
        """

        for k in list(arrivals.keys()):
            for v in list(arrivals[k]):
                row = GoogleAPI().get_row(df, k) + 2
                column = GoogleAPI().get_column(df, edit_header(v)) + 1

                try:
                    worksheet.update_cell(row, column, "?")
                    print(k, GoogleAPI().source_name(df, k), v, row, column, 'was updated to: ?')

                except:
                    print('Could not update', k, GoogleAPI().source_name(df, k), edit_header(v), row, column)
                    pass

    def loading(self, loading, worksheet, df):
        """
        This method will update records on the GGSS of the status of those loading on BL.

        :param loading: dict with {DataSource:YearWeek code} of loading sources
        :param worksheet: Worksheet to update records
        :param df: DataFrame
        """

        for k in list(loading.keys()):
            for v in list(loading[k]):

                try:
                    row = GoogleAPI().get_row(df, k) + 2  # + 2 needed to calibrate
                    column = GoogleAPI().get_column(df, edit_header(v)) + 1  # + 1 needed to calibrate

                    if Psql().get_progress(k, v) == 4: #Run Query of DataSource and YearWeek code.
                        #Status = 4 -> Loaded
                        #Status != -> Loading
                        #If the query raises an Error, then the source is not loading.

                        # TODO: Query on failed_tasks table to see which sources have failed, and mark them.

                        val = worksheet.cell(row, column).value
                        if val != "check MM":
                            worksheet.update_cell(row, column, "check MM")
                            print(k, GoogleAPI().source_name(df, k), v, val, 'was changed to check MM')

                    else:
                        val = worksheet.cell(row, column).value

                        if val != 'l':
                            worksheet.update_cell(row, column, "l")
                            print(k, GoogleAPI().source_name(df, k),v, val, 'was changed to L')
                        else:
                            print(k, GoogleAPI().source_name(df, k), v, 'remained the same:', val)

                except:
                    print('Could not query', k, GoogleAPI().source_name(df, k), v)
                    pass
