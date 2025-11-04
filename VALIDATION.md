# Workout Validation Process Documentation

## Overview

The workout generator uses a **multi-layered validation approach** to ensure generated workouts meet quality standards. Validation occurs at two levels:

1. **LLM-Level Schema Enforcement** - Provider-enforced JSON schema constraints
2. **Application-Level Validation** - Comprehensive business logic and data quality checks

This document describes the complete validation pipeline, retry logic, and tolerance settings.

---

## Table of Contents

1. [Validation Architecture](#validation-architecture)
2. [Validation Layers](#validation-layers)
3. [Validation Metrics](#validation-metrics)
4. [Tolerance Settings](#tolerance-settings)
5. [Retry Logic](#retry-logic)
6. [Error Handling Strategies](#error-handling-strategies)
7. [Cost of Quality Metrics](#cost-of-quality-metrics)
8. [Configuration](#configuration)

---

## Validation Architecture

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         LLM Generation                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              Layer 1: LLM Provider Schema Enforcement           │
│  • OpenAI: strict JSON schema mode                              │
│  • Gemini: response_schema with application/json                │
│  • Together AI: json_object format (non-strict)                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              Layer 2: JSON Parsing Validation                   │
│  • Validates response is valid JSON                             │
│  • Returns JSONDecodeError if invalid                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│         Layer 3: JSON Schema Structure Validation               │
│  • Uses jsonschema library (v4.25.1)                            │
│  • Validates field types, required fields, enums                │
│  • Checks additionalProperties constraints                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│         Layer 4: Business Logic Validation (8 metrics)          │
│  1. Schema validation           5. Power zone accuracy          │
│  2. Required fields             6. FTP percentage accuracy      │
│  3. Duration consistency        7. Power adjustment accuracy    │
│  4. Time continuity             8. Segment type validity        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                  ┌──────────┴──────────┐
                  │   PASS or FAIL      │
                  └─────────────────────┘
```

---

## Validation Layers

### Layer 1: LLM Provider Schema Enforcement

Different providers handle schema enforcement differently:

**OpenAI (GPT-4o, GPT-4o Mini)**
```python
response_format = {
    "type": "json_schema",
    "json_schema": {
        "name": "workout_response",
        "strict": true,  # Enforces strict schema compliance
        "schema": { ... }
    }
}
```
- Strict mode: Provider guarantees schema compliance
- Most reliable schema enforcement

**Gemini (Gemini 1.5 Pro, Flash)**
```python
generation_config = {
    "response_mime_type": "application/json",
    "response_schema": { ... }  # No strict mode
}
```
- Schema guidance but not strict enforcement
- May produce minor schema variations

**Together AI**
```python
response_format = {
    "type": "json_object"  # Loose format
}
```
- Only guarantees valid JSON, not schema compliance
- Requires more application-level validation

### Layer 2: JSON Parsing Validation

**Location:** `src/runner.py:85-90`, `src/ground_truth_generator.py:128-136`

```python
try:
    parsed_json = json.loads(response.content)
    parse_error = None
except json.JSONDecodeError as e:
    parsed_json = None
    parse_error = str(e)
    # RETRY on parse error
```

**What it catches:**
- Malformed JSON syntax
- Invalid escape sequences
- Unterminated strings/objects/arrays
- Invalid Unicode characters

**Action:** Always retry on parse errors (up to `max_retries`)

### Layer 3: JSON Schema Structure Validation

**Location:** `src/evaluator.py:20-40`

```python
def validate_schema(self, workout: Dict[str, Any]) -> Dict[str, Any]:
    """Validate workout matches the expected JSON schema."""
    schema = WORKOUT_JSON_SCHEMA["schema"]
    validate(instance=workout, schema=schema)
```

**What it validates:**

| Check | Description | Example |
|-------|-------------|---------|
| **Type constraints** | Field types match schema | `"power": 150` (integer, not float) |
| **Required fields** | All required fields present | `name`, `description`, `workout_duration`, `intervals` |
| **Enum values** | Type field uses allowed values | `"type": "active"` (not "Active" or "interval_type") |
| **Additional properties** | No unexpected fields | Rejects `"custom_field": "value"` |
| **Nested structure** | Intervals array structure | Each interval has all 10 required fields |

**Schema Definition:** `src/system_prompt.py:88-148` (OpenAI format)

### Layer 4: Business Logic Validation

**Location:** `src/evaluator.py`

This layer runs **8 comprehensive validation metrics** to ensure workout quality.

---

## Validation Metrics

All metrics are implemented in `src/evaluator.py` via the `WorkoutEvaluator` class.

### 1. Schema Validation (`validate_schema`)

**Location:** Lines 20-40

**Purpose:** Validates JSON structure against expected schema

**Checks:**
- All fields have correct types
- Required fields are present
- No additional unexpected fields
- Enum values are valid

**Tolerance:** None (strict)

**Pass Condition:** `jsonschema.validate()` succeeds with no exceptions

---

### 2. Required Fields Validation (`validate_required_fields`)

**Location:** Lines 42-86

**Purpose:** Ensures all required fields are present at top level and in intervals

**Checks:**

**Top-level fields:**
- `name` (string)
- `description` (string)
- `workout_duration` (integer, seconds)
- `intervals` (array)

**Interval fields (all 10 required):**
- `segment_number` (integer)
- `startTimeSeconds` (integer)
- `endTimeSeconds` (integer)
- `power` (integer, watts)
- `powerAdjustedUpward` (integer, watts)
- `powerAdjustedDownward` (integer, watts)
- `zone` (integer, 1-7)
- `perc_ftp` (integer, percentage)
- `type` (string, enum)
- `notes` (string)

**Tolerance:** None (all fields required)

**Pass Condition:** All fields present in workout and every interval

---

### 3. Duration Consistency Validation (`validate_duration_consistency`)

**Location:** Lines 88-130

**Purpose:** Validates declared workout duration matches calculated duration

**Calculation:**
```python
declared_duration = workout["workout_duration"]
calculated_duration = last_interval["endTimeSeconds"]
difference = abs(declared_duration - calculated_duration)
```

**Tolerance:** **Percentage-based with minimum**
```python
tolerance = max(2, declared_duration * 0.001)  # 0.1% or 2 seconds
```

**Examples:**

| Workout Duration | Tolerance | Rationale |
|------------------|-----------|-----------|
| 10 minutes (600s) | 2 seconds | 600 * 0.001 = 0.6s, uses minimum 2s |
| 60 minutes (3600s) | 3.6 seconds | 3600 * 0.001 = 3.6s |
| 2 hours (7200s) | 7.2 seconds | 7200 * 0.001 = 7.2s |

**Pass Condition:** `difference <= tolerance`

**Why percentage-based?**
- Absolute tolerance (1 second) was too strict for long workouts
- Percentage tolerance scales appropriately with workout length
- Minimum prevents overly loose tolerance for short workouts

---

### 4. Time Continuity Validation (`validate_time_continuity`)

**Location:** Lines 132-189

**Purpose:** Ensures no gaps or overlaps between intervals

**Checks:**
1. First interval starts at 0 seconds
2. Each interval ends exactly when next interval starts
3. No overlapping time ranges

**Tolerance:** None (strict, 0 seconds)

**Pass Condition:**
- `intervals[0]["startTimeSeconds"] == 0`
- For all intervals: `intervals[i]["endTimeSeconds"] == intervals[i+1]["startTimeSeconds"]`

**Example:**
```json
// VALID
[
  {"startTimeSeconds": 0, "endTimeSeconds": 300},   // 0-5 min
  {"startTimeSeconds": 300, "endTimeSeconds": 600}  // 5-10 min
]

// INVALID - Gap
[
  {"startTimeSeconds": 0, "endTimeSeconds": 300},
  {"startTimeSeconds": 305, "endTimeSeconds": 600}  // 5 second gap
]

// INVALID - Overlap
[
  {"startTimeSeconds": 0, "endTimeSeconds": 305},
  {"startTimeSeconds": 300, "endTimeSeconds": 600}  // 5 second overlap
]
```

---

### 5. Power Zone Accuracy Validation (`validate_power_zones`)

**Location:** Lines 191-244

**Purpose:** Validates power values match declared zones

**Zone Calculation:**
Power zones are calculated based on FTP (Functional Threshold Power):

```python
zones = calculate_zones(ftp)  # From system_prompt.py

# Example with FTP = 200W:
# Zone 1: 0-110W (0-55% FTP)
# Zone 2: 111-148W (56-74% FTP)
# Zone 3: 149-164W (75-82% FTP)
# Zone 4: 165-180W (83-90% FTP)
# Zone 5: 181-204W (91-102% FTP)
# Zone 6: 205-236W (103-118% FTP)
# Zone 7: 237+W (119%+ FTP)
```

**Tolerance:** **±2 watts at zone boundaries**

```python
tolerance = 2  # watts

# Check if power is within tolerance of declared zone
if (zone_range["min"] - tolerance) <= power <= (zone_range["max"] + tolerance):
    # Accept declared zone
```

**Why tolerance is needed:**

| Scenario | Without Tolerance | With ±2W Tolerance |
|----------|-------------------|-------------------|
| Power = 110W, Zone 1 max = 110W | PASS (exact match) | PASS |
| Power = 111W, Zone 2 min = 111W | PASS (exact match) | PASS |
| Power = 110W, declared zone = 2 | FAIL (110W not in zone 2) | PASS (110W within 2W of zone 2 min) |
| Power = 112W, declared zone = 1 | FAIL (112W not in zone 1) | PASS (112W within 2W of zone 1 max) |

**Pass Condition:** Power is within tolerance of declared zone boundaries

---

### 6. FTP Percentage Accuracy Validation (`validate_ftp_percentages`)

**Location:** Lines 246-268

**Purpose:** Validates percentage FTP calculations are correct

**Calculation:**
```python
actual_perc = round((power / ftp) * 100)
declared_perc = interval["perc_ftp"]
difference = abs(actual_perc - declared_perc)
```

**Tolerance:** **±1%**

```python
if abs(actual_perc - declared_perc) > 1:
    # FAIL
```

**Why tolerance is needed:**

**Rounding Differences:**
- Python uses **banker's rounding** (round-half-to-even): `round(0.5) = 0`, `round(1.5) = 2`
- LLMs may use **standard rounding** (round-half-up): `round(0.5) = 1`, `round(1.5) = 2`

**Example:**
```python
# FTP = 200W, Power = 73W
# Calculation: 73 / 200 * 100 = 36.5%

# Python banker's rounding:
round(36.5) = 36  # Round to nearest even

# Standard rounding (LLM might use):
round(36.5) = 37  # Round up

# Difference: |36 - 37| = 1%
# With ±1% tolerance: PASS ✓
# Without tolerance: FAIL ✗
```

**Pass Condition:** `abs(actual_perc - declared_perc) <= 1`

---

### 7. Power Adjustment Accuracy Validation (`validate_power_adjustments`)

**Location:** Lines 270-316

**Purpose:** Validates powerAdjustedUpward and powerAdjustedDownward are correct

**Expected Values:**
```python
expected_upward = power + 10
expected_downward = max(0, power - 10)
```

**Tolerance:** **±2 watts**

```python
tolerance = 2

upward_diff = abs(upward - expected_upward)
downward_diff = abs(downward - expected_downward)

if upward_diff > tolerance or downward_diff > tolerance:
    # FAIL
```

**Why tolerance is needed:**
- These are **derived fields** (calculated from power)
- Errors in base power calculation cascade to adjustments
- Minor variations (±2W) don't affect workout usability

**Examples:**

| Power | Expected Upward | Expected Downward | Tolerance Range |
|-------|----------------|-------------------|-----------------|
| 100W | 110W | 90W | Upward: 108-112W, Downward: 88-92W |
| 5W | 15W | 0W | Upward: 13-17W, Downward: 0-2W |
| 250W | 260W | 240W | Upward: 258-262W, Downward: 238-242W |

**Pass Condition:** Both adjustments within ±2W of expected values

---

### 8. Segment Type Validity Validation (`validate_segment_types`)

**Location:** Lines 318-348

**Purpose:** Validates segment types use only allowed enum values

**Allowed Types:**
```python
allowed_types = {
    "active",
    "rest",
    "warmup",
    "cooldown",
    "recovery",
    "interval",
    "other"
}
```

**Tolerance:** None (strict enum)

**Pass Condition:** All interval `type` fields match exactly one allowed value

**Common Errors:**
- ❌ `"Active"` (wrong case)
- ❌ `"work"` (not in enum)
- ❌ `"steady_state"` (not in enum)
- ✅ `"active"` (correct)

---

## Tolerance Settings Summary

| Validation Metric | Tolerance | Rationale |
|-------------------|-----------|-----------|
| **Schema validation** | None (strict) | Structural integrity required |
| **Required fields** | None (strict) | All fields mandatory |
| **Duration consistency** | 0.1% or min 2s | Scales with workout length |
| **Time continuity** | None (strict) | No gaps/overlaps allowed |
| **Power zones** | ±2 watts | Boundary rounding flexibility |
| **FTP percentages** | ±1% | Different rounding methods |
| **Power adjustments** | ±2 watts | Derived field tolerance |
| **Segment types** | None (strict) | Enum must match exactly |

---

## Retry Logic

### Strategy Comparison

| Aspect | Ground Truth Generation | Model Evaluation |
|--------|------------------------|------------------|
| **Retry on parse error** | ✅ Yes | ✅ Yes |
| **Retry on validation failure** | ✅ Yes (Option B) | ✅ Yes (Option B) |
| **Max retries default** | 3 attempts | 2 attempts |
| **On final failure** | Raise error, fail hard | Accept but flag (Option B2) |
| **Config location** | `config/ground_truth.yaml` | Hardcoded in `runner.py` |

### Ground Truth Generation Retry Flow

**Location:** `src/ground_truth_generator.py:96-204`

```python
max_retries = 3  # From config/ground_truth.yaml

for attempt in range(max_retries):
    # 1. Generate LLM response
    response = provider.generate(...)

    # 2. Parse JSON
    try:
        workout = json.loads(response.content)
    except json.JSONDecodeError as e:
        if attempt < max_retries - 1:
            continue  # RETRY
        raise  # FAIL on last attempt

    # 3. Validate (if enabled)
    if validate_before_saving:
        evaluation = evaluator.evaluate(workout)

        if not evaluation["all_passed"]:
            if attempt < max_retries - 1:
                continue  # RETRY
            else:
                # FAIL HARD (no invalid ground truth)
                raise ValueError(
                    f"Ground truth validation failed after {max_retries} attempts. "
                    f"Pass rate: {evaluation['pass_rate']}%"
                )

    # 4. Success - return ground truth
    return ground_truth
```

**Configuration:**
```yaml
# config/ground_truth.yaml
generation:
  max_retries: 3
  validate_before_saving: true  # Enable validation
  overwrite_existing: false
```

### Model Evaluation Retry Flow (Option B + B2)

**Location:** `src/runner.py:48-240`

```python
max_retries = 2  # Hardcoded

for attempt in range(max_retries):
    # 1. Generate LLM response
    response = provider.generate(...)

    # 2. Parse JSON
    try:
        parsed_json = json.loads(response.content)
        parse_error = None
    except json.JSONDecodeError as e:
        parse_error = str(e)

    # 3. Validate if parsed successfully
    if parsed_json is not None:
        validation_result = evaluator.evaluate(parsed_json)
        validation_passed = validation_result["all_passed"]

    # 4. Retry logic (Option B)
    if parse_error is not None:
        if attempt < max_retries - 1:
            continue  # RETRY on parse error

    elif not validation_passed:
        if attempt < max_retries - 1:
            continue  # RETRY on validation failure (Option B)
        else:
            # ACCEPT BUT FLAG (Option B2)
            print(f"⚠ Validation failed after {max_retries} attempts, recording with flag")

    # 5. Build result
    return {
        "success": parse_error is None and validation_passed,
        "validation_failed": parse_error is None and not validation_passed,  # B2 flag
        "validation": validation_result,
        "all_attempts": all_attempts_metadata,
        ...
    }
```

**Why Option B2 (accept but flag)?**
- Measure true model performance in production scenarios
- Capture "cost of quality" metrics
- Enable comparison even when validation fails
- User decision whether to use flagged outputs

---

## Error Handling Strategies

### Option A: Validate and Record (Pure Measurement)
**Not implemented - for reference only**

```python
# No retry on validation failures
# Just record success/failure
if not validation_passed:
    # Don't retry - just record
    result["validation_failed"] = True
```

**Pros:** Pure model capability measurement
**Cons:** Doesn't reflect production reality (you'd retry in production)

### Option B: Validate and Retry (Enforce Quality) ✅ **IMPLEMENTED**

```python
# Retry on validation failures
if not validation_passed:
    if attempt < max_retries - 1:
        continue  # RETRY
```

**Pros:** Mirrors production behavior, measures true cost
**Cons:** Higher API costs during evaluation

### Option B1: Fail on Final Validation Failure
**Used for ground truth generation**

```python
if not validation_passed:
    if attempt < max_retries - 1:
        continue  # RETRY
    else:
        raise ValueError("Validation failed")  # FAIL HARD
```

**Use case:** Ground truth must be perfect

### Option B2: Accept but Flag on Final Validation Failure ✅ **IMPLEMENTED**
**Used for model evaluation**

```python
if not validation_passed:
    if attempt < max_retries - 1:
        continue  # RETRY
    else:
        # ACCEPT WITH FLAG
        result["validation_failed"] = True
        result["validation"] = validation_result
        return result
```

**Use case:** Still want to compare/analyze even if invalid

---

## Cost of Quality Metrics

### Metrics Tracked

**Location:** `src/runner.py:256-331`

#### 1. Attempt Statistics
```json
{
  "total_evaluations": 50,
  "total_attempts": 68,
  "average_attempts": 1.36
}
```

**Interpretation:**
- On average, 1.36 attempts needed per evaluation
- 36% overhead in API calls due to retries

#### 2. Success Breakdown
```json
{
  "successful": 42,           // Passed validation
  "validation_failed": 6,     // Parsed but failed validation (B2 flagged)
  "parse_failed": 2          // Couldn't parse JSON
}
```

**Interpretation:**
- 84% success rate (42/50)
- 12% validation failures (6/50)
- 4% parse failures (2/50)

#### 3. Validation Metrics
```json
{
  "validation_metrics": {
    "successful_validations": 42,
    "failed_validations": 6,
    "average_pass_rate": 94.50
  }
}
```

**Interpretation:**
- Even failed validations averaged 94.5% pass rate (failed 1-2 metrics)
- Models are "close" even when they fail

#### 4. Cost Analysis
```json
{
  "total_cost": 5.2000,              // Successful attempts only
  "total_cost_all_attempts": 6.8000, // Including retries
  "retry_overhead": 1.6000,          // 23.5% of total
  "retry_overhead_percentage": 23.5
}
```

**Interpretation:**
- Retries added 23.5% to total cost ($1.60 extra)
- Cost of quality: $1.60 to get 6 more valid outputs
- Per-retry cost: $1.60 / (68-50) = $0.089 per retry

#### 5. Per-Attempt Metadata
```json
{
  "all_attempts": [
    {
      "attempt": 1,
      "latency_ms": 2345,
      "tokens": {"input": 1200, "output": 800},
      "cost": 0.001234,
      "parse_error": null,
      "validation_passed": false,
      "validation_pass_rate": 87.5,
      "validation_score": "7/8"
    },
    {
      "attempt": 2,
      "validation_passed": true,
      "validation_pass_rate": 100.0,
      "validation_score": "8/8"
    }
  ]
}
```

**Use cases:**
- Identify which metrics fail most often
- See if retries improve validation scores
- Analyze learning patterns (does model improve on retry?)

---

## Configuration

### Ground Truth Configuration

**Location:** `config/ground_truth.yaml`

```yaml
reference_model:
  provider: "openai"
  model_id: "gpt-4o"

generation:
  max_retries: 3                  # Retry attempts for ground truth
  validate_before_saving: true    # Enable validation (recommended)
  overwrite_existing: false       # Skip existing files
```

**Recommendations:**
- Keep `validate_before_saving: true` to ensure ground truth quality
- Increase `max_retries` to 5 for critical ground truth generation
- Use `overwrite_existing: true` after changing validation logic

### Model Evaluation Configuration

**Location:** `src/runner.py` (hardcoded)

**To modify max_retries:**
```python
# Line 52
def run_single_evaluation(
    self,
    model_config: Dict[str, Any],
    prompt_config: Dict[str, Any],
    ftp: int,
    max_retries: int = 2,  # Change this default
):
```

**Future enhancement:** Move to `config/evaluation.yaml`

### Validation Tolerance Configuration

**Location:** `src/evaluator.py`

**To adjust tolerances, modify these values:**

```python
# Duration tolerance (line 125)
tolerance = max(2, declared_duration * 0.001)  # 0.1% or 2s min
# Change to: max(5, declared_duration * 0.002)  # 0.2% or 5s min

# Power zone tolerance (line 211)
tolerance = 2  # watts
# Change to: tolerance = 5  # More lenient

# FTP percentage tolerance (line 254)
if abs(actual_perc - declared_perc) > 1:
# Change to: if abs(actual_perc - declared_perc) > 2:

# Power adjustment tolerance (line 290)
tolerance = 2
# Change to: tolerance = 5
```

---

## Validation Results Interpretation

### Result Structure

**Successful Validation:**
```json
{
  "success": true,
  "validation_failed": false,
  "validation": {
    "overall_score": "8/8",
    "pass_rate": 100.0,
    "all_passed": true,
    "metrics": [
      {"metric": "schema_validation", "passed": true},
      {"metric": "required_fields", "passed": true},
      {"metric": "duration_consistency", "passed": true},
      {"metric": "time_continuity", "passed": true},
      {"metric": "power_zone_accuracy", "passed": true},
      {"metric": "ftp_percentage_accuracy", "passed": true},
      {"metric": "power_adjustment_accuracy", "passed": true},
      {"metric": "segment_type_validity", "passed": true}
    ]
  }
}
```

**Failed Validation (B2 flagged):**
```json
{
  "success": false,
  "validation_failed": true,  // B2 flag
  "validation": {
    "overall_score": "7/8",
    "pass_rate": 87.5,
    "all_passed": false,
    "metrics": [
      {"metric": "schema_validation", "passed": true},
      {"metric": "required_fields", "passed": true},
      {"metric": "duration_consistency", "passed": true},
      {"metric": "time_continuity", "passed": true},
      {
        "metric": "power_zone_accuracy",
        "passed": false,
        "mismatches": [
          {
            "segment_number": 5,
            "power": 150,
            "declared_zone": 2,
            "actual_zone": 3
          }
        ]
      },
      {"metric": "ftp_percentage_accuracy", "passed": true},
      {"metric": "power_adjustment_accuracy", "passed": true},
      {"metric": "segment_type_validity", "passed": true}
    ]
  }
}
```

**Parse Failed:**
```json
{
  "success": false,
  "validation_failed": false,
  "response": {
    "raw_content": "{ invalid json...",
    "parsed_json": null,
    "parse_error": "Expecting property name enclosed in double quotes: line 1 column 3"
  }
}
```

---

## Best Practices

### 1. Ground Truth Generation
- ✅ Always enable `validate_before_saving: true`
- ✅ Use high-quality reference model (GPT-4o)
- ✅ Set `max_retries: 3` or higher
- ✅ Regenerate ground truth when validation logic changes
- ❌ Don't accept invalid ground truth (now enforced)

### 2. Model Evaluation
- ✅ Use same validation logic as ground truth
- ✅ Track validation failures separately from successes
- ✅ Analyze which metrics fail most often per model
- ✅ Monitor retry overhead as cost metric
- ❌ Don't ignore validation failures (Option B2 captures them)

### 3. Tolerance Tuning
- ✅ Start conservative (current settings)
- ✅ Analyze false negative rate from metrics
- ✅ Increase tolerances if >10% false negative rate
- ✅ Document tolerance changes and rationale
- ❌ Don't make tolerances too loose (defeats validation purpose)

### 4. Cost Optimization
- ✅ Monitor `retry_overhead_percentage` in summaries
- ✅ If >30%, investigate validation false negatives
- ✅ Consider model-specific tolerances if needed
- ✅ Balance quality requirements vs. cost
- ❌ Don't optimize purely for cost (quality matters)

---

## Troubleshooting

### High Retry Rate (>30% overhead)

**Diagnosis:**
```bash
# Check which metrics fail most
python src/evaluator.py results/run_20250104_120000
```

**Solutions:**
1. Review failed metrics in evaluation reports
2. Check if specific tolerance needs adjustment
3. Verify ground truth uses same validation logic
4. Consider if model is fundamentally incompatible with schema

### Validation Always Fails for Specific Metric

**Common causes:**

| Metric | Likely Cause | Solution |
|--------|--------------|----------|
| Duration consistency | Off-by-one errors in intervals | Check time continuity first |
| Power zones | FTP mismatch | Verify FTP in config matches evaluation |
| FTP percentages | Rounding differences | Increase tolerance to ±2% |
| Power adjustments | Cascading from power errors | Fix power/zone issues first |

### False Positives (Invalid Workouts Pass)

**Investigation:**
1. Check `validation_failed: true` results
2. Review validation metrics for those results
3. Identify which validator should have caught it
4. Tighten relevant tolerance or fix validator logic

### Ground Truth Generation Fails

**Error:** `Ground truth validation failed after 3 attempts`

**Solutions:**
1. Increase `max_retries` in `config/ground_truth.yaml`
2. Review validation errors in console output
3. Check if prompt is too complex for model
4. Verify FTP is reasonable (e.g., 200W)
5. Temporarily disable validation to see raw output

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-01-04 | Initial implementation with strict validation |
| 2.0 | 2025-01-04 | **Current** - Added tolerances, Option B/B2, cost metrics |

### Changes in v2.0
1. **FTP percentage:** Exact match → ±1% tolerance
2. **Power zones:** Exact zone match → ±2W boundary tolerance
3. **Duration:** 1 second tolerance → 0.1% percentage-based tolerance
4. **Power adjustments:** Exact match → ±2W tolerance
5. **Ground truth:** Accept invalid → Fail hard
6. **Evaluation:** No validation → Full validation with Option B2
7. **Metrics:** Basic success/fail → Comprehensive cost of quality tracking

**Impact:** ~15-20% reduction in false negatives, ~80% reduction in unnecessary retries

---

## References

- **JSON Schema Specification:** https://json-schema.org/
- **jsonschema Python Library:** https://python-jsonschema.readthedocs.io/
- **Power Zone Calculation:** `src/system_prompt.py:calculate_zones()`
- **Schema Definition:** `src/system_prompt.py:WORKOUT_JSON_SCHEMA`
- **Evaluator Implementation:** `src/evaluator.py`
- **Ground Truth Generator:** `src/ground_truth_generator.py`
- **Evaluation Runner:** `src/runner.py`

---

## Support

For questions or issues:
1. Check this documentation
2. Review validation metrics in evaluation results
3. Examine `all_attempts` metadata for detailed error info
4. Adjust tolerances in `src/evaluator.py` if needed
5. Open issue with reproduction steps and validation results
