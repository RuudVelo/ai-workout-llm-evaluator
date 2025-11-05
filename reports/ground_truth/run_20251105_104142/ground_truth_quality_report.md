# Ground Truth Quality Evaluation Report

**Generated:** 2025-11-05T10:41:42.151680
**Source Directory:** `ground_truth/run_20251105_101841`
**Files Analyzed:** 40

---

## Executive Summary

- **Total Files:** 40
- **Passed All Validations:** 20
- **Overall Pass Rate:** 50.0%
- **Average Validation Score:** 89.7%

---

## Validation Results Overview

**Files passing all validations:** 20 / 40 (50.0%)

### Common Validation Failures

| Metric | Failure Count |
|--------|--------------|
| power_zone_accuracy | 18 |
| duration_consistency | 15 |

---

## Per-File Analysis

| Prompt ID | File | Score | Pass Rate | Duration | Intervals | Attempts | Latency (s) | Cost | In Tokens | Out Tokens | Total Tokens | Issues | Status |
|-----------|------|-------|-----------|----------|-----------|----------|-------------|------|-----------|------------|--------------|--------|--------|
| climbing_intervals_wattage | `climbing_intervals_wattage.json` | 8/8 | 100.0% | 59.5 min | 11 | 2 | 18.01 | $0.0176 | 2,144 | 1,485 | 3,629 | 0 | ✅ PASS |
| descending_pyramid_threshold | `descending_pyramid_threshold.json` | 8/8 | 100.0% | 52.0 min | 9 | 2 | 13.27 | $0.0151 | 2,148 | 1,201 | 3,349 | 0 | ✅ PASS |
| endurance_65_sprints | `endurance_65_sprints.json` | 8/8 | 100.0% | 60.0 min | 8 | 1 | 24.31 | $0.0073 | 1,077 | 573 | 1,650 | 0 | ✅ PASS |
| group_ride_surges | `group_ride_surges.json` | 8/8 | 100.0% | 65.0 min | 11 | 1 | 8.19 | $0.0085 | 1,074 | 705 | 1,779 | 0 | ✅ PASS |
| low_cadence_strength | `low_cadence_strength.json` | 8/8 | 100.0% | 79.0 min | 14 | 1 | 15.68 | $0.0109 | 1,103 | 975 | 2,078 | 0 | ✅ PASS |
| mixed_tabata_sweet_spot | `mixed_tabata_sweet_spot.json` | 8/8 | 100.0% | 90.0 min | 23 | 2 | 29.06 | $0.0289 | 2,188 | 2,778 | 4,966 | 0 | ✅ PASS |
| over_under_classic | `over_under_classic.json` | 8/8 | 100.0% | 42.0 min | 16 | 2 | 20.19 | $0.0235 | 2,148 | 2,158 | 4,306 | 0 | ✅ PASS |
| progressive_blocks | `progressive_blocks.json` | 8/8 | 100.0% | 55.0 min | 5 | 1 | 6.67 | $0.0054 | 1,070 | 350 | 1,420 | 0 | ✅ PASS |
| shorthand_notation | `shorthand_notation.json` | 8/8 | 100.0% | 90.0 min | 14 | 2 | 19.98 | $0.0205 | 2,136 | 1,821 | 3,957 | 0 | ✅ PASS |
| simple_tempo_block | `simple_tempo_block.json` | 8/8 | 100.0% | 60.0 min | 3 | 1 | 3.56 | $0.0042 | 1,056 | 221 | 1,277 | 0 | ✅ PASS |
| simple_threshold_60min | `simple_threshold_60min.json` | 8/8 | 100.0% | 60.0 min | 10 | 3 | 21.10 | $0.0211 | 3,129 | 1,647 | 4,776 | 0 | ✅ PASS |
| sweet_spot_blocks_no_explanation | `sweet_spot_blocks_no_explanation.json` | 8/8 | 100.0% | 120.0 min | 8 | 2 | 14.30 | $0.0137 | 2,124 | 1,039 | 3,163 | 0 | ✅ PASS |
| tempo_sprints_combo | `tempo_sprints_combo.json` | 8/8 | 100.0% | 40.0 min | 15 | 1 | 9.88 | $0.0112 | 1,070 | 1,022 | 2,092 | 0 | ✅ PASS |
| tempo_time_window | `tempo_time_window.json` | 8/8 | 100.0% | 60.0 min | 3 | 1 | 3.77 | $0.0043 | 1,072 | 221 | 1,293 | 0 | ✅ PASS |
| tempo_window_over_under | `tempo_window_over_under.json` | 8/8 | 100.0% | 75.0 min | 10 | 2 | 22.48 | $0.0163 | 2,222 | 1,319 | 3,541 | 0 | ✅ PASS |
| threshold_4x8_detailed | `threshold_4x8_detailed.json` | 8/8 | 100.0% | 95.0 min | 9 | 1 | 7.18 | $0.0074 | 1,073 | 580 | 1,653 | 0 | ✅ PASS |
| threshold_5x6 | `threshold_5x6.json` | 8/8 | 100.0% | 72.0 min | 12 | 2 | 18.54 | $0.0174 | 2,136 | 1,470 | 3,606 | 0 | ✅ PASS |
| threshold_sprints_shorthand | `threshold_sprints_shorthand.json` | 8/8 | 100.0% | 76.0 min | 18 | 2 | 28.37 | $0.0244 | 2,162 | 2,258 | 4,420 | 0 | ✅ PASS |
| two_hour_tempo_climbing | `two_hour_tempo_climbing.json` | 8/8 | 100.0% | 120.0 min | 5 | 1 | 4.47 | $0.0053 | 1,056 | 346 | 1,402 | 0 | ✅ PASS |
| warmup_15min | `warmup_15min.json` | 8/8 | 100.0% | 20.0 min | 7 | 1 | 10.25 | $0.0065 | 1,048 | 488 | 1,536 | 0 | ✅ PASS |
| fartlek | `fartlek.json` | 7/8 | 87.5% | 120.0 min | 11 | 3 | 45.12 | $0.0380 | 3,132 | 3,581 | 6,713 | 1 | ⚠️ ISSUES |
| over_under_sweet_spot | `over_under_sweet_spot.json` | 7/8 | 87.5% | 50.8 min | 16 | 3 | 41.77 | $0.0316 | 3,225 | 2,827 | 6,052 | 1 | ⚠️ ISSUES |
| ronnestad_tripe_set_no_explanation | `ronnestad_tripe_set_no_explanation.json` | 7/8 | 87.5% | 75.0 min | 22 | 3 | 107.25 | $0.0867 | 3,180 | 9,170 | 12,350 | 1 | ⚠️ ISSUES |
| sweet_spot_blocks_2to1_explanation | `sweet_spot_blocks_2to1_explanation.json` | 7/8 | 87.5% | 110.0 min | 8 | 3 | 20.80 | $0.0208 | 3,237 | 1,574 | 4,811 | 1 | ⚠️ ISSUES |
| sweet_spot_progression_time_based | `sweet_spot_progression_time_based.json` | 7/8 | 87.5% | 65.0 min | 5 | 3 | 17.65 | $0.0159 | 3,336 | 997 | 4,333 | 1 | ⚠️ ISSUES |
| tabata_sprints_explained | `tabata_sprints_explained.json` | 7/8 | 87.5% | 45.0 min | 35 | 3 | 55.47 | $0.0642 | 3,255 | 6,567 | 9,822 | 1 | ⚠️ ISSUES |
| tabata_sprints_no_explanation | `tabata_sprints_no_explanation.json` | 7/8 | 87.5% | 55.0 min | 46 | 3 | 71.45 | $0.0838 | 3,177 | 8,835 | 12,012 | 1 | ⚠️ ISSUES |
| ascending_descending_pyramid | `ascending_descending_pyramid.json` | 6/8 | 75.0% | 67.5 min | 13 | 3 | 31.89 | $0.0296 | 3,258 | 2,590 | 5,848 | 2 | ⚠️ ISSUES |
| ascending_pyramid_threshold | `ascending_pyramid_threshold.json` | 6/8 | 75.0% | 95.0 min | 9 | 3 | 22.36 | $0.0227 | 3,219 | 1,800 | 5,019 | 2 | ⚠️ ISSUES |
| fractional_threshold_2to1 | `fractional_threshold_2to1.json` | 6/8 | 75.0% | 60.0 min | 17 | 3 | 37.78 | $0.0350 | 3,276 | 3,200 | 6,476 | 2 | ⚠️ ISSUES |
| fractional_vo2max_efforts | `fractional_vo2max_efforts.json` | 6/8 | 75.0% | 42.0 min | 10 | 3 | 20.99 | $0.0238 | 3,201 | 1,936 | 5,137 | 2 | ⚠️ ISSUES |
| mixed_zones_progression | `mixed_zones_progression.json` | 6/8 | 75.0% | 95.0 min | 8 | 3 | 21.53 | $0.0213 | 3,216 | 1,638 | 4,854 | 2 | ⚠️ ISSUES |
| progressive_ftp_percentage | `progressive_ftp_percentage.json` | 6/8 | 75.0% | 100.5 min | 9 | 3 | 29.06 | $0.0231 | 3,201 | 1,855 | 5,056 | 2 | ⚠️ ISSUES |
| ramping_intervals | `ramping_intervals.json` | 6/8 | 75.0% | 91.0 min | 10 | 3 | 35.24 | $0.0316 | 3,231 | 2,827 | 6,058 | 2 | ⚠️ ISSUES |
| ronnestad_different | `ronnestad_different.json` | 6/8 | 75.0% | 91.0 min | 55 | 3 | 74.86 | $0.0973 | 3,255 | 10,371 | 13,626 | 2 | ⚠️ ISSUES |
| ronnestad_no_explanation | `ronnestad_no_explanation.json` | 6/8 | 75.0% | 49.0 min | 27 | 3 | 48.12 | $0.0510 | 3,156 | 5,076 | 8,232 | 2 | ⚠️ ISSUES |
| sweet_spot_2to1_ratio | `sweet_spot_2to1_ratio.json` | 6/8 | 75.0% | 210.0 min | 10 | 3 | 24.75 | $0.0252 | 3,219 | 2,094 | 5,313 | 2 | ⚠️ ISSUES |
| threshold_intervals_3x10 | `threshold_intervals_3x10.json` | 6/8 | 75.0% | 110.0 min | 7 | 3 | 25.81 | $0.0206 | 3,189 | 1,570 | 4,759 | 2 | ⚠️ ISSUES |
| zwift_complex_progressive_blocks | `zwift_complex_progressive_blocks.json` | 6/8 | 75.0% | 71.0 min | 16 | 3 | 47.19 | $0.0362 | 3,354 | 3,323 | 6,677 | 2 | ⚠️ ISSUES |
| zwift_intervals_sprints | `zwift_intervals_sprints.json` | 6/8 | 75.0% | 79.0 min | 24 | 3 | 73.42 | $0.0364 | 3,246 | 3,366 | 6,612 | 2 | ⚠️ ISSUES |

---

## Quality Metrics Deep Dive

### Workout Characteristics

- **Average Duration:** 76.8 minutes
- **Duration Range:** 20 - 210 minutes
- **Average Intervals:** 14.2
- **Interval Range:** 3 - 55

### Segment Type Distribution

| Segment Type | Count |
|--------------|-------|
| interval | 260 |
| recovery | 129 |
| rest | 65 |
| warmup | 51 |
| cooldown | 44 |
| active | 20 |

### Power Zone Time Distribution

| Zone | Total Time (min) |
|------|------------------|
| Zone 0 | 20.0 |
| Zone 1 | 398.2 |
| Zone 2 | 1098.0 |
| Zone 3 | 573.3 |
| Zone 4 | 408.8 |
| Zone 5 | 45.9 |
| Zone 6 | 121.8 |
| Zone 7 | 29.5 |

---

## Issues & Anomalies

Found **33** validation issues:

### Issue #1: duration_consistency

- **File:** `ascending_descending_pyramid.json`
- **Prompt ID:** ascending_descending_pyramid
- **Details:** Duration mismatch: declared 4050s, calculated 3540s (diff: 510s)

### Issue #2: power_zone_accuracy

- **File:** `ascending_descending_pyramid.json`
- **Prompt ID:** ascending_descending_pyramid
- **Details:** 5 mismatch(es) found
  - Segment 1: Power 125W declared as Zone 2, actually Zone 1
  - Segment 2: Power 225W declared as Zone 4, actually Zone 3
  - Segment 4: Power 225W declared as Zone 4, actually Zone 3

### Issue #3: duration_consistency

- **File:** `ascending_pyramid_threshold.json`
- **Prompt ID:** ascending_pyramid_threshold
- **Details:** Duration mismatch: declared 5700s, calculated 3240s (diff: 2460s)

### Issue #4: power_zone_accuracy

- **File:** `ascending_pyramid_threshold.json`
- **Prompt ID:** ascending_pyramid_threshold
- **Details:** 9 mismatch(es) found
  - Segment 1: Power 125W declared as Zone 2, actually Zone 1
  - Segment 2: Power 225W declared as Zone 4, actually Zone 3
  - Segment 3: Power 125W declared as Zone 2, actually Zone 1

### Issue #5: power_zone_accuracy

- **File:** `fartlek.json`
- **Prompt ID:** fartlek
- **Details:** 3 mismatch(es) found
  - Segment 2: Power 275W declared as Zone 6, actually Zone 5
  - Segment 6: Power 225W declared as Zone 4, actually Zone 3
  - Segment 10: Power 275W declared as Zone 6, actually Zone 5

### Issue #6: duration_consistency

- **File:** `fractional_threshold_2to1.json`
- **Prompt ID:** fractional_threshold_2to1
- **Details:** Duration mismatch: declared 3600s, calculated 2730s (diff: 870s)

### Issue #7: power_zone_accuracy

- **File:** `fractional_threshold_2to1.json`
- **Prompt ID:** fractional_threshold_2to1
- **Details:** 9 mismatch(es) found
  - Segment 1: Power 125W declared as Zone 2, actually Zone 1
  - Segment 3: Power 125W declared as Zone 2, actually Zone 1
  - Segment 5: Power 125W declared as Zone 2, actually Zone 1

### Issue #8: duration_consistency

- **File:** `fractional_vo2max_efforts.json`
- **Prompt ID:** fractional_vo2max_efforts
- **Details:** Duration mismatch: declared 2520s, calculated 1920s (diff: 600s)

### Issue #9: power_zone_accuracy

- **File:** `fractional_vo2max_efforts.json`
- **Prompt ID:** fractional_vo2max_efforts
- **Details:** 6 mismatch(es) found
  - Segment 1: Power 125W declared as Zone 2, actually Zone 1
  - Segment 3: Power 125W declared as Zone 2, actually Zone 1
  - Segment 5: Power 125W declared as Zone 2, actually Zone 1

### Issue #10: duration_consistency

- **File:** `mixed_zones_progression.json`
- **Prompt ID:** mixed_zones_progression
- **Details:** Duration mismatch: declared 5700s, calculated 4920s (diff: 780s)

### Issue #11: power_zone_accuracy

- **File:** `mixed_zones_progression.json`
- **Prompt ID:** mixed_zones_progression
- **Details:** 2 mismatch(es) found
  - Segment 4: Power 125W declared as Zone 2, actually Zone 1
  - Segment 6: Power 125W declared as Zone 2, actually Zone 1

### Issue #12: power_zone_accuracy

- **File:** `over_under_sweet_spot.json`
- **Prompt ID:** over_under_sweet_spot
- **Details:** 7 mismatch(es) found
  - Segment 2: Power 230W declared as Zone 4, actually Zone 3
  - Segment 4: Power 230W declared as Zone 4, actually Zone 3
  - Segment 6: Power 230W declared as Zone 4, actually Zone 3

### Issue #13: duration_consistency

- **File:** `progressive_ftp_percentage.json`
- **Prompt ID:** progressive_ftp_percentage
- **Details:** Duration mismatch: declared 6030s, calculated 4440s (diff: 1590s)

### Issue #14: power_zone_accuracy

- **File:** `progressive_ftp_percentage.json`
- **Prompt ID:** progressive_ftp_percentage
- **Details:** 2 mismatch(es) found
  - Segment 2: Power 213W declared as Zone 4, actually Zone 3
  - Segment 4: Power 225W declared as Zone 4, actually Zone 3

### Issue #15: duration_consistency

- **File:** `ramping_intervals.json`
- **Prompt ID:** ramping_intervals
- **Details:** Duration mismatch: declared 5460s, calculated 5100s (diff: 360s)

### Issue #16: power_zone_accuracy

- **File:** `ramping_intervals.json`
- **Prompt ID:** ramping_intervals
- **Details:** 4 mismatch(es) found
  - Segment 1: Power 125W declared as Zone 2, actually Zone 1
  - Segment 4: Power 219W declared as Zone 4, actually Zone 3
  - Segment 6: Power 225W declared as Zone 4, actually Zone 3

### Issue #17: duration_consistency

- **File:** `ronnestad_different.json`
- **Prompt ID:** ronnestad_different
- **Details:** Duration mismatch: declared 5460s, calculated 2730s (diff: 2730s)

### Issue #18: power_zone_accuracy

- **File:** `ronnestad_different.json`
- **Prompt ID:** ronnestad_different
- **Details:** 27 mismatch(es) found
  - Segment 1: Power 125W declared as Zone 2, actually Zone 1
  - Segment 3: Power 125W declared as Zone 2, actually Zone 1
  - Segment 5: Power 125W declared as Zone 2, actually Zone 1

### Issue #19: duration_consistency

- **File:** `ronnestad_no_explanation.json`
- **Prompt ID:** ronnestad_no_explanation
- **Details:** Duration mismatch: declared 2940s, calculated 2670s (diff: 270s)

### Issue #20: power_zone_accuracy

- **File:** `ronnestad_no_explanation.json`
- **Prompt ID:** ronnestad_no_explanation
- **Details:** 13 mismatch(es) found
  - Segment 2: Power 313W declared as Zone 7, actually Zone 6
  - Segment 4: Power 313W declared as Zone 7, actually Zone 6
  - Segment 6: Power 313W declared as Zone 7, actually Zone 6

### Issue #21: duration_consistency

- **File:** `ronnestad_tripe_set_no_explanation.json`
- **Prompt ID:** ronnestad_tripe_set_no_explanation
- **Details:** Duration mismatch: declared 4500s, calculated 3075s (diff: 1425s)

### Issue #22: duration_consistency

- **File:** `sweet_spot_2to1_ratio.json`
- **Prompt ID:** sweet_spot_2to1_ratio
- **Details:** Duration mismatch: declared 12600s, calculated 6960s (diff: 5640s)

### Issue #23: power_zone_accuracy

- **File:** `sweet_spot_2to1_ratio.json`
- **Prompt ID:** sweet_spot_2to1_ratio
- **Details:** 6 mismatch(es) found
  - Segment 1: Power 125W declared as Zone 2, actually Zone 1
  - Segment 2: Power 225W declared as Zone 4, actually Zone 3
  - Segment 4: Power 225W declared as Zone 4, actually Zone 3

### Issue #24: power_zone_accuracy

- **File:** `sweet_spot_blocks_2to1_explanation.json`
- **Prompt ID:** sweet_spot_blocks_2to1_explanation
- **Details:** 5 mismatch(es) found
  - Segment 1: Power 125W declared as Zone 2, actually Zone 1
  - Segment 3: Power 125W declared as Zone 2, actually Zone 1
  - Segment 5: Power 125W declared as Zone 2, actually Zone 1

### Issue #25: power_zone_accuracy

- **File:** `sweet_spot_progression_time_based.json`
- **Prompt ID:** sweet_spot_progression_time_based
- **Details:** 3 mismatch(es) found
  - Segment 1: Power 125W declared as Zone 2, actually Zone 1
  - Segment 3: Power 125W declared as Zone 2, actually Zone 1
  - Segment 5: Power 125W declared as Zone 2, actually Zone 1

### Issue #26: duration_consistency

- **File:** `tabata_sprints_explained.json`
- **Prompt ID:** tabata_sprints_explained
- **Details:** Duration mismatch: declared 2700s, calculated 2280s (diff: 420s)

### Issue #27: power_zone_accuracy

- **File:** `tabata_sprints_no_explanation.json`
- **Prompt ID:** tabata_sprints_no_explanation
- **Details:** 2 mismatch(es) found
  - Segment 16: Power 150W declared as Zone 1, actually Zone 2
  - Segment 31: Power 150W declared as Zone 1, actually Zone 2

### Issue #28: duration_consistency

- **File:** `threshold_intervals_3x10.json`
- **Prompt ID:** threshold_intervals_3x10
- **Details:** Duration mismatch: declared 6600s, calculated 3900s (diff: 2700s)

### Issue #29: power_zone_accuracy

- **File:** `threshold_intervals_3x10.json`
- **Prompt ID:** threshold_intervals_3x10
- **Details:** 4 mismatch(es) found
  - Segment 1: Power 125W declared as Zone 2, actually Zone 1
  - Segment 3: Power 125W declared as Zone 2, actually Zone 1
  - Segment 5: Power 125W declared as Zone 2, actually Zone 1

### Issue #30: duration_consistency

- **File:** `zwift_complex_progressive_blocks.json`
- **Prompt ID:** zwift_complex_progressive_blocks
- **Details:** Duration mismatch: declared 4260s, calculated 2580s (diff: 1680s)

### Issue #31: power_zone_accuracy

- **File:** `zwift_complex_progressive_blocks.json`
- **Prompt ID:** zwift_complex_progressive_blocks
- **Details:** 2 mismatch(es) found
  - Segment 10: Power 275W declared as Zone 4, actually Zone 5
  - Segment 13: Power 0W declared as Zone 0, actually Zone 1

### Issue #32: duration_consistency

- **File:** `zwift_intervals_sprints.json`
- **Prompt ID:** zwift_intervals_sprints
- **Details:** Duration mismatch: declared 4740s, calculated 4170s (diff: 570s)

### Issue #33: power_zone_accuracy

- **File:** `zwift_intervals_sprints.json`
- **Prompt ID:** zwift_intervals_sprints
- **Details:** 4 mismatch(es) found
  - Segment 1: Power 125W declared as Zone 2, actually Zone 1
  - Segment 5: Power 175W declared as Zone 3, actually Zone 2
  - Segment 20: Power 175W declared as Zone 3, actually Zone 2

---

## Statistical Summary

### Generation Performance Overview

- **Total Tokens:** 195,653
- **Total Cost:** $1.0645
- **Total Latency:** 1151.78 seconds
- **Average Latency:** 28.79 seconds

### Token Statistics

| Metric | Input Tokens | Output Tokens | Total |
|--------|--------------|---------------|-------|
| **Total** | 97,799 | 97,854 | 195,653 |
| **Average per Workout** | 2445 | 2446 | 4891 |
| **Min** | 1,048 | 221 | - |
| **Max** | 3,354 | 10,371 | - |

### Cost Breakdown

| Metric | Input Cost | Output Cost | Total Cost |
|--------|------------|-------------|------------|
| **Total** | $0.2132 | $0.8513 | $1.0645 |
| **Average per Workout** | $0.0053 | $0.0213 | $0.0266 |
| **Min per Workout** | - | - | $0.0042 |
| **Max per Workout** | - | - | $0.0973 |

### Latency Statistics

| Metric | Latency (ms) | Latency (seconds) |
|--------|--------------|-------------------|
| **Total** | 1,151,781 | 1151.78 |
| **Average** | 28795 | 28.79 |
| **Min** | 3,558 | 3.56 |
| **Max** | 107,254 | 107.25 |

### Attempt Distribution

| Attempts | Number of Workouts | Percentage |
|----------|-------------------|------------|
| 1 | 10 | 25.0% |
| 2 | 9 | 22.5% |
| 3 | 21 | 52.5% |

### Model Usage

| Model | Usage Count |
|-------|-------------|
| GPT-4o | 40 |

---

## Recommendations

### Files Requiring Attention (20 file(s))

- `fartlek.json` - Score: 7/8 (1 issue(s))
- `over_under_sweet_spot.json` - Score: 7/8 (1 issue(s))
- `ronnestad_tripe_set_no_explanation.json` - Score: 7/8 (1 issue(s))
- `sweet_spot_blocks_2to1_explanation.json` - Score: 7/8 (1 issue(s))
- `sweet_spot_progression_time_based.json` - Score: 7/8 (1 issue(s))
- `tabata_sprints_explained.json` - Score: 7/8 (1 issue(s))
- `tabata_sprints_no_explanation.json` - Score: 7/8 (1 issue(s))
- `ascending_descending_pyramid.json` - Score: 6/8 (2 issue(s))
- `ascending_pyramid_threshold.json` - Score: 6/8 (2 issue(s))
- `fractional_threshold_2to1.json` - Score: 6/8 (2 issue(s))
- `fractional_vo2max_efforts.json` - Score: 6/8 (2 issue(s))
- `mixed_zones_progression.json` - Score: 6/8 (2 issue(s))
- `progressive_ftp_percentage.json` - Score: 6/8 (2 issue(s))
- `ramping_intervals.json` - Score: 6/8 (2 issue(s))
- `ronnestad_different.json` - Score: 6/8 (2 issue(s))
- `ronnestad_no_explanation.json` - Score: 6/8 (2 issue(s))
- `sweet_spot_2to1_ratio.json` - Score: 6/8 (2 issue(s))
- `threshold_intervals_3x10.json` - Score: 6/8 (2 issue(s))
- `zwift_complex_progressive_blocks.json` - Score: 6/8 (2 issue(s))
- `zwift_intervals_sprints.json` - Score: 6/8 (2 issue(s))

### General Recommendations

1. Regularly review validation failures to maintain data quality
2. Consider adding more diverse workout types to improve test coverage
3. Ensure power zone calculations are accurate (most common failure point)
4. Verify time continuity in complex workout structures
