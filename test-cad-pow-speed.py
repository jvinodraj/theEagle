import os
import datetime
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from fitparse import FitFile
from pytz import timezone

def extract_data_from_fit(file_path):
    """
    Extracts timestamp, cadence, power, and enhanced_speed from a FIT file,
    converts the timestamp to IST, converts cadence to steps per minute (spm),
    and computes pace (min/km).
    """
    records = []
    fitfile = FitFile(file_path)
    for record in fitfile.get_messages('record'):
        # Build a dictionary of field values
        data_dict = {data.name: data.value for data in record}
        # Check for required fields
        if ('timestamp' in data_dict and 'cadence' in data_dict and 
            'power' in data_dict and 'enhanced_speed' in data_dict):
            
            # Convert timestamp from UTC to IST
            timestamp = data_dict['timestamp'].replace(tzinfo=timezone("UTC")).astimezone(timezone("Asia/Kolkata"))
            
            # Convert cadence to steps per minute (spm)
            # Here we assume the cadence value is in strides per minute, so multiply by 2.
            cadence = data_dict['cadence'] * 2
            
            power = data_dict['power']
            enhanced_speed = data_dict['enhanced_speed']  # in m/s
            heart_rate = data_dict['heart_rate']  # in m/s
            
            # Calculate pace in minutes per kilometer: pace = (1000 / speed in m/s) / 60
            pace = (1000 / enhanced_speed) / 60 if enhanced_speed and enhanced_speed > 0 else None
            
            records.append({
                'timestamp': timestamp,
                'cadence': cadence,
                'power': power,
                'pace': pace,
                'heart_rate': heart_rate,
                'enhanced_speed': enhanced_speed
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
import pdb
pdb.set_trace()

# Create a new column with just the date (extracted from the timestamp)
df['date'] = df['timestamp'].dt.date

# Optional: Print the DataFrame to inspect the data
print(df.head())
df.to_csv("easy_runs_data.csv", index=False)

# # For each day, create a plot of pace vs. cadence (in spm) and power
# for date, group in df.groupby('date'):
#     fig, ax1 = plt.subplots(figsize=(10, 6))
    
#     # Plot cadence (spm) vs. pace on the left y-axis
#     color_cadence = 'tab:green'
#     ax1.set_xlabel('Pace (min/km)')
#     ax1.set_ylabel('Cadence (spm)', color=color_cadence)
#     ax1.scatter(group['pace'], group['cadence'], color=color_cadence, alpha=0.7, label='Cadence')
#     ax1.tick_params(axis='y', labelcolor=color_cadence)
    
#     # Create a twin axis for power on the right y-axis
#     ax2 = ax1.twinx()
#     color_power = 'tab:blue'
#     ax2.set_ylabel('Power (W)', color=color_power)
#     ax2.scatter(group['pace'], group['power'], color=color_power, alpha=0.7, label='Power')
#     ax2.tick_params(axis='y', labelcolor=color_power)
    
#     plt.title(f"Pace vs. Cadence (spm) and Power on {date}")
#     fig.tight_layout()  # Adjust layout to prevent clipping
#     plt.show()

# def ThreeDScatterPlot():
# Create 3D scatter plot
# fig = plt.figure(figsize=(10, 7))
# ax = fig.add_subplot(111, projection='3d')

# # Scatter plot with cadence as color
# scatter = ax.scatter(df["pace"], df["heart_rate"], df["power"], 
#                     c=df["cadence"], cmap="viridis", s=50, edgecolors="k")

# # Labels
# ax.set_xlabel("Pace (min/km)")
# ax.set_ylabel("Heart Rate (bpm)")
# ax.set_zlabel("Power (Watts)")
# ax.set_title("3D Scatter Plot: Pace vs Power vs HR (Color: Cadence)")

# # Color bar for cadence
# cbar = fig.colorbar(scatter, ax=ax, shrink=0.6)
# cbar.set_label("Cadence (spm)")

# plt.show()

import pdb
pdb.set_trace()

# Pivot data for heatmap (Power vs Date, values as Pace)
# heatmap_data = df.pivot(index="date", columns="power", values="pace")

# Aggregate duplicate values using 'mean'
heatmap_data = df.pivot_table(index="date", columns="power", values="pace", aggfunc="mean")

# Plot heatmap
plt.figure(figsize=(12, 6))
sns.heatmap(heatmap_data, cmap="coolwarm", annot=True, fmt=".2f", linewidths=0.5)

# Labels and title
plt.title("Heatmap: Pace Trend vs Power Output Over Time")
plt.xlabel("Power (Watts)")
plt.ylabel("Date")
plt.xticks(rotation=45)

plt.show()