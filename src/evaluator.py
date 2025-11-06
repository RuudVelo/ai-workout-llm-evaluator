"""
Evaluation metrics for workout generation quality.
"""

import json
from typing import Dict, Any
from pathlib import Path
from jsonschema import validate, ValidationError

from system_prompt import WORKOUT_JSON_SCHEMA, calculate_zones


class WorkoutEvaluator:
    """Evaluates generated workouts against validation rules."""

    def __init__(self, ftp: int):
        self.ftp = ftp
        self.zones = calculate_zones(ftp)

    def validate_schema(self, workout: Dict[str, Any]) -> Dict[str, Any]:
        """Validate workout matches the expected JSON schema."""
        result = {
            "metric": "schema_validation",
            "passed": False,
            "errors": [],
        }

        try:
            # Extract just the schema part for validation
            schema = WORKOUT_JSON_SCHEMA["schema"]
            validate(instance=workout, schema=schema)
            result["passed"] = True
        except ValidationError as e:
            result["errors"].append(str(e.message))
        except Exception as e:
            result["errors"].append(f"Validation error: {str(e)}")

        return result

    def validate_required_fields(self, workout: Dict[str, Any]) -> Dict[str, Any]:
        """Check all required fields are present."""
        result = {
            "metric": "required_fields",
            "passed": True,
            "missing_fields": [],
        }

        required_top_level = [
            "name",
            "description",
            "workout_duration",
            "intervals",
        ]
        for field in required_top_level:
            if field not in workout:
                result["missing_fields"].append(field)
                result["passed"] = False

        # Check interval fields
        if "intervals" in workout:
            required_interval_fields = [
                "segment_number",
                "startTimeSeconds",
                "endTimeSeconds",
                "power",
                "powerAdjustedUpward",
                "powerAdjustedDownward",
                "zone",
                "perc_ftp",
                "type",
                "notes",
            ]

            for idx, interval in enumerate(workout["intervals"]):
                for field in required_interval_fields:
                    if field not in interval:
                        result["missing_fields"].append(f"intervals[{idx}].{field}")
                        result["passed"] = False

        return result

    def validate_duration_consistency(self, workout: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that total duration matches sum of intervals."""
        result = {
            "metric": "duration_consistency",
            "passed": False,
            "declared_duration": None,
            "calculated_duration": None,
            "difference": None,
        }

        if "workout_duration" not in workout or "intervals" not in workout:
            result["errors"] = ["Missing workout_duration or intervals"]
            return result

        declared_duration = workout["workout_duration"]
        result["declared_duration"] = declared_duration

        # Calculate from intervals
        if workout["intervals"]:
            last_interval = workout["intervals"][-1]
            calculated_duration = last_interval.get("endTimeSeconds", 0)
            result["calculated_duration"] = calculated_duration

            difference = abs(declared_duration - calculated_duration)
            result["difference"] = difference

            # Use percentage-based tolerance (0.1%) with minimum of 2 seconds
            # This is more appropriate for workouts of different lengths
            tolerance = max(2, declared_duration * 0.001)  # 0.1% = 0.001
            result["passed"] = difference <= tolerance
        else:
            result["errors"] = ["No intervals found"]

        return result

    def validate_time_continuity(self, workout: Dict[str, Any]) -> Dict[str, Any]:
        """Validate no gaps or overlaps between intervals."""
        result = {
            "metric": "time_continuity",
            "passed": True,
            "gaps": [],
            "overlaps": [],
        }

        if "intervals" not in workout or not workout["intervals"]:
            result["passed"] = False
            result["errors"] = ["No intervals"]
            return result

        intervals = sorted(workout["intervals"], key=lambda x: x["startTimeSeconds"])

        # Check first interval starts at 0
        if intervals[0]["startTimeSeconds"] != 0:
            result["gaps"].append(
                {
                    "type": "start_gap",
                    "expected": 0,
                    "actual": intervals[0]["startTimeSeconds"],
                }
            )
            result["passed"] = False

        # Check continuity between intervals
        for i in range(len(intervals) - 1):
            current_end = intervals[i]["endTimeSeconds"]
            next_start = intervals[i + 1]["startTimeSeconds"]

            if current_end < next_start:
                result["gaps"].append(
                    {
                        "between_segments": [
                            intervals[i]["segment_number"],
                            intervals[i + 1]["segment_number"],
                        ],
                        "gap_seconds": next_start - current_end,
                    }
                )
                result["passed"] = False
            elif current_end > next_start:
                result["overlaps"].append(
                    {
                        "between_segments": [
                            intervals[i]["segment_number"],
                            intervals[i + 1]["segment_number"],
                        ],
                        "overlap_seconds": current_end - next_start,
                    }
                )
                result["passed"] = False

        return result

    def validate_power_zones(self, workout: Dict[str, Any]) -> Dict[str, Any]:
        """Validate power values match declared zones."""
        result = {
            "metric": "power_zone_accuracy",
            "passed": True,
            "mismatches": [],
        }

        if "intervals" not in workout:
            return result

        for interval in workout["intervals"]:
            power = interval.get("power", 0)
            declared_zone = interval.get("zone")

            # Determine actual zone with boundary tolerance
            # Allow 2W grace at zone boundaries to handle rounding
            actual_zone = None
            tolerance = 2  # watts

            for zone_num in range(1, 8):
                zone_key = f"z{zone_num}"
                zone_range = self.zones[zone_key]
                # Expand boundaries slightly for tolerance
                if (
                    (zone_range["min"] - tolerance)
                    <= power
                    <= (zone_range["max"] + tolerance)
                ):
                    actual_zone = zone_num
                    break

            # If declared zone is valid and within tolerance, accept it
            if declared_zone and 1 <= declared_zone <= 7:
                zone_key = f"z{declared_zone}"
                zone_range = self.zones[zone_key]
                # Check if power is within tolerance of declared zone
                if (
                    (zone_range["min"] - tolerance)
                    <= power
                    <= (zone_range["max"] + tolerance)
                ):
                    # Accept the declared zone even if actual_zone differs
                    continue

            # Only flag as mismatch if power clearly doesn't match declared zone
            if actual_zone != declared_zone:
                result["mismatches"].append(
                    {
                        "segment_number": interval.get("segment_number"),
                        "power": power,
                        "declared_zone": declared_zone,
                        "actual_zone": actual_zone,
                    }
                )
                result["passed"] = False

        return result

    def validate_ftp_percentages(self, workout: Dict[str, Any]) -> Dict[str, Any]:
        """Validate perc_ftp calculations are correct."""
        result = {
            "metric": "ftp_percentage_accuracy",
            "passed": True,
            "mismatches": [],
        }

        if "intervals" not in workout:
            return result

        for interval in workout["intervals"]:
            power = interval.get("power", 0)
            declared_perc = interval.get("perc_ftp")

            # Calculate actual percentage (rounded)
            actual_perc = round((power / self.ftp) * 100)

            # Allow ±1% tolerance to account for rounding differences
            # (Python's banker's rounding vs standard rounding)
            if abs(actual_perc - declared_perc) > 1:
                result["mismatches"].append(
                    {
                        "segment_number": interval.get("segment_number"),
                        "power": power,
                        "declared_perc_ftp": declared_perc,
                        "calculated_perc_ftp": actual_perc,
                        "difference": abs(actual_perc - declared_perc),
                    }
                )
                result["passed"] = False

        return result

    def validate_power_adjustments(self, workout: Dict[str, Any]) -> Dict[str, Any]:
        """Validate powerAdjustedUpward and powerAdjustedDownward."""
        result = {
            "metric": "power_adjustment_accuracy",
            "passed": True,
            "mismatches": [],
        }

        if "intervals" not in workout:
            return result

        for interval in workout["intervals"]:
            power = interval.get("power", 0)
            upward = interval.get("powerAdjustedUpward")
            downward = interval.get("powerAdjustedDownward")

            expected_upward = power + 10
            expected_downward = max(0, power - 10)

            # Allow ±2W tolerance for power adjustments
            # These are derived fields and minor variations are acceptable
            tolerance = 2

            upward_diff = (
                abs(upward - expected_upward) if upward is not None else float("inf")
            )
            downward_diff = (
                abs(downward - expected_downward)
                if downward is not None
                else float("inf")
            )

            if upward_diff > tolerance or downward_diff > tolerance:
                result["mismatches"].append(
                    {
                        "segment_number": interval.get("segment_number"),
                        "power": power,
                        "upward": {
                            "expected": expected_upward,
                            "actual": upward,
                            "difference": upward_diff if upward is not None else None,
                        },
                        "downward": {
                            "expected": expected_downward,
                            "actual": downward,
                            "difference": (
                                downward_diff if downward is not None else None
                            ),
                        },
                    }
                )
                result["passed"] = False

        return result

    def validate_segment_types(self, workout: Dict[str, Any]) -> Dict[str, Any]:
        """Validate segment types use only allowed enum values."""
        result = {
            "metric": "segment_type_validity",
            "passed": True,
            "invalid_types": [],
        }

        allowed_types = {
            "active",
            "rest",
            "warmup",
            "cooldown",
            "recovery",
            "interval",
            "other",
        }

        if "intervals" not in workout:
            return result

        for interval in workout["intervals"]:
            segment_type = interval.get("type")
            if segment_type not in allowed_types:
                result["invalid_types"].append(
                    {
                        "segment_number": interval.get("segment_number"),
                        "invalid_type": segment_type,
                    }
                )
                result["passed"] = False

        return result

    def evaluate(self, workout: Dict[str, Any]) -> Dict[str, Any]:
        """Run all validation metrics on a workout."""
        metrics = [
            self.validate_schema(workout),
            self.validate_required_fields(workout),
            self.validate_duration_consistency(workout),
            self.validate_time_continuity(workout),
            self.validate_power_zones(workout),
            self.validate_ftp_percentages(workout),
            self.validate_power_adjustments(workout),
            self.validate_segment_types(workout),
        ]

        passed_count = sum(1 for m in metrics if m.get("passed", False))
        total_count = len(metrics)

        return {
            "overall_score": f"{passed_count}/{total_count}",
            "pass_rate": round((passed_count / total_count) * 100, 2),
            "all_passed": passed_count == total_count,
            "metrics": metrics,
        }


def evaluate_result_file(
    result_path: Path, ftp: int, ground_truth_dir: Path = None
) -> Dict[str, Any]:
    """Evaluate a single result file."""
    with open(result_path, "r") as f:
        result = json.load(f)

    if not result.get("success", False):
        return {
            "result_file": result_path.name,
            "evaluation_skipped": True,
            "reason": "Generation failed or parse error",
        }

    workout = result["response"]["parsed_json"]
    evaluator = WorkoutEvaluator(ftp)
    evaluation = evaluator.evaluate(workout)

    eval_result = {
        "result_file": result_path.name,
        "prompt_id": result["prompt_id"],
        "model": result["model"]["display_name"],
        **evaluation,
    }

    # Add ground truth comparison if available
    if ground_truth_dir:
        prompt_id = result["prompt_id"]
        gt_file = ground_truth_dir / f"{prompt_id}.json"

        if gt_file.exists():
            from comparison_metrics import compare_to_ground_truth
            from structure_quality_metrics import evaluate_structure_quality

            with open(gt_file, "r") as f:
                ground_truth = json.load(f)

            comparison = compare_to_ground_truth(ground_truth["workout"], workout)
            eval_result["ground_truth_comparison"] = comparison

            # Add structure quality scoring
            structure_quality = evaluate_structure_quality(
                ground_truth["workout"], workout
            )
            eval_result["structure_quality"] = structure_quality
        else:
            eval_result["ground_truth_comparison"] = {
                "available": False,
                "reason": f"No ground truth file found: {gt_file.name}",
            }
            eval_result["structure_quality"] = {
                "available": False,
                "reason": f"No ground truth file found: {gt_file.name}",
            }

    return eval_result


def evaluate_run_directory(
    run_dir: Path, ground_truth_dir: Path = None
) -> Dict[str, Any]:
    """Evaluate all result files in a run directory."""
    run_dir = Path(run_dir)

    if ground_truth_dir:
        ground_truth_dir = Path(ground_truth_dir)

    # Load summary to get FTP
    with open(run_dir / "summary.json", "r") as f:
        summary = json.load(f)

    ftp = summary["ftp"]

    # Evaluate each result file
    evaluations = []
    for result_file in run_dir.glob("*.json"):
        if result_file.name == "summary.json" or result_file.name.startswith(
            "evaluation_"
        ):
            continue

        evaluation = evaluate_result_file(result_file, ftp, ground_truth_dir)
        evaluations.append(evaluation)

    # Calculate aggregate metrics
    valid_evals = [e for e in evaluations if not e.get("evaluation_skipped", False)]

    # Calculate ground truth metrics if available
    gt_comparisons = [
        e.get("ground_truth_comparison")
        for e in valid_evals
        if e.get("ground_truth_comparison", {}).get("all_passed") is not None
    ]

    # Calculate structure quality metrics if available
    structure_quality_scores = [
        e.get("structure_quality")
        for e in valid_evals
        if e.get("structure_quality", {}).get("composite_score") is not None
    ]

    aggregate = {
        "run_directory": str(run_dir),
        "total_results": len(evaluations),
        "evaluated": len(valid_evals),
        "skipped": len(evaluations) - len(valid_evals),
        "validation": {
            "all_passed_count": sum(
                1 for e in valid_evals if e.get("all_passed", False)
            ),
            "average_pass_rate": (
                round(
                    sum(e.get("pass_rate", 0) for e in valid_evals) / len(valid_evals),
                    2,
                )
                if valid_evals
                else 0
            ),
        },
        "evaluations": evaluations,
    }

    # Add ground truth comparison summary
    if gt_comparisons:
        aggregate["ground_truth_comparison"] = {
            "available": len(gt_comparisons),
            "all_passed_count": sum(
                1 for c in gt_comparisons if c.get("all_passed", False)
            ),
            "average_similarity": (
                round(
                    sum(c.get("similarity_percentage", 0) for c in gt_comparisons)
                    / len(gt_comparisons),
                    2,
                )
                if gt_comparisons
                else 0
            ),
        }

    # Add structure quality summary
    if structure_quality_scores:
        # Filter out None scores for average calculation
        valid_scores = [
            sq.get("composite_score", 0)
            for sq in structure_quality_scores
            if sq.get("composite_score") is not None
        ]

        aggregate["structure_quality"] = {
            "available": len(structure_quality_scores),
            "valid_scores": len(valid_scores),
            "average_composite_score": (
                round(sum(valid_scores) / len(valid_scores), 2)
                if valid_scores
                else 0
            ),
            "excellent_count": sum(
                1
                for sq in structure_quality_scores
                if sq.get("composite_score") is not None
                and sq.get("composite_score", 0) >= 90
            ),
            "good_count": sum(
                1
                for sq in structure_quality_scores
                if sq.get("composite_score") is not None
                and 75 <= sq.get("composite_score", 0) < 90
            ),
            "fair_count": sum(
                1
                for sq in structure_quality_scores
                if sq.get("composite_score") is not None
                and 60 <= sq.get("composite_score", 0) < 75
            ),
            "poor_count": sum(
                1
                for sq in structure_quality_scores
                if sq.get("composite_score") is not None
                and sq.get("composite_score", 0) < 60
            ),
        }

    # Save evaluation report
    eval_report_path = run_dir / "evaluation_report.json"
    with open(eval_report_path, "w") as f:
        json.dump(aggregate, f, indent=2)

    print("\nEvaluation Report:")
    print(f"  Total results: {aggregate['total_results']}")
    print(f"  Evaluated: {aggregate['evaluated']}")
    print(
        f"  Validation - All metrics passed: {aggregate['validation']['all_passed_count']}/{aggregate['evaluated']}"
    )
    print(
        f"  Validation - Average pass rate: {aggregate['validation']['average_pass_rate']}%"
    )

    if "ground_truth_comparison" in aggregate:
        gt_summary = aggregate["ground_truth_comparison"]
        print("\n  Ground Truth Comparison:")
        print(f"    Available: {gt_summary['available']}")
        print(
            f"    Perfect matches: {gt_summary['all_passed_count']}/{gt_summary['available']}"
        )
        print(f"    Average similarity: {gt_summary['average_similarity']}%")

    if "structure_quality" in aggregate:
        sq_summary = aggregate["structure_quality"]
        print("\n  Structure Quality Scoring:")
        print(f"    Available: {sq_summary['available']}")
        print(f"    Average composite score: {sq_summary['average_composite_score']}%")
        print(
            f"    Distribution: Excellent={sq_summary['excellent_count']}, "
            f"Good={sq_summary['good_count']}, Fair={sq_summary['fair_count']}, "
            f"Poor={sq_summary['poor_count']}"
        )

    print(f"\nReport saved to: {eval_report_path}")

    return aggregate


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate workout generation results")
    parser.add_argument(
        "run_directory",
        type=str,
        help="Path to the run directory containing results",
    )
    parser.add_argument(
        "--ground-truth",
        type=str,
        default="ground_truth",
        help="Path to ground truth directory (default: ground_truth)",
    )
    parser.add_argument(
        "--no-ground-truth",
        action="store_true",
        help="Skip ground truth comparison",
    )

    args = parser.parse_args()

    run_dir = Path(args.run_directory)
    ground_truth_dir = None if args.no_ground_truth else Path(args.ground_truth)

    evaluate_run_directory(run_dir, ground_truth_dir)
