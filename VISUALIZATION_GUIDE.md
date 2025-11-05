# Workout Visualization Guide

## Overview

The Workout Visualizer is a Streamlit-based interactive dashboard that allows you to compare ground truth workouts with model-generated workouts. It provides visual power charts with zone coloring and comprehensive metrics comparison.

## Features

- **Interactive Power Charts**: Bar charts showing power over time with Zwift zone colors
- **Side-by-Side Comparison**: Ground truth vs model-generated workouts
- **FTP Reference Line**: Dashed line showing your Functional Threshold Power
- **Comprehensive Metrics**: Duration, power stats, latency, tokens, costs
- **Delta Calculations**: Automatic comparison of metrics between ground truth and model
- **Hover Information**: Detailed segment information on mouse hover

## Installation

Dependencies are already included in `pyproject.toml`. To ensure they're installed:

```bash
poetry install
```

## Usage

### Starting the App

```bash
poetry run streamlit run src/workout_visualizer.py
```

Or simply:

```bash
streamlit run src/workout_visualizer.py
```

The app will open in your browser at `http://localhost:8501`

### Configuration

In the sidebar, you can configure:

1. **FTP (Watts)**: Your Functional Threshold Power (default: 250W)
2. **Ground Truth Folder**: Path to ground truth run directory
   - Example: `ground_truth/run_20251104_155341`
3. **Results Folder**: Path to model results run directory
   - Example: `results/run_20251105_120620`
4. **Workout Selection**: Choose a workout from the dropdown
5. **Model Selection**: Choose a model to compare against ground truth

### Understanding the Display

#### Power Charts

- **X-axis**: Time in MM:SS format
- **Y-axis**: Power in Watts
- **Bar Width**: Duration of each segment
- **Bar Color**: Zone-based coloring (see below)
- **Dashed Red Line**: FTP reference line
- **Hover**: Shows power, duration, zone, and time range for each segment

#### Zone Colors (Zwift Standard)

- **Grey (Zone 1)**: Recovery (0-55% FTP)
- **Blue (Zone 2)**: Endurance (55-75% FTP)
- **Green (Zone 3)**: Tempo (75-95% FTP)
- **Yellow (Zone 4)**: Threshold (95-105% FTP)
- **Orange (Zone 5)**: VO2 Max (105-120% FTP)
- **Red (Zone 6)**: Anaerobic (120-150% FTP)
- **Black (Zone 7)**: Neuromuscular (>150% FTP)

#### Metrics Display

For both ground truth and model workouts, you'll see:

- **Duration**: Total workout time (HH:MM:SS)
- **Average Power**: Time-weighted average (watts)
- **Min/Max Power**: Power range (watts)
- **Intervals**: Number of segments
- **Attempts**: Generation attempts until success
- **Latency**: Total generation time (seconds/milliseconds)
- **Total Cost**: API cost ($)

For model workouts, delta (Δ) values show the difference from ground truth.

#### Token Cost Breakdown

Click "Token Cost Breakdown" expanders to see:

- Input tokens and cost
- Output tokens and cost
- Total tokens and cost
- Delta from ground truth (for models)

## Example Data

The repository includes example data you can use to test:

- **Ground Truth**: `ground_truth/run_20251104_155341/`
- **Results**: `results/run_20251105_120620/`

Available models in example data:
- Gemini 2.5 Flash Lite
- GPT-OSS 20B

## Troubleshooting

### "No workouts found" Error

- Verify the ground truth folder path is correct
- Ensure the folder contains `.json` files
- Check that JSON files have the expected structure

### "Could not load model workout" Error

- Verify the results folder path is correct
- Ensure the selected model has generated the selected workout
- Check that the model display name matches the configuration

### Charts Not Displaying

- Check browser console for errors
- Verify the workout JSON has valid `intervals` data
- Ensure all required fields are present (`power`, `startTimeSeconds`, `endTimeSeconds`, `zone`)

## File Structure

```
src/
├── workout_visualizer.py     # Main Streamlit app
└── visualization_utils.py    # Helper functions for data loading and charting
```

## Dependencies

- **streamlit**: Web app framework
- **plotly**: Interactive charting library
- **pyyaml**: YAML configuration parsing
- **pathlib**: File path handling
- **json**: JSON data parsing

## Tips

1. **Performance**: The app caches loaded data for faster switching between workouts
2. **Comparison**: Use the delta metrics to quickly identify differences
3. **Zone Analysis**: Look at bar colors to understand workout intensity distribution
4. **Cost Analysis**: Compare token usage and costs across different models

## Future Enhancements

Potential improvements:
- Batch comparison across multiple workouts
- Aggregate statistics dashboard
- Export comparison reports
- Zone time distribution charts
- Cost optimization recommendations
