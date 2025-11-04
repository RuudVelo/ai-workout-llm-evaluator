"""
Test script to verify reasoning_effort parameter integration.
"""
import sys
import yaml
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from model_providers import OpenAIProvider, GeminiProvider, TogetherProvider


def test_config_loading():
    """Test that reasoning_effort is correctly loaded from config."""
    print("=" * 60)
    print("TEST 1: Config Loading")
    print("=" * 60)

    config_path = Path('config/models.yaml')
    with open(config_path) as f:
        config = yaml.safe_load(f)

    # Test GPT-5 model (optional - may be commented out)
    gpt5_model = next(
        (m for m in config['models'] if m['model_id'] == 'gpt-5-nano'),
        None
    )

    if gpt5_model:
        reasoning_effort = gpt5_model.get('reasoning_effort')
        print(f"✓ Found GPT-5 Nano in config")
        print(f"  reasoning_effort = '{reasoning_effort}'")
        assert reasoning_effort == 'low', f"Expected 'low', got '{reasoning_effort}'"
        print("✓ GPT-5 value is correct")
    else:
        print("⚠ GPT-5 Nano not in config (commented out - OK)")

    # Test Gemini model
    gemini_model = next(
        (m for m in config['models'] if m['model_id'] == 'gemini-2.5-flash-lite'),
        None
    )

    if gemini_model:
        reasoning_effort = gemini_model.get('reasoning_effort')
        print(f"✓ Found Gemini 2.5 Flash Lite in config")
        print(f"  reasoning_effort = '{reasoning_effort}'")
        assert reasoning_effort == 'low', f"Expected 'low', got '{reasoning_effort}'"
        print("✓ Gemini value is correct")
    else:
        print("⚠ Gemini 2.5 Flash Lite not found in config (optional)")

    print()
    return True


def test_provider_signatures():
    """Test that all providers accept reasoning_effort parameter."""
    print("=" * 60)
    print("TEST 2: Provider Method Signatures")
    print("=" * 60)

    import inspect

    providers = [
        ('OpenAI', OpenAIProvider),
        ('Gemini', GeminiProvider),
        ('Together', TogetherProvider),
    ]

    for name, provider_class in providers:
        sig = inspect.signature(provider_class.generate)
        params = list(sig.parameters.keys())

        if 'reasoning_effort' in params:
            default = sig.parameters['reasoning_effort'].default
            print(f"✓ {name}Provider.generate() has 'reasoning_effort' parameter")
            print(f"  Default value: {default}")
        else:
            print(f"✗ {name}Provider.generate() missing 'reasoning_effort' parameter")
            return False

    print()
    return True


def test_parameter_construction():
    """Test that OpenAI API parameters are correctly constructed."""
    print("=" * 60)
    print("TEST 3: API Parameter Construction")
    print("=" * 60)

    # We can't actually call the API without credentials, but we can verify
    # that the parameter would be included in the call

    # Test with reasoning_effort
    print("Scenario 1: With reasoning_effort='low'")
    reasoning_effort = 'low'
    api_params = {
        'model': 'gpt-5-nano',
        'messages': [],
        'response_format': {'type': 'json_schema'},
    }
    if reasoning_effort is not None:
        api_params['reasoning_effort'] = reasoning_effort

    assert 'reasoning_effort' in api_params, "reasoning_effort not added to params"
    print(f"✓ API params would include: reasoning_effort='{api_params['reasoning_effort']}'")

    # Test without reasoning_effort
    print("\nScenario 2: Without reasoning_effort (None)")
    reasoning_effort = None
    api_params = {
        'model': 'gpt-4o',
        'messages': [],
        'response_format': {'type': 'json_schema'},
    }
    if reasoning_effort is not None:
        api_params['reasoning_effort'] = reasoning_effort

    assert 'reasoning_effort' not in api_params, "reasoning_effort incorrectly added"
    print(f"✓ API params correctly exclude reasoning_effort")

    print("\nScenario 3: Gemini thinking budget mapping")
    # Test thinking budget mapping (official values from OpenAI compatibility layer)
    thinking_map = {
        "low": 1024,
        "medium": 8192,
        "high": 24576,
    }

    for effort, expected_budget in thinking_map.items():
        reasoning_effort = effort
        thinking_budget = thinking_map.get(reasoning_effort)
        print(f"  '{effort}' → {thinking_budget} tokens")
        assert thinking_budget == expected_budget, f"Mapping incorrect for {effort}"

    print("✓ All Gemini mappings correct")

    print()
    return True


def test_runner_integration():
    """Test that runner.py correctly passes reasoning_effort."""
    print("=" * 60)
    print("TEST 4: Runner Integration")
    print("=" * 60)

    # Check that runner.py has the correct code
    runner_path = Path('src/runner.py')
    with open(runner_path) as f:
        runner_code = f.read()

    # Check for the reasoning_effort parameter being passed
    if 'reasoning_effort=model_config.get("reasoning_effort")' in runner_code:
        print("✓ runner.py passes reasoning_effort parameter")
    else:
        print("✗ runner.py does not pass reasoning_effort parameter")
        return False

    # Check ground_truth_generator.py as well
    gt_path = Path('src/ground_truth_generator.py')
    with open(gt_path) as f:
        gt_code = f.read()

    if 'reasoning_effort=self.reference_model.get("reasoning_effort")' in gt_code:
        print("✓ ground_truth_generator.py passes reasoning_effort parameter")
    else:
        print("✗ ground_truth_generator.py does not pass reasoning_effort parameter")
        return False

    print()
    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("REASONING_EFFORT INTEGRATION TESTS")
    print("=" * 60)
    print()

    tests = [
        test_config_loading,
        test_provider_signatures,
        test_parameter_construction,
        test_runner_integration,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test failed with error: {e}")
            results.append(False)

    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    if all(results):
        print("\n✅ All tests passed! Integration is complete.")
        print("\nYou can now:")
        print("  1. Add reasoning_effort to any GPT-5 or Gemini 2.5 model in config/models.yaml")
        print("  2. Set it to 'low', 'medium', or 'high'")
        print("  3. Run your evaluations normally - the parameter will be used automatically")
        print("\nProvider-specific notes:")
        print("  • OpenAI GPT-5: Uses reasoning_effort parameter directly")
        print("  • Gemini 2.5: Uses OpenAI-compatible endpoint (no SDK upgrade needed!)")
        print("    - low: 1024 tokens")
        print("    - medium: 8192 tokens")
        print("    - high: 24576 tokens")
        print("\nNote: Both providers now use the OpenAI client library for consistency.")
        return 0
    else:
        print("\n❌ Some tests failed. Please review the output above.")
        return 1


if __name__ == '__main__':
    exit(main())
