import psycopg2
from helpers import *
from settings import PsqlSettings


class ConnectionManager:
    def __init__(self):
        pass

    @staticmethod
    def generate_connection_pool():
        """
        Establishes connection with the server.
        It takes the settings imported from the settings.py file
        :return: connection to PSQL Server
        """
        conn = psycopg2.connect(user=PsqlSettings.user, password=PsqlSettings.password, host=PsqlSettings.host,
                                port=PsqlSettings.port, database=PsqlSettings.database)

        return conn


class Psql():

    def __init__(self):
        pass

    def get_progress(self, datasource_id, year_week):
        """
        Runs progress status query of loading DataSource, YearWeek code

        If status ==4 -> loaded, else loading. If it can't run the query (error) then the source is not loading.

        :param datasource_id: DataSource Id of loading source
        :param year_week: YearWeek code of loading source
        :return: status.
        """

        conn = ConnectionManager.generate_connection_pool()
        cur = conn.cursor()

        if datasource_id == '3860':
            # They usually provide start date 2 days earlier than corresponded

            start_date = (datetime.datetime.strptime(get_first_day(year_week), '%Y-%m-%d') - timedelta(
                days=2)).date().strftime('%Y-%m-%d')
        else:
            start_date = get_first_day(year_week)

        end_date = get_last_day(year_week)

        cur.execute("""
            select datasource_id, dt.progress_id, start_date, end_date, ds.progress, created, data_type, comments
        
            from dataset dt inner join dataset_progress ds on dt.progress_id = ds.progress_id
        
            where (start_date between '""" + start_date + """' and '""" + end_date + """'
            or end_date between '""" + start_date + """' and '""" + end_date + """')
            and datasource_id=""" + datasource_id + """
            
            and data_type not in ('C')
            
            order by created DESC
            
            limit 1

        """)

        rows = cur.fetchone()

        progress_id = rows[1]

        cur.close()
        conn.close()

        return progress_id
