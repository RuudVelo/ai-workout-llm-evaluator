"""
Test script to demonstrate the postprocessing layer's effectiveness.

This shows how common LLM errors are automatically fixed without retries.
"""

import sys
import json
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from postprocessor import WorkoutPostprocessor
from evaluator import WorkoutEvaluator


# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def test_postprocessing():
    """Test the postprocessing layer with a sample workout containing common errors."""

    ftp = 250

    # Sample workout with MULTIPLE common errors that would trigger retries:
    # 1. Wrong FTP percentages (should be 40%, 80%, 100% but set incorrectly)
    # 2. Wrong power adjustments (should be ±10W)
    # 3. Wrong zones (100W should be zone 1, 200W should be zone 2, 250W should be zone 4)
    # 4. Wrong duration (says 900 but should be 600)
    # 5. Invalid segment type "tempo" (should be "interval")
    buggy_workout = {
        "name": "Test Workout",
        "description": "A workout with intentional errors",
        "workout_duration": 900,  # WRONG! Should be 600
        "intervals": [
            {
                "segment_number": 1,
                "startTimeSeconds": 0,
                "endTimeSeconds": 300,
                "power": 100,
                "powerAdjustedUpward": 115,  # WRONG! Should be 110
                "powerAdjustedDownward": 85,  # WRONG! Should be 90
                "zone": 2,  # WRONG! 100W at FTP=250 should be zone 1
                "perc_ftp": 50,  # WRONG! Should be 40%
                "type": "warmup",
                "notes": "Easy warmup"
            },
            {
                "segment_number": 2,
                "startTimeSeconds": 300,
                "endTimeSeconds": 450,
                "power": 200,
                "powerAdjustedUpward": 220,  # WRONG! Should be 210
                "powerAdjustedDownward": 180,  # WRONG! Should be 190
                "zone": 3,  # WRONG! 200W at FTP=250 should be zone 2
                "perc_ftp": 75,  # WRONG! Should be 80%
                "type": "tempo",  # WRONG! Invalid type, should be "interval"
                "notes": "Tempo effort"
            },
            {
                "segment_number": 3,
                "startTimeSeconds": 450,
                "endTimeSeconds": 600,
                "power": 250,
                "powerAdjustedUpward": 265,  # WRONG! Should be 260
                "powerAdjustedDownward": 235,  # WRONG! Should be 240
                "zone": 5,  # WRONG! 250W at FTP=250 should be zone 4
                "perc_ftp": 95,  # WRONG! Should be 100%
                "type": "interval",
                "notes": "Threshold effort"
            }
        ]
    }

    logger.info("=" * 80)
    logger.info("POSTPROCESSING TEST - Demonstrating Auto-Fix Capabilities")
    logger.info("=" * 80)
    logger.info(f"\nFTP: {ftp}W\n")

    # Validate BEFORE postprocessing
    logger.info("BEFORE POSTPROCESSING:")
    logger.info("-" * 80)
    evaluator_before = WorkoutEvaluator(ftp)
    evaluation_before = evaluator_before.evaluate(buggy_workout)

    logger.info(f"Validation Result: {evaluation_before['overall_score']}")
    logger.info(f"Pass Rate: {evaluation_before['pass_rate']}%")
    logger.info(f"All Passed: {evaluation_before['all_passed']}")

    # Show failed metrics
    failed_metrics = [m for m in evaluation_before['metrics'] if not m.get('passed', False)]
    if failed_metrics:
        logger.info("\nFailed Validations:")
        for metric in failed_metrics:
            logger.info(f"  ❌ {metric['metric']}")
            if 'mismatches' in metric and metric['mismatches']:
                for mismatch in metric['mismatches'][:3]:  # Show first 3
                    logger.info(f"     {mismatch}")

    logger.info("\n" + "=" * 80)
    logger.info("APPLYING POSTPROCESSING...")
    logger.info("=" * 80 + "\n")

    # Apply postprocessing (need a deep copy to preserve original)
    import copy
    postprocessor = WorkoutPostprocessor(ftp, logger)
    fixed_workout = postprocessor.postprocess(copy.deepcopy(buggy_workout))

    # Validate AFTER postprocessing
    logger.info("\n" + "=" * 80)
    logger.info("AFTER POSTPROCESSING:")
    logger.info("-" * 80)
    evaluator_after = WorkoutEvaluator(ftp)
    evaluation_after = evaluator_after.evaluate(fixed_workout)

    logger.info(f"Validation Result: {evaluation_after['overall_score']}")
    logger.info(f"Pass Rate: {evaluation_after['pass_rate']}%")
    logger.info(f"All Passed: {evaluation_after['all_passed']}")

    # Show improvements
    logger.info("\n" + "=" * 80)
    logger.info("SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Pass Rate Improvement: {evaluation_before['pass_rate']}% → {evaluation_after['pass_rate']}%")
    logger.info(f"Fixes Applied: {', '.join(postprocessor.get_fixes_summary())}")

    if evaluation_after['all_passed']:
        logger.info("\n✅ SUCCESS! All validations now pass.")
        logger.info("💰 This workout would have required 0 retries instead of potentially 3!")
        logger.info("📉 Cost savings: ~$0.03-0.10 per workout (depending on model)")
    else:
        logger.info("\n⚠️  Some validations still fail (would require LLM retry)")
        failed_after = [m for m in evaluation_after['metrics'] if not m.get('passed', False)]
        logger.info("Remaining issues:")
        for metric in failed_after:
            logger.info(f"  ❌ {metric['metric']}")

    logger.info("\n" + "=" * 80)

    # Show specific field changes
    logger.info("\nDETAILED FIELD CHANGES:")
    logger.info("-" * 80)
    logger.info(f"workout_duration: {buggy_workout['workout_duration']} → {fixed_workout['workout_duration']}")

    for i, (before_int, after_int) in enumerate(zip(buggy_workout['intervals'], fixed_workout['intervals'])):
        logger.info(f"\nInterval {i+1} ({before_int['power']}W):")
        if before_int['perc_ftp'] != after_int['perc_ftp']:
            logger.info(f"  perc_ftp: {before_int['perc_ftp']}% → {after_int['perc_ftp']}%")
        if before_int['zone'] != after_int['zone']:
            logger.info(f"  zone: {before_int['zone']} → {after_int['zone']}")
        if before_int['powerAdjustedUpward'] != after_int['powerAdjustedUpward']:
            logger.info(f"  powerAdjustedUpward: {before_int['powerAdjustedUpward']}W → {after_int['powerAdjustedUpward']}W")
        if before_int['powerAdjustedDownward'] != after_int['powerAdjustedDownward']:
            logger.info(f"  powerAdjustedDownward: {before_int['powerAdjustedDownward']}W → {after_int['powerAdjustedDownward']}W")
        if before_int['type'] != after_int['type']:
            logger.info(f"  type: '{before_int['type']}' → '{after_int['type']}'")

    logger.info("\n" + "=" * 80)


if __name__ == "__main__":
    test_postprocessing()
