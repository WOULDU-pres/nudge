"""Minimal FastAPI wrapper for the restored acpx/Codex-backed v2 loop."""

from __future__ import annotations

from fastapi import FastAPI

from src.ralph.loop_v2 import run_ralph_loop_v2

app = FastAPI(title='NUDGE Ralphthon v2 API')


@app.get('/health')
async def health() -> dict:
    return {'ok': True, 'mode': 'ralph-v2-acpx'}


@app.post('/run/v2')
async def run_v2(iterations: int = 1, personas_count: int = 2, max_turns: int = 3) -> dict:
    return await run_ralph_loop_v2(
        iterations=iterations,
        personas_count=personas_count,
        max_turns=max_turns,
    )
