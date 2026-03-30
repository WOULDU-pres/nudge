"""LLM-as-Judge evaluator for v2 acpx/Codex-based transcripts."""

from __future__ import annotations

from pathlib import Path

from config.settings import settings
from src.llm import call_llm, extract_json


def _transcript_text(session: dict) -> str:
    lines = []
    for idx, turn in enumerate(session.get('turns', []), start=1):
        role = '세일즈' if turn.get('role') == 'agent' else '고객'
        lines.append(f'[{idx}] {role}: {turn.get("content", "")}')
    return '\n\n'.join(lines)


async def evaluate_session(session: dict, strategy: dict, persona) -> dict:
    judge_prompt = (Path(settings.prompts_dir) / 'judge-system.md').read_text(encoding='utf-8')
    user_prompt = (
        f"## 전략 정보\n- strategy_id: {strategy.get('strategy_id', 'unknown')}\n"
        f"- hypothesis: {strategy.get('hypothesis', '')}\n"
        f"- tone: {strategy.get('tone', '')}\n\n"
        f"## 페르소나 정보\n- persona_id: {getattr(persona, 'persona_id', 'unknown')}\n"
        f"- archetype: {getattr(persona, 'archetype_name', '')}\n"
        f"- cluster_tags: {', '.join(getattr(persona, 'cluster_tags', []))}\n\n"
        f"## 대화\n{_transcript_text(session)}"
    )
    try:
        raw = await call_llm(prompt=user_prompt, system=judge_prompt, model=settings.expensive_model)
        parsed = extract_json(raw)
        scores = {
            'engagement': max(0, min(25, int(parsed.get('engagement', 0)))),
            'relevance': max(0, min(25, int(parsed.get('relevance', 0)))),
            'persuasion': max(0, min(25, int(parsed.get('persuasion', 0)))),
            'purchase_intent': max(0, min(25, int(parsed.get('purchase_intent', 0)))),
        }
        scores['total'] = sum(scores.values())
        outcome = str(parsed.get('outcome', 'neutral'))
        if outcome not in {'converted', 'interested', 'neutral', 'resistant', 'lost', 'error', 'wishlist'}:
            outcome = 'neutral'
        return {
            'session_id': session.get('session_id', 'unknown'),
            'strategy_id': session.get('strategy_id', 'unknown'),
            'persona_id': session.get('persona_id', 'unknown'),
            'scores': scores,
            'outcome': outcome,
            'reason': str(parsed.get('reason', 'judge completed')),
            'raw_judge': parsed,
        }
    except Exception as exc:
        return {
            'session_id': session.get('session_id', 'unknown'),
            'strategy_id': session.get('strategy_id', 'unknown'),
            'persona_id': session.get('persona_id', 'unknown'),
            'scores': {'engagement': 0, 'relevance': 0, 'persuasion': 0, 'purchase_intent': 0, 'total': 0},
            'outcome': 'error',
            'reason': f'evaluation failed: {exc}',
        }
