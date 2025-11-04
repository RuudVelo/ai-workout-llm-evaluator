"""
Model provider implementations for OpenAI, Gemini, and Together AI.
"""

import time
from typing import Any, Optional
import os
from dotenv import load_dotenv

from openai import OpenAI
import google.generativeai as genai
from together import Together

from system_prompt import (
    build_system_prompt_generate,
    WORKOUT_JSON_SCHEMA,
    GEMINI_SCHEMA,
)

# Load environment variables from .env file
load_dotenv()


class ModelResponse:
    """Standardized response from any model provider."""

    def __init__(
        self,
        content: str,
        input_tokens: int,
        output_tokens: int,
        latency_ms: int,
        cost: float,
        raw_response: Any = None,
    ):
        self.content = content
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.total_tokens = input_tokens + output_tokens
        self.latency_ms = latency_ms
        self.cost = cost
        self.raw_response = raw_response


class OpenAIProvider:
    """OpenAI API provider with structured output support."""

    def __init__(self, api_key: Optional[str] = None):
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

    def generate(
        self,
        model_id: str,
        user_prompt: str,
        ftp: int,
        input_price_per_million: float,
        output_price_per_million: float,
    ) -> ModelResponse:
        """Generate workout using OpenAI API with structured output."""
        system_prompt = build_system_prompt_generate(ftp)

        start_time = time.time()

        response = self.client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": WORKOUT_JSON_SCHEMA,
            },
        )

        latency_ms = int((time.time() - start_time) * 1000)

        # Extract token usage
        usage = response.usage
        input_tokens = usage.prompt_tokens
        output_tokens = usage.completion_tokens

        # Calculate cost
        cost = (input_tokens / 1_000_000 * input_price_per_million) + (
            output_tokens / 1_000_000 * output_price_per_million
        )

        content = response.choices[0].message.content

        return ModelResponse(
            content=content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            cost=cost,
            raw_response=response,
        )


class GeminiProvider:
    """Google Gemini API provider."""

    def __init__(self, api_key: Optional[str] = None):
        genai.configure(api_key=api_key or os.getenv("GEMINI_API_KEY"))

    def generate(
        self,
        model_id: str,
        user_prompt: str,
        ftp: int,
        input_price_per_million: float,
        output_price_per_million: float,
    ) -> ModelResponse:
        """Generate workout using Gemini API."""
        system_prompt = build_system_prompt_generate(ftp)

        model = genai.GenerativeModel(
            model_id,
            system_instruction=system_prompt,
            generation_config={
                "response_mime_type": "application/json",
                "response_schema": GEMINI_SCHEMA,
            },
        )

        start_time = time.time()
        response = model.generate_content(user_prompt)
        latency_ms = int((time.time() - start_time) * 1000)

        # Extract token usage
        input_tokens = response.usage_metadata.prompt_token_count
        output_tokens = response.usage_metadata.candidates_token_count

        # Calculate cost
        cost = (input_tokens / 1_000_000 * input_price_per_million) + (
            output_tokens / 1_000_000 * output_price_per_million
        )

        content = response.text

        return ModelResponse(
            content=content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            cost=cost,
            raw_response=response,
        )


class TogetherProvider:
    """Together AI provider for open-source models."""

    def __init__(self, api_key: Optional[str] = None):
        self.client = Together(api_key=api_key or os.getenv("TOGETHER_API_KEY"))

    def generate(
        self,
        model_id: str,
        user_prompt: str,
        ftp: int,
        input_price_per_million: float,
        output_price_per_million: float,
    ) -> ModelResponse:
        """Generate workout using Together AI API."""
        system_prompt = build_system_prompt_generate(ftp)

        start_time = time.time()

        response = self.client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={
                "type": "json_object",
                # Together AI doesn't support strict schema like OpenAI
                # but we can request JSON format
            },
        )

        latency_ms = int((time.time() - start_time) * 1000)

        # Extract token usage
        usage = response.usage
        input_tokens = usage.prompt_tokens
        output_tokens = usage.completion_tokens

        # Calculate cost
        cost = (input_tokens / 1_000_000 * input_price_per_million) + (
            output_tokens / 1_000_000 * output_price_per_million
        )

        content = response.choices[0].message.content

        return ModelResponse(
            content=content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            cost=cost,
            raw_response=response,
        )


def get_provider(provider_name: str):
    """Factory function to get the appropriate provider."""
    providers = {
        "openai": OpenAIProvider,
        "gemini": GeminiProvider,
        "together": TogetherProvider,
    }

    if provider_name not in providers:
        raise ValueError(f"Unknown provider: {provider_name}")

    return providers[provider_name]()
