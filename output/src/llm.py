"""Multi-provider LLM client with retry, rate limiting, and dual-key round-robin."""
import asyncio
import json
import random
import re
import logging
from typing import Optional

from google import genai
from google.genai import types as genai_types

logger = logging.getLogger(__name__)

# Global state
_clients: list = []
_client_idx: int = 0
_semaphore: Optional[asyncio.Semaphore] = None
_rate_delay: float = 0.05
_lock = asyncio.Lock() if hasattr(asyncio, 'Lock') else None


def _init_clients():
    """Initialize genai clients from all available API keys."""
    global _clients, _rate_delay
    if _clients:
        return
    from config.settings import settings
    _rate_delay = settings.rate_limit_delay
    for key in settings.api_keys:
        _clients.append(genai.Client(api_key=key))
    if not _clients:
        raise ValueError("No GEMINI_API_KEY configured")


def _get_client() -> genai.Client:
    """Round-robin client selection for rate limit distribution."""
    global _client_idx
    _init_clients()
    client = _clients[_client_idx % len(_clients)]
    _client_idx += 1
    return client


def _get_semaphore() -> asyncio.Semaphore:
    global _semaphore
    if _semaphore is None:
        from config.settings import settings
        _semaphore = asyncio.Semaphore(settings.max_concurrent)
    return _semaphore


def extract_json(text: str) -> dict | list:
    """Extract JSON from LLM response (handles ```json blocks, thinking tags, etc)."""
    text = text.strip()

    # Strip thinking tags if present (Gemini 2.5 thinking models)
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

    # Direct parse
    if text.startswith(("{", "[")):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

    # ```json ... ``` block (greedy to capture full content)
    m = re.search(r"```(?:json)?\s*\n?(.*?)```", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Try all ```json blocks (there may be multiple)
    blocks = re.findall(r"```(?:json)?\s*\n?(.*?)```", text, re.DOTALL)
    for block in blocks:
        try:
            return json.loads(block.strip())
        except json.JSONDecodeError:
            continue

    # Find first JSON object or array using bracket matching
    for ch, end_ch in [("{", "}"), ("[", "]")]:
        start = text.find(ch)
        if start != -1:
            # Try from start, find matching bracket by counting nesting
            depth = 0
            in_string = False
            escape = False
            for i in range(start, len(text)):
                c = text[i]
                if escape:
                    escape = False
                    continue
                if c == '\\' and in_string:
                    escape = True
                    continue
                if c == '"' and not escape:
                    in_string = not in_string
                    continue
                if not in_string:
                    if c == ch:
                        depth += 1
                    elif c == end_ch:
                        depth -= 1
                        if depth == 0:
                            try:
                                return json.loads(text[start:i + 1])
                            except json.JSONDecodeError:
                                break

    # Last resort: try rfind approach
    for ch, end_ch in [("{", "}"), ("[", "]")]:
        start = text.find(ch)
        if start != -1:
            end = text.rfind(end_ch)
            if end > start:
                try:
                    return json.loads(text[start:end + 1])
                except json.JSONDecodeError:
                    pass

    raise ValueError(f"Cannot extract JSON from response: {text[:300]}...")


async def call_llm(
    system_prompt: str,
    user_message: str,
    model: str = None,
    temperature: float = 0.7,
    max_tokens: int = 4096,
    expect_json: bool = False,
) -> str:
    """Call Gemini LLM with retry and rate limiting."""
    from config.settings import settings

    if model is None:
        model = settings.model_cheap

    sem = _get_semaphore()

    for attempt in range(settings.max_retries + 1):
        async with sem:
            await asyncio.sleep(_rate_delay)
            try:
                client = _get_client()
                config_dict = {
                    "system_instruction": system_prompt,
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                }
                # Disable thinking for models that support it
                # to avoid contaminated output
                if "2.5" in model:
                    config_dict["thinking_config"] = genai_types.ThinkingConfig(
                        thinking_budget=0,
                    )
                response = await asyncio.to_thread(
                    client.models.generate_content,
                    model=model,
                    contents=[
                        genai_types.Content(
                            role="user",
                            parts=[genai_types.Part(text=user_message)]
                        )
                    ],
                    config=genai_types.GenerateContentConfig(**config_dict),
                )

                text = response.text
                if not text:
                    raise ValueError("Empty response from LLM")

                if expect_json:
                    parsed = extract_json(text)
                    return json.dumps(parsed, ensure_ascii=False)

                return text

            except Exception as e:
                err_str = str(e).lower()
                # Fatal errors — don't retry
                if any(x in err_str for x in ["401", "403", "404", "invalid api key", "permission", "not found"]):
                    raise

                if attempt < settings.max_retries:
                    delay = settings.retry_base_delay * (2 ** attempt) + random.uniform(0, 0.5)
                    logger.warning(f"LLM call failed (attempt {attempt+1}/{settings.max_retries}), retrying in {delay:.1f}s: {e}")
                    await asyncio.sleep(delay)
                else:
                    raise


async def call_llm_cheap(system_prompt: str, user_message: str, **kwargs) -> str:
    """Call cheap model (for Act stage conversations)."""
    from config.settings import settings
    return await call_llm(system_prompt, user_message, model=settings.model_cheap, **kwargs)


async def call_llm_expensive(system_prompt: str, user_message: str, **kwargs) -> str:
    """Call expensive model (for H/E/R/L stages)."""
    from config.settings import settings
    return await call_llm(system_prompt, user_message, model=settings.model_expensive, **kwargs)
