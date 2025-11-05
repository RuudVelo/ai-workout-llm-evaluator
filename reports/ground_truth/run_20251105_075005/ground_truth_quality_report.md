# Ground Truth Quality Evaluation Report

**Generated:** 2025-11-05T07:50:05.471919
**Source Directory:** `ground_truth/run_20251104_155341`
**Files Analyzed:** 36

---

## Executive Summary

- **Total Files:** 36
- **Passed All Validations:** 22
- **Overall Pass Rate:** 61.1%
- **Average Validation Score:** 94.1%

---

## Validation Results Overview

**Files passing all validations:** 22 / 36 (61.1%)

### Common Validation Failures

| Metric | Failure Count |
|--------|--------------|
| duration_consistency | 12 |
| power_zone_accuracy | 5 |

---

## Per-File Analysis

| Prompt ID | File | Score | Pass Rate | Duration | Intervals | Attempts | Latency (s) | Cost | In Tokens | Out Tokens | Total Tokens | Issues | Status |
|-----------|------|-------|-----------|----------|-----------|----------|-------------|------|-----------|------------|--------------|--------|--------|
| climbing_intervals_wattage | `climbing_intervals_wattage.json` | 8/8 | 100.0% | 72.0 min | 12 | 1 | 17.60 | $0.0100 | 1,351 | 811 | 2,162 | 0 | ✅ PASS |
| descending_pyramid_threshold | `descending_pyramid_threshold.json` | 8/8 | 100.0% | 69.0 min | 16 | 2 | 33.25 | $0.0237 | 2,706 | 2,045 | 4,751 | 0 | ✅ PASS |
| endurance_65_sprints | `endurance_65_sprints.json` | 8/8 | 100.0% | 60.0 min | 7 | 1 | 8.19 | $0.0073 | 1,356 | 503 | 1,859 | 0 | ✅ PASS |
| group_ride_surges | `group_ride_surges.json` | 8/8 | 100.0% | 65.0 min | 10 | 1 | 13.79 | $0.0088 | 1,353 | 670 | 2,023 | 0 | ✅ PASS |
| low_cadence_strength | `low_cadence_strength.json` | 8/8 | 100.0% | 95.0 min | 20 | 3 | 90.81 | $0.0475 | 4,146 | 4,416 | 8,562 | 0 | ✅ PASS |
| mixed_zones_progression | `mixed_zones_progression.json` | 8/8 | 100.0% | 83.0 min | 8 | 1 | 28.45 | $0.0081 | 1,351 | 589 | 1,940 | 0 | ✅ PASS |
| over_under_classic | `over_under_classic.json` | 8/8 | 100.0% | 38.0 min | 23 | 3 | 85.66 | $0.0479 | 4,059 | 4,494 | 8,553 | 0 | ✅ PASS |
| progressive_blocks | `progressive_blocks.json` | 8/8 | 100.0% | 55.0 min | 8 | 1 | 10.82 | $0.0077 | 1,349 | 550 | 1,899 | 0 | ✅ PASS |
| progressive_ftp_percentage | `progressive_ftp_percentage.json` | 8/8 | 100.0% | 75.0 min | 9 | 2 | 49.42 | $0.0174 | 2,692 | 1,322 | 4,014 | 0 | ✅ PASS |
| ramping_intervals | `ramping_intervals.json` | 8/8 | 100.0% | 85.0 min | 10 | 3 | 42.34 | $0.0285 | 4,068 | 2,258 | 6,326 | 0 | ✅ PASS |
| ronnestad_anaerobic | `ronnestad_anaerobic.json` | 8/8 | 100.0% | 114.0 min | 52 | 2 | 122.44 | $0.0550 | 2,728 | 5,638 | 8,366 | 0 | ✅ PASS |
| shorthand_notation | `shorthand_notation.json` | 8/8 | 100.0% | 80.0 min | 13 | 1 | 10.14 | $0.0104 | 1,347 | 854 | 2,201 | 0 | ✅ PASS |
| simple_tempo_block | `simple_tempo_block.json` | 8/8 | 100.0% | 60.0 min | 15 | 1 | 23.97 | $0.0117 | 1,335 | 1,007 | 2,342 | 0 | ✅ PASS |
| simple_threshold_60min | `simple_threshold_60min.json` | 8/8 | 100.0% | 60.0 min | 9 | 1 | 20.14 | $0.0082 | 1,322 | 612 | 1,934 | 0 | ✅ PASS |
| sweet_spot_2to1_ratio | `sweet_spot_2to1_ratio.json` | 8/8 | 100.0% | 118.0 min | 16 | 1 | 24.61 | $0.0121 | 1,352 | 1,056 | 2,408 | 0 | ✅ PASS |
| sweet_spot_blocks_2to1 | `sweet_spot_blocks_2to1.json` | 8/8 | 100.0% | 100.0 min | 14 | 2 | 37.54 | $0.0204 | 2,716 | 1,660 | 4,376 | 0 | ✅ PASS |
| tempo_time_window | `tempo_time_window.json` | 8/8 | 100.0% | 60.0 min | 3 | 1 | 6.39 | $0.0051 | 1,351 | 242 | 1,593 | 0 | ✅ PASS |
| tempo_window_over_under | `tempo_window_over_under.json` | 8/8 | 100.0% | 75.0 min | 14 | 1 | 18.51 | $0.0112 | 1,390 | 943 | 2,333 | 0 | ✅ PASS |
| threshold_4x8_detailed | `threshold_4x8_detailed.json` | 8/8 | 100.0% | 79.3 min | 9 | 1 | 10.52 | $0.0082 | 1,352 | 607 | 1,959 | 0 | ✅ PASS |
| threshold_5x6 | `threshold_5x6.json` | 8/8 | 100.0% | 80.0 min | 11 | 1 | 10.49 | $0.0090 | 1,347 | 694 | 2,041 | 0 | ✅ PASS |
| two_hour_tempo_climbing | `two_hour_tempo_climbing.json` | 8/8 | 100.0% | 120.0 min | 3 | 1 | 3.87 | $0.0050 | 1,335 | 239 | 1,574 | 0 | ✅ PASS |
| zwift_intervals_sprints | `zwift_intervals_sprints.json` | 8/8 | 100.0% | 61.0 min | 16 | 3 | 62.20 | $0.0398 | 4,083 | 3,549 | 7,632 | 0 | ✅ PASS |
| ascending_descending_pyramid | `ascending_descending_pyramid.json` | 7/8 | 87.5% | 91.0 min | 18 | 3 | 67.21 | $0.0406 | 4,095 | 3,642 | 7,737 | 1 | ⚠️ ISSUES |
| fractional_threshold_2to1 | `fractional_threshold_2to1.json` | 7/8 | 87.5% | 56.0 min | 25 | 3 | 78.88 | $0.0464 | 4,113 | 4,304 | 8,417 | 1 | ⚠️ ISSUES |
| fractional_vo2max_efforts | `fractional_vo2max_efforts.json` | 7/8 | 87.5% | 36.0 min | 20 | 3 | 74.03 | $0.0405 | 4,038 | 3,643 | 7,681 | 1 | ⚠️ ISSUES |
| mixed_tabata_sweet_spot | `mixed_tabata_sweet_spot.json` | 7/8 | 87.5% | 120.0 min | 28 | 3 | 1062.46 | $0.0520 | 4,119 | 4,947 | 9,066 | 1 | ⚠️ ISSUES |
| over_under_sweet_spot | `over_under_sweet_spot.json` | 7/8 | 87.5% | 64.0 min | 19 | 3 | 66.93 | $0.0426 | 4,062 | 3,878 | 7,940 | 1 | ⚠️ ISSUES |
| ronnestad_double_set_no_explanation | `ronnestad_double_set_no_explanation.json` | 7/8 | 87.5% | 75.0 min | 18 | 3 | 199.36 | $0.0506 | 4,026 | 4,803 | 8,829 | 1 | ⚠️ ISSUES |
| sweet_spot_progression_time_based | `sweet_spot_progression_time_based.json` | 7/8 | 87.5% | 65.0 min | 5 | 3 | 32.38 | $0.0188 | 4,173 | 1,111 | 5,284 | 1 | ⚠️ ISSUES |
| tabata_sprints | `tabata_sprints.json` | 7/8 | 87.5% | 45.0 min | 33 | 3 | 107.29 | $0.0667 | 4,092 | 6,637 | 10,729 | 1 | ⚠️ ISSUES |
| tempo_sprints_combo | `tempo_sprints_combo.json` | 7/8 | 87.5% | 50.0 min | 19 | 3 | 50.28 | $0.0405 | 4,047 | 3,636 | 7,683 | 1 | ⚠️ ISSUES |
| threshold_intervals_3x10 | `threshold_intervals_3x10.json` | 7/8 | 87.5% | 60.0 min | 12 | 3 | 44.09 | $0.0287 | 4,041 | 2,285 | 6,326 | 1 | ⚠️ ISSUES |
| threshold_sprints_shorthand | `threshold_sprints_shorthand.json` | 7/8 | 87.5% | 88.3 min | 17 | 3 | 57.60 | $0.0390 | 4,080 | 3,466 | 7,546 | 1 | ⚠️ ISSUES |
| ascending_pyramid_threshold | `ascending_pyramid_threshold.json` | 6/8 | 75.0% | 67.0 min | 14 | 3 | 57.28 | $0.0316 | 4,056 | 2,616 | 6,672 | 2 | ⚠️ ISSUES |
| complex_progressive_blocks | `complex_progressive_blocks.json` | 6/8 | 75.0% | 67.0 min | 18 | 3 | 73.30 | $0.0392 | 4,191 | 3,461 | 7,652 | 2 | ⚠️ ISSUES |
| ronnestad_double_set | `ronnestad_double_set.json` | 6/8 | 75.0% | 87.0 min | 61 | 3 | 539.83 | $0.1156 | 4,167 | 12,243 | 16,410 | 2 | ⚠️ ISSUES |

---

## Quality Metrics Deep Dive

### Workout Characteristics

- **Average Duration:** 74.3 minutes
- **Duration Range:** 36 - 120 minutes
- **Average Intervals:** 16.8
- **Interval Range:** 3 - 61

### Segment Type Distribution

| Segment Type | Count |
|--------------|-------|
| interval | 248 |
| recovery | 172 |
| warmup | 124 |
| cooldown | 58 |
| active | 2 |
| rest | 1 |

### Power Zone Time Distribution

| Zone | Total Time (min) |
|------|------------------|
| Zone 1 | 694.0 |
| Zone 2 | 597.1 |
| Zone 3 | 738.5 |
| Zone 4 | 232.8 |
| Zone 5 | 146.8 |
| Zone 6 | 75.7 |
| Zone 7 | 17.2 |

---

## Issues & Anomalies

Found **17** validation issues:

### Issue #1: duration_consistency

- **File:** `ascending_descending_pyramid.json`
- **Prompt ID:** ascending_descending_pyramid
- **Details:** Duration mismatch: declared 5460s, calculated 3660s (diff: 1800s)

### Issue #2: duration_consistency

- **File:** `ascending_pyramid_threshold.json`
- **Prompt ID:** ascending_pyramid_threshold
- **Details:** Duration mismatch: declared 4020s, calculated 3420s (diff: 600s)

### Issue #3: power_zone_accuracy

- **File:** `ascending_pyramid_threshold.json`
- **Prompt ID:** ascending_pyramid_threshold
- **Details:** 4 mismatch(es) found
  - Segment 7: Power 225W declared as Zone 4, actually Zone 3
  - Segment 9: Power 225W declared as Zone 4, actually Zone 3
  - Segment 11: Power 225W declared as Zone 4, actually Zone 3

### Issue #4: duration_consistency

- **File:** `complex_progressive_blocks.json`
- **Prompt ID:** complex_progressive_blocks
- **Details:** Duration mismatch: declared 4020s, calculated 3000s (diff: 1020s)

### Issue #5: power_zone_accuracy

- **File:** `complex_progressive_blocks.json`
- **Prompt ID:** complex_progressive_blocks
- **Details:** 1 mismatch(es) found
  - Segment 2: Power 163W declared as Zone 3, actually Zone 2

### Issue #6: duration_consistency

- **File:** `fractional_threshold_2to1.json`
- **Prompt ID:** fractional_threshold_2to1
- **Details:** Duration mismatch: declared 3360s, calculated 2535s (diff: 825s)

### Issue #7: power_zone_accuracy

- **File:** `fractional_vo2max_efforts.json`
- **Prompt ID:** fractional_vo2max_efforts
- **Details:** 3 mismatch(es) found
  - Segment 1: Power 150W declared as Zone 3, actually Zone 2
  - Segment 2: Power 163W declared as Zone 3, actually Zone 2
  - Segment 14: Power 150W declared as Zone 3, actually Zone 2

### Issue #8: duration_consistency

- **File:** `mixed_tabata_sweet_spot.json`
- **Prompt ID:** mixed_tabata_sweet_spot
- **Details:** Duration mismatch: declared 7200s, calculated 5220s (diff: 1980s)

### Issue #9: duration_consistency

- **File:** `over_under_sweet_spot.json`
- **Prompt ID:** over_under_sweet_spot
- **Details:** Duration mismatch: declared 3840s, calculated 3480s (diff: 360s)

### Issue #10: duration_consistency

- **File:** `ronnestad_double_set.json`
- **Prompt ID:** ronnestad_double_set
- **Details:** Duration mismatch: declared 5220s, calculated 3480s (diff: 1740s)

### Issue #11: power_zone_accuracy

- **File:** `ronnestad_double_set.json`
- **Prompt ID:** ronnestad_double_set
- **Details:** 1 mismatch(es) found
  - Segment 33: Power 225W declared as Zone 4, actually Zone 3

### Issue #12: duration_consistency

- **File:** `ronnestad_double_set_no_explanation.json`
- **Prompt ID:** ronnestad_double_set_no_explanation
- **Details:** Duration mismatch: declared 4500s, calculated 3300s (diff: 1200s)

### Issue #13: power_zone_accuracy

- **File:** `sweet_spot_progression_time_based.json`
- **Prompt ID:** sweet_spot_progression_time_based
- **Details:** 2 mismatch(es) found
  - Segment 2: Power 225W declared as Zone 4, actually Zone 3
  - Segment 4: Power 225W declared as Zone 4, actually Zone 3

### Issue #14: duration_consistency

- **File:** `tabata_sprints.json`
- **Prompt ID:** tabata_sprints
- **Details:** Duration mismatch: declared 2700s, calculated 1920s (diff: 780s)

### Issue #15: duration_consistency

- **File:** `tempo_sprints_combo.json`
- **Prompt ID:** tempo_sprints_combo
- **Details:** Duration mismatch: declared 3000s, calculated 2460s (diff: 540s)

### Issue #16: duration_consistency

- **File:** `threshold_intervals_3x10.json`
- **Prompt ID:** threshold_intervals_3x10
- **Details:** Duration mismatch: declared 3600s, calculated 4800s (diff: 1200s)

### Issue #17: duration_consistency

- **File:** `threshold_sprints_shorthand.json`
- **Prompt ID:** threshold_sprints_shorthand
- **Details:** Duration mismatch: declared 5300s, calculated 4530s (diff: 770s)

---

## Statistical Summary

### Generation Performance Overview

- **Total Tokens:** 198,820
- **Total Cost:** $1.0556
- **Total Latency:** 3242.06 seconds
- **Average Latency:** 90.06 seconds

### Token Statistics

| Metric | Input Tokens | Output Tokens | Total |
|--------|--------------|---------------|-------|
| **Total** | 103,389 | 95,431 | 198,820 |
| **Average per Workout** | 2872 | 2651 | 5523 |
| **Min** | 1,322 | 239 | - |
| **Max** | 4,191 | 12,243 | - |

### Cost Breakdown

| Metric | Input Cost | Output Cost | Total Cost |
|--------|------------|-------------|------------|
| **Total** | $0.2254 | $0.8302 | $1.0556 |
| **Average per Workout** | $0.0063 | $0.0231 | $0.0293 |
| **Min per Workout** | - | - | $0.0050 |
| **Max per Workout** | - | - | $0.1156 |

### Latency Statistics

| Metric | Latency (ms) | Latency (seconds) |
|--------|--------------|-------------------|
| **Total** | 3,242,062 | 3242.06 |
| **Average** | 90057 | 90.06 |
| **Min** | 3,872 | 3.87 |
| **Max** | 1,062,459 | 1062.46 |

### Attempt Distribution

| Attempts | Number of Workouts | Percentage |
|----------|-------------------|------------|
| 1 | 14 | 38.9% |
| 2 | 4 | 11.1% |
| 3 | 18 | 50.0% |

### Model Usage

| Model | Usage Count |
|-------|-------------|
| GPT-4o | 36 |

---

## Recommendations

### Files Requiring Attention (14 file(s))

- `ascending_descending_pyramid.json` - Score: 7/8 (1 issue(s))
- `fractional_threshold_2to1.json` - Score: 7/8 (1 issue(s))
- `fractional_vo2max_efforts.json` - Score: 7/8 (1 issue(s))
- `mixed_tabata_sweet_spot.json` - Score: 7/8 (1 issue(s))
- `over_under_sweet_spot.json` - Score: 7/8 (1 issue(s))
- `ronnestad_double_set_no_explanation.json` - Score: 7/8 (1 issue(s))
- `sweet_spot_progression_time_based.json` - Score: 7/8 (1 issue(s))
- `tabata_sprints.json` - Score: 7/8 (1 issue(s))
- `tempo_sprints_combo.json` - Score: 7/8 (1 issue(s))
- `threshold_intervals_3x10.json` - Score: 7/8 (1 issue(s))
- `threshold_sprints_shorthand.json` - Score: 7/8 (1 issue(s))
- `ascending_pyramid_threshold.json` - Score: 6/8 (2 issue(s))
- `complex_progressive_blocks.json` - Score: 6/8 (2 issue(s))
- `ronnestad_double_set.json` - Score: 6/8 (2 issue(s))

### General Recommendations

1. Regularly review validation failures to maintain data quality
2. Consider adding more diverse workout types to improve test coverage
3. Ensure power zone calculations are accurate (most common failure point)
4. Verify time continuity in complex workout structures
