import configparser

config = configparser.ConfigParser()


class FtpSettings:
    config.read('ftpSettings.ini')

    user = config['credentials']['user']
    password = config['credentials']['password']
    server = config['server']['host']
    port = config['server']['port']


class PsqlSettings:
    config.read('psqlSettings.ini')

    user = config['credentials']['user']
    password = config['credentials']['password']

    host = config['server']['host']
    port = config['server']['port']
    database = config['server']['database']

class GgssSettings:
    config.read('ggss.ini')

    sheet_name = config['sheet']['sheet_name']
    sheet_owner = config['sheet']['owner']


class keySettings:
    config.read('keys.ini')

    key = config['key']['path']

class Ip:
    datasource_id = 4
    ftp_dir = 10
    last_week = 20
    last_row =51

class Tw:
    datasource_id = 4
    ftp_dir = 10
    last_week = 20
    last_row = 37

class Mm:
    datasource_id = 4
    ftp_dir = 10
    last_week = 20
    last_row = 59
