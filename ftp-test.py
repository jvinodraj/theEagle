from fitparse import FitFile
import pandas as pd
import os
import datetime

class FTPTest:
    def __init__(self, folderpath):
        self.folder_path = folderpath
        self.fit_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(".fit")]

    def extractFitFiles(self, fit_file_path):
        try:
            fitfile = FitFile(fit_file_path)
        except:
            return pd.DataFrame()

        data = []
        sel_cols = ['timestamp', 'enhanced_speed', 'power', 'heart_rate']
        for record in fitfile.get_messages("record"):
            record_data = {}
            for field in record.fields:
                record_data[field.name]=field.value
            # if record_data["power"] > 0:
            data.append(record_data)

        df = pd.DataFrame(data)[sel_cols] if data else pd.DataFrame()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df

    def calculateFTP(self):
        for file in self.fit_files:
            df = self.extractFitFiles(file)
            return df
            

if __name__ == "__main__":
    folder_path = r"C:\Users\a717631\FTPTests"
    ftp = FTPTest(folder_path)
    df = ftp.calculateFTP()
    start_time = df['timestamp'][0]
    print("Start Time(UTC): ", start_time)
    df['time_diff'] = (df['timestamp'] - start_time).dt.total_seconds() / 60
    ftp_test_df = df[(df['time_diff']>=20) & (df['time_diff']<=40)]
    ftp_test_df = ftp_test_df[ftp_test_df["power"] > 0] # filtering out zero power
    avg_20min_pow = ftp_test_df["power"].mean()
    FTP = avg_20min_pow *.95
    print(ftp_test_df)
    print("20 Min Avg Power: ", avg_20min_pow)
    print("FTP : ", FTP)    
