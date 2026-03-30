"""Unified LLM interface with acpx/Codex subprocess backend and optional API fallback."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import random
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import aiohttp
import anthropic
import openai
from google import genai
from google.genai import types as genai_types

from config.settings import settings

logger = logging.getLogger(__name__)

_semaphore: asyncio.Semaphore | None = None
_gemini_clients: list[genai.Client] = []
_gemini_client_idx: int = 0


def _get_semaphore() -> asyncio.Semaphore:
    global _semaphore
    if _semaphore is None:
        _semaphore = asyncio.Semaphore(settings.concurrent)
    return _semaphore


def _init_gemini_clients() -> list[genai.Client]:
    global _gemini_clients
    if not _gemini_clients:
        keys = settings.api_keys
        if not keys:
            raise ValueError('No GEMINI_API_KEY configured')
        _gemini_clients = [genai.Client(api_key=key) for key in keys]
    return _gemini_clients


def _next_gemini_client() -> genai.Client:
    global _gemini_client_idx
    clients = _init_gemini_clients()
    client = clients[_gemini_client_idx % len(clients)]
    _gemini_client_idx += 1
    return client


def _parse_retry_delay(exc: Exception) -> float:
    try:
        err_str = str(exc)
        match = re.search(r'retry in (\d+(?:\.\d+)?)\s*s', err_str, re.IGNORECASE)
        if match:
            return float(match.group(1))
        match = re.search(r'"retryDelay"\s*:\s*"(\d+)s"', err_str)
        if match:
            return float(match.group(1))
    except Exception:
        pass
    return 0.0


def _is_retryable(exc: Exception) -> bool:
    if hasattr(exc, 'code'):
        code = getattr(exc, 'code', 0)
        if code == 429 or (isinstance(code, int) and 500 <= code < 600):
            return True
    if isinstance(exc, openai.RateLimitError):
        return True
    if isinstance(exc, openai.APIStatusError) and exc.status_code >= 500:
        return True
    if isinstance(exc, anthropic.RateLimitError):
        return True
    if isinstance(exc, anthropic.APIStatusError) and exc.status_code >= 500:
        return True
    if isinstance(exc, aiohttp.ClientResponseError):
        return exc.status == 429 or exc.status >= 500
    err_str = str(exc).lower()
    return '429' in err_str or 'rate limit' in err_str or 'resource exhausted' in err_str


def _build_acpx_prompt(prompt: str, system: str = '') -> str:
    if system:
        return f"# System\n{system.strip()}\n\n# User\n{prompt.strip()}\n"
    return prompt.strip() + '\n'


def _parse_acpx_jsonl(stdout: str) -> str:
    chunks: list[str] = []
    fallback_lines: list[str] = []

    for raw_line in stdout.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            fallback_lines.append(raw_line)
            continue

        if obj.get('method') == 'session/update':
            update = obj.get('params', {}).get('update', {})
            if update.get('sessionUpdate') == 'agent_message_chunk':
                content = update.get('content', {})
                if content.get('type') == 'text':
                    chunks.append(content.get('text', ''))

    text = ''.join(chunks).strip()
    if text:
        return text
    if fallback_lines:
        joined = '\n'.join(fallback_lines).strip()
        if joined:
            return joined
    raise ValueError('acpx produced no assistant text')


def _call_acpx_sync(prompt: str, system: str = '', model: str = '') -> str:
    prompt_file: str | None = None
    try:
        fd, prompt_file = tempfile.mkstemp(prefix='ralph-acpx-', suffix='.md')
        os.close(fd)
        Path(prompt_file).write_text(_build_acpx_prompt(prompt, system), encoding='utf-8')

        cmd = [
            'acpx',
            '--format', 'json',
            '--json-strict',
            '--cwd', str(settings.output_dir),
            '--timeout', str(settings.ACPX_TIMEOUT),
        ]
        if settings.ACPX_APPROVE_ALL:
            cmd.append('--approve-all')
        if settings.ACPX_ALLOWED_TOOLS:
            cmd.extend(['--allowed-tools', settings.ACPX_ALLOWED_TOOLS])
        selected_model = model or settings.acpx_model
        if selected_model and selected_model != 'acpx':
            cmd.extend(['--model', selected_model])
        cmd.extend([
            settings.ACPX_AGENT,
            'exec',
            '-f', prompt_file,
        ])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=settings.ACPX_TIMEOUT + 10,
            check=False,
        )
        stdout = result.stdout or ''
        stderr = result.stderr or ''
        text = ''
        try:
            text = _parse_acpx_jsonl(stdout)
        except Exception:
            text = ''
        if result.returncode != 0 and not text:
            raise RuntimeError(f'acpx command failed ({result.returncode}): {stderr or stdout}')
        if not text:
            raise RuntimeError(f'acpx returned empty output. stderr={stderr!r}')
        return text.strip()
    finally:
        if prompt_file:
            try:
                Path(prompt_file).unlink(missing_ok=True)
            except OSError:
                pass


async def call_via_acpx(prompt: str, system: str = '', model: str = '') -> str:
    return await asyncio.to_thread(_call_acpx_sync, prompt, system, model)


async def _call_gemini(prompt: str, system: str, model: str, temperature: float) -> str:
    client = _next_gemini_client()

    def _sync_call() -> str:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=genai_types.GenerateContentConfig(
                system_instruction=system if system else None,
                temperature=temperature,
            ),
        )
        return response.text or ''

    return await asyncio.to_thread(_sync_call)


async def _call_openai(prompt: str, system: str, model: str, temperature: float) -> str:
    client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    messages = []
    if system:
        messages.append({'role': 'system', 'content': system})
    messages.append({'role': 'user', 'content': prompt})
    response = await client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message.content or ''


async def _call_anthropic(prompt: str, system: str, model: str, temperature: float) -> str:
    client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    kwargs: dict[str, Any] = {
        'model': model,
        'max_tokens': 4096,
        'temperature': temperature,
        'messages': [{'role': 'user', 'content': prompt}],
    }
    if system:
        kwargs['system'] = system
    response = await client.messages.create(**kwargs)
    return response.content[0].text


async def _call_ollama(prompt: str, system: str, model: str, temperature: float) -> str:
    url = f"{settings.OLLAMA_BASE_URL}/api/generate"
    payload: dict[str, Any] = {
        'model': model,
        'prompt': prompt,
        'stream': False,
        'options': {'temperature': temperature},
    }
    if system:
        payload['system'] = system
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            resp.raise_for_status()
            data = await resp.json()
            return data.get('response', '')


async def call_llm(
    prompt: str,
    system: str = '',
    model: str = '',
    temperature: float = 0.7,
    provider: str = '',
) -> str:
    backend = (settings.LLM_BACKEND or 'acpx').lower()
    provider = provider or settings.provider
    sem = _get_semaphore()
    async with sem:
        await asyncio.sleep(settings.rate_limit_delay)
        if provider == 'acpx' or backend == 'acpx':
            return await call_via_acpx(prompt=prompt, system=system, model=model)

        model = model or settings.model_cheap
        provider_fn = {
            'gemini': _call_gemini,
            'openai': _call_openai,
            'anthropic': _call_anthropic,
            'ollama': _call_ollama,
        }
        fn = provider_fn.get(provider)
        if fn is None:
            raise ValueError(f'Unknown provider: {provider}')

        max_retries = settings.max_retries
        last_exc = None
        for attempt in range(max_retries + 1):
            try:
                return await fn(prompt, system, model, temperature)
            except Exception as exc:
                last_exc = exc
                if attempt < max_retries and _is_retryable(exc):
                    delay = min(90, max(2, _parse_retry_delay(exc) or (2 ** min(attempt, 5)) + random.uniform(0, 1)))
                    logger.warning('Retry %d/%d for provider=%s model=%s in %.1fs: %s', attempt + 1, max_retries, provider, model, delay, exc)
                    await asyncio.sleep(delay)
                else:
                    raise
        raise RuntimeError(f'LLM call failed after retries: {last_exc}')


def extract_json(text: str) -> Any:
    if not text:
        raise ValueError('Empty text, no JSON to extract')

    raw = text.strip()
    raw = re.sub(r'<think>.*?</think>', '', raw, flags=re.DOTALL).strip()

    if raw.startswith(('```json', '```')):
        blocks = re.findall(r'```(?:json)?\s*(.*?)```', raw, re.DOTALL)
        for block in blocks:
            block = block.strip()
            try:
                return json.loads(block)
            except json.JSONDecodeError:
                continue

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    for open_ch, close_ch in (('{', '}'), ('[', ']')):
        start = raw.find(open_ch)
        if start == -1:
            continue
        depth = 0
        in_string = False
        escape = False
        for idx in range(start, len(raw)):
            ch = raw[idx]
            if escape:
                escape = False
                continue
            if ch == '\\' and in_string:
                escape = True
                continue
            if ch == '"':
                in_string = not in_string
                continue
            if in_string:
                continue
            if ch == open_ch:
                depth += 1
            elif ch == close_ch:
                depth -= 1
                if depth == 0:
                    candidate = raw[start:idx + 1]
                    try:
                        return json.loads(candidate)
                    except json.JSONDecodeError:
                        break

    raise ValueError(f'Could not extract JSON from response: {raw[:400]}')
