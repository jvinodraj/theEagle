import pandas as pd
import numpy as np
import fitparse
from pytz import timezone
# import datetime
from datetime import datetime, time
import pdb

body_weight = 72  # kg, adjust as needed

# Define pretty headers with units on the second line
header_map = {
    "Sprint": "Sprint",
    "duration": "Duration",
    "pace": "Pace",
    "Speed (m/s)": "Speed(m/s)",
    "Power(W)": "Power\n(W)",
    "min_hr": "HR\nmin",
    "max_hr": "HR\nmax",
    "avg_hr": "HR\navg",
    "GCT (ms)": "GCT\n(ms)",
    "Stride Length(m)": "Stride\nLength (m)",
    "Cadence (spm)": "Cadence\n(spm)",
    "VR (%)": "VR\n(%)",
    "VO (cm)": "VO\n(cm)",
    "efficiency (m/W)": "Efficiency\n(m/W)"
}

def load_df_fitparse(file_name):
    ist = timezone("Asia/Kolkata")
    recs  = fitparse.FitFile(file_name)
    data = []
    print("Info : \n", [{field.name: field.value} for msg  in recs.get_messages("file_id") for field in msg])
    [{field.name: field.value} for msg  in recs.get_messages("file_id") for field in msg]
    for record in recs.get_messages("record"):
        # pdb.set_trace()
        data_dict = {field.name: field.value for field in record}
        # print(data_dict)
        data.append(data_dict)
        # print(data)
        # exit(0)
    df = pd.DataFrame(data)
    df["timezone_ist"] = df["timestamp"].dt.tz_localize("UTC").dt.tz_convert(ist)
    return df

def analyze_base_run(df):
    pdb.set_trace()
    # Ensure distance is cumulative in meters
    df['cum_km'] = df['distance'] / 1000

    # Find the split indices for each km
    km_bins = np.arange(0, int(df['cum_km'].max()) + 2)
    labels = range(1, len(km_bins))  # one fewer than bins
    df['km_group'] = pd.cut(df['cum_km'], bins=km_bins, labels=labels, right=False)

    summary = []

    for km in sorted(df['km_group'].dropna().unique(), key=int):
        km_df = df[df['km_group'] == km]
        if km_df.empty:
            continue

        # Pace (min/km)
        avg_speed = km_df['enhanced_speed'].mean()  # m/s
        pace_min_per_km = (1000 / avg_speed) / 60 if avg_speed > 0 else np.nan
        pace_min = int(pace_min_per_km)
        pace_sec = int((pace_min_per_km - pace_min) * 60)
        pace_str = f"{pace_min}:{pace_sec:02d}"

        # Power
        avg_power = km_df['power'].mean()
        # Heart Rate
        min_hr = int(km_df['heart_rate'].min())
        max_hr = int(km_df['heart_rate'].max())
        avg_hr = int(km_df['heart_rate'].mean())
        hr_str = f"{min_hr}-{max_hr}-{avg_hr}"

        # GCT, Stride Length, Cadence, VR, VO
        avg_gct = round(km_df.get('stance_time', pd.Series([np.nan])).mean(), 2)
        avg_stride = round(km_df.get('step_length', pd.Series([np.nan])).mean() / 1000, 2)
        avg_cad = round(km_df.get('cadence', pd.Series([np.nan])).mean() * 2, 0)
        avg_vr = round(km_df.get('vertical_ratio', pd.Series([np.nan])).mean(), 2)
        avg_vo = round(km_df.get('vertical_oscillation', pd.Series([np.nan])).mean() / 10, 2)

        # Efficiencies
        eff_pwr = round(avg_speed / avg_power, 5) if avg_power else np.nan
        eff_hr = round(avg_speed / avg_hr, 5) if avg_hr else np.nan
        eff_stride = round(avg_speed / avg_stride, 5) if avg_stride else np.nan
        eff_cad = round(avg_speed / avg_cad, 5) if avg_cad else np.nan

        summary.append({
            "Distance": km,
            "Pace": pace_str,
            "Speed": round(avg_speed, 2),
            "Power": round(avg_power, 2),
            "HR": hr_str,
            "GCT": avg_gct,
            "Stride Len": avg_stride,
            "Cad": avg_cad,
            "VR": avg_vr,
            "VO": avg_vo,
            "Eff PWR": eff_pwr,
            "Eff HR": eff_hr,
            "Eff Stride": eff_stride,
            "Eff Cad": eff_cad
        })

    # After building the DataFrame
    unit_row = {
        "Distance": "km",
        "Pace": "(min/km)",
        "Speed": "(m/s)",
        "Power": "(W)",
        "HR": "(min-max-avg)",
        "GCT": "(ms)",
        "Stride Len": "(m)",
        "Cad": "(spm)",
        "VR": "(%)",
        "VO": "(cm)",
        "Eff PWR": "(m/W)",
        "Eff HR": "(m/s·bpm⁻¹)",
        "Eff Stride": "(m/s·ms⁻¹)",
        "Eff Cad": "(m/s·spm⁻¹)"
    }

    # Insert the unit row at top of DataFrame
    summary.insert(0, unit_row)
    

    # Print as table
    summary_df = pd.DataFrame(summary)
    print(summary_df.to_string(index=False))

    # Prepare data
    from prettytable import PrettyTable
    table = PrettyTable()
    # import pdb
    # pdb.set_trace()
    table.field_names = [h.replace("\\n", "\n") for h in summary_df.columns]
    for row in summary_df.values:
        table.add_row(row)
    print(table)




if __name__ == "__main__": 
    file_name = r"C:\Users\A717631\fits\Base\28-Jul-2025.fit"
    df = load_df_fitparse(file_name)
    print(file_name)

    # Run analysis
    analyze_base_run(df)
