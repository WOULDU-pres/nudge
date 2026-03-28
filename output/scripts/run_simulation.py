#!/usr/bin/env python3
"""RALPH Loop 1회 실행 스크립트."""
from __future__ import annotations

import asyncio
import json
import logging
import sys
import time
from pathlib import Path

# output/ 디렉토리를 sys.path에 추가
OUTPUT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(OUTPUT_DIR))

from config.settings import get_settings
from src.ralph.loop import run_ralph_loop
import yaml


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(message)s",
        datefmt="%H:%M:%S",
    )


def load_strategy_prompt() -> str:
    """strategy_prompt.md 로드."""
    sp_path = OUTPUT_DIR / "strategy_prompt.md"
    if not sp_path.exists():
        raise FileNotFoundError(f"strategy_prompt.md not found at {sp_path}")
    with open(sp_path, "r", encoding="utf-8") as f:
        return f.read()


def load_product_brief() -> str:
    """product.yaml에서 product_brief 로드."""
    product_path = OUTPUT_DIR / "config" / "product.yaml"
    if product_path.exists():
        with open(product_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data.get("product_brief", "")
    return ""


async def main():
    setup_logging()
    logger = logging.getLogger("run_simulation")

    settings = get_settings()
    logger.info(f"Ralphthon Simulation — mode={settings.RALPHTHON_MODE}, "
                f"provider={settings.RALPHTHON_PROVIDER}, "
                f"cheap={settings.RALPHTHON_MODEL_CHEAP}, "
                f"expensive={settings.RALPHTHON_MODEL_EXPENSIVE}")

    # Dry run check
    if "--dry-run" in sys.argv:
        logger.info("Dry run — checking imports and structure only")
        from src.personas.loader import load_personas
        personas = load_personas(3)
        logger.info(f"  Loaded {len(personas)} personas: {[p['id'] for p in personas]}")
        sp = load_strategy_prompt()
        logger.info(f"  Strategy prompt loaded: {len(sp)} chars")
        print("avg_score: 0.0")
        print("cluster_coverage: 0.0")
        print("best_strategy: dry-run")
        return

    # Load inputs
    strategy_prompt = load_strategy_prompt()
    product_brief = load_product_brief()

    # Generate run_id
    run_id = f"run_{int(time.time())}"
    run_dir = OUTPUT_DIR / "runs" / run_id

    logger.info(f"Run ID: {run_id}")
    logger.info(f"Run dir: {run_dir}")

    # Execute RALPH Loop
    result = await run_ralph_loop(
        strategy_prompt=strategy_prompt,
        product_brief=product_brief,
        run_dir=run_dir,
    )

    summary = result["summary"]

    # ── stdout: grep-parsable output ──
    print(f"avg_score: {summary['avg_score']}")
    print(f"cluster_coverage: {summary['cluster_coverage']}")
    print(f"best_strategy: {summary['best_strategy']}")

    # Extra info
    print(f"elapsed_seconds: {result.get('elapsed_seconds', 0)}")
    print(f"run_id: {run_id}")

    if summary.get("cluster_scores"):
        print(f"cluster_scores: {json.dumps(summary['cluster_scores'], ensure_ascii=False)}")
    if summary.get("outcome_distribution"):
        print(f"outcome_distribution: {json.dumps(summary['outcome_distribution'], ensure_ascii=False)}")
    if summary.get("strategy_scores"):
        print(f"strategy_scores: {json.dumps(summary['strategy_scores'], ensure_ascii=False)}")


if __name__ == "__main__":
    asyncio.run(main())
