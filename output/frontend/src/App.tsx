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
  PieChart,
  Pie,
  Legend,
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

// ── Helpers ──────────────────────────────────────────────
function scoreColor(score: number): string {
  if (score >= 80) return "bg-emerald-500 text-white";
  if (score >= 70) return "bg-emerald-300 text-emerald-900";
  if (score >= 60) return "bg-yellow-300 text-yellow-900";
  if (score >= 50) return "bg-orange-300 text-orange-900";
  return "bg-red-400 text-white";
}

function scoreBgOnly(score: number): string {
  if (score >= 80) return "#10b981";
  if (score >= 70) return "#6ee7b7";
  if (score >= 60) return "#fde047";
  if (score >= 50) return "#fdba74";
  return "#f87171";
}

const OUTCOME_COLORS: Record<string, string> = {
  converted: "#10b981",
  interested: "#06b6d4",
  neutral: "#a3a3a3",
  resistant: "#f97316",
  lost: "#ef4444",
  error: "#7c3aed",
};

const FUNNEL_LABELS: Record<string, string> = {
  "0": "Attention",
  "1": "Interest",
  "2": "Desire",
  "3": "Action",
};

const FUNNEL_COLORS = ["#e5e7eb", "#93c5fd", "#6366f1", "#10b981"];

// ── Card wrapper ─────────────────────────────────────────
function Card({ title, children, className = "" }: { title: string; children: React.ReactNode; className?: string }) {
  return (
    <div className={`bg-white shadow-sm border border-gray-200 rounded-lg p-6 ${className}`}>
      <h2 className="text-lg font-semibold text-gray-800 mb-4">{title}</h2>
      {children}
    </div>
  );
}

// ── A. Strategy Leaderboard ──────────────────────────────
function StrategyLeaderboard() {
  const sorted = Object.entries(summary.strategy_scores).sort(([, a], [, b]) => b - a);
  return (
    <Card title="🏆 Strategy Leaderboard">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200 text-left text-gray-500">
              <th className="pb-2 pr-4">Rank</th>
              <th className="pb-2 pr-4">Strategy</th>
              <th className="pb-2 pr-4">Avg Score</th>
              <th className="pb-2 pr-4">Hypothesis</th>
            </tr>
          </thead>
          <tbody>
            {sorted.map(([id, score], i) => {
              const strat = strategies.find((s) => s.strategy_id === id);
              return (
                <tr key={id} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 pr-4 font-mono text-gray-400">#{i + 1}</td>
                  <td className="py-3 pr-4 font-medium text-indigo-700">{id.replace("strategy-", "")}</td>
                  <td className="py-3 pr-4">
                    <span className={`inline-block px-2 py-0.5 rounded text-xs font-bold ${scoreColor(score)}`}>{score.toFixed(1)}</span>
                  </td>
                  <td className="py-3 pr-4 text-gray-600 max-w-md truncate">{strat?.hypothesis ?? "—"}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </Card>
  );
}

// ── B. Heatmap ───────────────────────────────────────────
function Heatmap() {
  const strategyIds = Object.keys(summary.strategy_cluster_matrix);
  const clusterIds = Array.from(new Set(strategyIds.flatMap((s) => Object.keys(summary.strategy_cluster_matrix[s]))));

  return (
    <Card title="🔥 Strategy × Cluster Heatmap">
      <div className="overflow-x-auto">
        <div className="inline-grid gap-1" style={{ gridTemplateColumns: `140px repeat(${clusterIds.length}, 1fr)` }}>
          {/* header row */}
          <div />
          {clusterIds.map((c) => (
            <div key={c} className="text-xs font-medium text-gray-500 text-center px-2 pb-1 truncate">
              {c}
            </div>
          ))}
          {/* data rows */}
          {strategyIds.map((s) => (
            <>
              <div key={`label-${s}`} className="text-xs font-medium text-gray-700 flex items-center truncate pr-2">
                {s.replace("strategy-", "")}
              </div>
              {clusterIds.map((c) => {
                const val = summary.strategy_cluster_matrix[s]?.[c];
                return (
                  <div
                    key={`${s}-${c}`}
                    className="rounded flex items-center justify-center text-xs font-bold min-w-[60px] h-10"
                    style={{ backgroundColor: val != null ? scoreBgOnly(val) : "#f3f4f6" }}
                  >
                    {val != null ? val.toFixed(1) : "—"}
                  </div>
                );
              })}
            </>
          ))}
        </div>
        {/* legend */}
        <div className="flex items-center gap-2 mt-3 text-xs text-gray-500">
          <span>Low</span>
          {[
            ["#f87171", "<50"],
            ["#fdba74", "50-59"],
            ["#fde047", "60-69"],
            ["#6ee7b7", "70-79"],
            ["#10b981", "80+"],
          ].map(([bg, label]) => (
            <div key={label} className="flex items-center gap-1">
              <span className="inline-block w-4 h-3 rounded" style={{ backgroundColor: bg }} />
              <span>{label}</span>
            </div>
          ))}
          <span>High</span>
        </div>
      </div>
    </Card>
  );
}

// ── C. Cluster Insights ──────────────────────────────────
function ClusterInsights() {
  return (
    <Card title="🔍 Cluster Insights">
      <div className="space-y-4">
        {Object.entries(reason.cluster_insights).map(([key, insight]) => (
          <div key={key} className="border-l-4 border-indigo-400 pl-4">
            <h3 className="text-sm font-semibold text-indigo-700 mb-1">{key.replace("strategy-", "")}</h3>
            <p className="text-sm text-gray-600 leading-relaxed">{insight}</p>
          </div>
        ))}
      </div>
    </Card>
  );
}

// ── D. Experiment Trend ──────────────────────────────────
function ExperimentTrend() {
  const chartData = trendData.map((d, i) => ({
    name: `Exp ${i}`,
    score: d.avg_score,
    verdict: d.verdict,
    note: d.note,
  }));

  return (
    <Card title="📈 Experiment Trend">
      <ResponsiveContainer width="100%" height={260}>
        <LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="name" tick={{ fontSize: 12 }} />
          <YAxis domain={[50, 70]} tick={{ fontSize: 12 }} />
          <Tooltip
            contentStyle={{ backgroundColor: "#fff", border: "1px solid #e5e7eb", borderRadius: 8, fontSize: 12 }}
            formatter={(value) => [Number(value).toFixed(2), "Avg Score"]}
            labelFormatter={(_label, payload) => {
              const item = payload?.[0]?.payload as { note?: string } | undefined;
              return item?.note ?? "";
            }}
          />
          <Line type="monotone" dataKey="score" stroke="#6366f1" strokeWidth={2} dot={{ r: 5, fill: "#6366f1" }} activeDot={{ r: 7 }} />
        </LineChart>
      </ResponsiveContainer>
      {/* Verdict badges */}
      <div className="flex flex-wrap gap-2 mt-3">
        {trendData.map((d, i) => (
          <span
            key={d.run_id}
            className={`text-xs px-2 py-1 rounded-full font-medium ${d.verdict === "keep" ? "bg-emerald-100 text-emerald-700" : "bg-red-100 text-red-700"}`}
          >
            Exp {i}: {d.verdict}
          </span>
        ))}
      </div>
    </Card>
  );
}

// ── E. Conversation Viewer ───────────────────────────────
function ConversationViewer() {
  const ids = getAvailableTranscriptIds();
  const [selectedId, setSelectedId] = useState<string>(ids[0] ?? "");
  const [transcript, setTranscript] = useState<Transcript | null>(loadTranscript(ids[0] ?? ""));

  const handleSelect = (id: string) => {
    setSelectedId(id);
    setTranscript(loadTranscript(id));
  };

  return (
    <Card title="💬 Conversation Viewer" className="lg:col-span-2">
      {/* selector */}
      <div className="flex flex-wrap gap-2 mb-4">
        {ids.map((id) => (
          <button
            key={id}
            onClick={() => handleSelect(id)}
            className={`text-xs px-3 py-1.5 rounded-full border transition-colors ${
              selectedId === id ? "bg-indigo-600 text-white border-indigo-600" : "bg-white text-gray-600 border-gray-300 hover:border-indigo-400"
            }`}
          >
            {id.replace("conv-", "")}
          </button>
        ))}
      </div>
      {/* chat */}
      {transcript && (
        <div className="bg-gray-50 rounded-lg p-4 max-h-96 overflow-y-auto space-y-3">
          <div className="text-xs text-gray-400 mb-2">
            Strategy: {transcript.strategy_id} · Persona: {transcript.persona_id} · Ended by: {transcript.ended_by}
          </div>
          {transcript.turns.map((turn, i) => (
            <div key={i} className={`flex ${turn.role === "agent" ? "justify-start" : "justify-end"}`}>
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
                  turn.role === "agent" ? "bg-indigo-100 text-indigo-900 rounded-bl-sm" : "bg-cyan-100 text-cyan-900 rounded-br-sm"
                }`}
              >
                <span className="block text-xs font-semibold mb-1 opacity-60">{turn.role === "agent" ? "🤖 Agent" : "👤 Persona"}</span>
                {turn.content}
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}

// ── F. Outcome Distribution ──────────────────────────────
function OutcomeDistribution() {
  const data = Object.entries(summary.outcome_distribution)
    .filter(([, v]) => v > 0)
    .map(([name, value]) => ({ name, value }));

  return (
    <Card title="🎯 Outcome Distribution">
      <ResponsiveContainer width="100%" height={260}>
        <PieChart>
          <Pie data={data} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={90} label={(props) => `${props.name ?? ""}: ${props.value ?? ""}`}>
            {data.map((entry) => (
              <Cell key={entry.name} fill={OUTCOME_COLORS[entry.name] ?? "#a3a3a3"} />
            ))}
          </Pie>
          <Tooltip />
          <Legend wrapperStyle={{ fontSize: 12 }} />
        </PieChart>
      </ResponsiveContainer>
    </Card>
  );
}

// ── G. Funnel Distribution ───────────────────────────────
function FunnelDistribution() {
  const data = Object.entries(summary.funnel_distribution).map(([stage, count]) => ({
    stage: FUNNEL_LABELS[stage] ?? `Stage ${stage}`,
    count,
    stageNum: Number(stage),
  }));

  return (
    <Card title="🔻 Funnel Distribution">
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={data} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="stage" tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip contentStyle={{ backgroundColor: "#fff", border: "1px solid #e5e7eb", borderRadius: 8, fontSize: 12 }} />
          <Bar dataKey="count" radius={[6, 6, 0, 0]}>
            {data.map((entry) => (
              <Cell key={entry.stage} fill={FUNNEL_COLORS[entry.stageNum] ?? "#6366f1"} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </Card>
  );
}

// ── H. Winning & Losing Patterns ─────────────────────────
function Patterns() {
  return (
    <Card title="📋 Winning & Losing Patterns" className="lg:col-span-2">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 className="text-sm font-semibold text-emerald-700 mb-2">✅ Winning Patterns</h3>
          <ul className="space-y-2">
            {reason.winning_patterns.map((p, i) => (
              <li key={i} className="text-sm text-gray-600 leading-relaxed bg-emerald-50 border border-emerald-200 rounded-lg p-3">
                {p}
              </li>
            ))}
          </ul>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-red-700 mb-2">❌ Losing Patterns</h3>
          <ul className="space-y-2">
            {reason.losing_patterns.map((p, i) => (
              <li key={i} className="text-sm text-gray-600 leading-relaxed bg-red-50 border border-red-200 rounded-lg p-3">
                {p}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </Card>
  );
}

// ── I. Evaluation Details ────────────────────────────────
function EvaluationDetails() {
  const [sortBy, setSortBy] = useState<"total" | "engagement" | "persuasion" | "purchase_intent">("total");
  const sorted = useMemo(() => [...evaluations].sort((a, b) => b.scores[sortBy] - a.scores[sortBy]), [sortBy]);

  return (
    <Card title="📊 Evaluation Details" className="lg:col-span-2">
      <div className="flex gap-2 mb-3">
        {(["total", "engagement", "persuasion", "purchase_intent"] as const).map((key) => (
          <button
            key={key}
            onClick={() => setSortBy(key)}
            className={`text-xs px-3 py-1 rounded-full border transition-colors ${
              sortBy === key ? "bg-indigo-600 text-white border-indigo-600" : "bg-white text-gray-600 border-gray-300 hover:border-indigo-400"
            }`}
          >
            {key.replace("_", " ")}
          </button>
        ))}
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-gray-200 text-left text-gray-500">
              <th className="pb-2 pr-3">Session</th>
              <th className="pb-2 pr-3">Strategy</th>
              <th className="pb-2 pr-3">Persona</th>
              <th className="pb-2 pr-3">Eng</th>
              <th className="pb-2 pr-3">Rel</th>
              <th className="pb-2 pr-3">Per</th>
              <th className="pb-2 pr-3">PI</th>
              <th className="pb-2 pr-3">Total</th>
              <th className="pb-2 pr-3">Outcome</th>
              <th className="pb-2 pr-3">Funnel</th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((ev) => (
              <tr key={ev.session_id} className="border-b border-gray-50 hover:bg-gray-50">
                <td className="py-2 pr-3 font-mono text-gray-500">{ev.session_id.replace("conv-", "").slice(0, 25)}</td>
                <td className="py-2 pr-3 text-indigo-700">{ev.strategy_id.replace("strategy-", "")}</td>
                <td className="py-2 pr-3">{ev.persona_id}</td>
                <td className="py-2 pr-3 text-center">{ev.scores.engagement}</td>
                <td className="py-2 pr-3 text-center">{ev.scores.relevance}</td>
                <td className="py-2 pr-3 text-center">{ev.scores.persuasion}</td>
                <td className="py-2 pr-3 text-center">{ev.scores.purchase_intent}</td>
                <td className="py-2 pr-3">
                  <span className={`inline-block px-2 py-0.5 rounded text-xs font-bold ${scoreColor(ev.scores.total)}`}>{ev.scores.total}</span>
                </td>
                <td className="py-2 pr-3">
                  <span
                    className="inline-block px-2 py-0.5 rounded text-xs font-medium"
                    style={{ backgroundColor: OUTCOME_COLORS[ev.outcome] + "22", color: OUTCOME_COLORS[ev.outcome] }}
                  >
                    {ev.outcome}
                  </span>
                </td>
                <td className="py-2 pr-3 text-center">{FUNNEL_LABELS[String(ev.funnel_progress)] ?? ev.funnel_progress}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}

// ── KPI Summary Bar ──────────────────────────────────────
function KpiBar() {
  const kpis = [
    { label: "Avg Score", value: summary.avg_score.toFixed(1), color: "text-indigo-600" },
    { label: "Coverage", value: `${summary.cluster_coverage}%`, color: "text-emerald-600" },
    { label: "Best Strategy", value: summary.best_strategy.replace("strategy-", ""), color: "text-cyan-600" },
    { label: "Total Evals", value: String(evaluations.length), color: "text-gray-700" },
    { label: "Experiments", value: String(trendData.length), color: "text-gray-700" },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4 mb-6">
      {kpis.map((k) => (
        <div key={k.label} className="bg-white shadow-sm border border-gray-200 rounded-lg p-4 text-center">
          <div className="text-xs text-gray-500 mb-1">{k.label}</div>
          <div className={`text-xl font-bold ${k.color}`}>{k.value}</div>
        </div>
      ))}
    </div>
  );
}

// ── Main App ─────────────────────────────────────────────
export default function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🧪</span>
            <h1 className="text-xl font-bold text-gray-900">Ralphthon Dashboard</h1>
          </div>
          <span className="text-xs text-gray-400">Sales Conversation Simulation</span>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* KPIs */}
        <KpiBar />

        {/* Grid layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* A. Leaderboard - full width */}
          <div className="lg:col-span-2">
            <StrategyLeaderboard />
          </div>

          {/* B. Heatmap */}
          <Heatmap />

          {/* C. Cluster Insights */}
          <ClusterInsights />

          {/* D. Experiment Trend */}
          <ExperimentTrend />

          {/* F. Outcome Distribution */}
          <OutcomeDistribution />

          {/* G. Funnel Distribution */}
          <FunnelDistribution />

          {/* Placeholder for balance */}
          <Card title="⚡ Funnel Analysis">
            <div className="space-y-2 text-sm text-gray-600">
              {reason.funnel_analysis && (
                <>
                  <div className="flex justify-between">
                    <span>Attention → Interest</span>
                    <span className="font-semibold text-emerald-600">{reason.funnel_analysis.attention_to_interest_rate}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Interest → Desire</span>
                    <span className="font-semibold text-yellow-600">{reason.funnel_analysis.interest_to_desire_rate}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Desire → Action</span>
                    <span className="font-semibold text-red-600">{reason.funnel_analysis.desire_to_action_rate}</span>
                  </div>
                  <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
                    <span className="text-xs font-semibold text-red-700">⚠️ Bottleneck: </span>
                    <span className="text-xs text-red-600">{reason.funnel_analysis.bottleneck_stage}</span>
                  </div>
                </>
              )}
            </div>
          </Card>

          {/* H. Patterns - full width */}
          <Patterns />

          {/* E. Conversation Viewer - full width */}
          <ConversationViewer />

          {/* I. Evaluation Details - full width */}
          <EvaluationDetails />
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 text-center text-xs text-gray-400">Ralphthon Simulation Dashboard · Built with React + Recharts + Tailwind CSS</div>
      </footer>
    </div>
  );
}
