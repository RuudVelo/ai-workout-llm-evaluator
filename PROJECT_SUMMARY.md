# Project Summary: LLM Eval for Cycling Workout Generator

## What We Built

A complete Python-based evaluation framework for testing how well different LLMs generate structured cycling workouts from natural language prompts.

## Core Features

### 1. Multi-Provider Support
- **OpenAI**: GPT-4o, GPT-4o Mini, GPT-4 Turbo
- **Google Gemini**: Gemini 1.5 Pro, Gemini 2.5 Flash variants
- **Together AI**: Llama 3.3 70B, Qwen 2.5 72B, Llama 3.1 8B

All providers support structured JSON output.

### 2. Ground Truth Generation
- Uses a configurable "reference model" (your best model)
- Generates baseline workouts for all test prompts
- Validates quality before saving
- Supports manual curation (won't overwrite existing files)

### 3. Comprehensive Evaluation

**Structural Validation** (8 metrics):
- JSON schema compliance
- Required fields presence
- Duration consistency
- Time continuity (no gaps/overlaps)
- Power zone accuracy
- FTP percentage correctness
- Power adjustment validation (±10W)
- Segment type validity

**Ground Truth Comparison** (6 metrics):
- Duration similarity
- Interval count matching
- Segment type distribution
- Power zone distribution
- Workout structure (warmup → work → cooldown)
- Average power comparison

### 4. Cost & Performance Tracking
- Input/output token counts
- Cost per request (based on pricing config)
- Latency measurement (milliseconds)
- Aggregate statistics per run

### 5. Flexible Configuration
- YAML-based config for models, prompts, ground truth
- Filter by model or prompt
- Easy to add new providers/models
- Modular design

## Project Structure

```
eval_workout_generator/
├── config/
│   ├── models.yaml           # Model definitions + pricing
│   ├── prompts.yaml          # 19 test prompts
│   └── ground_truth.yaml     # Reference model config
│
├── src/
│   ├── system_prompt.py      # Prompt templates + schema
│   ├── model_providers.py    # OpenAI, Gemini, Together AI adapters
│   ├── runner.py             # Main evaluation runner
│   ├── evaluator.py          # Validation + comparison logic
│   ├── ground_truth_generator.py  # Reference workout generator
│   └── comparison_metrics.py # Ground truth comparison metrics
│
├── ground_truth/             # Reference workouts (generated)
├── results/                  # Timestamped run outputs
│   └── run_YYYYMMDD_HHMMSS/
│       ├── *.json           # Individual results
│       ├── summary.json     # Run summary
│       └── evaluation_report.json  # Analysis
│
├── README.md                 # Main documentation
├── WORKFLOW.md               # Step-by-step guide
├── PROJECT_SUMMARY.md        # This file
├── pyproject.toml            # Poetry dependencies
└── .env                      # API keys (not committed)
```

## Test Coverage

### 19 Diverse Test Prompts

1. **Simple requests**: "Create a 60 minute threshold workout"
2. **Detailed specs**: "60min total — 15min warm-up, 3x10min @ 90% FTP..."
3. **Zone-based**: "Z2 endurance for 45 minutes, Z3 tempo for 20..."
4. **Shorthand notation**: "WU 10min @150W, 6×5min @300W..."
5. **Complex multi-block**: Progressive, ramping, sprint combos
6. **Special cases**: Low-cadence strength, variable intensity

This covers a wide range of:
- Workout types (endurance, tempo, threshold, VO2, sprints)
- Complexity levels (simple → complex)
- Notation styles (natural language → shorthand)
- Duration (5 min → 2 hours)

## Key Design Decisions

### 1. Structured Output First
All providers must return valid JSON matching the schema. This ensures:
- Parseable outputs (no regex extraction)
- Type safety
- Easier evaluation

### 2. Two-Phase Evaluation
- **Phase 1**: Structural validation (always runs, no ground truth needed)
- **Phase 2**: Semantic comparison (optional, requires ground truth)

This allows you to:
- Run quick checks without ground truth
- Progressively add ground truth as needed
- Separate "technically correct" from "semantically correct"

### 3. Configurable Reference Model
Ground truth generation is separate from evaluation, using a configurable model. This means:
- You control the quality baseline
- Can regenerate if you change your mind
- Manual curation supported (won't overwrite)

### 4. Tolerances Built In
Comparison metrics use reasonable tolerances:
- Duration: ±60 seconds
- Interval count: ±30%
- Zone distribution: ±15% for major zones
- Average power: ±15W

This acknowledges that different valid workouts can achieve the same goals.

## Workflow Summary

```bash
# One-time setup
poetry install
cp .env.example .env
# Edit .env with API keys

# Generate ground truth (once or when prompts change)
poetry run python src/ground_truth_generator.py generate

# Run evaluations
poetry run python src/runner.py

# Analyze results
poetry run python src/evaluator.py results/run_<timestamp>
```

## Output Examples

### Run Summary
```
Successful: 57/57
Total cost: $0.4567
Results saved to: results/run_20251103_143000
```

### Evaluation Report
```
Validation - All metrics passed: 52/57
Validation - Average pass rate: 94.5%

Ground Truth Comparison:
  Available: 57
  Perfect matches: 12/57
  Average similarity: 78.3%
```

## Extensibility

### Adding a New Provider

1. Implement provider class in `model_providers.py`:
```python
class NewProvider:
    def generate(self, model_id, user_prompt, ftp, ...):
        # ... API call logic
        return ModelResponse(...)
```

2. Register in `get_provider()` factory

3. Add models to `config/models.yaml`

### Adding New Metrics

1. Add method to `WorkoutEvaluator` for validation metrics
2. Add method to `WorkoutComparator` for comparison metrics
3. Metrics automatically included in reports

### Custom Analysis

Load JSON results programmatically for custom analysis, charts, reports.

## Cost Estimates

Based on typical usage (19 prompts):

| Activity | Cost (USD) |
|----------|------------|
| Ground truth generation (GPT-4o) | ~$0.30 |
| Full evaluation (3 models) | ~$0.50-1.00 |
| **Total per complete run** | **~$0.80-1.30** |

Cost scales linearly with:
- Number of prompts
- Number of models
- Model pricing

## Limitations & Future Work

### Current Limitations
1. No parallel execution (runs sequentially)
2. No automatic retry on API failures
3. No rate limiting handling
4. Ground truth is model-generated (not human-verified)
5. Comparison metrics use simple heuristics (not ML-based)

### Potential Enhancements
- [ ] Parallel execution for faster runs
- [ ] HTML/PDF report generation
- [ ] Time-series comparison (track improvements)
- [ ] Semantic similarity using embeddings
- [ ] Human evaluation interface
- [ ] Automatic prompt refinement
- [ ] Cost optimization recommendations
- [ ] Integration with CI/CD
- [ ] Export to spreadsheets
- [ ] Visualization dashboard

## Dependencies

### Core
- `openai` - OpenAI API client
- `google-generativeai` - Gemini API client
- `together` - Together AI API client
- `python-dotenv` - Environment variables

### Utilities
- `pyyaml` - Configuration files
- `pydantic` - Data validation
- `jsonschema` - Schema validation
- `pandas` - Data analysis (available, not yet used)

### Development
- `pytest` - Testing framework
- `black` - Code formatting
- `poetry` - Dependency management

## Technical Highlights

### 1. Provider Abstraction
Uniform interface across all LLM providers via `ModelResponse` class.

### 2. Schema-Driven
Single source of truth for workout structure (`WORKOUT_JSON_SCHEMA`).

### 3. Zone Calculation
Power zones dynamically calculated from FTP using standard Coggan percentages.

### 4. Robust Error Handling
- Retries with validation
- Graceful degradation
- Detailed error reporting

### 5. Timestamped Runs
Immutable result storage - never overwrites previous runs.

## Success Metrics

The framework helps answer:

1. **Which model is most accurate?** → Ground truth similarity %
2. **Which model is cheapest?** → Cost per prompt
3. **Which model is fastest?** → Latency (ms)
4. **Which prompts are problematic?** → Low pass rates
5. **Is a cheap model good enough?** → Cost vs quality trade-off

## Getting Help

- **Setup issues**: See [README.md](README.md)
- **Workflow questions**: See [WORKFLOW.md](WORKFLOW.md)
- **Code questions**: All modules have docstrings
- **Config questions**: YAML files have inline comments

## License

MIT

---

**Built for**: Evaluating LLM-generated cycling workouts
**Focus**: Structured output quality, cost efficiency, semantic correctness
**Status**: Fully functional, ready for production use
