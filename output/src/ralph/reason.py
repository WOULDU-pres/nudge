"""R (Reason) — 패턴 분석."""
from __future__ import annotations

import logging
from src.llm import call_llm, parse_json_response
from src.evaluation.schema import EvaluationResult
from src.conversation.turn import ConversationSession

logger = logging.getLogger("ralphthon.ralph.reason")

REASON_SYSTEM = """당신은 세일즈 대화 분석 전문가입니다.

## 지시

상위 점수 대화와 하위 점수 대화를 비교 분석하여 패턴을 발견하세요.

반드시 아래 JSON 형식으로 응답하세요:

```json
{
  "winning_patterns": [
    "상위 대화에서 공통적으로 발견되는 패턴 (구체적으로)"
  ],
  "losing_patterns": [
    "하위 대화에서 공통적으로 발견되는 패턴 (구체적으로)"
  ],
  "cluster_insights": {
    "클러스터명": "해당 클러스터에 대한 인사이트"
  }
}
```

## 분석 원칙

- 구체적으로. "좋았다/나빴다"가 아니라 "어떤 표현이, 어떤 유형의 고객에게, 왜 효과적이었는지".
- 클러스터별 차이를 반드시 확인.
- 에이전트의 첫 턴이 결과에 미친 영향을 분석.
- 반론 대응이 있었다면 그 효과를 분석.
"""


async def reason(
    evaluations: list[EvaluationResult],
    sessions: list[ConversationSession],
    personas: list[dict],
) -> dict:
    """상위/하위 대화 비교 분석.

    Returns:
        {"winning_patterns": [...], "losing_patterns": [...], "cluster_insights": {...}}
    """
    if not evaluations:
        return {"winning_patterns": [], "losing_patterns": [], "cluster_insights": {}}

    # Sort by total score
    sorted_evals = sorted(evaluations, key=lambda e: e.scores.total, reverse=True)
    top_n = max(3, len(sorted_evals) // 5)  # top 20% or at least 3
    top_evals = sorted_evals[:top_n]
    bottom_evals = sorted_evals[-top_n:]

    # Build session lookup
    session_map = {s.session_id: s for s in sessions}
    persona_map = {p["id"]: p for p in personas}

    def _format_eval(ev: EvaluationResult) -> str:
        sess = session_map.get(ev.session_id)
        persona = persona_map.get(ev.persona_id, {})
        cluster = ", ".join(persona.get("cluster_tags", []))
        transcript = ""
        if sess:
            for turn in sess.turns[:4]:  # First 4 turns for brevity
                role = "세일즈" if turn.role == "agent" else "고객"
                transcript += f"  {role}: {turn.content[:150]}...\n"
        return (
            f"[{ev.strategy_id} × {ev.persona_id} (클러스터: {cluster})] "
            f"total={ev.scores.total}, outcome={ev.outcome}\n{transcript}"
        )

    top_text = "\n".join(_format_eval(e) for e in top_evals)
    bottom_text = "\n".join(_format_eval(e) for e in bottom_evals)

    user_msg = f"### 상위 점수 대화 (TOP)\n{top_text}\n\n### 하위 점수 대화 (BOTTOM)\n{bottom_text}"

    raw = await call_llm(
        system_prompt=REASON_SYSTEM,
        user_message=user_msg,
        temperature=0.3,
        model_tier="expensive",
    )

    if "[LLM ERROR]" in raw:
        logger.warning(f"Reason LLM error: {raw[:200]}")
        return {"winning_patterns": [], "losing_patterns": [], "cluster_insights": {}}

    parsed = parse_json_response(raw)
    if parsed is None:
        logger.warning("Reason JSON parse failed")
        return {"winning_patterns": [], "losing_patterns": [], "cluster_insights": {}}

    return {
        "winning_patterns": parsed.get("winning_patterns", []),
        "losing_patterns": parsed.get("losing_patterns", []),
        "cluster_insights": parsed.get("cluster_insights", {}),
    }
