"""Async multi-provider LLM client with retry logic and rate limiting."""

import asyncio
import json
import logging
import random
import re
from typing import Any

import os

import aiohttp
import anthropic
import openai
from google import genai
from google.genai import types as genai_types

from config.settings import settings

logger = logging.getLogger(__name__)

# Global semaphore for concurrency control
_semaphore: asyncio.Semaphore | None = None

# Gemini key rotation: use 2 keys round-robin to double rate limit
_gemini_keys: list[str] = []
_gemini_key_idx: int = 0
_gemini_key_lock = None  # initialized lazily in event loop


def _get_gemini_keys() -> list[str]:
    """Initialize Gemini API keys from settings."""
    global _gemini_keys
    if not _gemini_keys:
        keys = []
        k1 = settings.GEMINI_API_KEY
        if k1:
            keys.append(k1)
        k2 = getattr(settings, 'GEMINI_API_KEY_2', '') or os.environ.get('GEMINI_API_KEY_2', '')
        if k2:
            keys.append(k2)
        _gemini_keys = keys if keys else ['']
    return _gemini_keys


def _next_gemini_key() -> str:
    """Round-robin select next Gemini API key."""
    global _gemini_key_idx
    keys = _get_gemini_keys()
    key = keys[_gemini_key_idx % len(keys)]
    _gemini_key_idx += 1
    return key


def _get_semaphore() -> asyncio.Semaphore:
    """Lazy-init semaphore (must be created inside a running event loop)."""
    global _semaphore
    if _semaphore is None:
        _semaphore = asyncio.Semaphore(settings.concurrent)
    return _semaphore


def _parse_retry_delay(exc: Exception) -> float:
    """Extract server-suggested retry delay from error message."""
    try:
        err_str = str(exc)
        # Look for "retry in XX.XXs" pattern
        match = re.search(r'retry in (\d+(?:\.\d+)?)\s*s', err_str, re.IGNORECASE)
        if match:
            return float(match.group(1))
        # Look for retryDelay field
        match = re.search(r'"retryDelay"\s*:\s*"(\d+)s"', err_str)
        if match:
            return float(match.group(1))
    except Exception:
        pass
    return 0.0


def _is_retryable(exc: Exception) -> bool:
    """Check if an exception is retryable (429 or 5xx)."""
    # google-genai errors
    if hasattr(exc, "code"):
        code = getattr(exc, "code", 0)
        if code == 429 or (isinstance(code, int) and 500 <= code < 600):
            return True
    # openai errors
    if isinstance(exc, openai.RateLimitError):
        return True
    if isinstance(exc, openai.APIStatusError) and exc.status_code >= 500:
        return True
    # anthropic errors
    if isinstance(exc, anthropic.RateLimitError):
        return True
    if isinstance(exc, anthropic.APIStatusError) and exc.status_code >= 500:
        return True
    # aiohttp errors
    if isinstance(exc, aiohttp.ClientResponseError):
        if exc.status == 429 or exc.status >= 500:
            return True
    # Generic fallback
    err_str = str(exc).lower()
    if "429" in err_str or "rate limit" in err_str or "resource exhausted" in err_str:
        return True
    return False


async def _call_gemini(prompt: str, system: str, model: str, temperature: float) -> str:
    """Call Gemini via google-genai SDK (synchronous, wrapped with to_thread)."""
    api_key = _next_gemini_key()
    client = genai.Client(api_key=api_key)

    def _sync_call() -> str:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=genai_types.GenerateContentConfig(
                system_instruction=system if system else None,
                temperature=temperature,
            ),
        )
        return response.text

    return await asyncio.to_thread(_sync_call)

async def _call_openai(prompt: str, system: str, model: str, temperature: float) -> str:
    """Call OpenAI via async client."""
    client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    response = await client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message.content or ""


async def _call_anthropic(prompt: str, system: str, model: str, temperature: float) -> str:
    """Call Anthropic via async client."""
    client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    kwargs: dict[str, Any] = {
        "model": model,
        "max_tokens": 4096,
        "temperature": temperature,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        kwargs["system"] = system
    response = await client.messages.create(**kwargs)
    return response.content[0].text


async def _call_ollama(prompt: str, system: str, model: str, temperature: float) -> str:
    """Call Ollama via REST API."""
    url = f"{settings.OLLAMA_BASE_URL}/api/generate"
    payload: dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature},
    }
    if system:
        payload["system"] = system

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            resp.raise_for_status()
            data = await resp.json()
            return data.get("response", "")


async def call_llm(
    prompt: str,
    system: str = "",
    model: str = "",
    temperature: float = 0.7,
    provider: str = "",
) -> str:
    """Call an LLM with retry logic, rate limiting, and concurrency control.

    Args:
        prompt: The user prompt.
        system: Optional system instruction.
        model: Model name override (uses settings default if empty).
        temperature: Sampling temperature.
        provider: Provider override (uses settings default if empty).

    Returns:
        The LLM response text.
    """
    provider = provider or settings.RALPHTHON_PROVIDER
    model = model or settings.RALPHTHON_MODEL

    provider_fn = {
        "gemini": _call_gemini,
        "openai": _call_openai,
        "anthropic": _call_anthropic,
        "ollama": _call_ollama,
    }

    fn = provider_fn.get(provider)
    if fn is None:
        raise ValueError(f"Unknown provider: {provider}. Choose from: {list(provider_fn.keys())}")

    sem = _get_semaphore()

    max_retries = 15  # generous retries for rate-limited free tier
    last_exc = None
    for attempt in range(max_retries + 1):
        should_retry = False
        async with sem:
            await asyncio.sleep(settings.RATE_LIMIT_DELAY)
            try:
                result = await fn(prompt, system, model, temperature)
                return result
            except Exception as exc:
                last_exc = exc
                if attempt < max_retries and _is_retryable(exc):
                    should_retry = True
                else:
                    logger.error("LLM call failed (%s, model=%s): %s", provider, model, str(exc)[:200])
                    raise
        # Retry OUTSIDE semaphore so other tasks can proceed during our backoff
        if should_retry:
            server_delay = _parse_retry_delay(last_exc)
            base_delay = max(5, (2 ** min(attempt, 5)) + random.uniform(1, 3))
            delay = min(90, max(base_delay, server_delay))
            if attempt % 3 == 0:
                logger.warning(
                    "Retry %d/%d for %s (model=%s): rate limited — waiting %.0fs",
                    attempt + 1, max_retries, provider, model, delay,
                )
            await asyncio.sleep(delay)

    raise RuntimeError("Exhausted all retries")


def extract_json(text: str) -> Any:
    """Extract JSON object or array from LLM response text.

    Looks for the first JSON block (object or array) in the text,
    handling cases where LLM wraps JSON in markdown code fences.

    Args:
        text: Raw LLM response text.

    Returns:
        Parsed JSON (dict or list).

    Raises:
        ValueError: If no valid JSON found in text.
    """
    if not text:
        raise ValueError("Empty text, no JSON to extract")

    # Try to parse the whole text first
    text_stripped = text.strip()
    if text_stripped.startswith(("{", "[")):
        try:
            return json.loads(text_stripped)
        except json.JSONDecodeError:
            pass

    # Try to find JSON in code fences
    fence_pattern = re.compile(r"```(?:json)?\s*\n?([\s\S]*?)```", re.MULTILINE)
    for match in fence_pattern.finditer(text):
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            continue

    # Try to find JSON object or array with regex
    # Match outermost { ... } or [ ... ]
    for pattern in [
        re.compile(r"\{[\s\S]*\}", re.MULTILINE),
        re.compile(r"\[[\s\S]*\]", re.MULTILINE),
    ]:
        match = pattern.search(text)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                continue

    raise ValueError(f"No valid JSON found in text: {text[:200]}...")
