import os
import fitparse
import numpy as np
import matplotlib.pyplot as plt
import datetime
from collections import defaultdict
from pytz import timezone

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

class RunningAnalysis:
    def __init__(self, folder_path, run_type):
        self.folder_path = folder_path
        self.run_type = run_type
        self.fit_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(".fit")]
        self.ist = timezone("Asia/Kolkata")
    
    def _parse_fit_file(self, file_path):
        fitfile = fitparse.FitFile(file_path)
        data = defaultdict(lambda: {"heart_rate": [], "power": [], "pace": []})
        
        for record in fitfile.get_messages("record"):
            fields = {field.name: field.value for field in record}
            if "heart_rate" in fields and fields["heart_rate"] and "power" in fields and fields["power"] and "enhanced_speed" in fields and fields["enhanced_speed"] > 0:
                timestamp_ist = fields["timestamp"].replace(tzinfo=timezone("UTC")).astimezone(self.ist)
                date_str = timestamp_ist.strftime("%Y-%m-%d")  # Group by date
                
                data[date_str]["heart_rate"].append(fields["heart_rate"])
                data[date_str]["power"].append(fields["power"])
                data[date_str]["pace"].append(fields["enhanced_speed"])  # Speed in m/s

        return data
    
    def efficiency_factor_chart(self):
        date_ef_map = {}

        for file in self.fit_files:
            data = self._parse_fit_file(file)
            for date, values in data.items():
                if values["heart_rate"] and values["power"]:
                    avg_hr = np.mean(values["heart_rate"])
                    avg_power = np.mean(values["power"])
                    ef = avg_power / avg_hr if avg_hr > 0 else None
                    
                    if ef:
                        if date not in date_ef_map:
                            date_ef_map[date] = []
                        date_ef_map[date].append(ef)

        self._plot_line_chart(date_ef_map, f"{self.run_type} - Efficiency Factor Over Time", "Date", "Efficiency Factor", f"efficiency_factor_{self.run_type}.png")

    def running_economy_chart(self):
        date_re_map = {}

        for file in self.fit_files:
            data = self._parse_fit_file(file)
            for date, values in data.items():
                if values["power"] and values["pace"]:
                    power_array = np.array(values["power"])
                    pace_array = np.array(values["pace"])
                    
                    # Running Economy: Power / Pace (W per m/s)
                    re_values = power_array / pace_array  # Element-wise division
                    
                    if date not in date_re_map:
                        date_re_map[date] = []
                    date_re_map[date].extend(re_values.tolist())

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
    
        # Legend 1: Interpreting Trends
        trend_text = "✔ Increasing EF → Improved aerobic efficiency.\n ❌ Decreasing EF → Overtraining, fatigue, or inefficiency."
        plt.text(1.02, 0.7, trend_text, fontsize=10, color="black", transform=plt.gca().transAxes, bbox=dict(facecolor="white", edgecolor="black", boxstyle="round,pad=0.5"))
    
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
    
        table.auto_set_font_size(False)
        table.set_fontsize(10)
    
        # Save and show the plot
        plt.savefig(os.path.join(save_chart_folder, filename), bbox_inches="tight")
        plt.show()
        plt.close()


    def _plot_box_chart(self, date_re_map, title, xlabel, ylabel, filename):
        sorted_dates = sorted(date_re_map.keys(), key=lambda d: datetime.datetime.strptime(d, "%Y-%m-%d"))
        re_values = [date_re_map[date] for date in sorted_dates]  # List of lists for boxplot

        plt.figure(figsize=(15, 7))


        # Legend 1: Interpreting Trends
        trend_text = """
        ☆ Lower RE: More efficient running (less power used for given speed). 
        ☆ Higher RE: Less efficient running (more power needed).
        ☆ Tight Boxplot: Consistent efficiency across a day.
        ☆ Wider Boxplot: Large variability in efficiency across a day.
        """
        plt.text(1.02, 0.7, trend_text, fontsize=10, color="black", transform=plt.gca().transAxes, bbox=dict(facecolor="white", edgecolor="black", boxstyle="round,pad=0.5"))
    
        # Legend 2: Benchmark Values as Table
        benchmark_values = [
            ["Adaptation", "200+"],
            ["Development", "150 - 200"],
            ["Performance", "100 - 150"],
            ["Peak Efficiency", "< 100"],
        ]
    
        table = plt.table(cellText=benchmark_values,
                          colLabels=["Runner Phase", "RE (W·min/km)"],
                          cellLoc="center",
                          loc="right",
                          bbox=[1.02, 0.3, 0.3, 0.3])  # Positioning the table outside the plot
    
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        
        # plt.boxplot(re_values, labels=sorted_dates, vert=True, patch_artist=True)
        plt.boxplot(re_values, tick_labels=sorted_dates, vert=True, patch_artist=True)
        plt.xticks(rotation=45)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.grid(True)
        plt.savefig(os.path.join(save_chart_folder, filename))
        plt.show()
        # plt.close()

# Example usage
easy_run_analysis = RunningAnalysis(easy_run_folder, "Easy Runs")
# easy_run_analysis.efficiency_factor_chart()
easy_run_analysis.running_economy_chart()
