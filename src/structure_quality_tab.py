"""
Structure Quality tab for Streamlit visualizer.

This module provides visualization for structure quality metrics including:
- Composite scores by model
- Component breakdown (zone distribution vs pattern similarity)
- Per-workout heatmaps
- Score distributions
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List
from visualization_utils import (
    load_evaluation_report,
    extract_structure_quality_data,
    get_score_category,
    get_score_color,
)


def render_structure_quality_tab(results_folder: str):
    """
    Render the Structure Quality tab showing comprehensive structure quality metrics.

    Args:
        results_folder: Path to results run directory
    """
    st.header("🎯 Structure Quality Analysis")

    st.markdown("""
    Structure Quality Score measures how well models replicate workout patterns compared to ground truth.
    It combines two key metrics:
    - **Power Zone Distribution** (50%): How accurately the model matches time spent in each power zone
    - **Power Pattern Similarity** (50%): How well the model captures the temporal structure of the workout
    """)

    # Load evaluation report
    with st.spinner("Loading evaluation report..."):
        evaluation_report = load_evaluation_report(results_folder)

    if not evaluation_report:
        st.error("❌ No evaluation report found. Please run the evaluator first:")
        st.code("poetry run python src/evaluator.py results/run_<timestamp> --ground-truth ground_truth/run_<timestamp>")
        return

    # Check if structure quality is available
    if 'structure_quality' not in evaluation_report:
        st.warning("⚠️ Structure quality metrics not available in this evaluation report.")
        st.info("Re-run the evaluator to generate structure quality metrics.")
        return

    # Extract structure quality data
    sq_data = extract_structure_quality_data(evaluation_report)

    if not sq_data:
        st.warning("⚠️ No structure quality data found in evaluation report.")
        return

    # Convert to DataFrame
    df = pd.DataFrame(sq_data)

    # Summary statistics
    sq_summary = evaluation_report.get('structure_quality', {})

    st.markdown("### 📊 Overall Statistics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        avg_score = sq_summary.get('average_composite_score', 0)
        st.metric("Average Score", f"{avg_score:.1f}%")

    with col2:
        excellent_count = sq_summary.get('excellent_count', 0)
        st.metric("Excellent (≥90%)", excellent_count,
                 delta=None,
                 delta_color="normal")

    with col3:
        good_count = sq_summary.get('good_count', 0)
        st.metric("Good (75-89%)", good_count)

    with col4:
        fair_count = sq_summary.get('fair_count', 0)
        poor_count = sq_summary.get('poor_count', 0)
        st.metric("Fair/Poor", f"{fair_count}/{poor_count}")

    # Model comparison charts
    st.markdown("### 📈 Model Comparison")

    # Group by model and calculate averages
    model_stats = df.groupby('model').agg({
        'composite_score': 'mean',
        'zone_distribution_score': 'mean',
        'pattern_similarity_score': 'mean'
    }).reset_index()

    model_stats = model_stats.sort_values('composite_score', ascending=False)

    # Bar chart: Composite scores by model
    fig_composite = go.Figure()

    colors = [get_score_color(score) for score in model_stats['composite_score']]

    fig_composite.add_trace(go.Bar(
        x=model_stats['model'],
        y=model_stats['composite_score'],
        marker=dict(color=colors),
        text=model_stats['composite_score'].round(1),
        textposition='outside',
        texttemplate='%{text}%',
        hovertemplate='<b>%{x}</b><br>Score: %{y:.1f}%<extra></extra>'
    ))

    fig_composite.update_layout(
        title="Average Composite Score by Model",
        xaxis_title="Model",
        yaxis_title="Composite Score (%)",
        yaxis=dict(range=[0, 105]),
        height=400,
        template='plotly_white',
        showlegend=False
    )

    # Add threshold lines
    fig_composite.add_hline(y=90, line_dash="dash", line_color="green",
                           annotation_text="Excellent", annotation_position="right")
    fig_composite.add_hline(y=75, line_dash="dash", line_color="blue",
                           annotation_text="Good", annotation_position="right")
    fig_composite.add_hline(y=60, line_dash="dash", line_color="orange",
                           annotation_text="Fair", annotation_position="right")

    st.plotly_chart(fig_composite, use_container_width=True)

    # Component breakdown
    st.markdown("### 🔍 Component Breakdown")

    col1, col2 = st.columns(2)

    with col1:
        # Zone Distribution scores
        fig_zone = go.Figure()

        fig_zone.add_trace(go.Bar(
            x=model_stats['model'],
            y=model_stats['zone_distribution_score'],
            marker=dict(color='#4169E1'),
            text=model_stats['zone_distribution_score'].round(1),
            textposition='outside',
            texttemplate='%{text}%',
            hovertemplate='<b>%{x}</b><br>Zone Distribution: %{y:.1f}%<extra></extra>'
        ))

        fig_zone.update_layout(
            title="Power Zone Distribution Match",
            xaxis_title="Model",
            yaxis_title="Score (%)",
            yaxis=dict(range=[0, 105]),
            height=350,
            template='plotly_white',
            showlegend=False
        )

        st.plotly_chart(fig_zone, use_container_width=True)

    with col2:
        # Pattern Similarity scores
        fig_pattern = go.Figure()

        fig_pattern.add_trace(go.Bar(
            x=model_stats['model'],
            y=model_stats['pattern_similarity_score'],
            marker=dict(color='#00C851'),
            text=model_stats['pattern_similarity_score'].round(1),
            textposition='outside',
            texttemplate='%{text}%',
            hovertemplate='<b>%{x}</b><br>Pattern Similarity: %{y:.1f}%<extra></extra>'
        ))

        fig_pattern.update_layout(
            title="Power Pattern Similarity",
            xaxis_title="Model",
            yaxis_title="Score (%)",
            yaxis=dict(range=[0, 105]),
            height=350,
            template='plotly_white',
            showlegend=False
        )

        st.plotly_chart(fig_pattern, use_container_width=True)

    # Scatter plot: Zone vs Pattern
    st.markdown("### 🎯 Component Correlation")

    fig_scatter = px.scatter(
        model_stats,
        x='zone_distribution_score',
        y='pattern_similarity_score',
        text='model',
        color='composite_score',
        color_continuous_scale='RdYlGn',
        range_color=[0, 100],
        labels={
            'zone_distribution_score': 'Zone Distribution Score (%)',
            'pattern_similarity_score': 'Pattern Similarity Score (%)',
            'composite_score': 'Composite Score (%)'
        },
        title="Zone Distribution vs Pattern Similarity"
    )

    fig_scatter.update_traces(
        textposition='top center',
        marker=dict(size=12, line=dict(width=1, color='white'))
    )

    fig_scatter.update_layout(
        height=450,
        template='plotly_white'
    )

    st.plotly_chart(fig_scatter, use_container_width=True)

    # Heatmap: Per-workout scores
    st.markdown("### 🗺️ Per-Workout Heatmap")

    st.markdown("This heatmap shows structure quality scores for each workout-model combination. "
               "Darker green indicates better structural similarity to ground truth.")

    # Create pivot table for heatmap
    heatmap_data = df.pivot_table(
        values='composite_score',
        index='prompt_id',
        columns='model',
        aggfunc='mean'
    )

    fig_heatmap = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale='RdYlGn',
        zmin=0,
        zmax=100,
        text=heatmap_data.values.round(1),
        texttemplate='%{text}',
        textfont={"size": 8},
        colorbar=dict(title="Score (%)")
    ))

    # Calculate appropriate height based on number of workouts
    # Ensure at least 25 pixels per row for readability
    min_height_per_row = 25
    calculated_height = max(400, len(heatmap_data) * min_height_per_row)

    fig_heatmap.update_layout(
        title="Structure Quality Scores by Workout and Model",
        xaxis_title="Model",
        yaxis_title="Workout",
        height=calculated_height,
        template='plotly_white',
        yaxis=dict(
            tickmode='linear',  # Show all labels
            tickfont=dict(size=10),  # Adjust font size for readability
            automargin=True  # Auto-adjust margins to fit labels
        ),
        xaxis=dict(
            tickangle=-45,  # Angle model names for better readability
            tickfont=dict(size=10),
            automargin=True
        ),
        margin=dict(l=200, r=50, t=80, b=100)  # Extra left margin for long prompt_ids
    )

    st.plotly_chart(fig_heatmap, use_container_width=True)

    # Score distribution
    st.markdown("### 📊 Score Distribution")

    # Model selector for distribution
    available_models = sorted(df['model'].unique().tolist())
    selected_model_filter = st.selectbox(
        "Filter by Model",
        options=["All Models"] + available_models,
        help="Select a specific model to view its score distribution, or 'All Models' to see overall distribution"
    )

    # Filter dataframe based on selection
    if selected_model_filter == "All Models":
        df_filtered = df.copy()
        title_suffix = "(All Models)"
    else:
        df_filtered = df[df['model'] == selected_model_filter].copy()
        title_suffix = f"({selected_model_filter})"

    col1, col2 = st.columns([2, 1])

    with col1:
        # Histogram
        fig_hist = px.histogram(
            df_filtered,
            x='composite_score',
            nbins=20,
            color_discrete_sequence=['#4169E1'],
            labels={'composite_score': 'Composite Score (%)'},
            title=f"Distribution of Composite Scores {title_suffix}"
        )

        fig_hist.update_layout(
            xaxis_title="Composite Score (%)",
            yaxis_title="Count",
            showlegend=False,
            height=350,
            template='plotly_white'
        )

        # Add vertical lines for thresholds
        fig_hist.add_vline(x=90, line_dash="dash", line_color="green",
                          annotation_text="Excellent")
        fig_hist.add_vline(x=75, line_dash="dash", line_color="blue",
                          annotation_text="Good")
        fig_hist.add_vline(x=60, line_dash="dash", line_color="orange",
                          annotation_text="Fair")

        st.plotly_chart(fig_hist, use_container_width=True)

    with col2:
        # Category breakdown
        df_filtered['category'] = df_filtered['composite_score'].apply(get_score_category)
        category_counts = df_filtered['category'].value_counts()

        # Reorder categories in intuitive order: Excellent, Good, Fair, Poor
        category_order = ['Excellent', 'Good', 'Fair', 'Poor']
        ordered_categories = [cat for cat in category_order if cat in category_counts.index]
        ordered_values = [category_counts[cat] for cat in ordered_categories]

        fig_pie = px.pie(
            values=ordered_values,
            names=ordered_categories,
            color=ordered_categories,
            color_discrete_map={
                'Excellent': '#00C851',
                'Good': '#4169E1',
                'Fair': '#FFD700',
                'Poor': '#FF0000'
            },
            title=f"Score Categories {title_suffix}"
        )

        fig_pie.update_layout(
            height=350,
            showlegend=True
        )

        st.plotly_chart(fig_pie, use_container_width=True)

    # Show statistics for filtered data
    if len(df_filtered) > 0:
        st.markdown(f"**Statistics for {selected_model_filter}:**")
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)

        with col_stat1:
            st.metric("Total Workouts", len(df_filtered))

        with col_stat2:
            avg_score = df_filtered['composite_score'].mean()
            st.metric("Average Score", f"{avg_score:.1f}%")

        with col_stat3:
            median_score = df_filtered['composite_score'].median()
            st.metric("Median Score", f"{median_score:.1f}%")

        with col_stat4:
            std_score = df_filtered['composite_score'].std()
            st.metric("Std Deviation", f"{std_score:.1f}%")

    # Detailed data table
    st.markdown("### 📋 Detailed Scores")

    # Prepare display dataframe
    df_display = df.copy()
    df_display['Category'] = df_display['composite_score'].apply(get_score_category)
    df_display = df_display[[
        'model', 'prompt_id', 'composite_score',
        'zone_distribution_score', 'pattern_similarity_score', 'Category'
    ]]

    df_display.columns = [
        'Model', 'Workout', 'Composite Score (%)',
        'Zone Dist. (%)', 'Pattern Sim. (%)', 'Category'
    ]

    df_display = df_display.sort_values('Composite Score (%)', ascending=False)

    # Apply styling
    def color_category(val):
        if val == 'Excellent':
            return 'background-color: #00C851; color: white'
        elif val == 'Good':
            return 'background-color: #4169E1; color: white'
        elif val == 'Fair':
            return 'background-color: #FFD700; color: black'
        else:
            return 'background-color: #FF0000; color: white'

    styled_df = df_display.style.applymap(color_category, subset=['Category'])

    st.dataframe(styled_df, use_container_width=True, height=400)

    # Export option
    st.markdown("### 💾 Export Data")

    csv = df_display.to_csv(index=False)
    st.download_button(
        label="Download as CSV",
        data=csv,
        file_name=f"structure_quality_scores_{results_folder.split('/')[-1]}.csv",
        mime="text/csv"
    )
