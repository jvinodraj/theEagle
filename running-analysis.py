import os
import fitparse
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
from collections import defaultdict
from pytz import timezone
import pandas as pd
import sys, pdb

sys.displayhook = print  # Ensures all statements are printed

# General variables for folders
aerobic_run_folder = "aerobic_runs/"
easy_run_folder = "easy_runs/"
save_chart_folder = "charts/"
os.makedirs(save_chart_folder, exist_ok=True)

# Change the font to one that supports more characters (like 'Arial')
# plt.rcParams["font.family"] = "Arial"
# plt.rcParams["font.family"] = "Arial Unicode MS"
# Reset to default font settings
plt.rcParams["font.family"] = plt.rcParamsDefault["font.family"]
# Normalize RE to W/kg using weight (assuming 72 kg)
weight_kg = 72  # Adjust based on your weight

class RunningAnalysis:
    def __init__(self, folder_path, run_type):
        self.folder_path = folder_path
        self.run_type = run_type
        self.fit_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(".fit")]
        self.ist = timezone("Asia/Kolkata")

    def _fit_parse_file(self, file_name):
        try:
            # print("Parsing the fit file :", file_name)
            fitfile = fitparse.FitFile(file_name)
        except:
            print("Error at parsing fit file")

        # print(fitfile)
        # return 0

        data = []
        for record in fitfile.get_messages("record"):
            record_data = {}
            for field in record.fields:
                record_data[field.name] = field.value
            data.append(record_data)

        df = pd.DataFrame(data) if data else pd.DataFrame()
        return df

    def getDF(self):
        for file in self.fit_files:
            df = self._fit_parse_file(file)
        return df
            

    def efficiency_factor_chart(self):

        # Legend 1: Interpreting Trends
        trend_text = "✔ Increasing EF → Improved aerobic efficiency.\n X Decreasing EF → Overtraining, fatigue, or inefficiency."
    
        # Legend 2: Benchmark Values as Table
        benchmark_header = ["Runner Type", "EF (W/bpm)"]
        benchmark_values = [
            ["Adaptation", "0.8 - 1.2"],
            ["Development", "1.2 - 1.6"],
            ["Performance", "1.6 - 2.0"],
            ["Peak Efficiency", "2.0+"],
        ]
        
        date_ef_map = {}

        for file in self.fit_files:
            df = self._fit_parse_file(file)
            df["timezone_ist"] = df["timestamp"].dt.tz_localize("UTC").dt.tz_convert(self.ist)
            
            date = df["timezone_ist"][0].strftime("%Y-%m-%d")
            print("Preparing Eff. Factor for the date : ", date)

            df        = df[df['power'] > 0]
            avg_hr    = np.mean(df["heart_rate"])
            avg_power = np.mean(df["power"])
            ef        = avg_power / avg_hr if avg_hr > 0 else None
            
            if ef:
                if date not in date_ef_map:
                    date_ef_map[date] = []
                date_ef_map[date].append(ef)

        self._plot_line_chart(date_ef_map, f"{self.run_type} - Efficiency Factor Over Time", "Date", "Efficiency Factor", 
                              trend_text, benchmark_values, benchmark_header,
                              f"efficiency_factor_{self.run_type}.png")
        
        return

    def running_economy_chart(self):
        date_re_map = {}

        # 📌 Legend 1: Interpreting Trends
        trend_text = "✔ Lower RE → More efficient running.\n✖ Higher RE →  inefficient running (wasting energy)."
    
        # 📌 Legend 2: Benchmark Values as Table
        benchmark_values = [
            ["Elite", "≤ 0.9 W/kg"],
            ["Efficient", "0.9 - 1.1 W/kg"],
            ["Average", "1.1 - 1.3 W/kg"],
            ["Inefficient", "≥ 1.3 W/kg"]
        ]

        for file in self.fit_files:
            
            df                 = self._fit_parse_file(file)
            df["timezone_ist"] = df["timestamp"].dt.tz_localize("UTC").dt.tz_convert(self.ist)
            date               = df["timezone_ist"][0].strftime("%Y-%m-%d")
            df                 = df[df['power'] > 0]

            print("Preparing Running Economy for the date : ", date)

            sel_cols = ['timezone_ist', 'enhanced_speed', 'power']
            # print (df[sel_cols])

            # Compute Running Economy (W/m/s)
            df["running_economy"] = df["power"] / df["enhanced_speed"]

            # Normalize RE to W/kg using weight (assuming 72 kg)
            # weight_kg = 72  # Adjust based on your weight
            df["running_economy_wkg"] = df["running_economy"] / weight_kg

            # pdb.set_trace()
    
            if date not in date_re_map:
                date_re_map[date] = []
            date_re_map[date].extend(df["running_economy_wkg"])

        self._plot_box_chart(date_re_map, f"{self.run_type} - Running Economy Over Time", "Date", "Running Economy", trend_text, benchmark_values, f"running_economy_{self.run_type}.png")

    def running_hr_drift_index(self):

        # Legend 1: Interpreting Trends
        trend_text = """
✔ Lower HRDI → Stable endurance.

✖ High HRDI → Dehydration, overexertion, poor pacing.
"""
    
        # Legend 2: Benchmark Values as Table
        benchmark_header = ["HR Drift (%)", "Interpretation", "Possible Causes & Actions"]
        benchmark_values = [
            ["0% – 3%",  "Minimal Drift",   "Excellent Efficiency"],
            ["3% – 6%",  "Moderate drift",  "Normal Aerobic Response"],
            ["6% – 10%", "Hight HR Drift",  "Fatigue or dehydration"],
            ["> 10%",    "Severe HR Drift", "Inefficient or Overtraining"]
        ]
        
        date_hrdi_map = {}

        for file in self.fit_files:
            df                 = self._fit_parse_file(file)
            df["timezone_ist"] = df["timestamp"].dt.tz_localize("UTC").dt.tz_convert(self.ist)
            date               = df["timezone_ist"][0].strftime("%Y-%m-%d")
            df                 = df[df['power'] > 0]

            print("Preparing HRDI for the date : ", date)
        

            # Split dataset into two halves
            half_index = len(df) // 2
            first_half = df.iloc[:half_index]
            last_half  = df.iloc[half_index:]
            
            # Calculate HR Drift Index
            avg_hr_first_half = first_half["heart_rate"].mean()
            avg_hr_last_half  = last_half["heart_rate"].mean()
            hr_drift_index    = ((avg_hr_last_half - avg_hr_first_half) / avg_hr_first_half) * 100
            
            print(f"HR Drift Index: {hr_drift_index:.2f}%")

            if date not in date_hrdi_map:
                date_hrdi_map[date] = []
            # pdb.set_trace()
            date_hrdi_map[date].append(hr_drift_index)

        print (date_hrdi_map)

        self._plot_line_chart(date_hrdi_map, f"{self.run_type} - Heart Rate Drift Index Over Time", "Date", "HRDI", 
                              trend_text, benchmark_values, benchmark_header, 
                              f"hr_drift_index_{self.run_type}.png")

    # Compute 1-minute rolling averages
    def compute_rolling_averages(self, df, window=60):
        df["cadence"] *= 2
        # pdb.set_trace()
        # df["enhanced_speed"] = 1000 / df["enhanced_speed"] / 60
        rolling_cols = ['enhanced_speed', 'heart_rate', 'power', 'cadence', 'step_length']
        for col in rolling_cols:
            df[f'{col}_rolling'] = df[col].rolling(window, min_periods=1).mean()
        return df


    # Identify conditions where higher pace is achieved with lower heart rate at a given power
    def analyze_efficiency(self, df):
        # pdb.set_trace()
        # df['pace'] = 1 / df['enhanced_speed_rolling']  # Convert speed to pace (min/km-like metric)
        df['pace'] = 1000 / df['enhanced_speed_rolling'] / 60 # Convert speed to pace (min/km-like metric)
        df['efficiency'] = df['heart_rate_rolling'] / df['power_rolling']  # Lower is better
        pdb.set_trace()

        #Find the Efficient pace
        # filtered_df = df[(df['power'] >= 210) & (df['power'] <= 250) & (df['heart_rate'] > 130)]  # Filter power range
        # min_index = filtered_df['efficiency'].idxmin()  # Find index with lowest efficiency
        # rec  = df.loc[min_index, ['heart_rate', 'cadence', 'power', 'step_length', 'pace', 'vertical_ratio']]
        # print(df.loc[min_index, ['heart_rate', 'cadence', 'power']])  # Print selected columns

        # Step 1: Compute HR/Power ratio
        # df['hr_power_ratio'] = df['heart_rate'] / df['power']

        # Step 2: Filter data where Power is between 210 and 250
        
        print(['heart_rate', 'cadence', 'power', 'pace'])
        for i in range(120, 136):
            filtered_df = df[(df['power'] >= 200) & (df['power'] <= 250) & (df['heart_rate'] >= i)]

            # Step 3: Find the row with the minimum HR/Power ratio
            efficient_record = filtered_df.loc[filtered_df['efficiency'].idxmin(), ['heart_rate', 'cadence', 'power', 'pace']]

            # Display the most efficient record
            # print(efficient_record)
            print(*efficient_record.values)

        
        return df

    def get_dates(self, n):

        today = dt.datetime.today()

        if n == 0:
            return today.strftime("%d-%b-%Y")
        
        date_list = [(today - dt.timedelta(days=i)).strftime("%d-%b-%Y") for i in range(abs(n))]
        return date_list

    def pace_hr_power_chart(self, n_dates=-30):

        # pace_hr_power_map = {}

        date_list = self.get_dates(n_dates)

        for file in self.fit_files:

            # pdb.set_trace()
            if n_dates == 0:
                if date_list in file:
                    print("Processing the run : ", file)
                else:
                    print("Skipping the file : ", file)
                    continue
            else: 
                # Extract the date part from the file
                file_date = file.split('/')[-1].replace('.fit', '')

                # Check if the date is in date_list
                if file_date in date_list:
                    print("Processing the run : ", file)
                else:
                    print("Skipping the file : ", file)
                    continue

            df                 = self._fit_parse_file(file)
            df["timezone_ist"] = df["timestamp"].dt.tz_localize("UTC").dt.tz_convert(self.ist)
            date               = df["timezone_ist"][0].strftime("%Y-%m-%d")
            df                 = df[df['power'] > 0]

            print("Preparing pace by hr by power for the date : ", date)

            df = self.compute_rolling_averages(df)
            df = self.analyze_efficiency(df)
            # self._plot_3d(df)
            self._plot_3dBar(df)


    def _plot_line_chart(self, date_ef_map, title, xlabel, ylabel, interpretation, benchmark, benchmark_header, filename):
        sorted_dates = sorted(date_ef_map.keys(), key=lambda d: datetime.datetime.strptime(d, "%Y-%m-%d"))
        ef_values = [np.mean(date_ef_map[date]) for date in sorted_dates]  # Mean EF for each date
        ef_min = [np.min(date_ef_map[date]) for date in sorted_dates]
        ef_max = [np.max(date_ef_map[date]) for date in sorted_dates]
    
        plt.figure(figsize=(10, 9))
        
        # Plot EF values and shaded region for min-max range
        plt.plot(sorted_dates, ef_values, marker="o", linestyle="-", color="b", label="Avg Efficiency Factor")
        plt.fill_between(sorted_dates, ef_min, ef_max, color="blue", alpha=0.2, label="Min-Max Range")
    
        # Add grid and labels
        plt.xticks(rotation=45)
        plt.title(title, fontsize=14, fontweight="bold")
        plt.xlabel(xlabel, fontsize=12)
        plt.ylabel(ylabel, fontsize=12)
        plt.legend()
        plt.grid(True, linestyle="--", alpha=0.6)

        # Adjust layout to make space for the table
        # plt.subplots_adjust(bottom=0.25)  # Reserve space below for the table
    
        # Legend 1: Interpreting Trends
        trend_text = interpretation
        plt.text(1.02, 0.7, trend_text, fontsize=10, color="black", transform=plt.gca().transAxes, 
                 bbox=dict(facecolor="white", edgecolor="black", boxstyle="round,pad=0.5"))
                 # bbox=dict(facecolor="white", edgecolor="black", boxstyle="round,pad=0.5"), ha="center")

    
        # Legend 2: Benchmark Values as Table
        benchmark_values = benchmark
    
        table = plt.table(cellText=benchmark_values,
                          colLabels=benchmark_header,
                          cellLoc="center",
                          loc="right",
                          bbox=[1.02, 0.3, 0.75, 0.3])  # Positioning the table outside the plot
                           # bbox=[0.15, -0.6, 0.7, 0.2])  # Adjusted bbox to position the table below
    
        table.auto_set_font_size(False)
        table.set_fontsize(10)

        # # Add formula as a text box below the chart
        # formula_text = r"$HRDI = \left( \frac{HR_{2nd} - HR_{1st}}{HR_{1st}} \right) \times 100$"
        # plt.text(0.5, -15, formula_text, fontsize=12, ha="center", transform=plt.gca().transAxes, bbox=dict(facecolor="white", alpha=0.5))

    
        # Save and show the plot
        plt.savefig(os.path.join(save_chart_folder, filename), bbox_inches="tight")
        plt.show()
        plt.close()


    def _plot_box_chart(self, date_re_map, title, xlabel, ylabel, interpretation, benchmark, filename):
        sorted_dates = sorted(date_re_map.keys(), key=lambda d: datetime.datetime.strptime(d, "%Y-%m-%d"))
        re_values = [date_re_map[date] for date in sorted_dates]  # List of lists for boxplot

        plt.figure(figsize=(10, 9))
        # plt.boxplot(re_values, labels=sorted_dates, vert=True, patch_artist=True)
        plt.boxplot(re_values, tick_labels=sorted_dates, vert=True, patch_artist=True)
        plt.xticks(rotation=45)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.grid(True)

        # 📌 Legend 1: Interpreting Trends
        trend_text = interpretation
        plt.text(1.02, 0.7, trend_text, fontsize=10, color="black", transform=plt.gca().transAxes, 
                 bbox=dict(facecolor="white", edgecolor="black", boxstyle="round,pad=0.5"))
    
        # 📌 Legend 2: Benchmark Values as Table
        benchmark_values = benchmark
    
        table = plt.table(cellText=benchmark_values,
                          colLabels=["Runner Category", "Running Economy"],
                          cellLoc="center",
                          loc="right",
                          bbox=[1.02, 0.3, 0.5, 0.3])  # Adjust position
    
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        
        plt.savefig(os.path.join(save_chart_folder, filename), bbox_inches="tight")
        plt.show()
        plt.close()

    # Visualization using 3D Scatter Plot
    def _plot_3d(self, df):
        fig = plt.figure(figsize=(10, 7))
        ax = fig.add_subplot(111, projection='3d')

        # Sort data: Pace (High → Low), Heart Rate (Low → High)
        df = df.sort_values(by=["pace", "heart_rate_rolling"], ascending=[True, True])
        
        scatter = ax.scatter(df['power_rolling'], df['pace'], df['heart_rate_rolling'], c=df['cadence_rolling'], cmap='coolwarm', alpha=0.8)
        
        ax.set_xlabel('Power (Watts)')
        ax.set_ylabel('Pace (min/km)')
        ax.set_zlabel('Heart Rate (bpm)')
        cbar = plt.colorbar(scatter, ax=ax, shrink=0.5)
        cbar.set_label('Cadence (spm)')
        plt.title('Efficiency Analysis: Pace vs HR at Given Power')
        plt.show()


#     import matplotlib.pyplot as plt
# import numpy as np
# from mpl_toolkits.mplot3d import Axes3D

    def _plot_3dBar(self, df):
        # Sort data: Pace (High → Low), Heart Rate (Low → High)
        df = df.sort_values(by=["pace", "heart_rate_rolling"], ascending=[False, True])

        # Create figure and 3D axis
        fig = plt.figure(figsize=(10, 7))
        ax = fig.add_subplot(111, projection='3d')

        # Define x, y, z coordinates
        x = df["power_rolling"].values
        y = df["pace"].values
        z = np.zeros(len(df))  # Bars start at z = 0

        # Define bar width and depth
        dx = np.full_like(x, 5)   # Width of bars (adjustable)
        dy = np.full_like(y, 0.1)  # Depth of bars (adjustable)
        dz = df["heart_rate_rolling"].values  # Bar height (HR values)

        # Color mapping based on cadence
        colors = plt.cm.coolwarm(df["cadence_rolling"] / df["cadence_rolling"].max())

        # Plot 3D bars
        ax.bar3d(x, y, z, dx, dy, dz, color=colors, alpha=0.8)

        # Labels and title
        ax.set_xlabel("Power (Watts)")
        ax.set_ylabel("Pace (min/km)")
        ax.set_zlabel("Heart Rate (bpm)")
        plt.title("Efficiency Analysis: Pace vs HR at Given Power (Bar3D)")

        # Show plot
        plt.show()


# Easy Runs
run_analysis = RunningAnalysis(easy_run_folder, "Easy Runs")
# run_analysis.efficiency_factor_chart()
# run_analysis.running_economy_chart()
# run_analysis.running_hr_drift_index()
run_analysis.pace_hr_power_chart(n_dates=2)

#Aerobic Runs
# run_analysis = RunningAnalysis(aerobic_run_folder, "Aerobic Runs")
# run_analysis.efficiency_factor_chart()
# run_analysis.running_economy_chart()
# run_analysis.running_hr_drift_index()
