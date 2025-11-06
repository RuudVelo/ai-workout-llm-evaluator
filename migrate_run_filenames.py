#!/usr/bin/env python3
"""
Migration script to rename JSON files in old run folders.

This script updates filenames from the old format:
    {prompt_id}_{model_id}.json
to the new format:
    {prompt_id}_{sanitized_display_name}.json

The display_name is read from:
1. First, from the JSON file content itself (what was used during generation)
2. Then mapped to the CURRENT display_name in models.yaml for that provider/model_id

Usage:
    python migrate_run_filenames.py <run_folder_path>

Example:
    python migrate_run_filenames.py results/run_20251105_164834

Options:
    --dry-run    : Show what would be renamed without actually renaming
    --use-current: Use current display_names from models.yaml instead of JSON content
"""

import json
import yaml
import argparse
from pathlib import Path
from typing import Dict, Optional


def sanitize_display_name(display_name: str) -> str:
    """
    Convert display_name to filesystem-safe string.

    This matches the sanitize function in runner.py.
    """
    sanitized = display_name
    sanitized = sanitized.replace("/", "_")
    sanitized = sanitized.replace(" ", "_")
    sanitized = sanitized.replace("(", "")
    sanitized = sanitized.replace(")", "")
    sanitized = sanitized.replace("[", "")
    sanitized = sanitized.replace("]", "")
    return sanitized


def load_current_model_config(
    models_yaml_path: str = "config/models.yaml",
) -> Dict:
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


def get_new_filename(
    json_file: Path,
    use_current_config: bool = False,
    config_mapping: Optional[Dict] = None,
) -> Optional[str]:
    """
    Determine the new filename for a JSON file.

    Args:
        json_file: Path to the JSON file
        use_current_config: If True, use display_name from current models.yaml
        config_mapping: Mapping of (provider, model_id) -> current display_name

    Returns:
        New filename or None if file should not be renamed
    """
    # Skip special files
    if json_file.name in ["summary.json", "evaluation.json"]:
        return None

    # Skip log files
    if json_file.suffix == ".log":
        return None

    try:
        with open(json_file, "r") as f:
            data = json.load(f)

        # Extract model info
        model_info = data.get("model", {})
        provider = model_info.get("provider")
        model_id = model_info.get("model_id")
        json_display_name = model_info.get("display_name")

        # Extract prompt_id
        prompt_id = data.get("prompt_id")

        if not prompt_id or not provider or not model_id:
            print(
                f"  ⚠️  Skipping {json_file.name}: Missing prompt_id, provider, or model_id"
            )
            return None

        # Determine which display_name to use
        if use_current_config and config_mapping:
            key = (provider, model_id)
            if key in config_mapping:
                display_name = config_mapping[key]
                print(
                    f"  📝 Using current config display_name: {display_name}"
                )
            else:
                print(
                    f"  ⚠️  Model {provider}/{model_id} not found in current config, using JSON display_name"
                )
                display_name = json_display_name
        else:
            display_name = json_display_name

        if not display_name:
            print(
                f"  ⚠️  Skipping {json_file.name}: No display_name available"
            )
            return None

        # Generate new filename
        sanitized_name = sanitize_display_name(display_name)
        new_filename = f"{prompt_id}_{sanitized_name}.json"

        return new_filename

    except json.JSONDecodeError:
        print(f"  ❌ Error: {json_file.name} is not valid JSON")
        return None
    except Exception as e:
        print(f"  ❌ Error processing {json_file.name}: {e}")
        return None


def migrate_run_folder(
    run_folder: str, dry_run: bool = False, use_current: bool = False
):
    """
    Migrate all JSON files in a run folder to use display_name in filenames.

    Args:
        run_folder: Path to the run folder
        dry_run: If True, only show what would be done
        use_current: If True, use display_names from current models.yaml
    """
    run_path = Path(run_folder)

    if not run_path.exists():
        print(f"❌ Error: Run folder does not exist: {run_folder}")
        return

    if not run_path.is_dir():
        print(f"❌ Error: Path is not a directory: {run_folder}")
        return

    print(f"\n{'=' * 80}")
    print("Migration Script for Run Folder")
    print(f"{'=' * 80}")
    print(f"Run folder: {run_folder}")
    print(
        f"Mode: {'DRY RUN (no changes will be made)' if dry_run else 'LIVE (files will be renamed)'}"
    )
    print(
        f"Display names: {'Current config (models.yaml)' if use_current else 'From JSON files'}"
    )
    print(f"{'=' * 80}\n")

    # Load current config if needed
    config_mapping = None
    if use_current:
        config_mapping = load_current_model_config()
        print(
            f"✓ Loaded {len(config_mapping)} models from config/models.yaml\n"
        )

    # Find all JSON files
    json_files = list(run_path.glob("*.json"))

    if not json_files:
        print("⚠️  No JSON files found in the run folder")
        return

    print(f"Found {len(json_files)} JSON files\n")

    # Process each file
    renamed_count = 0
    skipped_count = 0
    error_count = 0

    for json_file in sorted(json_files):
        print(f"Processing: {json_file.name}")

        new_filename = get_new_filename(
            json_file, use_current, config_mapping
        )

        if new_filename is None:
            skipped_count += 1
            continue

        # Check if filename would change
        if json_file.name == new_filename:
            print("  ✓ Already has correct name")
            skipped_count += 1
            continue

        new_path = json_file.parent / new_filename

        # Check if target file already exists
        if new_path.exists():
            print(f"  ⚠️  Target file already exists: {new_filename}")
            print("     Skipping to avoid overwriting")
            error_count += 1
            continue

        print(f"  → Will rename to: {new_filename}")

        if not dry_run:
            try:
                json_file.rename(new_path)
                print("  ✓ Renamed successfully")
                renamed_count += 1
            except Exception as e:
                print(f"  ❌ Error renaming file: {e}")
                error_count += 1
        else:
            renamed_count += 1

        print()

    # Summary
    print(f"\n{'=' * 80}")
    print("Migration Summary")
    print(f"{'=' * 80}")
    print(f"Total files processed: {len(json_files)}")
    print(f"Files renamed: {renamed_count}")
    print(f"Files skipped: {skipped_count}")
    print(f"Errors: {error_count}")

    if dry_run:
        print(
            "\n⚠️  This was a DRY RUN - no files were actually renamed"
        )
        print("Run without --dry-run to perform the actual migration")
    else:
        print("\n✓ Migration completed successfully!")

    print(f"{'=' * 80}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Migrate JSON filenames in run folders to use display_name",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (preview changes)
  python migrate_run_filenames.py results/run_20251105_164834 --dry-run

  # Actually rename files using current config display names
  python migrate_run_filenames.py results/run_20251105_164834 --use-current

  # Rename using display names from JSON files
  python migrate_run_filenames.py results/run_20251105_164834
        """,
    )

    parser.add_argument(
        "run_folder",
        help="Path to the run folder (e.g., results/run_20251105_164834)",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be renamed without actually renaming files",
    )

    parser.add_argument(
        "--use-current",
        action="store_true",
        help="Use current display_names from models.yaml instead of JSON content",
    )

    args = parser.parse_args()

    migrate_run_folder(
        args.run_folder, args.dry_run, args.use_current
    )


if __name__ == "__main__":
    main()
