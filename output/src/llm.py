"""멀티프로바이더 LLM 클라이언트 — google-genai SDK 기반."""
from __future__ import annotations

import asyncio
import json
import re
import time
import logging

logger = logging.getLogger("ralphthon.llm")

# ── Rate limiting ──────────────────────────────────────────
_RATE_LIMIT_DELAY = 0.25  # seconds — paid tier: Pro 256 RPM, Flash Lite 4K RPM
_rate_lock = asyncio.Lock()
_last_call_time = 0.0


async def call_llm(
    system_prompt: str,
    user_message: str,
    temperature: float = 0.7,
    model_tier: str = "cheap",
    max_retries: int = 3,
) -> str:
    """LLM 호출 — 프로바이더에 따라 분기.

    Args:
        system_prompt: 시스템 프롬프트
        user_message: 사용자 메시지
        temperature: 0.0–1.0
        model_tier: "cheap" 또는 "expensive"
        max_retries: 429/5xx 재시도 횟수

    Returns:
        LLM 응답 텍스트.  실패 시 "[LLM ERROR] ..." 문자열.
    """
    from config.settings import get_settings
    settings = get_settings()

    provider = settings.RALPHTHON_PROVIDER.lower()
    model = (
        settings.RALPHTHON_MODEL_CHEAP
        if model_tier == "cheap"
        else settings.RALPHTHON_MODEL_EXPENSIVE
    )

    global _last_call_time

    for attempt in range(max_retries):
        # ── Global rate-limit gate ──
        async with _rate_lock:
            now = time.monotonic()
            wait = _RATE_LIMIT_DELAY - (now - _last_call_time)
            if wait > 0:
                await asyncio.sleep(wait)
            _last_call_time = time.monotonic()

        try:
            if provider == "gemini":
                result = await _call_gemini(system_prompt, user_message, temperature, model)
            elif provider == "openai":
                result = await _call_openai(system_prompt, user_message, temperature, model)
            else:
                result = f"[LLM ERROR] Unknown provider: {provider}"

            # Check for rate-limit in error string
            if "[LLM ERROR]" in result and "429" in result:
                retry_match = re.search(r"retry in ([\d.]+)s", result)
                delay = float(retry_match.group(1)) + 2 if retry_match else (attempt + 1) * 15
                logger.warning(f"Rate limited (attempt {attempt+1}), waiting {delay:.0f}s")
                await asyncio.sleep(delay)
                continue
            return result

        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                retry_match = re.search(r"retry in ([\d.]+)s", err_str)
                delay = float(retry_match.group(1)) + 2 if retry_match else (attempt + 1) * 15
                logger.warning(f"Rate limited exception (attempt {attempt+1}), waiting {delay:.0f}s")
                await asyncio.sleep(delay)
                continue
            return f"[LLM ERROR] {e}"

    return "[LLM ERROR] max retries exceeded"


# ── Gemini (google-genai SDK) ─────────────────────────────
_gemini_client = None


def _get_gemini_client():
    global _gemini_client
    if _gemini_client is None:
        from google import genai
        from config.settings import get_settings
        _gemini_client = genai.Client(api_key=get_settings().GEMINI_API_KEY)
    return _gemini_client


async def _call_gemini(
    system_prompt: str, user_message: str, temperature: float, model: str
) -> str:
    from google.genai import types

    client = _get_gemini_client()
    try:
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=model,
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=temperature,
            ),
        )
        return response.text or ""
    except Exception as e:
        return f"[LLM ERROR] Gemini: {e}"


# ── OpenAI ────────────────────────────────────────────────
async def _call_openai(
    system_prompt: str, user_message: str, temperature: float, model: str
) -> str:
    try:
        import openai
        from config.settings import get_settings
        client = openai.OpenAI(api_key=get_settings().OPENAI_API_KEY)
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=temperature,
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        return f"[LLM ERROR] OpenAI: {e}"


# ── Helpers ───────────────────────────────────────────────
def extract_json(text: str) -> str | None:
    """LLM 응답에서 ```json ... ``` 블록 또는 [{...}] 를 추출."""
    # Try fenced code block first
    m = re.search(r"```(?:json)?\s*\n?([\s\S]*?)```", text)
    if m:
        return m.group(1).strip()
    # Try raw JSON array
    m = re.search(r"(\[[\s\S]*\])", text)
    if m:
        return m.group(1).strip()
    # Try raw JSON object
    m = re.search(r"(\{[\s\S]*\})", text)
    if m:
        return m.group(1).strip()
    return None


def parse_json_response(text: str) -> dict | list | None:
    """LLM 응답에서 JSON을 추출+파싱."""
    raw = extract_json(text)
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None
