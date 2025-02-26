"""
This is feature engineering! This is to transform and prepare the data so we 
can start analyzing which metrics (like heart rate, cadence, power, etc.) are 
most efficient for your running performance.

This is to create a new feature_engineering.py module inside src/, and this will:

1. Add new features like pace, power-to-weight ratio, and cadence-to-speed ratio.
2. Normalize or scale data if needed for consistency.
3. Handle any missing or outlier values.

"""
import pandas as pd
import pdb

class FeatureEngineer:
    def __init__(self, data_path):
        self.data_path = data_path
        self.data = pd.read_csv(data_path, parse_dates=['timestamp'], index_col='timestamp')

    def add_features(self):
        """Adds new calculated features."""
        # Pace (min/km) - converting speed (m/s) to min/km
        if 'speed' in self.data.columns:
            self.data['pace_min_per_km'] = 1000 / (self.data['speed'] * 60)

        # Power-to-weight ratio (W/kg)
        if 'power' in self.data.columns:
            weight_kg = 72  # Vinod's weight
            self.data['power_to_weight'] = self.data['power'] / weight_kg

        # Cadence-to-speed ratio
        if 'cadence' in self.data.columns and 'speed' in self.data.columns:
            self.data['cadence_to_speed'] = self.data['cadence'] / self.data['speed']

    def handle_missing_values(self):
        """Fills missing values by interpolation."""
        self.data.interpolate(method='time', inplace=True)

    def save_transformed_data(self, output_path):
        """Saves the enhanced dataset to a CSV."""
        # pdb.set_trace()
        self.data.to_csv(output_path)
        print(f"Enhanced data saved to {output_path}")

# Example usage
if __name__ == "__main__":
    engineer = FeatureEngineer('data/processed/cleaned_fit_data.csv')
    engineer.add_features()
    engineer.handle_missing_values()
    engineer.save_transformed_data('data/processed/enhanced_fit_data.csv')
