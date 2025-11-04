# Ground Truth Quality Evaluation Report

**Generated:** 2025-11-04T14:13:48.183229
**Source Directory:** `ground_truth`
**Files Analyzed:** 19

---

## Executive Summary

- **Total Files:** 19
- **Passed All Validations:** 15
- **Overall Pass Rate:** 78.9%
- **Average Validation Score:** 97.4%

---

## Validation Results Overview

**Files passing all validations:** 15 / 19 (78.9%)

### Common Validation Failures

| Metric | Failure Count |
|--------|--------------|
| power_zone_accuracy | 2 |
| duration_consistency | 2 |

---

## Per-File Analysis

| Prompt ID | File | Score | Pass Rate | Duration | Intervals | Attempts | Latency (s) | Cost | In Tokens | Out Tokens | Total Tokens | Issues | Status |
|-----------|------|-------|-----------|----------|-----------|----------|-------------|------|-----------|------------|--------------|--------|--------|
| climbing_intervals_wattage | `climbing_intervals_wattage.json` | 8/8 | 100.0% | 75.0 min | 11 | 2 | 23.11 | $0.0179 | 2,012 | 1,549 | 3,561 | 0 | ✅ PASS |
| endurance_65_sprints | `endurance_65_sprints.json` | 8/8 | 100.0% | 60.0 min | 7 | 1 | 9.38 | $0.0066 | 1,011 | 509 | 1,520 | 0 | ✅ PASS |
| group_ride_surges | `group_ride_surges.json` | 8/8 | 100.0% | 65.0 min | 11 | 1 | 12.02 | $0.0087 | 1,008 | 750 | 1,758 | 0 | ✅ PASS |
| low_cadence_strength | `low_cadence_strength.json` | 8/8 | 100.0% | 94.0 min | 14 | 1 | 11.73 | $0.0108 | 1,037 | 986 | 2,023 | 0 | ✅ PASS |
| mixed_zones_progression | `mixed_zones_progression.json` | 8/8 | 100.0% | 95.0 min | 8 | 2 | 19.62 | $0.0146 | 2,012 | 1,171 | 3,183 | 0 | ✅ PASS |
| progressive_blocks | `progressive_blocks.json` | 8/8 | 100.0% | 55.0 min | 10 | 1 | 11.50 | $0.0081 | 1,004 | 680 | 1,684 | 0 | ✅ PASS |
| progressive_ftp_percentage | `progressive_ftp_percentage.json` | 8/8 | 100.0% | 86.0 min | 10 | 3 | 28.60 | $0.0234 | 3,003 | 1,937 | 4,940 | 0 | ✅ PASS |
| ramping_intervals | `ramping_intervals.json` | 8/8 | 100.0% | 75.0 min | 9 | 2 | 20.15 | $0.0158 | 2,022 | 1,304 | 3,326 | 0 | ✅ PASS |
| simple_threshold_60min | `simple_threshold_60min.json` | 8/8 | 100.0% | 60.0 min | 5 | 1 | 8.86 | $0.0052 | 977 | 357 | 1,334 | 0 | ✅ PASS |
| tempo_sprints_combo | `tempo_sprints_combo.json` | 8/8 | 100.0% | 45.0 min | 14 | 3 | 42.41 | $0.0342 | 3,012 | 3,174 | 6,186 | 0 | ✅ PASS |
| threshold_4x8_detailed | `threshold_4x8_detailed.json` | 8/8 | 100.0% | 70.0 min | 9 | 1 | 10.58 | $0.0073 | 1,007 | 589 | 1,596 | 0 | ✅ PASS |
| threshold_5x6 | `threshold_5x6.json` | 8/8 | 100.0% | 61.0 min | 11 | 3 | 29.84 | $0.0254 | 3,006 | 2,165 | 5,171 | 0 | ✅ PASS |
| threshold_sprints_shorthand | `threshold_sprints_shorthand.json` | 8/8 | 100.0% | 75.0 min | 17 | 2 | 27.65 | $0.0236 | 2,030 | 2,203 | 4,233 | 0 | ✅ PASS |
| two_hour_tempo_climbing | `two_hour_tempo_climbing.json` | 8/8 | 100.0% | 120.0 min | 3 | 1 | 4.12 | $0.0042 | 990 | 236 | 1,226 | 0 | ✅ PASS |
| zwift_intervals_sprints | `zwift_intervals_sprints.json` | 8/8 | 100.0% | 80.0 min | 20 | 2 | 40.23 | $0.0264 | 2,032 | 2,531 | 4,563 | 0 | ✅ PASS |
| complex_progressive_blocks | `complex_progressive_blocks.json` | 7/8 | 87.5% | 64.0 min | 18 | 3 | 41.26 | $0.0284 | 3,156 | 2,471 | 5,627 | 1 | ⚠️ ISSUES |
| shorthand_notation | `shorthand_notation.json` | 7/8 | 87.5% | 90.0 min | 14 | 3 | 38.43 | $0.0313 | 3,006 | 2,849 | 5,855 | 1 | ⚠️ ISSUES |
| simple_tempo_block | `simple_tempo_block.json` | 7/8 | 87.5% | 60.0 min | 10 | 3 | 34.34 | $0.0211 | 2,970 | 1,678 | 4,648 | 1 | ⚠️ ISSUES |
| threshold_intervals_3x10 | `threshold_intervals_3x10.json` | 7/8 | 87.5% | 60.0 min | 11 | 3 | 32.78 | $0.0255 | 3,006 | 2,179 | 5,185 | 1 | ⚠️ ISSUES |

---

## Quality Metrics Deep Dive

### Workout Characteristics

- **Average Duration:** 73.2 minutes
- **Duration Range:** 45 - 120 minutes
- **Average Intervals:** 11.2
- **Interval Range:** 3 - 20

### Segment Type Distribution

| Segment Type | Count |
|--------------|-------|
| interval | 93 |
| recovery | 55 |
| warmup | 35 |
| cooldown | 23 |
| rest | 5 |
| other | 1 |

### Power Zone Time Distribution

| Zone | Total Time (min) |
|------|------------------|
| Zone 1 | 401.5 |
| Zone 2 | 318.5 |
| Zone 3 | 418.3 |
| Zone 4 | 149.3 |
| Zone 5 | 48.3 |
| Zone 6 | 47.0 |

---

## Issues & Anomalies

Found **4** validation issues:

### Issue #1: power_zone_accuracy

- **File:** `complex_progressive_blocks.json`
- **Prompt ID:** complex_progressive_blocks
- **Details:** 1 mismatch(es) found
  - Segment 10: Power 275W declared as Zone 4, actually Zone 5

### Issue #2: duration_consistency

- **File:** `shorthand_notation.json`
- **Prompt ID:** shorthand_notation
- **Details:** Duration mismatch: declared 5400s, calculated 4680s (diff: 720s)

### Issue #3: power_zone_accuracy

- **File:** `simple_tempo_block.json`
- **Prompt ID:** simple_tempo_block
- **Details:** 3 mismatch(es) found
  - Segment 2: Power 162W declared as Zone 3, actually Zone 2
  - Segment 3: Power 175W declared as Zone 3, actually Zone 2
  - Segment 7: Power 175W declared as Zone 3, actually Zone 2

### Issue #4: duration_consistency

- **File:** `threshold_intervals_3x10.json`
- **Prompt ID:** threshold_intervals_3x10
- **Details:** Duration mismatch: declared 3600s, calculated 3900s (diff: 300s)

---

## Statistical Summary

### Generation Performance Overview

- **Total Tokens:** 67,619
- **Total Cost:** $0.3386
- **Total Latency:** 446.61 seconds
- **Average Latency:** 23.51 seconds

### Token Statistics

| Metric | Input Tokens | Output Tokens | Total |
|--------|--------------|---------------|-------|
| **Total** | 38,301 | 29,318 | 67,619 |
| **Average per Workout** | 2016 | 1543 | 3559 |
| **Min** | 977 | 236 | - |
| **Max** | 3,156 | 3,174 | - |

### Cost Breakdown

| Metric | Input Cost | Output Cost | Total Cost |
|--------|------------|-------------|------------|
| **Total** | $0.0835 | $0.2551 | $0.3386 |
| **Average per Workout** | $0.0044 | $0.0134 | $0.0178 |
| **Min per Workout** | - | - | $0.0042 |
| **Max per Workout** | - | - | $0.0342 |

### Latency Statistics

| Metric | Latency (ms) | Latency (seconds) |
|--------|--------------|-------------------|
| **Total** | 446,606 | 446.61 |
| **Average** | 23506 | 23.51 |
| **Min** | 4,115 | 4.12 |
| **Max** | 42,414 | 42.41 |

### Attempt Distribution

| Attempts | Number of Workouts | Percentage |
|----------|-------------------|------------|
| 1 | 7 | 36.8% |
| 2 | 5 | 26.3% |
| 3 | 7 | 36.8% |

### Model Usage

| Model | Usage Count |
|-------|-------------|
| GPT-4o | 19 |

---

## Recommendations

### Files Requiring Attention (4 file(s))

- `complex_progressive_blocks.json` - Score: 7/8 (1 issue(s))
- `shorthand_notation.json` - Score: 7/8 (1 issue(s))
- `simple_tempo_block.json` - Score: 7/8 (1 issue(s))
- `threshold_intervals_3x10.json` - Score: 7/8 (1 issue(s))

### General Recommendations

1. Regularly review validation failures to maintain data quality
2. Consider adding more diverse workout types to improve test coverage
3. Ensure power zone calculations are accurate (most common failure point)
4. Verify time continuity in complex workout structures
