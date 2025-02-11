import os
import fitparse
import numpy as np
import matplotlib.pyplot as plt
import datetime
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
            

    def efficiency_factor_chart(self):
        date_ef_map = {}

        for file in self.fit_files:
            df = self._fit_parse_file(file)
            df["timezone_ist"] = df["timestamp"].dt.tz_localize("UTC").dt.tz_convert(self.ist)
            
            date = df["timezone_ist"][0].strftime("%Y-%m-%d")

            df        = df[df['power'] > 0]
            avg_hr    = np.mean(df["heart_rate"])
            avg_power = np.mean(df["power"])
            ef        = avg_power / avg_hr if avg_hr > 0 else None
            
            if ef:
                if date not in date_ef_map:
                    date_ef_map[date] = []
                date_ef_map[date].append(ef)

        self._plot_line_chart(date_ef_map, f"{self.run_type} - Efficiency Factor Over Time", "Date", "Efficiency Factor", f"efficiency_factor_{self.run_type}.png")
        
        return

    def running_economy_chart(self):
        date_re_map = {}

        for file in self.fit_files:
            df                 = self._fit_parse_file(file)
            df["timezone_ist"] = df["timestamp"].dt.tz_localize("UTC").dt.tz_convert(self.ist)
            date               = df["timezone_ist"][0].strftime("%Y-%m-%d")
            # pdb.set_trace()
            df                 = df[df['power'] > 0]

            sel_cols = ['timezone_ist', 'enhanced_speed', 'power']
            print (df[sel_cols])

            # Compute Running Economy (W/m/s)
            df["running_economy"] = df["power"] / df["enhanced_speed"]

            # Normalize RE to W/kg using weight (assuming 72 kg)
            # weight_kg = 72  # Adjust based on your weight
            df["running_economy_wkg"] = df["running_economy"] / weight_kg

            # pdb.set_trace()
    
            if date not in date_re_map:
                date_re_map[date] = []
            date_re_map[date].extend(df["running_economy_wkg"])

        self._plot_box_chart(date_re_map, f"{self.run_type} - Running Economy Over Time", "Date", "Running Economy", f"running_economy_{self.run_type}.png")


    def _plot_line_chart(self, date_ef_map, title, xlabel, ylabel, filename):
        sorted_dates = sorted(date_ef_map.keys(), key=lambda d: datetime.datetime.strptime(d, "%Y-%m-%d"))
        ef_values = [np.mean(date_ef_map[date]) for date in sorted_dates]  # Mean EF for each date
        ef_min = [np.min(date_ef_map[date]) for date in sorted_dates]
        ef_max = [np.max(date_ef_map[date]) for date in sorted_dates]
    
        plt.figure(figsize=(12, 7))
        
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
        trend_text = "✔ Increasing EF → Improved aerobic efficiency.\n X Decreasing EF → Overtraining, fatigue, or inefficiency."
        plt.text(1.02, 0.7, trend_text, fontsize=10, color="black", transform=plt.gca().transAxes, 
                 bbox=dict(facecolor="white", edgecolor="black", boxstyle="round,pad=0.5"))
                 # bbox=dict(facecolor="white", edgecolor="black", boxstyle="round,pad=0.5"), ha="center")

    
        # Legend 2: Benchmark Values as Table
        benchmark_values = [
            ["Adaptation", "0.8 - 1.2"],
            ["Development", "1.2 - 1.6"],
            ["Performance", "1.6 - 2.0"],
            ["Peak Efficiency", "2.0+"],
        ]
    
        table = plt.table(cellText=benchmark_values,
                          colLabels=["Runner Phase", "EF (W/bpm)"],
                          cellLoc="center",
                          loc="right",
                          bbox=[1.02, 0.3, 0.3, 0.3])  # Positioning the table outside the plot
                           # bbox=[0.15, -0.6, 0.7, 0.2])  # Adjusted bbox to position the table below
    
        table.auto_set_font_size(False)
        table.set_fontsize(10)
    
        # Save and show the plot
        plt.savefig(os.path.join(save_chart_folder, filename), bbox_inches="tight")
        plt.show()
        plt.close()


    def _plot_box_chart(self, date_re_map, title, xlabel, ylabel, filename):
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
        trend_text = "✔ Lower RE → More efficient running.\n✖ Higher RE →  inefficient running (wasting energy)."
        plt.text(1.02, 0.7, trend_text, fontsize=10, color="black", transform=plt.gca().transAxes, 
                 bbox=dict(facecolor="white", edgecolor="black", boxstyle="round,pad=0.5"))
    
        # 📌 Legend 2: Benchmark Values as Table
        benchmark_values = [
            ["Elite", "≤ 0.9 W/kg"],
            ["Efficient", "0.9 - 1.1 W/kg"],
            ["Average", "1.1 - 1.3 W/kg"],
            ["Inefficient", "≥ 1.3 W/kg"]
        ]
    
        table = plt.table(cellText=benchmark_values,
                          colLabels=["Runner Category", "Running Economy"],
                          cellLoc="center",
                          loc="right",
                          bbox=[1.02, 0.3, 0.4, 0.3])  # Adjust position
    
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        
        plt.savefig(os.path.join(save_chart_folder, filename), bbox_inches="tight")
        plt.show()
        # plt.close()
        
# run_analysis = RunningAnalysis(easy_run_folder, "Easy Runs")
# run_analysis.efficiency_factor_chart()
# easy_run_analysis.running_economy_chart()
run_analysis = RunningAnalysis(aerobic_run_folder, "Aerobic Runs")
# run_analysis.efficiency_factor_chart()
run_analysis.running_economy_chart()
