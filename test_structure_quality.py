"""
Quick test of structure quality metrics.
"""

import json
from pathlib import Path
from src.structure_quality_metrics import evaluate_structure_quality

# Load a ground truth workout
gt_dir = Path("ground_truth/run_20251105_151109")
gt_file = gt_dir / "simple_threshold_60min.json"

if gt_file.exists():
    with open(gt_file, "r") as f:
        gt_data = json.load(f)

    gt_workout = gt_data["workout"]

    # Test with itself (should get perfect score)
    print("Testing structure quality metrics...")
    print("=" * 60)

    result = evaluate_structure_quality(gt_workout, gt_workout)

    print(json.dumps(result, indent=2))
    print("=" * 60)

    if result.get("enabled"):
        score = result.get("composite_score", 0)
        print(f"\n✓ Structure Quality Score: {score}%")

        components = result.get("components", {})
        zone_match = components.get("power_zone_distribution_match", {})
        pattern_sim = components.get("power_pattern_similarity", {})

        print(f"  - Power Zone Distribution: {zone_match.get('score', 0) * 100:.2f}%")
        print(f"  - Power Pattern Similarity: {pattern_sim.get('score', 0) * 100:.2f}%")

        if score >= 90:
            print("\n✓ EXCELLENT - Score >= 90%")
        elif score >= 75:
            print("\n✓ GOOD - Score >= 75%")
        elif score >= 60:
            print("\n⚠ FAIR - Score >= 60%")
        else:
            print("\n✗ POOR - Score < 60%")
    else:
        print("Structure quality scoring is disabled or failed")

else:
    print(f"Ground truth file not found: {gt_file}")
