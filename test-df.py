import fitparse
import pandas as pd

def load_df_fitparse(file_name):
    recs  = fitparse.FitFile(file_name)
    data = []
    for record in recs.get_messages("record"):
        data_dict = {field.name: field.value for field in record}
        # print(data_dict)
        data.append(data_dict)
        # print(data)
    return pd.DataFrame(data)

    # Classification based on efficiency score
    def classify_efficiency(score):
        if score > 1.2:  # High power, low HR
            return "Efficient"
        elif score > 0.8:  # Moderate efficiency
            return "Average"
        elif score > 0.5:  # High HR relative to power
            return "Poor"
        else:  # Very inefficient running
            return "Inefficient"
        
if __name__ == "__main__":
    file_name = r"C:\Users\a717631\OneDrive - Eviden\Documents\Repo\theEagle\easy_runs\17-Feb-2025.fit"
    df = load_df_fitparse(file_name)
    import pdb
    # pdb.set_trace()

    # Sort by timestamp
    df = df.sort_values("timestamp")

    # Convert power to Watts per kg
    df["power_wkg"] = df["power"] / 72  # Assuming your weight is 72 kg

    # Convert timestamp column to datetime and set as index
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df.set_index("timestamp", inplace=True)  # Ensure rolling works with time-based window


    # Compute 5-minute rolling averages
    rolling_window = "5min"
    df["hr_rolling"] = df["heart_rate"].rolling(rolling_window, min_periods=1).mean()
    df["power_rolling"] = df["power_wkg"].rolling(rolling_window, min_periods=1).mean()
    df["cadence_rolling"] = df["cadence"].rolling(rolling_window, min_periods=1).mean()
    df["speed_rolling"] = df["enhanced_speed"].rolling(rolling_window, min_periods=1).mean()
    df["altitude_rolling"] = df["enhanced_altitude"].rolling(rolling_window, min_periods=1).mean()
    df["vo_rolling"] = df["vertical_oscillation"].rolling(rolling_window, min_periods=1).mean()
    df["vr_rolling"] = df["vertical_ratio"].rolling(rolling_window, min_periods=1).mean()

    # Efficiency score calculation (normalized)
    df["efficiency_score"] = (
        df["power_rolling"] / df["hr_rolling"] * 100  # Power per HR unit
    ) * (df["cadence_rolling"] / 180)  # Normalize by cadence (ideal ~180)

        # Classification based on efficiency score
    def classify_efficiency(score):
        if score > 1.2:  # High power, low HR
            return "Efficient"
        elif score > 0.8:  # Moderate efficiency
            return "Average"
        elif score > 0.5:  # High HR relative to power
            return "Poor"
        else:  # Very inefficient running
            return "Inefficient"

    df["efficiency_category"] = df["efficiency_score"].apply(classify_efficiency)

    # Filter only segments where efficiency is sustained for ≥5 minutes
    df_filtered = df[df["hr_rolling"] < df["hr_rolling"].quantile(0.4)]  # Bottom 40% HR

    # Save results
    df_filtered.to_csv("efficient_run_records.csv", index=False)
    print(df_filtered[["timestamp", "power_rolling", "hr_rolling", "efficiency_category"]].head())
    