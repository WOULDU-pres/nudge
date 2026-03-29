import { summary, evaluations, strategies, reason, trendData, sampleTranscripts } from "./sampleData";
import type { Summary, Evaluation, Strategy, ReasonData, TrendEntry, Transcript } from "../types";

export function loadSummary(): Summary {
  return summary;
}

export function loadEvaluations(): Evaluation[] {
  return evaluations;
}

export function loadStrategies(): Strategy[] {
  return strategies;
}

export function loadReason(): ReasonData {
  return reason;
}

export function loadTrendData(): TrendEntry[] {
  return trendData;
}

export function loadTranscript(sessionId: string): Transcript | null {
  return sampleTranscripts[sessionId] ?? null;
}

export function getAvailableTranscriptIds(): string[] {
  return Object.keys(sampleTranscripts);
}
