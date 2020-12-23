from datetime import datetime, timedelta
import re


class ExtractWeek:

    # TODO: for some sources, adding the first 4 digits and last 2 won't work in previous years (e.g 2019 + 91). Refactor that.

    def __init__(self):
        pass

    def get_files(self, lines, r_week, r_date, r_format):

        """
        The Following method will read over the dictionary "lines".
        For the file names in "Week" Format, it will process a "Week" regex, convert it to YearWeek code
        and store it in the dict weeks_rd
        For the file names in "Date" Format, it will process a "Date" regex and add the Date format included in another
        dict. Then it will convert it into YearWeek code and store it in weeks_rd.


      :param lines: dict with data source that have missing weeks as keys and file_names of the corresponding ftp as values
      :param r_week: dict with data source as key and regex to extract the Week Number from the file_name
      :param r_date: dict with data source as key and regex to extract the Date from the file_name
      :param r_format: dict with data source as key and the "date format" (e.g %y%m%d) as value

      :return WeeksRd: dict with data source as key and ALL of the files that we have on ftp given on "YYYYWW" format, for
      a given DataSource
        """

        name = dict()
        asd = dict()
        weeks_rd = dict()

        for k in set(lines.keys()):
            for v in lines[k]:
                tokens = v.split(maxsplit=9)

                # Initiate keys in dict

                if k not in name:
                    name[k] = []
                if k not in asd:
                    asd[k] = []
                if k not in weeks_rd:
                    weeks_rd[k] = []

                # All file names (3 is the split that includes the file name)
                name[k].append(tokens[3])

            if k in list(r_date.keys()):  # Examining ONLY the sources with file names in "Date" format
                asd[k].append(re.compile(r_date[k]))
                for v in list(name[k]):
                    try:
                        # TODO: try to find a solution to specific cases from within the ggss. Code should not adapt

                        # Sources that need +1 days
                        if k in ['3156', '3041', '2836']:
                            days = 1
                        # Need -4 days (some of them only -1, others -4. however -4 works for all of them)
                        elif k in ['3279', '2375', '4367', '3100', '3944', '3482', '2407', '3748', '1964', '3992']:
                            days = -4
                        # No changes in days
                        else:
                            days = 0

                        # Apply regex to get the associated date.
                        date = datetime.strptime(asd[k][0].findall(v)[0], r_format[k])
                        # Concat "YYYY" (isocalendar()[0]) + "WW" (isocalendar()[1])
                        added_result = str(date.date().isocalendar()[0]) + str((date + timedelta(days=days)).date().isocalendar()[1])
                        # Append results
                        weeks_rd[k].append(added_result)

                    except:
                        pass

            elif k in list(r_week.keys()):  # Now examining those with file name in "Week" format
                asd[k].append(re.compile(r_week[k]))

                for v in list(name[k]):
                    try:

                        if k == '1882':  # This particular case needs 1 extra week.
                            extra = 1
                        else:
                            extra = 0

                        # Apply regex and get Year-Week code
                        week = str(asd[k][0].findall(v)[0][:4]) + str(int(asd[k][0].findall(v)[0][-2:]))
                        # Add/Subtract relevant extra weeks
                        added_weeks = str(int(week) + extra)
                        # Append results
                        weeks_rd[k].append(added_weeks)

                    except:
                        pass

        return weeks_rd

    def get_arrivals(self, weeks_rd, m_week):
        """
        This method will compare both dicts (weeks_rd, where we have all the available files for DataSources that have
        missing weeks, and m_week, where we have the exact weeks that are missing) and take the NEW arrived ones.

        :param weeks_rd: dict with data source as key and ALL of the files that we have on ftp given on "YYYYWW" format
        :param m_week: dict with data source that has missing weeks of data as key and the missing data given on "YYYYWW" format

        :return: final: dict with data source id as key and the new arrival data as value given on "YYYYWW" format
        """
        final = dict()

        for k in list(weeks_rd.keys()):
            for v in list(weeks_rd[k]):
                if v in (m_week[k]):
                    if k not in final:
                        final[k] = []

                    final[k].append(v)
                    print(v, 'was found for datasource', k)

        return final
