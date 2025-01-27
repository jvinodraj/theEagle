import fitparse
import pandas as pd
import matplotlib.pyplot as plt

# Path to the .fit file
fit_file_path = r"C:\Users\username\Downloads\fit_files\18076803329_ACTIVITY.fit"

# Parse the .fit file
fitfile = fitparse.FitFile(fit_file_path)

# Extract heart rate and power data
heart_rates = []
powers = []

for record in fitfile.get_messages("record"):
    record_data = {data.name: data.value for data in record}
    if "heart_rate" in record_data and "power" in record_data:
        heart_rates.append(record_data["heart_rate"])
        powers.append(record_data["power"])

# Create a pandas DataFrame
df = pd.DataFrame({
    "Heart Rate (bpm)": heart_rates,
    "Power (W)": powers
})

# Plot the data
plt.figure(figsize=(10, 6))
plt.scatter(df["Heart Rate (bpm)"], df["Power (W)"], color="green", alpha=0.7, label="HR vs Power")
plt.title("Heart Rate vs Power", fontsize=16)
plt.xlabel("Heart Rate (bpm)", fontsize=14)
plt.ylabel("Power (W)", fontsize=14)
plt.grid(True, linestyle="--", alpha=0.6)
plt.legend()
plt.show()
