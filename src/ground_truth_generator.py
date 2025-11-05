"""
Ground truth generator - creates reference workouts using a strong LLM.
"""

import json
import yaml
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from model_providers import get_provider
from evaluator import WorkoutEvaluator
from postprocessor import WorkoutPostprocessor


def setup_logging(log_dir: Path, run_name: str) -> logging.Logger:
    """Setup logging to both file and console."""
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"{run_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    # Create logger
    logger = logging.getLogger(run_name)
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


class GroundTruthGenerator:
    """Generates ground truth workouts using a reference model."""

    def __init__(
        self,
        config_dir: str = "config",
        ground_truth_dir: str = "ground_truth",
        log_dir: str = "logs",
    ):
        self.config_dir = Path(config_dir)
        self.ground_truth_base_dir = Path(ground_truth_dir)

        # Create timestamped run directory
        self.run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.ground_truth_dir = self.ground_truth_base_dir / f"run_{self.run_timestamp}"
        self.ground_truth_dir.mkdir(parents=True, exist_ok=True)

        # Setup logging
        self.log_dir = Path(log_dir)
        self.logger = setup_logging(self.log_dir, "ground_truth_generation")

        # Load configurations
        self.gt_config = self._load_yaml(self.config_dir / "ground_truth.yaml")
        self.prompts_config = self._load_yaml(self.config_dir / "prompts.yaml")
        self.models_config = self._load_yaml(self.config_dir / "models.yaml")

        # Get reference model config
        ref_model = self.gt_config["reference_model"]
        self.reference_model = self._find_model_config(
            ref_model["provider"], ref_model["model_id"]
        )

        if not self.reference_model:
            raise ValueError(
                f"Reference model not found in models.yaml: "
                f"{ref_model['provider']}/{ref_model['model_id']}"
            )

    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        """Load YAML configuration file."""
        with open(path, "r") as f:
            return yaml.safe_load(f)

    def _find_model_config(self, provider: str, model_id: str) -> Optional[Dict]:
        """Find model configuration in models.yaml."""
        for model in self.models_config["models"]:
            if model["provider"] == provider and model["model_id"] == model_id:
                return model
        return None

    def _save_json(self, data: Dict[str, Any], path: Path):
        """Save data as JSON file."""
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def generate_ground_truth(
        self, prompt_config: Dict[str, Any], ftp: int
    ) -> Dict[str, Any]:
        """Generate a ground truth workout for a single prompt."""
        prompt_id = prompt_config["id"]
        user_prompt = prompt_config["user_prompt"]

        self.logger.info(f"  Generating ground truth for: {prompt_id}")

        provider_name = self.reference_model["provider"]
        model_id = self.reference_model["model_id"]
        display_name = self.reference_model["display_name"]

        max_retries = self.gt_config["generation"].get("max_retries", 3)
        validate = self.gt_config["generation"].get("validate_before_saving", True)

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
                # Generate workout
                provider = get_provider(provider_name)
                response = provider.generate(
                    model_id=model_id,
                    user_prompt=user_prompt,
                    ftp=ftp,
                    input_price_per_million=self.reference_model["pricing"][
                        "input_per_million"
                    ],
                    output_price_per_million=self.reference_model["pricing"][
                        "output_per_million"
                    ],
                    reasoning_effort=self.reference_model.get("reasoning_effort"),
                )

                # Calculate input and output costs for this attempt
                input_cost = (
                    response.input_tokens
                    * self.reference_model["pricing"]["input_per_million"]
                    / 1_000_000
                )
                output_cost = (
                    response.output_tokens
                    * self.reference_model["pricing"]["output_per_million"]
                    / 1_000_000
                )

                # Track this attempt's metrics
                total_cost_all_attempts += response.cost
                total_input_cost_all_attempts += input_cost
                total_output_cost_all_attempts += output_cost
                total_latency_all_attempts += response.latency_ms
                total_input_tokens_all_attempts += response.input_tokens
                total_output_tokens_all_attempts += response.output_tokens

                all_attempts_metadata.append(
                    {
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
                    }
                )

                # Parse JSON
                parse_error = None
                workout = None
                try:
                    workout = json.loads(response.content)
                except json.JSONDecodeError as e:
                    parse_error = str(e)
                    self.logger.info(f"    Attempt {attempt + 1}: JSON parse error - {str(e)}")
                    if attempt < max_retries - 1:
                        continue
                    # Last attempt with parse error - still save the result
                    self.logger.warning(f"    ⚠ Parse failed after {max_retries} attempts, recording with error")

                    # Build ground truth object with parse error
                    ground_truth = {
                        "prompt_id": prompt_id,
                        "prompt_description": prompt_config["description"],
                        "user_prompt": user_prompt,
                        "ftp": ftp,
                        "reference_model": {
                            "provider": provider_name,
                            "model_id": model_id,
                            "display_name": display_name,
                        },
                        "generated_at": datetime.now().isoformat(),
                        "generation_metadata": {
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
                        },
                        "parse_error": parse_error,
                        "raw_response": response.content,
                        "validation_passed": False,
                        "workout": None,
                    }
                    return ground_truth

                # Apply postprocessing fixes to parsed JSON (before validation)
                postprocessor = WorkoutPostprocessor(ftp, self.logger)
                workout = postprocessor.postprocess(workout)

                # Validate if requested
                if validate:
                    evaluator = WorkoutEvaluator(ftp)
                    evaluation = evaluator.evaluate(workout)

                    if not evaluation["all_passed"]:
                        self.logger.info(
                            f"    Attempt {attempt + 1}: Validation failed "
                            f"(pass rate: {evaluation['pass_rate']}%)"
                        )
                        if attempt < max_retries - 1:
                            self.logger.info("    Retrying...")
                            continue
                        else:
                            # Last attempt with validation failure - still save the result
                            self.logger.warning(
                                f"    ⚠ Validation failed after {max_retries} attempts "
                                f"(pass rate: {evaluation['pass_rate']}%), recording with flag"
                            )
                            # Continue to build ground truth object with validation failure flag

                # Build ground truth object (either success or failed validation on last attempt)
                ground_truth = {
                    "prompt_id": prompt_id,
                    "prompt_description": prompt_config["description"],
                    "user_prompt": user_prompt,
                    "ftp": ftp,
                    "reference_model": {
                        "provider": provider_name,
                        "model_id": model_id,
                        "display_name": display_name,
                    },
                    "generated_at": datetime.now().isoformat(),
                    "generation_metadata": {
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
                    },
                    "workout": workout,
                }

                if validate:
                    ground_truth["validation_results"] = evaluation
                    ground_truth["validation_passed"] = evaluation["all_passed"]
                else:
                    ground_truth["validation_passed"] = None

                if validate and not evaluation["all_passed"]:
                    self.logger.warning(
                        f"    ⚠ Generated with validation failure "
                        f"(attempt {attempt + 1}, pass rate: {evaluation['pass_rate']}%)"
                    )
                else:
                    self.logger.info(
                        f"    ✓ Generated successfully "
                        f"(attempt {attempt + 1}, {response.latency_ms}ms)"
                    )
                return ground_truth

            except Exception as e:
                self.logger.info(f"    Attempt {attempt + 1}: Error - {str(e)}")

                # Track this attempt even if it errored
                if attempt >= max_retries - 1:
                    # Last attempt with exception - still save the result
                    self.logger.warning(f"    ⚠ Generation failed after {max_retries} attempts, recording with error")

                    # Build ground truth object with error
                    ground_truth = {
                        "prompt_id": prompt_id,
                        "prompt_description": prompt_config["description"],
                        "user_prompt": user_prompt,
                        "ftp": ftp,
                        "reference_model": {
                            "provider": provider_name,
                            "model_id": model_id,
                            "display_name": display_name,
                        },
                        "generated_at": datetime.now().isoformat(),
                        "generation_metadata": {
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
                        },
                        "error": str(e),
                        "validation_passed": False,
                        "workout": None,
                    }
                    return ground_truth

                # Not last attempt, continue retrying
                continue

        # Should never reach here, but just in case
        return {
            "prompt_id": prompt_id,
            "error": "Maximum retries exceeded without success",
            "validation_passed": False,
        }

    def generate_all(self, prompt_filter: list = None, force: bool = False):
        """Generate ground truth for all prompts."""
        ftp = self.prompts_config["ftp"]
        prompts = self.prompts_config["prompts"]

        # Apply filter if provided
        if prompt_filter:
            prompts = [p for p in prompts if p["id"] in prompt_filter]

        overwrite = force or self.gt_config["generation"].get(
            "overwrite_existing", False
        )

        self.logger.info(f"\n{'=' * 80}")
        self.logger.info("Ground Truth Generation")
        self.logger.info(
            f"Reference Model: {self.reference_model['display_name']} "
            f"({self.reference_model['provider']}/{self.reference_model['model_id']})"
        )
        self.logger.info(f"FTP: {ftp}W")
        self.logger.info(f"Prompts: {len(prompts)}")
        self.logger.info(f"Overwrite existing: {overwrite}")
        self.logger.info(f"Run directory: {self.ground_truth_dir}")
        self.logger.info(f"Logs will be saved to: {self.log_dir}")
        self.logger.info(f"{'=' * 80}\n")

        generated = 0
        skipped = 0
        generated_with_errors = 0

        for prompt_config in prompts:
            prompt_id = prompt_config["id"]
            gt_file = self.ground_truth_dir / f"{prompt_id}.json"

            # Check if already exists
            if gt_file.exists() and not overwrite:
                self.logger.info(f"  Skipping {prompt_id} (already exists)")
                skipped += 1
                continue

            # Always generate and save - generate_ground_truth now returns a result even on failure
            ground_truth = self.generate_ground_truth(prompt_config, ftp)
            self._save_json(ground_truth, gt_file)

            # Check if it was successful or had errors/validation failures
            if ground_truth.get("validation_passed") is False or ground_truth.get("error") or ground_truth.get("parse_error"):
                generated_with_errors += 1
            else:
                generated += 1

        self.logger.info(f"\n{'=' * 80}")
        self.logger.info("Ground Truth Generation Complete!")
        self.logger.info(f"Generated successfully: {generated}")
        self.logger.info(f"Generated with errors/validation failures: {generated_with_errors}")
        self.logger.info(f"Skipped: {skipped}")
        self.logger.info(f"Ground truth saved to: {self.ground_truth_dir}")
        self.logger.info(f"{'=' * 80}\n")

        return {
            "generated": generated,
            "generated_with_errors": generated_with_errors,
            "skipped": skipped,
        }

    def validate_ground_truth(self, prompt_id: str = None):
        """Validate existing ground truth files."""
        if prompt_id:
            files = [self.ground_truth_dir / f"{prompt_id}.json"]
        else:
            files = list(self.ground_truth_dir.glob("*.json"))

        self.logger.info(f"\nValidating {len(files)} ground truth file(s)...\n")

        results = []
        for gt_file in files:
            with open(gt_file, "r") as f:
                ground_truth = json.load(f)

            ftp = ground_truth["ftp"]
            workout = ground_truth["workout"]
            prompt_id = ground_truth["prompt_id"]

            evaluator = WorkoutEvaluator(ftp)
            evaluation = evaluator.evaluate(workout)

            status = "✓ PASS" if evaluation["all_passed"] else "✗ FAIL"
            self.logger.info(f"  {status} {prompt_id} " f"(pass rate: {evaluation['pass_rate']}%)")

            results.append(
                {
                    "prompt_id": prompt_id,
                    "file": str(gt_file),
                    "all_passed": evaluation["all_passed"],
                    "pass_rate": evaluation["pass_rate"],
                }
            )

        self.logger.info("\nValidation complete!")
        passed = sum(1 for r in results if r["all_passed"])
        self.logger.info(f"Passed: {passed}/{len(results)}")

        return results


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate or validate ground truth workouts"
    )
    parser.add_argument(
        "action",
        choices=["generate", "validate"],
        help="Action to perform",
    )
    parser.add_argument(
        "--prompts",
        nargs="+",
        help="Specific prompt IDs to process (optional)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force overwrite existing ground truth files",
    )

    args = parser.parse_args()

    generator = GroundTruthGenerator()

    if args.action == "generate":
        generator.generate_all(prompt_filter=args.prompts, force=args.force)
    elif args.action == "validate":
        if args.prompts:
            for prompt_id in args.prompts:
                generator.validate_ground_truth(prompt_id)
        else:
            generator.validate_ground_truth()


if __name__ == "__main__":
    main()
