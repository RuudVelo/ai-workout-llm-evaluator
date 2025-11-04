# Recent Updates

## Automatic Ground Truth Model Exclusion (Latest)

### What Changed

The evaluation runner now **automatically excludes** the ground truth reference model from evaluation runs to prevent duplicate generation and unnecessary costs.

### How It Works

1. **Composite Key Detection**: Uses both `provider` AND `model_id` to identify the reference model
2. **Automatic Filtering**: Reads `ground_truth.yaml` at startup and filters the model from `models.yaml`
3. **Cost Savings**: Prevents paying twice for the same model (once in ground truth generation, once in evaluation)

### Example Console Output

```
================================================================================
Starting evaluation run: 20251104_123000
FTP: 250W
⚠ Skipping ground truth reference model: openai/gpt-4o
  (Already generated via ground_truth_generator.py)
Models to evaluate: 7
Prompts: 19
Total evaluations: 133
================================================================================
```

### Why This Matters

**Before:**
- Ground truth uses gpt-4o → costs $0.50
- Evaluation also runs gpt-4o → costs another $0.50
- **Total: $1.00** (paying twice for the same outputs)

**After:**
- Ground truth uses gpt-4o → costs $0.50
- Evaluation skips gpt-4o automatically
- **Total: $0.50** (50% cost savings)

### Configuration

No configuration needed! The runner automatically:
1. Loads `ground_truth.yaml` to find the reference model
2. Filters it from the evaluation model list using `provider` + `model_id`
3. Displays a warning message so you know it was skipped

## Metadata Structure Cleanup (Previous)

### What Changed

Removed redundant top-level metadata fields that duplicated data from the `all_attempts` array.

**Removed fields:**
- `latency_ms` (was duplicating `all_attempts[-1].latency_ms`)
- `tokens` (was duplicating `all_attempts[-1].tokens`)
- `cost` (was duplicating `all_attempts[-1].cost`)
- `input_cost` (was duplicating `all_attempts[-1].input_cost`)
- `output_cost` (was duplicating `all_attempts[-1].output_cost`)

### New Metadata Structure

**Ground truth and evaluation results now use:**
```json
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
      "tokens": {"input": 450, "output": 315, "total": 765},
      "cost": 0.003456,
      "input_cost": 0.000981,
      "output_cost": 0.002475
    },
    {
      "attempt": 2,
      "latency_ms": 1456,
      "tokens": {"input": 450, "output": 320, "total": 770},
      "cost": 0.003456,
      "input_cost": 0.000981,
      "output_cost": 0.002475
    }
  ]
}
```

**To access last attempt data:** Use `all_attempts[-1]` instead of top-level fields.

### Why This Matters

- ✅ Eliminates redundancy and confusion
- ✅ Single source of truth for each data point
- ✅ Cleaner, more maintainable structure
- ✅ All attempt data (including last) in one place

## Retry Logic & Cost Tracking (Previous)

### What Changed

Added comprehensive retry logic and cost tracking to both ground truth generation and regular evaluation runs.

### Ground Truth Generator

**Retry behavior:**
- Default: 3 attempts (configurable in `config/ground_truth.yaml`)
- Retries on: JSON parse errors AND validation failures
- Saves best result after validation passes

### Evaluation Runner

**Retry behavior:**
- Default: 2 attempts (configurable via `max_retries` parameter)
- Retries on: JSON parse errors and API errors
- Does NOT retry on validation failures (accepts what model returns)

**Summary includes:**
```json
{
  "total_cost": 0.4567,                // Sum of successful attempts
  "total_cost_all_attempts": 0.4789,   // TRUE COST including retries
  "total_attempts": 61                  // Total API calls made
}
```

**Console output shows retry overhead:**
```
Total cost (successful attempts): 0.4567
Total cost (all attempts): 0.4789
  → Retry overhead: 0.0222 (4.6%)
```

### Why This Matters

**Without this tracking:**
- You'd only see cost of successful attempts
- Hidden costs from retries would surprise you
- Can't analyze which models/prompts cause retries
- Impossible to optimize retry strategy

**With this tracking:**
- ✅ Full cost transparency
- ✅ Identify problematic prompts (high retry rate)
- ✅ Compare retry overhead across models
- ✅ Make informed decisions about retry limits
- ✅ Budget accurately for LLM costs

### Example Impact

If 5 out of 57 evaluations need 2 attempts:
- **Without tracking**: Shows €0.45 (underestimate)
- **With tracking**: Shows €0.47 actual cost
- **Difference**: 4.4% hidden costs revealed!

For large-scale evals (1000s of prompts), this adds up quickly.

## Currency Flexibility (Previous)

Changed all cost fields from `cost_usd` to `cost` to support any currency (EUR, USD, etc.).

## Environment Variables (Previous)

Added `load_dotenv()` to automatically load API keys from `.env` file.
