"""
Ground truth generator - creates reference workouts using a strong LLM.
"""

import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from model_providers import get_provider
from evaluator import WorkoutEvaluator


class GroundTruthGenerator:
    """Generates ground truth workouts using a reference model."""

    def __init__(
        self,
        config_dir: str = "config",
        ground_truth_dir: str = "ground_truth",
    ):
        self.config_dir = Path(config_dir)
        self.ground_truth_dir = Path(ground_truth_dir)
        self.ground_truth_dir.mkdir(parents=True, exist_ok=True)

        # Load configurations
        self.gt_config = self._load_yaml(
            self.config_dir / "ground_truth.yaml"
        )
        self.prompts_config = self._load_yaml(
            self.config_dir / "prompts.yaml"
        )
        self.models_config = self._load_yaml(
            self.config_dir / "models.yaml"
        )

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

    def _find_model_config(
        self, provider: str, model_id: str
    ) -> Optional[Dict]:
        """Find model configuration in models.yaml."""
        for model in self.models_config["models"]:
            if (
                model["provider"] == provider
                and model["model_id"] == model_id
            ):
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

        print(f"  Generating ground truth for: {prompt_id}")

        provider_name = self.reference_model["provider"]
        model_id = self.reference_model["model_id"]
        display_name = self.reference_model["display_name"]

        max_retries = self.gt_config["generation"].get(
            "max_retries", 3
        )
        validate = self.gt_config["generation"].get(
            "validate_before_saving", True
        )

        # Track cumulative cost across all attempts
        total_cost_all_attempts = 0.0
        all_attempts_metadata = []

        for attempt in range(max_retries):
            try:
                # Generate workout
                provider = get_provider(provider_name)
                response = provider.generate(
                    model_id=model_id,
                    user_prompt=user_prompt,
                    ftp=ftp,
                    input_price_per_million=self.reference_model[
                        "pricing"
                    ]["input_per_million"],
                    output_price_per_million=self.reference_model[
                        "pricing"
                    ]["output_per_million"],
                )

                # Track this attempt's cost
                total_cost_all_attempts += response.cost
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
                    }
                )

                # Parse JSON
                try:
                    workout = json.loads(response.content)
                except json.JSONDecodeError as e:
                    print(
                        f"    Attempt {attempt + 1}: JSON parse error - {str(e)}"
                    )
                    if attempt < max_retries - 1:
                        continue
                    raise

                # Validate if requested
                if validate:
                    evaluator = WorkoutEvaluator(ftp)
                    evaluation = evaluator.evaluate(workout)

                    if not evaluation["all_passed"]:
                        print(
                            f"    Attempt {attempt + 1}: Validation failed "
                            f"(pass rate: {evaluation['pass_rate']}%)"
                        )
                        if attempt < max_retries - 1:
                            print("    Retrying...")
                            continue
                        else:
                            # Fail properly instead of accepting invalid workout
                            raise ValueError(
                                f"Ground truth validation failed after {max_retries} attempts. "
                                f"Pass rate: {evaluation['pass_rate']}%"
                            )

                # Success! Build ground truth object
                ground_truth = {
                    "prompt_id": prompt_id,
                    "prompt_description": prompt_config[
                        "description"
                    ],
                    "user_prompt": user_prompt,
                    "ftp": ftp,
                    "reference_model": {
                        "provider": provider_name,
                        "model_id": model_id,
                        "display_name": display_name,
                    },
                    "generated_at": datetime.now().isoformat(),
                    "generation_metadata": {
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
                    },
                    "workout": workout,
                }

                if validate:
                    ground_truth["validation_results"] = evaluation

                print(
                    f"    ✓ Generated successfully "
                    f"(attempt {attempt + 1}, {response.latency_ms}ms)"
                )
                return ground_truth

            except Exception as e:
                print(f"    Attempt {attempt + 1}: Error - {str(e)}")
                if attempt < max_retries - 1:
                    continue
                raise

        raise RuntimeError(
            f"Failed to generate ground truth after {max_retries} attempts"
        )

    def generate_all(
        self, prompt_filter: list = None, force: bool = False
    ):
        """Generate ground truth for all prompts."""
        ftp = self.prompts_config["ftp"]
        prompts = self.prompts_config["prompts"]

        # Apply filter if provided
        if prompt_filter:
            prompts = [p for p in prompts if p["id"] in prompt_filter]

        overwrite = force or self.gt_config["generation"].get(
            "overwrite_existing", False
        )

        print(f"\n{'=' * 80}")
        print("Ground Truth Generation")
        print(
            f"Reference Model: {self.reference_model['display_name']} "
            f"({self.reference_model['provider']}/{self.reference_model['model_id']})"
        )
        print(f"FTP: {ftp}W")
        print(f"Prompts: {len(prompts)}")
        print(f"Overwrite existing: {overwrite}")
        print(f"{'=' * 80}\n")

        generated = 0
        skipped = 0
        failed = 0

        for prompt_config in prompts:
            prompt_id = prompt_config["id"]
            gt_file = self.ground_truth_dir / f"{prompt_id}.json"

            # Check if already exists
            if gt_file.exists() and not overwrite:
                print(f"  Skipping {prompt_id} (already exists)")
                skipped += 1
                continue

            try:
                ground_truth = self.generate_ground_truth(
                    prompt_config, ftp
                )
                self._save_json(ground_truth, gt_file)
                generated += 1

            except Exception as e:
                print(f"  ✗ Failed to generate {prompt_id}: {str(e)}")
                failed += 1

        print(f"\n{'=' * 80}")
        print("Ground Truth Generation Complete!")
        print(f"Generated: {generated}")
        print(f"Skipped: {skipped}")
        print(f"Failed: {failed}")
        print(f"Ground truth saved to: {self.ground_truth_dir}")
        print(f"{'=' * 80}\n")

        return {
            "generated": generated,
            "skipped": skipped,
            "failed": failed,
        }

    def validate_ground_truth(self, prompt_id: str = None):
        """Validate existing ground truth files."""
        if prompt_id:
            files = [self.ground_truth_dir / f"{prompt_id}.json"]
        else:
            files = list(self.ground_truth_dir.glob("*.json"))

        print(f"\nValidating {len(files)} ground truth file(s)...\n")

        results = []
        for gt_file in files:
            with open(gt_file, "r") as f:
                ground_truth = json.load(f)

            ftp = ground_truth["ftp"]
            workout = ground_truth["workout"]
            prompt_id = ground_truth["prompt_id"]

            evaluator = WorkoutEvaluator(ftp)
            evaluation = evaluator.evaluate(workout)

            status = (
                "✓ PASS" if evaluation["all_passed"] else "✗ FAIL"
            )
            print(
                f"  {status} {prompt_id} "
                f"(pass rate: {evaluation['pass_rate']}%)"
            )

            results.append(
                {
                    "prompt_id": prompt_id,
                    "file": str(gt_file),
                    "all_passed": evaluation["all_passed"],
                    "pass_rate": evaluation["pass_rate"],
                }
            )

        print("\nValidation complete!")
        passed = sum(1 for r in results if r["all_passed"])
        print(f"Passed: {passed}/{len(results)}")

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
        generator.generate_all(
            prompt_filter=args.prompts, force=args.force
        )
    elif args.action == "validate":
        if args.prompts:
            for prompt_id in args.prompts:
                generator.validate_ground_truth(prompt_id)
        else:
            generator.validate_ground_truth()


if __name__ == "__main__":
    main()
