import os
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from fitparse import FitFile
from pytz import timezone

def extract_data_from_fit(file_path):
    """
    Extracts timestamp, heart_rate, power, and enhanced_speed from a FIT file,
    converts timestamp to IST, and computes pace (min/km).
    """
    records = []
    fitfile = FitFile(file_path)
    for record in fitfile.get_messages('record'):
        data_dict = {data.name: data.value for data in record}
        if ('timestamp' in data_dict and 'heart_rate' in data_dict and 
            'power' in data_dict and 'enhanced_speed' in data_dict):
            # Convert timestamp from UTC to IST
            timestamp = data_dict['timestamp'].replace(tzinfo=timezone("UTC")).astimezone(timezone("Asia/Kolkata"))
            heart_rate = data_dict['heart_rate']
            power = data_dict['power']
            enhanced_speed = data_dict['enhanced_speed']  # in m/s

            # Calculate pace in minutes per kilometer: pace = (1000 / speed) / 60
            pace = (1000 / enhanced_speed) / 60 if enhanced_speed and enhanced_speed > 0 else None

            records.append({
                'timestamp': timestamp,
                'heart_rate': heart_rate,
                'power': power,
                'pace': pace
            })
    return records

def load_easy_runs_data(folder_path="easy_runs"):
    """
    Loads and combines data from all FIT files in the specified folder into a DataFrame.
    """
    all_records = []
    for file in os.listdir(folder_path):
        if file.endswith(".fit"):
            file_path = os.path.join(folder_path, file)
            all_records.extend(extract_data_from_fit(file_path))
    return pd.DataFrame(all_records)

# Load the data
df = load_easy_runs_data("easy_runs")

# Filter to only include records with power >= 181 W
df_filtered = df[df['power'] >= 181].copy()

# Create custom power bins
# For example, bins: 181-185, 186-190, 191-195, etc.
# We'll use bins of width 5. Define bin edges starting at 181.
max_power = int(df_filtered['power'].max())
# Add a little extra to include the max value.
bins = np.arange(181, max_power + 6, 5)

# Create labels for bins: e.g., "181-185", "186-190", ...
labels = [f"{bins[i]}-{bins[i+1]-1}" for i in range(len(bins)-1)]

# Bin the power values using pd.cut (using right=False so the interval is [lower, upper))
df_filtered['power_bin'] = pd.cut(df_filtered['power'], bins=bins, right=False, labels=labels)

# Group by power_bin and compute average (mean) pace, median pace, and count
grouped = df_filtered.groupby('power_bin')['pace'].agg(['mean', 'median', 'count']).reset_index()

print(grouped)

# Visualization: Plot average pace (min/km) against power bins.
plt.figure(figsize=(10,6))
plt.plot(grouped['power_bin'], grouped['mean'], marker='o', linestyle='-', label='Average Pace')
plt.xlabel('Power Bin (W)')
plt.ylabel('Pace (min/km)')
plt.title('Average Pace vs. Power Bins')
plt.grid(True)
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()
plt.show()
