import json
from copy import deepcopy
from pathlib import Path

ROOT = Path('/home/hwjoo/01-projects/2026/hwjoo-idea/ralphton')
MASTER = ROOT / 'personas' / 'ralphton-200-personas.json'
PROMPT = ROOT / 'ralphthon-harness' / 'scripts' / 'soul_generation_prompt.md'
SPLIT_SCRIPT = ROOT / 'ralphthon-harness' / 'scripts' / 'split_personas.py'

SUMMARY_PREFIX = {
    'budget_practical_buyer': '가격 대비 효용을 가장 중시하는 실용형 구매자.',
    'busy_convenience_seeker': '복용이 간단하고 루틴에 쉽게 붙는 영양제를 선호하는 편의성 중시형.',
    'skeptical_comparison_buyer': '성분표와 비교 근거가 선명해야 움직이는 검증형 구매자.',
    'emotionally_open_caregiver': '몸 상태와 정서적 안심을 함께 보는 돌봄 민감형 구매자.',
    'premium_status_buyer': '가격보다 원료 품질과 브랜드 격을 중시하는 프리미엄 지향형.',
    'risk_averse_safety_first': '새로움보다 안전성, 인증, 부작용 부담 최소화를 우선하는 신중형 구매자.',
    'trend_sensitive_early_adopter': '새로운 원료와 포뮬러, 트렌드 신호에 민감한 선도형 구매자.',
    'inertia_bound_traditionalist': '익숙한 복용 루틴을 쉽게 바꾸지 않는 관성형 구매자.',
    'overwhelmed_complexity_avoider': '성분과 복용법이 복잡해 보이면 피로감을 느끼는 단순성 선호형.',
    'hard_sell_resistant': '강한 푸시보다 선택권 존중을 원하는 압박 저항형 구매자.',
    'story_driven_dreamer': '수치보다 변화된 생활 장면과 감정 서사에 반응하는 서사형 구매자.',
    'data_rational_analyst': '함량, 근거, 인과 구조를 따지는 분석형 구매자.',
    'family_benefit_prioritizer': '나보다 가족 전체의 컨디션과 생활 이익을 우선하는 가족 중심형 구매자.',
    'career_efficiency_optimizer': '업무 집중력과 피로 관리에 도움이 되는 효율형 구매자.',
    'identity_expressive_buyer': '영양제 선택도 자기 취향과 라이프스타일의 일부로 보는 정체성 표현형 구매자.',
    'deal_hunter': '혜택과 거래 조건이 선명할 때 빠르게 움직이는 딜 민감형 구매자.',
    'relationship_trust_buyer': '제품보다 사람과 태도에서 신뢰를 먼저 보는 관계형 구매자.',
    'autonomy_protective_buyer': '스스로 비교하고 결정할 권리를 중시하는 자율성 보호형 구매자.',
    'low_attention_skimmer': '첫 문장에서 핵심 효능과 적합 대상이 보여야 듣는 저주의력형 구매자.',
    'voice_sensitive_listener': '설명 내용만큼 목소리와 전달감에 민감한 청각 중심형 구매자.',
}

CURRENT_ALTERNATIVE_MAP = {
    '조금 불편하지만 익숙한 기존 방식 유지 중': '조금 불편해도 물, 수면, 식사 같은 기존 루틴으로 버티는 중',
    '익숙하지만 번거로운 수동 방식을 계속 사용': '필요한 제품을 따로 챙겨 먹는 번거로운 루틴을 계속 유지 중',
    '경쟁 제품 또는 수동 루틴 사용 중': '다른 영양제 브랜드나 수동 복용 루틴을 사용 중',
    '임시방편으로 버티는 중': '커피, 에너지드링크, 휴식 같은 임시방편으로 버티는 중',
    '무료 또는 익숙한 저가 대안을 사용 중': '가성비 저가 영양제나 익숙한 기본 제품을 사용 중',
    '기존 프로세스나 경쟁 솔루션을 검토 중': '기존 복용 루틴이나 다른 영양제 브랜드를 비교 검토 중',
    '익숙한 방식 또는 지인의 추천 루틴을 유지 중': '지인이 추천한 기존 영양제나 익숙한 복용 루틴을 유지 중',
    '조직 또는 개인이 쓰는 익숙한 도구 유지 중': '집이나 회사에서 익숙하게 챙겨 먹는 제품 또는 개인 루틴 유지 중',
    '현재 방식에 큰 불만 없이 유지 중': '현재 먹는 제품이나 생활 루틴에 큰 불만 없이 유지 중',
    '저렴하지만 비효율적인 도구를 계속 활용 중': '저렴하지만 성분이나 체감이 애매한 제품을 계속 활용 중',
}

ARCHETYPE_UPDATES = {
    'budget_practical_buyer': {
        'persuasion_triggers': ['price_per_day_value', 'ingredient_value', 'felt_effect_vs_cost'],
        'objection_profile': {
            'trigger_conditions': ['price_presented_without_daily_value', 'benefits_not_tied_to_body_condition', 'formula_feels_irrelevant'],
            'resolution_requirements': ['simple_cost_per_day_explanation', 'specific_body_context', 'clear_difference_from_current_routine'],
        },
        'likely_reaction_style': {
            'if_interested': '하루 섭취 비용과 체감 포인트를 숫자로 다시 확인하려 한다',
            'if_unconvinced': '좋아 보이지만 가격 대비 확신이 없어 보류한다고 말한다',
            'if_annoyed': '말만 길고 성분 설명이 뜬구름 같으면 빠르게 대화를 끝내려 한다',
        },
        'scoring_hints': {
            'purchase_intent_boosts': ['cost_per_day_proof', 'routine_before_after_comparison'],
            'purchase_intent_penalties': ['unclear_value', 'high_price_without_ingredient_context'],
        },
    },
    'busy_convenience_seeker': {
        'persuasion_triggers': ['easy_intake', 'routine_fit', 'simple_next_step'],
        'objection_profile': {
            'trigger_conditions': ['benefit_not_stated_immediately', 'too_many_pills_or_steps', 'explanation_takes_too_long_to_get_to_point'],
            'resolution_requirements': ['benefit_in_first_few_seconds', 'one_clear_intake_path', 'low_friction_routine_story'],
        },
        'likely_reaction_style': {
            'if_interested': '복용법이 간단하면 바로 시작해보려 한다',
            'if_unconvinced': '나중에 보겠다고 하고 바로 이탈한다',
            'if_annoyed': '설명이 길고 복용 단계가 많아 보이면 초반에 관심을 끊는다',
        },
        'scoring_hints': {
            'purchase_intent_boosts': ['quick_win', 'easy_daily_fit'],
            'purchase_intent_penalties': ['high_friction', 'unclear_intake_start'],
        },
    },
    'skeptical_comparison_buyer': {
        'persuasion_triggers': ['ingredient_comparison', 'clear_differentiation', 'specific_body_example'],
        'objection_profile': {
            'trigger_conditions': ['claims_lack_evidence', 'advantage_over_other_supplements_unclear', 'voice_sounds_overly_sales_driven'],
            'resolution_requirements': ['comparison_table', 'realistic_claims', 'specific_evidence_point'],
        },
        'scoring_hints': {
            'purchase_intent_boosts': ['clear_differentiation', 'credible_evidence'],
            'purchase_intent_penalties': ['lack_of_evidence', 'me_too_positioning'],
        },
    },
    'emotionally_open_caregiver': {
        'persuasion_triggers': ['emotional_understanding', 'easy_intake', 'reduced_worry'],
        'objection_profile': {
            'trigger_conditions': ['too_many_ingredients_explained', 'technical_terms_without_help', 'tone_feels_pushy'],
            'resolution_requirements': ['simple_step_by_step_explanation', 'gentle_reassurance', 'one_clear_benefit_at_a_time'],
        },
        'likely_reaction_style': {
            'if_interested': '안심이 되면 천천히 들어보며 복용 장면을 떠올린다',
            'if_unconvinced': '좋아 보이지만 내가 꾸준히 챙길 수 있을지 걱정된다고 말한다',
            'if_annoyed': '부담스럽다고 느끼면 방어적으로 닫힌다',
        },
        'scoring_hints': {
            'purchase_intent_boosts': ['worry_reduction', 'easy_routine_adoption'],
            'purchase_intent_penalties': ['feels_hard_to_keep_up', 'emotional_disconnect'],
        },
    },
    'premium_status_buyer': {
        'persuasion_triggers': ['premium_quality_signal', 'credibility', 'effortless_wellness'],
        'likely_reaction_style': {
            'if_interested': '조용히 긍정하며 더 높은 수준의 원료와 품질 정보를 원한다',
            'if_unconvinced': '브랜드나 제안의 격이 맞지 않는다고 느낀다',
            'if_annoyed': '싸구려 세일즈처럼 느끼면 빠르게 신뢰를 잃는다',
        },
    },
    'risk_averse_safety_first': {
        'objection_profile': {
            'trigger_conditions': ['unclear_body_outcome', 'too_much_novelty', 'missing_safety_explanation'],
        },
        'likely_reaction_style': {
            'if_interested': '부작용 가능성과 안전성을 먼저 확인하려 한다',
            'if_unconvinced': '굳이 위험을 감수할 이유가 없다고 느낀다',
            'if_annoyed': '불확실한 약속이 많으면 경계심이 커진다',
        },
        'scoring_hints': {
            'purchase_intent_penalties': ['unknowns', 'perceived_side_effect_risk'],
        },
    },
    'trend_sensitive_early_adopter': {
        'persuasion_triggers': ['new_formula', 'trend_signal', 'first_mover_advantage'],
    },
    'inertia_bound_traditionalist': {
        'persuasion_triggers': ['easy_transition', 'minimal_change', 'familiar_routine'],
        'objection_profile': {
            'trigger_conditions': ['change_cost_seems_high', 'switching_routine_is_unclear', 'new_routine_feels_disruptive'],
            'resolution_requirements': ['low_transition_cost', 'familiarity_bridge', 'simple_switching_story'],
        },
        'likely_reaction_style': {
            'if_interested': '기존 루틴을 크게 바꾸지 않아도 되는지 확인한다',
            'if_unconvinced': '지금도 괜찮아서 굳이 바꿀 필요 없다고 느낀다',
            'if_annoyed': '변화를 강요받는다고 느끼면 바로 닫힌다',
        },
        'scoring_hints': {
            'purchase_intent_boosts': ['easy_migration', 'familiarity'],
            'purchase_intent_penalties': ['switching_cost', 'routine_disruption'],
        },
    },
    'overwhelmed_complexity_avoider': {
        'objection_profile': {
            'trigger_conditions': ['too_many_ingredients', 'technical_terms_without_context', 'unclear_starting_point'],
        },
        'scoring_hints': {
            'purchase_intent_boosts': ['easy_intake_start', 'confidence_building'],
            'purchase_intent_penalties': ['looks_complicated', 'feels_hard_to_keep_up'],
        },
    },
    'story_driven_dreamer': {
        'likely_reaction_style': {
            'if_interested': '변화된 몸 상태와 생활 장면을 더 구체적으로 상상해본다',
            'if_unconvinced': '좋은 정보지만 마음이 움직이지 않았다고 느낀다',
            'if_annoyed': '기계적인 설명만 이어지면 집중을 놓는다',
        },
    },
    'data_rational_analyst': {
        'likely_reaction_style': {
            'if_interested': '함량과 근거 구조를 다시 검토하려 한다',
            'if_unconvinced': '주장이 성립하지 않는다고 느낀다',
            'if_annoyed': '감성만 강하면 설득을 포기한다',
        },
    },
    'career_efficiency_optimizer': {
        'persuasion_triggers': ['energy_support', 'focus_support', 'fatigue_recovery'],
        'objection_profile': {
            'trigger_conditions': ['workfit_is_unclear', 'benefit_does_not_map_to_workday', 'switch_cost_feels_unjustified'],
            'resolution_requirements': ['workday_specific_example', 'performance_gain', 'clear_use_case'],
        },
        'likely_reaction_style': {
            'if_interested': '업무 시간대에 어떻게 바로 도움이 되는지 확인하려 한다',
            'if_unconvinced': '좋아 보여도 실무에 바로 도움 되진 않는다고 느낀다',
            'if_annoyed': '일과 무관한 이야기만 길면 흥미를 잃는다',
        },
        'scoring_hints': {
            'purchase_intent_boosts': ['workday_energy_gain', 'clear_focus_gain'],
            'purchase_intent_penalties': ['work_irrelevance', 'effort_gt_reward'],
        },
        'cluster_tags': ['focus_support', 'career_focused', 'efficiency_seeking'],
    },
    'deal_hunter': {
        'objection_profile': {
            'trigger_conditions': ['deal_is_vague', 'urgency_without_benefit', 'terms_are_unclear'],
        },
    },
}

PROMPT_CONTENT = '''# Soul.md 생성 지시서

아래 profile.json을 읽고 해당 페르소나의 soul.md를 작성하세요.
대상 아이템은 서비스/앱이 아니라 "영양제·건강기능식품"입니다.

## soul.md 형식

```markdown
# {persona_id} — {한국어 이름} ({나이대}, {직업/상황})

## 나는 누구인가
{3~4문장. 이 사람의 현재 상황, 건강 고민, 구매 심리, 생활 리듬을 생생하게 묘사.
profile.life_context, purchase_context, age_band를 바탕으로 구체적인 인물상을 그린다.}

## 대화 스타일
- {말투 특징 3~5개. 존댓말/반말, 길게/짧게, 질문 많은지, 감정적인지 등}
- {decision_style.preferred_message_style과 disliked_message_style을 자연어로}
- {voice_preferences를 반영한 대화 패턴}
- {length_tolerance를 반영: short면 짧은 답변 선호, long이면 상세 설명 좋아함}

## 설득 포인트
- {persuasion_triggers를 영양제 맥락으로 구체적 상황에 풀어쓰기}
- {scoring_hints.engagement_boosts를 자연어로}
- {scoring_hints.purchase_intent_boosts를 자연어로}
- "..." → 귀 쫑긋 (구체적 반응 묘사)

## 절대 안 먹히는 것
- {disliked_message_style을 구체적 상황으로}
- {scoring_hints.engagement_penalties를 자연어로}
- {scoring_hints.purchase_intent_penalties를 자연어로}
- "..." → {if_annoyed 반응 묘사}

## 예상 반론
- {objection_profile.trigger_conditions를 질문 형태로 변환}
- {objection_profile.primary_type 관련 핵심 반론 1~2개}
- {objection_profile.secondary_type 관련 보조 반론 1개}
- {objection_profile.resolution_requirements를 "이걸 해결해주면 넘어간다" 형태로}

## 관심 신호
- {if_interested: 이런 행동을 보이면 관심 있다는 뜻}

## 이탈 신호
- {if_unconvinced: 이런 행동이면 설득 실패 중}
- {if_annoyed: 이런 행동이면 완전 이탈}
```

## 영양제 맥락 규칙
- 가격은 월 구독이 아니라 1통 기준, 1개월 기준, 1일 섭취 비용 기준으로 풀어쓴다.
- 기능은 소프트웨어 기능이 아니라 성분, 함량, 원료, 복용 편의, 체감 포인트, 안전성으로 바꾼다.
- 도입/세팅/온보딩은 복용 시작, 루틴 편입, 섭취 습관 형성으로 바꾼다.
- 무료 체험/무료 앱은 저가 제품, 샘플, 소용량 체험, 기존 복용 루틴 등으로 바꾼다.
- 과장된 의학적 치료 표현은 피하고, 일상적 컨디션 관리·부담 완화·체감 포인트 중심으로 쓴다.
- 직장인/학생/부모/중장년 등 각 variation의 생활 리듬에 맞는 복용 장면을 꼭 넣는다.

## 규칙
1. 한국어로 작성
2. 이름은 한국식으로 자연스럽게 생성 (김지현, 박서준, 이하은 등)
3. profile의 구조화된 데이터를 "살아있는 사람"처럼 풀어쓰기
4. LLM이 이 문서를 system prompt로 받았을 때 해당 인물로 자연스럽게 연기할 수 있어야 함
5. 너무 길지 않게 (300~500 단어)
6. 각 섹션은 구체적 예시 포함 (추상적 설명 금지)
'''


def deep_update(target, updates):
    for key, value in updates.items():
        if isinstance(value, dict):
            target.setdefault(key, {})
            deep_update(target[key], value)
        else:
            target[key] = deepcopy(value)


def main():
    data = json.loads(MASTER.read_text(encoding='utf-8'))
    for persona in data['personas']:
        arch = persona['archetype_id']
        life_context = persona['profile']['life_context']
        variation = persona['variation_slot']
        persona['summary'] = f"{SUMMARY_PREFIX[arch]} {life_context} 맥락에서 반응이 드러나는 {variation} variation."
        old_alt = persona['purchase_context']['current_alternative']
        if old_alt in CURRENT_ALTERNATIVE_MAP:
            persona['purchase_context']['current_alternative'] = CURRENT_ALTERNATIVE_MAP[old_alt]
        deep_update(persona, ARCHETYPE_UPDATES.get(arch, {}))

    MASTER.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    PROMPT.write_text(PROMPT_CONTENT, encoding='utf-8')

    # split_personas.py rewrites per-persona profile.json and index.json from the master file.
    exec(compile(SPLIT_SCRIPT.read_text(encoding='utf-8'), str(SPLIT_SCRIPT), 'exec'), {'__name__': '__main__'})


if __name__ == '__main__':
    main()
