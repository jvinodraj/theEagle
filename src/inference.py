import joblib
import pandas as pd
from feature_engineering import FeatureEngineer
import pdb

class InferencePipeline:
    def __init__(self, model_path='models/running_efficiency_model.pkl'):
        pdb.set_trace()
        self.model = joblib.load(model_path)
        self.feature_engineering = FeatureEngineer()

    def predict(self, raw_data):
        # Apply feature engineering
        processed_data = self.feature_engineering.transform(raw_data)

        # Make predictions
        predictions = self.model.predict(processed_data)
        return predictions

if __name__ == "__main__":
    # Example input data (replace with real new data)
    new_data = pd.DataFrame({
        'heart_rate': [150],
        'cadence': [160],
        'power': [300],
        'power_to_weight': [4.2],
        'cadence_to_speed': [1.8]
    })

    pipeline = InferencePipeline()
    prediction = pipeline.predict(new_data)
    print("Predicted Efficiency:", prediction)
