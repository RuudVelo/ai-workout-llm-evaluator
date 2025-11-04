# Ground Truth Quality Evaluation Report

**Generated:** 2025-11-04T14:51:18.197766
**Source Directory:** `ground_truth`
**Files Analyzed:** 19

---

## Executive Summary

- **Total Files:** 19
- **Passed All Validations:** 13
- **Overall Pass Rate:** 68.4%
- **Average Validation Score:** 95.4%

---

## Validation Results Overview

**Files passing all validations:** 13 / 19 (68.4%)

### Common Validation Failures

| Metric | Failure Count |
|--------|--------------|
| duration_consistency | 6 |
| power_zone_accuracy | 1 |

---

## Per-File Analysis

| Prompt ID | File | Score | Pass Rate | Duration | Intervals | Attempts | Latency (s) | Cost | In Tokens | Out Tokens | Total Tokens | Issues | Status |
|-----------|------|-------|-----------|----------|-----------|----------|-------------|------|-----------|------------|--------------|--------|--------|
| climbing_intervals_wattage | `climbing_intervals_wattage.json` | 8/8 | 100.0% | 68.0 min | 12 | 2 | 30.90 | $0.0204 | 2,628 | 1,684 | 4,312 | 0 | ✅ PASS |
| endurance_65_sprints | `endurance_65_sprints.json` | 8/8 | 100.0% | 60.0 min | 5 | 1 | 7.15 | $0.0061 | 1,319 | 367 | 1,686 | 0 | ✅ PASS |
| group_ride_surges | `group_ride_surges.json` | 8/8 | 100.0% | 65.0 min | 11 | 1 | 11.31 | $0.0094 | 1,316 | 752 | 2,068 | 0 | ✅ PASS |
| progressive_blocks | `progressive_blocks.json` | 8/8 | 100.0% | 55.0 min | 8 | 1 | 10.04 | $0.0077 | 1,312 | 552 | 1,864 | 0 | ✅ PASS |
| shorthand_notation | `shorthand_notation.json` | 8/8 | 100.0% | 75.0 min | 14 | 1 | 14.04 | $0.0111 | 1,310 | 945 | 2,255 | 0 | ✅ PASS |
| simple_tempo_block | `simple_tempo_block.json` | 8/8 | 100.0% | 60.0 min | 11 | 3 | 35.95 | $0.0248 | 3,894 | 1,880 | 5,774 | 0 | ✅ PASS |
| simple_threshold_60min | `simple_threshold_60min.json` | 8/8 | 100.0% | 60.0 min | 9 | 1 | 10.79 | $0.0080 | 1,285 | 596 | 1,881 | 0 | ✅ PASS |
| tempo_sprints_combo | `tempo_sprints_combo.json` | 8/8 | 100.0% | 40.0 min | 19 | 1 | 24.67 | $0.0130 | 1,312 | 1,171 | 2,483 | 0 | ✅ PASS |
| threshold_4x8_detailed | `threshold_4x8_detailed.json` | 8/8 | 100.0% | 74.7 min | 10 | 1 | 10.23 | $0.0085 | 1,315 | 646 | 1,961 | 0 | ✅ PASS |
| threshold_intervals_3x10 | `threshold_intervals_3x10.json` | 8/8 | 100.0% | 60.0 min | 9 | 1 | 11.94 | $0.0081 | 1,310 | 605 | 1,915 | 0 | ✅ PASS |
| threshold_sprints_shorthand | `threshold_sprints_shorthand.json` | 8/8 | 100.0% | 83.0 min | 17 | 2 | 35.96 | $0.0254 | 2,646 | 2,260 | 4,906 | 0 | ✅ PASS |
| two_hour_tempo_climbing | `two_hour_tempo_climbing.json` | 8/8 | 100.0% | 120.0 min | 5 | 2 | 14.61 | $0.0121 | 2,596 | 741 | 3,337 | 0 | ✅ PASS |
| zwift_intervals_sprints | `zwift_intervals_sprints.json` | 8/8 | 100.0% | 70.0 min | 20 | 2 | 43.92 | $0.0282 | 2,648 | 2,580 | 5,228 | 0 | ✅ PASS |
| complex_progressive_blocks | `complex_progressive_blocks.json` | 7/8 | 87.5% | 67.0 min | 13 | 3 | 50.48 | $0.0359 | 4,080 | 3,108 | 7,188 | 1 | ⚠️ ISSUES |
| low_cadence_strength | `low_cadence_strength.json` | 7/8 | 87.5% | 96.0 min | 14 | 3 | 53.32 | $0.0348 | 4,035 | 2,993 | 7,028 | 1 | ⚠️ ISSUES |
| mixed_zones_progression | `mixed_zones_progression.json` | 7/8 | 87.5% | 75.0 min | 8 | 3 | 34.46 | $0.0233 | 3,942 | 1,691 | 5,633 | 1 | ⚠️ ISSUES |
| ramping_intervals | `ramping_intervals.json` | 7/8 | 87.5% | 90.0 min | 25 | 3 | 113.24 | $0.0344 | 3,957 | 2,961 | 6,918 | 1 | ⚠️ ISSUES |
| threshold_5x6 | `threshold_5x6.json` | 7/8 | 87.5% | 74.0 min | 12 | 3 | 76.38 | $0.0295 | 3,930 | 2,401 | 6,331 | 1 | ⚠️ ISSUES |
| progressive_ftp_percentage | `progressive_ftp_percentage.json` | 6/8 | 75.0% | 82.2 min | 9 | 3 | 35.27 | $0.0244 | 3,927 | 1,815 | 5,742 | 2 | ⚠️ ISSUES |

---

## Quality Metrics Deep Dive

### Workout Characteristics

- **Average Duration:** 72.4 minutes
- **Duration Range:** 40 - 120 minutes
- **Average Intervals:** 12.2
- **Interval Range:** 5 - 25

### Segment Type Distribution

| Segment Type | Count |
|--------------|-------|
| interval | 110 |
| recovery | 52 |
| warmup | 35 |
| cooldown | 22 |
| rest | 11 |
| other | 1 |

### Power Zone Time Distribution

| Zone | Total Time (min) |
|------|------------------|
| Zone 1 | 386.2 |
| Zone 2 | 345.7 |
| Zone 3 | 354.3 |
| Zone 4 | 145.3 |
| Zone 5 | 11.3 |
| Zone 6 | 82.5 |
| Zone 7 | 0.3 |

---

## Issues & Anomalies

Found **7** validation issues:

### Issue #1: duration_consistency

- **File:** `complex_progressive_blocks.json`
- **Prompt ID:** complex_progressive_blocks
- **Details:** Duration mismatch: declared 4020s, calculated 2880s (diff: 1140s)

### Issue #2: duration_consistency

- **File:** `low_cadence_strength.json`
- **Prompt ID:** low_cadence_strength
- **Details:** Duration mismatch: declared 5760s, calculated 5640s (diff: 120s)

### Issue #3: duration_consistency

- **File:** `mixed_zones_progression.json`
- **Prompt ID:** mixed_zones_progression
- **Details:** Duration mismatch: declared 4500s, calculated 5100s (diff: 600s)

### Issue #4: duration_consistency

- **File:** `progressive_ftp_percentage.json`
- **Prompt ID:** progressive_ftp_percentage
- **Details:** Duration mismatch: declared 4935s, calculated 5340s (diff: 405s)

### Issue #5: power_zone_accuracy

- **File:** `progressive_ftp_percentage.json`
- **Prompt ID:** progressive_ftp_percentage
- **Details:** 1 mismatch(es) found
  - Segment 4: Power 225W declared as Zone 4, actually Zone 3

### Issue #6: duration_consistency

- **File:** `ramping_intervals.json`
- **Prompt ID:** ramping_intervals
- **Details:** Duration mismatch: declared 5400s, calculated 3240s (diff: 2160s)

### Issue #7: duration_consistency

- **File:** `threshold_5x6.json`
- **Prompt ID:** threshold_5x6
- **Details:** Duration mismatch: declared 4440s, calculated 3900s (diff: 540s)

---

## Statistical Summary

### Generation Performance Overview

- **Total Tokens:** 78,510
- **Total Cost:** $0.3651
- **Total Latency:** 624.66 seconds
- **Average Latency:** 32.88 seconds

### Token Statistics

| Metric | Input Tokens | Output Tokens | Total |
|--------|--------------|---------------|-------|
| **Total** | 48,762 | 29,748 | 78,510 |
| **Average per Workout** | 2566 | 1566 | 4132 |
| **Min** | 1,285 | 367 | - |
| **Max** | 4,080 | 3,108 | - |

### Cost Breakdown

| Metric | Input Cost | Output Cost | Total Cost |
|--------|------------|-------------|------------|
| **Total** | $0.1063 | $0.2588 | $0.3651 |
| **Average per Workout** | $0.0056 | $0.0136 | $0.0192 |
| **Min per Workout** | - | - | $0.0061 |
| **Max per Workout** | - | - | $0.0359 |

### Latency Statistics

| Metric | Latency (ms) | Latency (seconds) |
|--------|--------------|-------------------|
| **Total** | 624,660 | 624.66 |
| **Average** | 32877 | 32.88 |
| **Min** | 7,151 | 7.15 |
| **Max** | 113,237 | 113.24 |

### Attempt Distribution

| Attempts | Number of Workouts | Percentage |
|----------|-------------------|------------|
| 1 | 8 | 42.1% |
| 2 | 4 | 21.1% |
| 3 | 7 | 36.8% |

### Model Usage

| Model | Usage Count |
|-------|-------------|
| GPT-4o | 19 |

---

## Recommendations

### Files Requiring Attention (6 file(s))

- `complex_progressive_blocks.json` - Score: 7/8 (1 issue(s))
- `low_cadence_strength.json` - Score: 7/8 (1 issue(s))
- `mixed_zones_progression.json` - Score: 7/8 (1 issue(s))
- `ramping_intervals.json` - Score: 7/8 (1 issue(s))
- `threshold_5x6.json` - Score: 7/8 (1 issue(s))
- `progressive_ftp_percentage.json` - Score: 6/8 (2 issue(s))

### General Recommendations

1. Regularly review validation failures to maintain data quality
2. Consider adding more diverse workout types to improve test coverage
3. Ensure power zone calculations are accurate (most common failure point)
4. Verify time continuity in complex workout structures
