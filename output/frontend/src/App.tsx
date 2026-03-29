import { useState, useMemo } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  Cell,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Legend,
  ReferenceLine,
} from "recharts";
import {
  loadSummary,
  loadEvaluations,
  loadStrategies,
  loadReason,
  loadTrendData,
  loadTranscript,
  getAvailableTranscriptIds,
} from "./data/loader";
import type { Transcript } from "./types";

const summary = loadSummary();
const evaluations = loadEvaluations();
const strategies = loadStrategies();
const reason = loadReason();
const trendData = loadTrendData();

// ── Color Palette ─────────────────────────────────────────
const STRATEGY_COLORS: Record<string, string> = {
  "strategy-health-conscious": "#6366f1",
  "strategy-cost-sensitive": "#06b6d4",
  "strategy-busy-professional": "#f59e0b",
};

const STRATEGY_LABELS: Record<string, string> = {
  "strategy-health-conscious": "건강 전문가형",
  "strategy-cost-sensitive": "가성비 강조형",
  "strategy-busy-professional": "바쁜 직장인형",
};

const OUTCOME_COLORS: Record<string, string> = {
  converted: "#10b981",
  interested: "#6366f1",
  neutral: "#94a3b8",
  resistant: "#f97316",
  lost: "#ef4444",
};

// ── Helpers ───────────────────────────────────────────────
function scoreColor(score: number): string {
  if (score >= 80) return "bg-emerald-500 text-white";
  if (score >= 70) return "bg-emerald-400 text-white";
  if (score >= 60) return "bg-amber-400 text-amber-950";
  if (score >= 50) return "bg-orange-400 text-white";
  return "bg-red-500 text-white";
}



// ── Section Wrapper ───────────────────────────────────────
function Section({
  id,
  number,
  title,
  subtitle,
  children,
  className = "",
}: {
  id?: string;
  number: string;
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <section id={id} className={`mb-10 ${className}`}>
      <div className="flex items-baseline gap-3 mb-1">
        <span className="text-xs font-bold text-indigo-500 bg-indigo-50 px-2 py-0.5 rounded-full">{number}</span>
        <h2 className="text-lg font-bold text-gray-900">{title}</h2>
      </div>
      {subtitle && <p className="text-sm text-gray-500 mb-4 ml-10">{subtitle}</p>}
      <div className="ml-0 mt-3">{children}</div>
    </section>
  );
}

function Card({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={`bg-white border border-gray-200 rounded-xl shadow-sm p-5 ${className}`}>
      {children}
    </div>
  );
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// [1] EXECUTIVE HERO
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
function ExecutiveHero() {
  const latestScore = trendData[trendData.length - 1]?.avg_score ?? summary.avg_score;
  const baseline = trendData[0]?.avg_score ?? summary.avg_score;
  const delta = latestScore - baseline;

  const kpis = [
    {
      label: "평균 점수",
      value: latestScore.toFixed(1),
      sub: `baseline ${baseline.toFixed(1)}`,
      delta: delta > 0 ? `+${delta.toFixed(1)}` : delta.toFixed(1),
      good: delta >= 0,
    },
    {
      label: "전환율 (Desire→Action)",
      value: "0%",
      sub: "전 전략 공통 병목",
      delta: "⚠ 핵심 이슈",
      good: false,
    },
    {
      label: "최고 전략",
      value: STRATEGY_LABELS[summary.best_strategy] ?? summary.best_strategy,
      sub: `${summary.strategy_scores[summary.best_strategy]?.toFixed(1) ?? "—"}점`,
      delta: "",
      good: true,
    },
    {
      label: "클러스터 커버리지",
      value: `${summary.cluster_coverage}%`,
      sub: `${evaluations.length}건 평가`,
      delta: "완료",
      good: true,
    },
  ];

  return (
    <div className="mb-10">
      {/* Headline */}
      <div className="bg-gradient-to-r from-indigo-600 to-violet-600 rounded-2xl p-8 text-white mb-6 shadow-lg">
        <p className="text-sm font-medium text-indigo-200 mb-2">핵심 발견</p>
        <h2 className="text-2xl font-bold mb-2">
          Desire → Action 전환율 0% — 관심은 끄는데 구매로 이어지지 않음
        </h2>
        <p className="text-indigo-100 text-sm leading-relaxed max-w-3xl">
          3개 전략 × 10명 페르소나 시뮬레이션 결과, 모든 전략에서 "관심(Desire)" 단계까지는 도달하지만
          실제 "구매 행동(Action)"으로의 전환은 0%입니다. 클로징 기법과 risk_removal 전략의 강화가 필요합니다.
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {kpis.map((k) => (
          <Card key={k.label}>
            <p className="text-xs text-gray-500 mb-1">{k.label}</p>
            <p className="text-2xl font-bold text-gray-900">{k.value}</p>
            <div className="flex items-center justify-between mt-2">
              <span className="text-xs text-gray-400">{k.sub}</span>
              {k.delta && (
                <span className={`text-xs font-bold ${k.good ? "text-emerald-500" : "text-red-500"}`}>
                  {k.delta}
                </span>
              )}
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// [2] FUNNEL ANALYSIS
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
function FunnelAnalysis() {
  const stages = [
    { name: "Attention", count: summary.funnel_distribution["0"] ?? 0, color: "#e5e7eb" },
    { name: "Interest", count: summary.funnel_distribution["1"] ?? 0, color: "#93c5fd" },
    { name: "Desire", count: summary.funnel_distribution["2"] ?? 0, color: "#6366f1" },
    { name: "Action", count: summary.funnel_distribution["3"] ?? 0, color: "#10b981" },
  ];

  // Total conversations
  const total = evaluations.length;

  // Cumulative: people who reached at least this stage
  // stage 0: 1 person stuck at Attention only
  // stage 1: 6 people stuck at Interest
  // stage 2: 23 people stuck at Desire
  // stage 3: 0 people reached Action
  // So people who reached at least Attention = all = 30
  // reached at least Interest = total - stage0 stuck = 30 - 1 = 29
  // reached at least Desire = 29 - 6 = 23
  // reached Action = 0
  const reachedAtLeast = [
    total,
    total - stages[0].count,
    total - stages[0].count - stages[1].count,
    stages[3].count,
  ];

  const conversionRates = [
    { from: "Attention", to: "Interest", rate: reason.funnel_analysis?.attention_to_interest_rate ?? "—" },
    { from: "Interest", to: "Desire", rate: reason.funnel_analysis?.interest_to_desire_rate ?? "—" },
    { from: "Desire", to: "Action", rate: reason.funnel_analysis?.desire_to_action_rate ?? "—", bottleneck: true },
  ];

  // Per-strategy funnel
  const strategyFunnel = reason.funnel_analysis?.cluster_conversion_rates
    ? Object.entries(reason.funnel_analysis.cluster_conversion_rates).map(([stratId, rates]) => ({
        strategy: STRATEGY_LABELS[stratId] ?? stratId.replace("strategy-", ""),
        stratId,
        attToInt: rates.attention_to_interest ?? "—",
        intToDes: rates.interest_to_desire ?? "—",
        desToAct: rates.desire_to_action ?? "—",
      }))
    : [];

  return (
    <Section number="01" title="퍼널 분석" subtitle="어디에서 고객을 잃고 있는가?" id="funnel">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Visual Funnel */}
        <Card className="lg:col-span-2">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">AIDA 퍼널 잔존율</h3>
          <div className="flex flex-col items-center gap-1">
            {["Attention", "Interest", "Desire", "Action"].map((stage, i) => {
              const reached = reachedAtLeast[i];
              const pct = total > 0 ? (reached / total) * 100 : 0;
              const width = Math.max(20, pct);
              const isBottleneck = i === 3;

              return (
                <div key={stage} className="w-full flex items-center gap-4">
                  <div className="w-20 text-right text-xs font-medium text-gray-600">{stage}</div>
                  <div className="flex-1 relative">
                    <div className="h-12 rounded-lg flex items-center relative overflow-hidden" style={{ backgroundColor: "#f3f4f6" }}>
                      <div
                        className="h-full rounded-lg flex items-center justify-center transition-all duration-500"
                        style={{
                          width: `${width}%`,
                          backgroundColor: isBottleneck ? "#ef4444" : stages[i].color,
                          minWidth: "60px",
                        }}
                      >
                        <span className={`text-xs font-bold ${i >= 2 ? "text-white" : "text-gray-700"}`}>
                          {reached}명 ({pct.toFixed(0)}%)
                        </span>
                      </div>
                    </div>
                  </div>
                  {i < 3 && (
                    <div className="w-24 text-center">
                      <div className={`text-lg font-bold ${i === 2 ? "text-red-500" : "text-gray-600"}`}>
                        {i === 2 ? "↓" : "→"} {conversionRates[i].rate}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
          {/* Bottleneck callout */}
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-xl flex items-start gap-3">
            <span className="text-2xl">🚨</span>
            <div>
              <p className="text-sm font-bold text-red-700">병목 지점: Desire → Action</p>
              <p className="text-xs text-red-600 mt-1">
                23명이 "관심" 단계까지 도달했지만 단 한 명도 구매 행동으로 전환되지 않았습니다.
                CTA(Call-to-Action) 강화, 구체적 혜택 제시, risk_removal 기법 적용이 필요합니다.
              </p>
            </div>
          </div>
        </Card>

        {/* Per-Strategy Funnel Comparison */}
        <Card>
          <h3 className="text-sm font-semibold text-gray-700 mb-4">전략별 전환율 비교</h3>
          <div className="space-y-4">
            {strategyFunnel.map((sf) => (
              <div key={sf.stratId} className="border border-gray-100 rounded-lg p-3">
                <div className="flex items-center gap-2 mb-3">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: STRATEGY_COLORS[sf.stratId] ?? "#6366f1" }} />
                  <span className="text-xs font-semibold text-gray-800">{sf.strategy}</span>
                </div>
                <div className="space-y-1.5 text-xs">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Attention → Interest</span>
                    <span className="font-semibold text-emerald-600">{sf.attToInt}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Interest → Desire</span>
                    <span className="font-semibold text-amber-600">{sf.intToDes}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Desire → Action</span>
                    <span className="font-bold text-red-500">{sf.desToAct}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </Section>
  );
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// [3] STRATEGY COMPARISON
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
function StrategyComparison() {
  // Build radar data
  const dimensions = ["engagement", "relevance", "persuasion", "purchase_intent"] as const;
  const dimLabels: Record<string, string> = {
    engagement: "참여도",
    relevance: "관련성",
    persuasion: "설득력",
    purchase_intent: "구매의도",
  };

  const strategyIds = Object.keys(summary.strategy_scores);

  // Average scores per dimension per strategy
  const radarData = dimensions.map((dim) => {
    const point: Record<string, string | number> = { dimension: dimLabels[dim] };
    strategyIds.forEach((sid) => {
      const evals = evaluations.filter((e) => e.strategy_id === sid);
      const avg = evals.length > 0 ? evals.reduce((sum, e) => sum + e.scores[dim], 0) / evals.length : 0;
      point[sid] = Math.round(avg * 10) / 10;
    });
    return point;
  });

  // Bar chart: overall score comparison
  const barData = Object.entries(summary.strategy_scores)
    .sort(([, a], [, b]) => b - a)
    .map(([id, score]) => ({
      name: STRATEGY_LABELS[id] ?? id.replace("strategy-", ""),
      score,
      id,
    }));

  // Outcome per strategy
  const outcomeByStrategy = strategyIds.map((sid) => {
    const evals = evaluations.filter((e) => e.strategy_id === sid);
    const outcomes: Record<string, number> = {};
    evals.forEach((e) => {
      outcomes[e.outcome] = (outcomes[e.outcome] ?? 0) + 1;
    });
    return {
      strategy: STRATEGY_LABELS[sid] ?? sid.replace("strategy-", ""),
      sid,
      outcomes,
      total: evals.length,
    };
  });

  return (
    <Section number="02" title="전략 성과 비교" subtitle="어떤 전략이 가장 효과적인가?" id="strategies">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Radar Chart */}
        <Card>
          <h3 className="text-sm font-semibold text-gray-700 mb-4">차원별 성과 레이더</h3>
          <ResponsiveContainer width="100%" height={320}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="#e5e7eb" />
              <PolarAngleAxis dataKey="dimension" tick={{ fontSize: 12, fill: "#6b7280" }} />
              <PolarRadiusAxis angle={90} domain={[0, 20]} tick={{ fontSize: 10 }} />
              {strategyIds.map((sid) => (
                <Radar
                  key={sid}
                  name={STRATEGY_LABELS[sid] ?? sid}
                  dataKey={sid}
                  stroke={STRATEGY_COLORS[sid] ?? "#6366f1"}
                  fill={STRATEGY_COLORS[sid] ?? "#6366f1"}
                  fillOpacity={0.15}
                  strokeWidth={2}
                />
              ))}
              <Legend
                wrapperStyle={{ fontSize: 11 }}
                formatter={(value: string) => STRATEGY_LABELS[value] ?? value}
              />
            </RadarChart>
          </ResponsiveContainer>
          <p className="text-xs text-gray-400 mt-2 text-center">각 차원은 20점 만점 기준</p>
        </Card>

        {/* Score Ranking Bar */}
        <Card>
          <h3 className="text-sm font-semibold text-gray-700 mb-4">종합 점수 순위</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={barData} layout="vertical" margin={{ left: 10, right: 30 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" horizontal={false} />
              <XAxis type="number" domain={[50, 70]} tick={{ fontSize: 11 }} />
              <YAxis type="category" dataKey="name" tick={{ fontSize: 11 }} width={120} />
              <Tooltip
                contentStyle={{ backgroundColor: "#fff", border: "1px solid #e5e7eb", borderRadius: 8, fontSize: 12 }}
              formatter={(value) => [`${Number(value).toFixed(1)}점`, "종합 점수"]}
            />
            <ReferenceLine x={summary.avg_score} stroke="#94a3b8" strokeDasharray="3 3" label={{ value: `평균 ${summary.avg_score}`, position: "top", fontSize: 10, fill: "#94a3b8" }} />
              <Bar dataKey="score" radius={[0, 6, 6, 0]} barSize={28}>
                {barData.map((entry) => (
                  <Cell key={entry.id} fill={STRATEGY_COLORS[entry.id] ?? "#6366f1"} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>

          {/* Outcome Distribution per Strategy */}
          <h3 className="text-sm font-semibold text-gray-700 mt-6 mb-3">전략별 결과 분포</h3>
          <div className="space-y-3">
            {outcomeByStrategy.map((os) => (
              <div key={os.sid}>
                <div className="flex items-center gap-2 mb-1">
                  <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: STRATEGY_COLORS[os.sid] ?? "#6366f1" }} />
                  <span className="text-xs font-medium text-gray-700">{os.strategy}</span>
                  <span className="text-xs text-gray-400">({os.total}건)</span>
                </div>
                <div className="flex h-5 rounded-full overflow-hidden bg-gray-100">
                  {Object.entries(os.outcomes).map(([outcome, count]) => {
                    const pct = (count / os.total) * 100;
                    return pct > 0 ? (
                      <div
                        key={outcome}
                        className="h-full flex items-center justify-center text-[10px] font-bold text-white transition-all"
                        style={{
                          width: `${pct}%`,
                          backgroundColor: OUTCOME_COLORS[outcome] ?? "#94a3b8",
                          minWidth: count > 0 ? "24px" : 0,
                        }}
                        title={`${outcome}: ${count}`}
                      >
                        {count}
                      </div>
                    ) : null;
                  })}
                </div>
              </div>
            ))}
            {/* Legend */}
            <div className="flex flex-wrap gap-3 mt-2">
              {Object.entries(OUTCOME_COLORS).map(([k, c]) => (
                <div key={k} className="flex items-center gap-1">
                  <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: c }} />
                  <span className="text-[10px] text-gray-500">{k}</span>
                </div>
              ))}
            </div>
          </div>
        </Card>
      </div>

      {/* Strategy Cards with Hypothesis */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
        {strategies.map((s) => {
          const score = summary.strategy_scores[s.strategy_id] ?? 0;
          const rank = Object.entries(summary.strategy_scores)
            .sort(([, a], [, b]) => b - a)
            .findIndex(([id]) => id === s.strategy_id) + 1;

          return (
            <Card key={s.strategy_id}>
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: STRATEGY_COLORS[s.strategy_id] ?? "#6366f1" }} />
                  <span className="text-sm font-bold text-gray-800">
                    {STRATEGY_LABELS[s.strategy_id] ?? s.strategy_id}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`text-xs px-2 py-0.5 rounded-full font-bold ${scoreColor(score)}`}>
                    {score.toFixed(1)}
                  </span>
                  <span className="text-xs text-gray-400">#{rank}</span>
                </div>
              </div>
              <p className="text-xs text-gray-600 leading-relaxed mb-3">{s.hypothesis}</p>
              <div className="flex flex-wrap gap-1">
                <span className="text-[10px] bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">톤: {s.tone}</span>
              </div>
            </Card>
          );
        })}
      </div>
    </Section>
  );
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// [4] TECHNIQUE EFFECTIVENESS
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
function TechniqueEffectiveness() {
  const techniques = reason.technique_effectiveness;
  if (!techniques) return null;

  const techniqueLabels: Record<string, string> = {
    relative_numbers: "상대적 수치 비교",
    lifestyle_connection: "일상 연결",
    risk_removal: "위험 제거 (환불보장 등)",
    upgrade_framing: "업그레이드 프레이밍",
  };

  const data = Object.entries(techniques)
    .map(([key, val]) => ({
      name: techniqueLabels[key] ?? key,
      key,
      used: val.used,
      avgWhenUsed: val.avg_score_when_used,
      avgWhenNot: val.avg_score_when_not,
      lift: val.avg_score_when_used > 0 ? val.avg_score_when_used - val.avg_score_when_not : 0,
    }))
    .sort((a, b) => b.lift - a.lift);

  return (
    <Section number="03" title="기법 효과성 분석" subtitle="어떤 설득 기법이 점수를 올리는가?" id="techniques">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Comparison Bar */}
        <Card>
          <h3 className="text-sm font-semibold text-gray-700 mb-4">사용 시 vs 미사용 시 평균 점수</h3>
          <div className="space-y-4">
            {data.map((t) => (
              <div key={t.key}>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-medium text-gray-700">{t.name}</span>
                  <span className="text-xs text-gray-400">사용 {t.used}회</span>
                </div>
                <div className="space-y-1">
                  {/* Used bar */}
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] w-12 text-right text-gray-400">사용</span>
                    <div className="flex-1 bg-gray-100 rounded-full h-5 overflow-hidden">
                      <div
                        className="h-full rounded-full flex items-center justify-end pr-2 transition-all"
                        style={{
                          width: `${t.avgWhenUsed > 0 ? Math.max((t.avgWhenUsed / 80) * 100, 5) : 0}%`,
                          backgroundColor: t.used > 0 ? "#6366f1" : "#d1d5db",
                        }}
                      >
                        {t.avgWhenUsed > 0 && (
                          <span className="text-[10px] font-bold text-white">{t.avgWhenUsed.toFixed(1)}</span>
                        )}
                      </div>
                    </div>
                  </div>
                  {/* Not used bar */}
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] w-12 text-right text-gray-400">미사용</span>
                    <div className="flex-1 bg-gray-100 rounded-full h-5 overflow-hidden">
                      <div
                        className="h-full rounded-full flex items-center justify-end pr-2 transition-all"
                        style={{
                          width: `${Math.max((t.avgWhenNot / 80) * 100, 5)}%`,
                          backgroundColor: "#d1d5db",
                        }}
                      >
                        <span className="text-[10px] font-bold text-gray-600">{t.avgWhenNot.toFixed(1)}</span>
                      </div>
                    </div>
                  </div>
                </div>
                {/* Lift indicator */}
                {t.lift > 0 && (
                  <div className="text-right mt-0.5">
                    <span className="text-[10px] font-bold text-emerald-500">
                      +{t.lift.toFixed(1)}점 향상
                    </span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </Card>

        {/* Insight Cards */}
        <Card>
          <h3 className="text-sm font-semibold text-gray-700 mb-4">핵심 인사이트</h3>
          <div className="space-y-3">
            <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-lg">🏆</span>
                <span className="text-sm font-bold text-emerald-700">가장 효과적: 업그레이드 프레이밍</span>
              </div>
              <p className="text-xs text-emerald-600 leading-relaxed">
                사용 시 평균 70.28점 vs 미사용 시 50점 — <strong>+20.28점 향상</strong>.
                기존 제품 대비 "업그레이드"로 프레이밍하면 설득력이 크게 높아집니다.
              </p>
            </div>
            <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-lg">💡</span>
                <span className="text-sm font-bold text-amber-700">미활용 기회: 위험 제거 기법</span>
              </div>
              <p className="text-xs text-amber-600 leading-relaxed">
                risk_removal(환불 보장 등)은 <strong>한 번도 사용되지 않았습니다</strong>.
                Desire→Action 병목을 해결할 핵심 기법으로, 다음 실험에서 반드시 적용해야 합니다.
              </p>
            </div>
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-xl">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-lg">📊</span>
                <span className="text-sm font-bold text-blue-700">높은 효과: 일상 연결 + 상대적 수치</span>
              </div>
              <p className="text-xs text-blue-600 leading-relaxed">
                "커피 한 잔 값"(상대적 수치), "아침 루틴"(일상 연결) 기법을
                사용하면 평균 19~20점 향상됩니다. 두 기법을 조합해 활용하세요.
              </p>
            </div>
          </div>
        </Card>
      </div>
    </Section>
  );
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// [5] EXPERIMENT EVOLUTION
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
function ExperimentEvolution() {
  const chartData = trendData.map((d, i) => ({
    name: i === 0 ? "Baseline" : `실험 ${i}`,
    score: d.avg_score,
    verdict: d.verdict,
    note: d.note,
    run_id: d.run_id,
  }));

  const baseline = trendData[0]?.avg_score ?? 0;

  return (
    <Section number="04" title="실험 진화 과정" subtitle="각 실험에서 무엇을 시도했고, 결과는 어떠했나?" id="experiments">
      <Card>
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={chartData} margin={{ top: 20, right: 30, bottom: 10, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
            <XAxis dataKey="name" tick={{ fontSize: 11, fill: "#6b7280" }} />
            <YAxis domain={[50, 70]} tick={{ fontSize: 11, fill: "#6b7280" }} />
            <Tooltip
              contentStyle={{
                backgroundColor: "#fff",
                border: "1px solid #e5e7eb",
                borderRadius: 12,
                fontSize: 12,
                boxShadow: "0 4px 6px rgba(0,0,0,0.07)",
              }}
              formatter={(value) => [`${Number(value).toFixed(2)}점`, "평균 점수"]}
              labelFormatter={(_label, payload) => {
                const item = (payload as unknown as Array<{ payload?: { note?: string } }>)?.[0]?.payload;
                return item?.note ?? "";
              }}
            />
            <ReferenceLine
              y={baseline}
              stroke="#6366f1"
              strokeDasharray="5 5"
              label={{ value: `Baseline ${baseline}`, position: "right", fontSize: 10, fill: "#6366f1" }}
            />
            <Line
              type="monotone"
              dataKey="score"
              stroke="#6366f1"
              strokeWidth={3}
              dot={(props) => {
                const { cx, cy, payload, index } = props as { cx?: number; cy?: number; payload?: { verdict?: string }; index?: number };
                if (cx == null || cy == null) return <circle key={index} />;
                const isKeep = payload?.verdict === "keep";
                return (
                  <circle
                    key={index}
                    cx={cx}
                    cy={cy}
                    r={7}
                    fill={isKeep ? "#10b981" : "#ef4444"}
                    stroke="#fff"
                    strokeWidth={2}
                  />
                );
              }}
              activeDot={{ r: 9 }}
            />
          </LineChart>
        </ResponsiveContainer>

        {/* Experiment Timeline */}
        <div className="mt-6 relative">
          <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200" />
          <div className="space-y-4">
            {trendData.map((d, i) => {
              const isKeep = d.verdict === "keep";
              const delta = d.avg_score - baseline;
              return (
                <div key={d.run_id} className="flex items-start gap-4 ml-0">
                  <div className={`w-9 h-9 rounded-full flex items-center justify-center text-xs font-bold text-white z-10 shrink-0 ${isKeep ? "bg-emerald-500" : "bg-red-400"}`}>
                    {i === 0 ? "B" : `E${i}`}
                  </div>
                  <div className={`flex-1 p-3 rounded-xl border ${isKeep ? "bg-emerald-50 border-emerald-200" : "bg-gray-50 border-gray-200"}`}>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-bold text-gray-800">
                        {i === 0 ? "Baseline" : d.note}
                      </span>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-gray-700">{d.avg_score.toFixed(2)}점</span>
                        {i > 0 && (
                          <span className={`text-xs font-bold ${delta >= 0 ? "text-emerald-500" : "text-red-500"}`}>
                            {delta >= 0 ? "+" : ""}{delta.toFixed(2)}
                          </span>
                        )}
                        <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${isKeep ? "bg-emerald-100 text-emerald-700" : "bg-red-100 text-red-600"}`}>
                          {isKeep ? "KEEP" : "DISCARD"}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </Card>
    </Section>
  );
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// [6] WINNING & LOSING PATTERNS
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
function Patterns() {
  return (
    <Section number="05" title="승패 패턴 분석" subtitle="성공/실패한 대화에서 어떤 차이가 있었나?" id="patterns">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Winning */}
        <Card>
          <div className="flex items-center gap-2 mb-4">
            <span className="text-xl">✅</span>
            <h3 className="text-sm font-bold text-emerald-700">성공 패턴</h3>
          </div>
          <div className="space-y-3">
            {reason.winning_patterns.map((p, i) => (
              <div key={i} className="flex items-start gap-3">
                <span className="text-xs font-bold text-emerald-500 bg-emerald-100 w-6 h-6 rounded-full flex items-center justify-center shrink-0 mt-0.5">
                  {i + 1}
                </span>
                <p className="text-xs text-gray-700 leading-relaxed">{p}</p>
              </div>
            ))}
          </div>
        </Card>

        {/* Losing */}
        <Card>
          <div className="flex items-center gap-2 mb-4">
            <span className="text-xl">❌</span>
            <h3 className="text-sm font-bold text-red-700">실패 패턴</h3>
          </div>
          <div className="space-y-3">
            {reason.losing_patterns.map((p, i) => (
              <div key={i} className="flex items-start gap-3">
                <span className="text-xs font-bold text-red-500 bg-red-100 w-6 h-6 rounded-full flex items-center justify-center shrink-0 mt-0.5">
                  {i + 1}
                </span>
                <p className="text-xs text-gray-700 leading-relaxed">{p}</p>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Cluster Insights */}
      <div className="mt-6">
        <Card>
          <h3 className="text-sm font-bold text-gray-700 mb-4">💡 전략별 핵심 인사이트</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {Object.entries(reason.cluster_insights).map(([key, insight]) => (
              <div key={key} className="p-4 rounded-xl border border-gray-100 bg-gray-50">
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: STRATEGY_COLORS[key] ?? "#6366f1" }} />
                  <span className="text-xs font-bold text-gray-800">
                    {STRATEGY_LABELS[key] ?? key.replace("strategy-", "")}
                  </span>
                </div>
                <p className="text-xs text-gray-600 leading-relaxed">{insight}</p>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </Section>
  );
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// [7] CONVERSATION VIEWER (Collapsible)
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
function ConversationViewer() {
  const ids = getAvailableTranscriptIds();
  const [selectedId, setSelectedId] = useState<string>(ids[0] ?? "");
  const [transcript, setTranscript] = useState<Transcript | null>(loadTranscript(ids[0] ?? ""));
  const [isOpen, setIsOpen] = useState(false);

  const handleSelect = (id: string) => {
    setSelectedId(id);
    setTranscript(loadTranscript(id));
  };

  return (
    <Section number="06" title="대화 상세 보기" subtitle="실제 시뮬레이션 대화를 확인합니다" id="conversations">
      <Card>
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="w-full flex items-center justify-between py-2"
        >
          <span className="text-sm font-semibold text-gray-700">💬 대화 내용 펼치기</span>
          <span className="text-gray-400 text-lg">{isOpen ? "▲" : "▼"}</span>
        </button>

        {isOpen && (
          <div className="mt-4">
            {/* Selector */}
            <div className="flex flex-wrap gap-2 mb-4">
              {ids.map((id) => {
                const parts = id.replace("conv-", "").split("-");
                const personaId = parts[parts.length - 1];
                const strategyKey = parts.slice(0, -1).join("-");

                return (
                  <button
                    key={id}
                    onClick={() => handleSelect(id)}
                    className={`text-xs px-3 py-1.5 rounded-full border transition-all ${
                      selectedId === id
                        ? "text-white border-indigo-600 shadow-sm"
                        : "bg-white text-gray-600 border-gray-200 hover:border-indigo-300"
                    }`}
                    style={selectedId === id ? { backgroundColor: STRATEGY_COLORS[`strategy-${strategyKey}`] ?? "#6366f1" } : {}}
                  >
                    {STRATEGY_LABELS[`strategy-${strategyKey}`]?.slice(0, 4) ?? strategyKey} · {personaId}
                  </button>
                );
              })}
            </div>

            {/* Chat */}
            {transcript && (
              <div className="bg-gray-50 rounded-xl p-4 max-h-[500px] overflow-y-auto space-y-3">
                <div className="flex items-center gap-3 pb-3 border-b border-gray-200 mb-3">
                  <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: STRATEGY_COLORS[transcript.strategy_id] ?? "#6366f1" }} />
                  <span className="text-xs font-semibold text-gray-700">
                    {STRATEGY_LABELS[transcript.strategy_id] ?? transcript.strategy_id}
                  </span>
                  <span className="text-xs text-gray-400">·</span>
                  <span className="text-xs text-gray-500">페르소나: {transcript.persona_id}</span>
                  <span className="text-xs text-gray-400">·</span>
                  <span className="text-xs text-gray-400">종료: {transcript.ended_by}</span>
                </div>

                {transcript.turns.map((turn, i) => (
                  <div key={i} className={`flex ${turn.role === "agent" ? "justify-start" : "justify-end"}`}>
                    <div
                      className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                        turn.role === "agent"
                          ? "bg-indigo-100 text-indigo-900 rounded-bl-sm"
                          : "bg-white border border-gray-200 text-gray-800 rounded-br-sm shadow-sm"
                      }`}
                    >
                      <span className={`block text-[10px] font-semibold mb-1 ${turn.role === "agent" ? "text-indigo-400" : "text-gray-400"}`}>
                        {turn.role === "agent" ? "🤖 세일즈 에이전트" : "👤 고객 페르소나"}
                      </span>
                      {turn.content}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </Card>
    </Section>
  );
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// [7+] EVALUATION TABLE (Collapsible)
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
function EvaluationTable() {
  const [isOpen, setIsOpen] = useState(false);
  const [sortBy, setSortBy] = useState<"total" | "engagement" | "persuasion" | "purchase_intent">("total");
  const sorted = useMemo(() => [...evaluations].sort((a, b) => b.scores[sortBy] - a.scores[sortBy]), [sortBy]);

  const FUNNEL_LABELS: Record<number, string> = {
    0: "Attention",
    1: "Interest",
    2: "Desire",
    3: "Action",
  };

  return (
    <Section number="07" title="평가 상세 데이터" subtitle="개별 대화 세션의 점수를 확인합니다" id="details">
      <Card>
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="w-full flex items-center justify-between py-2"
        >
          <span className="text-sm font-semibold text-gray-700">📊 전체 평가 테이블 펼치기 ({evaluations.length}건)</span>
          <span className="text-gray-400 text-lg">{isOpen ? "▲" : "▼"}</span>
        </button>

        {isOpen && (
          <div className="mt-4">
            {/* Sort buttons */}
            <div className="flex gap-2 mb-3">
              {(["total", "engagement", "persuasion", "purchase_intent"] as const).map((key) => {
                const labels: Record<string, string> = {
                  total: "종합",
                  engagement: "참여도",
                  persuasion: "설득력",
                  purchase_intent: "구매의도",
                };
                return (
                  <button
                    key={key}
                    onClick={() => setSortBy(key)}
                    className={`text-xs px-3 py-1.5 rounded-full border transition-all ${
                      sortBy === key
                        ? "bg-indigo-600 text-white border-indigo-600"
                        : "bg-white text-gray-600 border-gray-200 hover:border-indigo-300"
                    }`}
                  >
                    {labels[key]}
                  </button>
                );
              })}
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="border-b border-gray-200 text-left text-gray-500">
                    <th className="pb-2 pr-3">전략</th>
                    <th className="pb-2 pr-3">페르소나</th>
                    <th className="pb-2 pr-3 text-center">참여</th>
                    <th className="pb-2 pr-3 text-center">관련성</th>
                    <th className="pb-2 pr-3 text-center">설득</th>
                    <th className="pb-2 pr-3 text-center">구매의도</th>
                    <th className="pb-2 pr-3 text-center">종합</th>
                    <th className="pb-2 pr-3">결과</th>
                    <th className="pb-2 pr-3">퍼널</th>
                  </tr>
                </thead>
                <tbody>
                  {sorted.map((ev) => (
                    <tr key={ev.session_id} className="border-b border-gray-50 hover:bg-indigo-50/30 transition-colors">
                      <td className="py-2.5 pr-3">
                        <div className="flex items-center gap-1.5">
                          <div className="w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: STRATEGY_COLORS[ev.strategy_id] ?? "#6366f1" }} />
                          <span className="text-gray-700 font-medium">
                            {STRATEGY_LABELS[ev.strategy_id]?.slice(0, 6) ?? ev.strategy_id.replace("strategy-", "")}
                          </span>
                        </div>
                      </td>
                      <td className="py-2.5 pr-3 font-mono text-gray-500">{ev.persona_id}</td>
                      <td className="py-2.5 pr-3 text-center">{ev.scores.engagement}</td>
                      <td className="py-2.5 pr-3 text-center">{ev.scores.relevance}</td>
                      <td className="py-2.5 pr-3 text-center">{ev.scores.persuasion}</td>
                      <td className="py-2.5 pr-3 text-center">{ev.scores.purchase_intent}</td>
                      <td className="py-2.5 pr-3 text-center">
                        <span className={`inline-block px-2 py-0.5 rounded text-xs font-bold ${scoreColor(ev.scores.total)}`}>
                          {ev.scores.total}
                        </span>
                      </td>
                      <td className="py-2.5 pr-3">
                        <span
                          className="inline-block px-2 py-0.5 rounded-full text-[10px] font-medium"
                          style={{
                            backgroundColor: (OUTCOME_COLORS[ev.outcome] ?? "#94a3b8") + "18",
                            color: OUTCOME_COLORS[ev.outcome] ?? "#94a3b8",
                          }}
                        >
                          {ev.outcome}
                        </span>
                      </td>
                      <td className="py-2.5 pr-3 text-xs text-gray-500">
                        {FUNNEL_LABELS[ev.funnel_progress] ?? ev.funnel_progress}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </Card>
    </Section>
  );
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// NAV
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
function SideNav() {
  const navItems = [
    { id: "funnel", label: "퍼널 분석", num: "01" },
    { id: "strategies", label: "전략 비교", num: "02" },
    { id: "techniques", label: "기법 효과", num: "03" },
    { id: "experiments", label: "실험 진화", num: "04" },
    { id: "patterns", label: "승패 패턴", num: "05" },
    { id: "conversations", label: "대화 보기", num: "06" },
    { id: "details", label: "상세 데이터", num: "07" },
  ];

  return (
    <nav className="hidden xl:block fixed left-4 top-1/2 -translate-y-1/2 z-20">
      <div className="bg-white/80 backdrop-blur-sm border border-gray-200 rounded-2xl p-2 shadow-lg">
        {navItems.map((item) => (
          <a
            key={item.id}
            href={`#${item.id}`}
            className="flex items-center gap-2 px-3 py-2 rounded-xl text-xs text-gray-500 hover:text-indigo-600 hover:bg-indigo-50 transition-all"
          >
            <span className="font-mono text-[10px] text-indigo-400">{item.num}</span>
            <span>{item.label}</span>
          </a>
        ))}
      </div>
    </nav>
  );
}

// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
// MAIN APP
// ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
export default function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Side Navigation */}
      <SideNav />

      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-30">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
              <span className="text-white text-sm font-bold">N</span>
            </div>
            <div>
              <h1 className="text-base font-bold text-gray-900">NUDGE 세일즈 시뮬레이션</h1>
              <p className="text-[10px] text-gray-400">AI 영양제 판매 대화 최적화 실험 대시보드</p>
            </div>
          </div>
          <div className="flex items-center gap-4 text-xs text-gray-400">
            <span>실험 {trendData.length}회</span>
            <span>·</span>
            <span>평가 {evaluations.length}건</span>
            <span>·</span>
            <span>전략 {strategies.length}개</span>
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <ExecutiveHero />
        <FunnelAnalysis />
        <StrategyComparison />
        <TechniqueEffectiveness />
        <ExperimentEvolution />
        <Patterns />
        <ConversationViewer />
        <EvaluationTable />
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between text-xs text-gray-400">
          <span>NUDGE Team · 주현우 · 임승현 · 이재윤</span>
          <span>Built with React + Recharts + Tailwind CSS</span>
        </div>
      </footer>
    </div>
  );
}
