import pandas as pd
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

def analyze_sprint_intervals(df, power_threshold=200, discard_interval_sec=30):
    """
    Analyze sprint intervals and calculate average power for each sprint.

    :param df:              Pandas DataFrame with 'timestamp' and 'power' columns.
    :param power_threshold: Minimum power to consider as a sprint (adjust as needed).
    :discard_interval_sec:  distacard any interval that is less than with partcular
                            seconds
    """
    in_sprint          = False
    timerange_interval = []
    
    sprint_intervals   = []
    current_sprint     = []
    
    # pace
    current_pace       = []
    pace_interval      = []
    
    # Cadence
    current_cadence    = []
    cadence_interval   = []
    
    # Heart Rate
    current_hr         = []
    hr_interval        = []    
    
    # stance_time
    current_gct         = []
    gct_interval        = []
    
    # stride_length
    current_strlen      = []
    strlen_interval     = []
    
    # vertical_ratio
    current_vr          = []
    vr_interval         = []

    # vertical oscillation
    current_vo          = []
    vo_interval         = []

    for i, row in df.iterrows():
        # pdb.set_trace()
        # print(row['stance_time_balance'])
        if row['stance_time_balance'] != None:
            print(row['stance_time_balance'])
            # pdb.set_trace()

        if row['power'] >= power_threshold:
            if not in_sprint:
                in_sprint       = True
                start_time      = row['timezone_ist']
                current_pace    = [row['enhanced_speed']]
                current_sprint  = [row['power']]
                current_gct     = [row['stance_time']] 
                current_strlen  = [row['step_length']/1000]  # Convert to meters
                current_cadence = [row['cadence'] * 2]
                current_hr      = [row['heart_rate']]
                current_vr      = [row['vertical_ratio']]
                current_vo      = [row['vertical_oscillation']/10]
            else:
                current_pace.append(row['enhanced_speed'])
                current_sprint.append(row['power'])
                current_gct.append(row['stance_time'])
                current_strlen.append(row['step_length']/1000)  # Convert to meters
                current_cadence.append(row['cadence'] * 2)
                current_hr.append(row['heart_rate'])
                current_vr.append(row['vertical_ratio'])
                current_vo.append(row['vertical_oscillation']/10)
                
        else:
            if in_sprint:
                in_sprint = False
                end_time = row['timezone_ist']
                # import pdb
                # pdb.set_trace()
                if (end_time - start_time).total_seconds() < discard_interval_sec:
                    continue
                if current_sprint:
                    timerange_interval.append((start_time, end_time))
                    sprint_intervals.append(current_sprint)
                    pace_interval.append(current_pace)
                    gct_interval.append(current_gct)
                    strlen_interval.append(current_strlen)
                    cadence_interval.append(current_cadence)
                    hr_interval.append(current_hr)
                    vr_interval.append(current_vr)
                    vo_interval.append(current_vo)

    # This will hold the summary of each sprint
    sprint_summary = []
    
    # Print average power for each sprint
    for i, sprint in enumerate(sprint_intervals):
        avg_power = sum(sprint) / len(sprint)
        start_time = timerange_interval[i][0].time()
        end_time   = timerange_interval[i][1].time()
        # import pdb
        # pdb.set_trace()
        total_speed   = sum(pace_interval[i]) / len(pace_interval[i])
        # pace_min_per_km = (1000 / total_speed) / 60
        pace_in_minutes = (1000 / total_speed) / 60
        minutes = int(pace_in_minutes)
        seconds = int((pace_in_minutes - minutes) * 60)
        formatted_pace = f"{minutes}:{seconds:02d}"
        
        #calculating GCT
        avg_gct = sum(gct_interval[i]) / len(gct_interval[i])

        # stride length
        avg_strlen = sum(strlen_interval[i]) / len(strlen_interval[i])

        # avg cadence
        avg_cad = sum(cadence_interval[i]) / len(cadence_interval[i])

        #heart rate calculation
        avg_hr  = sum(hr_interval[i]) / len(hr_interval[i])
        min_hr  = min(hr_interval[i])
        max_hr  = max(hr_interval[i])

        #vertical ratio calculation 
        avg_vr = sum(vr_interval[i]) / len(vr_interval[i])

        #vertical oscillation calculation
        avg_vo = sum(vo_interval[i]) / len(vo_interval[i])

        # Convert to datetime by adding a common date
        start_dt = datetime.combine(datetime.today(), start_time)
        end_dt = datetime.combine(datetime.today(), end_time)

        # Calculate the difference
        delta = end_dt - start_dt
        # print(delta)
        # print(f"Total seconds: {delta.total_seconds()}")

        #Efficiency calculation
        if avg_power > 0:
            efficiency = (total_speed ) / avg_power
            # print(f"Efficiency: {efficiency:.2f} m/W")
        else:
            efficiency = 0
            # print("Efficiency: N/A (Power is zero)")

        #Heart Rate based Mechanical Efficiency
        hr_efficiency = (total_speed) / avg_hr

        #Stride Based Mechanical Efficiency
        stride_efficiency = (avg_strlen) / avg_gct

        #Cadence based Mechanical Efficiency
        cadence_efficiency = (total_speed) / avg_cad

        #Minx, Max and Avg HR
        hr = f"{min_hr}-{max_hr}-{round(avg_hr)}"

        sprint_summary.append({
            "Sprint": i + 1,
            "Delta": str(delta).replace("0 days, ", ""),
            "Pace": formatted_pace,
            "Speed": round(total_speed, 2),
            "Power": round(avg_power),
            "HR": hr,
            "GCT": round(avg_gct, 2),
            "Stride Len": round(avg_strlen, 2),
            "Cad": round(avg_cad),
            "VR": round(avg_vr, 2),
            "VO": round(avg_vo, 2),
            "Eff PWR": round(efficiency, 5),
            "Eff HR": round(hr_efficiency, 5),
            "Eff Stride": round(stride_efficiency, 5),
            "Eff Cad": round(cadence_efficiency, 5)
        })


        print(f"Sprint {i+1}: \
Δ={delta}; Pace={formatted_pace}; S={total_speed:.2f}; Pow={avg_power:.2f}W; HR(min-max-avg)={min_hr}-{max_hr}-{avg_hr:.0f}; \
GCT={avg_gct:.2f}ms; SL={avg_strlen:.2f}m; Cad={avg_cad:.0f}; VR={avg_vr:.2f}% \
VO={avg_vo:.2f}cm; Eff={efficiency:.5f} m/W")
        #   [{start_time} - {end_time}] \
    print("\nLegend: \nΔ = duration, P = Power, HR = Heart Rate, GCT = Ground Contact Time, Cad = Cadence(spm), VR = Vertical Ratio, VO = Vertical Oscillation\n"
    "SL = Stride Length, Pace = min/km, S = Speed m/s, Eff = Power based Mechanical Efficiency m/W\n")

    # After building the DataFrame
    unit_row = {
        "Sprint": "",
        "Delta": "",
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
    sprint_summary.insert(0, unit_row)
    # Convert sprint_summary to DataFrame for better visualization
    sprint_summary_df = pd.DataFrame(sprint_summary)
    
    # sprint_summary_df.rename(columns=header_map, inplace=True)
    print(sprint_summary_df.to_string(index=False))


    from prettytable import PrettyTable

    # Prepare data
    table = PrettyTable()
    # import pdb
    # pdb.set_trace()
    table.field_names = [h.replace("\\n", "\n") for h in sprint_summary_df.columns]
    for row in sprint_summary_df.values:
        table.add_row(row)
    print(table)
    



if __name__ == "__main__": 
    file_name = r"C:\Users\A717631\fits\interval\24-Jul-2025.fit"
    df = load_df_fitparse(file_name)
    print(file_name)

    # Run analysis
    running_power = 350
    interval_sec = 40
    print("When running power is > ", running_power, " and interval is > ", interval_sec, "sec")
    analyze_sprint_intervals(df, power_threshold=running_power, discard_interval_sec=interval_sec)
