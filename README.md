# Cycling Workout Generator - LLM Evaluation Framework

A Python-based evaluation framework for testing LLM-generated structured cycling workouts across multiple providers (OpenAI, Google Gemini, Together AI).

## Overview

This project evaluates how well different LLMs can generate structured JSON workout plans from natural language descriptions. It tests:
- **Structured output generation** (JSON schema compliance)
- **Accuracy** (power zones, FTP percentages, timing)
- **Cost efficiency** (tokens used, API costs)
- **Latency** (response times)

## Features

- ✅ Support for multiple LLM providers (OpenAI, Gemini, Together AI)
- ✅ Structured JSON output with schema validation
- ✅ Token usage and cost tracking
- ✅ Latency measurement
- ✅ Comprehensive evaluation metrics
- ✅ Configurable prompts and models via YAML
- ✅ Timestamped result storage

## Project Structure

```
eval_workout_generator/
├── config/
│   ├── models.yaml          # Model configurations with pricing
│   └── prompts.yaml         # Test prompts with descriptions
├── ground_truth/            # (Future) Ground truth workouts
├── results/                 # Timestamped run results
│   └── run_YYYYMMDD_HHMMSS/
│       ├── *.json          # Individual results
│       ├── summary.json    # Run summary
│       └── evaluation_report.json
├── src/
│   ├── system_prompt.py    # System prompt & schema definitions
│   ├── model_providers.py  # Provider implementations
│   ├── runner.py           # Main eval runner
│   └── evaluator.py        # Evaluation metrics
├── pyproject.toml
└── .env                    # API keys (not committed)
```

## Setup

### Prerequisites

- Python 3.10+
- pyenv (for Python version management)
- Poetry (for dependency management)

### Installation

1. Clone the repository and navigate to it:
```bash
cd eval_workout_generator
```

2. Set up Python environment with pyenv:
```bash
pyenv install 3.10  # or your preferred version
pyenv local 3.10
```

3. Install dependencies with Poetry:
```bash
poetry install
```

4. Configure API keys:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

## Quick Start

```bash
# 1. Generate ground truth workouts (one-time setup)
poetry run python src/ground_truth_generator.py generate

# 2. Run evaluations across all models
poetry run python src/runner.py

# 3. Evaluate results with ground truth comparison
poetry run python src/evaluator.py results/run_<timestamp>
```

The framework will:
- Generate workouts from 19 test prompts across all configured models
- Track tokens, cost, and latency for each generation
- Validate structural correctness (schema, zones, timing)
- Compare against ground truth for semantic similarity
- Produce detailed evaluation reports

## Configuration

### Models (`config/models.yaml`)

Configure which models to test with pricing info:

```yaml
models:
  - provider: openai
    model_id: gpt-4o-mini
    display_name: "GPT-4o Mini"
    supports_structured_output: true
    pricing:
      input_per_million: 0.150
      output_per_million: 0.600
```

### Prompts (`config/prompts.yaml`)

Define test prompts with descriptions:

```yaml
ftp: 250  # Default FTP for all tests

prompts:
  - id: simple_threshold_60min
    description: "Simple threshold workout request"
    user_prompt: "Create a 60 minute threshold workout."
```

### Ground Truth (`config/ground_truth.yaml`)

Configure which model to use as the reference for ground truth generation:

```yaml
reference_model:
  provider: openai
  model_id: gpt-4o  # Use your strongest model
  display_name: "GPT-4o (Reference)"

generation:
  max_retries: 3  # Retry on validation failure
  overwrite_existing: false  # Preserve manual ground truth
  validate_before_saving: true  # Ensure quality
```

**Tip**: Use your best-performing model (e.g., GPT-4o, Gemini 1.5 Pro) as the reference model to establish high-quality baselines.

## Usage

### 1. Generate Ground Truth (Recommended First Step)

Generate reference workouts using a strong model (configured in `config/ground_truth.yaml`):

```bash
# Generate ground truth for all prompts
poetry run python src/ground_truth_generator.py generate

# Generate for specific prompts only
poetry run python src/ground_truth_generator.py generate --prompts simple_threshold_60min endurance_65_sprints

# Force regenerate existing ground truth
poetry run python src/ground_truth_generator.py generate --force

# Validate existing ground truth files
poetry run python src/ground_truth_generator.py validate
```

Ground truth files are saved to `ground_truth/` and serve as baseline for comparison.

### 2. Run Evaluations

Run all prompts across all configured models:

```bash
poetry run python src/runner.py
```

Run with filters:

```python
# In src/runner.py, modify main():
runner.run_all(
    model_filter=["gpt-4o-mini"],  # Only these models
    prompt_filter=["simple_threshold_60min"]  # Only these prompts
)
```

### 3. Evaluate Results

After running evaluations, analyze the results:

```bash
# Evaluate with ground truth comparison (recommended)
poetry run python src/evaluator.py results/run_YYYYMMDD_HHMMSS

# Evaluate without ground truth comparison
poetry run python src/evaluator.py results/run_YYYYMMDD_HHMMSS --no-ground-truth

# Use custom ground truth directory
poetry run python src/evaluator.py results/run_YYYYMMDD_HHMMSS --ground-truth my_custom_gt/
```

This generates an `evaluation_report.json` with:
- **Structural validation**: Schema, fields, timing, zones
- **Ground truth comparison**: Duration, power distribution, structure similarity
- **Aggregate metrics**: Pass rates, similarity scores

## Evaluation Metrics

### Structural Validation (Always Runs)

1. **Schema Validation**: JSON matches expected structure
2. **Required Fields**: All mandatory fields present
3. **Duration Consistency**: Total duration matches sum of intervals
4. **Time Continuity**: No gaps or overlaps between segments
5. **Power Zone Accuracy**: Power values match declared zones
6. **FTP Percentage Accuracy**: Correct percentage calculations
7. **Power Adjustments**: ±10W adjustments are correct
8. **Segment Type Validity**: Only allowed enum values used

### Ground Truth Comparison (When Available)

1. **Duration Comparison**: Total workout duration similarity
2. **Interval Count**: Number of segments within tolerance
3. **Segment Type Distribution**: Warmup, intervals, cooldown presence
4. **Power Zone Distribution**: Time spent in each zone
5. **Workout Structure**: High-level flow (warmup → work → cooldown)
6. **Average Power**: Time-weighted average power target

## Output Format

### Individual Result
```json
{
  "prompt_id": "simple_threshold_60min",
  "model": {
    "provider": "openai",
    "model_id": "gpt-4o-mini",
    "display_name": "GPT-4o Mini"
  },
  "ftp": 250,
  "timestamp": "2025-11-03T14:30:00",
  "latency_ms": 1234,
  "tokens": {
    "input": 450,
    "output": 320,
    "total": 770
  },
  "cost_usd": 0.000259,
  "response": {
    "parsed_json": { /* workout object */ },
    "parse_error": null
  },
  "success": true
}
```

### Evaluation Report
```json
{
  "run_directory": "results/run_20251103_143000",
  "total_results": 20,
  "evaluated": 18,
  "skipped": 2,
  "all_passed_count": 15,
  "average_pass_rate": 87.5,
  "evaluations": [ /* ... */ ]
}
```

## Example Prompts

The framework includes 19 diverse test prompts covering:
- Simple requests ("Create a 60 minute threshold workout")
- Detailed specifications with intervals and recoveries
- Zone-based progressive workouts
- Shorthand notation (WU, CD, rec, etc.)
- Complex multi-block workouts
- Low-cadence strength work
- Sprint intervals

## Cost Tracking

All runs track:
- Input tokens
- Output tokens
- Total tokens
- Cost per request (based on model pricing)
- Total cost per run

Example output:
```
Evaluation complete!
Successful: 18/20
Total cost: $0.1234
Results saved to: results/run_20251103_143000
```

## Extending

### Adding New Models

Edit `config/models.yaml`:
```yaml
- provider: openai  # or gemini, together
  model_id: new-model-id
  display_name: "Model Display Name"
  supports_structured_output: true
  pricing:
    input_per_million: X.XX
    output_per_million: Y.YY
```

### Adding New Prompts

Edit `config/prompts.yaml`:
```yaml
- id: my_new_prompt
  description: "Brief description"
  user_prompt: "Your prompt text here"
```

### Adding New Providers

1. Implement a new provider class in `src/model_providers.py`
2. Follow the `ModelResponse` interface
3. Add to `get_provider()` factory function

## Development

Run tests:
```bash
poetry run pytest
```

Format code:
```bash
poetry run black src/
```

## Future Enhancements

- [ ] Ground truth comparison metrics
- [ ] Semantic similarity evaluation
- [ ] HTML report generation
- [ ] Parallel execution for faster runs
- [ ] Retry logic for API failures
- [ ] Rate limiting support
- [ ] Compare runs over time
- [ ] Export to CSV/Excel

## License

MIT
