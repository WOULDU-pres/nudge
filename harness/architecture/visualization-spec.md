# Visualization Spec — 대시보드 UI 상세 설계

에이전트가 이 문서를 읽으면, Ralphthon 시뮬레이션 결과를 시각화하는
웹 대시보드를 구현할 수 있어야 한다.

---

## 기술 스택

- **React 19 + TypeScript**
- **HeroUI v3** (`@heroui/react` + `@heroui/styles`) — 컴포넌트 라이브러리
- **Tailwind CSS v4** (HeroUI v3 필수 의존)
- **Recharts** (차트 라이브러리)
- Vite 빌드

### HeroUI v3 설치 & 설정

```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm i @heroui/styles @heroui/react tailwind-variants recharts
npm i -D tailwindcss @tailwindcss/postcss postcss
```

```css
/* src/index.css — import 순서 중요! */
@import "tailwindcss";
@import "@heroui/styles";
```

### HeroUI v3 핵심 규칙 (반드시 준수)

1. **Provider 불필요** — v2의 `<HeroUIProvider>`는 사용하지 않는다
2. **Compound Components** — `<Card><Card.Header>...</Card.Header></Card>` 패턴
3. **onPress 사용** — onClick 대신 onPress (React Aria 접근성)
4. **시맨틱 Variants** — raw 색상 대신 primary/secondary/danger 사용
5. **CSS 변수 theming** — oklch 색공간 기반 (`--accent`, `--background` 등)

### HeroUI 컴포넌트 문서 참조 (구현 전 필수)

에이전트는 컴포넌트 구현 전 반드시 **`~/.claude/skills/heroui-react/`** 스킬의 스크립트로 문서를 확인:

```bash
# 사용 가능한 컴포넌트 목록
node ~/.claude/skills/heroui-react/scripts/list_components.mjs

# 특정 컴포넌트 문서 (구현 전 반드시 실행)
node ~/.claude/skills/heroui-react/scripts/get_component_docs.mjs Card
node ~/.claude/skills/heroui-react/scripts/get_component_docs.mjs Table Button Tooltip Accordion

# 컴포넌트 CSS 스타일 (BEM 클래스)
node ~/.claude/skills/heroui-react/scripts/get_styles.mjs Button

# 테마 변수 확인
node ~/.claude/skills/heroui-react/scripts/get_theme.mjs
```

---

## UI/UX 디자인 시스템 — ui-ux-pro-max + heroui-react 스킬 병행 사용

**Phase 4 UI 개발 시 두 스킬을 반드시 함께 사용하라:**
- **`~/.claude/skills/ui-ux-pro-max/`** — 디자인 원칙, 색상, 타이포, UX 가이드라인
- **`~/.claude/skills/heroui-react/`** — 컴포넌트 API, 패턴, 문서 참조

### 역할 분담

| 관심사 | 사용 스킬 | 무엇을 얻는가 |
|--------|----------|--------------|
| 디자인 시스템 (색상, 폰트, 스타일 톤) | ui-ux-pro-max | design-system/MASTER.md |
| 차트/히트맵 디자인 가이드라인 | ui-ux-pro-max `--domain chart` | 차트 유형별 모범사례 |
| UX 접근성/애니메이션 규칙 | ui-ux-pro-max `--domain ux` | WCAG, 터치, 키보드 |
| 컴포넌트 구현 패턴 | heroui-react | Card, Table, Accordion API |
| 컴포넌트 props/이벤트 | heroui-react `get_component_docs.mjs` | v3 정확한 용법 |
| 테마 커스텀 변수 | heroui-react `get_theme.mjs` | oklch CSS 변수 |

### 필수 워크플로 (Phase 4 시작 시 반드시 순서대로 실행)

#### Step 1: ui-ux-pro-max 디자인 시스템 생성

```bash
python3 ~/.claude/skills/ui-ux-pro-max/scripts/search.py \
  "analytics dashboard data visualization persuasion simulation" \
  --design-system -p "Ralphthon Dashboard" --persist
```

이 명령이 생성하는 것:
- `design-system/MASTER.md` — 글로벌 디자인 규칙 (색상, 타이포, 레이아웃, 스타일 톤)
- 5개 도메인 병렬 검색 (product, style, color, landing, typography)
- reasoning rules 기반 최적 매칭
- anti-patterns (반드시 피할 것)

#### Step 2: ui-ux-pro-max 도메인별 상세 검색

```bash
# 히트맵/라인차트 디자인 가이드라인
python3 ~/.claude/skills/ui-ux-pro-max/scripts/search.py "heatmap line-chart real-time dashboard" --domain chart

# UX 접근성 + 애니메이션 가이드라인
python3 ~/.claude/skills/ui-ux-pro-max/scripts/search.py "animation accessibility color-contrast" --domain ux

# React 스택 가이드라인
python3 ~/.claude/skills/ui-ux-pro-max/scripts/search.py "state performance responsive" --stack react
```

#### Step 3: heroui-react 컴포넌트 문서 확인

```bash
# 이 대시보드에서 사용할 컴포넌트 문서를 미리 확인
node ~/.claude/skills/heroui-react/scripts/list_components.mjs
node ~/.claude/skills/heroui-react/scripts/get_component_docs.mjs Card Table Button Accordion Chip Badge Select TextField
node ~/.claude/skills/heroui-react/scripts/get_theme.mjs
```

#### Step 4: 디자인 시스템 → HeroUI 테마로 매핑

design-system/MASTER.md의 색상 팔레트를 HeroUI의 oklch CSS 변수에 매핑한다:

```css
:root {
  /* MASTER.md의 primary 색상 → HeroUI --accent 변수로 */
  --accent: oklch(/* MASTER.md에서 가져온 값 */);
  --accent-foreground: var(--snow);

  /* 히트맵 전용 (HeroUI 밖, MASTER.md 가이드 따름) */
  --heatmap-strong:    oklch(0.55 0.15 145);   /* 80-100 */
  --heatmap-positive:  oklch(0.75 0.18 145);   /* 65-79  */
  --heatmap-mixed:     oklch(0.85 0.15 85);    /* 50-64  */
  --heatmap-weak:      oklch(0.75 0.15 55);    /* 35-49  */
  --heatmap-poor:      oklch(0.60 0.20 25);    /* 0-34   */
}
```

#### Step 5: Pre-Delivery 체크리스트 (ui-ux-pro-max 기준)

- [ ] No emoji icons — SVG 아이콘 사용 (Heroicons/Lucide)
- [ ] 색상 대비 4.5:1+ (WCAG AA)
- [ ] 모든 클릭 가능 요소에 cursor-pointer
- [ ] hover 시 150-300ms 전환 애니메이션
- [ ] focus states 키보드 내비게이션 (HeroUI onPress가 자동 처리)
- [ ] 모바일 375px, 태블릿 768px, 데스크톱 1024px 반응형
- [ ] prefers-reduced-motion 존중
- [ ] 히트맵 셀에 숫자 항상 표시 (색맹 대응)
- [ ] HeroUI 시맨틱 variant 사용 (raw 색상 금지)
- [ ] Compound component 패턴 (Card.Header, Table.Row 등)

---

## 디자인 시스템

### 스타일: Analytics Dashboard (Minimalism + Dark Mode 지원)

ui-ux-pro-max 기준 Priority 1~5를 반영한다.

### 색상 팔레트

HeroUI의 oklch 기반 시맨틱 테마를 사용한다.
커스텀 색상은 히트맵 밴딩에만 필요.

```css
:root {
  /* HeroUI 시맨틱 변수 — 테마가 자동 관리 */
  /* --accent, --background, --foreground 등은 HeroUI가 제공 */

  /* 히트맵 전용 커스텀 변수 */
  --heatmap-strong:    oklch(0.55 0.15 145);   /* 80-100 진한 초록 */
  --heatmap-positive:  oklch(0.75 0.18 145);   /* 65-79  연한 초록 */
  --heatmap-mixed:     oklch(0.85 0.15 85);    /* 50-64  노랑 */
  --heatmap-weak:      oklch(0.75 0.15 55);    /* 35-49  주황 */
  --heatmap-poor:      oklch(0.60 0.20 25);    /* 0-34   빨강 */
}
```

HeroUI 시맨틱 매핑:
- `primary` → 주 액션 (Run 버튼, 선택된 전략)
- `secondary` → 보조 정보 (클러스터 라벨)
- `danger` → 실패/낮은 점수
- `ghost` → 비활성 셀, 부가 액션

### 히트맵 색상 밴딩 (5단계)

```
--heatmap-strong:    #15803D;    /* 80-100  강한 적합 — 진한 초록 */
--heatmap-positive:  #4ADE80;    /* 65-79   양호 — 연한 초록 */
--heatmap-mixed:     #FCD34D;    /* 50-64   혼합 — 노랑 */
--heatmap-weak:      #FB923C;    /* 35-49   약함 — 주황 */
--heatmap-poor:      #EF4444;    /* 0-34    부적합 — 빨강 */
```

접근성: 모든 색상 대비 4.5:1 이상 (WCAG AA).
색맹 대응: 히트맵 셀에 숫자 점수를 항상 표시.

### 타이포그래피

```
--font-heading:    'Inter', sans-serif;    /* 제목 */
--font-body:       'Inter', sans-serif;    /* 본문 */
--font-mono:       'JetBrains Mono', monospace;  /* 코드/데이터 */

본문: 16px, line-height: 1.5
제목: 20-28px, font-weight: 600-700
데이터: 14px mono
```

### 간격 & 레이아웃

```
--spacing-xs:  4px;
--spacing-sm:  8px;
--spacing-md:  16px;
--spacing-lg:  24px;
--spacing-xl:  32px;

카드: rounded-lg (8px), shadow-sm, padding 24px
카드 간 간격: 16-24px
최대 너비: 1280px
```

---

## 전체 레이아웃

```
┌───────────────────────────────────────────────────────┐
│  Header: "Ralphthon — Persuasion Strategy Simulator"     │
│  [TextField 프롬프트 입력]  [Button Run]  [Select 모드]  │
├───────────────────────────────────────────────────────┤
│                                                       │
│  ┌─────────────────────────────────────────────────┐  │
│  │  A. Strategy Leaderboard  (전략 순위표)         │  │
│  └─────────────────────────────────────────────────┘  │
│                                                       │
│  ┌─────────────────────────────────────────────────┐  │
│  │  B. Heatmap  (전략 × 클러스터 행렬)             │  │
│  │     ← 셀 클릭 가능                              │  │
│  └─────────────────────────────────────────────────┘  │
│                                                       │
│  ┌──────────────────────┬──────────────────────────┐  │
│  │  C. Cell Explanation  │  D. Cluster Insight      │  │
│  │  (선택된 셀 상세)     │  (클러스터별 분석)       │  │
│  └──────────────────────┴──────────────────────────┘  │
│                                                       │
│  ┌──────────────────────┬──────────────────────────┐  │
│  │  E. Persona Drilldown│  F. Experiment Trend      │  │
│  │  (대표 페르소나 3명)  │  (점수 추이 그래프)      │  │
│  └──────────────────────┴──────────────────────────┘  │
│                                                       │
│  ┌─────────────────────────────────────────────────┐  │
│  │  G. Conversation Viewer  (대화 원문 열람)       │  │
│  └─────────────────────────────────────────────────┘  │
│                                                       │
├───────────────────────────────────────────────────────┤
│  Footer: 실행 상태, 총 API 호출 수, 소요 시간        │
└───────────────────────────────────────────────────────┘
```

반응형 브레이크포인트:
- ≥1024px: 2열 그리드 (C+D, E+F)
- <1024px: 1열 스택

### Header — HeroUI 컴포넌트

```tsx
import { TextField, Button, Select, Card } from "@heroui/react";

<Card className="sticky top-0 z-50">
  <Card.Content className="flex items-center gap-4">
    <h1 className="text-xl font-bold whitespace-nowrap">Ralphthon</h1>
    <TextField
      label="Prompt"
      placeholder="20~30대 실무자에게 AI 음성 세일즈를 테스트해줘"
      className="flex-1"
      value={prompt}
      onChange={setPrompt}
    />
    <Select
      label="Mode"
      selectedKey={mode}
      onSelectionChange={setMode}
      className="w-32"
    >
      <Select.Item key="DEV">DEV (10)</Select.Item>
      <Select.Item key="TEST">TEST (50)</Select.Item>
      <Select.Item key="DEMO">DEMO (200)</Select.Item>
    </Select>
    <Button
      variant="primary"
      onPress={runSimulation}
      isLoading={isRunning}
    >
      Run
    </Button>
  </Card.Content>
</Card>
```

- **TextField** — 프롬프트 입력 (HeroUI v3)
- **Select** — 모드 선택 (compound: Select.Item)
- **Button** variant="primary" + isLoading — 실행 버튼
- sticky top-0 — 스크롤 시 상단 고정

---

## 패널 상세 — HeroUI 컴포넌트 매핑

### A. Strategy Leaderboard (전략 순위표)

표시할 데이터: `DemoBundle.leaderboard` 또는 `ralph-iteration.summary`

```
┌───┬──────────────────────┬──────────┬──────────────┬────────────┐
│ # │ 전략                  │ 평균점수  │ 태그          │ 강/약       │
├───┼──────────────────────┼──────────┼──────────────┼────────────┤
│ 1 │ strategy-roi-proof   │  67.2    │ roi, direct  │ ▲ROI ▼PREM │
│ 2 │ strategy-empathy     │  58.3    │ empathy,care │ ▲EMP ▼ROI  │
│ 3 │ strategy-social      │  52.0    │ social,trust │ ▲TRU ▼LOW  │
└───┴──────────────────────┴──────────┴──────────────┴────────────┘
```

**HeroUI 컴포넌트:**

```tsx
import { Table, Chip, Badge } from "@heroui/react";

<Card>
  <Card.Header>
    <Card.Title>Strategy Leaderboard</Card.Title>
  </Card.Header>
  <Card.Content>
    <Table aria-label="Strategy rankings">
      <Table.Header>
        <Table.Column>#</Table.Column>
        <Table.Column>전략</Table.Column>
        <Table.Column>평균점수</Table.Column>
        <Table.Column>태그</Table.Column>
        <Table.Column>강/약</Table.Column>
      </Table.Header>
      <Table.Body>
        <Table.Row key="1" onPress={() => selectStrategy("roi")}>
          <Table.Cell>1</Table.Cell>
          <Table.Cell>strategy-roi-proof</Table.Cell>
          <Table.Cell>
            <Badge variant="primary">67.2</Badge>
          </Table.Cell>
          <Table.Cell>
            <Chip size="sm" variant="secondary">roi</Chip>
            <Chip size="sm" variant="secondary">direct</Chip>
          </Table.Cell>
          <Table.Cell>▲ROI ▼PREM</Table.Cell>
        </Table.Row>
      </Table.Body>
    </Table>
  </Card.Content>
</Card>
```

- **Table** — HeroUI Table 컴포넌트 (정렬/선택 내장)
- **Chip** — 태그 표시 (variant="secondary")
- **Badge** — 점수 표시
- **Card** — 패널 감싸기 (compound: Card.Header + Card.Content)
- onPress로 행 클릭 → heatmap 연동

---

### B. Heatmap (전략 × 클러스터 행렬)

이것이 제품의 핵심 시각화. 가장 중요한 패널.

```
                 ROI   EMP   TRU   VOICE  PRES   PREM   LOW    COMP
strategy-roi    [84]  [51]  [67]   [55]  [42]   [38]   [61]   [44]
strategy-emp    [45]  [78]  [62]   [68]  [71]   [41]   [53]   [59]
strategy-soc    [52]  [61]  [72]   [58]  [64]   [45]   [47]   [55]
```

구현 상세:

1. **행**: 전략 variants (3~4개)
2. **열**: 8개 고정 클러스터
   - ROI, EMPATHY, TRUST, VOICE-SENSITIVE,
   - PRESSURE-AVERSION, PREMIUM, LOW-ATTENTION, COMPLEXITY-AVOIDER
3. **셀**:
   - 배경색: 점수 기반 밴딩 (5단계 색상)
   - 텍스트: 점수 숫자 (항상 표시 — 색맹 접근성)
   - 폰트: 14px mono, bold, 중앙 정렬
4. **셀 크기**: 최소 64x48px (터치 타겟 확보)
5. **셀 클릭**: 클릭하면 C(Cell Explanation) 패널이 업데이트됨
6. **선택 표시**: 선택된 셀에 2px solid border (--color-accent)
7. **행 레이블**: 전략 이름 (왼쪽 고정)
8. **열 레이블**: 클러스터 약어 (상단 고정, 45도 회전 또는 축약)

ui-ux-pro-max 참고 (charts.csv #5 Heatmap/Intensity):
- Gradient: Cool(blue) to Hot(red) — 우리는 green-yellow-red 5단계
- 색맹 대응: 숫자 항상 표시 + 패턴 오버레이 고려
- 숫자 범례 제공
- Recharts 또는 D3.js 또는 CSS Grid로 직접 구현

CSS Grid 구현 예시:
```css
.heatmap {
  display: grid;
  grid-template-columns: 200px repeat(8, 1fr);
  gap: 2px;
}
.heatmap-cell {
  min-height: 48px;
  min-width: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: monospace;
  font-weight: 700;
  font-size: 14px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 200ms ease-out;
}
.heatmap-cell:hover {
  transform: scale(1.05);
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}
.heatmap-cell[data-selected="true"] {
  outline: 2px solid var(--color-accent);
  outline-offset: 1px;
}
```

색상 매핑 함수:
```typescript
function getHeatmapColor(score: number): string {
  if (score >= 80) return '#15803D'; // strong
  if (score >= 65) return '#4ADE80'; // positive
  if (score >= 50) return '#FCD34D'; // mixed
  if (score >= 35) return '#FB923C'; // weak
  return '#EF4444';                  // poor
}

function getHeatmapTextColor(score: number): string {
  // 어두운 배경(strong, poor)은 흰 텍스트, 밝은 배경은 검은 텍스트
  if (score >= 80 || score < 35) return '#FFFFFF';
  return '#1E293B';
}
```

---

### C. Cell Explanation (선택된 셀 상세)

히트맵 셀 클릭 시 표시되는 패널.

데이터 소스: `cell_explanations` 또는 judge 결과에서 집계

표시 내용:
```
┌────────────────────────────────────────┐
│  strategy-roi-proof × ROI              │
│  평균 점수: 84                          │
│                                        │
│  ▲ Boosts (높은 이유)                   │
│  • 가격 프레이밍(하루 500원)이 효과적    │
│  • 숫자 기반 근거가 ROI 민감형에 적합    │
│  • 30일 환불이 리스크 감소로 작용        │
│                                        │
│  ▼ Penalties (낮추는 요인)              │
│  • 감정적 연결 부족                      │
│  • 첫 턴 오프닝이 다소 딱딱              │
│                                        │
│  📊 Prompt Profile 영향                 │
│  • analytical 축 강조 → ROI 가중치 +5   │
│                                        │
│  [대표 페르소나 보기 →]                  │
└────────────────────────────────────────┘
```

**HeroUI 컴포넌트:**

```tsx
import { Card, Chip, Button } from "@heroui/react";

<Card>
  <Card.Header>
    <Card.Title>{strategyId} × {clusterId}</Card.Title>
    <Card.Description>평균 점수: {score}</Card.Description>
  </Card.Header>
  <Card.Content className="space-y-4">
    <div>
      <h4 className="text-sm font-semibold">▲ Boosts</h4>
      {boosts.map(b => (
        <Chip key={b} size="sm" variant="primary">{b}</Chip>
      ))}
    </div>
    <div>
      <h4 className="text-sm font-semibold">▼ Penalties</h4>
      {penalties.map(p => (
        <Chip key={p} size="sm" variant="danger">{p}</Chip>
      ))}
    </div>
  </Card.Content>
  <Card.Footer>
    <Button variant="ghost" onPress={scrollToPersonaDrilldown}>
      대표 페르소나 보기 →
    </Button>
  </Card.Footer>
</Card>
```

- **Card** — 셀 설명 패널 전체
- **Chip** variant="primary" — boost / variant="danger" — penalty
- **Button** variant="ghost" — 드릴다운 링크

---

### D. Cluster Insight (클러스터별 분석)

8개 클러스터 각각의 요약.

```
┌────────────────────────────────────────┐
│  클러스터 인사이트                       │
│                                        │
│  ROI ───────────── 최강: roi-proof (84) │
│  공통 boost: 숫자, 비교, 가격 프레이밍   │
│  공통 penalty: 감정적 호소               │
│                                        │
│  EMPATHY ──────── 최강: empathy (78)    │
│  공통 boost: 공감, 이야기, 따뜻함        │
│  공통 penalty: 차가운 데이터 접근        │
│                                        │
│  ...                                   │
└────────────────────────────────────────┘
```

**HeroUI 컴포넌트:**

```tsx
import { Card, Accordion, Chip } from "@heroui/react";

<Card>
  <Card.Header>
    <Card.Title>Cluster Insights</Card.Title>
  </Card.Header>
  <Card.Content>
    <Accordion>
      {clusters.map(c => (
        <Accordion.Item
          key={c.id}
          title={`${c.id} — 최강: ${c.topStrategyId}`}
          subtitle={`평균 ${c.avgScore}점`}
        >
          <div className="space-y-2">
            <p className="text-sm">{c.narrative}</p>
            <div className="flex gap-1">
              {c.commonBoosts.map(b => (
                <Chip key={b} size="sm" variant="primary">{b}</Chip>
              ))}
              {c.commonPenalties.map(p => (
                <Chip key={p} size="sm" variant="danger">{p}</Chip>
              ))}
            </div>
          </div>
        </Accordion.Item>
      ))}
    </Accordion>
  </Card.Content>
</Card>
```

- **Accordion** — 8개 클러스터를 접힘/펼침으로 관리
- **Chip** — boost/penalty 키워드
- Accordion.Item의 title 클릭 → heatmap 해당 열 하이라이트 연동

---

### E. Persona Drilldown (대표 페르소나 3명)

선택된 셀(전략 × 클러스터)에서 대표 페르소나를 보여준다.

```
┌────────────────────────────────────────┐
│  대표 페르소나 (strategy-roi × ROI)     │
│                                        │
│  🟢 Best: P001 (92점)                  │
│  김도윤, 24세. 예산 민감형.              │
│  "가격이 커피보다 싸다니 생각해볼게요"   │
│                                        │
│  🟡 Median: P035 (67점)                │
│  이수진, 31세. 비교 구매형.              │
│  "다른 제품이랑 비교해봐야 할 것 같아요" │
│                                        │
│  🔴 Failure: P078 (28점)               │
│  박현우, 45세. 권위 신뢰형.              │
│  "뭐 500원이라고 해도 잘 모르겠는데요"   │
│                                        │
│  [대화 전문 보기 →]                      │
└────────────────────────────────────────┘
```

**HeroUI 컴포넌트:**

```tsx
import { Card, Button } from "@heroui/react";

const roles = [
  { label: "Best",    persona: best,    borderClass: "border-l-4 border-green-500" },
  { label: "Median",  persona: median,  borderClass: "border-l-4 border-yellow-500" },
  { label: "Failure", persona: failure, borderClass: "border-l-4 border-red-500" },
];

<Card>
  <Card.Header>
    <Card.Title>대표 페르소나</Card.Title>
    <Card.Description>{strategyId} × {clusterId}</Card.Description>
  </Card.Header>
  <Card.Content className="space-y-3">
    {roles.map(r => (
      <Card key={r.label} className={r.borderClass}>
        <Card.Header>
          <Card.Title>{r.label}: {r.persona.id} ({r.persona.score}점)</Card.Title>
          <Card.Description>{r.persona.profileSummary}</Card.Description>
        </Card.Header>
        <Card.Content>
          <blockquote className="text-sm italic">
            "{r.persona.representativeQuote}"
          </blockquote>
        </Card.Content>
        <Card.Footer>
          <Button size="sm" variant="ghost"
            onPress={() => viewConversation(r.persona.id)}>
            대화 전문 보기 →
          </Button>
        </Card.Footer>
      </Card>
    ))}
  </Card.Content>
</Card>
```

- **Card 중첩** — 외부 Card가 패널, 내부 Card 3개가 각 역할
- border-l-4 색상으로 Best/Median/Failure 시각 구분
- **Button** variant="ghost" → Conversation Viewer 연동

---

### F. Experiment Trend (실험 추이 그래프)

results.tsv 기반 점수 변화 추이.

```
avg_score
  60 ┤                              ╭──● keep
  55 ┤                     ╭────────╯
  50 ┤           ╭─● keep ─╯
  45 ┤  ● keep ──╯
  40 ┤──╯
     └────────────────────────────────
      exp1  exp2  exp3  exp4  exp5  exp6
```

구현 요소:
- **Line Chart** (Recharts `<LineChart>`)
- X축: 실험 번호 (exp1, exp2, ...)
- Y축: avg_score (0-100)
- 점: keep=초록 원, discard=빨강 ×, crash=회색 △
- 호버: 실험 상세 (commit, description, strategy)
- 보조 라인: cluster_coverage (점선, 오른쪽 Y축)

ui-ux-pro-max 참고 (charts.csv #1 Line Chart):
- Primary: #0080FF
- 호버 + 줌 인터랙션
- Chart.js 또는 Recharts

Recharts 예시:
```tsx
<LineChart width={600} height={300} data={experiments}>
  <XAxis dataKey="experiment" />
  <YAxis domain={[0, 100]} />
  <Tooltip />
  <Line
    type="monotone"
    dataKey="avg_score"
    stroke="#1E40AF"
    strokeWidth={2}
    dot={(props) => {
      const { cx, cy, payload } = props;
      if (payload.status === 'keep')
        return <circle cx={cx} cy={cy} r={5} fill="#15803D" />;
      if (payload.status === 'discard')
        return <text x={cx} y={cy} textAnchor="middle" fill="#EF4444">×</text>;
      return <text x={cx} y={cy} textAnchor="middle" fill="#9CA3AF">△</text>;
    }}
  />
  <Line
    type="monotone"
    dataKey="cluster_coverage"
    stroke="#F59E0B"
    strokeDasharray="5 5"
    strokeWidth={1}
  />
</LineChart>
```

---

### G. Conversation Viewer (대화 원문)

선택된 전략 × 페르소나의 대화 transcript를 보여준다.

```
┌────────────────────────────────────────┐
│  대화: strategy-roi-proof × P001       │
│  점수: 92 | outcome: interested         │
│                                        │
│  🤖 에이전트:                           │
│  안녕하세요! 혹시 매일 영양제 드시나요?  │
│  요즘 직장인분들 사이에서 하루 500원     │
│  으로 건강관리 시작하시는 분들이...      │
│                                        │
│  👤 P001 (김도윤):                      │
│  아... 영양제요? 솔직히 먹어봤는데      │
│  효과를 잘 모르겠더라고요. 그리고       │
│  500원이라고 해도 매달이면 꽤...        │
│                                        │
│  🤖 에이전트:                           │
│  맞아요, 그 고민 많이 하시더라고요.     │
│  바이탈케어는 60정에 29,900원이에요...  │
│                                        │
│  ...                                   │
└────────────────────────────────────────┘
```

**HeroUI 컴포넌트:**

```tsx
import { Card, Badge, ScrollShadow } from "@heroui/react";

<Card>
  <Card.Header>
    <Card.Title>대화: {strategyId} × {personaId}</Card.Title>
    <div className="flex gap-2">
      <Badge variant="primary">{score}점</Badge>
      <Badge variant="secondary">{outcome}</Badge>
    </div>
  </Card.Header>
  <Card.Content>
    <ScrollShadow className="max-h-96">
      <div className="space-y-3">
        {turns.map((turn, i) => (
          <div key={i} className={
            turn.role === "agent"
              ? "flex justify-start"
              : "flex justify-end"
          }>
            <Card className={
              turn.role === "agent"
                ? "max-w-[80%] bg-primary/10"
                : "max-w-[80%] bg-default/50"
            }>
              <Card.Content>
                <p className="text-xs font-semibold mb-1">
                  {turn.role === "agent" ? "🤖 에이전트" : `👤 ${personaId}`}
                </p>
                <p className="text-sm">{turn.content}</p>
              </Card.Content>
            </Card>
          </div>
        ))}
      </div>
    </ScrollShadow>
  </Card.Content>
</Card>
```

- **ScrollShadow** — 스크롤 가능 영역 (페이드 그림자)
- **Card** 중첩 — 채팅 버블로 사용
- **Badge** — 점수/outcome 표시
- `bg-primary/10` / `bg-default/50` — 에이전트/페르소나 구분

---

## 인터랙션 흐름

```
사용자가 프롬프트 입력 → [Run] 클릭
    │
    ▼
파이프라인 실행 (로딩 스켈레톤 표시)
    │
    ▼
A. Leaderboard 표시
B. Heatmap 표시
F. Trend 표시 (이전 실험 포함)
    │
    ▼
사용자가 Heatmap 셀 클릭
    │
    ├─→ C. Cell Explanation 업데이트
    ├─→ D. Cluster Insight 해당 클러스터 하이라이트
    └─→ E. Persona Drilldown 업데이트
           │
           └─→ "대화 전문 보기" 클릭
                  │
                  ▼
               G. Conversation Viewer
```

---

## 데이터 매핑: JSON 필드 → 패널

| 패널 | 읽는 데이터 | JSON 경로 |
|------|-----------|-----------|
| A. Leaderboard | 전략 순위 | `summary.strategies[]` + `summary.cluster_scores` |
| B. Heatmap | 전략×클러스터 점수 | `evaluations[]` → 전략별 클러스터별 평균 집계 |
| C. Cell Explanation | 셀 상세 | `evaluations[]` 필터 → boost/penalty 집계 |
| D. Cluster Insight | 클러스터 요약 | `reason.cluster_insights` |
| E. Persona Drilldown | 대표 페르소나 | `evaluations[]` → 해당 셀에서 상위/중간/하위 |
| F. Experiment Trend | 실험 추이 | `results.tsv` 파싱 |
| G. Conversation Viewer | 대화 원문 | `transcripts/<strategy>/<persona>.json` |

---

## UX 가이드라인 체크리스트

ui-ux-pro-max Priority 1~6 기준:

- [ ] **접근성**: 색상 대비 4.5:1+, alt text, keyboard nav, aria-labels
- [ ] **터치**: 최소 44x44px 터치 타겟, hover 의존 금지
- [ ] **성능**: 로딩 스켈레톤, CLS < 0.1, lazy load
- [ ] **레이아웃**: mobile-first, 가로 스크롤 금지, viewport meta
- [ ] **타이포**: 본문 16px+, line-height 1.5, mono for data
- [ ] **애니메이션**: 200ms 전환, prefers-reduced-motion 체크

---

## HeroUI 컴포넌트 전체 매핑 요약

| 패널 | HeroUI 컴��넌트 | 용도 |
|------|-----------------|------|
| Header | TextField, Button, Select, Card | 입력/실행/모드 |
| A. Leaderboard | Table, Chip, Badge, Card | 전략 순위표 |
| B. Heatmap | CSS Grid + Tooltip | 전략×클러스터 행렬 (커스텀) |
| C. Cell Explanation | Card, Chip, Button | 셀 상세 설명 |
| D. Cluster Insight | Card, Accordion, Chip | 클러스터별 분석 |
| E. Persona Drilldown | Card (중첩), Button | 대표 페르소나 3명 |
| F. Experiment Trend | Card + Recharts LineChart | 점수 추이 |
| G. Conversation | Card, Badge, ScrollShadow | ��화 원문 |

### 에이전트 구현 지시

1. **HeroUI v3 문서를 먼저 확인**: 각 컴포넌트 사용 전 `get_component_docs.mjs` 실행
2. **Compound pattern 준수**: Card.Header, Table.Row 등 dot-notation 사용
3. **onPress 사용**: onClick 대신 onPress (React Aria 접근성)
4. **시맨틱 variant**: raw 색상 대신 primary/secondary/danger/ghost
5. **히트맵만 커스텀**: B 패널의 히트맵 그리드는 CSS Grid로 직접 구현
6. **나머지는 HeroUI**: 다른 모든 패널은 HeroUI 컴포넌트 조합

---

## 필수 vs 선택

### 필수 (V1)
- A. Leaderboard
- B. Heatmap
- C. Cell Explanation
- F. Experiment Trend
- H. Strategy Recommendation Report (전략 추천 리포트)

### 있으면 좋음 (V1+)
- D. Cluster Insight
- E. Persona Drilldown
- G. Conversation Viewer

### 나중 (V2)
- 실시간 스트리밍 업데이트
- 다크 모드 토글
- 프롬프트 히스토리
- 전략 diff 비교

---

## H. Strategy Recommendation Report (전략 추천 리포트)

**Phase 3 결과를 바탕으로, 실제 세일즈에서 어떤 전략을 어떻게 사용해야 하는지 문서화하는 패널.**

이 패널은 시뮬레이션 결과의 "So what?"에 답한다.
데이터 분석을 넘어, 세일즈 실무자가 바로 참고할 수 있는 **전략 추천 리포트**를 생성한다.

### 데이터 소스

- 최고 점수 run의 `summary.json` — 전략별 점수
- 최고 점수 run의 `evaluations.json` — 페르소나별 결과
- 최고 점수 run의 `strategies.json` — 전략 상세 (approach, tone, opening 등)
- 최고 점수 run의 `reason.json` — 승리/패배 패턴
- 최고 점수 run의 `learnings.json` — 학습 포인트
- `results.tsv` — 실험 히스토리 (어떤 프롬프트 변경이 효과적이었는지)

### 리포트 구성

```
┌─────────────────────────────────────────────────────────┐
│  H. Strategy Recommendation Report                       │
│  "이 시뮬레이션 결과를 실전에 어떻게 쓸 것인가?"          │
│                                                         │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  1. 핵심 요약 (Executive Summary)                    │ │
│  │  - 최고 전략: strategy-roi-lifestyle (avg 79.3)      │ │
│  │  - 추천 이유: 1문장                                  │ │
│  │  - 주의사항: 1문장                                   │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                         │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  2. 전략별 실전 가이드                               │ │
│  │                                                     │ │
│  │  🥇 strategy-roi-lifestyle (79.3점)                  │ │
│  │  ├─ 이 전략을 쓸 때: "가격 민감형, ROI 중시 고객"    │ │
│  │  ├─ 오프닝 예시: "혹시 하루 500원으로..."            │ │
│  │  ├─ 핵심 화법: 구체적 숫자 + 생활비 대비 비유        │ │
│  │  ├─ 반론 대응: "합리적 관점" 인정 후 USP 전환        │ │
│  │  ├─ ✅ 잘 먹히는 고객: 예산 민감, 실용적, 젊은층     │ │
│  │  └─ ⚠️ 안 먹히는 고객: 감정 기반, 권위 신뢰형       │ │
│  │                                                     │ │
│  │  🥈 strategy-empathy-recovery (71.8점)               │ │
│  │  ├─ ...                                             │ │
│  │                                                     │ │
│  │  🥉 strategy-risk-free-experience (71.2점)           │ │
│  │  ├─ ...                                             │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                         │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  3. 고객 유형별 추천 전략 매트릭스                    │ │
│  │                                                     │ │
│  │  고객 유형        1순위 전략      2순위 전략          │ │
│  │  ──────────────  ──────────────  ──────────────      │ │
│  │  예산 민감형     ROI-lifestyle    Risk-free           │ │
│  │  감성 공감형     Empathy-recov.   ROI-lifestyle       │ │
│  │  비교 구매형     ROI-lifestyle    Empathy-recov.      │ │
│  │  권위 신뢰형     Risk-free        Empathy-recov.      │ │
│  │  ...                                                │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                         │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  4. 검증된 인사이트 (Do's & Don'ts)                  │ │
│  │                                                     │ │
│  │  ✅ Do's (검증됨):                                   │ │
│  │  - 첫 턴에서 고객의 생활 장면에 연결된 질문으로 시작  │ │
│  │  - 가격은 "하루 500원 = 커피값의 1/10"으로 프레이밍   │ │
│  │  - 반론은 "합리적 소비자"로 칭찬 후 전환              │ │
│  │  - 성분은 모호한 표현 대신 수치(mg, IU)로 설명        │ │
│  │                                                     │ │
│  │  ❌ Don'ts (실험으로 확인):                           │ │
│  │  - GMP 인증 같은 기본 정보로 첫 턴 시작하지 마세요    │ │
│  │  - "고함량", "수백%" 같은 모호한 표현은 신뢰 하락     │ │
│  │  - 고객의 기존 제품을 비하하면 역효과                  │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                         │
│  ┌─────────────────────────────────────────────────────┐ │
│  │  5. 실험 히스토리 & 진화 과정                        │ │
│  │                                                     │ │
│  │  baseline (69.8) → v2 데이터구체성 추가 (73.6 ✅)    │ │
│  │  → v3 과학적비유 (73.2 ×)                            │ │
│  │  → v4 스토리텔링 (71.9 ×)                            │ │
│  │  → v6 질문형합성 (72.5 ×)                            │ │
│  │                                                     │ │
│  │  핵심 발견: 데이터 구체성 + 직관적 비유 + 반론        │ │
│  │  리프레이밍이 가장 큰 점수 향상 요인. 과학적 비유나   │ │
│  │  스토리텔링 전환은 추가 개선 효과 없음.               │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                         │
│  [📄 리포트 다운로드 (Markdown)]                         │
│  [📋 클립보드 복사]                                      │
└─────────────────────────────────────────────────────────┘
```

### 구현 상세

1. **핵심 요약**: summary.json의 best_strategy + strategy_scores에서 순위 추출
2. **전략별 가이드**: strategies.json의 각 필드(approach, opening_style, objection_handling, tone)를 실전 가이드 형태로 재구성. evaluations.json에서 해당 전략의 고/저 점수 페르소나 분석.
3. **고객 유형별 매트릭스**: evaluations.json에서 persona cluster_tags별로 전략 점수를 집계하여 매트릭스 생성.
4. **Do's & Don'ts**: reason.json의 winning_patterns → Do's, losing_patterns → Don'ts. learnings.json의 learnings 반영.
5. **실험 히스토리**: results.tsv를 파싱하여 keep/discard 이력과 핵심 발견 요약.
6. **Markdown 다운로드**: 리포트 전체를 Markdown 파일로 다운로드 가능하게.

### 리포트 생성 로직 (LLM 사용하지 않음 — 순수 데이터 집계)

```typescript
function generateReport(
  summary: Summary,
  evaluations: Evaluation[],
  strategies: Strategy[],
  reason: ReasonData,
  learnings: LearningsData,
  experiments: ExperimentRow[],
): Report {
  // 1. 전략 순위 정렬
  const ranked = Object.entries(summary.strategy_scores)
    .sort(([,a], [,b]) => b - a);

  // 2. 전략별 고객 유형 매핑
  // evaluations에서 persona cluster_tags별 평균 점수 집계
  const strategyByCluster = aggregateByClusterTag(evaluations);

  // 3. Do's & Don'ts
  const dos = reason.winning_patterns;
  const donts = reason.losing_patterns;

  // 4. 실험 진화 요약
  const evolution = experiments.map(e => ({
    ...e,
    delta: e.avg_score - experiments[0].avg_score,
  }));

  return { ranked, strategyByCluster, dos, donts, evolution };
}
```

### 우선순위

**필수 (V1)** — Phase 4 완료 시 이 패널이 포함되어야 한다.

이 패널이 없으면 대시보드는 "데이터를 보여주는 도구"에 불과하지만,
이 패널이 있으면 "실전 세일즈 가이드를 생성하는 시스템"이 된다.
