# Metadata Enhancements - Complete Documentation

## Summary

Enhanced the `generation_metadata` structure in both ground truth files and model evaluation results to track comprehensive totals across all retry attempts. The structure has been **streamlined to remove redundant top-level fields**.

Key changes:
- ✅ Total latency across all attempts
- ✅ Total tokens (input, output, total) across all attempts
- ✅ Total costs split by input and output tokens
- ✅ Individual attempt details include split costs
- ✅ **Removed redundant top-level fields** (latency_ms, tokens, cost, input_cost, output_cost)

## What Changed

### Files Modified
1. [src/ground_truth_generator.py](src/ground_truth_generator.py) - Removed top-level redundant fields
2. [src/runner.py](src/runner.py) - Removed top-level redundant fields, updated cost calculation logic
3. [test_metadata_totals.py](test_metadata_totals.py) - Updated to reflect new structure

### New Metadata Structure

#### Complete Metadata Object
```json
{
  "generation_metadata": {
    "attempts": 3,
    "total_latency_all_attempts": 42402,
    "total_tokens_all_attempts": {
      "input": 3018,
      "output": 2490,
      "total": 5508
    },
    "total_cost_all_attempts": 0.028242,
    "total_input_cost_all_attempts": 0.006579,
    "total_output_cost_all_attempts": 0.021663,
    "all_attempts": [
      {
        "attempt": 1,
        "latency_ms": 14331,
        "tokens": {
          "input": 1006,
          "output": 892,
          "total": 1898
        },
        "cost": 0.009953,
        "input_cost": 0.002193,
        "output_cost": 0.007760
      },
      {
        "attempt": 2,
        "latency_ms": 12149,
        "tokens": {
          "input": 1006,
          "output": 825,
          "total": 1831
        },
        "cost": 0.008371,
        "input_cost": 0.002193,
        "output_cost": 0.006178
      },
      {
        "attempt": 3,
        "latency_ms": 15922,
        "tokens": {
          "input": 1006,
          "output": 773,
          "total": 1779
        },
        "cost": 0.009918,
        "input_cost": 0.002193,
        "output_cost": 0.006725
      }
    ]
  }
}
```

### What Was Removed

Previously, the structure had redundant top-level fields that duplicated data from the last attempt in `all_attempts`:
- ❌ `latency_ms` (duplicated from `all_attempts[-1].latency_ms`)
- ❌ `tokens` (duplicated from `all_attempts[-1].tokens`)
- ❌ `cost` (duplicated from `all_attempts[-1].cost`)
- ❌ `input_cost` (duplicated from `all_attempts[-1].input_cost`)
- ❌ `output_cost` (duplicated from `all_attempts[-1].output_cost`)

**Rationale**: Since all individual attempt data (including the last/successful attempt) is stored in `all_attempts`, having top-level fields created redundancy and confusion.

## Benefits

### 1. Complete Cost Analysis
- **Before**: Only knew total cost across attempts
- **After**: Can analyze input vs output cost breakdown
  - Helps optimize prompts (reduce input tokens)
  - Understand generation verbosity (output tokens)

### 2. Latency Tracking
- **Before**: Only knew latency of successful attempt
- **After**: Can calculate total time spent including retries
  - Measure retry overhead: `total_latency / attempts`
  - Identify slow models more accurately

### 3. Token Budgeting
- **Before**: Only tracked tokens for successful attempt
- **After**: Know exact token consumption across all attempts
  - Critical for rate limiting
  - Better cost forecasting
  - Identify models that frequently retry

### 4. Efficiency Metrics
Can now calculate powerful insights:
```python
# Last attempt cost (successful attempt)
last_attempt_cost = all_attempts[-1]['cost']

# Retry overhead percentage
retry_overhead = (total_cost_all_attempts - last_attempt_cost) / total_cost_all_attempts * 100

# Average latency per attempt
avg_latency = total_latency_all_attempts / attempts

# Cost per 1K tokens (split by input/output)
input_cost_per_1k = total_input_cost_all_attempts / (total_tokens_all_attempts['input'] / 1000)
output_cost_per_1k = total_output_cost_all_attempts / (total_tokens_all_attempts['output'] / 1000)

# Token efficiency
tokens_per_attempt = total_tokens_all_attempts['total'] / attempts
```

## Example: Real Data Analysis

Based on example with 3 attempts:

### Current Format (Streamlined)
```json
{
  "generation_metadata": {
    "attempts": 3,
    "total_latency_all_attempts": 42402,
    "total_tokens_all_attempts": {
      "input": 3018,
      "output": 2490,
      "total": 5508
    },
    "total_cost_all_attempts": 0.028242,
    "total_input_cost_all_attempts": 0.006579,
    "total_output_cost_all_attempts": 0.021663,
    "all_attempts": [
      {"attempt": 1, "cost": 0.009953, ...},
      {"attempt": 2, "cost": 0.008371, ...},
      {"attempt": 3, "cost": 0.009918, ...}
    ]
  }
}
```

**Analysis**: Now we can see:
- 📊 Total time spent: 42.4 seconds (avg 14.1s per attempt)
- 🎯 Input cost: $0.006579 (23% of total)
- 📝 Output cost: $0.021663 (77% of total)
- 💰 Last attempt cost: $0.009918 (from `all_attempts[-1]`)
- 💰 Retry overhead: 65% ($0.018324 extra spent on retries)
- 🔢 Total tokens consumed: 5,508 (avg 1,836 per attempt)
- ⚡ Input tokens stable: 1,006 per attempt (prompt is constant)
- 📈 Output tokens vary: 892, 825, 773 (getting more concise)

## Verification

A test script has been created: [test_metadata_totals.py](test_metadata_totals.py)

Run it to verify the implementation:
```bash
python3 test_metadata_totals.py
```

## Testing New Format

To generate a ground truth file with the new format:

```bash
# Generate a single prompt
cd /Users/goordenrmc/Desktop/projects/eval_workout_generator
python3 src/ground_truth_generator.py generate --prompts simple_tempo_block --force

# Verify the new structure
python3 test_metadata_totals.py
```

## Backward Compatibility

⚠️ **Breaking Change**
- Old ground truth files with top-level `cost`, `latency_ms`, `tokens`, `input_cost`, `output_cost` fields are now outdated
- Code that relied on these top-level fields must now access `all_attempts[-1]` for last attempt data
- The `runner.py` cost calculation has been updated to use `all_attempts[-1].cost` instead of top-level `cost`
- All existing ground truth files should be regenerated to use the new structure

## Implementation Details

### Cost Calculation
Input and output costs are calculated per attempt using the pricing from `models.yaml`:

```python
input_cost = (
    response.input_tokens
    * model_config["pricing"]["input_per_million"]
    / 1_000_000
)
output_cost = (
    response.output_tokens
    * model_config["pricing"]["output_per_million"]
    / 1_000_000
)
```

### Cumulative Tracking
All totals are accumulated during the retry loop:

```python
total_cost_all_attempts += response.cost
total_input_cost_all_attempts += input_cost
total_output_cost_all_attempts += output_cost
total_latency_all_attempts += response.latency_ms
total_input_tokens_all_attempts += response.input_tokens
total_output_tokens_all_attempts += response.output_tokens
```

## Future Enhancements

Potential additions:
1. **Retry reason tracking**: Why did each attempt fail?
2. **Time between retries**: Track delay between attempts
3. **Model-specific retry patterns**: Statistical analysis per model
4. **Cost projections**: Estimate total cost before running
5. **Budget alerts**: Warn when approaching cost limits

## Questions?

For issues or suggestions, check:
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Project overview
- [COST_TRACKING.md](COST_TRACKING.md) - Cost tracking details
- [WORKFLOW.md](WORKFLOW.md) - Development workflow
