"""
Streamlit app for visualizing and comparing workout generation results.

This app allows users to:
- Compare ground truth workouts with model-generated workouts
- View interactive power charts with zone coloring
- Analyze generation metrics (latency, tokens, cost)
- Select different workouts and models for comparison

Usage:
    streamlit run src/workout_visualizer.py
"""

import streamlit as st
from pathlib import Path
import sys

# Add src to path for imports
sys.path.append(str(Path(__file__).parent))

from visualization_utils import (
    load_ground_truth_workout,
    load_model_workout,
    list_available_workouts,
    list_available_models,
    calculate_workout_stats,
    create_power_chart,
    calculate_deltas,
)


# Page configuration
st.set_page_config(
    page_title="Workout Generator Visualizer",
    page_icon="🚴",
    layout="wide",
    initial_sidebar_state="expanded"
)


def main():
    """Main Streamlit application."""

    st.title("🚴 Workout Generator Visualizer")

    # Sidebar configuration
    st.sidebar.header("Configuration")

    # FTP input
    ftp = st.sidebar.number_input(
        "FTP (Watts)",
        min_value=100,
        max_value=500,
        value=250,
        step=5,
        help="Functional Threshold Power - used for the reference line on charts"
    )

    # Ground truth folder selection
    st.sidebar.subheader("Ground Truth Run")
    gt_folder = st.sidebar.text_input(
        "Ground Truth Folder",
        value="ground_truth/run_20251104_155341",
        help="Path to ground truth run directory"
    )

    # Model results folder selection
    st.sidebar.subheader("Model Results Run")
    results_folder = st.sidebar.text_input(
        "Results Folder",
        value="results/run_20251105_120620",
        help="Path to model results run directory"
    )

    # Validate folders exist
    gt_path = Path(gt_folder)
    results_path = Path(results_folder)

    if not gt_path.exists():
        st.error(f"❌ Ground truth folder not found: {gt_folder}")
        st.info("Please enter a valid path to a ground truth run directory")
        return

    if not results_path.exists():
        st.error(f"❌ Results folder not found: {results_folder}")
        st.info("Please enter a valid path to a results run directory")
        return

    # Load available workouts from ground truth
    workouts = list_available_workouts(gt_folder)

    if not workouts:
        st.warning(f"⚠️ No workouts found in {gt_folder}")
        return

    # Load available models
    models_yaml = "config/models.yaml"
    gt_yaml = "config/ground_truth.yaml"

    available_models = list_available_models(models_yaml, gt_yaml)

    if not available_models:
        st.warning("⚠️ No models found in config/models.yaml")
        return

    # Workout selection dropdown
    st.sidebar.subheader("Workout Selection")

    workout_options = {desc: prompt_id for prompt_id, desc in workouts}
    selected_workout_desc = st.sidebar.selectbox(
        "Select Workout",
        options=list(workout_options.keys()),
        help="Choose a workout to visualize"
    )

    selected_prompt_id = workout_options[selected_workout_desc]

    # Model selection dropdown
    selected_model = st.sidebar.selectbox(
        "Select Model",
        options=available_models,
        help="Choose a model to compare against ground truth"
    )

    # Divider
    st.markdown("---")

    # Load workout data
    with st.spinner("Loading workout data..."):
        gt_data = load_ground_truth_workout(gt_folder, selected_prompt_id)
        model_data = load_model_workout(results_folder, selected_model, selected_prompt_id)

    # Check if data loaded successfully
    if not gt_data:
        st.error(f"❌ Could not load ground truth workout: {selected_prompt_id}")
        return

    if not model_data:
        st.error(f"❌ Could not load model workout for {selected_model}: {selected_prompt_id}")
        st.info("This model may not have generated this specific workout.")
        return

    # Calculate statistics
    gt_stats = calculate_workout_stats(gt_data, ftp)
    model_stats = calculate_workout_stats(model_data, ftp)
    deltas = calculate_deltas(gt_stats, model_stats)

    # Workout description in compact format
    st.markdown(f"**{gt_stats.get('description', 'N/A')}** | _{gt_stats.get('user_prompt', 'N/A')}_")

    # Custom CSS for consistent metric fonts and styling
    st.markdown("""
        <style>
        [data-testid="stMetricValue"] {
            font-size: 22px;
            font-weight: 400;
        }
        [data-testid="stMetricLabel"] {
            font-size: 14px;
            font-weight: 400;
        }
        div[data-testid="stMetric"] {
            background-color: transparent;
            padding: 5px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Create two columns for side-by-side comparison
    left_col, right_col = st.columns(2)

    # LEFT COLUMN: Ground Truth
    with left_col:
        st.markdown("#### 🎯 Ground Truth")

        # Chart
        gt_chart = create_power_chart(
            gt_data,
            ftp,
            "Ground Truth"
        )
        if gt_chart:
            st.plotly_chart(gt_chart, use_container_width=True)
        else:
            st.error("Could not generate ground truth chart")

        # Compact metrics in 3 columns - using same HTML structure as right side
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"<p style='font-size: 14px; margin-bottom: 2px; font-weight: 400;'>Duration</p><p style='font-size: 22px; font-weight: 400; margin-top: 0px;'>{gt_stats['duration_formatted']}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size: 14px; margin-bottom: 2px; font-weight: 400;'>Intervals</p><p style='font-size: 22px; font-weight: 400; margin-top: 0px;'>{gt_stats['num_intervals']}</p>", unsafe_allow_html=True)
        with m2:
            st.markdown(f"<p style='font-size: 14px; margin-bottom: 2px; font-weight: 400;'>Avg Power</p><p style='font-size: 22px; font-weight: 400; margin-top: 0px;'>{gt_stats['avg_power']:.1f}W</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size: 14px; margin-bottom: 2px; font-weight: 400;'>Min/Max</p><p style='font-size: 22px; font-weight: 400; margin-top: 0px;'>{gt_stats['min_power']}/{gt_stats['max_power']}W</p>", unsafe_allow_html=True)
        with m3:
            st.markdown(f"<p style='font-size: 14px; margin-bottom: 2px; font-weight: 400;'>Latency</p><p style='font-size: 22px; font-weight: 400; margin-top: 0px;'>{gt_stats['latency_sec']:.1f}s</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size: 14px; margin-bottom: 2px; font-weight: 400;'>Cost</p><p style='font-size: 22px; font-weight: 400; margin-top: 0px;'>${gt_stats['total_cost']:.4f}</p>", unsafe_allow_html=True)

        # Compact token info
        with st.expander("📊 Tokens & Cost Details"):
            st.text(f"Input:  {gt_stats['input_tokens']:,} tokens (${gt_stats['input_cost']:.6f})")
            st.text(f"Output: {gt_stats['output_tokens']:,} tokens (${gt_stats['output_cost']:.6f})")
            st.text(f"Total:  {gt_stats['total_tokens']:,} tokens (${gt_stats['total_cost']:.6f})")
            st.text(f"Attempts: {gt_stats['attempts']}")

    # RIGHT COLUMN: Model
    with right_col:
        st.markdown(f"#### 🤖 {selected_model}")

        # Chart
        model_chart = create_power_chart(
            model_data,
            ftp,
            selected_model
        )
        if model_chart:
            st.plotly_chart(model_chart, use_container_width=True)
        else:
            st.error("Could not generate model chart")

        # Compact metrics with deltas
        m1, m2, m3 = st.columns(3)
        with m1:
            duration_delta_sec = int(deltas.get('duration', '0'))
            st.markdown(f"<p style='font-size: 14px; margin-bottom: 2px; font-weight: 400;'>Duration</p><p style='font-size: 22px; font-weight: 400; margin-top: 0px;'>{model_stats['duration_formatted']} <span style='font-size: 16px; color: {'green' if duration_delta_sec <= 0 else 'red'}'>({duration_delta_sec:+d}s)</span></p>", unsafe_allow_html=True)

            intervals_delta = int(deltas.get('num_intervals', '0'))
            st.markdown(f"<p style='font-size: 14px; margin-bottom: 2px; font-weight: 400;'>Intervals</p><p style='font-size: 22px; font-weight: 400; margin-top: 0px;'>{model_stats['num_intervals']} <span style='font-size: 16px; color: {'green' if intervals_delta <= 0 else 'red'}'>({intervals_delta:+d})</span></p>", unsafe_allow_html=True)

        with m2:
            avg_power_delta = float(deltas.get('avg_power', '0'))
            st.markdown(f"<p style='font-size: 14px; margin-bottom: 2px; font-weight: 400;'>Avg Power</p><p style='font-size: 22px; font-weight: 400; margin-top: 0px;'>{model_stats['avg_power']:.1f}W <span style='font-size: 16px; color: {'green' if avg_power_delta <= 0 else 'red'}'>({avg_power_delta:+.1f}W)</span></p>", unsafe_allow_html=True)

            min_delta = int(deltas.get('min_power', '0'))
            max_delta = int(deltas.get('max_power', '0'))
            st.markdown(f"<p style='font-size: 14px; margin-bottom: 2px; font-weight: 400;'>Min/Max</p><p style='font-size: 22px; font-weight: 400; margin-top: 0px;'>{model_stats['min_power']}/{model_stats['max_power']}W <span style='font-size: 16px; color: gray'>({min_delta:+d}/{max_delta:+d}W)</span></p>", unsafe_allow_html=True)

        with m3:
            latency_delta = (model_stats['latency_ms'] - gt_stats['latency_ms'])/1000
            st.markdown(f"<p style='font-size: 14px; margin-bottom: 2px; font-weight: 400;'>Latency</p><p style='font-size: 22px; font-weight: 400; margin-top: 0px;'>{model_stats['latency_sec']:.1f}s <span style='font-size: 16px; color: {'green' if latency_delta <= 0 else 'red'}'>({latency_delta:+.1f}s)</span></p>", unsafe_allow_html=True)

            cost_delta = model_stats['total_cost'] - gt_stats['total_cost']
            st.markdown(f"<p style='font-size: 14px; margin-bottom: 2px; font-weight: 400;'>Cost</p><p style='font-size: 22px; font-weight: 400; margin-top: 0px;'>${model_stats['total_cost']:.4f} <span style='font-size: 16px; color: {'green' if cost_delta <= 0 else 'red'}'>({cost_delta:+.4f})</span></p>", unsafe_allow_html=True)

        # Compact token info with deltas
        with st.expander("📊 Tokens & Cost Details"):
            st.text(f"Input:  {model_stats['input_tokens']:,} ({deltas.get('input_tokens', '0')}) tokens (${model_stats['input_cost']:.6f})")
            st.text(f"Output: {model_stats['output_tokens']:,} ({deltas.get('output_tokens', '0')}) tokens (${model_stats['output_cost']:.6f})")
            st.text(f"Total:  {model_stats['total_tokens']:,} ({deltas.get('total_tokens', '0')}) tokens (${model_stats['total_cost']:.6f})")
            st.text(f"Attempts: {model_stats['attempts']}")


if __name__ == "__main__":
    main()
