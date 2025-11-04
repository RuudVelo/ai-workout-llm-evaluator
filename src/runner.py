"""
Main runner to execute prompts across all configured models.
"""

import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import traceback

from model_providers import get_provider, ModelResponse
from evaluator import WorkoutEvaluator


class EvalRunner:
    """Runs evaluation prompts across multiple models."""

    def __init__(
        self, config_dir: str = "config", results_dir: str = "results"
    ):
        self.config_dir = Path(config_dir)
        self.results_dir = Path(results_dir)

        # Load configurations
        self.models_config = self._load_yaml(
            self.config_dir / "models.yaml"
        )
        self.prompts_config = self._load_yaml(
            self.config_dir / "prompts.yaml"
        )

        # Create timestamped results directory
        self.run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_dir = self.results_dir / f"run_{self.run_timestamp}"
        self.run_dir.mkdir(parents=True, exist_ok=True)

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

        print(f"  Running {display_name} on prompt: {prompt_id}")

        # Track cumulative cost across all attempts
        total_cost_all_attempts = 0.0
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
                )

                # Try to parse JSON response
                try:
                    parsed_json = json.loads(response.content)
                    parse_error = None
                except json.JSONDecodeError as e:
                    parsed_json = None
                    parse_error = str(e)

                # Run validation if JSON parsed successfully
                validation_result = None
                validation_passed = False

                if parsed_json is not None:
                    evaluator = WorkoutEvaluator(ftp)
                    validation_result = evaluator.evaluate(parsed_json)
                    validation_passed = validation_result["all_passed"]

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
                    "parse_error": parse_error,
                    "validation_passed": validation_passed,
                }

                if validation_result:
                    attempt_metadata["validation_pass_rate"] = validation_result["pass_rate"]
                    attempt_metadata["validation_score"] = validation_result["overall_score"]

                total_cost_all_attempts += response.cost
                all_attempts_metadata.append(attempt_metadata)

                # Retry logic: retry on parse error OR validation failure (Option B)
                if parse_error is not None:
                    if attempt < max_retries - 1:
                        print(
                            f"    Attempt {attempt + 1}: JSON parse error, retrying..."
                        )
                        continue
                    # Last attempt, will return with error below

                elif not validation_passed:
                    if attempt < max_retries - 1:
                        print(
                            f"    Attempt {attempt + 1}: Validation failed "
                            f"(pass rate: {validation_result['pass_rate']}%), retrying..."
                        )
                        continue
                    # Last attempt, will return with validation failure (Option B2: accept but flag)
                    print(
                        f"    ⚠ Validation failed after {max_retries} attempts "
                        f"(pass rate: {validation_result['pass_rate']}%), recording with flag"
                    )

                # Build result (either success or failed validation on last attempt)
                result = {
                    "prompt_id": prompt_id,
                    "prompt_description": prompt_config[
                        "description"
                    ],
                    "user_prompt": user_prompt,
                    "model": {
                        "provider": provider_name,
                        "model_id": model_id,
                        "display_name": display_name,
                    },
                    "ftp": ftp,
                    "timestamp": datetime.now().isoformat(),
                    "latency_ms": response.latency_ms,
                    "tokens": {
                        "input": response.input_tokens,
                        "output": response.output_tokens,
                        "total": response.total_tokens,
                    },
                    "cost": round(response.cost, 6),
                    "attempts": attempt + 1,
                    "total_cost_all_attempts": round(
                        total_cost_all_attempts, 6
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
                    print(
                        f"    ✓ Success (attempt {attempt + 1}, {response.latency_ms}ms)"
                    )
                elif parse_error is None and not validation_passed:
                    print(
                        f"    ⚠ Validation failed but recorded (attempt {attempt + 1})"
                    )
                else:
                    print(
                        f"    ✗ Parse failed after {attempt + 1} attempt(s)"
                    )

                return result

            except Exception as e:
                # Handle errors gracefully
                print(f"    Attempt {attempt + 1}: Error - {str(e)}")

                if attempt < max_retries - 1:
                    continue

                # All attempts failed
                print(f"    ✗ Failed after {max_retries} attempt(s)")

                return {
                    "prompt_id": prompt_id,
                    "prompt_description": prompt_config[
                        "description"
                    ],
                    "user_prompt": user_prompt,
                    "model": {
                        "provider": provider_name,
                        "model_id": model_id,
                        "display_name": display_name,
                    },
                    "ftp": ftp,
                    "timestamp": datetime.now().isoformat(),
                    "attempts": attempt + 1,
                    "total_cost_all_attempts": round(
                        total_cost_all_attempts, 6
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
            "total_cost_all_attempts": round(
                total_cost_all_attempts, 6
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

        # Apply filters if provided
        if model_filter:
            models = [
                m for m in models if m["model_id"] in model_filter
            ]

        if prompt_filter:
            prompts = [p for p in prompts if p["id"] in prompt_filter]

        print(f"\n{'=' * 80}")
        print(f"Starting evaluation run: {self.run_timestamp}")
        print(f"FTP: {ftp}W")
        print(f"Models: {len(models)}")
        print(f"Prompts: {len(prompts)}")
        print(f"Total evaluations: {len(models) * len(prompts)}")
        print(f"{'=' * 80}\n")

        all_results = []

        # Run each model against each prompt
        for model_config in models:
            print(f"\n{model_config['display_name']}:")

            for prompt_config in prompts:
                result = self.run_single_evaluation(
                    model_config, prompt_config, ftp
                )
                all_results.append(result)

                # Save individual result
                filename = f"{prompt_config['id']}_{model_config['model_id'].replace('/', '_')}.json"
                result_path = self.run_dir / filename
                self._save_json(result, result_path)

        # Calculate costs
        total_cost_successful_only = sum(
            r.get("cost", 0) for r in all_results
        )
        total_cost_including_retries = sum(
            r.get("total_cost_all_attempts", r.get("cost", 0))
            for r in all_results
        )

        # Calculate validation metrics
        successful_results = [r for r in all_results if r.get("success", False)]
        validation_failed_results = [r for r in all_results if r.get("validation_failed", False)]
        parse_failed_results = [
            r for r in all_results
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
            "total_attempts": sum(
                r.get("attempts", 1) for r in all_results
            ),
            "total_cost": round(total_cost_successful_only, 4),
            "total_cost_all_attempts": round(
                total_cost_including_retries, 4
            ),
            "validation_metrics": {
                "successful_validations": len(successful_results),
                "failed_validations": len(validation_failed_results),
                "average_pass_rate": round(
                    sum(
                        r.get("validation", {}).get("pass_rate", 0)
                        for r in all_results
                        if r.get("validation")
                    ) / len([r for r in all_results if r.get("validation")]),
                    2
                ) if any(r.get("validation") for r in all_results) else 0,
            },
            "results": all_results,
        }

        summary_path = self.run_dir / "summary.json"
        self._save_json(summary, summary_path)

        print(f"\n{'=' * 80}")
        print("Evaluation complete!")
        print(
            f"Total evaluations: {summary['total_evaluations']}"
        )
        print(
            f"  ✓ Successful (passed validation): {summary['successful']}"
        )
        print(
            f"  ⚠ Validation failed: {summary['validation_failed']}"
        )
        print(
            f"  ✗ Parse failed: {summary['parse_failed']}"
        )
        print(
            f"\nValidation metrics:"
        )
        print(
            f"  Average pass rate: {summary['validation_metrics']['average_pass_rate']:.2f}%"
        )
        print(
            f"\nCost analysis:"
        )
        print(
            f"  Total attempts: {summary['total_attempts']} "
            f"(avg: {summary['total_attempts'] / summary['total_evaluations']:.2f} per eval)"
        )
        print(
            f"  Total cost (successful attempts): ${summary['total_cost']:.4f}"
        )
        print(
            f"  Total cost (all attempts): ${summary['total_cost_all_attempts']:.4f}"
        )
        if summary["total_cost_all_attempts"] > summary["total_cost"]:
            overhead = (
                summary["total_cost_all_attempts"]
                - summary["total_cost"]
            )
            print(
                f"  → Retry overhead: ${overhead:.4f} "
                f"({(overhead / summary['total_cost_all_attempts'] * 100):.1f}% of total cost)"
            )
        print(f"\nResults saved to: {self.run_dir}")
        print(f"{'=' * 80}\n")

        return summary


def main():
    """Main entry point."""
    runner = EvalRunner()

    # You can optionally filter models or prompts
    # Example: runner.run_all(model_filter=["gpt-4o-mini"], prompt_filter=["simple_threshold_60min"])

    runner.run_all()


if __name__ == "__main__":
    main()
