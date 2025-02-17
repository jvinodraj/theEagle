import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import fitparse

def load_df_fitparse(file_name):
    recs  = fitparse.FitFile(file_name)
    data = []
    for record in recs.get_messages("record"):
        data_dict = {field.name: field.value for field in record}
        # print(data_dict)
        data.append(data_dict)
        # print(data)
    return pd.DataFrame(data)

# Load Data (Assuming 'df' is the given pandas DataFrame with a timestamp index)
def preprocess_data(df):
    df = df.copy()
    
    # Convert speed to pace (minutes per km)
    df['pace'] = 1 / df['enhanced_speed'] * 1000 / 60
    
    # Compute rolling averages
    for col in ['cadence', 'enhanced_altitude', 'enhanced_speed', 'heart_rate', 'vertical_oscillation', 'vertical_ratio', 'power', 'pace']:
        df[f'{col}_5min'] = df[col].rolling(window=5, min_periods=1).mean()
        df[f'{col}_10min'] = df[col].rolling(window=10, min_periods=1).mean()
        df[f'{col}_15min'] = df[col].rolling(window=15, min_periods=1).mean()
    
    return df

# Identify conditions where higher pace is achieved with lower heart rate at a given power level
def analyze_pace_efficiency(df, power_level):
    df_filtered = df[df['power'] == power_level]
    df_filtered = df_filtered.sort_values(by='pace')
    
    return df_filtered[['pace', 'heart_rate', 'cadence', 'vertical_ratio', 'power']]

# Correlation analysis
def correlation_analysis(df):
    correlation_matrix = df[['pace', 'cadence', 'vertical_ratio', 'heart_rate', 'power']].corr()
    plt.figure(figsize=(8, 6))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f')
    plt.title('Correlation Between Metrics')
    plt.show()

# Visualization of trends
def plot_trends(df):
    plt.figure(figsize=(10, 5))
    sns.lineplot(data=df, x=df.index, y='pace', label='Pace', color='blue')
    sns.lineplot(data=df, x=df.index, y='heart_rate', label='Heart Rate', color='red')
    plt.xlabel('Time')
    plt.ylabel('Values')
    plt.title('Pace and Heart Rate Over Time')
    plt.legend()
    plt.show()

# Example usage
if __name__ == "__main__":
    # Sample data loading
    # df = pd.read_csv("your_data.csv", parse_dates=['timestamp'], index_col='timestamp')
    file_name = r"C:\Users\a717631\OneDrive - Eviden\Documents\Repo\theEagle\easy_runs\17-Feb-2025.fit"
    df = load_df_fitparse(file_name)
    df = preprocess_data(df)
    
    # Analyze pace efficiency at a given power level (adjust as needed)
    power_level = 250
    efficiency_df = analyze_pace_efficiency(df, power_level)
    print(efficiency_df.head())
    
    # Correlation analysis
    correlation_analysis(df)
    
    # Plot trends
    plot_trends(df)
