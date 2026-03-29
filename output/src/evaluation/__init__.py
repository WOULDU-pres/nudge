"""Evaluation module — Judge scoring and result aggregation."""
from src.evaluation.schema import (
    EvaluationResult,
    Scores,
    Outcome,
    ObjectionHandling,
)
from src.evaluation.evaluator import judge_conversation
from src.evaluation.aggregator import (
    aggregate_results,
    compute_avg_score,
    compute_cluster_scores,
    compute_cluster_coverage,
    compute_strategy_scores,
    compute_outcome_distribution,
    compute_funnel_distribution,
    compute_strategy_cluster_matrix,
    find_best_strategy,
    get_top_bottom_results,
)

__all__ = [
    # Schema
    "EvaluationResult",
    "Scores",
    "Outcome",
    "ObjectionHandling",
    # Evaluator
    "judge_conversation",
    # Aggregator
    "aggregate_results",
    "compute_avg_score",
    "compute_cluster_scores",
    "compute_cluster_coverage",
    "compute_strategy_scores",
    "compute_outcome_distribution",
    "compute_funnel_distribution",
    "compute_strategy_cluster_matrix",
    "find_best_strategy",
    "get_top_bottom_results",
]
