# Complete Evaluation Workflow

This document explains the end-to-end workflow for running LLM evaluations on cycling workout generation.

## Overview

```
┌─────────────────────┐
│  1. Ground Truth    │  Generate reference workouts using your best model
│     Generation      │  (One-time setup, can be updated)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  2. Run Evaluations │  Test all models against all prompts
│                     │  Track tokens, cost, latency
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  3. Evaluate        │  Validate structure + compare to ground truth
│     Results         │  Generate detailed reports
└─────────────────────┘
```

## Step-by-Step Guide

### Step 1: Configure Ground Truth Reference Model

Edit `config/ground_truth.yaml`:

```yaml
reference_model:
  provider: openai
  model_id: gpt-4o  # Your best/most reliable model
  display_name: "GPT-4o (Reference)"
```

**Why this matters**: The reference model creates your "gold standard" workouts. Choose your most capable model (typically GPT-4o or Gemini 1.5 Pro).

### Step 2: Generate Ground Truth Workouts

```bash
# Generate all ground truth files
poetry run python src/ground_truth_generator.py generate
```

**What happens**:
- Sends each of your 19 prompts to the reference model
- Validates the generated workouts (retries if invalid)
- Saves to `ground_truth/<prompt_id>.json`
- Each file contains the workout + generation metadata

**Expected output**:
```
================================================================================
Ground Truth Generation
Reference Model: GPT-4o (openai/gpt-4o)
FTP: 250W
Prompts: 19
Overwrite existing: False
================================================================================

  Generating ground truth for: endurance_65_sprints
    ✓ Generated successfully (attempt 1, 1234ms)
  Generating ground truth for: threshold_intervals_3x10
    ✓ Generated successfully (attempt 1, 1456ms)
...

================================================================================
Ground Truth Generation Complete!
Generated: 19
Skipped: 0
Failed: 0
Ground truth saved to: ground_truth
================================================================================
```

**Cost estimate**: Varies by model, typically $0.20-0.50 for all 19 prompts with GPT-4o.

### Step 3: (Optional) Validate Ground Truth

```bash
# Validate all ground truth files
poetry run python src/ground_truth_generator.py validate
```

**What it checks**:
- All structural validation metrics pass
- Workouts are well-formed and consistent

### Step 4: Configure Models to Test

Edit `config/models.yaml` to include/exclude models:

```yaml
models:
  - provider: openai
    model_id: gpt-4o-mini
    display_name: "GPT-4o Mini"
    # ... pricing

  - provider: gemini
    model_id: gemini-1.5-flash
    display_name: "Gemini 1.5 Flash"
    # ... pricing
```

**Tip**: Start with fast, cheap models (GPT-4o Mini, Gemini Flash) for testing, then add expensive ones.

### Step 5: Run Evaluations

```bash
# Run all models against all prompts
poetry run python src/runner.py
```

**What happens**:
- Creates timestamped directory: `results/run_20251103_143000/`
- For each model × prompt combination:
  - Generates workout
  - Tracks tokens, cost, latency
  - Saves individual result JSON
- Creates `summary.json` with aggregate stats

**Expected output**:
```
================================================================================
Starting evaluation run: 20251103_143000
FTP: 250W
Models: 3
Prompts: 19
Total evaluations: 57
================================================================================

GPT-4o Mini:
  Running GPT-4o Mini on prompt: endurance_65_sprints
  Running GPT-4o Mini on prompt: threshold_intervals_3x10
  ...

Gemini 1.5 Flash:
  Running Gemini 1.5 Flash on prompt: endurance_65_sprints
  ...

================================================================================
Evaluation complete!
Successful: 57/57
Total cost: $0.4567
Results saved to: results/run_20251103_143000
================================================================================
```

### Step 6: Evaluate Results

```bash
# Evaluate with ground truth comparison
poetry run python src/evaluator.py results/run_20251103_143000
```

**What happens**:
- Loads all result files from the run
- For each result:
  - **Structural validation**: Checks schema, timing, zones, etc.
  - **Ground truth comparison**: Compares to reference workout
- Generates `evaluation_report.json` with:
  - Per-result metrics
  - Aggregate statistics
  - Model performance comparison

**Expected output**:
```
Evaluation Report:
  Total results: 57
  Evaluated: 57
  Validation - All metrics passed: 52/57
  Validation - Average pass rate: 94.5%

  Ground Truth Comparison:
    Available: 57
    Perfect matches: 12/57
    Average similarity: 78.3%

Report saved to: results/run_20251103_143000/evaluation_report.json
```

## Understanding the Results

### Individual Result File

`results/run_20251103_143000/simple_threshold_60min_gpt-4o-mini.json`:

```json
{
  "prompt_id": "simple_threshold_60min",
  "model": {
    "provider": "openai",
    "model_id": "gpt-4o-mini",
    "display_name": "GPT-4o Mini"
  },
  "attempts": 1,
  "total_latency_all_attempts": 1234,
  "total_tokens_all_attempts": {
    "input": 450,
    "output": 320,
    "total": 770
  },
  "total_cost_all_attempts": 0.000259,
  "all_attempts": [
    {
      "attempt": 1,
      "latency_ms": 1234,
      "tokens": {"input": 450, "output": 320, "total": 770},
      "cost": 0.000259
    }
  ],
  "response": {
    "parsed_json": { /* the generated workout */ }
  },
  "success": true
}
```

### Evaluation Report

`results/run_20251103_143000/evaluation_report.json`:

```json
{
  "validation": {
    "all_passed_count": 52,
    "average_pass_rate": 94.5
  },
  "ground_truth_comparison": {
    "available": 57,
    "all_passed_count": 12,
    "average_similarity": 78.3
  },
  "evaluations": [
    {
      "prompt_id": "simple_threshold_60min",
      "model": "GPT-4o Mini",
      "pass_rate": 100,
      "ground_truth_comparison": {
        "similarity_percentage": 85.7,
        "metrics": [ /* detailed comparisons */ ]
      }
    }
  ]
}
```

## Interpreting Metrics

### Structural Validation (Pass/Fail)

- **100% pass rate**: Perfect technical correctness
- **87.5% pass rate**: 1 out of 8 checks failed (review which metric failed)
- **Common failures**: Time gaps, zone miscalculations, FTP percentage errors

### Ground Truth Similarity (0-100%)

- **100%**: Perfect match to reference workout
- **80-99%**: Very similar (minor differences in structure/timing)
- **60-79%**: Reasonably similar (different approach, same intent)
- **<60%**: Significant differences (may not meet requirements)

**Important**: Similarity isn't always about better/worse. A model might structure a workout differently but still be correct!

## Iterative Workflow

### Scenario 1: Testing a New Model

```bash
# 1. Add model to config/models.yaml
# 2. Run just that model
# (Edit src/runner.py to filter)
poetry run python src/runner.py  # filtered

# 3. Evaluate
poetry run python src/evaluator.py results/run_<timestamp>
```

### Scenario 2: Refining Ground Truth

```bash
# 1. Manually edit ground_truth/<prompt_id>.json
# 2. Re-run evaluations (ground truth unchanged)
poetry run python src/evaluator.py results/run_<old_timestamp>

# Now comparison uses your updated ground truth
```

### Scenario 3: Adding New Test Prompts

```bash
# 1. Add prompt to config/prompts.yaml
# 2. Generate ground truth for new prompt only
poetry run python src/ground_truth_generator.py generate --prompts my_new_prompt

# 3. Run full evaluation
poetry run python src/runner.py

# 4. Evaluate
poetry run python src/evaluator.py results/run_<timestamp>
```

## Cost Management

**Typical costs** (19 prompts):
- Ground truth (GPT-4o): ~$0.30
- Full eval (3 models): ~$0.50-1.00
- **Total per complete run**: ~$0.80-1.30

**Tips to reduce costs**:
1. Start with prompt filters (test 2-3 prompts first)
2. Use cheaper models initially (GPT-4o Mini, Gemini Flash)
3. Set `overwrite_existing: false` to preserve ground truth
4. Test with one model before running all

## Troubleshooting

### "No ground truth file found"

**Solution**: Run ground truth generator first:
```bash
poetry run python src/ground_truth_generator.py generate
```

### "Generation failed or parse error"

**Causes**:
- API key invalid/missing
- Model doesn't support JSON schema
- Rate limit hit

**Solution**: Check `.env` file, verify API keys work

### "Validation failed" during ground truth generation

**Meaning**: Reference model produced invalid workout

**Solution**:
- Check if reference model supports structured output
- Try different reference model in `config/ground_truth.yaml`
- Use `--force` to regenerate

## Next Steps

Once you have results:

1. **Analyze model performance**: Which models perform best?
2. **Cost-benefit analysis**: Is the cheapest model good enough?
3. **Identify failure patterns**: Which prompts cause issues?
4. **Refine prompts**: Update problematic prompts and rerun
5. **Export results**: Create comparison charts/tables

## Advanced: Custom Analysis

You can load and analyze results programmatically:

```python
import json
from pathlib import Path

# Load evaluation report
with open("results/run_20251103_143000/evaluation_report.json") as f:
    report = json.load(f)

# Find best performing model
evaluations = report["evaluations"]
by_model = {}
for eval in evaluations:
    model = eval["model"]
    if model not in by_model:
        by_model[model] = []
    by_model[model].append(eval["ground_truth_comparison"]["similarity_percentage"])

for model, scores in by_model.items():
    avg = sum(scores) / len(scores)
    print(f"{model}: {avg:.1f}% avg similarity")
```
