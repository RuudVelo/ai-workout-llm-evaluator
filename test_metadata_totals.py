#!/usr/bin/env python3
"""
Test script to verify that metadata totals are being calculated correctly.
This creates a mock scenario to test the logic without calling real APIs.
"""

import json
from pathlib import Path


def verify_ground_truth_metadata():
    """Verify that existing ground truth files have the expected metadata structure."""

    print("=" * 80)
    print("Verifying Ground Truth Metadata Structure")
    print("=" * 80)

    ground_truth_dir = Path("ground_truth")

    # Check one example file
    test_file = ground_truth_dir / "climbing_intervals_wattage.json"

    if not test_file.exists():
        print(f"✗ Test file not found: {test_file}")
        return False

    with open(test_file, "r") as f:
        data = json.load(f)

    metadata = data.get("generation_metadata", {})

    print(f"\nChecking: {test_file.name}")
    print(f"Attempts: {metadata.get('attempts', 'N/A')}")

    # Check for new fields (these won't exist in old files)
    expected_new_fields = [
        "total_latency_all_attempts",
        "total_tokens_all_attempts",
        "total_input_cost_all_attempts",
        "total_output_cost_all_attempts"
    ]

    missing_fields = []
    for field in expected_new_fields:
        if field in metadata:
            print(f"✓ Found: {field} = {metadata[field]}")
        else:
            missing_fields.append(field)
            print(f"⚠ Missing: {field} (expected in new files)")

    # Verify existing structure
    print(f"\n✓ Field 'total_cost_all_attempts': {metadata.get('total_cost_all_attempts', 'N/A')}")

    # Show last attempt cost from all_attempts array
    if all_attempts := metadata.get("all_attempts", []):
        last_attempt_cost = all_attempts[-1].get("cost", "N/A")
        print(f"✓ Last attempt cost (from all_attempts): {last_attempt_cost}")

    # Verify all_attempts structure
    all_attempts = metadata.get("all_attempts", [])
    print(f"\n✓ Found {len(all_attempts)} attempts in metadata")

    if all_attempts:
        first_attempt = all_attempts[0]
        print(f"\nFirst attempt structure:")
        for key, value in first_attempt.items():
            print(f"  - {key}: {value}")

    # Calculate expected totals manually to verify logic
    if all_attempts and metadata.get('attempts', 0) > 1:
        print("\n" + "=" * 80)
        print("Manual Verification of Totals (from existing data)")
        print("=" * 80)

        total_latency = sum(a.get('latency_ms', 0) for a in all_attempts)
        total_cost = sum(a.get('cost', 0) for a in all_attempts)
        total_input_tokens = sum(a.get('tokens', {}).get('input', 0) for a in all_attempts)
        total_output_tokens = sum(a.get('tokens', {}).get('output', 0) for a in all_attempts)

        print(f"\nCalculated from all_attempts array:")
        print(f"  Total latency: {total_latency}ms")
        print(f"  Total cost: ${total_cost:.6f}")
        print(f"  Total input tokens: {total_input_tokens}")
        print(f"  Total output tokens: {total_output_tokens}")
        print(f"  Total tokens: {total_input_tokens + total_output_tokens}")

        print(f"\nStored in metadata:")
        print(f"  total_cost_all_attempts: ${metadata.get('total_cost_all_attempts', 0):.6f}")

        # Verify consistency
        stored_cost = metadata.get('total_cost_all_attempts', 0)
        if abs(stored_cost - total_cost) < 0.000001:
            print(f"✓ Cost totals match!")
        else:
            print(f"✗ Cost mismatch: stored={stored_cost}, calculated={total_cost}")

    print("\n" + "=" * 80)
    if missing_fields:
        print("⚠ New fields will appear after regenerating ground truth files")
        print("  Run: python3 src/ground_truth_generator.py generate --prompts simple_tempo_block --force")
    else:
        print("✓ All expected fields present!")
    print("=" * 80)

    return True


def show_expected_structure():
    """Show what the new metadata structure should look like."""

    print("\n" + "=" * 80)
    print("Expected Metadata Structure (New)")
    print("=" * 80)

    example = {
        "generation_metadata": {
            "attempts": 3,
            "total_latency_all_attempts": 42402,  # Sum of all attempts
            "total_tokens_all_attempts": {  # Sum of all attempts
                "input": 3018,
                "output": 2490,
                "total": 5508
            },
            "total_cost_all_attempts": 0.028242,  # Sum of all attempts
            "total_input_cost_all_attempts": 0.006579,  # Sum of all attempts
            "total_output_cost_all_attempts": 0.021663,  # Sum of all attempts
            "all_attempts": [
                {
                    "attempt": 1,
                    "latency_ms": 14331,
                    "tokens": {"input": 1006, "output": 892, "total": 1898},
                    "cost": 0.009953,
                    "input_cost": 0.002193,
                    "output_cost": 0.007760
                },
                {
                    "attempt": 2,
                    "latency_ms": 12149,
                    "tokens": {"input": 1006, "output": 825, "total": 1831},
                    "cost": 0.008371,
                    "input_cost": 0.002193,
                    "output_cost": 0.006178
                },
                {
                    "attempt": 3,
                    "latency_ms": 15922,
                    "tokens": {"input": 1006, "output": 773, "total": 1779},
                    "cost": 0.009918,
                    "input_cost": 0.002193,
                    "output_cost": 0.006725
                }
            ]
        }
    }

    print(json.dumps(example, indent=2))
    print("\n" + "=" * 80)


if __name__ == "__main__":
    show_expected_structure()
    verify_ground_truth_metadata()
