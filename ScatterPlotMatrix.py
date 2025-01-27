import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from fitparse import FitFile

# Load the FIT file
fit_file_path =  r"C:\Users\username\Downloads\18111378159_ACTIVITY.fit"  # Replace with your FIT file path
fit_file = FitFile(fit_file_path)

# User's weight in kilograms
user_weight = 72  # Update this with your weight in kg

# Extract relevant fields
data = []
for record in fit_file.get_messages('record'):
    record_data = {}
    for field in record:
        if field.name in ['enhanced_speed', 'heart_rate', 'cadence', 'stride_length', 'vertical_ratio', 'vertical_oscillation', 'ground_contact_time', 'power']:
            record_data[field.name] = field.value
    if record_data:
        data.append(record_data)

# Convert to DataFrame
df = pd.DataFrame(data)

# Rename columns for clarity
df.rename(columns={
    'enhanced_speed': 'Pace (m/s)',
    'heart_rate': 'Heart Rate (bpm)',
    'cadence': 'Cadence (spm)',
    'stride_length': 'Stride Length (m)',
    'vertical_ratio': 'Vertical Ratio (%)',
    'vertical_oscillation': 'Vertical Oscillation (cm)',
    'ground_contact_time': 'Ground Contact Time (ms)',
    'power': 'Power (W)'
}, inplace=True)

# Convert pace from m/s to min/km
df['Pace (min/km)'] = (1 / df['Pace (m/s)']) * 16.6667  # Conversion formula
df.drop(columns=['Pace (m/s)'], inplace=True)

# Calculate Power-to-Weight Ratio (PWR)
df['PWR (W/kg)'] = df['Power (W)'] / user_weight

# Create a scatter plot matrix
sns.set(style="ticks")
scatter_plot = sns.pairplot(df, diag_kind="kde", plot_kws={'alpha': 0.6})
scatter_plot.fig.suptitle("Scatter Plot Matrix for Run Metrics (Including PWR)", y=1.02)

plt.savefig('plot_image.png')

# Show the plot
plt.show()
