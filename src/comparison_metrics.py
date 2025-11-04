"""
Comparison metrics for evaluating generated workouts against ground truth.
"""

from typing import Dict, Any, List
import json


class WorkoutComparator:
    """Compares generated workouts to ground truth references."""

    def __init__(self, ground_truth: Dict[str, Any], generated: Dict[str, Any]):
        self.gt = ground_truth
        self.gen = generated

    def compare_duration(self) -> Dict[str, Any]:
        """Compare total workout duration."""
        gt_duration = self.gt.get("workout_duration", 0)
        gen_duration = self.gen.get("workout_duration", 0)

        difference = abs(gt_duration - gen_duration)
        tolerance_seconds = 60  # 1 minute tolerance

        return {
            "metric": "duration_comparison",
            "ground_truth_seconds": gt_duration,
            "generated_seconds": gen_duration,
            "difference_seconds": difference,
            "passed": difference <= tolerance_seconds,
            "tolerance_seconds": tolerance_seconds,
        }

    def compare_interval_count(self) -> Dict[str, Any]:
        """Compare number of intervals."""
        gt_count = len(self.gt.get("intervals", []))
        gen_count = len(self.gen.get("intervals", []))

        # Allow some flexibility - workouts can be structured differently
        # but should be within reasonable bounds
        tolerance_percentage = 0.3  # 30% tolerance
        min_acceptable = int(gt_count * (1 - tolerance_percentage))
        max_acceptable = int(gt_count * (1 + tolerance_percentage))

        passed = min_acceptable <= gen_count <= max_acceptable

        return {
            "metric": "interval_count_comparison",
            "ground_truth_count": gt_count,
            "generated_count": gen_count,
            "difference": abs(gt_count - gen_count),
            "acceptable_range": [min_acceptable, max_acceptable],
            "passed": passed,
        }

    def compare_segment_types(self) -> Dict[str, Any]:
        """Compare segment type distribution."""
        gt_intervals = self.gt.get("intervals", [])
        gen_intervals = self.gen.get("intervals", [])

        # Count segment types
        gt_types = {}
        gen_types = {}

        for interval in gt_intervals:
            seg_type = interval.get("type", "unknown")
            gt_types[seg_type] = gt_types.get(seg_type, 0) + 1

        for interval in gen_intervals:
            seg_type = interval.get("type", "unknown")
            gen_types[seg_type] = gen_types.get(seg_type, 0) + 1

        # Check if critical types are present
        critical_types = ["warmup", "cooldown"]
        missing_critical = []

        for ctype in critical_types:
            if gt_types.get(ctype, 0) > 0 and gen_types.get(ctype, 0) == 0:
                missing_critical.append(ctype)

        return {
            "metric": "segment_type_distribution",
            "ground_truth_types": gt_types,
            "generated_types": gen_types,
            "missing_critical_types": missing_critical,
            "passed": len(missing_critical) == 0,
        }

    def compare_power_distribution(self) -> Dict[str, Any]:
        """Compare power zone distribution."""
        gt_intervals = self.gt.get("intervals", [])
        gen_intervals = self.gen.get("intervals", [])

        # Calculate time in each zone
        def calculate_zone_time(intervals):
            zone_time = {i: 0 for i in range(1, 8)}
            for interval in intervals:
                zone = interval.get("zone", 0)
                duration = interval.get("endTimeSeconds", 0) - interval.get(
                    "startTimeSeconds", 0
                )
                if 1 <= zone <= 7:
                    zone_time[zone] += duration
            return zone_time

        gt_zone_time = calculate_zone_time(gt_intervals)
        gen_zone_time = calculate_zone_time(gen_intervals)

        # Calculate percentages
        gt_total = sum(gt_zone_time.values())
        gen_total = sum(gen_zone_time.values())

        gt_zone_pct = (
            {z: round((t / gt_total) * 100, 1) for z, t in gt_zone_time.items()}
            if gt_total > 0
            else {}
        )
        gen_zone_pct = (
            {z: round((t / gen_total) * 100, 1) for z, t in gen_zone_time.items()}
            if gen_total > 0
            else {}
        )

        # Calculate similarity (within 15% for main zones)
        zone_differences = {}
        major_mismatch = False

        for zone in range(1, 8):
            gt_pct = gt_zone_pct.get(zone, 0)
            gen_pct = gen_zone_pct.get(zone, 0)
            diff = abs(gt_pct - gen_pct)
            zone_differences[f"zone_{zone}"] = {
                "ground_truth_pct": gt_pct,
                "generated_pct": gen_pct,
                "difference_pct": round(diff, 1),
            }

            # Check if this is a significant zone in GT and there's major mismatch
            if gt_pct > 10 and diff > 15:
                major_mismatch = True

        return {
            "metric": "power_zone_distribution",
            "ground_truth_time_seconds": gt_zone_time,
            "generated_time_seconds": gen_zone_time,
            "zone_differences": zone_differences,
            "passed": not major_mismatch,
        }

    def compare_workout_structure(self) -> Dict[str, Any]:
        """Compare high-level workout structure (warmup -> main -> cooldown)."""
        gt_intervals = self.gt.get("intervals", [])
        gen_intervals = self.gen.get("intervals", [])

        def get_structure(intervals):
            """Extract basic structure pattern."""
            if not intervals:
                return []

            structure = []
            for interval in intervals:
                seg_type = interval.get("type", "unknown")
                # Simplify structure
                if seg_type in ["warmup"]:
                    structure.append("warmup")
                elif seg_type in ["cooldown"]:
                    structure.append("cooldown")
                elif seg_type in ["interval", "active"]:
                    structure.append("work")
                elif seg_type in ["recovery", "rest"]:
                    structure.append("recovery")
                else:
                    structure.append("other")
            return structure

        gt_structure = get_structure(gt_intervals)
        gen_structure = get_structure(gen_intervals)

        # Check if basic pattern matches (warmup at start, cooldown at end)
        has_warmup_start = (
            len(gt_structure) > 0 and gt_structure[0] == "warmup"
        ) and (len(gen_structure) > 0 and gen_structure[0] == "warmup")

        has_cooldown_end = (
            len(gt_structure) > 0 and gt_structure[-1] == "cooldown"
        ) and (len(gen_structure) > 0 and gen_structure[-1] == "cooldown")

        structure_similarity = has_warmup_start and has_cooldown_end

        return {
            "metric": "workout_structure",
            "ground_truth_pattern": gt_structure,
            "generated_pattern": gen_structure,
            "has_warmup_start": has_warmup_start,
            "has_cooldown_end": has_cooldown_end,
            "passed": structure_similarity,
        }

    def compare_average_power(self) -> Dict[str, Any]:
        """Compare average power across the workout."""
        gt_intervals = self.gt.get("intervals", [])
        gen_intervals = self.gen.get("intervals", [])

        def calculate_avg_power(intervals):
            """Calculate time-weighted average power."""
            total_power_time = 0
            total_time = 0

            for interval in intervals:
                power = interval.get("power", 0)
                duration = interval.get("endTimeSeconds", 0) - interval.get(
                    "startTimeSeconds", 0
                )
                total_power_time += power * duration
                total_time += duration

            return round(total_power_time / total_time) if total_time > 0 else 0

        gt_avg = calculate_avg_power(gt_intervals)
        gen_avg = calculate_avg_power(gen_intervals)

        difference = abs(gt_avg - gen_avg)
        tolerance_watts = 15  # 15W tolerance

        return {
            "metric": "average_power",
            "ground_truth_watts": gt_avg,
            "generated_watts": gen_avg,
            "difference_watts": difference,
            "passed": difference <= tolerance_watts,
            "tolerance_watts": tolerance_watts,
        }

    def compare_all(self) -> Dict[str, Any]:
        """Run all comparison metrics."""
        metrics = [
            self.compare_duration(),
            self.compare_interval_count(),
            self.compare_segment_types(),
            self.compare_power_distribution(),
            self.compare_workout_structure(),
            self.compare_average_power(),
        ]

        passed_count = sum(1 for m in metrics if m.get("passed", False))
        total_count = len(metrics)

        return {
            "comparison_score": f"{passed_count}/{total_count}",
            "similarity_percentage": round((passed_count / total_count) * 100, 2),
            "all_passed": passed_count == total_count,
            "metrics": metrics,
        }


def compare_to_ground_truth(
    ground_truth_workout: Dict[str, Any],
    generated_workout: Dict[str, Any],
) -> Dict[str, Any]:
    """Compare a generated workout to its ground truth."""
    comparator = WorkoutComparator(ground_truth_workout, generated_workout)
    return comparator.compare_all()
