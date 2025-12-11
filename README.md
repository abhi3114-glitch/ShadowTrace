# ShadowTrace

ShadowTrace is a desktop utility that estimates indoor movement and device orientation using laptop sensors. It is designed to track activity patterns, detect significant movement events, and generate daily heatmaps of device usage.

## Features

- **Real-time Movement Detection**: Monitors the accelerometer to detect when the device is active or stationary.
- **Activity Logging**: Records movement duration and frequency to a local SQLite database.
- **Hourly Analysis**: Visualizes activity levels throughout the day using interactive bar charts.
- **Tilt Heatmap**: Generates a scatter plot representing the distribution of device orientation (tilt), helping to identify different usage locations (e.g., desk, lap, couch).
- **Simulation Mode**: Automatically detects if hardware sensors are missing and falls back to a simulation mode that generates realistic random walk data for demonstration purposes.
- **Privacy Focused**: All data is stored locally on the machine. No data is uploaded to the cloud.

## Installation

### Prerequisites

- Python 3.10 or higher (Python 3.11 recommended for full hardware support on Windows)
- Windows 10/11 (for hardware sensor access)

### Setup

1. Clone the repository to your local machine.
2. Install the required dependencies:

   ```bash
   pip install streamlit pandas plotly winsdk scikit-learn
   ```

   Note: `winsdk` is required for accessing real hardware sensors on Windows. If it fails to install or if no sensors are detected, the application will default to Simulation Mode.

## Usage

1. Open a terminal in the project directory.
2. Run the application using Streamlit:

   ```bash
   streamlit run app.py
   ```

   If you have Python 3.11 installed via the Windows Launcher:
   ```bash
   py -3.11 -m streamlit run app.py
   ```

3. The dashboard will open in your default web browser (usually at http://localhost:8501).

## Architecture

- **app.py**: The main entry point for the Streamlit dashboard and the background sensor logging thread.
- **sensors/**: Contains the sensor logic.
  - `base.py`: Abstract base class for sensor implementations.
  - `windows_native.py`: interfacing with Windows Runtime API for real hardware access.
  - `simulated.py`: Generates synthetic data when hardware is unavailable.
- **database/**: Handles SQLite database connections and schema management.
- **analysis/**: Contains logic for movement event detection and clustering analysis.

## troubleshooting

- **Mode: Simulation**: If the sidebar shows "Simulation Mode", it means the application could not detect a physical accelerometer. This is expected on desktops or older laptops.
- **Import Errors**: Ensure you have installed all requirements. If you encounter issues with `winsdk`, try using Python 3.11.

## License

This project is licensed under the MIT License.
