# Data Tracking Process

## About

The Data Analysts of the team were doing this task manually up until recently. The process entailed the following:

1. Checking every ftp path manually to see whether the new files arrived
2. Checking every ftp path manually to see whether the **old** files arrived*
3. Manually updating the Google Spreadsheet tracker
4. Manually checking another internal tool to see that the loading went through.

*probably the most daunting task, as these files could arrive at any time without previous notice. Weeks could go by without even noticing the arrival of old files.

The process would take almost most of the time from Mondays to Wednesdays (around 18 hours).

The purpose of this project is to deliver an automatic GGSS Updater that will automate the first 3 points established below and leave the final checking for the analysts, where they can actually add value on their own.
The system will also work as a "monitor" of the files that arrive in the ftp and notify the analysts when this happens.

## Structure

### Google Spreadsheet
The team tracks the arrival of weekly files of data in a google spreadsheet that has the following format:
![1][]

In the first 20 columns there is information about the companies. Among those, the most important (or taken into account in this code) are:

- Company Name
- Datasource ID (Unique identifier)
- Ftp location (where the files arrive on the ftp server)

From column 20 onwards, there is information about the arrivals of those files. As depicted above, the top x-intercept provides "Year-Week" codes to identify
which week it is referring to. Below, a status for that specific file is depicted. The legend for tracker goes as follows:

- "x" `(Loaded)`
- "l" `(loading)`
- "?" `(arrived but not loaded)`
- "-" `(did not arrive)`

[1]: https://i.ibb.co/Kb4QhK5/ttttt.png

### FTP Server

For each source, files will arrive at a certain ftp directory following a specific format. For instance, some files will send the start date of the week and end date of the week in the name:
```python
"3020_DATA_VERSION1_15-06-2020_21-06-2020.csv" # for week 25 of 2020 for data source 3020
```
Others, will provide a "Year-week" code
```shell
"1080_DATA_VERSION1_2020025.csv" # for week 25 of 2020 for data source 1080
```

## Initialize

### Extra files

To run this process, you will need 4 external files that are not committed in this repository. These are:

- `ftpSettings.ini`
- `psqlSettings.ini`
- `keys.ini`
- `APIkey.json`

The first 2 will contain credentials and external information about both the FTP Server and PostgreSQL. The `.json` file will
contain the key for the Google API. This API will need the `Sheets API` and `Drive API` to be enabled in order for the system to work. `keys.ini` will contain the path location of the credentials. To get the credentials,
you will need to create a service account and then enable the corresponding APIS and export keys in a `.json` file. More information about how to do this can be [**found here**](https://developers.google.com/android/management/service-account).

Bare in mind, for the python scripts to access the corresponding spreadsheets, you **will have to share these with the service account**. Otherwise, it will not work.

### Run

To run the system there will be 3 different main files. Each of them refers to a tab in the spreadsheet. Open the shell and run:

```shell
python main.py
```

Then the process will start.

## Process

### Arrivals

The first part of the process consists of retrieving the new arrivals in the ftp.

In order to achieve this, we need to:

1. Know which sources are missing
2. Know what we have on ftp
3. Compare and balance out

#### Scanning over the spreadsheet

The methods in `googleAPI.py` will retrieve the data mentioned in the first point from the spreadsheets in dictionaries. These dictionaries will include "data source ids" as keys and "year-week" codes for the sources that are missing as values.

For instance, if the source that has data source id = 3020 is missing data for weeks 25, 24 and 23, the method `get_missing_weeks()` will return the following:

```python
{"3020":["202025", "202024", "202023"]}
```

Another important tool will be the ftp directory associated with each data source id. For this purpose, the method `get_missing_directories()` will return a dictionary with the ftp directories of the sources that have missing files, as depicted below:

```python
{"3020":["//ftp/source1/DATA"]}
```

A similar process occurs for the files marked as either "l" ("L") or "?". For these sources, data will be retrieved and soon after automatic queries will be run on PostgreSQL to identify the loading status.


#### Accessing ftp server

Once both dictionaries are available, the system will loop over the keys and access the corresponding ftp directory of each source.

A new dictionary will be created, for which for each data source, the name of the files associated with it will be stored. While iterating over the lines, we will split them and take the file names and store them in the dictionary that will look as follows:

```shell
{"3020":["3020_DATA_VERSION1_15-06-2020_21-06-2020.csv", "3020_DATA_VERSION1_08-06-2020_14-06-2020.csv", etc]}
``` 

#### From file names to actionable dates


Since the dates of arrival of the files will most likely not coincide with the dates to which the file's data belongs to, extracting the dates from the file names is the most reliable way of associating them with a certain week.

Unfortunately, not all files share the naming patterns. As shown above, some of the provide "Year-week" codes, other provides dates and not particularly in that order.

For this reason, a google spreadsheet containing the necessary regex pattern for each data source was created. The methods in `googleAPI.py` will retrieve this data in dictionaries, for which they'll be futher looped so as to associate each regex with a certain data source id and a certain file name. We divided this in 2 categories:

1. Files that provide dates
2. Files that provide "Year-week" codes

For the files that provided dates, we will also include the date format to translate it using the `strptime` and `strftime`.

The aforementioned spreadsheet looks as follows:

![2][]

[2]:https://i.ibb.co/Wty0MZL/regex.png

Later on, the methods in `regex.py` will retrieve the necessary data in dictionaries. Again, associating the data to a particular data source.

Once all dictionaries are ready, the process in `weekExtraction.py` will:

1. For those that are as type "d", in the missing_week dictionary, apply regex and date format over the file names, convert them into YearWeek codes and store them in a dictionary with Data Source ID as keys and Year-week code as values.

2. For those that are as type "w", apply regex and store in the same dictionary.

This final dictionary, named `weeks_rd`, will contain all the files that are on ftp for each source:

```shell
# weeks_rd

{3020:[202024, 202023, 202022... YYYYWW]} # Files on ftp for data source 3020
```

Once this is done, the method `get_arrivals(weeks_rd, missing_week)` will compare what is on the ftp (weeks_rd) vs what it is missing. In our previous example, we said that data source id was missing weeks 25, 24 and 23. However, the `weeks_rd` now contains weeks 24 and 23. That means those weeks did arrive on ftp. For this, it will return a new dictionary named `arrivals`. The nature of this dictionary is quite self-explanatory: all new arrivals will be stored there.

```shell
# arrivals
{"3020":[202024, 202023]}
```

### Marking

After the arrivals dictionary is ready, the methods in `worksheetMark.py` will mark the previously missing fields (marked as "-") on the google spreadsheet as "?"; the files are on ftp but not loaded yet.

For those in the dictionary containing sources that are currently loading, or arrived but did not load yet, automatic queries on PostgreSQL will be ran to identify the loading status. The queries and the connection methods will be found on `psql.py`, The logic works as follow:

- If the loading status = 4, then the file is loaded ("x")
- If not, then the file is loading ("l")
- If the query does not go through, it means the loading did not start (remain on "?")


