"""Aggregation utilities for evaluation results.

Computes summary statistics across multiple EvaluationResults:
- Average scores (overall and per-cluster)
- Cluster coverage
- Outcome distribution
- Best/worst strategies
- Funnel progress distribution
"""
import logging
from collections import defaultdict
from typing import Optional

from src.evaluation.schema import EvaluationResult, Outcome
from src.personas.schema import Persona

logger = logging.getLogger(__name__)


def compute_avg_score(results: list[EvaluationResult]) -> float:
    """Average total score across all evaluations."""
    if not results:
        return 0.0
    valid = [r for r in results if r.outcome != Outcome.ERROR]
    if not valid:
        return 0.0
    return sum(r.scores.total for r in valid) / len(valid)


def compute_dimension_averages(results: list[EvaluationResult]) -> dict[str, float]:
    """Average for each scoring dimension."""
    valid = [r for r in results if r.outcome != Outcome.ERROR]
    if not valid:
        return {
            "engagement": 0.0,
            "relevance": 0.0,
            "persuasion": 0.0,
            "purchase_intent": 0.0,
            "total": 0.0,
        }
    n = len(valid)
    return {
        "engagement": sum(r.scores.engagement for r in valid) / n,
        "relevance": sum(r.scores.relevance for r in valid) / n,
        "persuasion": sum(r.scores.persuasion for r in valid) / n,
        "purchase_intent": sum(r.scores.purchase_intent for r in valid) / n,
        "total": sum(r.scores.total for r in valid) / n,
    }


def compute_outcome_distribution(results: list[EvaluationResult]) -> dict[str, int]:
    """Count of each outcome type."""
    dist: dict[str, int] = {}
    for outcome in Outcome:
        dist[outcome.value] = 0
    for r in results:
        dist[r.outcome.value] = dist.get(r.outcome.value, 0) + 1
    return dist


def compute_funnel_distribution(results: list[EvaluationResult]) -> dict[int, int]:
    """Count of each funnel_progress level (0-3)."""
    dist = {0: 0, 1: 0, 2: 0, 3: 0}
    valid = [r for r in results if r.outcome != Outcome.ERROR]
    for r in valid:
        dist[r.funnel_progress] = dist.get(r.funnel_progress, 0) + 1
    return dist


def compute_cluster_scores(
    results: list[EvaluationResult],
    personas: list[Persona],
) -> dict[str, float]:
    """Average total score per cluster.

    Args:
        results: All evaluation results.
        personas: All personas (to map persona_id -> cluster).

    Returns:
        Dict mapping cluster tag -> average total score.
    """
    # Build persona_id -> primary_cluster lookup
    persona_cluster_map: dict[str, str] = {}
    for p in personas:
        persona_cluster_map[p.persona_id] = p.primary_cluster

    # Group scores by cluster
    cluster_totals: dict[str, list[int]] = defaultdict(list)
    for r in results:
        if r.outcome == Outcome.ERROR:
            continue
        cluster = persona_cluster_map.get(r.persona_id, "unknown")
        cluster_totals[cluster].append(r.scores.total)

    # Compute averages
    cluster_avgs: dict[str, float] = {}
    for cluster, totals in sorted(cluster_totals.items()):
        cluster_avgs[cluster] = sum(totals) / len(totals) if totals else 0.0

    return cluster_avgs


def compute_cluster_coverage(
    cluster_scores: dict[str, float],
    threshold: float = 40.0,
) -> float:
    """Percentage of clusters with average score >= threshold.

    Args:
        cluster_scores: Dict of cluster -> avg score.
        threshold: Minimum avg score to count as "covered".

    Returns:
        Coverage percentage (0-100).
    """
    if not cluster_scores:
        return 0.0
    covered = sum(1 for avg in cluster_scores.values() if avg >= threshold)
    return (covered / len(cluster_scores)) * 100.0


def compute_strategy_scores(
    results: list[EvaluationResult],
) -> dict[str, float]:
    """Average total score per strategy.

    Returns:
        Dict mapping strategy_id -> average total score, sorted descending.
    """
    strategy_totals: dict[str, list[int]] = defaultdict(list)
    for r in results:
        if r.outcome == Outcome.ERROR:
            continue
        strategy_totals[r.strategy_id].append(r.scores.total)

    strategy_avgs: dict[str, float] = {}
    for sid, totals in strategy_totals.items():
        strategy_avgs[sid] = sum(totals) / len(totals) if totals else 0.0

    # Sort descending by score
    return dict(sorted(strategy_avgs.items(), key=lambda x: x[1], reverse=True))


def find_best_strategy(results: list[EvaluationResult]) -> Optional[str]:
    """Find the strategy_id with the highest average total score."""
    strategy_avgs = compute_strategy_scores(results)
    if not strategy_avgs:
        return None
    return next(iter(strategy_avgs))  # Already sorted descending


def compute_strategy_cluster_matrix(
    results: list[EvaluationResult],
    personas: list[Persona],
) -> dict[str, dict[str, float]]:
    """Build a strategy x cluster score matrix.

    Returns:
        Nested dict: strategy_id -> cluster_tag -> avg_score
    """
    # Build persona_id -> primary_cluster lookup
    persona_cluster_map: dict[str, str] = {}
    for p in personas:
        persona_cluster_map[p.persona_id] = p.primary_cluster

    # Group: strategy -> cluster -> scores
    matrix: dict[str, dict[str, list[int]]] = defaultdict(lambda: defaultdict(list))
    for r in results:
        if r.outcome == Outcome.ERROR:
            continue
        cluster = persona_cluster_map.get(r.persona_id, "unknown")
        matrix[r.strategy_id][cluster].append(r.scores.total)

    # Average
    avg_matrix: dict[str, dict[str, float]] = {}
    for sid, clusters in sorted(matrix.items()):
        avg_matrix[sid] = {}
        for cluster, totals in sorted(clusters.items()):
            avg_matrix[sid][cluster] = sum(totals) / len(totals) if totals else 0.0

    return avg_matrix


def get_top_bottom_results(
    results: list[EvaluationResult],
    n: int = 3,
) -> tuple[list[EvaluationResult], list[EvaluationResult]]:
    """Get top N and bottom N results by total score.

    Used by Reason stage for pattern analysis.

    Returns:
        Tuple of (top_n, bottom_n) results.
    """
    valid = [r for r in results if r.outcome != Outcome.ERROR]
    sorted_results = sorted(valid, key=lambda r: r.scores.total, reverse=True)

    top = sorted_results[:n]
    bottom = sorted_results[-n:] if len(sorted_results) >= n else sorted_results

    return top, bottom


def aggregate_results(
    results: list[EvaluationResult],
    personas: list[Persona],
) -> dict:
    """Produce the full summary dict for a RALPH iteration.

    Returns a dict matching ralph-iteration.schema.json → summary.
    """
    cluster_scores = compute_cluster_scores(results, personas)
    cluster_coverage = compute_cluster_coverage(cluster_scores)
    avg_score = compute_avg_score(results)
    best_strategy = find_best_strategy(results)
    outcome_dist = compute_outcome_distribution(results)

    summary = {
        "avg_score": round(avg_score, 2),
        "cluster_coverage": round(cluster_coverage, 2),
        "best_strategy": best_strategy or "none",
        "cluster_scores": {k: round(v, 2) for k, v in cluster_scores.items()},
        "outcome_distribution": outcome_dist,
    }

    logger.info(
        f"Aggregated {len(results)} evaluations: "
        f"avg={summary['avg_score']}, coverage={summary['cluster_coverage']}%, "
        f"best={summary['best_strategy']}"
    )

    return summary
