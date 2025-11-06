# Migration Notes: Display Name Changes

## Summary

This migration updates the workout evaluation system to support multiple configurations of the same model (e.g., different reasoning_effort or temperature settings) by using display names in filenames and making run folders self-contained.

## Changes Made

### 1. Visualizer Updates ([src/visualization_utils.py](src/visualization_utils.py))

- **Added**: `list_available_models_from_run()` - Reads display names directly from JSON files in the selected run folder
- **Changed**: Visualizer now reads models from the run folder instead of `models.yaml`
- **Benefit**: Run folders are now self-contained and portable - you can copy them anywhere and still visualize the results

### 2. Runner Updates ([src/runner.py](src/runner.py))

- **Already implemented** (commit 72ca4cc): Filenames now use sanitized display_name instead of model_id
- **Format**: `{prompt_id}_{sanitized_display_name}.json`
- **Example**: `threshold_4x8_Gemini_2.5_Flash_low_reas.json`

### 3. Migration Script ([migrate_run_filenames.py](migrate_run_filenames.py))

A new utility script to rename old JSON files from the old format to the new format.

## Workflow

### Your Standard Workflow

1. **Configure models** in [config/models.yaml](config/models.yaml):
   ```yaml
   - provider: gemini
     model_id: gemini-2.5-flash
     display_name: "Gemini 2.5 Flash low reas"  # Unique per config
     reasoning_effort: low
     temperature: 0.0
   ```

2. **Run evaluations**:
   ```bash
   poetry run python src/runner.py
   ```
   - Generates: `results/run_YYYYMMDD_HHMMSS/`
   - Filenames: `{prompt_id}_{display_name}.json`

3. **Visualize results**:
   ```bash
   streamlit run src/workout_visualizer.py
   ```
   - Select the run folder
   - Models appear in dropdown (read from JSON files)
   - Compare against ground truth

### Migrating Old Run Folders

If you have old run folders (before commit 72ca4cc) with model_id-based filenames:

```bash
# Preview changes (dry run)
poetry run python migrate_run_filenames.py results/run_20251105_164834 --dry-run --use-current

# Actually rename files using current config display names
poetry run python migrate_run_filenames.py results/run_20251105_164834 --use-current

# Or use display names from JSON files (preserves historical names)
poetry run python migrate_run_filenames.py results/run_20251105_164834
```

**Options:**
- `--dry-run`: Preview changes without actually renaming
- `--use-current`: Use display names from current `models.yaml` (recommended for consistency)
- Without `--use-current`: Use display names stored in JSON files (preserves historical data)

## Important Notes

### Display Names Must Be Unique

If you run the same model_id with different configurations, use different display names:

❌ **Don't do this** (will overwrite files):
```yaml
- model_id: gemini-2.5-flash
  display_name: "Gemini 2.5 Flash"
  reasoning_effort: low

- model_id: gemini-2.5-flash
  display_name: "Gemini 2.5 Flash"  # Same name!
  reasoning_effort: high
```

✅ **Do this instead**:
```yaml
- model_id: gemini-2.5-flash
  display_name: "Gemini 2.5 Flash low reas"
  reasoning_effort: low

- model_id: gemini-2.5-flash
  display_name: "Gemini 2.5 Flash high reas"
  reasoning_effort: high
```

### Run Folders Are Self-Contained

- Each run folder contains all the data needed for visualization
- Display names are read from JSON files, not from `models.yaml`
- You can copy/move run folders and they'll still work
- You can update `models.yaml` without breaking old visualizations

### Filename vs JSON Content

After migration with `--use-current`:
- **Filename**: Uses CURRENT display name from `models.yaml` (e.g., `prompt_Gemini_2.5_Flash_low_reas.json`)
- **JSON content**: Still contains ORIGINAL display name from when it was generated (e.g., `"Gemini 2.5 Flash"`)
- **Visualizer**: Shows the display name from JSON content (the original name)

This is intentional - it preserves the historical context while organizing files by current naming convention.

## Files Modified

1. [src/visualization_utils.py](src/visualization_utils.py:122-156) - Added `list_available_models_from_run()`
2. [src/workout_visualizer.py](src/workout_visualizer.py:21-33) - Updated to use new function
3. [migrate_run_filenames.py](migrate_run_filenames.py) - New migration script

## Migration Status

- ✅ `results/run_20251105_164834` - Migrated (320 files renamed)
- ✅ Future runs automatically use new format

## Troubleshooting

### Models not showing up in visualizer

**Cause**: Old run folder with model_id-based filenames

**Solution**: Run the migration script:
```bash
poetry run python migrate_run_filenames.py results/run_XXXXXXXX_XXXXXX --use-current
```

### Files being overwritten during evaluation

**Cause**: Two model configs with the same display_name

**Solution**: Make display names unique in `models.yaml`

### Can't find a specific model in old run

**Cause**: Display name in config doesn't match what's in the JSON files

**Solution**: Either:
1. Use the migration script with `--use-current` to update filenames
2. Check what display names are in the JSON files and use those
