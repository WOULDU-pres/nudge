"""점수 집계."""
from __future__ import annotations

from collections import defaultdict
from src.evaluation.schema import EvaluationResult


def aggregate_results(
    evaluations: list[EvaluationResult],
    personas: list[dict],
) -> dict:
    """평가 결과를 집계.

    Returns:
        {
            "avg_score": float,
            "cluster_coverage": float,  # 60점 이상 클러스터 비율 (%)
            "best_strategy": str,
            "cluster_scores": {cluster: avg_score},
            "strategy_scores": {strategy_id: avg_score},
            "outcome_distribution": {outcome: count},
        }
    """
    if not evaluations:
        return {
            "avg_score": 0.0,
            "cluster_coverage": 0.0,
            "best_strategy": "none",
            "cluster_scores": {},
            "strategy_scores": {},
            "outcome_distribution": {},
        }

    # Build persona → cluster_tags map
    persona_clusters: dict[str, list[str]] = {}
    for p in personas:
        pid = p.get("id", "")
        tags = p.get("cluster_tags", [])
        persona_clusters[pid] = tags

    # Aggregate per strategy
    strategy_totals: dict[str, list[int]] = defaultdict(list)
    for ev in evaluations:
        strategy_totals[ev.strategy_id].append(ev.scores.total)

    strategy_avgs = {
        sid: sum(scores) / len(scores) for sid, scores in strategy_totals.items()
    }
    best_strategy = max(strategy_avgs, key=strategy_avgs.get) if strategy_avgs else "none"

    # Overall avg
    all_scores = [ev.scores.total for ev in evaluations]
    avg_score = sum(all_scores) / len(all_scores) if all_scores else 0.0

    # Cluster scores
    cluster_totals: dict[str, list[int]] = defaultdict(list)
    for ev in evaluations:
        tags = persona_clusters.get(ev.persona_id, [])
        for tag in tags:
            cluster_totals[tag].append(ev.scores.total)

    cluster_avgs = {
        tag: sum(scores) / len(scores) for tag, scores in cluster_totals.items()
    }

    # Cluster coverage: clusters with avg >= 60
    if cluster_avgs:
        above_60 = sum(1 for avg in cluster_avgs.values() if avg >= 60)
        cluster_coverage = (above_60 / len(cluster_avgs)) * 100
    else:
        cluster_coverage = 0.0

    # Outcome distribution
    outcome_dist: dict[str, int] = defaultdict(int)
    for ev in evaluations:
        outcome_dist[ev.outcome] += 1

    return {
        "avg_score": round(avg_score, 2),
        "cluster_coverage": round(cluster_coverage, 1),
        "best_strategy": best_strategy,
        "cluster_scores": {k: round(v, 2) for k, v in cluster_avgs.items()},
        "strategy_scores": {k: round(v, 2) for k, v in strategy_avgs.items()},
        "outcome_distribution": dict(outcome_dist),
    }
