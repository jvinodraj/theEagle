import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Initial Load Focus Points (Your Current Values)
load_focus = {
    "Anaerobic": 329,
    "High Aerobic": 840,
    "Low Aerobic": 918
}

# Decay rate (Assume daily decay rate, e.g., 0.05 means ~5% per day)
decay_rate = 0.05  # Adjust this based on observations

# Time period (Days)
days = np.arange(0, 30, 1)  # Simulating for 30 days

# Compute decay function for each load category
load_decay = {
    category: values * np.exp(-decay_rate * days)
    for category, values in load_focus.items()
}

df = pd.DataFrame(load_decay)
print(df)
# Plot results
plt.figure(figsize=(10, 5))
for category, values in load_decay.items():
    plt.plot(days, values, label=f"{category} Load")

# print(load_decay)
plt.xlabel("Days")
plt.ylabel("Load Focus Points")
