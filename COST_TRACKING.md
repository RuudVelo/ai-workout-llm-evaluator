# Cost Tracking Documentation

## Overview

The evaluation framework tracks costs at multiple levels to give you complete transparency on LLM API expenses.

## Ground Truth Generation - Detailed Cost Tracking

When generating ground truth, the system tracks costs across **all retry attempts**, not just the successful one.

### Example Output

```json
{
  "prompt_id": "threshold_intervals_3x10",
  "generation_metadata": {
    "attempts": 2,
    "total_latency_all_attempts": 2690,
    "total_tokens_all_attempts": {
      "input": 900,
      "output": 635,
      "total": 1535
    },
    "total_cost_all_attempts": 0.006912,
    "total_input_cost_all_attempts": 0.001962,
    "total_output_cost_all_attempts": 0.004950,
    "all_attempts": [
      {
        "attempt": 1,
        "latency_ms": 1234,
        "tokens": {
          "input": 450,
          "output": 315,
          "total": 765
        },
        "cost": 0.003455,
        "input_cost": 0.000981,
        "output_cost": 0.002474
      },
      {
        "attempt": 2,
        "latency_ms": 1456,
        "tokens": {
          "input": 450,
          "output": 320,
          "total": 770
        },
        "cost": 0.003457,
        "input_cost": 0.000981,
        "output_cost": 0.002476
      }
    ]
  }
}
```

### Field Descriptions

- **`attempts`**: Number of attempts needed (1 = succeeded first try)
- **`total_cost_all_attempts`**: Cumulative cost across ALL attempts (including failed ones)
- **`total_latency_all_attempts`**: Total time spent across all attempts
- **`total_tokens_all_attempts`**: Total tokens consumed across all attempts
- **`total_input_cost_all_attempts`**: Total input token cost across all attempts
- **`total_output_cost_all_attempts`**: Total output token cost across all attempts
- **`all_attempts`**: Array with detailed metadata for each individual attempt (includes `latency_ms`, `tokens`, `cost`, `input_cost`, `output_cost` per attempt)

### Why Retries Happen

Retries occur when:
1. **JSON parse error** - Model didn't return valid JSON
2. **Validation failure** - JSON is valid but doesn't meet structural requirements:
   - Schema mismatch
   - Missing required fields
   - Incorrect zone calculations
   - Time gaps/overlaps
   - etc.

### Cost Impact

If a prompt requires 3 attempts:
- Attempt 1 (failed): €0.0034
- Attempt 2 (failed): €0.0035
- Attempt 3 (success): €0.0033
- **Total actual cost**: €0.0102

Without `total_cost_all_attempts`, you'd only see €0.0033 and underestimate costs by 3x!

## Regular Evaluation Runs - With Retry Logic

The runner (`runner.py`) now includes retry logic (default: 2 attempts) and tracks costs across all attempts:

```json
{
  "prompt_id": "simple_threshold_60min",
  "model": {
    "provider": "openai",
    "model_id": "gpt-4o-mini"
  },
  "attempts": 1,
  "total_latency_all_attempts": 1234,
  "total_tokens_all_attempts": {
    "input": 420,
    "output": 305,
    "total": 725
  },
  "total_cost_all_attempts": 0.000259,
  "total_input_cost_all_attempts": 0.000084,
  "total_output_cost_all_attempts": 0.000175,
  "all_attempts": [
    {
      "attempt": 1,
      "latency_ms": 1234,
      "tokens": {
        "input": 420,
        "output": 305,
        "total": 725
      },
      "cost": 0.000259,
      "input_cost": 0.000084,
      "output_cost": 0.000175,
      "parse_error": null,
      "validation_passed": true
    }
  ],
  "success": true
}
```

### Retry Configuration

Default: **2 attempts** (configurable in code)

Retries happen on:
- JSON parse errors (malformed JSON)
- API errors (rate limits, timeouts, etc.)

Unlike ground truth generation, the runner does NOT retry on validation failures - it accepts whatever JSON the model returns.

## Aggregate Cost Tracking

### Ground Truth Summary

After generating all ground truth:
```
Generated: 19
Total cost: 0.0654  (sum of all successful attempts)
```

**Note**: This is the cost of successful attempts only. Check individual files' `total_cost_all_attempts` to see true costs.

### Evaluation Run Summary

```json
{
  "run_timestamp": "20251103_143000",
  "total_evaluations": 57,
  "successful": 55,
  "failed": 2,
  "total_attempts": 61,
  "total_cost": 0.4567,
  "total_cost_all_attempts": 0.4789
}
```

**Console output:**
```
Evaluation complete!
Successful: 55/57
Total attempts: 61 (avg: 1.1 per eval)
Total cost (successful attempts): 0.4567
Total cost (all attempts): 0.4789
  → Retry overhead: 0.0222 (4.6%)
```

This shows:
- **total_cost**: Cost of successful (final) attempts only
- **total_cost_all_attempts**: True cost including failed retry attempts
- **Retry overhead**: How much extra you paid for retries

## Cost Analysis Examples

### Example 1: Perfect Ground Truth (No Retries)

All prompts succeed on first attempt:
```
19 prompts × €0.0034 avg = €0.0646 total
All "attempts": 1
All "total_cost_all_attempts" = "cost"
```

### Example 2: Some Retries Needed

3 prompts need 2 attempts, rest succeed first try:
```
Total actual cost: €0.0748
(16 prompts × €0.0034 avg + 3 prompts × €0.0068 with retries)

Without tracking all_attempts:
You'd need to manually sum each prompt's total_cost_all_attempts field
```

### Example 3: Multi-Model Evaluation

Testing 3 models against 19 prompts:
```
3 models × 19 prompts = 57 API calls
57 × €0.0003 avg = €0.0171 total
(Assuming gpt-4o-mini pricing)
```

## Monitoring Retry Rates

To check how often retries are needed:

```python
import json
from pathlib import Path

# Analyze ground truth
gt_dir = Path("ground_truth")
total_attempts = 0
total_prompts = 0

for gt_file in gt_dir.glob("*.json"):
    with open(gt_file) as f:
        data = json.load(f)
    attempts = data["generation_metadata"]["attempts"]
    total_attempts += attempts
    total_prompts += 1

avg_attempts = total_attempts / total_prompts
print(f"Average attempts per prompt: {avg_attempts:.2f}")

if avg_attempts > 1.1:
    print("⚠️  High retry rate - consider:")
    print("  - Using a better model")
    print("  - Simplifying system prompt")
    print("  - Loosening validation rules")
```

## Cost Optimization Tips

### 1. Choose Reference Model Wisely

Better models = fewer retries:
- **GPT-4o**: Expensive per call, but rarely needs retries
- **GPT-4o-mini**: Cheaper per call, may need occasional retries
- **Balance**: Total cost = (base cost) × (1 + retry_rate)

### 2. Monitor Total vs. Single Attempt Costs

If `total_cost_all_attempts` is consistently much higher than `cost`:
→ Your reference model struggles with your prompts

### 3. Start Small

Generate ground truth for 2-3 prompts first:
```bash
poetry run python src/ground_truth_generator.py generate \
  --prompts simple_threshold_60min endurance_65_sprints
```

Check retry rates before committing to all 19 prompts.

### 4. Adjust Retry Settings

In `config/ground_truth.yaml`:
```yaml
generation:
  max_retries: 3  # Lower to 2 if costs too high
  validate_before_saving: false  # Skip validation to avoid retries (not recommended)
```

## Currency Note

All costs are in whatever currency you specified in `config/models.yaml` pricing. The framework doesn't assume a specific currency - just ensure consistency across all model configurations.

## Future Enhancement: Budget Limits

Not yet implemented, but could add:
```yaml
budget:
  max_cost_per_prompt: 0.01  # Stop if single prompt exceeds this
  max_total_cost: 1.00  # Stop entire run if exceeded
```

Would prevent runaway costs during experimentation.
