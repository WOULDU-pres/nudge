"""Practical FastAPI wrapper for the restored acpx/Codex-backed v2 loop."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field

from config.settings import settings
from src.llm import call_via_acpx
from src.ralph.loop_v2 import run_ralph_loop_v2

app = FastAPI(title='NUDGE Ralphthon v2 API', version='2.0')


class RunV2Request(BaseModel):
    iterations: int = Field(default=1, ge=1, le=10)
    personas_count: int = Field(default=2, ge=1, le=20)
    max_turns: int = Field(default=3, ge=1, le=10)
    product_path: str = Field(default='config/product.yaml')
    run_id: Optional[str] = None


class AcpxPromptRequest(BaseModel):
    prompt: str
    system: str = ''
    model: str = ''


@app.get('/health')
async def health() -> dict[str, Any]:
    return {
        'ok': True,
        'mode': 'ralph-v2-acpx',
        'backend': settings.LLM_BACKEND,
        'acpx_agent': settings.ACPX_AGENT,
    }


@app.get('/config')
async def config_summary() -> dict[str, Any]:
    return {
        'backend': settings.LLM_BACKEND,
        'provider': settings.provider,
        'acpx_agent': settings.ACPX_AGENT,
        'acpx_model': settings.acpx_model,
        'acpx_timeout': settings.ACPX_TIMEOUT,
        'mode': settings.RALPHTHON_MODE,
        'strategies_per_run': settings.STRATEGIES_PER_RUN,
        'max_turns': settings.MAX_TURNS,
        'max_concurrent': settings.MAX_CONCURRENT,
        'personas_dir': str(settings.personas_dir),
        'prompts_dir': str(settings.prompts_dir),
        'harness_dir': str(settings.harness_dir),
    }


@app.get('/run/v2/defaults')
async def run_defaults() -> dict[str, Any]:
    return RunV2Request().model_dump()


@app.post('/acpx/ping')
async def acpx_ping(req: AcpxPromptRequest) -> dict[str, Any]:
    response = await call_via_acpx(prompt=req.prompt, system=req.system, model=req.model)
    return {
        'backend': 'acpx',
        'agent': settings.ACPX_AGENT,
        'response': response,
    }


@app.post('/run/v2')
async def run_v2(req: RunV2Request) -> dict[str, Any]:
    return await run_ralph_loop_v2(
        iterations=req.iterations,
        personas_count=req.personas_count,
        max_turns=req.max_turns,
        product_path=req.product_path,
        run_id=req.run_id,
    )
