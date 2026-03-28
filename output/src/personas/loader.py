"""페르소나 로더 — profile.json + soul.md."""
from __future__ import annotations

import json
from pathlib import Path
from config.settings import get_settings


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
            "cluster_tags": cluster_tags,
        })

    return personas
