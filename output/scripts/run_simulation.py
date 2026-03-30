#!/usr/bin/env python3
"""Entry point for running the merged Ralphthon simulation loop.

Usage:
    cd output && python scripts/run_simulation.py
    cd output && python scripts/run_simulation.py --dry-run
    cd output && python scripts/run_simulation.py --product config/product.yaml

Output (grep-friendly):
    avg_score:XX.X
    cluster_coverage:XX.X
    best_strategy:strategy-xxx
"""

import argparse
import asyncio
import logging
import os
import sys

# Add output/ directory to sys.path so imports work
script_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.dirname(script_dir)
if output_dir not in sys.path:
    sys.path.insert(0, output_dir)

# Ensure .env and relative paths resolve from output/
os.chdir(output_dir)


def setup_logging() -> None:
    """Configure logging for the simulation."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("google").setLevel(logging.WARNING)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Ralphthon simulation loop")
    parser.add_argument(
        "--product",
        default="config/product.yaml",
        help="Product YAML path relative to output/",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Import-check only; do not execute the full simulation loop",
    )
    return parser.parse_args()


async def main(args: argparse.Namespace):
    """Run the Ralphthon simulation loop."""
    from config.settings import settings
    from src.ralph.loop import run_ralph_loop

    if args.dry_run:
        print("--- Dry Run: Checking imports ---")
        from src.agents.sales_agent import SalesAgent  # noqa: F401
        from src.agents.customer_agent import CustomerAgent  # noqa: F401
        from src.evaluation.evaluator import evaluate_conversation  # noqa: F401
        from src.evaluation.aggregator import aggregate_results  # noqa: F401
        print(f"Provider: {settings.RALPHTHON_PROVIDER}")
        print(f"Model: {settings.RALPHTHON_MODEL}")
        print(f"Cheap model: {settings.cheap_model}")
        print(f"Expensive model: {settings.expensive_model}")
        print(f"Mode: {settings.RALPHTHON_MODE} ({settings.persona_count} personas)")
        print(f"Harness dir: {settings.harness_dir}")
        print(f"Personas dir: {settings.personas_dir}")
        print(f"Prompts dir: {settings.prompts_dir}")
        print("--- Dry Run: All imports OK ---")
        return None

    print("=== Ralphthon Simulation ===")
    print(f"Provider: {settings.RALPHTHON_PROVIDER}")
    print(f"Model: {settings.RALPHTHON_MODEL}")
    print(f"Expensive model: {settings.expensive_model}")
    print(f"Cheap model: {settings.cheap_model}")
    print(f"Mode: {settings.RALPHTHON_MODE} ({settings.persona_count} personas)")
    print(f"Strategies per run: {settings.STRATEGIES_PER_RUN}")
    print(f"Max turns: {settings.MAX_TURNS}")
    print(f"Max concurrent: {settings.MAX_CONCURRENT}")
    print(f"Rate limit delay: {settings.RATE_LIMIT_DELAY}s")
    print(f"Product path: {args.product}")
    print()

    summary = await run_ralph_loop(product_path=args.product)
    return summary


if __name__ == "__main__":
    setup_logging()
    cli_args = parse_args()
    try:
        result = asyncio.run(main(cli_args))
        sys.exit(0)
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        sys.exit(1)
    except Exception as exc:
        logging.error("Simulation failed: %s", exc, exc_info=True)
        print("avg_score:0.0")
        print("cluster_coverage:0.0")
        print("best_strategy:error")
        sys.exit(1)
