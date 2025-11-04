# Pre-Flight Checklist

Use this checklist before running your first evaluation.

## Setup (One-Time)

- [ ] **Python environment**
  ```bash
  pyenv install 3.10
  pyenv local 3.10
  ```

- [ ] **Dependencies installed**
  ```bash
  poetry install
  ```

- [ ] **API keys configured**
  ```bash
  cp .env.example .env
  # Edit .env and add your API keys
  ```

- [ ] **Verify API keys work**
  ```bash
  # Test OpenAI
  poetry run python -c "from openai import OpenAI; print(OpenAI().models.list().data[0].id)"

  # Test Gemini
  poetry run python -c "import google.generativeai as genai; import os; genai.configure(api_key=os.getenv('GEMINI_API_KEY')); print(genai.list_models()[0].name)"
  ```

## Configuration

- [ ] **Review models** in `config/models.yaml`
  - Remove models you don't want to test
  - Update pricing if needed
  - Verify model IDs are current

- [ ] **Review prompts** in `config/prompts.yaml`
  - All 19 prompts look good?
  - FTP set correctly (default: 250W)?
  - Want to add custom prompts?

- [ ] **Configure ground truth** in `config/ground_truth.yaml`
  - Reference model set to your best model
  - `max_retries: 3` is reasonable
  - `validate_before_saving: true` is recommended

## Before First Run

- [ ] **Estimate costs**
  - Ground truth (19 prompts × reference model): ~$0.30
  - Full eval (19 prompts × N models): ~$0.50-1.00
  - **Recommendation**: Start with 2-3 prompts first!

- [ ] **Test with limited prompts** (optional but recommended)
  ```python
  # Edit src/runner.py main() to filter:
  runner.run_all(
      prompt_filter=["simple_threshold_60min", "endurance_65_sprints"]
  )
  ```

- [ ] **Test with one model** (optional but recommended)
  ```python
  # Edit src/runner.py main() to filter:
  runner.run_all(
      model_filter=["gpt-4o-mini"]
  )
  ```

## Running Evaluations

### Step 1: Generate Ground Truth

- [ ] **Run ground truth generator**
  ```bash
  poetry run python src/ground_truth_generator.py generate
  ```

- [ ] **Verify ground truth files**
  ```bash
  ls -lh ground_truth/
  # Should see 19 JSON files
  ```

- [ ] **Validate ground truth** (optional)
  ```bash
  poetry run python src/ground_truth_generator.py validate
  # All should pass
  ```

### Step 2: Run Evaluations

- [ ] **Run evaluations**
  ```bash
  poetry run python src/runner.py
  ```

- [ ] **Check output**
  - No errors?
  - Success rate: X/Y?
  - Total cost reasonable?
  - Results directory created?

- [ ] **Verify result files**
  ```bash
  ls results/run_*/
  # Should see individual JSONs + summary.json
  ```

### Step 3: Evaluate Results

- [ ] **Run evaluator**
  ```bash
  poetry run python src/evaluator.py results/run_<timestamp>
  ```

- [ ] **Review report**
  - Validation pass rate?
  - Ground truth similarity?
  - Any patterns in failures?

- [ ] **Check evaluation report**
  ```bash
  cat results/run_<timestamp>/evaluation_report.json | head -50
  ```

## Analysis

- [ ] **Identify best performing model**
  - Highest similarity %?
  - Best cost/performance ratio?

- [ ] **Identify problem prompts**
  - Which prompts have low pass rates?
  - Which prompts have low similarity?

- [ ] **Review individual failures**
  ```bash
  # Find a failed result
  cat results/run_<timestamp>/<prompt_id>_<model>.json
  ```

## Next Steps

- [ ] **Decide on production model**
  - Based on cost, speed, accuracy

- [ ] **Refine problematic prompts**
  - Edit `config/prompts.yaml`
  - Regenerate ground truth
  - Re-run evaluations

- [ ] **Document findings**
  - Create comparison table
  - Note model strengths/weaknesses
  - Cost analysis

## Troubleshooting

### "No ground truth file found"
→ Run: `poetry run python src/ground_truth_generator.py generate`

### "API key not found"
→ Check `.env` file exists and has correct keys

### "Rate limit exceeded"
→ Add delay between requests or use cheaper models

### "JSON parse error"
→ Some models may not support structured output properly

### "Validation failed"
→ Review which metrics failed in evaluation report

### "Cost too high"
→ Start with prompt/model filters, test incrementally

## Quick Reference

```bash
# Generate ground truth
poetry run python src/ground_truth_generator.py generate

# Run evaluations
poetry run python src/runner.py

# Evaluate results
poetry run python src/evaluator.py results/run_<timestamp>

# Validate ground truth
poetry run python src/ground_truth_generator.py validate
```

## Notes

- Results are immutable (timestamped directories)
- Ground truth is preserved unless `--force` is used
- You can re-run evaluator on old results with new ground truth
- All costs are estimates based on current pricing

---

**Ready to run?** Start with the Quick Start in [README.md](README.md)!
