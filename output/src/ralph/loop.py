"""RALPH Loop — H→P→A→E→R→L 전체 순환."""
from __future__ import annotations

import asyncio
import json
import logging
import time
from pathlib import Path

from src.ralph.hypothesize import hypothesize
from src.ralph.plan import plan
from src.ralph.act import act
from src.ralph.reason import reason
from src.ralph.learn import learn
from src.evaluation.evaluator import judge_conversation
from src.evaluation.aggregator import aggregate_results
from src.conversation.turn import ConversationSession
from src.evaluation.schema import EvaluationResult
from config.settings import get_settings

logger = logging.getLogger("ralphthon.ralph")


async def run_ralph_loop(
    strategy_prompt: str,
    product_brief: str,
    personas: list[dict] | None = None,
    previous_learnings: str = "",
    best_strategy_summary: str = "",
    run_dir: Path | None = None,
) -> dict:
    """RALPH Loop 1회 실행.

    Args:
        strategy_prompt: strategy_prompt.md 내용
        product_brief: 제품 정보
        personas: 페르소나 리스트 (None이면 plan()으로 로드)
        previous_learnings: 이전 L 출력
        best_strategy_summary: 이전 최고 전략 요약
        run_dir: 실행 결과 저장 디렉토리

    Returns:
        {
            "summary": {avg_score, cluster_coverage, best_strategy, ...},
            "strategies": [...],
            "evaluations": [...],
            "reason": {...},
            "learnings": {...},
            "sessions": [...],  # ConversationSession dicts
        }
    """
    settings = get_settings()
    start_time = time.time()

    # ── H (Hypothesize) ──────────────────────────────────
    logger.info("=" * 60)
    logger.info("H (Hypothesize) — 전략 가설 생성")
    strategies = await hypothesize(
        strategy_prompt=strategy_prompt,
        product_brief=product_brief,
        previous_learnings=previous_learnings,
        best_strategy_summary=best_strategy_summary,
    )
    logger.info(f"  Generated {len(strategies)} strategies: {[s['strategy_id'] for s in strategies]}")

    # ── P (Plan) ─────────────────────────────────────────
    logger.info("P (Plan) — 페르소나 선택")
    if personas is None:
        personas = plan()
    logger.info(f"  Selected {len(personas)} personas ({settings.RALPHTHON_MODE} mode)")

    # ── A (Act) ──────────────────────────────────────────
    logger.info("A (Act) — 대화 시뮬레이션")
    sessions: list[ConversationSession] = await act(strategies, personas, product_brief=product_brief)
    logger.info(f"  Completed {len(sessions)} conversations")

    # ── E (Evaluate) ─────────────────────────────────────
    logger.info("E (Evaluate) — Judge 채점")
    semaphore = asyncio.Semaphore(settings.RALPHTHON_MAX_CONCURRENT)

    async def _judge_one(sess: ConversationSession) -> EvaluationResult:
        async with semaphore:
            # Judge는 transcript만 보고 채점 — 페르소나 정보 전달 안 함 (편향 방지)
            return await judge_conversation(sess)

    eval_tasks = [_judge_one(s) for s in sessions]
    evaluations: list[EvaluationResult] = await asyncio.gather(*eval_tasks)
    logger.info(f"  Evaluated {len(evaluations)} conversations")

    # Log individual scores
    for ev in evaluations:
        logger.info(f"    {ev.strategy_id} × {ev.persona_id}: total={ev.scores.total}, outcome={ev.outcome}")

    # ── Aggregate ────────────────────────────────────────
    summary = aggregate_results(evaluations, personas)
    logger.info(f"  avg_score={summary['avg_score']}, cluster_coverage={summary['cluster_coverage']}")
    logger.info(f"  best_strategy={summary['best_strategy']}")

    # ── R (Reason) ───────────────────────────────────────
    logger.info("R (Reason) — 패턴 분석")
    reason_output = await reason(evaluations, sessions, personas)
    logger.info(f"  winning_patterns: {len(reason_output.get('winning_patterns', []))}")
    logger.info(f"  losing_patterns: {len(reason_output.get('losing_patterns', []))}")

    # ── L (Learn) ────────────────────────────────────────
    logger.info("L (Learn) — 학습 추출")
    learnings_output = await learn(reason_output, strategy_prompt)
    logger.info(f"  learnings: {len(learnings_output.get('learnings', []))}")
    logger.info(f"  recommended_changes: {len(learnings_output.get('recommended_prompt_changes', []))}")

    elapsed = time.time() - start_time
    logger.info(f"RALPH Loop completed in {elapsed:.1f}s")
    logger.info("=" * 60)

    # ── Assemble result ──────────────────────────────────
    result = {
        "summary": summary,
        "strategies": strategies,
        "evaluations": [ev.model_dump() for ev in evaluations],
        "reason": reason_output,
        "learnings": learnings_output,
        "sessions": [s.model_dump() for s in sessions],
        "elapsed_seconds": round(elapsed, 1),
    }

    # ── Save to run_dir ──────────────────────────────────
    if run_dir:
        run_dir.mkdir(parents=True, exist_ok=True)
        _save_run(result, strategies, evaluations, sessions, reason_output, learnings_output, run_dir)

    return result


def _save_run(
    result: dict,
    strategies: list[dict],
    evaluations: list[EvaluationResult],
    sessions: list[ConversationSession],
    reason_output: dict,
    learnings_output: dict,
    run_dir: Path,
):
    """결과를 run_dir에 저장."""
    # summary.json
    with open(run_dir / "summary.json", "w", encoding="utf-8") as f:
        json.dump(result["summary"], f, ensure_ascii=False, indent=2)

    # strategies.json
    with open(run_dir / "strategies.json", "w", encoding="utf-8") as f:
        json.dump(strategies, f, ensure_ascii=False, indent=2)

    # evaluations.json
    with open(run_dir / "evaluations.json", "w", encoding="utf-8") as f:
        json.dump([ev.model_dump() for ev in evaluations], f, ensure_ascii=False, indent=2)

    # reason.json
    with open(run_dir / "reason.json", "w", encoding="utf-8") as f:
        json.dump(reason_output, f, ensure_ascii=False, indent=2)

    # learnings.json
    with open(run_dir / "learnings.json", "w", encoding="utf-8") as f:
        json.dump(learnings_output, f, ensure_ascii=False, indent=2)

    # transcripts/<strategy_id>/<persona_id>.json
    transcripts_dir = run_dir / "transcripts"
    for sess in sessions:
        strat_dir = transcripts_dir / sess.strategy_id
        strat_dir.mkdir(parents=True, exist_ok=True)
        with open(strat_dir / f"{sess.persona_id}.json", "w", encoding="utf-8") as f:
            json.dump(sess.model_dump(), f, ensure_ascii=False, indent=2)

    logger.info(f"  Saved run artifacts to {run_dir}")
