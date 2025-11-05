#!/usr/bin/env python3
"""
Quick test script to verify visualization data loading functions work correctly.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from visualization_utils import (
    load_all_ground_truth_workouts,
    load_all_model_workouts,
    calculate_aggregate_stats,
    calculate_per_workout_comparison,
    list_available_models,
)

def test_data_loading():
    """Test data loading functionality."""
    print("=" * 60)
    print("Testing Workout Visualization Data Loading")
    print("=" * 60)

    # Test directories
    gt_folder = "ground_truth/run_20251104_155341"
    results_folder = "results/run_20251105_120620"
    ftp = 250

    print(f"\n1. Loading ground truth workouts from: {gt_folder}")
    gt_workouts = load_all_ground_truth_workouts(gt_folder)
    print(f"   ✓ Loaded {len(gt_workouts)} ground truth workouts")
    print(f"   Workout IDs: {', '.join(list(gt_workouts.keys())[:3])}...")

    print(f"\n2. Loading available models")
    models = list_available_models("config/models.yaml", "config/ground_truth.yaml")
    print(f"   ✓ Found {len(models)} models: {', '.join(models)}")

    print(f"\n3. Loading model workouts and calculating aggregate stats")
    for model_name in models:
        print(f"\n   Model: {model_name}")
        model_workouts = load_all_model_workouts(results_folder, model_name)
        print(f"   ✓ Loaded {len(model_workouts)} workouts for {model_name}")

        agg_stats = calculate_aggregate_stats(gt_workouts, model_workouts, ftp)
        if agg_stats:
            print(f"   ✓ Aggregate stats calculated:")
            print(f"      - Success rate: {agg_stats['success_rate']:.1f}%")
            print(f"      - Avg cost: ${agg_stats['avg_cost']:.4f}")
            print(f"      - Avg latency: {agg_stats['avg_latency_ms']:.0f}ms")
            print(f"      - Total tokens: {agg_stats['total_tokens']:,}")
        else:
            print(f"   ✗ No aggregate stats available")

    print(f"\n4. Testing per-workout comparison")
    for model_name in models:
        model_workouts = load_all_model_workouts(results_folder, model_name)
        comparisons = calculate_per_workout_comparison(gt_workouts, model_workouts, ftp, model_name)
        print(f"   ✓ Generated {len(comparisons)} per-workout comparisons for {model_name}")
        if comparisons:
            print(f"      Example workout: {comparisons[0]['Workout']}")
            print(f"      Cost: ${comparisons[0]['cost']:.4f} (Δ {comparisons[0]['delta_cost']:+.4f})")

    print("\n" + "=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_data_loading()
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
