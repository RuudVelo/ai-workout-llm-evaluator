#!/usr/bin/env python3
"""
Script to update display_name values inside JSON files to match current models.yaml.

This script updates the display_name field in the JSON content (not the filename).
It matches files by provider + model_id and updates the display_name to what's
currently configured in models.yaml.

Usage:
    python update_json_display_names.py <run_folder_path>

Example:
    python update_json_display_names.py results/run_20251105_164834

Options:
    --dry-run    : Show what would be updated without actually modifying files
"""

import json
import yaml
import argparse
from pathlib import Path
from typing import Dict


def load_current_model_config(models_yaml_path: str = "config/models.yaml") -> Dict:
    """
    Load current models.yaml and create a mapping of (provider, model_id) -> display_name.
    """
    try:
        with open(models_yaml_path, "r") as f:
            config = yaml.safe_load(f)

        mapping = {}
        for model in config.get("models", []):
            key = (model["provider"], model["model_id"])
            mapping[key] = model["display_name"]

        return mapping
    except Exception as e:
        print(f"Error loading models.yaml: {e}")
        return {}


def update_json_display_name(
    json_file: Path, config_mapping: Dict, dry_run: bool = False
) -> bool:
    """
    Update the display_name field inside a JSON file to match current config.

    Args:
        json_file: Path to the JSON file
        config_mapping: Mapping of (provider, model_id) -> current display_name
        dry_run: If True, don't actually modify the file

    Returns:
        True if file was updated (or would be updated in dry run), False otherwise
    """
    # Skip special files
    if json_file.name in ["summary.json", "evaluation.json"]:
        return False

    # Skip log files
    if json_file.suffix == ".log":
        return False

    try:
        with open(json_file, "r") as f:
            data = json.load(f)

        # Extract model info
        model_info = data.get("model", {})
        provider = model_info.get("provider")
        model_id = model_info.get("model_id")
        current_display_name = model_info.get("display_name")

        if not provider or not model_id:
            print(f"  ⚠️  Skipping: Missing provider or model_id")
            return False

        # Look up new display name
        key = (provider, model_id)
        if key not in config_mapping:
            print(f"  ⚠️  Model {provider}/{model_id} not found in current config")
            return False

        new_display_name = config_mapping[key]

        # Check if update is needed
        if current_display_name == new_display_name:
            print(f"  ✓ Already up to date: {current_display_name}")
            return False

        print(f"  📝 Old: {current_display_name}")
        print(f"  📝 New: {new_display_name}")

        if not dry_run:
            # Update the display_name in the JSON
            data["model"]["display_name"] = new_display_name

            # Write back to file (preserving formatting with indent)
            with open(json_file, "w") as f:
                json.dump(data, f, indent=2)

            print(f"  ✓ Updated successfully")
        else:
            print(f"  → Would update (dry run)")

        return True

    except json.JSONDecodeError:
        print(f"  ❌ Error: Not valid JSON")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def update_run_folder(run_folder: str, dry_run: bool = False):
    """
    Update all JSON files in a run folder to use current display_names from models.yaml.

    Args:
        run_folder: Path to the run folder
        dry_run: If True, only show what would be done
    """
    run_path = Path(run_folder)

    if not run_path.exists():
        print(f"❌ Error: Run folder does not exist: {run_folder}")
        return

    if not run_path.is_dir():
        print(f"❌ Error: Path is not a directory: {run_folder}")
        return

    print(f"\n{'=' * 80}")
    print("Update JSON Display Names Script")
    print(f"{'=' * 80}")
    print(f"Run folder: {run_folder}")
    print(
        f"Mode: {'DRY RUN (no files will be modified)' if dry_run else 'LIVE (JSON files will be updated)'}"
    )
    print(f"{'=' * 80}\n")

    # Load current config
    config_mapping = load_current_model_config()
    print(f"✓ Loaded {len(config_mapping)} models from config/models.yaml")
    print(f"\nCurrent model display names in config:")
    for (provider, model_id), display_name in sorted(config_mapping.items()):
        print(f"  • {provider}/{model_id} → {display_name}")
    print()

    # Find all JSON files
    json_files = list(run_path.glob("*.json"))

    if not json_files:
        print("⚠️  No JSON files found in the run folder")
        return

    print(f"Found {len(json_files)} JSON files\n")

    # Process each file
    updated_count = 0
    skipped_count = 0
    error_count = 0

    for json_file in sorted(json_files):
        print(f"Processing: {json_file.name}")

        try:
            updated = update_json_display_name(json_file, config_mapping, dry_run)
            if updated:
                updated_count += 1
            else:
                skipped_count += 1
        except Exception as e:
            print(f"  ❌ Unexpected error: {e}")
            error_count += 1

        print()

    # Summary
    print(f"{'=' * 80}")
    print("Update Summary")
    print(f"{'=' * 80}")
    print(f"Total files processed: {len(json_files)}")
    print(f"Files updated: {updated_count}")
    print(f"Files skipped: {skipped_count}")
    print(f"Errors: {error_count}")

    if dry_run:
        print(f"\n⚠️  This was a DRY RUN - no files were actually modified")
        print(f"Run without --dry-run to perform the actual updates")
    else:
        print(f"\n✓ Update completed successfully!")

    print(f"{'=' * 80}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Update display_name values in JSON files to match current models.yaml",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (preview changes)
  python update_json_display_names.py results/run_20251105_164834 --dry-run

  # Actually update JSON files
  python update_json_display_names.py results/run_20251105_164834

Note:
  This script updates the display_name INSIDE the JSON files, not the filenames.
  Use migrate_run_filenames.py to update filenames.
        """,
    )

    parser.add_argument(
        "run_folder",
        help="Path to the run folder (e.g., results/run_20251105_164834)",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be updated without actually modifying files",
    )

    args = parser.parse_args()

    update_run_folder(args.run_folder, args.dry_run)


if __name__ == "__main__":
    main()
