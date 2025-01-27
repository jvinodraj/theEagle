import fitparse
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Load FIT file and parse data
def load_fit_file(fit_file_path):
    fitfile = fitparse.FitFile(fit_file_path)
    data = []
    
    for record in fitfile.get_messages('record'):
        record_data = {}
        for record_data_field in record:
            record_data[record_data_field.name] = record_data_field.value
        data.append(record_data)
    
    return pd.DataFrame(data)

# Load the FIT file
fit_file_path =  r"C:\Users\username\Downloads\18111378159_ACTIVITY.fit"    # Replace with your FIT file path
df = load_fit_file(fit_file_path)

# Ensure required columns exist
required_columns = ['timestamp', 'heart_rate', 'power']
assert all(col in df.columns for col in required_columns), "FIT file is missing required fields."

# Handle missing values and sort data by time
df = df.dropna(subset=required_columns)
df = df.sort_values(by='timestamp')
df['time'] = (df['timestamp'] - df['timestamp'].iloc[0]).dt.total_seconds()

# 1. Scatter Plot (Power vs. Heart Rate)
plt.figure(figsize=(10, 6))
plt.scatter(df['heart_rate'], df['power'], c='blue', alpha=0.5)
plt.title('Power vs. Heart Rate', fontsize=16)
plt.xlabel('Heart Rate (bpm)', fontsize=14)
plt.ylabel('Power (Watts)', fontsize=14)
plt.grid(alpha=0.3)
plt.show()

# 2. Time-Series Plot (Power and HR Over Time)
plt.figure(figsize=(12, 6))
plt.plot(df['time'], df['heart_rate'], label='Heart Rate (bpm)', color='red', alpha=0.7)
plt.plot(df['time'], df['power'], label='Power (Watts)', color='blue', alpha=0.7)
plt.title('Power and Heart Rate Over Time', fontsize=16)
plt.xlabel('Time (s)', fontsize=14)
plt.ylabel('Values', fontsize=14)
plt.legend()
plt.grid(alpha=0.3)
plt.show()

# 3. Zone Analysis (Average Power vs. HR Zone)
def classify_hr_zone(hr):
    if hr <= 134:
        return "Zone 2"
    elif hr <= 153:
        return "Zone 3"
    elif hr <= 173:
        return "Zone 4"
    else:
        return "Zone 5"

df['hr_zone'] = df['heart_rate'].apply(classify_hr_zone)
zone_avg_power = df.groupby('hr_zone')['power'].mean().reindex(["Zone 2", "Zone 3", "Zone 4", "Zone 5"])

# plt.figure(figsize=(8, 6))
# zone_avg_power.plot(kind='bar', color='green', alpha=0.7)
# plt.title('Average Power by Heart Rate Zone', fontsize=16)
# plt.xlabel('Heart Rate Zone', fontsize=14)
# plt.ylabel('Average Power (Watts)', fontsize=14)
# plt.xticks(rotation=0)
# plt.grid(axis='y', alpha=0.3)
# plt.show()

plt.figure(figsize=(10, 6))
sns.boxplot(x='hr_zone', y='power', data=df, palette='Set3', order=["Zone 2", "Zone 3", "Zone 4", "Zone 5"])
plt.title('Power Distribution by Heart Rate Zone', fontsize=16)
plt.xlabel('Heart Rate Zone', fontsize=14)
plt.ylabel('Power (Watts)', fontsize=14)
plt.grid(axis='y', alpha=0.3)
# plt.save('power by Hr.png')
plt.show()

