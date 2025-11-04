# Recent Updates

## Retry Logic & Cost Tracking (Latest)

### What Changed

Added comprehensive retry logic and cost tracking to both ground truth generation and regular evaluation runs.

### Ground Truth Generator

**Retry behavior:**
- Default: 3 attempts (configurable in `config/ground_truth.yaml`)
- Retries on: JSON parse errors AND validation failures
- Saves best result after validation passes

**Cost tracking:**
```json
"generation_metadata": {
  "cost": 0.003456,                    // Cost of successful attempt
  "attempts": 2,                        // Number of attempts needed
  "total_cost_all_attempts": 0.006912, // TRUE cost (all attempts)
  "all_attempts": [                     // Detailed per-attempt data
    {
      "attempt": 1,
      "latency_ms": 1234,
      "tokens": {...},
      "cost": 0.003456
    },
    {
      "attempt": 2,
      "latency_ms": 1456,
      "tokens": {...},
      "cost": 0.003456
    }
  ]
}
```

### Evaluation Runner

**Retry behavior:**
- Default: 2 attempts (configurable via `max_retries` parameter)
- Retries on: JSON parse errors and API errors
- Does NOT retry on validation failures (accepts what model returns)

**Cost tracking:**
```json
{
  "cost": 0.000259,                    // Cost of successful attempt
  "attempts": 1,                        // Number of attempts needed
  "total_cost_all_attempts": 0.000259, // TRUE cost (all attempts)
  "all_attempts": [...]                 // Detailed per-attempt data
}
```

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
