import os
import pandas as pd
from fitparse import FitFile

# Function to process a .fit file
def process_fit_file(file_path, weight_kg):
    fitfile = FitFile(file_path)
    records = []

    # Iterate over the messages in the fit file
    for record in fitfile.get_messages("record"):
        record_data = {}
        for data in record:
            record_data[data.name] = data.value

        # Extract relevant fields: time, power, and heart rate
        if "power" in record_data and "heart_rate" in record_data:
            records.append({
                "timestamp": record_data.get("timestamp"),
                "power": record_data.get("power"),
                "heart_rate": record_data.get("heart_rate"),
                "speed": record_data.get("speed", None),
            })

    # Convert records into a DataFrame
    df = pd.DataFrame(records)

    # Calculate Power-to-Weight Ratio (PWR)
    df["power_to_weight_ratio"] = df["power"] / weight_kg

    return df

# Main function to process multiple files and export to Excel
def export_to_excel(fit_files_dir, weight_kg, output_excel):
    all_data = []

    # Process each .fit file in the directory
    for file_name in os.listdir(fit_files_dir):
        if file_name.endswith(".fit"):
            file_path = os.path.join(fit_files_dir, file_name)
            print(f"Processing file: {file_name}")
            df = process_fit_file(file_path, weight_kg)
            df["file_name"] = file_name  # Add the file name for reference
            all_data.append(df)

    # Concatenate all data into a single DataFrame
    final_df = pd.concat(all_data, ignore_index=True)

    # Save to Excel
    final_df.to_excel(output_excel, index=False, engine="openpyxl")
    print(f"Data exported to {output_excel}")

# Example usage
if __name__ == "__main__":
    fit_files_directory = r"C:\Users\username\Downloads\fit_files"  # Replace with your .fit file directory
    body_weight_kg = 72  # Replace with your weight in kilograms
    output_file = "garmin_data.xlsx"

    export_to_excel(fit_files_directory, body_weight_kg, output_file)
