"""Strategy generation / reasoning / learning helpers for acpx-backed v2 loop."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from config.settings import settings
from src.llm import call_llm, extract_json


def load_product(product_path: str = 'config/product.yaml') -> dict:
    with open(product_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_strategy_prompt() -> str:
    local_path = Path('strategy_prompt.md')
    if local_path.exists():
        return local_path.read_text(encoding='utf-8')
    return (Path(settings.prompts_dir) / 'strategy_prompt.md').read_text(encoding='utf-8')


async def hypothesize_strategy(product: dict, previous_learnings: list[str] | None = None, iteration: int = 1) -> dict:
    system_prompt = load_strategy_prompt()
    learnings_text = '\n'.join(f'- {x}' for x in (previous_learnings or [])) or '- 없음'
    user_prompt = (
        f"제품 정보:\n{json.dumps(product, ensure_ascii=False, indent=2)}\n\n"
        f"이전 학습:\n{learnings_text}\n\n"
        f"현재 iteration: {iteration}\n"
        '한국어 세일즈 전략 1개를 JSON으로만 출력하세요. 반드시 strategy_id, hypothesis, tone, funnel을 포함하세요.'
    )
    raw = await call_llm(prompt=user_prompt, system=system_prompt, model=settings.expensive_model)
    parsed = extract_json(raw)
    if isinstance(parsed, list):
        parsed = parsed[0]
    parsed.setdefault('strategy_id', f'iteration-{iteration}-strategy')
    parsed.setdefault('hypothesis', '생활 밀착형 가치 제안')
    parsed.setdefault('tone', '공감적이고 구체적')
    parsed.setdefault('funnel', {
        'attention': {'hook_type': '질문형', 'opening_line_guide': '바쁜 일상과 연결', 'target_emotion': '공감'},
        'interest': {'value_framing': '하루 루틴 단순화', 'information_depth': '핵심만', 'engagement_trigger': '짧은 확인 질문'},
        'desire': {'emotional_driver': '매일 덜 피곤한 느낌', 'proof_type': '구체적 설명', 'objection_preempt': '가격/효과 반론 사전 대응'},
        'action': {'cta_style': '소프트CTA', 'urgency_type': '없음', 'fallback': '추가 정보 제공'},
    })
    return parsed


async def reason_about_iteration(iteration_result: dict) -> dict:
    system_prompt = '당신은 세일즈 시뮬레이션 결과에서 패턴을 추출하는 분석가다. JSON으로만 답하라.'
    user_prompt = json.dumps(iteration_result, ensure_ascii=False, indent=2)
    raw = await call_llm(prompt=user_prompt, system=system_prompt, model=settings.expensive_model)
    try:
        parsed = extract_json(raw)
    except Exception:
        parsed = {}
    parsed.setdefault('winning_patterns', [])
    parsed.setdefault('losing_patterns', [])
    parsed.setdefault('summary', '패턴 분석 완료')
    return parsed


async def learn_from_iteration(reason_output: dict) -> dict:
    system_prompt = '당신은 다음 iteration을 위한 학습 포인트를 뽑아내는 연구자다. JSON으로만 답하라.'
    user_prompt = json.dumps(reason_output, ensure_ascii=False, indent=2)
    raw = await call_llm(prompt=user_prompt, system=system_prompt, model=settings.expensive_model)
    try:
        parsed = extract_json(raw)
    except Exception:
        parsed = {}
    parsed.setdefault('learnings', [])
    parsed.setdefault('next_strategy_hint', '더 생활 맥락과 ROI를 구체화')
    return parsed
