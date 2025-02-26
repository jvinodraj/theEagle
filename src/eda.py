"""
EDA(exploratory data analysis)! 
This is visualize trends, check correlations between metrics like heart rate, 
cadence, power, and pace, and get a feel for which features might drive 
performance the most.

 eda.py module with:

1. Time series plots for heart rate, cadence, power, and pace.
2. Correlation heatmaps to see how strongly features relate.
3. Some scatter plots to explore pairwise relationships.
"""


import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

class EDA:
    def __init__(self, data_path):
        self.data = pd.read_csv(data_path, parse_dates=['timestamp'], index_col='timestamp')

    def plot_time_series(self, columns):
        """Plots time series data for given columns."""
        plt.figure(figsize=(10, 6))
        for col in columns:
            if col in self.data.columns:
                plt.plot(self.data.index, self.data[col], label=col)
        plt.legend()
        plt.xlabel('Time')
        plt.ylabel('Value')
        plt.title('Time Series Plot')
        plt.show()

    def plot_correlation_heatmap(self):
        """Plots a heatmap showing correlations between features."""
        plt.figure(figsize=(8, 6))
        corr = self.data.corr()
        sns.heatmap(corr, annot=True, cmap='coolwarm')
        plt.title('Feature Correlation Heatmap')
        plt.show()

    def plot_pairwise_relationships(self, columns):
        """Plots pairwise relationships for given columns."""
        sns.pairplot(self.data[columns])
        plt.show()

# Example usage
if __name__ == "__main__":
    eda = EDA('data/processed/enhanced_fit_data.csv')
    eda.plot_time_series(['heart_rate', 'cadence', 'power', 'pace_min_per_km'])
    eda.plot_correlation_heatmap()
    eda.plot_pairwise_relationships(['heart_rate', 'cadence', 'power', 'pace_min_per_km', 'power_to_weight', 'cadence_to_speed'])
