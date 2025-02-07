# theEagle
Python-based tool to analyze Garmin FIT files for running performance metrics. Includes visualizations like scatter plots, box plots by heart rate zones, and power analysis to help runners optimize cadence, stride length, and overall efficiency


# Power by Heart Rate Zone Analysis

This repository contains a Python script to analyze running data from Garmin FIT files and visualize the relationship between power and heart rate zones using a box plot. The script leverages the FIT file format to extract performance metrics such as heart rate, power, cadence, and more.

## Installation
1. Clone this repository:
    ```bash
    git clone https://github.com/your-username/power-hr-boxplot.git
    ```
2. Install the required Python libraries:
    ```bash
    pip install fitparse pandas matplotlib seaborn
    ```

## Usage
1. Place your `.fit` file in the project directory.
2. Update the `fit_file_path` variable in the script to the path of your FIT file:
    ```python
    fit_file_path = "path/to/your/fitfile.fit"
    ```
3. Run the script:
    ```bash
    python power_hr_boxplot.py
    ```
4. View the generated box plot, which displays power distribution by heart rate zones.

## Example Output
The box plot visualizes the power (Watts) distribution for each heart rate zone:
- **X-Axis**: Heart rate zones (Zone 1 to Zone 5).
- **Y-Axis**: Power output (Watts).

![Sample Box Plot](images/BoxPlot.png)  

## Data Fields Used
- **Heart Rate**: Recorded heart rate (bpm).
- **Power**: Power output (Watts).
- Optional fields include cadence, stride length, vertical oscillation, etc., if additional analysis is desired.

## Customization
You can adjust:
- Heart rate zone definitions by modifying the `classify_hr_zone` function.
- Plot aesthetics (color palette, title, labels) in the `sns.boxplot` function.

## Contributing
Contributions are welcome! Feel free to fork the repository and submit a pull request for enhancements or bug fixes.

## Questions?
If you have any questions or suggestions, feel free to open an issue or reach out via [vinodraj.j@gmail.com].

