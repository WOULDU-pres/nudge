# Soul.md 생성 지시서

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
