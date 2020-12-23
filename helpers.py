import datetime
from datetime import timedelta


def get_first_day(year_week):
    """

    :param year_week: YearWeek code
    :return: start_date of that week in "YYYY-MM-DD" format. It takes start day as Monday.
    """
    start_date = (datetime.datetime.strptime(str(int(year_week) - 1) + '-1', "%Y%W-%w").date()).strftime("%Y-%m-%d")

    return start_date


def get_last_day(year_week):
    """

    :param year_week: YearWeek code
    :return: end_date of that week in "YYYY-MM-DD" format. It takes end date as Sunday.
    """
    end_date = (
        (datetime.datetime.strptime(str(int(year_week) - 1) + '-6', "%Y%W-%w") + timedelta(days=1)).date()).strftime(
        "%Y-%m-%d")

    return end_date


def edit_header(header):
    """
    Needed to find the "headers" on the spreadsheet. It receives a year week code and returns it in the header format.

    Note that this might only work for SS Data Tracker

    :param header: YearWeek Code
    :return: Header in GGSS format
    """
    header = header[:4] + "\nW" + header[-2:]

    return header
