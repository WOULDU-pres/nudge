"""RALPH Loop — H -> P -> A -> E -> R -> L orchestration."""
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

from src.ralph.hypothesize import hypothesize
from src.ralph.plan import plan_personas
from src.ralph.act import act
from src.ralph.evaluate import evaluate
from src.ralph.reason import reason
from src.ralph.learn import learn
from src.evaluation.aggregator import (
    aggregate_results,
    compute_strategy_scores,
    compute_strategy_cluster_matrix,
    compute_funnel_distribution,
)

logger = logging.getLogger(__name__)


def _save_run_artifacts(
    run_dir: Path,
    strategies: list[dict],
    sessions: list,
    eval_results: list,
    reason_output: dict,
    learn_output: dict,
    summary: dict,
):
    """Save all RALPH artifacts to runs/<run_id>/."""
    run_dir.mkdir(parents=True, exist_ok=True)

    # strategies.json
    with open(run_dir / "strategies.json", "w", encoding="utf-8") as f:
        json.dump(strategies, f, ensure_ascii=False, indent=2)

    # evaluations.json
    evals_data = [r.model_dump() for r in eval_results]
    # Convert enums to strings
    for e in evals_data:
        if hasattr(e.get("outcome", ""), "value"):
            e["outcome"] = e["outcome"].value
        if "scores" in e and hasattr(e["scores"], "items"):
            pass  # already dict from model_dump
        if hasattr(e.get("objection_handling", ""), "value"):
            e["objection_handling"] = e["objection_handling"].value
    with open(run_dir / "evaluations.json", "w", encoding="utf-8") as f:
        json.dump(evals_data, f, ensure_ascii=False, indent=2)

    # transcripts/<strategy_id>/<persona_id>.json
    transcripts_dir = run_dir / "transcripts"
    for session in sessions:
        strat_dir = transcripts_dir / session.strategy_id
        strat_dir.mkdir(parents=True, exist_ok=True)
        session_data = session.model_dump()
        # Convert enums
        for t in session_data.get("turns", []):
            if hasattr(t.get("role", ""), "value"):
                t["role"] = t["role"].value
        if hasattr(session_data.get("ended_by", ""), "value"):
            session_data["ended_by"] = session_data["ended_by"].value
        with open(strat_dir / f"{session.persona_id}.json", "w", encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)

    # reason.json
    with open(run_dir / "reason.json", "w", encoding="utf-8") as f:
        json.dump(reason_output, f, ensure_ascii=False, indent=2)

    # learnings.json
    with open(run_dir / "learnings.json", "w", encoding="utf-8") as f:
        json.dump(learn_output, f, ensure_ascii=False, indent=2)

    # summary.json
    with open(run_dir / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)


async def run_ralph_loop(
    product_brief: str,
    persona_count: int = 50,
    num_strategies: int = 3,
    max_round_trips: int = 3,
    max_concurrent: int = 20,
    previous_learnings: dict | None = None,
    strategy_ledger: dict | None = None,
    run_id: str | None = None,
) -> dict:
    """Execute one full RALPH cycle: H -> P -> A -> E -> R -> L.

    Args:
        product_brief: Product information text.
        persona_count: Number of personas to use.
        num_strategies: Number of strategies to generate.
        max_round_trips: Conversation turns.
        max_concurrent: Max parallel LLM calls.
        previous_learnings: Learnings from previous cycle.
        strategy_ledger: Strategy history ledger.
        run_id: Optional run identifier.

    Returns:
        Dict matching ralph-iteration.schema.json with all results.
    """
    from config.settings import settings

    if run_id is None:
        run_id = datetime.now(timezone.utc).strftime("run-%Y%m%d-%H%M%S")

    output_dir = settings.output_dir
    run_dir = output_dir / "runs" / run_id

    logger.info(f"=== RALPH Loop Start: {run_id} ===")
    logger.info(f"Personas: {persona_count}, Strategies: {num_strategies}, Turns: {max_round_trips}")

    # H — Hypothesize
    logger.info("--- H (Hypothesize) ---")
    strategies = await hypothesize(
        product_brief=product_brief,
        num_strategies=num_strategies,
        previous_learnings=previous_learnings,
        strategy_ledger=strategy_ledger,
    )
    logger.info(f"Generated {len(strategies)} strategies")

    # P — Plan
    logger.info("--- P (Plan) ---")
    personas = plan_personas(count=persona_count)
    logger.info(f"Selected {len(personas)} personas")

    # A — Act
    logger.info("--- A (Act) ---")
    sessions = await act(
        strategies=strategies,
        personas=personas,
        product_brief=product_brief,
        max_round_trips=max_round_trips,
        max_concurrent=max_concurrent,
    )
    logger.info(f"Completed {len(sessions)} conversations")

    # E — Evaluate
    logger.info("--- E (Evaluate) ---")
    eval_results = await evaluate(
        sessions=sessions,
        personas=personas,
        max_concurrent=max_concurrent,
    )
    logger.info(f"Evaluated {len(eval_results)} conversations")

    # Aggregate results
    summary = aggregate_results(eval_results, personas)

    # R — Reason
    logger.info("--- R (Reason) ---")
    reason_output = await reason(
        eval_results=eval_results,
        sessions=sessions,
        top_n=min(5, len(eval_results) // 2 or 1),
    )

    # L — Learn
    logger.info("--- L (Learn) ---")
    learn_output = await learn(reason_output=reason_output)

    # Add extra summary fields
    summary["strategy_scores"] = compute_strategy_scores(eval_results)
    summary["strategy_cluster_matrix"] = compute_strategy_cluster_matrix(eval_results, personas)
    summary["funnel_distribution"] = compute_funnel_distribution(eval_results)

    # Save artifacts
    logger.info(f"Saving artifacts to {run_dir}")
    _save_run_artifacts(
        run_dir=run_dir,
        strategies=strategies,
        sessions=sessions,
        eval_results=eval_results,
        reason_output=reason_output,
        learn_output=learn_output,
        summary=summary,
    )

    # Build full iteration result
    iteration_result = {
        "iteration_id": 0,
        "run_id": run_id,
        "strategies": strategies,
        "evaluations": [r.to_schema_dict() for r in eval_results],
        "reason": reason_output,
        "learnings": learn_output,
        "summary": summary,
    }

    # Print grep-able output
    print(f"avg_score: {summary['avg_score']}")
    print(f"cluster_coverage: {summary['cluster_coverage']}")
    print(f"best_strategy: {summary['best_strategy']}")

    logger.info(f"=== RALPH Loop Complete: avg={summary['avg_score']}, coverage={summary['cluster_coverage']}% ===")
    return iteration_result
