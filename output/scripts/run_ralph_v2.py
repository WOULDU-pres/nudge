#!/usr/bin/env python3
"""Run the restored acpx/Codex-backed Ralph loop v2."""

from __future__ import annotations

import argparse
import asyncio
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.dirname(SCRIPT_DIR)
if OUTPUT_DIR not in sys.path:
    sys.path.insert(0, OUTPUT_DIR)
os.chdir(OUTPUT_DIR)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Run Ralph v2 with acpx/Codex backend')
    parser.add_argument('--iterations', type=int, default=3)
    parser.add_argument('--personas-count', type=int, default=3)
    parser.add_argument('--max-turns', type=int, default=4)
    parser.add_argument('--product', default='config/product.yaml')
    parser.add_argument('--dry-run', action='store_true')
    return parser.parse_args()


async def main(args: argparse.Namespace) -> int:
    from config.settings import settings
    from src.ralph.loop_v2 import run_ralph_loop_v2

    if args.dry_run:
        print('--- Dry Run: Ralph v2 / acpx backend ---')
        print(f'LLM_BACKEND: {settings.LLM_BACKEND}')
        print(f'ACPX_AGENT: {settings.ACPX_AGENT}')
        print(f'ACPX_MODEL: {settings.acpx_model}')
        print(f'Output dir: {settings.output_dir}')
        print(f'Harness dir: {settings.harness_dir}')
        print(f'Personas dir: {settings.personas_dir}')
        print(f'Prompts dir: {settings.prompts_dir}')
        return 0

    summary = await run_ralph_loop_v2(
        iterations=args.iterations,
        personas_count=args.personas_count,
        max_turns=args.max_turns,
        product_path=args.product,
    )

    best = summary.get('best_iteration') or {}
    print('=' * 60)
    print('RALPH Loop v2 complete')
    print('=' * 60)
    print(f"Score trend: {summary.get('score_trend', [])}")
    print(f"Purchase trend: {summary.get('purchase_rate_trend', [])}")
    print(f"Total learnings: {summary.get('total_learnings', 0)}")
    print(f"Best iteration: {best.get('iteration')} / {best.get('strategy_id')}")
    print(f"Elapsed: {summary.get('elapsed_sec', 0)}s")
    return 0


if __name__ == '__main__':
    raise SystemExit(asyncio.run(main(parse_args())))
