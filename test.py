import os
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fitparse import FitFile
from pytz import timezone

def extract_data_from_fit(file_path):
    """
    Extracts timestamp, heart_rate, power, and enhanced_speed from a FIT file,
    converts the timestamp to IST, and computes pace (min/km).
    """
    records = []
    fitfile = FitFile(file_path)
    for record in fitfile.get_messages('record'):
        # Build a dictionary of field values
        data_dict = {data.name: data.value for data in record}
        # Check for required fields
        if ('timestamp' in data_dict and 'heart_rate' in data_dict and 
            'power' in data_dict and 'enhanced_speed' in data_dict):
            
            # Convert timestamp from UTC to IST
            timestamp = data_dict['timestamp'].replace(tzinfo=timezone("UTC")).astimezone(timezone("Asia/Kolkata"))
            heart_rate = data_dict['heart_rate']
            power = data_dict['power']
            enhanced_speed = data_dict['enhanced_speed']  # in m/s
            
            # Calculate pace (min/km) = (1000 / speed in m/s) / 60
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

# Load data from the "easy_runs" folder
df = load_easy_runs_data("easy_runs")

# Create a new column with just the date (from the timestamp)
df['date'] = df['timestamp'].dt.date

# Optional: Print the DataFrame to inspect the data
print(df.head())

# For each day, create a plot of pace vs. heart rate and power
for date, group in df.groupby('date'):
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    # Plot heart rate vs. pace on the left y-axis
    color_hr = 'tab:red'
    ax1.set_xlabel('Pace (min/km)')
    ax1.set_ylabel('Heart Rate (bpm)', color=color_hr)
    ax1.scatter(group['pace'], group['heart_rate'], color=color_hr, alpha=0.7, label='Heart Rate')
    ax1.tick_params(axis='y', labelcolor=color_hr)
    
    # Create a twin axis for power on the right y-axis
    ax2 = ax1.twinx()
    color_power = 'tab:blue'
    ax2.set_ylabel('Power (W)', color=color_power)
    ax2.scatter(group['pace'], group['power'], color=color_power, alpha=0.7, label='Power')
    ax2.tick_params(axis='y', labelcolor=color_power)
    
    plt.title(f"Pace vs. Heart Rate and Power on {date}")
    fig.tight_layout()  # Adjust layout to prevent clipping
    save_chart_folder = "easy_runs"
    filename = date + ".png"
    plt.savefig(os.path.join(save_chart_folder, filename), bbox_inches="tight")
    plt.show()
