import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Initial Load Focus Points (Intensity type range, decay_rate)
load_focus = {
    "Anaerobic"    : [329, .022],
    "High Aerobic" : [840, .106],
    "Low Aerobic"  : [918, .0245]
}

# Time period (Days)
days = np.arange(0, 30, 1)  # Simulating for 30 days

#populating dates
dates = pd.date_range(start="2024-02-01", end="2024-03-01")

# Compute decay function for each load category
load_decay = {
    category: points * np.exp(-decay_rate * days)
    for category, [points, decay_rate] in load_focus.items()
}

df = pd.DataFrame(load_decay)
df.insert(0, "Dates", dates)
print(df)
# Plot results
plt.figure(figsize=(10, 5))
for category, values in load_decay.items():
    plt.plot(days, values, label=f"{category} Load")

# print(load_decay)
plt.xlabel("Days")
plt.ylabel("Load Focus Points")
plt.legend()
# Save the figure
plt.savefig("load_decay_plot.png", dpi=300, bbox_inches="tight")  # Saves with high resolution
plt.show()
