# Class for reading and processing FIT files
import pandas as pd
import fitparse
import datetime as dt
from pytz import timezone
import pytz
import pdb

class DataLoader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data      = None
        # Convert timestamp to IST
        self.utc = pytz.UTC
        self.ist = pytz.timezone('Asia/Kolkata')

    def read_fit_file(self):
        """Reads a FIT file and extracts running metrics."""
        fit_data = fitparse.FitFile(self.file_path)
        records = []

        for record in fit_data.get_messages('record'):
            data = {}
            for field in record:
                if field.name and field.value is not None:
                    if field.name != "timestamp":
                        data[field.name] = field.value
                    else:
                        # pdb.set_trace()
                        # pass
                        data[field.name] = field.value.replace(tzinfo=self.utc).astimezone(self.ist) 
            # pdb.set_trace()
            data["speed"] = data.pop("enhanced_speed")
            records.append(data)

        self.data = pd.DataFrame(records)

    def preprocess_data(self):
        """Prepares data: selects columns, converts timestamp, resamples."""
        if self.data is None:
            raise ValueError("No data to preprocess. Please read the FIT file first.")

        columns_to_keep = ['timestamp', 'heart_rate', 'cadence', 'speed', 'power', 'step_length']
        # pdb.set_trace()
        self.data = self.data[[col for col in columns_to_keep if col in self.data.columns]]

        self.data['timestamp'] = pd.to_datetime(self.data['timestamp'])
        self.data.set_index('timestamp', inplace=True)

        # Resample and calculate 1-minute moving averages
        self.data = self.data.resample('1min').mean().interpolate()

    def save_clean_data(self, output_path):
        """Saves the processed data to a CSV file."""
        if self.data is None:
            raise ValueError("No data to save. Please preprocess the data first.")

        self.data.to_csv(output_path)
        print(f"Data saved to {output_path}")

# Example usage
if __name__ == "__main__":
    loader = DataLoader('LSD/15-Feb-2025.fit')
    loader.read_fit_file()
    loader.preprocess_data()
    loader.save_clean_data('data/processed/cleaned_fit_data.csv')
