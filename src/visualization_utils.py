"""
Utility functions for workout visualization in Streamlit.
Handles data loading, chart generation, and statistics calculation.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import plotly.graph_objects as go
import yaml


# Zwift zone colors
ZONE_COLORS = {
    1: "#808080",  # Grey - Recovery
    2: "#4169E1",  # Blue - Endurance
    3: "#00C851",  # Green - Tempo
    4: "#FFD700",  # Yellow - Threshold
    5: "#FF8800",  # Orange - VO2 Max
    6: "#FF0000",  # Red - Anaerobic
    7: "#000000",  # Black - Neuromuscular
}


def load_ground_truth_workout(run_dir: str, prompt_id: str) -> Optional[Dict]:
    """
    Load a ground truth workout JSON file.

    Args:
        run_dir: Path to ground truth run directory (e.g., 'ground_truth/run_20251104_155341')
        prompt_id: Prompt identifier (e.g., 'threshold_intervals_3x10')

    Returns:
        Dictionary with workout data or None if not found
    """
    file_path = Path(run_dir) / f"{prompt_id}.json"

    if not file_path.exists():
        return None

    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading ground truth workout: {e}")
        return None


def load_model_workout(run_dir: str, model_display_name: str, prompt_id: str) -> Optional[Dict]:
    """
    Load a model-generated workout JSON file.

    Args:
        run_dir: Path to results run directory (e.g., 'results/run_20251105_120620')
        model_display_name: Display name of the model (e.g., 'GPT-4o')
        prompt_id: Prompt identifier

    Returns:
        Dictionary with workout data or None if not found
    """
    run_path = Path(run_dir)

    if not run_path.exists():
        return None

    # Search for files matching the prompt_id
    # Files may be named: {prompt_id}_{model_identifier}.json
    for json_file in run_path.glob(f"{prompt_id}_*.json"):
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                # Check if this file is for the requested model
                if data.get('model', {}).get('display_name') == model_display_name:
                    return data
        except (json.JSONDecodeError, IOError):
            continue

    # Also try exact match
    exact_file = run_path / f"{prompt_id}.json"
    if exact_file.exists():
        try:
            with open(exact_file, 'r') as f:
                data = json.load(f)
                if data.get('model', {}).get('display_name') == model_display_name:
                    return data
        except (json.JSONDecodeError, IOError):
            pass

    return None


def list_available_workouts(run_dir: str) -> List[Tuple[str, str]]:
    """
    List all available workout prompt IDs in a run directory.

    Args:
        run_dir: Path to run directory

    Returns:
        List of tuples (prompt_id, display_name) sorted alphabetically
    """
    run_path = Path(run_dir)

    if not run_path.exists():
        return []

    workouts = []
    for json_file in run_path.glob("*.json"):
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                prompt_id = data.get('prompt_id', json_file.stem)
                description = data.get('prompt_description', prompt_id)
                workouts.append((prompt_id, description))
        except (json.JSONDecodeError, IOError):
            continue

    return sorted(workouts, key=lambda x: x[1])


def list_available_models(models_yaml_path: str, ground_truth_yaml_path: str) -> List[str]:
    """
    List all available models from models.yaml, excluding the ground truth model.

    Args:
        models_yaml_path: Path to models.yaml
        ground_truth_yaml_path: Path to ground_truth.yaml

    Returns:
        List of model display names
    """
    try:
        with open(models_yaml_path, 'r') as f:
            models_config = yaml.safe_load(f)

        with open(ground_truth_yaml_path, 'r') as f:
            gt_config = yaml.safe_load(f)

        gt_model_id = gt_config['reference_model']['model_id']
        gt_provider = gt_config['reference_model']['provider']

        model_names = []
        for model in models_config.get('models', []):
            # Exclude ground truth model
            if model['model_id'] == gt_model_id and model['provider'] == gt_provider:
                continue
            model_names.append(model['display_name'])

        return sorted(model_names)

    except (IOError, yaml.YAMLError, KeyError) as e:
        print(f"Error loading models: {e}")
        return []


def calculate_workout_stats(workout_data: Dict, ftp: int) -> Dict:
    """
    Calculate comprehensive statistics from workout data.

    Args:
        workout_data: Workout JSON data (ground truth or model result format)
        ftp: Functional Threshold Power

    Returns:
        Dictionary with calculated statistics
    """
    if not workout_data:
        return {}

    # Handle different data structures
    # Ground truth: workout_data['workout']
    # Model results: workout_data['response']['parsed_json']
    workout = None
    if 'workout' in workout_data:
        workout = workout_data['workout']
    elif 'response' in workout_data and 'parsed_json' in workout_data['response']:
        workout = workout_data['response']['parsed_json']
    else:
        return {}

    intervals = workout.get('intervals', [])

    if not intervals:
        return {}

    # Basic workout info
    duration = workout.get('workout_duration', 0)
    num_intervals = len(intervals)

    # Power statistics
    powers = [seg['power'] for seg in intervals]
    durations = [seg['endTimeSeconds'] - seg['startTimeSeconds'] for seg in intervals]

    # Time-weighted average power
    total_power_time = sum(p * d for p, d in zip(powers, durations))
    avg_power = total_power_time / duration if duration > 0 else 0

    min_power = min(powers) if powers else 0
    max_power = max(powers) if powers else 0

    # Generation metadata - can be at different levels
    # Ground truth: workout_data['generation_metadata']
    # Model results: directly at top level
    metadata = workout_data.get('generation_metadata', workout_data)

    attempts = metadata.get('attempts', 1)
    latency = metadata.get('total_latency_all_attempts', 0)

    tokens = metadata.get('total_tokens_all_attempts', {})
    input_tokens = tokens.get('input', 0)
    output_tokens = tokens.get('output', 0)
    total_tokens = tokens.get('total', 0)

    total_cost = metadata.get('total_cost_all_attempts', 0)
    input_cost = metadata.get('total_input_cost_all_attempts', 0)
    output_cost = metadata.get('total_output_cost_all_attempts', 0)

    # Prompt info
    user_prompt = workout_data.get('user_prompt', 'N/A')
    description = workout_data.get('prompt_description', 'N/A')

    return {
        'duration': duration,
        'duration_formatted': format_time(duration),
        'avg_power': round(avg_power, 1),
        'min_power': min_power,
        'max_power': max_power,
        'num_intervals': num_intervals,
        'attempts': attempts,
        'latency_ms': latency,
        'latency_sec': round(latency / 1000, 2),
        'input_tokens': input_tokens,
        'output_tokens': output_tokens,
        'total_tokens': total_tokens,
        'total_cost': round(total_cost, 6),
        'input_cost': round(input_cost, 6),
        'output_cost': round(output_cost, 6),
        'user_prompt': user_prompt,
        'description': description,
    }


def format_time(seconds: int) -> str:
    """Format seconds as HH:MM:SS or MM:SS."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def format_time_axis(seconds: int) -> str:
    """Format seconds for axis labels (MM:SS)."""
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02d}:{secs:02d}"


def create_power_chart(workout_data: Dict, ftp: int, title: str) -> Optional[go.Figure]:
    """
    Create an interactive Plotly bar chart showing power over time with zone colors.

    Args:
        workout_data: Workout JSON data
        ftp: Functional Threshold Power for the dashed line
        title: Chart title

    Returns:
        Plotly Figure object or None if data is invalid
    """
    if not workout_data:
        return None

    # Handle different data structures
    workout = None
    if 'workout' in workout_data:
        workout = workout_data['workout']
    elif 'response' in workout_data and 'parsed_json' in workout_data['response']:
        workout = workout_data['response']['parsed_json']
    else:
        return None

    intervals = workout.get('intervals', [])

    if not intervals:
        return None

    # Prepare data for bar chart
    x_positions = []  # Center position of each bar
    widths = []  # Width of each bar (duration)
    heights = []  # Height of each bar (power)
    colors = []  # Color based on zone
    hover_texts = []  # Custom hover text

    for segment in intervals:
        start = segment['startTimeSeconds']
        end = segment['endTimeSeconds']
        power = segment['power']
        zone = segment.get('zone', 1)
        duration = end - start

        # Bar center position
        center = start + duration / 2
        x_positions.append(center)
        widths.append(duration)
        heights.append(power)
        colors.append(ZONE_COLORS.get(zone, "#CCCCCC"))

        # Hover text
        hover_text = (
            f"Power: {power} W<br>"
            f"Duration: {format_time(duration)}<br>"
            f"Zone: {zone}<br>"
            f"Time: {format_time_axis(start)} - {format_time_axis(end)}"
        )
        hover_texts.append(hover_text)

    # Create figure
    fig = go.Figure()

    # Add bars
    fig.add_trace(go.Bar(
        x=x_positions,
        y=heights,
        width=widths,
        marker=dict(
            color=colors,
            line=dict(width=0.5, color='white')
        ),
        hovertext=hover_texts,
        hoverinfo='text',
        showlegend=False
    ))

    # Add FTP line
    max_time = intervals[-1]['endTimeSeconds']
    fig.add_trace(go.Scatter(
        x=[0, max_time],
        y=[ftp, ftp],
        mode='lines',
        line=dict(color='red', width=2, dash='dash'),
        name=f'FTP ({ftp}W)',
        showlegend=True,
        hoverinfo='skip'
    ))

    # Update layout
    fig.update_layout(
        title=dict(text=title, font=dict(size=14)),
        xaxis_title="Time",
        yaxis_title="Power (W)",
        xaxis=dict(
            tickmode='array',
            tickvals=[i for i in range(0, max_time + 1, max(60, max_time // 10))],
            ticktext=[format_time_axis(i) for i in range(0, max_time + 1, max(60, max_time // 10))],
            range=[0, max_time]
        ),
        yaxis=dict(
            range=[0, max(heights) * 1.1]
        ),
        hovermode='closest',
        bargap=0,
        height=300,
        margin=dict(l=50, r=20, t=40, b=40),
        template='plotly_white'
    )

    return fig


def calculate_deltas(gt_stats: Dict, model_stats: Dict) -> Dict:
    """
    Calculate differences between ground truth and model statistics.

    Args:
        gt_stats: Ground truth statistics
        model_stats: Model statistics

    Returns:
        Dictionary with delta values
    """
    deltas = {}

    numeric_fields = [
        'duration', 'avg_power', 'min_power', 'max_power',
        'num_intervals', 'latency_ms', 'total_tokens',
        'input_tokens', 'output_tokens', 'total_cost'
    ]

    for field in numeric_fields:
        gt_val = gt_stats.get(field, 0)
        model_val = model_stats.get(field, 0)
        delta = model_val - gt_val

        # Format delta with sign
        if field in ['total_cost', 'input_cost', 'output_cost']:
            deltas[field] = f"{delta:+.6f}"
        elif field in ['avg_power']:
            deltas[field] = f"{delta:+.1f}"
        else:
            deltas[field] = f"{delta:+d}" if isinstance(delta, int) else f"{delta:+.0f}"

    return deltas
