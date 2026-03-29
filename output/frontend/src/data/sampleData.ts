import type { Summary, Evaluation, Strategy, ReasonData, TrendEntry, Transcript } from "../types";

export const summary: Summary = {
  avg_score: 63.8,
  cluster_coverage: 100.0,
  best_strategy: "strategy-health-conscious",
  cluster_scores: {
    budget_sensitive: 63.8,
  },
  outcome_distribution: {
    converted: 0,
    interested: 10,
    neutral: 19,
    resistant: 0,
    lost: 1,
    error: 0,
  },
  strategy_scores: {
    "strategy-health-conscious": 66.4,
    "strategy-cost-sensitive": 64.8,
    "strategy-busy-professional": 60.2,
  },
  strategy_cluster_matrix: {
    "strategy-busy-professional": { budget_sensitive: 60.2 },
    "strategy-cost-sensitive": { budget_sensitive: 64.8 },
    "strategy-health-conscious": { budget_sensitive: 66.4 },
  },
  funnel_distribution: { "0": 1, "1": 6, "2": 23, "3": 0 },
};

export const evaluations: Evaluation[] = [
  {
    session_id: "conv-strategy-busy-professional-P001",
    strategy_id: "strategy-busy-professional",
    persona_id: "P001",
    scores: { engagement: 15, relevance: 20, persuasion: 18, purchase_intent: 8, total: 61 },
    outcome: "neutral",
    reason: "고객의 반론을 잘 인정하고 전환하려 했으나, 가격에 대한 부담을 완전히 해소하지 못해 구매 의향까지는 이어지지 못했습니다.",
    funnel_progress: 1,
    objection_handling: "acknowledged_and_pivoted",
    tone_match: true,
  },
  {
    session_id: "conv-strategy-busy-professional-P002",
    strategy_id: "strategy-busy-professional",
    persona_id: "P002",
    scores: { engagement: 18, relevance: 20, persuasion: 17, purchase_intent: 10, total: 65 },
    outcome: "neutral",
    reason: "고객이 가격에 긍정적 반응을 보였고, 제품의 차별점에 대해 구체적인 근거를 요구하며 관심을 보였으나, 구매 의사까지는 도달하지 못했습니다.",
    funnel_progress: 2,
    objection_handling: "acknowledged_and_pivoted",
    tone_match: true,
  },
  {
    session_id: "conv-strategy-busy-professional-P008",
    strategy_id: "strategy-busy-professional",
    persona_id: "P008",
    scores: { engagement: 5, relevance: 10, persuasion: 5, purchase_intent: 3, total: 23 },
    outcome: "lost",
    reason: "고객의 반응이 없어 대화가 시작되지 않았습니다.",
    funnel_progress: 0,
    objection_handling: "none",
    tone_match: true,
  },
  {
    session_id: "conv-strategy-health-conscious-P001",
    strategy_id: "strategy-health-conscious",
    persona_id: "P001",
    scores: { engagement: 18, relevance: 20, persuasion: 18, purchase_intent: 12, total: 68 },
    outcome: "interested",
    reason: "고객이 가격에 긍정적으로 반응하고, 제품 성분에 대해 구체적인 질문을 하며 관심을 보였습니다.",
    funnel_progress: 2,
    objection_handling: "acknowledged_and_pivoted",
    tone_match: true,
  },
  {
    session_id: "conv-strategy-health-conscious-P003",
    strategy_id: "strategy-health-conscious",
    persona_id: "P003",
    scores: { engagement: 20, relevance: 20, persuasion: 18, purchase_intent: 15, total: 73 },
    outcome: "interested",
    reason: "고객이 기존 영양제 대비 업그레이드 포인트에 대해 적극적으로 질문하며 높은 관심을 보였습니다.",
    funnel_progress: 2,
    objection_handling: "acknowledged_and_pivoted",
    tone_match: true,
  },
  {
    session_id: "conv-strategy-health-conscious-P004",
    strategy_id: "strategy-health-conscious",
    persona_id: "P004",
    scores: { engagement: 18, relevance: 20, persuasion: 20, purchase_intent: 15, total: 73 },
    outcome: "interested",
    reason: "에이전트가 최적의 비율에 대한 구체적인 설명을 잘 제공하여 고객의 신뢰를 얻었습니다.",
    funnel_progress: 2,
    objection_handling: "acknowledged_and_pivoted",
    tone_match: true,
  },
  {
    session_id: "conv-strategy-cost-sensitive-P001",
    strategy_id: "strategy-cost-sensitive",
    persona_id: "P001",
    scores: { engagement: 18, relevance: 20, persuasion: 18, purchase_intent: 12, total: 68 },
    outcome: "interested",
    reason: "가격 비교를 통해 고객이 가성비에 긍정적 반응을 보였습니다.",
    funnel_progress: 2,
    objection_handling: "acknowledged_and_pivoted",
    tone_match: true,
  },
  {
    session_id: "conv-strategy-cost-sensitive-P005",
    strategy_id: "strategy-cost-sensitive",
    persona_id: "P005",
    scores: { engagement: 15, relevance: 18, persuasion: 15, purchase_intent: 10, total: 58 },
    outcome: "neutral",
    reason: "고객이 관심은 보였으나 기존 제품과의 차별점에 대한 확신을 갖지 못했습니다.",
    funnel_progress: 2,
    objection_handling: "acknowledged",
    tone_match: true,
  },
  {
    session_id: "conv-strategy-cost-sensitive-P007",
    strategy_id: "strategy-cost-sensitive",
    persona_id: "P007",
    scores: { engagement: 18, relevance: 20, persuasion: 18, purchase_intent: 12, total: 68 },
    outcome: "interested",
    reason: "업그레이드 프레이밍이 효과적으로 작용하여 고객이 긍정적 반응을 보였습니다.",
    funnel_progress: 2,
    objection_handling: "acknowledged_and_pivoted",
    tone_match: true,
  },
  {
    session_id: "conv-strategy-health-conscious-P007",
    strategy_id: "strategy-health-conscious",
    persona_id: "P007",
    scores: { engagement: 18, relevance: 20, persuasion: 15, purchase_intent: 10, total: 63 },
    outcome: "neutral",
    reason: "고객이 성분에 대해 질문했으나, 구매 의사까지는 도달하지 못했습니다.",
    funnel_progress: 2,
    objection_handling: "acknowledged",
    tone_match: true,
  },
];

export const strategies: Strategy[] = [
  {
    strategy_id: "strategy-busy-professional",
    hypothesis:
      "바쁜 일상 속에서 건강 관리에 대한 니즈는 높지만, 시간과 노력이 부족한 2040 직장인/학생을 타겟으로 '간편함'과 '효율성'을 강조하여 설득한다.",
    funnel: {
      attention: { hook_type: "일상연결형", opening_line_guide: "아침 출근/등교 준비에 쫓기는 상황을 언급", target_emotion: "공감, 호기심" },
      interest: { value_framing: "단 30초의 투자로 얻는 하루 종일 활력", information_depth: "맥락적프레이밍", engagement_trigger: "현재 아침 루틴에 대한 질문" },
      desire: { emotional_driver: "시간 절약, 에너지 증진", proof_type: "ROI계산", objection_preempt: "하루 1,000원, 커피 한 잔 값으로 비타민 13종과 미네랄 7종" },
      action: { cta_style: "시험제안", urgency_type: "없음", fallback: "제품 상세 정보 링크 제공", risk_removal: "30일 이내 불만족 시 100% 환불 보장" },
    },
    tone: "친근하고 실용적이며 문제 해결 지향적",
    persona_adaptation: "바쁜 직장인/학생의 경우 핵심만 간결하게 전달하고, 편의성에 초점을 맞춘다.",
  },
  {
    strategy_id: "strategy-health-conscious",
    hypothesis:
      "건강에 관심은 있지만, 복잡한 영양제 조합이나 성분 공부에 부담을 느끼는 고객에게 '올인원'과 '한국인 맞춤 배합'의 전문성을 강조하여 신뢰를 구축한다.",
    funnel: {
      attention: { hook_type: "데이터형", opening_line_guide: "한국인의 비타민/미네랄 부족률에 대한 놀라운 통계 제시", target_emotion: "인지, 중요성 인식" },
      interest: { value_framing: "한국인에게 꼭 필요한 영양소를 최적의 비율로 한 번에 섭취", information_depth: "기술적우위", engagement_trigger: "현재 섭취 중인 영양제에 대한 질문" },
      desire: { emotional_driver: "최적화된 영양 섭취, 복잡함 해소", proof_type: "전문가권위", objection_preempt: "식약처 인증 한국인 맞춤 배합으로 업그레이드 루틴 제안" },
      action: { cta_style: "소프트CTA", urgency_type: "없음", fallback: "성분 정보나 식약처 인증 자료 제공", risk_removal: "월 자동배송 20% 할인 + 첫 달 30일 환불 보장" },
    },
    tone: "정보 제공적이고 신뢰감 있으며 전문가적",
    persona_adaptation: "성분이나 효능에 대해 꼼꼼하게 질문하는 고객에게는 활성형 성분, 흡수율 데이터 등 상세 정보 제공.",
  },
  {
    strategy_id: "strategy-cost-sensitive",
    hypothesis:
      "가격에 민감하거나, 영양제 섭취의 필요성을 크게 느끼지 못하는 고객에게 '합리적인 가격', '편의성 대비 고효율', '간단한 습관 형성'을 통해 가치를 인지시킨다.",
    funnel: {
      attention: { hook_type: "충격형", opening_line_guide: "매일 마시는 커피 한 잔보다 저렴한 비용으로 필수 영양소 충족", target_emotion: "놀라움, 가치 재인식" },
      interest: { value_framing: "편의점 비타민보다 3배 강력한 효과를 비슷한 가격에", information_depth: "비교데이터", engagement_trigger: "건강 관리 지출 비용에 대한 질문" },
      desire: { emotional_driver: "가성비, 현명한 소비", proof_type: "ROI계산", objection_preempt: "하루 1,000원 최소 투자로 비타민/미네랄 부족 해결" },
      action: { cta_style: "한정제안", urgency_type: "가격변동", fallback: "월 자동배송 20% 할인 정보 제공", risk_removal: "첫 구독 20% 할인 + 30일 환불 보장" },
    },
    tone: "실리적이고 경제적이며 설득적",
    persona_adaptation: "가격에 민감한 고객에게는 '하루 1,000원', '커피 한 잔 값' 등 상대적 수치로 가성비 강조.",
  },
];

export const reason: ReasonData = {
  winning_patterns: [
    "상위 대화에서는 에이전트가 고객의 현재 상황을 적극적으로 경청하고, 그에 맞춰 제품의 특징을 개인화하여 설명했습니다. 특히 '커피 한 잔 값'이라는 일상적인 비용 비교로 경제적 가치를 제시하며 초기 비용 저항을 낮추는 데 성공했습니다.",
    "고객의 질문에 대해 '최적의 비율' 같은 추상적 개념을 '한국인의 식습관 고려', '비타민 D, 아연 1000% 충족' 같은 구체적 수치와 사례로 풀어 설명하여 신뢰도를 높였습니다.",
    "반론이 제기될 때마다 고객의 의견을 먼저 인정하고 긍정적으로 반응한 후, 제품의 차별점으로 대화를 전환하는 'acknowledged_and_pivoted' 전략을 일관되게 사용했습니다.",
    "제품의 간편함(하루 한 알, 30초)과 효율성(여러 영양제 대신 하나로 해결)을 반복 강조하여 바쁜 현대인의 니즈를 충족시켰습니다.",
  ],
  losing_patterns: [
    "하위 대화에서는 에이전트가 고객의 반론에 대해 구체적인 정보나 설득력 있는 근거를 충분히 제시하지 못했습니다.",
    "고객이 반복적으로 차별점을 물었음에도 일반적인 설명에 머물러 고객의 의구심을 해소하지 못했습니다.",
    "일부 하위 대화에서는 고객 중심의 대화보다는 정보 수집에 치중하는 모습을 보여 구매 의도를 약화시켰습니다.",
    "고객이 직접적으로 불신을 표현했을 때 강력한 증거를 제시하지 못하고 일반적인 장점만 반복했습니다.",
  ],
  cluster_insights: {
    "strategy-health-conscious":
      "건강에 대한 인식이 높은 고객들은 제품의 효능, 성분, 과학적 근거에 대한 구체적인 정보를 요구합니다. '최적의 비율'과 '1000% 충족' 같은 수치와 실제 사용자 경험을 제시하는 것이 효과적입니다.",
    "strategy-cost-sensitive":
      "비용에 민감한 고객들은 가격 대비 효능, 즉 가성비를 중요하게 생각합니다. '커피 한 잔 값' 같은 일상적인 비교를 통해 저렴한 비용을 강조하는 것이 효과적입니다.",
    "strategy-busy-professional":
      "바쁜 전문직 고객들은 시간 효율성과 간편함을 최우선으로 생각합니다. '30초 투자', '하루 한 알' 같은 메시지로 제품의 편리함을 강조하는 것이 중요합니다.",
  },
  funnel_analysis: {
    attention_to_interest_rate: "100%",
    interest_to_desire_rate: "88.89%",
    desire_to_action_rate: "0%",
    bottleneck_stage: "Desire to Action",
    cluster_bottlenecks: {
      "strategy-health-conscious": "Desire to Action",
      "strategy-cost-sensitive": "Desire to Action",
      "strategy-busy-professional": "Desire to Action",
    },
    cluster_conversion_rates: {
      "strategy-health-conscious": { attention_to_interest: "100%", interest_to_desire: "80%", desire_to_action: "0%" },
      "strategy-cost-sensitive": { attention_to_interest: "100%", interest_to_desire: "100%", desire_to_action: "0%" },
      "strategy-busy-professional": { attention_to_interest: "100%", interest_to_desire: "100%", desire_to_action: "0%" },
    },
  },
  technique_effectiveness: {
    relative_numbers: { used: 6, avg_score_when_used: 69.83, avg_score_when_not: 50 },
    lifestyle_connection: { used: 8, avg_score_when_used: 69.25, avg_score_when_not: 50 },
    risk_removal: { used: 0, avg_score_when_used: 0, avg_score_when_not: 67.4 },
    upgrade_framing: { used: 7, avg_score_when_used: 70.28, avg_score_when_not: 50 },
  },
};

export const trendData: TrendEntry[] = [
  { run_id: "run-20260329-065718", avg_score: 63.8, cluster_coverage: 100.0, best_strategy: "strategy-health-conscious", verdict: "keep", note: "baseline" },
  { run_id: "run-20260329-070104", avg_score: 62.67, cluster_coverage: 100.0, best_strategy: "strategy-busy_professional", verdict: "discard", note: "exp1: concrete numbers + personalization" },
  { run_id: "run-20260329-070426", avg_score: 55.17, cluster_coverage: 100.0, best_strategy: "strategy-busy_professional_upgrade", verdict: "discard", note: "exp2: deep empathy + pivot strengthening" },
  { run_id: "run-20260329-070737", avg_score: 63.17, cluster_coverage: 100.0, best_strategy: "strategy-upgrade-existing-routine", verdict: "discard", note: "exp3: anti-abstract + immediate answers" },
  { run_id: "run-20260329-071140", avg_score: 61.21, cluster_coverage: 100.0, best_strategy: "strategy-value_seeker", verdict: "discard", note: "exp4: daily scenario + cluster differentiation" },
  { run_id: "run-20260329-071537", avg_score: 64.66, cluster_coverage: 100.0, best_strategy: "strategy-busy-professional", verdict: "keep", note: "exp5: strategy diversity enforcement" },
];

export const sampleTranscripts: Record<string, Transcript> = {
  "conv-strategy-health-conscious-P001": {
    session_id: "conv-strategy-health-conscious-P001",
    strategy_id: "strategy-health-conscious",
    persona_id: "P001",
    turns: [
      { role: "agent", content: "안녕하세요! 혹시 아침 식사 거르시는 날이 많으신가요? 요즘 같은 시대에 많은 분들이 비타민이나 미네랄 부족을 겪고 계신데, 혹시 알고 계셨나요? 😊" },
      { role: "persona", content: "네, 아침 거를 때 많아요. 근데 뭘 얼마나 부족하길래 그래요? 비타민제 같은 거 사 먹어야 할 정도인가요?" },
      { role: "agent", content: "네, 좋은 질문입니다! 한국 성인 기준으로 봤을 때, 하루 권장 섭취량 대비 비타민 D 부족률이 80% 이상이고, 마그네슘 같은 미네랄도 50% 이상 부족하다는 통계가 있어요. 그래서 단순히 '필요하다'를 넘어, '부족할 확률이 매우 높다'고 볼 수 있습니다.\n\n아침을 거르시면 이런 영양소 섭취가 더 어려워질 수 있는데, 혹시 이런 부족한 영양소를 한 번에, 간편하게 채울 수 있는 방법이 있다면 어떠실 것 같으세요? 😊" },
      { role: "persona", content: "아침 거르는 날이 많긴 한데, 통계가 그렇다고 해서 꼭 비타민제까지 먹어야 하나 싶기도 하고요. 그래서 하루에 얼마인데요? 편의점에서 파는 비타민 음료랑 비교하면 뭐가 다른가요?" },
      { role: "agent", content: "아, 네! 아침을 거르시는 날이 많으신데, 혹시 부족할까 걱정되시는 마음 충분히 이해됩니다. 😊\n\n편의점 비타민 음료와 비교해주셨는데요, 저희 데일리 멀티비타민 플러스는 비타민 13종과 미네랄 7종을 식약처 인증을 받은 한국인 맞춤 배합으로 하루 1정으로 간편하게 섭취할 수 있다는 점이에요.\n\n가격은 월 29,900원으로, 하루에 약 1,000원 정도 생각하시면 되는데요. 꾸준히 드셨을 때 건강 관리의 효율성을 생각하면 오히려 합리적인 선택이 되실 거예요." },
      { role: "persona", content: "월 29,900원이면... 하루에 1,000원이라... 음. 편의점 비타민 음료도 한 2,000원 정도 하니까 가격 자체는 그렇게 부담스러운 건 아니겠네요.\n\n근데 식약처 인증받은 한국인 맞춤 배합이라고 하셨는데, 정확히 어떤 성분이 얼마나 들어있는지 좀 더 자세히 알 수 있을까요?" },
    ],
    ended_by: "turn_limit",
  },
  "conv-strategy-busy-professional-P001": {
    session_id: "conv-strategy-busy-professional-P001",
    strategy_id: "strategy-busy-professional",
    persona_id: "P001",
    turns: [
      { role: "agent", content: "안녕하세요! 혹시 요즘 아침 출근 준비하느라 바쁘시진 않으세요? 😊 단 30초로 하루 건강을 챙길 수 있다면 관심 있으시겠어요?" },
      { role: "persona", content: "30초요? 그게 뭔데요? 뭘 어떻게 한다는 거예요?" },
      { role: "agent", content: "아, 궁금하시죠! 😊 저희 데일리 멀티비타민 플러스인데요, 하루 한 알이면 비타민 13종과 미네랄 7종을 한 번에 섭취할 수 있어요. 아침에 물 한 잔과 함께 딱 한 알! 30초면 충분합니다." },
      { role: "persona", content: "그런 건 편의점에서도 파는데... 뭐가 다른 건데요? 그리고 한 달에 얼마예요?" },
      { role: "agent", content: "좋은 질문입니다! 편의점 비타민 음료와 달리, 저희는 식약처 인증을 받은 한국인 맞춤 배합이에요. 가격은 월 29,900원, 하루 약 1,000원이에요. 커피 한 잔보다 저렴한 투자로 하루 종일 활력을 유지할 수 있어요." },
      { role: "persona", content: "1,000원... 그 정도면 뭐 나쁘지 않은데, 근데 진짜 효과가 있는 건지 모르겠어요. 영양제 먹어도 체감하기 힘들잖아요." },
    ],
    ended_by: "turn_limit",
  },
  "conv-strategy-cost-sensitive-P001": {
    session_id: "conv-strategy-cost-sensitive-P001",
    strategy_id: "strategy-cost-sensitive",
    persona_id: "P001",
    turns: [
      { role: "agent", content: "매일 마시는 커피 한 잔보다 저렴한 비용으로 내 몸의 필수 영양소를 모두 채울 수 있다면 믿으시겠어요? 😊" },
      { role: "persona", content: "커피보다 싸다고요? 얼마인데요?" },
      { role: "agent", content: "네! 하루에 딱 1,000원 정도예요. 월 29,900원인데, 편의점 비타민 음료가 보통 2,000원~3,000원 하잖아요? 그것보다 저렴하면서 비타민 13종과 미네랄 7종을 한 번에 챙길 수 있어요." },
      { role: "persona", content: "흠, 가격은 괜찮은데... 편의점 비타민이랑 뭐가 다른 건지 잘 모르겠어요. 성분이 좋다는 건 알겠는데 체감이 될까요?" },
      { role: "agent", content: "좋은 지적이세요! 편의점 비타민 음료 대비 3배 이상의 활성형 성분이 들어있고, 식약처 인증 한국인 맞춤 배합이에요. 그리고 30일 환불 보장이 있어서 부담 없이 시작하실 수 있어요." },
      { role: "persona", content: "30일 환불 보장이요? 그건 좀 괜찮네요. 그래도 좀 더 생각해볼게요." },
    ],
    ended_by: "turn_limit",
  },
};
