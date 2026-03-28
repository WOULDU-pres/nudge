"""Judge — LLM-as-Judge 4차원 평가."""
from __future__ import annotations

import logging
from src.llm import call_llm, parse_json_response
from src.evaluation.schema import EvaluationResult, Scores
from src.conversation.turn import ConversationSession

logger = logging.getLogger("ralphthon.evaluation")

JUDGE_SYSTEM = """당신은 세일즈 대화 품질을 평가하는 공정한 심사관입니다.

아래 기준으로 0-100 점수를 매기세요:

## 평가 차원 (각 0-25)

1. **engagement** (참여도) 0-25
   - 고객이 대화에 관심을 보였는가?
   - 질문을 했는가? 단답으로만 반응했는가?
   - 대화를 이어가려 했는가?

2. **relevance** (적합성) 0-25
   - 에이전트가 고객의 상황/니즈에 맞게 대응했는가?
   - 고객의 관심사를 파악하고 반영했는가?
   - 고객 유형에 적절한 접근이었는가?

3. **persuasion** (설득력) 0-25
   - 고객의 반론을 효과적으로 다뤘는가?
   - 논리적이고 설득력 있는 근거를 제시했는가?
   - 프레이밍이 효과적이었는가?

4. **purchase_intent** (구매의향) 0-25
   - 대화 끝에 고객이 구매/관심 쪽으로 기울었는가?
   - 구체적인 다음 행동(구매, 추가 문의 등)을 언급했는가?
   - 아니면 명시적으로 거부했는가?

## 출력

반드시 아래 JSON 형식으로만 응답하세요. 다른 텍스트 없이 JSON만:

```json
{
  "engagement": <0-25>,
  "relevance": <0-25>,
  "persuasion": <0-25>,
  "purchase_intent": <0-25>,
  "total": <0-100>,
  "outcome": "<converted|interested|neutral|resistant|lost>",
  "reason": "<한 줄 판정 근거>"
}
```

## outcome 기준

- **converted**: 고객이 구매 의사를 표현함
- **interested**: 관심을 보이고 추가 질문/정보를 요청함
- **neutral**: 특별한 관심도 거부도 없는 중립 반응
- **resistant**: 명시적으로 거부하거나 강한 반감 표현
- **lost**: 대화 중 이탈하거나 무관심 표현

## 채점 원칙

- 공정하게. 편향 없이.
- 고객의 실제 반응을 기준으로. 에이전트의 의도가 아니라 결과를 평가.
- 같은 수준의 대화에는 비슷한 점수를 부여 (일관성).
- JSON 파싱이 가능한 형태로만 출력.
- 한국어 사교적 표현("생각해볼게요" = 대부분 거절) 이해.
"""


async def judge_conversation(
    session: ConversationSession,
    persona_profile: dict | None = None,
) -> EvaluationResult:
    """대화 transcript를 Judge로 채점.

    Returns:
        EvaluationResult (실패 시 0점 fallback)
    """
    # Build transcript text
    transcript_lines = []
    for turn in session.turns:
        role_label = "세일즈" if turn.role == "agent" else "고객"
        transcript_lines.append(f"{role_label}: {turn.content}")
    transcript_text = "\n".join(transcript_lines)

    # Persona context
    persona_context = ""
    if persona_profile:
        summary = persona_profile.get("summary", "")
        cluster = ", ".join(persona_profile.get("cluster_tags", []))
        persona_context = f"\n\n[페르소나 참고: {summary} / 클러스터: {cluster}]"

    user_message = f"아래 세일즈 대화를 평가하세요:\n\n{transcript_text}{persona_context}"

    raw = await call_llm(
        system_prompt=JUDGE_SYSTEM,
        user_message=user_message,
        temperature=0.1,
        model_tier="expensive",
    )

    if "[LLM ERROR]" in raw:
        logger.warning(f"Judge error for {session.session_id}: {raw[:200]}")
        return _zero_result(session, f"LLM error: {raw[:100]}")

    parsed = parse_json_response(raw)
    if parsed is None:
        logger.warning(f"Judge JSON parse fail for {session.session_id}")
        return _zero_result(session, "JSON parse failure")

    try:
        scores = Scores(
            engagement=int(parsed.get("engagement", 0)),
            relevance=int(parsed.get("relevance", 0)),
            persuasion=int(parsed.get("persuasion", 0)),
            purchase_intent=int(parsed.get("purchase_intent", 0)),
            total=int(parsed.get("total", 0)),
        )
        outcome = parsed.get("outcome", "neutral")
        valid_outcomes = {"converted", "interested", "neutral", "resistant", "lost"}
        if outcome not in valid_outcomes:
            outcome = "neutral"

        return EvaluationResult(
            session_id=session.session_id,
            strategy_id=session.strategy_id,
            persona_id=session.persona_id,
            scores=scores,
            outcome=outcome,
            reason=parsed.get("reason", ""),
        )
    except Exception as e:
        logger.warning(f"Judge result parse error: {e}")
        return _zero_result(session, str(e))


def _zero_result(session: ConversationSession, reason: str) -> EvaluationResult:
    return EvaluationResult(
        session_id=session.session_id,
        strategy_id=session.strategy_id,
        persona_id=session.persona_id,
        scores=Scores(),
        outcome="error",
        reason=reason,
    )
