export interface Scores {
  engagement: number;
  relevance: number;
  persuasion: number;
  purchase_intent: number;
  total: number;
}

export interface Evaluation {
  session_id: string;
  strategy_id: string;
  persona_id: string;
  scores: Scores;
  outcome: string;
  reason: string;
  funnel_progress: number;
  objection_handling: string;
  tone_match: boolean;
}

export interface Summary {
  avg_score: number;
  cluster_coverage: number;
  best_strategy: string;
  cluster_scores: Record<string, number>;
  outcome_distribution: Record<string, number>;
  strategy_scores: Record<string, number>;
  strategy_cluster_matrix: Record<string, Record<string, number>>;
  funnel_distribution: Record<string, number>;
}

export interface Strategy {
  strategy_id: string;
  hypothesis: string;
  funnel: {
    attention: { hook_type: string; opening_line_guide: string; target_emotion: string };
    interest: { value_framing: string; information_depth: string; engagement_trigger: string };
    desire: { emotional_driver: string; proof_type: string; objection_preempt: string };
    action: { cta_style: string; urgency_type: string; fallback: string; risk_removal: string };
  };
  tone: string;
  persona_adaptation: string;
}

export interface ObjectionHandlingDetail {
  count: number;
  avg_score: number;
  examples?: string[];
}

export interface ReasonData {
  winning_patterns: string[];
  losing_patterns: string[];
  cluster_insights: Record<string, string>;
  objection_handling_analysis?: Record<string, ObjectionHandlingDetail>;
  tone_matching_analysis?: {
    matched: { count: number; avg_score: number };
    mismatched: { count: number; avg_score: number };
    notes: string;
  };
  funnel_analysis?: {
    attention_to_interest_rate: string;
    interest_to_desire_rate: string;
    desire_to_action_rate: string;
    bottleneck_stage: string;
    cluster_bottlenecks: Record<string, string>;
    cluster_conversion_rates: Record<string, Record<string, string>>;
  };
  technique_effectiveness?: Record<string, { used: number; avg_score_when_used: number; avg_score_when_not: number }>;
}

export interface Turn {
  role: "agent" | "persona";
  content: string;
}

export interface Transcript {
  session_id: string;
  strategy_id: string;
  persona_id: string;
  turns: Turn[];
  ended_by: string;
  error_message?: string | null;
}

export interface TrendEntry {
  run_id: string;
  avg_score: number;
  cluster_coverage: number;
  best_strategy: string;
  verdict: string;
  note: string;
}

export interface RunData {
  summary: Summary;
  evaluations: Evaluation[];
  strategies: Strategy[];
  reason: ReasonData;
  transcripts: Record<string, Transcript>;
}
