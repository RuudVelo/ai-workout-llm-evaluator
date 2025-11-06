"""
Structure quality metrics for evaluating workout pattern and distribution similarity.

This module compares generated workouts to ground truth based on:
1. Power zone distribution similarity (Jensen-Shannon divergence)
2. Power pattern similarity (Segmented DTW with correlation fallback)
"""

import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from scipy.spatial.distance import jensenshannon
from scipy.stats import pearsonr
import yaml
from pathlib import Path


class StructureQualityEvaluator:
    """Evaluates workout structure quality against ground truth."""

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize evaluator with configuration.

        Args:
            config_path: Path to evaluation.yaml config file
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "evaluation.yaml"

        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        self.sq_config = self.config["structure_quality_scoring"]
        self.enabled = self.sq_config["enabled"]

    def evaluate(
        self, ground_truth: Dict[str, Any], generated: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate structure quality of generated workout vs ground truth.

        Args:
            ground_truth: Ground truth workout dict
            generated: Generated workout dict

        Returns:
            Dict with structure quality scores and details
        """
        if not self.enabled:
            return {"enabled": False, "message": "Structure quality scoring disabled"}

        try:
            # Extract intervals
            gt_intervals = ground_truth.get("intervals", [])
            gen_intervals = generated.get("intervals", [])

            if not gt_intervals or not gen_intervals:
                return self._handle_error("Missing intervals in one or both workouts")

            # Calculate component scores
            zone_distribution_result = self._calculate_zone_distribution_similarity(
                gt_intervals, gen_intervals
            )

            pattern_similarity_result = self._calculate_pattern_similarity(
                gt_intervals, gen_intervals
            )

            # Calculate composite score
            weights = self.sq_config["component_weights"]
            composite_score = (
                zone_distribution_result["score"]
                * weights["power_zone_distribution_match"]
                + pattern_similarity_result["score"]
                * weights["power_pattern_similarity"]
            )

            return {
                "enabled": True,
                "composite_score": round(composite_score * 100, 2),  # 0-100 scale
                "components": {
                    "power_zone_distribution_match": zone_distribution_result,
                    "power_pattern_similarity": pattern_similarity_result,
                },
                "weights": weights,
            }

        except Exception as e:
            return self._handle_error(f"Calculation error: {str(e)}")

    def _calculate_zone_distribution_similarity(
        self, gt_intervals: List[Dict], gen_intervals: List[Dict]
    ) -> Dict[str, Any]:
        """
        Calculate power zone distribution similarity using Jensen-Shannon divergence.

        Args:
            gt_intervals: Ground truth intervals
            gen_intervals: Generated intervals

        Returns:
            Dict with score and details
        """
        config = self.sq_config["power_zone_distribution"]

        # Calculate time in each zone
        gt_zone_time = self._calculate_zone_time(gt_intervals)
        gen_zone_time = self._calculate_zone_time(gen_intervals)

        # Convert to percentages
        gt_total = sum(gt_zone_time.values())
        gen_total = sum(gen_zone_time.values())

        if gt_total == 0 or gen_total == 0:
            return {"score": 0.0, "error": "No valid zone time"}

        gt_zone_pct = {z: (t / gt_total) * 100 for z, t in gt_zone_time.items()}
        gen_zone_pct = {z: (t / gen_total) * 100 for z, t in gen_zone_time.items()}

        # Create probability distributions for Jensen-Shannon
        # Convert percentages to probabilities (0-1)
        gt_dist = np.array([gt_zone_pct.get(z, 0) / 100 for z in range(1, 8)])
        gen_dist = np.array([gen_zone_pct.get(z, 0) / 100 for z in range(1, 8)])

        # Handle edge case: ensure distributions are valid probabilities
        gt_dist = gt_dist / gt_dist.sum() if gt_dist.sum() > 0 else gt_dist
        gen_dist = gen_dist / gen_dist.sum() if gen_dist.sum() > 0 else gen_dist

        # Calculate Jensen-Shannon divergence (0 = identical, 1 = completely different)
        js_divergence = jensenshannon(gt_dist, gen_dist)

        # Check for invalid values
        if np.isnan(js_divergence) or np.isinf(js_divergence):
            return {
                "score": 0.0,
                "method": config["method"],
                "js_divergence": None,
                "error": "Invalid JS divergence (NaN or Inf)",
                "ground_truth_zone_pct": {
                    f"zone_{z}": round(pct, 1) for z, pct in gt_zone_pct.items()
                },
                "generated_zone_pct": {
                    f"zone_{z}": round(pct, 1) for z, pct in gen_zone_pct.items()
                },
            }

        # Convert to similarity score (0-1, higher is better)
        # JS divergence is already bounded [0, 1]
        js_similarity = 1 - js_divergence

        return {
            "score": float(js_similarity),
            "method": config["method"],
            "js_divergence": float(js_divergence),
            "ground_truth_zone_pct": {
                f"zone_{z}": round(pct, 1) for z, pct in gt_zone_pct.items()
            },
            "generated_zone_pct": {
                f"zone_{z}": round(pct, 1) for z, pct in gen_zone_pct.items()
            },
        }

    def _calculate_zone_time(self, intervals: List[Dict]) -> Dict[int, float]:
        """Calculate total time spent in each power zone."""
        zone_time = {z: 0.0 for z in range(1, 8)}

        for interval in intervals:
            zone = interval.get("zone", 0)
            duration = interval.get("endTimeSeconds", 0) - interval.get(
                "startTimeSeconds", 0
            )
            # Protect against negative durations (invalid data)
            duration = max(0, duration)
            if 1 <= zone <= 7:
                zone_time[zone] += duration

        return zone_time

    def _calculate_pattern_similarity(
        self, gt_intervals: List[Dict], gen_intervals: List[Dict]
    ) -> Dict[str, Any]:
        """
        Calculate power pattern similarity using segmented DTW or correlation fallback.

        Args:
            gt_intervals: Ground truth intervals
            gen_intervals: Generated intervals

        Returns:
            Dict with score and details
        """
        config = self.sq_config["power_pattern_similarity"]
        method = config["method"]

        # Check if workout is too long for DTW
        gt_duration = gt_intervals[-1]["endTimeSeconds"] if gt_intervals else 0
        max_duration = config.get("dtw_max_duration", 7200)

        if method == "segmented_dtw" and gt_duration <= max_duration:
            try:
                return self._calculate_segmented_dtw(gt_intervals, gen_intervals)
            except Exception as e:
                # Fall back to correlation
                fallback_method = config.get("fallback_method", "correlation")
                result = self._calculate_correlation_similarity(
                    gt_intervals, gen_intervals
                )
                result["note"] = f"DTW failed ({str(e)}), used fallback: {fallback_method}"
                return result
        else:
            # Use correlation for long workouts or if method is 'correlation'
            return self._calculate_correlation_similarity(gt_intervals, gen_intervals)

    def _calculate_segmented_dtw(
        self, gt_intervals: List[Dict], gen_intervals: List[Dict]
    ) -> Dict[str, Any]:
        """
        Calculate pattern similarity using segmented DTW.

        Segments workout into warmup/main/cooldown and applies DTW to each.
        """
        config = self.sq_config["power_pattern_similarity"]

        # Identify segments
        gt_segments = self._identify_segments(gt_intervals)
        gen_segments = self._identify_segments(gen_intervals)

        segment_scores = {}
        segment_weights = config["segment_weights"]

        total_score = 0.0
        total_weight = 0.0

        for segment_type in ["warmup", "main", "cooldown"]:
            if segment_type in gt_segments and segment_type in gen_segments:
                gt_seg = gt_segments[segment_type]
                gen_seg = gen_segments[segment_type]

                # Create power time series for this segment
                gt_series = self._create_power_series(gt_seg)
                gen_series = self._create_power_series(gen_seg)

                # Calculate DTW similarity
                try:
                    similarity = self._calculate_dtw_similarity(gt_series, gen_series)
                except ImportError:
                    # DTW library not available, fall back to correlation
                    similarity = self._calculate_series_correlation(
                        gt_series, gen_series
                    )

                weight = segment_weights.get(segment_type, 0)
                segment_scores[segment_type] = {
                    "similarity": round(similarity, 4),
                    "weight": weight,
                    "gt_duration": len(gt_series),
                    "gen_duration": len(gen_series),
                }

                total_score += similarity * weight
                total_weight += weight

        # Calculate final score
        final_score = total_score / total_weight if total_weight > 0 else 0.0

        return {
            "score": float(final_score),
            "method": "segmented_dtw",
            "segment_scores": segment_scores,
            "total_weight": total_weight,
        }

    def _calculate_correlation_similarity(
        self, gt_intervals: List[Dict], gen_intervals: List[Dict]
    ) -> Dict[str, Any]:
        """
        Calculate pattern similarity using Pearson correlation.

        Simpler fallback method that resamples both workouts to same length.
        """
        # Create power time series
        gt_series = self._create_power_series(gt_intervals)
        gen_series = self._create_power_series(gen_intervals)

        # Calculate correlation
        correlation = self._calculate_series_correlation(gt_series, gen_series)

        return {
            "score": float(correlation),
            "method": "correlation",
            "gt_duration": len(gt_series),
            "gen_duration": len(gen_series),
        }

    def _identify_segments(self, intervals: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Identify warmup, main set, and cooldown segments.

        Args:
            intervals: List of interval dicts

        Returns:
            Dict mapping segment type to list of intervals
        """
        config = self.sq_config["power_pattern_similarity"]["segment_identification"]

        segments = {"warmup": [], "main": [], "cooldown": []}

        warmup_types = set(config["warmup_types"])
        main_types = set(config["main_types"])
        cooldown_types = set(config["cooldown_types"])

        for interval in intervals:
            seg_type = interval.get("type", "")
            if seg_type in warmup_types:
                segments["warmup"].append(interval)
            elif seg_type in cooldown_types:
                segments["cooldown"].append(interval)
            elif seg_type in main_types or seg_type not in warmup_types.union(
                cooldown_types
            ):
                segments["main"].append(interval)

        # If no explicit warmup/cooldown, try auto-detection
        if config.get("auto_detect_segments", True):
            if not segments["warmup"] and not segments["cooldown"]:
                segments = self._auto_detect_segments(intervals, config)

        return segments

    def _auto_detect_segments(
        self, intervals: List[Dict], config: Dict
    ) -> Dict[str, List[Dict]]:
        """
        Auto-detect segments when not explicitly labeled.

        Assumes first N minutes = warmup, last N minutes = cooldown, rest = main.
        """
        warmup_threshold = config.get("warmup_duration_threshold", 600)
        cooldown_threshold = config.get("cooldown_duration_threshold", 600)

        segments = {"warmup": [], "main": [], "cooldown": []}

        if not intervals:
            return segments

        total_duration = intervals[-1]["endTimeSeconds"]

        for interval in intervals:
            start = interval["startTimeSeconds"]
            end = interval["endTimeSeconds"]

            if start < warmup_threshold:
                segments["warmup"].append(interval)
            elif end > (total_duration - cooldown_threshold):
                segments["cooldown"].append(interval)
            else:
                segments["main"].append(interval)

        return segments

    def _create_power_series(
        self, intervals: List[Dict], resolution_seconds: int = 1
    ) -> np.ndarray:
        """
        Create a time series of power values at specified resolution.

        Args:
            intervals: List of interval dicts
            resolution_seconds: Time resolution in seconds

        Returns:
            Numpy array of power values
        """
        if not intervals:
            return np.array([])

        # Get total duration
        total_duration = intervals[-1]["endTimeSeconds"]

        # Create array of power values
        series = []
        for t in range(0, total_duration, resolution_seconds):
            # Find which interval this timestamp belongs to
            power = self._get_power_at_time(intervals, t)
            series.append(power)

        return np.array(series)

    def _get_power_at_time(self, intervals: List[Dict], time_seconds: int) -> float:
        """Get power value at a specific time point."""
        for interval in intervals:
            if (
                interval["startTimeSeconds"]
                <= time_seconds
                < interval["endTimeSeconds"]
            ):
                return float(interval.get("power", 0))
        return 0.0

    def _calculate_dtw_similarity(
        self, series1: np.ndarray, series2: np.ndarray
    ) -> float:
        """
        Calculate DTW similarity between two time series.

        Returns similarity score 0-1 (higher is better).
        """
        try:
            from dtaidistance import dtw

            # Calculate DTW distance
            distance = dtw.distance(series1, series2)

            # Normalize to similarity score
            # Use maximum possible distance as normalizer
            max_len = max(len(series1), len(series2))
            max_power = max(np.max(series1), np.max(series2))
            max_distance = max_len * max_power

            if max_distance == 0:
                return 1.0

            similarity = 1 - (distance / max_distance)
            return max(0.0, min(1.0, similarity))

        except ImportError:
            # dtaidistance not installed, fall back to correlation
            return self._calculate_series_correlation(series1, series2)

    def _calculate_series_correlation(
        self, series1: np.ndarray, series2: np.ndarray
    ) -> float:
        """
        Calculate Pearson correlation between two time series.

        Resamples to same length if needed.
        Returns correlation as similarity score 0-1.
        """
        # Resample to same length if different
        if len(series1) != len(series2):
            target_len = max(len(series1), len(series2))
            series1 = self._resample_series(series1, target_len)
            series2 = self._resample_series(series2, target_len)

        # Handle edge cases
        if len(series1) < 2 or len(series2) < 2:
            return 0.0

        if np.std(series1) == 0 or np.std(series2) == 0:
            # Constant series - check if they're the same constant
            return 1.0 if np.allclose(series1, series2) else 0.0

        # Calculate correlation
        correlation, _ = pearsonr(series1, series2)

        # Convert -1 to 1 range to 0-1 similarity
        # Negative correlation is bad, so treat as 0
        similarity = max(0.0, (correlation + 1) / 2)

        return similarity

    def _resample_series(self, series: np.ndarray, target_length: int) -> np.ndarray:
        """Resample a time series to target length using linear interpolation."""
        if len(series) == 0:
            return np.zeros(target_length)

        original_indices = np.linspace(0, len(series) - 1, len(series))
        target_indices = np.linspace(0, len(series) - 1, target_length)

        resampled = np.interp(target_indices, original_indices, series)
        return resampled

    def _handle_error(self, error_message: str) -> Dict[str, Any]:
        """Handle errors according to config."""
        fallback_config = self.sq_config["fallback"]
        on_error = fallback_config.get("on_calculation_error", "skip")

        if on_error == "neutral_score":
            neutral_value = fallback_config.get("neutral_score_value", 0.5)
            return {
                "enabled": True,
                "composite_score": neutral_value * 100,
                "error": error_message,
                "fallback_applied": "neutral_score",
            }
        elif on_error == "skip":
            return {
                "enabled": True,
                "composite_score": None,
                "error": error_message,
                "fallback_applied": "skip",
            }
        else:
            raise ValueError(error_message)


def evaluate_structure_quality(
    ground_truth_workout: Dict[str, Any],
    generated_workout: Dict[str, Any],
    config_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Convenience function to evaluate structure quality.

    Args:
        ground_truth_workout: Ground truth workout dict
        generated_workout: Generated workout dict
        config_path: Optional path to evaluation config

    Returns:
        Structure quality evaluation results
    """
    evaluator = StructureQualityEvaluator(config_path)
    return evaluator.evaluate(ground_truth_workout, generated_workout)
