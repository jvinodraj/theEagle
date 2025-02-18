import pandas as pd
import fitparse
from pytz import timezone
import datetime

def load_df_fitparse(file_name):
    ist = timezone("Asia/Kolkata")
    recs  = fitparse.FitFile(file_name)
    data = []
    for record in recs.get_messages("record"):
        data_dict = {field.name: field.value for field in record}
        # print(data_dict)
        data.append(data_dict)
        # print(data)
    df = pd.DataFrame(data)
    df["timezone_ist"] = df["timestamp"].dt.tz_localize("UTC").dt.tz_convert(ist)
    return df

def analyze_sprint_intervals(df, power_threshold=200, discard_interval_sec=30):
    """
    Analyze sprint intervals and calculate average power for each sprint.

    :param df: Pandas DataFrame with 'timestamp' and 'power' columns.
    :param power_threshold: Minimum power to consider as a sprint (adjust as needed).
    """
    sprint_intervals = []
    in_sprint = False
    current_sprint = []
    timerange_interval = []


    for i, row in df.iterrows():
        if row['power'] >= power_threshold:
            if not in_sprint:
                in_sprint = True
                start_time = row['timezone_ist']
                current_sprint = [row['power']]
            else:
                current_sprint.append(row['power'])
        else:
            if in_sprint:
                in_sprint = False
                end_time = row['timezone_ist']
                # import pdb
                # pdb.set_trace()
                if (end_time - start_time).total_seconds() < discard_interval_sec:
                    continue
                if current_sprint:
                    sprint_intervals.append(current_sprint)
                    timerange_interval.append((start_time, end_time))

    # Print average power for each sprint
    for i, sprint in enumerate(sprint_intervals):
        avg_power = sum(sprint) / len(sprint)
        start_time = timerange_interval[i][0].time()
        end_time   = timerange_interval[i][1].time()
        print(f"Sprint {i+1}: Avg Power = {avg_power:.2f} Watt; between {start_time} and {end_time}")



if __name__ == "__main__":
    file_name = r"C:\Users\a717631\OneDrive\Documents\Repo\theEagle\interval\18-Feb-2025.fit"
    df = load_df_fitparse(file_name)

    # Run analysis
    analyze_sprint_intervals(df, power_threshold=350, discard_interval_sec=45)


