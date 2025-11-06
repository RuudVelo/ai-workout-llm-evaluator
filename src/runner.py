"""
Main runner to execute prompts across all configured models.
"""

import json
import yaml
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import traceback

from model_providers import get_provider, ModelResponse
from evaluator import WorkoutEvaluator
from postprocessor import WorkoutPostprocessor


def sanitize_display_name(display_name: str) -> str:
    """
    Convert display_name to filesystem-safe string.

    Removes or replaces characters that are problematic for filenames:
    - Slashes (/) → underscores
    - Spaces → underscores
    - Parentheses → removed
    - Other special characters as needed

    Args:
        display_name: The model's display name (e.g., "GPT-4o", "Claude 3.5 Sonnet")

    Returns:
        Sanitized string safe for use in filenames
    """
    sanitized = display_name
    sanitized = sanitized.replace('/', '_')
    sanitized = sanitized.replace(' ', '_')
    sanitized = sanitized.replace('(', '')
    sanitized = sanitized.replace(')', '')
    sanitized = sanitized.replace('[', '')
    sanitized = sanitized.replace(']', '')
    return sanitized


def setup_logging(log_file: Path) -> logging.Logger:
    """Setup logging to both file and console."""
    log_file.parent.mkdir(parents=True, exist_ok=True)

    # Create logger
    logger = logging.getLogger("evaluation_runner")
    logger.setLevel(logging.INFO)

    # Remove existing handlers to avoid duplicates
    logger.handlers = []

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(message)s')
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


class EvalRunner:
    """Runs evaluation prompts across multiple models."""

    def __init__(self, config_dir: str = "config", results_dir: str = "results"):
        self.config_dir = Path(config_dir)
        self.results_dir = Path(results_dir)

        # Load configurations
        self.models_config = self._load_yaml(self.config_dir / "models.yaml")
        self.prompts_config = self._load_yaml(self.config_dir / "prompts.yaml")
        self.gt_config = self._load_yaml(self.config_dir / "ground_truth.yaml")

        # Get reference model info (used to skip it during evaluation)
        ref_model = self.gt_config["reference_model"]
        self.reference_provider = ref_model["provider"]
        self.reference_model_id = ref_model["model_id"]

        # Create timestamped results directory
        self.run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_dir = self.results_dir / f"run_{self.run_timestamp}"
        self.run_dir.mkdir(parents=True, exist_ok=True)

        # Setup logging to file in run directory
        log_file = self.run_dir / f"evaluation_{self.run_timestamp}.log"
        self.logger = setup_logging(log_file)

    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        """Load YAML configuration file."""
        with open(path, "r") as f:
            return yaml.safe_load(f)

    def _save_json(self, data: Dict[str, Any], path: Path):
        """Save data as JSON file."""
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def run_single_evaluation(
        self,
        model_config: Dict[str, Any],
        prompt_config: Dict[str, Any],
        ftp: int,
        max_retries: int = 2,
    ) -> Dict[str, Any]:
        """Run a single prompt against a single model with full validation and retry logic (Option B)."""
        provider_name = model_config["provider"]
        model_id = model_config["model_id"]
        display_name = model_config["display_name"]
        prompt_id = prompt_config["id"]
        user_prompt = prompt_config["user_prompt"]

        self.logger.info(f"  Running {display_name} on prompt: {prompt_id}")

        # Track cumulative metrics across all attempts
        total_cost_all_attempts = 0.0
        total_input_cost_all_attempts = 0.0
        total_output_cost_all_attempts = 0.0
        total_latency_all_attempts = 0
        total_input_tokens_all_attempts = 0
        total_output_tokens_all_attempts = 0
        all_attempts_metadata = []

        for attempt in range(max_retries):
            try:
                # Get provider and generate
                provider = get_provider(provider_name)

                response: ModelResponse = provider.generate(
                    model_id=model_id,
                    user_prompt=user_prompt,
                    ftp=ftp,
                    input_price_per_million=model_config["pricing"][
                        "input_per_million"
                    ],
                    output_price_per_million=model_config["pricing"][
                        "output_per_million"
                    ],
                    reasoning_effort=model_config.get("reasoning_effort"),
                    temperature=model_config.get("temperature"),
                )

                # Calculate input and output costs for this attempt
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

                # Try to parse JSON response
                try:
                    parsed_json = json.loads(response.content)
                    parse_error = None
                except json.JSONDecodeError as e:
                    parsed_json = None
                    parse_error = str(e)

                # Apply postprocessing fixes if JSON parsed successfully (before validation)
                if parsed_json is not None:
                    postprocessor = WorkoutPostprocessor(ftp, self.logger)
                    parsed_json = postprocessor.postprocess(parsed_json)

                # Run validation if JSON parsed successfully
                validation_result = None
                validation_passed = False

                if parsed_json is not None:
                    evaluator = WorkoutEvaluator(ftp)
                    validation_result = evaluator.evaluate(parsed_json)
                    validation_passed = validation_result["all_passed"]

                # Track this attempt's metrics
                total_cost_all_attempts += response.cost
                total_input_cost_all_attempts += input_cost
                total_output_cost_all_attempts += output_cost
                total_latency_all_attempts += response.latency_ms
                total_input_tokens_all_attempts += response.input_tokens
                total_output_tokens_all_attempts += response.output_tokens

                # Track this attempt's metadata
                attempt_metadata = {
                    "attempt": attempt + 1,
                    "latency_ms": response.latency_ms,
                    "tokens": {
                        "input": response.input_tokens,
                        "output": response.output_tokens,
                        "total": response.total_tokens,
                    },
                    "cost": round(response.cost, 6),
                    "input_cost": round(input_cost, 6),
                    "output_cost": round(output_cost, 6),
                    "parse_error": parse_error,
                    "validation_passed": validation_passed,
                }

                if validation_result:
                    attempt_metadata["validation_pass_rate"] = validation_result[
                        "pass_rate"
                    ]
                    attempt_metadata["validation_score"] = validation_result[
                        "overall_score"
                    ]

                all_attempts_metadata.append(attempt_metadata)

                # Retry logic: retry on parse error OR validation failure (Option B)
                if parse_error is not None:
                    if attempt < max_retries - 1:
                        self.logger.info(
                            f"    Attempt {attempt + 1}: JSON parse error, retrying..."
                        )
                        continue
                    # Last attempt, will return with error below

                elif not validation_passed:
                    if attempt < max_retries - 1:
                        self.logger.info(
                            f"    Attempt {attempt + 1}: Validation failed "
                            f"(pass rate: {validation_result['pass_rate']}%), retrying..."
                        )
                        continue
                    # Last attempt, will return with validation failure (Option B2: accept but flag)
                    self.logger.warning(
                        f"    ⚠ Validation failed after {max_retries} attempts "
                        f"(pass rate: {validation_result['pass_rate']}%), recording with flag"
                    )

                # Build result (either success or failed validation on last attempt)
                result = {
                    "prompt_id": prompt_id,
                    "prompt_description": prompt_config["description"],
                    "user_prompt": user_prompt,
                    "model": {
                        "provider": provider_name,
                        "model_id": model_id,
                        "display_name": display_name,
                    },
                    "ftp": ftp,
                    "timestamp": datetime.now().isoformat(),
                    "attempts": attempt + 1,
                    "total_latency_all_attempts": total_latency_all_attempts,
                    "total_tokens_all_attempts": {
                        "input": total_input_tokens_all_attempts,
                        "output": total_output_tokens_all_attempts,
                        "total": total_input_tokens_all_attempts
                        + total_output_tokens_all_attempts,
                    },
                    "total_cost_all_attempts": round(total_cost_all_attempts, 6),
                    "total_input_cost_all_attempts": round(
                        total_input_cost_all_attempts, 6
                    ),
                    "total_output_cost_all_attempts": round(
                        total_output_cost_all_attempts, 6
                    ),
                    "all_attempts": all_attempts_metadata,
                    "response": {
                        "raw_content": response.content,
                        "parsed_json": parsed_json,
                        "parse_error": parse_error,
                    },
                    "validation": validation_result,
                    "success": parse_error is None and validation_passed,
                    "validation_failed": parse_error is None and not validation_passed,
                }

                if parse_error is None and validation_passed:
                    self.logger.info(
                        f"    ✓ Success (attempt {attempt + 1}, {response.latency_ms}ms)"
                    )
                elif parse_error is None and not validation_passed:
                    self.logger.warning(
                        f"    ⚠ Validation failed but recorded (attempt {attempt + 1})"
                    )
                else:
                    self.logger.warning(f"    ✗ Parse failed after {attempt + 1} attempt(s)")

                return result

            except Exception as e:
                # Handle errors gracefully
                self.logger.info(f"    Attempt {attempt + 1}: Error - {str(e)}")

                if attempt < max_retries - 1:
                    continue

                # All attempts failed
                self.logger.warning(f"    ✗ Failed after {max_retries} attempt(s)")

                return {
                    "prompt_id": prompt_id,
                    "prompt_description": prompt_config["description"],
                    "user_prompt": user_prompt,
                    "model": {
                        "provider": provider_name,
                        "model_id": model_id,
                        "display_name": display_name,
                    },
                    "ftp": ftp,
                    "timestamp": datetime.now().isoformat(),
                    "attempts": attempt + 1,
                    "total_latency_all_attempts": total_latency_all_attempts,
                    "total_tokens_all_attempts": {
                        "input": total_input_tokens_all_attempts,
                        "output": total_output_tokens_all_attempts,
                        "total": total_input_tokens_all_attempts
                        + total_output_tokens_all_attempts,
                    },
                    "total_cost_all_attempts": round(total_cost_all_attempts, 6),
                    "total_input_cost_all_attempts": round(
                        total_input_cost_all_attempts, 6
                    ),
                    "total_output_cost_all_attempts": round(
                        total_output_cost_all_attempts, 6
                    ),
                    "all_attempts": all_attempts_metadata,
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                    "success": False,
                    "validation_failed": False,
                }

        # Should never reach here, but just in case
        return {
            "prompt_id": prompt_id,
            "error": "Maximum retries exceeded without success",
            "attempts": max_retries,
            "total_latency_all_attempts": total_latency_all_attempts,
            "total_tokens_all_attempts": {
                "input": total_input_tokens_all_attempts,
                "output": total_output_tokens_all_attempts,
                "total": total_input_tokens_all_attempts
                + total_output_tokens_all_attempts,
            },
            "total_cost_all_attempts": round(total_cost_all_attempts, 6),
            "total_input_cost_all_attempts": round(
                total_input_cost_all_attempts, 6
            ),
            "total_output_cost_all_attempts": round(
                total_output_cost_all_attempts, 6
            ),
            "success": False,
            "validation_failed": False,
        }

    def run_all(
        self,
        model_filter: List[str] = None,
        prompt_filter: List[str] = None,
    ):
        """Run all prompts across all models."""
        ftp = self.prompts_config["ftp"]
        prompts = self.prompts_config["prompts"]
        models = self.models_config["models"]

        # Filter out ground truth reference model (to avoid duplicate generation/cost)
        original_model_count = len(models)
        models = [
            m for m in models
            if not (m["provider"] == self.reference_provider
                    and m["model_id"] == self.reference_model_id)
        ]
        skipped_reference_model = original_model_count > len(models)

        # Apply filters if provided
        # Support filtering by both model_id and display_name for flexibility
        if model_filter:
            models = [
                m for m in models
                if m["model_id"] in model_filter or m["display_name"] in model_filter
            ]

        if prompt_filter:
            prompts = [p for p in prompts if p["id"] in prompt_filter]

        self.logger.info(f"\n{'=' * 80}")
        self.logger.info(f"Starting evaluation run: {self.run_timestamp}")
        self.logger.info(f"FTP: {ftp}W")
        if skipped_reference_model:
            self.logger.info(f"⚠ Skipping ground truth reference model: {self.reference_provider}/{self.reference_model_id}")
            self.logger.info(f"  (Already generated via ground_truth_generator.py)")
        self.logger.info(f"Models to evaluate: {len(models)}")
        self.logger.info(f"Prompts: {len(prompts)}")
        self.logger.info(f"Total evaluations: {len(models) * len(prompts)}")
        self.logger.info(f"Results will be saved to: {self.run_dir}")
        self.logger.info(f"{'=' * 80}\n")

        all_results = []

        # Run each model against each prompt
        for model_config in models:
            self.logger.info(f"\n{model_config['display_name']}:")

            for prompt_config in prompts:
                result = self.run_single_evaluation(model_config, prompt_config, ftp)
                all_results.append(result)

                # Save individual result
                display_name_safe = sanitize_display_name(model_config['display_name'])
                filename = f"{prompt_config['id']}_{display_name_safe}.json"
                result_path = self.run_dir / filename
                self._save_json(result, result_path)

        # Calculate costs
        # For successful attempts, get cost from last attempt in all_attempts array
        total_cost_successful_only = sum(
            r.get("all_attempts", [{}])[-1].get("cost", 0)
            if r.get("all_attempts") else 0
            for r in all_results
        )
        total_cost_including_retries = sum(
            r.get("total_cost_all_attempts", 0) for r in all_results
        )

        # Calculate validation metrics
        successful_results = [r for r in all_results if r.get("success", False)]
        validation_failed_results = [
            r for r in all_results if r.get("validation_failed", False)
        ]
        parse_failed_results = [
            r
            for r in all_results
            if not r.get("success", False) and not r.get("validation_failed", False)
        ]

        # Save summary
        summary = {
            "run_timestamp": self.run_timestamp,
            "ftp": ftp,
            "total_evaluations": len(all_results),
            "successful": len(successful_results),
            "validation_failed": len(validation_failed_results),
            "parse_failed": len(parse_failed_results),
            "total_attempts": sum(r.get("attempts", 1) for r in all_results),
            "total_cost": round(total_cost_successful_only, 4),
            "total_cost_all_attempts": round(total_cost_including_retries, 4),
            "validation_metrics": {
                "successful_validations": len(successful_results),
                "failed_validations": len(validation_failed_results),
                "average_pass_rate": (
                    round(
                        sum(
                            r.get("validation", {}).get("pass_rate", 0)
                            for r in all_results
                            if r.get("validation")
                        )
                        / len([r for r in all_results if r.get("validation")]),
                        2,
                    )
                    if any(r.get("validation") for r in all_results)
                    else 0
                ),
            },
            "results": all_results,
        }

        summary_path = self.run_dir / "summary.json"
        self._save_json(summary, summary_path)

        self.logger.info(f"\n{'=' * 80}")
        self.logger.info("Evaluation complete!")
        self.logger.info(f"Total evaluations: {summary['total_evaluations']}")
        self.logger.info(f"  ✓ Successful (passed validation): {summary['successful']}")
        self.logger.info(f"  ⚠ Validation failed: {summary['validation_failed']}")
        self.logger.info(f"  ✗ Parse failed: {summary['parse_failed']}")
        self.logger.info(f"\nValidation metrics:")
        self.logger.info(
            f"  Average pass rate: {summary['validation_metrics']['average_pass_rate']:.2f}%"
        )
        self.logger.info(f"\nCost analysis:")
        self.logger.info(
            f"  Total attempts: {summary['total_attempts']} "
            f"(avg: {summary['total_attempts'] / summary['total_evaluations']:.2f} per eval)"
        )
        self.logger.info(f"  Total cost (successful attempts): ${summary['total_cost']:.4f}")
        self.logger.info(f"  Total cost (all attempts): ${summary['total_cost_all_attempts']:.4f}")
        if summary["total_cost_all_attempts"] > summary["total_cost"]:
            overhead = summary["total_cost_all_attempts"] - summary["total_cost"]
            self.logger.info(
                f"  → Retry overhead: ${overhead:.4f} "
                f"({(overhead / summary['total_cost_all_attempts'] * 100):.1f}% of total cost)"
            )
        self.logger.info(f"\nResults saved to: {self.run_dir}")
        self.logger.info(f"{'=' * 80}\n")

        return summary


def main():
    """Main entry point."""
    runner = EvalRunner()

    # You can optionally filter models or prompts
    # Example: runner.run_all(model_filter=["gpt-4o-mini"], prompt_filter=["simple_threshold_60min"])

    runner.run_all()


if __name__ == "__main__":
    main()
