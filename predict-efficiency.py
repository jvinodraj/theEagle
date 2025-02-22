import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

# Load running data
data = {
    "heart_rate": [120, 121, 122, 129, 130, 131, 135, 135, 135],
    "cadence": [164, 164, 166, 168, 170, 170, 160, 160, 160],
    "power": [206, 216, 203, 228, 228, 226, 233, 233, 233],
    "pace": [8.29, 8.36, 8.39, 7.57, 7.57, 7.59, 7.63, 7.63, 7.63],
}

df = pd.DataFrame(data)

# Efficiency Score: (Pace * Power) / (HR * Cadence)
df["efficiency_score"] = (df["pace"] * df["power"]) / (df["heart_rate"] * df["cadence"])

# Features and target
X = df[["heart_rate", "cadence", "power", "pace"]]
y = df["efficiency_score"]

# Scale Features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# Train Random Forest
model = RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42)
model.fit(X_train, y_train)

# Predictions
y_pred = model.predict(X_test)

# Evaluate
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"Improved Model Performance:\nMSE: {mse:.5f}\nR² Score: {r2:.5f}")

# Predict efficiency for a new run
new_run = np.array([[125, 165, 220, 7.8]])
new_run_scaled = scaler.transform(new_run)  # Scale input
predicted_efficiency = model.predict(new_run_scaled)
print(f"Predicted Efficiency Score: {predicted_efficiency[0]:.5f}")
