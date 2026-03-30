"""Aggregate evaluation results into summary statistics."""

import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


def aggregate_results(
    evaluations: list[dict],
    personas: list,
    strategies: list[dict],
) -> dict:
    """Aggregate evaluation results into a summary.

    Computes:
        - avg_score: Average total score across all evaluations.
        - cluster_coverage: Percentage of archetypes (clusters) with avg score >= 60.
        - best_strategy: Strategy ID with the highest average score.
        - cluster_scores: Per-cluster average scores.
        - outcome_distribution: Count of each outcome type.

    Args:
        evaluations: List of evaluation-result dicts.
        personas: List of Persona objects.
        strategies: List of strategy dicts.

    Returns:
        Summary dict matching ralph-iteration summary schema.
    """
    if not evaluations:
        return {
            "avg_score": 0.0,
            "cluster_coverage": 0.0,
            "best_strategy": "none",
            "cluster_scores": {},
            "outcome_distribution": {},
        }

    # Build persona_id -> archetype_id mapping
    persona_cluster_map: dict[str, str] = {}
    for persona in personas:
        pid = persona.persona_id if hasattr(persona, "persona_id") else persona.get("persona_id", "")
        aid = persona.archetype_id if hasattr(persona, "archetype_id") else persona.get("archetype_id", "")
        persona_cluster_map[pid] = aid

    # Filter out error evaluations for score computation
    valid_evals = [e for e in evaluations if e.get("outcome") != "error"]

    # --- Average score ---
    all_scores = [e["scores"]["total"] for e in valid_evals]
    avg_score = round(sum(all_scores) / len(all_scores), 1) if all_scores else 0.0

    # --- Per-strategy average scores ---
    strategy_scores: dict[str, list[int]] = defaultdict(list)
    for e in valid_evals:
        strategy_scores[e["strategy_id"]].append(e["scores"]["total"])

    strategy_avgs = {
        sid: round(sum(scores) / len(scores), 1)
        for sid, scores in strategy_scores.items()
        if scores
    }

    best_strategy = max(strategy_avgs, key=strategy_avgs.get, default="none")

    # --- Per-cluster average scores ---
    cluster_scores_raw: dict[str, list[int]] = defaultdict(list)
    for e in valid_evals:
        persona_id = e.get("persona_id", "")
        cluster = persona_cluster_map.get(persona_id, "unknown")
        cluster_scores_raw[cluster].append(e["scores"]["total"])

    cluster_scores = {
        cluster: round(sum(scores) / len(scores), 1)
        for cluster, scores in cluster_scores_raw.items()
        if scores
    }

    # --- Cluster coverage: percentage of clusters with avg >= 60 ---
    total_clusters = len(cluster_scores)
    passing_clusters = sum(1 for avg in cluster_scores.values() if avg >= 60)
    cluster_coverage = round(
        (passing_clusters / total_clusters * 100) if total_clusters > 0 else 0.0, 1
    )

    # --- Outcome distribution ---
    outcome_distribution: dict[str, int] = defaultdict(int)
    for e in evaluations:
        outcome_distribution[e.get("outcome", "unknown")] += 1

    return {
        "avg_score": avg_score,
        "cluster_coverage": cluster_coverage,
        "best_strategy": best_strategy,
        "cluster_scores": cluster_scores,
        "outcome_distribution": dict(outcome_distribution),
    }
