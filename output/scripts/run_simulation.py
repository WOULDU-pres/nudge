"""Run a single RALPH simulation cycle.

Usage:
    python scripts/run_simulation.py [--product config/product.yaml]
    python scripts/run_simulation.py --dry-run
"""
import asyncio
import argparse
import json
import logging
import sys
import os
from pathlib import Path

# Add output directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import yaml


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler()],
    )


def load_product_brief(path: str) -> str:
    """Load product information from YAML or text file."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Product file not found: {path}")

    content = p.read_text(encoding="utf-8")

    if p.suffix in (".yaml", ".yml"):
        data = yaml.safe_load(content)
        product = data.get("product", data)
        lines = []
        lines.append(f"제품명: {product.get('name', '알 수 없음')}")
        lines.append(f"카테고리: {product.get('category', '')}")
        lines.append(f"가격: {product.get('price', '')}")
        lines.append(f"대상: {product.get('target', '')}")
        if product.get("key_benefits"):
            lines.append("핵심 혜택:")
            for b in product["key_benefits"]:
                lines.append(f"  - {b}")
        if product.get("differentiators"):
            lines.append("차별점:")
            for d in product["differentiators"]:
                lines.append(f"  - {d}")
        if product.get("common_objections"):
            lines.append("예상 반론:")
            for o in product["common_objections"]:
                lines.append(f"  - {o}")
        return "\n".join(lines)
    else:
        return content


async def main():
    parser = argparse.ArgumentParser(description="Run RALPH simulation")
    parser.add_argument("--product", default="config/product.yaml", help="Product info file")
    parser.add_argument("--dry-run", action="store_true", help="Check structure only")
    args = parser.parse_args()

    setup_logging()

    if args.dry_run:
        print("--- Dry Run: Checking imports ---")
        from src.ralph.loop import run_ralph_loop
        from src.agents.sales_agent import SalesAgent
        from src.agents.customer_agent import CustomerAgent
        from src.evaluation.evaluator import judge_conversation
        from src.evaluation.aggregator import aggregate_results
        from config.settings import settings
        print(f"Provider: {settings.provider}")
        print(f"Mode: {settings.mode}")
        print(f"Cheap model: {settings.model_cheap}")
        print(f"Expensive model: {settings.model_expensive}")
        print(f"Personas dir: {settings.personas_dir}")
        print(f"Strategies per run: {settings.strategies_per_run}")
        print("--- Dry Run: All imports OK ---")
        return

    from config.settings import settings
    from src.ralph.loop import run_ralph_loop

    # Load product brief
    product_brief = load_product_brief(args.product)
    print(f"Product loaded: {args.product}")

    # Run RALPH loop
    result = await run_ralph_loop(
        product_brief=product_brief,
        persona_count=settings.persona_count,
        num_strategies=settings.strategies_per_run,
        max_round_trips=settings.conversation_turns,
        max_concurrent=settings.max_concurrent,
    )

    print(f"\nRun ID: {result['run_id']}")
    print(f"Strategies: {len(result['strategies'])}")
    print(f"Evaluations: {len(result['evaluations'])}")


if __name__ == "__main__":
    asyncio.run(main())
