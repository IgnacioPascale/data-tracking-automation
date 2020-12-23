import ftplib
from settings import FtpSettings


class FtpTracking:

    def __init__(self):
        pass

    @staticmethod
    def connect():
        """
        Establish connection with ftp server
        :return: ftp pool connection
        """

        ftp = ftplib.FTP(FtpSettings.server)

        username = FtpSettings.user
        password = FtpSettings.password
        ftp.login(username, password)

        return ftp

    def get_lines(self, m_dir):
        """
        get_lines will go over the ftp paths of the DataSources in the arg "m_dir" and get all the lines available
        in the ftp server for that source. It will then proceed to store them in a dictionary.

        :arg m_dir: dictionary with DataSource as key and ftp Paths as values. (of missing weeks)
        :return: lines(dict) that has DataSource as key and the name of the files on the ftp path
        """
        lines = dict()

        toggle_off = ['3025']  # List of DataSources id's we don't want to track

        for k, v in m_dir.items():  # We will look at the keys of the DataSources that have missing data
            if k in toggle_off:
                pass

            else:
                lines[k] = []
                try:
                    ftp = self.connect()
                    ftp.dir(v, lines[k].append)
                except:
                    print('Could not log directory', v)
                    pass

        return lines


class FtpRetrieval:

    def download_file(self, file_name, ftp_dir, dir_local):
        ftp = FtpTracking().connect()
        ftp.cwd(ftp_dir)

        with open(file_name, "wb") as file:
            try:
                frame = ftp.retrbinary("RETR " + file_name,
                                       open(dir_local + "//" + file_name, 'wb').write)
                print('Successfully downloaded', file_name)
            except:
                print('Could not download', file_name)

    def load_file(self, file_name, ftp_dir, dir_local):

        with open(dir_local+file_name, "rb") as file:
            ftp = FtpTracking().connect()
            ftp.cwd(ftp_dir)

            try:

                ftp.storbinary("STOR " +file_name, file)
                print(file_name, "was loaded successfully on", ftp_dir)

            except:

                print('Could not upload', file_name)
                pass

            ftp.quit()
            file.close()
