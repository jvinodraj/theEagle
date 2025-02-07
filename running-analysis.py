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

class RunningAnalysis:
    def __init__(self, folder_path, run_type):
        self.folder_path = folder_path
        self.run_type = run_type
        self.fit_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(".fit")]
        self.ist = timezone("Asia/Kolkata")
    
    def _parse_fit_file(self, file_path):
        fitfile = fitparse.FitFile(file_path)
        data = defaultdict(lambda: {"heart_rate": [], "power": []})
        
        for record in fitfile.get_messages("record"):
            fields = {field.name: field.value for field in record}
            if "heart_rate" in fields and fields["heart_rate"] and "power" in fields and fields["power"]:
                timestamp_ist = fields["timestamp"].replace(tzinfo=timezone("UTC")).astimezone(self.ist)
                date_str = timestamp_ist.strftime("%Y-%m-%d")  # Group by date
                
                data[date_str]["heart_rate"].append(fields["heart_rate"])
                data[date_str]["power"].append(fields["power"])
        
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

        self._plot_line_chart(date_ef_map, f"Efficiency Factor ({self.run_type}) Over Time", "Date", "Efficiency Factor", f"efficiency_factor_{self.run_type}.png")

    def _plot_line_chart(self, date_ef_map, title, xlabel, ylabel, filename):
        # Convert dates to datetime objects and sort them
        sorted_dates = sorted(date_ef_map.keys(), key=lambda d: datetime.datetime.strptime(d, "%Y-%m-%d"))
        
        # Extract values in sorted order
        ef_values = [np.mean(date_ef_map[date]) for date in sorted_dates]  # Mean EF for each date
        ef_min = [np.min(date_ef_map[date]) for date in sorted_dates]  # Min EF
        ef_max = [np.max(date_ef_map[date]) for date in sorted_dates]  # Max EF

        plt.figure(figsize=(10, 6))
        plt.plot(sorted_dates, ef_values, marker="o", linestyle="-", color="b", label="Avg Efficiency Factor")
        plt.fill_between(sorted_dates, ef_min, ef_max, color="blue", alpha=0.2, label="Min-Max Range")
        plt.xticks(rotation=45)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.legend()
        plt.grid(True)
        plt.savefig(os.path.join(save_chart_folder, filename))
        plt.show()
        plt.close()

# Example usage
easy_run_analysis = RunningAnalysis(easy_run_folder, "Easy Runs")
easy_run_analysis.efficiency_factor_chart()
