"""
Model Building!!!
This is simple start and interpret results easily, 
maybe with a linear regression or decision tree, and 
then refine from there.

model.py module with:

1. Feature selection based on our enhanced metrics.
2. Splitting data into training and test sets.
3. Building a baseline model to predict running efficiency (like pace or power-to-weight ratio).
4. Evaluating model performance with metrics like R² and RMSE.
"""
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import joblib

class RunEfficiencyModel:
    def __init__(self, data_path):
        self.data = pd.read_csv(data_path, parse_dates=['timestamp'], index_col='timestamp')
        self.model = LinearRegression()

    def prepare_data(self):
        """Prepares features and target for model training."""
        features = ['heart_rate', 'cadence', 'power', 'power_to_weight', 'cadence_to_speed']
        target = 'pace_min_per_km'
        self.X = self.data[features].dropna()
        self.y = self.data.loc[self.X.index, target]

    def train_model(self):
        """Splits the data, trains the model, and evaluates performance."""
        X_train, X_test, y_train, y_test = train_test_split(self.X, self.y, test_size=0.2, random_state=42)
        self.model.fit(X_train, y_train)
        predictions = self.model.predict(X_test)
        
        # Evaluation
        # rmse = mean_squared_error(y_test, predictions, squared=False)
        rmse = mean_squared_error(y_test, predictions) ** 0.5
        r2 = r2_score(y_test, predictions)

        print(f"Model RMSE: {rmse:.2f}")
        print(f"Model R²: {r2:.2f}")

    def get_feature_importance(self):
        """Prints feature importance based on model coefficients."""
        importance = pd.Series(self.model.coef_, index=self.X.columns)
        print("Feature importance:")
        print(importance.sort_values(ascending=False))

# Example usage
if __name__ == "__main__":
    model = RunEfficiencyModel('data/processed/enhanced_fit_data.csv')
    model.prepare_data()
    model.train_model()
    model.get_feature_importance()

    # Save the trained model
    joblib.dump(model, 'models/running_efficiency_model.pkl')
    print("Model saved successfully!")
