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
    list_available_models_from_run,
    calculate_workout_stats,
    create_power_chart,
    calculate_deltas,
    load_all_ground_truth_workouts,
    load_all_model_workouts,
    calculate_aggregate_stats,
    calculate_per_workout_comparison,
)
from structure_quality_tab import render_structure_quality_tab
import pandas as pd


# Page configuration
st.set_page_config(
    page_title="Workout Generator Visualizer",
    page_icon="🚴",
    layout="wide",
    initial_sidebar_state="expanded"
)


def render_visual_comparison_tab(ftp, gt_folder, results_folder, selected_workout_desc, workout_options, selected_model):
    """Render the visual comparison tab (current functionality)."""
    selected_prompt_id = workout_options[selected_workout_desc]

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
            st.markdown(f"<p style='font-size: 14px; margin-bottom: 2px; font-weight: 400;'>Cost</p><p style='font-size: 22px; font-weight: 400; margin-top: 0px;'>€{gt_stats['total_cost']:.4f}</p>", unsafe_allow_html=True)

        # Compact token info
        with st.expander("📊 Tokens & Cost Details"):
            st.text(f"Input:  {gt_stats['input_tokens']:,} tokens (€{gt_stats['input_cost']:.6f})")
            st.text(f"Output: {gt_stats['output_tokens']:,} tokens (€{gt_stats['output_cost']:.6f})")
            st.text(f"Total:  {gt_stats['total_tokens']:,} tokens (€{gt_stats['total_cost']:.6f})")
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
            st.markdown(f"<p style='font-size: 14px; margin-bottom: 2px; font-weight: 400;'>Cost</p><p style='font-size: 22px; font-weight: 400; margin-top: 0px;'>€{model_stats['total_cost']:.4f} <span style='font-size: 16px; color: {'green' if cost_delta <= 0 else 'red'}'>({cost_delta:+.4f})</span></p>", unsafe_allow_html=True)

        # Compact token info with deltas
        with st.expander("📊 Tokens & Cost Details"):
            st.text(f"Input:  {model_stats['input_tokens']:,} ({deltas.get('input_tokens', '0')}) tokens (€{model_stats['input_cost']:.6f})")
            st.text(f"Output: {model_stats['output_tokens']:,} ({deltas.get('output_tokens', '0')}) tokens (€{model_stats['output_cost']:.6f})")
            st.text(f"Total:  {model_stats['total_tokens']:,} ({deltas.get('total_tokens', '0')}) tokens (€{model_stats['total_cost']:.6f})")
            st.text(f"Attempts: {model_stats['attempts']}")


def render_model_vs_model_tab(ftp, results_folder, selected_workout_desc, workout_options, available_models):
    """Render the model vs model comparison tab."""
    selected_prompt_id = workout_options[selected_workout_desc]

    st.markdown("---")

    # Model selectors in two columns
    selector_col1, selector_col2 = st.columns(2)

    with selector_col1:
        model_left = st.selectbox(
            "Left Model",
            options=available_models,
            key="model_left",
            help="Select the model to display on the left"
        )

    with selector_col2:
        model_right = st.selectbox(
            "Right Model",
            options=available_models,
            key="model_right",
            index=min(1, len(available_models) - 1) if len(available_models) > 1 else 0,
            help="Select the model to display on the right"
        )

    # Load workout data
    with st.spinner("Loading workout data..."):
        model_left_data = load_model_workout(results_folder, model_left, selected_prompt_id)
        model_right_data = load_model_workout(results_folder, model_right, selected_prompt_id)

    # Check if data loaded successfully
    if not model_left_data:
        st.error(f"❌ Could not load workout for {model_left}: {selected_prompt_id}")
        st.info("This model may not have generated this specific workout.")
        return

    if not model_right_data:
        st.error(f"❌ Could not load workout for {model_right}: {selected_prompt_id}")
        st.info("This model may not have generated this specific workout.")
        return

    # Calculate statistics
    model_left_stats = calculate_workout_stats(model_left_data, ftp)
    model_right_stats = calculate_workout_stats(model_right_data, ftp)
    deltas = calculate_deltas(model_left_stats, model_right_stats)

    # Display workout description and prompt (use left model's data, both should have the same prompt)
    description = model_left_stats.get('description', selected_workout_desc)
    user_prompt = model_left_stats.get('user_prompt', 'N/A')
    st.markdown(f"**{description}** | _{user_prompt}_")

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

    # LEFT COLUMN: Model Left
    with left_col:
        st.markdown(f"#### 🤖 {model_left}")

        # Chart
        model_left_chart = create_power_chart(
            model_left_data,
            ftp,
            model_left
        )
        if model_left_chart:
            st.plotly_chart(model_left_chart, use_container_width=True)
        else:
            st.error("Could not generate chart")

        # Compact metrics in 3 columns
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"<p style='font-size: 14px; margin-bottom: 2px; font-weight: 400;'>Duration</p><p style='font-size: 22px; font-weight: 400; margin-top: 0px;'>{model_left_stats['duration_formatted']}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size: 14px; margin-bottom: 2px; font-weight: 400;'>Intervals</p><p style='font-size: 22px; font-weight: 400; margin-top: 0px;'>{model_left_stats['num_intervals']}</p>", unsafe_allow_html=True)
        with m2:
            st.markdown(f"<p style='font-size: 14px; margin-bottom: 2px; font-weight: 400;'>Avg Power</p><p style='font-size: 22px; font-weight: 400; margin-top: 0px;'>{model_left_stats['avg_power']:.1f}W</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size: 14px; margin-bottom: 2px; font-weight: 400;'>Min/Max</p><p style='font-size: 22px; font-weight: 400; margin-top: 0px;'>{model_left_stats['min_power']}/{model_left_stats['max_power']}W</p>", unsafe_allow_html=True)
        with m3:
            st.markdown(f"<p style='font-size: 14px; margin-bottom: 2px; font-weight: 400;'>Latency</p><p style='font-size: 22px; font-weight: 400; margin-top: 0px;'>{model_left_stats['latency_sec']:.1f}s</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size: 14px; margin-bottom: 2px; font-weight: 400;'>Cost</p><p style='font-size: 22px; font-weight: 400; margin-top: 0px;'>€{model_left_stats['total_cost']:.4f}</p>", unsafe_allow_html=True)

        # Compact token info
        with st.expander("📊 Tokens & Cost Details"):
            st.text(f"Input:  {model_left_stats['input_tokens']:,} tokens (€{model_left_stats['input_cost']:.6f})")
            st.text(f"Output: {model_left_stats['output_tokens']:,} tokens (€{model_left_stats['output_cost']:.6f})")
            st.text(f"Total:  {model_left_stats['total_tokens']:,} tokens (€{model_left_stats['total_cost']:.6f})")
            st.text(f"Attempts: {model_left_stats['attempts']}")

    # RIGHT COLUMN: Model Right
    with right_col:
        st.markdown(f"#### 🤖 {model_right}")

        # Chart
        model_right_chart = create_power_chart(
            model_right_data,
            ftp,
            model_right
        )
        if model_right_chart:
            st.plotly_chart(model_right_chart, use_container_width=True)
        else:
            st.error("Could not generate chart")

        # Compact metrics with deltas (comparing to left model)
        m1, m2, m3 = st.columns(3)
        with m1:
            duration_delta_sec = int(deltas.get('duration', '0'))
            st.markdown(f"<p style='font-size: 14px; margin-bottom: 2px; font-weight: 400;'>Duration</p><p style='font-size: 22px; font-weight: 400; margin-top: 0px;'>{model_right_stats['duration_formatted']} <span style='font-size: 16px; color: {'green' if duration_delta_sec <= 0 else 'red'}'>({duration_delta_sec:+d}s)</span></p>", unsafe_allow_html=True)

            intervals_delta = int(deltas.get('num_intervals', '0'))
            st.markdown(f"<p style='font-size: 14px; margin-bottom: 2px; font-weight: 400;'>Intervals</p><p style='font-size: 22px; font-weight: 400; margin-top: 0px;'>{model_right_stats['num_intervals']} <span style='font-size: 16px; color: {'green' if intervals_delta <= 0 else 'red'}'>({intervals_delta:+d})</span></p>", unsafe_allow_html=True)

        with m2:
            avg_power_delta = float(deltas.get('avg_power', '0'))
            st.markdown(f"<p style='font-size: 14px; margin-bottom: 2px; font-weight: 400;'>Avg Power</p><p style='font-size: 22px; font-weight: 400; margin-top: 0px;'>{model_right_stats['avg_power']:.1f}W <span style='font-size: 16px; color: {'green' if avg_power_delta <= 0 else 'red'}'>({avg_power_delta:+.1f}W)</span></p>", unsafe_allow_html=True)

            min_delta = int(deltas.get('min_power', '0'))
            max_delta = int(deltas.get('max_power', '0'))
            st.markdown(f"<p style='font-size: 14px; margin-bottom: 2px; font-weight: 400;'>Min/Max</p><p style='font-size: 22px; font-weight: 400; margin-top: 0px;'>{model_right_stats['min_power']}/{model_right_stats['max_power']}W <span style='font-size: 16px; color: gray'>({min_delta:+d}/{max_delta:+d}W)</span></p>", unsafe_allow_html=True)

        with m3:
            latency_delta = (model_right_stats['latency_ms'] - model_left_stats['latency_ms'])/1000
            st.markdown(f"<p style='font-size: 14px; margin-bottom: 2px; font-weight: 400;'>Latency</p><p style='font-size: 22px; font-weight: 400; margin-top: 0px;'>{model_right_stats['latency_sec']:.1f}s <span style='font-size: 16px; color: {'green' if latency_delta <= 0 else 'red'}'>({latency_delta:+.1f}s)</span></p>", unsafe_allow_html=True)

            cost_delta = model_right_stats['total_cost'] - model_left_stats['total_cost']
            st.markdown(f"<p style='font-size: 14px; margin-bottom: 2px; font-weight: 400;'>Cost</p><p style='font-size: 22px; font-weight: 400; margin-top: 0px;'>€{model_right_stats['total_cost']:.4f} <span style='font-size: 16px; color: {'green' if cost_delta <= 0 else 'red'}'>({cost_delta:+.4f})</span></p>", unsafe_allow_html=True)

        # Compact token info with deltas
        with st.expander("📊 Tokens & Cost Details"):
            st.text(f"Input:  {model_right_stats['input_tokens']:,} ({deltas.get('input_tokens', '0')}) tokens (€{model_right_stats['input_cost']:.6f})")
            st.text(f"Output: {model_right_stats['output_tokens']:,} ({deltas.get('output_tokens', '0')}) tokens (€{model_right_stats['output_cost']:.6f})")
            st.text(f"Total:  {model_right_stats['total_tokens']:,} ({deltas.get('total_tokens', '0')}) tokens (€{model_right_stats['total_cost']:.6f})")
            st.text(f"Attempts: {model_right_stats['attempts']}")

    # Comparison summary at the bottom
    st.markdown("---")
    st.markdown("### 📊 Comparison Summary")

    summary_cols = st.columns(4)

    with summary_cols[0]:
        duration_diff = model_right_stats['duration'] - model_left_stats['duration']
        st.metric("Duration Difference", f"{duration_diff:+d}s",
                 delta=f"{abs(duration_diff)}s", delta_color="inverse")

    with summary_cols[1]:
        latency_diff = model_right_stats['latency_sec'] - model_left_stats['latency_sec']
        st.metric("Latency Difference", f"{latency_diff:+.1f}s",
                 delta=f"{abs(latency_diff):.1f}s", delta_color="inverse")

    with summary_cols[2]:
        cost_diff = model_right_stats['total_cost'] - model_left_stats['total_cost']
        st.metric("Cost Difference", f"€{cost_diff:+.4f}",
                 delta=f"€{abs(cost_diff):.4f}", delta_color="inverse")

    with summary_cols[3]:
        token_diff = model_right_stats['total_tokens'] - model_left_stats['total_tokens']
        st.metric("Token Difference", f"{token_diff:+,}",
                 delta=f"{abs(token_diff):,}", delta_color="inverse")


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
        "Ground Truth Folder Path",
        value="ground_truth/run_20251104_155341",
        help="Enter the path to the ground truth run directory"
    )

    # Model results folder selection
    st.sidebar.subheader("Model Results Run")
    results_folder = st.sidebar.text_input(
        "Results Folder Path",
        value="results/run_20251105_120620",
        help="Enter the path to the model results run directory"
    )

    # Validate folders exist
    if not gt_folder or not results_folder:
        st.info("📁 Please enter ground truth and results run directories in the sidebar")
        return

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

    # Load available models from the results run folder (self-contained approach)
    available_models = list_available_models_from_run(results_folder)

    if not available_models:
        st.warning(f"⚠️ No models found in {results_folder}")
        st.info("Make sure the results folder contains JSON files with model data")
        return

    # Workout selection dropdown (for Visual Comparison tab)
    st.sidebar.subheader("Workout Selection")

    workout_options = {desc: prompt_id for prompt_id, desc in workouts}
    selected_workout_desc = st.sidebar.selectbox(
        "Select Workout",
        options=list(workout_options.keys()),
        help="Choose a workout to visualize"
    )

    # Model selection dropdown
    selected_model = st.sidebar.selectbox(
        "Select Model",
        options=available_models,
        help="Choose a model to compare against ground truth"
    )

    # Navigation in sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("Navigation")
    view_mode = st.sidebar.radio(
        "Select View",
        options=["📊 Table Comparison", "📈 Visual Comparison Ground Truth", "🔄 Model vs Model", "🎯 Structure Quality"],
        help="Choose between aggregate table view, ground truth comparison, model-to-model comparison, or structure quality analysis"
    )

    # Render content based on selected view
    if view_mode == "📊 Table Comparison":
        # TABLE COMPARISON TAB
        st.header("Aggregate Model Comparison")

        # Load all workouts for all models
        with st.spinner("Loading all workout data..."):
            gt_workouts = load_all_ground_truth_workouts(gt_folder)

            if not gt_workouts:
                st.error("No ground truth workouts found")
                return

            # Calculate aggregate stats for each model
            model_stats_list = []
            for model_name in available_models:
                model_workouts = load_all_model_workouts(results_folder, model_name)
                agg_stats = calculate_aggregate_stats(gt_workouts, model_workouts, ftp)

                if agg_stats:
                    agg_stats['Model'] = model_name
                    model_stats_list.append(agg_stats)

        # Summary Cards Section
        if model_stats_list:
            st.subheader("📊 Key Insights")

            # Find best models for different metrics
            df_stats = pd.DataFrame(model_stats_list)

            # Best model for cost (lowest avg cost)
            best_cost_model = df_stats.loc[df_stats['avg_cost'].idxmin()]

            # Fastest model (lowest avg latency)
            best_speed_model = df_stats.loc[df_stats['avg_latency_ms'].idxmin()]

            # Most token efficient (lowest avg total tokens)
            best_tokens_model = df_stats.loc[df_stats['total_tokens'].idxmin()]

            # Highest success rate
            best_success_model = df_stats.loc[df_stats['success_rate'].idxmax()]

            # Display summary cards in columns
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.markdown(f"""
                <div style='padding: 15px; background-color: #f0f9ff; border-radius: 8px; border-left: 4px solid #0ea5e9;'>
                    <p style='font-size: 14px; color: #64748b; margin: 0;'>💰 Most Cost-Effective</p>
                    <p style='font-size: 20px; font-weight: 600; margin: 5px 0;'>{best_cost_model['Model']}</p>
                    <p style='font-size: 14px; color: #0ea5e9; margin: 0;'>€{best_cost_model['avg_cost']:.4f}/workout</p>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div style='padding: 15px; background-color: #f0fdf4; border-radius: 8px; border-left: 4px solid #22c55e;'>
                    <p style='font-size: 14px; color: #64748b; margin: 0;'>⚡ Fastest</p>
                    <p style='font-size: 20px; font-weight: 600; margin: 5px 0;'>{best_speed_model['Model']}</p>
                    <p style='font-size: 14px; color: #22c55e; margin: 0;'>{best_speed_model['avg_latency_ms']:.0f}ms avg</p>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                <div style='padding: 15px; background-color: #fef3c7; border-radius: 8px; border-left: 4px solid #f59e0b;'>
                    <p style='font-size: 14px; color: #64748b; margin: 0;'>🎯 Most Token Efficient</p>
                    <p style='font-size: 20px; font-weight: 600; margin: 5px 0;'>{best_tokens_model['Model']}</p>
                    <p style='font-size: 14px; color: #f59e0b; margin: 0;'>{best_tokens_model['total_tokens']:,} tokens</p>
                </div>
                """, unsafe_allow_html=True)

            with col4:
                st.markdown(f"""
                <div style='padding: 15px; background-color: #fce7f3; border-radius: 8px; border-left: 4px solid #ec4899;'>
                    <p style='font-size: 14px; color: #64748b; margin: 0;'>✅ Most Reliable</p>
                    <p style='font-size: 20px; font-weight: 600; margin: 5px 0;'>{best_success_model['Model']}</p>
                    <p style='font-size: 14px; color: #ec4899; margin: 0;'>{best_success_model['success_rate']:.1f}% success</p>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

        if not model_stats_list:
            st.warning("No model data available for comparison")
        else:
            # Create DataFrame
            df = pd.DataFrame(model_stats_list)

            # Reorder columns
            column_order = [
                'Model', 'total_workouts', 'success_rate',
                'avg_cost', 'delta_avg_cost', 'total_cost', 'delta_total_cost',
                'total_input_tokens', 'delta_total_input_tokens',
                'total_output_tokens', 'delta_total_output_tokens',
                'total_tokens', 'delta_total_tokens',
                'avg_latency_ms', 'delta_avg_latency_ms',
                'total_latency_ms', 'delta_total_latency_ms',
                'avg_attempts', 'delta_avg_attempts',
                'avg_duration', 'delta_avg_duration',
                'avg_power', 'delta_avg_power',
                'avg_intervals', 'delta_avg_intervals'
            ]

            df = df[column_order]

            # Rename columns for display
            df_display = df.rename(columns={
                'Model': 'Model',
                'total_workouts': 'Workouts',
                'success_rate': 'Success %',
                'avg_cost': 'Avg Cost (€)',
                'delta_avg_cost': 'Δ Avg Cost',
                'total_cost': 'Total Cost (€)',
                'delta_total_cost': 'Δ Total Cost',
                'total_input_tokens': 'Input Tokens',
                'delta_total_input_tokens': 'Δ Input',
                'total_output_tokens': 'Output Tokens',
                'delta_total_output_tokens': 'Δ Output',
                'total_tokens': 'Total Tokens',
                'delta_total_tokens': 'Δ Tokens',
                'avg_latency_ms': 'Avg Latency (ms)',
                'delta_avg_latency_ms': 'Δ Avg Latency',
                'total_latency_ms': 'Total Latency (ms)',
                'delta_total_latency_ms': 'Δ Total Latency',
                'avg_attempts': 'Avg Attempts',
                'delta_avg_attempts': 'Δ Attempts',
                'avg_duration': 'Avg Duration (s)',
                'delta_avg_duration': 'Δ Duration',
                'avg_power': 'Avg Power (W)',
                'delta_avg_power': 'Δ Power',
                'avg_intervals': 'Avg Intervals',
                'delta_avg_intervals': 'Δ Intervals'
            })

            # Format numeric columns
            df_display['Avg Cost (€)'] = df_display['Avg Cost (€)'].apply(lambda x: f"€{x:.4f}")
            df_display['Total Cost (€)'] = df_display['Total Cost (€)'].apply(lambda x: f"€{x:.4f}")
            df_display['Success %'] = df_display['Success %'].apply(lambda x: f"{x:.1f}%")
            df_display['Avg Latency (ms)'] = df_display['Avg Latency (ms)'].apply(lambda x: f"{x:.0f}")
            df_display['Total Latency (ms)'] = df_display['Total Latency (ms)'].apply(lambda x: f"{x:.0f}")
            df_display['Avg Duration (s)'] = df_display['Avg Duration (s)'].apply(lambda x: f"{x:.0f}")
            df_display['Avg Power (W)'] = df_display['Avg Power (W)'].apply(lambda x: f"{x:.1f}")
            df_display['Avg Intervals'] = df_display['Avg Intervals'].apply(lambda x: f"{x:.1f}")
            df_display['Avg Attempts'] = df_display['Avg Attempts'].apply(lambda x: f"{x:.1f}")

            # Format delta columns with color indicators
            def format_delta_cost(x):
                if x < 0:
                    return f"🟢 {x:.4f}"
                elif x > 0:
                    return f"🔴 {x:+.4f}"
                else:
                    return f"{x:.4f}"

            def format_delta_numeric(x):
                if x < 0:
                    return f"🟢 {x:+.0f}"
                elif x > 0:
                    return f"🔴 {x:+.0f}"
                else:
                    return f"{x:.0f}"

            df_display['Δ Avg Cost'] = df_display['Δ Avg Cost'].apply(format_delta_cost)
            df_display['Δ Total Cost'] = df_display['Δ Total Cost'].apply(format_delta_cost)
            df_display['Δ Input'] = df_display['Δ Input'].apply(format_delta_numeric)
            df_display['Δ Output'] = df_display['Δ Output'].apply(format_delta_numeric)
            df_display['Δ Tokens'] = df_display['Δ Tokens'].apply(format_delta_numeric)
            df_display['Δ Avg Latency'] = df_display['Δ Avg Latency'].apply(format_delta_numeric)
            df_display['Δ Total Latency'] = df_display['Δ Total Latency'].apply(format_delta_numeric)
            df_display['Δ Attempts'] = df_display['Δ Attempts'].apply(format_delta_numeric)
            df_display['Δ Duration'] = df_display['Δ Duration'].apply(format_delta_numeric)
            df_display['Δ Power'] = df_display['Δ Power'].apply(lambda x: f"🟢 {x:+.1f}" if x < 0 else (f"🔴 {x:+.1f}" if x > 0 else f"{x:.1f}"))
            df_display['Δ Intervals'] = df_display['Δ Intervals'].apply(format_delta_numeric)

            # Display dataframe
            st.dataframe(df_display, use_container_width=True, height=400)

        # Per-Workout Breakdown Section
        st.markdown("---")
        st.header("Per-Workout Breakdown")

        # Collect all per-workout comparisons
        with st.spinner("Loading per-workout comparisons..."):
            all_workout_comparisons = []
            for model_name in available_models:
                model_workouts = load_all_model_workouts(results_folder, model_name)
                comparisons = calculate_per_workout_comparison(gt_workouts, model_workouts, ftp, model_name)
                all_workout_comparisons.extend(comparisons)

        if not all_workout_comparisons:
            st.warning("No per-workout comparison data available")
        else:
            # Create DataFrame
            df_workouts = pd.DataFrame(all_workout_comparisons)

            # Add filters
            col1, col2 = st.columns(2)
            with col1:
                # Model filter
                all_models = sorted(df_workouts['Model'].unique())
                selected_models_filter = st.multiselect(
                    "Filter by Model(s)",
                    options=all_models,
                    default=all_models,
                    help="Select one or more models to display"
                )
            with col2:
                # Workout filter
                all_workouts = sorted(df_workouts['Workout'].unique())
                selected_workouts_filter = st.multiselect(
                    "Filter by Workout(s)",
                    options=all_workouts,
                    default=all_workouts,
                    help="Select one or more workouts to display"
                )

            # Apply filters
            df_filtered = df_workouts[
                (df_workouts['Model'].isin(selected_models_filter)) &
                (df_workouts['Workout'].isin(selected_workouts_filter))
            ]

            if df_filtered.empty:
                st.info("No workouts match the selected filters")
            else:
                # Reorder columns for display
                display_columns = [
                    'Model', 'Workout',
                    'cost', 'delta_cost',
                    'input_tokens', 'delta_input_tokens',
                    'output_tokens', 'delta_output_tokens',
                    'total_tokens', 'delta_total_tokens',
                    'latency_ms', 'delta_latency_ms',
                    'attempts', 'delta_attempts',
                    'duration', 'delta_duration',
                    'avg_power', 'delta_avg_power',
                    'intervals', 'delta_intervals',
                    'validation_passed'
                ]

                df_display_workouts = df_filtered[display_columns].copy()

                # Rename columns for display
                df_display_workouts = df_display_workouts.rename(columns={
                    'Model': 'Model',
                    'Workout': 'Workout',
                    'cost': 'Cost (€)',
                    'delta_cost': 'Δ Cost',
                    'input_tokens': 'Input Tokens',
                    'delta_input_tokens': 'Δ Input',
                    'output_tokens': 'Output Tokens',
                    'delta_output_tokens': 'Δ Output',
                    'total_tokens': 'Total Tokens',
                    'delta_total_tokens': 'Δ Tokens',
                    'latency_ms': 'Latency (ms)',
                    'delta_latency_ms': 'Δ Latency',
                    'attempts': 'Attempts',
                    'delta_attempts': 'Δ Attempts',
                    'duration': 'Duration (s)',
                    'delta_duration': 'Δ Duration',
                    'avg_power': 'Avg Power (W)',
                    'delta_avg_power': 'Δ Power',
                    'intervals': 'Intervals',
                    'delta_intervals': 'Δ Intervals',
                    'validation_passed': 'Valid'
                })

                # Format numeric columns
                df_display_workouts['Cost (€)'] = df_display_workouts['Cost (€)'].apply(lambda x: f"€{x:.4f}")
                df_display_workouts['Latency (ms)'] = df_display_workouts['Latency (ms)'].apply(lambda x: f"{x:.0f}")
                df_display_workouts['Duration (s)'] = df_display_workouts['Duration (s)'].apply(lambda x: f"{x:.0f}")
                df_display_workouts['Avg Power (W)'] = df_display_workouts['Avg Power (W)'].apply(lambda x: f"{x:.1f}")
                df_display_workouts['Valid'] = df_display_workouts['Valid'].apply(lambda x: '✅' if x else '❌')

                # Format delta columns with color indicators
                def format_delta_cost_workout(x):
                    if x < 0:
                        return f"🟢 {x:.4f}"
                    elif x > 0:
                        return f"🔴 {x:+.4f}"
                    else:
                        return f"{x:.4f}"

                def format_delta_numeric_workout(x):
                    if x < 0:
                        return f"🟢 {x:+.0f}"
                    elif x > 0:
                        return f"🔴 {x:+.0f}"
                    else:
                        return f"{x:.0f}"

                df_display_workouts['Δ Cost'] = df_display_workouts['Δ Cost'].apply(format_delta_cost_workout)
                df_display_workouts['Δ Input'] = df_display_workouts['Δ Input'].apply(format_delta_numeric_workout)
                df_display_workouts['Δ Output'] = df_display_workouts['Δ Output'].apply(format_delta_numeric_workout)
                df_display_workouts['Δ Tokens'] = df_display_workouts['Δ Tokens'].apply(format_delta_numeric_workout)
                df_display_workouts['Δ Latency'] = df_display_workouts['Δ Latency'].apply(format_delta_numeric_workout)
                df_display_workouts['Δ Attempts'] = df_display_workouts['Δ Attempts'].apply(format_delta_numeric_workout)
                df_display_workouts['Δ Duration'] = df_display_workouts['Δ Duration'].apply(format_delta_numeric_workout)
                df_display_workouts['Δ Power'] = df_display_workouts['Δ Power'].apply(lambda x: f"🟢 {x:+.1f}" if x < 0 else (f"🔴 {x:+.1f}" if x > 0 else f"{x:.1f}"))
                df_display_workouts['Δ Intervals'] = df_display_workouts['Δ Intervals'].apply(format_delta_numeric_workout)

                # Display dataframe
                st.dataframe(df_display_workouts, use_container_width=True, height=600)

    elif view_mode == "🎯 Structure Quality":
        # STRUCTURE QUALITY TAB
        render_structure_quality_tab(results_folder)

    elif view_mode == "🔄 Model vs Model":
        # MODEL VS MODEL COMPARISON TAB
        render_model_vs_model_tab(ftp, results_folder, selected_workout_desc, workout_options, available_models)

    else:  # Visual Comparison Ground Truth view
        render_visual_comparison_tab(ftp, gt_folder, results_folder, selected_workout_desc, workout_options, selected_model)


if __name__ == "__main__":
    main()
