# Reasoning Effort Configuration

This framework supports controlling the reasoning effort for models that support it (GPT-5 and Gemini 2.5 series).

## Overview

Both OpenAI's GPT-5 models and Google's Gemini 2.5 models include reasoning capabilities that can be controlled to trade off between quality, latency, and cost.

## Configuration

Add the `reasoning_effort` parameter to any model in `config/models.yaml`:

```yaml
- provider: openai
  model_id: gpt-5-nano
  display_name: "GPT-5 Nano"
  supports_structured_output: true
  reasoning_effort: low  # Options: low, medium, high
  pricing:
    input_per_million: 0.043
    output_per_million: 0.35

- provider: gemini
  model_id: gemini-2.5-flash-lite
  display_name: "Gemini 2.5 Flash Lite"
  supports_structured_output: true
  reasoning_effort: low  # Options: low, medium, high, or specific token count
  pricing:
    input_per_million: 0.087
    output_per_million: 0.348
```

## Values

### String Values (All Providers)

- **`low`**: Faster, lower-latency responses with minimal reasoning
- **`medium`**: Balanced reasoning (default if omitted)
- **`high`**: Maximum reasoning for complex tasks

### Provider-Specific Behavior

#### OpenAI GPT-5 Models

The `reasoning_effort` parameter is passed directly to the OpenAI API:

```python
response = client.chat.completions.create(
    model="gpt-5-nano",
    messages=[...],
    reasoning_effort="low"  # low, medium, or high
)
```

**Effect**:
- Controls the length of the chain of thought before responding
- Lower effort = faster responses, lower latency
- Higher effort = more thorough reasoning, potentially better results

#### Google Gemini 2.5 Models

The `reasoning_effort` parameter is **natively supported** through Gemini's OpenAI-compatible endpoint. Our implementation uses the **OpenAI client library** pointed at Gemini's API, providing seamless reasoning_effort support without any SDK mixing or compatibility issues.

**How it works**:
```python
# We use the OpenAI client with Gemini's endpoint
client = OpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# reasoning_effort is natively supported
response = client.chat.completions.create(
    model="gemini-2.5-flash-lite",
    reasoning_effort="low",  # Works directly, no mapping needed!
    ...
)
```

Mapping table ([official values](https://ai.google.dev/gemini-api/docs/openai#python)):

| reasoning_effort | thinking_budget (tokens) |
|-----------------|-------------------------|
| `low`           | 1,024                   |
| `medium`        | 8,192                   |
| `high`          | 24,576                  |
| `none`          | Disabled (not available for 2.5 Pro) |

**Current Status**:
- ✅ Fully functional with current dependencies
- ✅ No SDK upgrade required
- ✅ Works identically to OpenAI GPT-5 models

## SDK Requirements

### OpenAI & Gemini
Both providers use the `openai` package - no additional SDKs needed!

- **OpenAI GPT-5**: Uses standard OpenAI endpoint
- **Gemini 2.5**: Uses Gemini's OpenAI-compatible endpoint

The `reasoning_effort` parameter works identically for both providers.

### Together AI
Uses the `together` package. Does not support `reasoning_effort`.

## Testing

Run the integration test to verify everything is configured correctly:

```bash
poetry run python test_reasoning_effort.py
```

This will verify:
1. Configuration is properly loaded from `models.yaml`
2. All providers accept the `reasoning_effort` parameter
3. Parameters are correctly constructed for API calls
4. Runner integration is working

## Examples

### Optimize for Speed (Low Latency)
```yaml
reasoning_effort: low
```

Use when:
- Speed is critical
- Task is relatively simple
- Cost optimization is important

### Optimize for Quality (High Reasoning)
```yaml
reasoning_effort: high
```

Use when:
- Task requires complex reasoning
- Quality is more important than speed
- Willing to accept higher costs

### Balanced Approach
```yaml
reasoning_effort: medium
```
or simply omit the parameter (default behavior)

## Cost and Performance Implications

### Latency
- `low`: ~20-40% faster responses
- `medium`: Baseline
- `high`: ~50-100% slower responses

### Cost
The reasoning tokens are counted as part of the input/output tokens, so higher reasoning effort will increase costs proportionally.

### Quality
For complex tasks requiring multi-step reasoning, higher effort typically produces:
- More accurate results
- Better structured outputs
- Fewer validation errors

## Best Practices

1. **Start with `low`** for simple, well-defined tasks
2. **Use `medium`** (or omit) for general-purpose workouts
3. **Reserve `high`** for complex progressive workouts with multiple phases
4. **Test both** to find the right balance for your use case
5. **Monitor costs** when using higher reasoning efforts

## Implementation Details: Clean Architecture

### Unified Approach Using OpenAI Client

Our implementation uses a **clean, unified approach** without SDK mixing:

**Both OpenAI and Gemini providers** use the `OpenAI` client library:

```python
# OpenAIProvider
class OpenAIProvider:
    def __init__(self, api_key=None):
        self.client = OpenAI(api_key=api_key)
        # Uses default OpenAI endpoint

# GeminiProvider
class GeminiProvider:
    def __init__(self, api_key=None):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        # Uses Gemini's OpenAI-compatible endpoint
```

### Benefits of This Approach

1. **No SDK Mixing**: Single client library (`openai`) for both providers
2. **Native Support**: `reasoning_effort` works directly, no manual mapping needed
3. **Identical Interface**: Both providers work the same way
4. **No Conflicts**: No overlap between `reasoning_effort` and `thinking_budget` because we only use the OpenAI-compatible endpoint
5. **Works Now**: No SDK upgrades or migrations required

### Parameter Flow

**What you write in config**:
```yaml
reasoning_effort: low
```

**What happens**:
```python
# For both OpenAI and Gemini:
api_params = {"model": model_id, "messages": [...]}
if reasoning_effort is not None:
    api_params["reasoning_effort"] = reasoning_effort  # Added directly

response = client.chat.completions.create(**api_params)
```

The OpenAI client handles everything - no manual mapping, no conflicts!

## Troubleshooting

### Parameter Not Working
Verify the configuration is correct:
```bash
poetry run python test_reasoning_effort.py
```

Check that:
- The parameter is spelled correctly in `models.yaml`
- The value is one of: `low`, `medium`, `high`, or `none`
- The model supports reasoning (GPT-5 or Gemini 2.5 series)
- API key is correctly configured for the provider

### Model Not Found Errors
For Gemini models, ensure you're using the correct model ID format:
- ✅ `gemini-2.5-flash-lite` (correct)
- ✅ `gemini-2.5-flash` (correct)
- ❌ `models/gemini-2.5-flash` (incorrect - don't include "models/" prefix)
