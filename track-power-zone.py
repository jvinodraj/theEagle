import os
import pandas as pd
import matplotlib.pyplot as plt
from fitparse import FitFile

def extract_running_data(file_path, zone2_hr_range):
    """Extract power data for Zone 2 heart rate from a FIT file."""
    try:
        fitfile = FitFile(file_path)
    except Exception as e:
        print(f"Error reading FIT file {file_path}: {e}")
        return pd.DataFrame()
    
    data = []
    for record in fitfile.get_messages("record"):
        record_data = {}
        for field in record.fields:
            record_data[field.name] = field.value
        
        if "heart_rate" in record_data and "power" in record_data and "timestamp" in record_data:
            if zone2_hr_range[0] <= record_data["heart_rate"] <= zone2_hr_range[1]:
                data.append(record_data)
    
    return pd.DataFrame(data) if data else pd.DataFrame()

def process_fit_files(folder_path, zone2_hr_range):
    """Process all FIT files in the specified folder."""
    all_data = []
    
    if not os.path.exists(folder_path):
        print(f"Error: Folder path {folder_path} does not exist.")
        return pd.DataFrame()
    
    for file in os.listdir(folder_path):
        if file.lower().endswith(".fit"):
            file_path = os.path.join(folder_path, file)
            df = extract_running_data(file_path, zone2_hr_range)
            if not df.empty:
                all_data.append(df)
    
    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

def plot_power_zone_boxplot(df):
    """Plot a box plot for Zone 2 power distribution classified by date."""
    if df.empty:
        print("No data available for Zone 2 heart rate.")
        return
    
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["date"] = df["timestamp"].dt.date
    
    plt.figure(figsize=(12, 6))
    df.boxplot(column="power", by="date", grid=True, patch_artist=True, boxprops=dict(facecolor='lightblue'))
    plt.xlabel("Date")
    plt.ylabel("Power (Watts)")
    plt.title("Power Distribution for Zone 2 Heart Rate by Date")
    plt.suptitle("")  # Remove default suptitle
    plt.xticks(rotation=45)
    plt.show()

if __name__ == "__main__":
    folder_path = r"C:\\Users\\username\\Downloads\\EasyRuns"
    zone2_hr_range = (116, 134)  # Example Zone 2 heart rate range, adjust as needed
    
    df = process_fit_files(folder_path, zone2_hr_range)
    if not df.empty:
        plot_power_zone_boxplot(df)
    else:
        print("No valid data found in the provided FIT files.")
