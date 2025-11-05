"""
Postprocessing layer to auto-fix deterministic validation failures.

This module automatically corrects common LLM errors that don't require semantic
understanding, significantly reducing the need for costly retries.
"""

import logging
from typing import Dict, Any, List
from system_prompt import calculate_zones


class WorkoutPostprocessor:
    """Automatically fixes deterministic validation failures in workout JSON."""

    def __init__(self, ftp: int, logger: logging.Logger = None):
        self.ftp = ftp
        self.zones = calculate_zones(ftp)
        self.logger = logger or logging.getLogger(__name__)
        self.fixes_applied = []

    def postprocess(self, workout: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply all postprocessing fixes to a workout.

        Returns the fixed workout and logs what was corrected.
        """
        self.fixes_applied = []

        if not isinstance(workout, dict):
            return workout

        # Apply fixes in order of safety and importance
        workout = self._fix_power_adjustments(workout)
        workout = self._fix_ftp_percentages(workout)
        workout = self._fix_power_zones(workout)
        workout = self._fix_duration_consistency(workout)
        workout = self._fix_segment_types(workout)
        workout = self._fix_minor_time_gaps(workout)

        if self.fixes_applied:
            self.logger.info(
                f"    Postprocessing applied {len(self.fixes_applied)} fix(es): "
                f"{', '.join(set(self.fixes_applied))}"
            )

        return workout

    def _fix_power_adjustments(self, workout: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fix powerAdjustedUpward and powerAdjustedDownward fields.

        These are UI helper fields with deterministic formulas:
        - powerAdjustedUpward = power + 10
        - powerAdjustedDownward = max(0, power - 10)
        """
        if "intervals" not in workout:
            return workout

        fixed_count = 0
        for interval in workout["intervals"]:
            power = interval.get("power", 0)
            expected_upward = power + 10
            expected_downward = max(0, power - 10)

            # Fix upward if incorrect or missing
            if interval.get("powerAdjustedUpward") != expected_upward:
                interval["powerAdjustedUpward"] = expected_upward
                fixed_count += 1

            # Fix downward if incorrect or missing
            if interval.get("powerAdjustedDownward") != expected_downward:
                interval["powerAdjustedDownward"] = expected_downward
                fixed_count += 1

        if fixed_count > 0:
            self.fixes_applied.append("power_adjustments")

        return workout

    def _fix_ftp_percentages(self, workout: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fix perc_ftp field to match power value.

        Formula: perc_ftp = round((power/ftp) * 100)
        """
        if "intervals" not in workout:
            return workout

        fixed_count = 0
        for interval in workout["intervals"]:
            power = interval.get("power", 0)
            expected_perc = round((power / self.ftp) * 100)

            # Allow ±1% tolerance (same as evaluator)
            if abs(interval.get("perc_ftp", 0) - expected_perc) > 1:
                interval["perc_ftp"] = expected_perc
                fixed_count += 1

        if fixed_count > 0:
            self.fixes_applied.append("ftp_percentages")

        return workout

    def _fix_power_zones(self, workout: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fix zone field based on power value.

        Uses the same zone calculation as the system prompt.
        """
        if "intervals" not in workout:
            return workout

        fixed_count = 0
        for interval in workout["intervals"]:
            power = interval.get("power", 0)
            declared_zone = interval.get("zone")

            # Calculate correct zone
            actual_zone = self._calculate_zone(power)

            # Only fix if zone is wrong or missing
            if declared_zone != actual_zone:
                interval["zone"] = actual_zone
                fixed_count += 1

        if fixed_count > 0:
            self.fixes_applied.append("power_zones")

        return workout

    def _calculate_zone(self, power: int) -> int:
        """Calculate the power zone for a given power value."""
        for zone_num in range(1, 8):
            zone_key = f"z{zone_num}"
            zone_range = self.zones[zone_key]
            if zone_range["min"] <= power <= zone_range["max"]:
                return zone_num
        # If power exceeds all zones, return zone 7
        return 7

    def _fix_duration_consistency(self, workout: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fix workout_duration to match the last interval's endTimeSeconds.

        The true duration is defined by the interval structure, not the declared value.
        """
        if "intervals" not in workout or not workout["intervals"]:
            return workout

        last_interval = workout["intervals"][-1]
        calculated_duration = last_interval.get("endTimeSeconds", 0)
        declared_duration = workout.get("workout_duration", 0)

        # Only fix if there's a mismatch
        if calculated_duration != declared_duration:
            workout["workout_duration"] = calculated_duration
            self.fixes_applied.append("duration_consistency")

        return workout

    def _fix_segment_types(self, workout: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fix invalid segment types by mapping to valid enum values.

        Valid types: active, rest, warmup, cooldown, recovery, interval, other
        """
        if "intervals" not in workout:
            return workout

        valid_types = {
            "active",
            "rest",
            "warmup",
            "cooldown",
            "recovery",
            "interval",
            "other",
        }

        # Common invalid types and their mappings
        type_mapping = {
            "tempo": "interval",
            "threshold": "interval",
            "vo2max": "interval",
            "vo2": "interval",
            "sweet spot": "interval",
            "sweetspot": "interval",
            "sprint": "interval",
            "work": "interval",
            "effort": "interval",
            "endurance": "active",
            "steady": "active",
            "easy": "recovery",
            "cool down": "cooldown",
            "warm up": "warmup",
            "warm-up": "warmup",
            "cool-down": "cooldown",
        }

        fixed_count = 0
        for interval in workout["intervals"]:
            segment_type = interval.get("type", "").lower()

            if segment_type not in valid_types:
                # Try to map to valid type
                mapped_type = type_mapping.get(segment_type, "other")
                interval["type"] = mapped_type
                fixed_count += 1

        if fixed_count > 0:
            self.fixes_applied.append("segment_types")

        return workout

    def _fix_minor_time_gaps(self, workout: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fix minor time gaps or overlaps between intervals (≤5 seconds).

        This handles off-by-one errors and small timing mistakes that don't
        indicate structural problems. Larger gaps suggest the LLM misunderstood
        the workout structure and should trigger a retry.
        """
        if "intervals" not in workout or not workout["intervals"]:
            return workout

        intervals = sorted(workout["intervals"], key=lambda x: x.get("startTimeSeconds", 0))
        fixed_count = 0

        # Fix first interval if it doesn't start at 0
        if intervals[0].get("startTimeSeconds", 0) != 0:
            gap = intervals[0]["startTimeSeconds"]
            if 0 < gap <= 5:
                intervals[0]["startTimeSeconds"] = 0
                fixed_count += 1

        # Fix gaps/overlaps between intervals
        for i in range(len(intervals) - 1):
            current_end = intervals[i].get("endTimeSeconds", 0)
            next_start = intervals[i + 1].get("startTimeSeconds", 0)

            gap = next_start - current_end

            # Only fix small gaps/overlaps (≤5 seconds)
            if 0 < abs(gap) <= 5:
                # Adjust the next interval's start time to match current end
                intervals[i + 1]["startTimeSeconds"] = current_end

                # Also need to adjust all subsequent times by the same amount
                time_shift = gap
                for j in range(i + 1, len(intervals)):
                    intervals[j]["startTimeSeconds"] -= time_shift
                    intervals[j]["endTimeSeconds"] -= time_shift

                fixed_count += 1
                break  # Re-process after adjustment

        if fixed_count > 0:
            self.fixes_applied.append("time_continuity")

        return workout

    def get_fixes_summary(self) -> List[str]:
        """Return a list of fixes that were applied."""
        return self.fixes_applied


def postprocess_workout(workout: Dict[str, Any], ftp: int, logger: logging.Logger = None) -> Dict[str, Any]:
    """
    Convenience function to postprocess a workout.

    Args:
        workout: The workout JSON to fix
        ftp: Functional Threshold Power in watts
        logger: Optional logger for reporting fixes

    Returns:
        Fixed workout JSON
    """
    processor = WorkoutPostprocessor(ftp, logger)
    return processor.postprocess(workout)
