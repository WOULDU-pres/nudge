목표:
- 지정된 persona 폴더들의 soul.md를 서비스/앱/도구 중심 문맥에서 영양제·건강기능식품 중심 문맥으로 재작성한다.

반드시 지킬 것:
1. 각 soul.md의 제목(# Pxxx — 이름 (설명))은 유지한다. 이름과 괄호 속 직업/상황 라벨을 바꾸지 않는다.
2. 섹션 구조와 순서를 유지한다.
   - ## 나는 누구인가
   - ## 대화 스타일
   - ## 설득 포인트
   - ## 절대 안 먹히는 것
   - ## 예상 반론
   - ## 관심 신호
   - ## 이탈 신호
3. 기존 파일을 통째로 기계적으로 치환하지 말고, persona별 생활 맥락에 맞게 자연스럽게 다시 쓴다.
4. updated profile.json을 함께 참고한다. profile.json은 이미 영양제 기준으로 일부 변환되어 있다.
5. 서비스/앱/툴/구독/도입/온보딩/기능/무료체험 같은 표현은 영양제 맥락으로 바꾼다.
6. 직장인/학생/워킹페어런트/프리랜서/중장년 등 각 인물의 실제 하루 리듬에 맞는 복용 장면을 넣는다.
7. 과장된 의학적 치료 표현은 피하고, 일상적 컨디션 관리·피로감·집중력·복용 편의·안심·루틴 적합성 중심으로 쓴다.
8. 너무 템플릿처럼 보이지 않게, 기존 soul.md가 갖고 있던 개별 인물 느낌을 최대한 살린다.

권장 변환 기준:
- budget_practical_buyer: 1일 섭취 비용, 함량 대비 값, 체감 포인트
- busy_convenience_seeker: 하루 1~2정, 복용 간단함, 바쁜 루틴에 붙는지
- skeptical_comparison_buyer: 성분표/함량/원료/비교표/근거
- emotionally_open_caregiver: 부담 없음, 챙기기 쉬움, 가족 안심
- premium_status_buyer: 원료 품질, 브랜드 신뢰, 정제된 인상
- risk_averse_safety_first: 안전성, 인증, 부작용 부담, 익숙함
- trend_sensitive_early_adopter: 신원료, 새로운 포뮬러, 트렌드성
- inertia_bound_traditionalist: 기존 루틴 유지, 갈아타기 쉬움
- overwhelmed_complexity_avoider: 성분 설명 단순화, 이해 쉬움, 복용법 단순
- hard_sell_resistant: 강매 금지, 선택권 존중
- story_driven_dreamer: 변화된 일상 장면, 감정 서사
- data_rational_analyst: 수치, 함량, 근거, 논리 구조
- family_benefit_prioritizer: 가족 전체의 컨디션/생활 이익
- career_efficiency_optimizer: 에너지, 집중, 피로 회복, 오후 퍼짐 감소
- identity_expressive_buyer: 자기 관리 이미지, 취향, 라이프스타일 적합성
- deal_hunter: 묶음 혜택, 첫 구매 혜택, 정기배송/세트 할인
- relationship_trust_buyer: 진심, 태도, 신뢰감 있는 설명
- autonomy_protective_buyer: 여러 선택지, 스스로 비교 판단 가능
- low_attention_skimmer: 첫 문장에 누가 먹기 좋은지/핵심 포인트
- voice_sensitive_listener: 영양제 설명을 전달하는 목소리/톤/신뢰감

작업 방식:
- 지정된 범위의 실제 존재하는 persona 폴더만 처리한다.
- 각 persona마다 profile.json과 기존 soul.md를 읽고 soul.md만 덮어쓴다.
- 끝나면 처리한 persona 수, 샘플 몇 개, 아직 남은 문제(있다면)를 간단히 보고한다.
