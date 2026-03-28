"""페르소나 로더 — profile.json + soul.md."""
from __future__ import annotations

import json
import re
from pathlib import Path
from config.settings import get_settings


def _filter_soul_for_customer(soul_text: str) -> str:
    """Customer LLM에게 전달할 soul.md에서 메타 정보 섹션을 제거한다.

    제거 대상:
      - ## 설득 포인트: "이렇게 하면 설득된다" → LLM이 정답지로 사용하는 문제
      - ## 관심 신호: "이 행동이 나오면 관심 있는 것" → 자기참조적
      - ## 이탈 신호: "이 행동이 나오면 이탈" → 자기참조적
    
    변환 대상:
      - ## 예상 반론: 반론 자체는 유지하되 "→ 해결법" 힌트는 제거
    """
    lines = soul_text.split("\n")
    filtered: list[str] = []
    
    # 완전히 제거할 섹션들
    skip_sections = {"설득 포인트", "관심 신호", "이탈 신호"}
    
    current_section = ""
    skipping = False
    in_objection_section = False
    
    for line in lines:
        # ## 헤더 감지
        header_match = re.match(r"^##\s+(.+)", line)
        if header_match:
            section_name = header_match.group(1).strip()
            current_section = section_name
            
            if section_name in skip_sections:
                skipping = True
                in_objection_section = False
                continue
            elif section_name == "예상 반론":
                skipping = False
                in_objection_section = True
                filtered.append(line)
                continue
            else:
                skipping = False
                in_objection_section = False
                filtered.append(line)
                continue
        
        if skipping:
            continue
        
        if in_objection_section:
            # "→ ..." 해결법 힌트를 제거 (반론 텍스트만 남김)
            # 예: '- "반론내용" → 해결법 힌트' → '- "반론내용"'
            cleaned = re.sub(r"\s*→.*$", "", line)
            if cleaned.strip():
                filtered.append(cleaned)
            elif not line.strip():
                filtered.append(line)
            continue
        
        filtered.append(line)
    
    return "\n".join(filtered)


def load_personas(count: int | None = None, personas_dir: Path | None = None) -> list[dict]:
    """페르소나 로딩.

    Args:
        count: 로드할 페르소나 수. None이면 settings.persona_count 사용.
        personas_dir: 페르소나 디렉토리. None이면 settings.personas_dir 사용.

    Returns:
        [{"id": "P001", "profile": {...}, "soul": "...", "cluster_tags": [...]}]
    """
    settings = get_settings()
    if count is None:
        count = settings.persona_count
    if personas_dir is None:
        personas_dir = settings.personas_dir

    personas = []
    for i in range(1, count + 1):
        pid = f"P{i:03d}"
        pdir = personas_dir / pid
        if not pdir.exists():
            break

        # profile.json
        profile_path = pdir / "profile.json"
        profile = {}
        cluster_tags = []
        if profile_path.exists():
            with open(profile_path, "r", encoding="utf-8") as f:
                profile = json.load(f)
            cluster_tags = profile.get("cluster_tags", [])

        # soul.md
        soul_path = pdir / "soul.md"
        soul = ""
        if soul_path.exists():
            with open(soul_path, "r", encoding="utf-8") as f:
                soul = f.read()

        personas.append({
            "id": pid,
            "profile": profile,
            "soul": soul,
            "soul_for_customer": _filter_soul_for_customer(soul),
            "cluster_tags": cluster_tags,
        })

    return personas
