"""RALPH Loop v2 using acpx/Codex-backed conversations and judge calls."""

from __future__ import annotations

import json
import time
from pathlib import Path

from src.agents.llm_customer_agent import LLMCustomerAgent
from src.agents.llm_sales_agent import LLMSalesAgent
from src.conversation.engine_v2 import run_conversation_v2
from src.evaluation.llm_evaluator import evaluate_session
from src.personas.loader import load_personas
from src.ralph.strategy import (
    load_product,
    hypothesize_strategy,
    learn_from_iteration,
    reason_about_iteration,
)


def _save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


async def run_single_session(strategy: dict, persona, product: dict, max_turns: int) -> tuple[dict, dict]:
    sales = LLMSalesAgent(strategy=strategy, product=product)
    customer = LLMCustomerAgent(persona=persona)
    session = await run_conversation_v2(sales, customer, strategy['strategy_id'], persona.persona_id, max_turns=max_turns)
    evaluation = await evaluate_session(session, strategy, persona)
    return session, evaluation


async def run_ralph_loop_v2(
    iterations: int = 3,
    personas_count: int = 3,
    max_turns: int = 4,
    product_path: str = 'config/product.yaml',
    run_id: str | None = None,
) -> dict:
    if run_id is None:
        run_id = f'ralph-v2-{int(time.time())}'

    product = load_product(product_path)
    all_personas = load_personas('../harness/data/personas', mode='DEMO')
    personas = all_personas[:personas_count]
    run_dir = Path('runs') / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    previous_learnings: list[str] = []
    results: list[dict] = []
    score_trend: list[float] = []
    purchase_trend: list[float] = []
    total_learnings: list[str] = []
    started_at = time.time()

    for iteration in range(1, iterations + 1):
        strategy = await hypothesize_strategy(product, previous_learnings, iteration)
        sessions: list[dict] = []
        evaluations: list[dict] = []

        for persona in personas:
            session, evaluation = await run_single_session(strategy, persona, product, max_turns)
            sessions.append(session)
            evaluations.append(evaluation)

        valid_scores = [e['scores']['total'] for e in evaluations if e.get('outcome') != 'error']
        avg_weighted_score = round(sum(valid_scores) / len(valid_scores), 2) if valid_scores else 0.0
        purchase_rate = round(
            100.0 * sum(1 for e in evaluations if e.get('outcome') in {'converted', 'interested', 'wishlist'}) / max(len(evaluations), 1),
            1,
        )
        reason_output = await reason_about_iteration({
            'strategy': strategy,
            'sessions': sessions,
            'evaluations': evaluations,
            'iteration': iteration,
        })
        learning_output = await learn_from_iteration(reason_output)
        iteration_learnings = [str(x) for x in learning_output.get('learnings', [])]
        previous_learnings = iteration_learnings
        total_learnings.extend(iteration_learnings)

        iteration_result = {
            'iteration': iteration,
            'strategy': strategy,
            'sessions': sessions,
            'evaluations': evaluations,
            'avg_weighted_score': avg_weighted_score,
            'purchase_rate': purchase_rate,
            'reason': reason_output,
            'learning': learning_output,
        }
        results.append(iteration_result)
        score_trend.append(avg_weighted_score)
        purchase_trend.append(purchase_rate)
        _save_json(run_dir / f'iter_{iteration}.json', iteration_result)

    best_iteration = max(results, key=lambda x: x['avg_weighted_score']) if results else None
    final_summary = {
        'run_id': run_id,
        'iterations': iterations,
        'personas_count': personas_count,
        'max_turns': max_turns,
        'score_trend': score_trend,
        'purchase_rate_trend': purchase_trend,
        'average_purchase_rate': round(sum(purchase_trend) / len(purchase_trend), 1) if purchase_trend else 0.0,
        'total_learnings': len(total_learnings),
        'learnings': total_learnings,
        'best_iteration': {
            'iteration': best_iteration['iteration'],
            'avg_weighted_score': best_iteration['avg_weighted_score'],
            'purchase_rate': best_iteration['purchase_rate'],
            'strategy_id': best_iteration['strategy'].get('strategy_id', 'unknown'),
            'hypothesis': best_iteration['strategy'].get('hypothesis', ''),
        } if best_iteration else None,
        'elapsed_sec': round(time.time() - started_at, 1),
        'results': results,
    }
    _save_json(Path('ralph_v2_result.json'), final_summary)
    _save_json(run_dir / 'summary.json', final_summary)
    return final_summary
