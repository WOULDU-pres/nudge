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


def load_product_brief(product_arg: str | None = None) -> str:
    """제품 정보 로드. 우선순위: CLI 인자 > product.yaml > 빈 문자열.
    
    Args:
        product_arg: --product 인자로 전달된 값.
                     파일 경로(.yaml, .yml, .md, .txt)이면 파일에서 로드.
                     그 외는 텍스트로 직접 사용.
    """
    # 1. CLI 인자가 있으면
    if product_arg:
        product_path = Path(product_arg)
        if product_path.exists() and product_path.suffix in (".yaml", ".yml", ".md", ".txt"):
            with open(product_path, "r", encoding="utf-8") as f:
                if product_path.suffix in (".yaml", ".yml"):
                    data = yaml.safe_load(f)
                    return data.get("product_brief", yaml.dump(data, allow_unicode=True))
                else:
                    return f.read()
        else:
            # 텍스트로 직접 사용
            return product_arg

    # 2. product.yaml fallback
    product_path = OUTPUT_DIR / "config" / "product.yaml"
    if product_path.exists():
        with open(product_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data.get("product_brief", "")
    
    return ""


def parse_args():
    """커맨드라인 인자 파싱."""
    import argparse
    parser = argparse.ArgumentParser(description="Ralphthon RALPH Loop 1회 실행")
    parser.add_argument("--product", type=str, default=None,
                       help="제품 정보. 파일 경로(.yaml/.md/.txt) 또는 텍스트 직접 입력")
    parser.add_argument("--dry-run", action="store_true",
                       help="LLM 호출 없이 구조만 확인")
    return parser.parse_args()


async def main():
    args = parse_args()
    setup_logging()
    logger = logging.getLogger("run_simulation")

    settings = get_settings()
    logger.info(f"Ralphthon Simulation — mode={settings.RALPHTHON_MODE}, "
                f"provider={settings.RALPHTHON_PROVIDER}, "
                f"cheap={settings.RALPHTHON_MODEL_CHEAP}, "
                f"expensive={settings.RALPHTHON_MODEL_EXPENSIVE}")

    # Dry run check
    if args.dry_run:
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
    product_brief = load_product_brief(args.product)
    
    if not product_brief.strip():
        logger.error("제품 정보가 없습니다. --product <파일경로 또는 텍스트> 로 지정하거나 config/product.yaml을 작성하세요.")
        sys.exit(1)
    
    logger.info(f"Product: {product_brief[:100]}...")

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
