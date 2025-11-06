# Complete Migration Guide

This guide explains how to migrate old run folders to work with the new display name system.

## Two Migration Scripts

### 1. `migrate_run_filenames.py` - Updates Filenames

**What it does:** Renames JSON files to include the display_name

**Example:**
```
Before: ascending_descending_pyramid_gemini-2.5-flash.json
After:  ascending_descending_pyramid_Gemini_2.5_Flash_low_reas.json
```

**When to use:** When you have old run folders with model_id-based filenames

**Usage:**
```bash
# Preview changes
poetry run python migrate_run_filenames.py results/run_20251105_164834 --dry-run --use-current

# Actually rename files
poetry run python migrate_run_filenames.py results/run_20251105_164834 --use-current
```

### 2. `update_json_display_names.py` - Updates JSON Content

**What it does:** Updates the `display_name` field inside JSON files to match current `models.yaml`

**Example:**
```json
Before: {"model": {"display_name": "Gemini 2.5 Flash"}}
After:  {"model": {"display_name": "Gemini 2.5 Flash low reas"}}
```

**When to use:** When you want the visualizer to show current display names instead of historical names

**Usage:**
```bash
# Preview changes
poetry run python update_json_display_names.py results/run_20251105_164834 --dry-run

# Actually update JSON files
poetry run python update_json_display_names.py results/run_20251105_164834
```

## Complete Migration Workflow

### Scenario 1: Old Run Folder (Pre-72ca4cc)

If you have a run folder from before commit 72ca4cc (filenames use model_id):

```bash
# Step 1: Update filenames to include display_name
poetry run python migrate_run_filenames.py results/run_20251105_164834 --use-current

# Step 2 (optional): Update JSON content to show current display names
poetry run python update_json_display_names.py results/run_20251105_164834
```

**Result:**
- ✅ Filenames now include display_name (allows multiple configs of same model)
- ✅ JSON content shows current display names in visualizer
- ✅ All models appear in visualizer dropdown

### Scenario 2: Recent Run Folder (Post-72ca4cc)

If you have a recent run folder (filenames already use display_name) but want to update the display names shown in the visualizer:

```bash
# Only update JSON content
poetry run python update_json_display_names.py results/run_20251105_164834
```

**Result:**
- ✅ Filenames stay the same
- ✅ JSON content shows current display names in visualizer

## Understanding the Difference

### Filenames vs JSON Content

After running both scripts on `results/run_20251105_164834`:

**Filename:**
```
ascending_descending_pyramid_Gemini_2.5_Flash_low_reas.json
```

**JSON Content Before `update_json_display_names.py`:**
```json
{
  "model": {
    "provider": "gemini",
    "model_id": "gemini-2.5-flash",
    "display_name": "Gemini 2.5 Flash"  // Original historical name
  }
}
```

**JSON Content After `update_json_display_names.py`:**
```json
{
  "model": {
    "provider": "gemini",
    "model_id": "gemini-2.5-flash",
    "display_name": "Gemini 2.5 Flash low reas"  // Current name from models.yaml
  }
}
```

**What the Visualizer Shows:**
- The visualizer reads the `display_name` from JSON content
- If you run `update_json_display_names.py`, you'll see current names
- If you don't, you'll see historical names (what they were called when generated)

## Decision Matrix

### Should I update JSON content?

| Situation | Recommendation | Reason |
|-----------|---------------|---------|
| Want to see current model names in visualizer | ✅ Yes | Shows "Gemini 2.5 Flash low reas" |
| Want to preserve historical context | ❌ No | Shows "Gemini 2.5 Flash" (what it was called) |
| Sharing results with others | ✅ Yes | Others see your current naming convention |
| Archival/record keeping | ❌ No | Preserves exact names from time of generation |

## Examples

### Example 1: Full Migration with Current Names

```bash
# Migrate old run folder to current display names
cd /path/to/project

# Step 1: Rename files (dry run first)
poetry run python migrate_run_filenames.py results/run_20251105_164834 --dry-run --use-current

# Step 2: Actually rename files
poetry run python migrate_run_filenames.py results/run_20251105_164834 --use-current

# Step 3: Update JSON content (dry run first)
poetry run python update_json_display_names.py results/run_20251105_164834 --dry-run

# Step 4: Actually update JSON content
poetry run python update_json_display_names.py results/run_20251105_164834
```

### Example 2: Preserve Historical Names

```bash
# Only fix filenames, keep historical display names in JSON
poetry run python migrate_run_filenames.py results/run_20251105_164834 --use-current

# Don't run update_json_display_names.py
```

### Example 3: Update Just Display Names

```bash
# For a recent run that already has correct filenames
poetry run python update_json_display_names.py results/run_20251105_164834
```

## Checking Results

### Before Migration

```bash
# Check what models are detected
poetry run python -c "
from src.visualization_utils import list_available_models_from_run
models = list_available_models_from_run('results/run_20251105_164834')
print(f'Found {len(models)} models')
"
```

If you see only 2 models (GPT-4o Mini and GPT-OSS 20B), you need to migrate filenames.

### After Migration

```bash
# Check display names
poetry run python -c "
from src.visualization_utils import list_available_models_from_run
models = list_available_models_from_run('results/run_20251105_164834')
print('Models in visualizer:')
for model in models:
    print(f'  - {model}')
"
```

Should show all 8 models with either historical or current display names.

## Current Status

### `results/run_20251105_164834`

✅ **Filenames migrated** (320 files renamed with --use-current)
- Files now named with current display names from models.yaml

❌ **JSON content NOT yet updated**
- JSON still contains historical display names
- Visualizer shows: "Gemini 2.5 Flash" (not "Gemini 2.5 Flash low reas")

To update JSON content:
```bash
poetry run python update_json_display_names.py results/run_20251105_164834
```

## Safety Notes

- ✅ Both scripts support `--dry-run` - always use it first!
- ✅ Both scripts validate files before modifying
- ✅ No data loss - only renames or updates display_name field
- ⚠️ Make backups before running if you're concerned
- ⚠️ Can't be automatically undone (would need to restore from backup)

## Integration with Visualizer

The visualizer now:
1. Scans the selected run folder for JSON files
2. Reads `display_name` from each JSON file
3. Shows unique display names in dropdown
4. Matches files by `display_name` when loading workouts

This makes run folders **self-contained and portable** - no dependency on `models.yaml` for visualization!
