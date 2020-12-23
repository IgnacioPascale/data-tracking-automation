from googleAPI import GoogleAPI
from regex import Regex
from ftpAccess import FtpTracking
from weekExtraction import ExtractWeek
from worksheetMark import WorksheetMark
from settings import Ip, GgssSettings


class Main:

    def __init__(self):
        pass


if __name__ == "__main__":
    gc = GoogleAPI().connect()
    worksheet = GoogleAPI().worksheet_access(gc, GgssSettings.sheet_name , GgssSettings.sheet_owner)
    data_tracker = GoogleAPI().get_df(gc, GgssSettings.sheet_name, GgssSettings.sheet_owner)

    m_week = GoogleAPI().get_missing_week(data_tracker, Ip.last_row, Ip.datasource_id, Ip.last_week)
    m_dir = GoogleAPI().get_directories(m_week, data_tracker, Ip.last_row, Ip.datasource_id, Ip.ftp_dir)

    regex_ggss = GoogleAPI().get_df(gc, "SS_LOADING_REGEX", "Regex")
    r_week = Regex().get_week(regex_ggss)
    r_date = Regex().get_date(regex_ggss)
    r_format = Regex().get_format(regex_ggss)

    ftp = FtpTracking().connect()
    lines = FtpTracking().get_lines(m_dir)

    weeks_rd = ExtractWeek().get_files(lines, r_week, r_date, r_format)
    arrivals = ExtractWeek().get_arrivals(weeks_rd, m_week)
    loading = GoogleAPI().get_status(data_tracker, Ip.last_row, Ip.datasource_id, Ip.last_week)

    WorksheetMark().ftp_arrival(arrivals, worksheet, data_tracker)

    WorksheetMark().loading(loading, worksheet, data_tracker)
