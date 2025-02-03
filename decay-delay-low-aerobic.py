import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Set Pandas display options
pd.set_option("display.max_columns", None)  # Show all columns
pd.set_option("display.expand_frame_repr", False)  # Prevent column wrapping
pd.set_option("display.width", 1000)  # Set a wider display width

# Decay rate (Assume daily decay rate, e.g., 0.05 means ~5% per day)
decay_rates = {
    "Low Aerobic 2%": 0.02,
    "Low Aerobic 2.45%": 0.0245,
    "Low Aerobic 2.5%": 0.025,
    "Low Aerobic 3%": 0.03,
}

# Initial Load Focus Points (Your Current Values)
load_focus = 918

# Time period (Days)
days = np.arange(0, 30, 1)  # Simulating for 30 days

# Compute decay function for each load category
# load_decay = {
#     category: values * np.exp(-decay_rate * days)
#     for category, values in load_focus.items()
# }

load_decay = {
    category: load_focus * np.exp(-decay_rate * days)
    for category, decay_rate in decay_rates.items()
}

df = pd.DataFrame(load_decay)

# Generate dates for Feb 1 to Feb 29
dates = pd.date_range(start="2024-02-01", end="2024-03-01")

# insert dates column at the first location
df.insert(0, "Dates", dates)

print(df)
