"""
soul.md 배치 생성 스크립트
사용법: python3 generate_souls.py <start> <end>
예시: python3 generate_souls.py 1 10  → P001~P010 생성
"""
import json, os, sys

BASE = "ralphthon-harness/data/personas"
PROMPT_TEMPLATE = open("ralphthon-harness/scripts/soul_generation_prompt.md").read()

def load_profile(pid):
    with open(f"{BASE}/{pid}/profile.json") as f:
        return json.load(f)

def get_persona_ids(start, end):
    """index.json에서 범위 내 persona_id 목록 반환"""
    with open(f"{BASE}/index.json") as f:
        index = json.load(f)
    all_ids = [p["persona_id"] for p in index["personas"]]
    return all_ids[start-1:end]

def build_prompt_for_batch(persona_ids):
    """여러 페르소나의 soul.md를 한 번에 생성하는 프롬프트"""
    parts = [PROMPT_TEMPLATE, "\n---\n\n아래 페르소나들의 soul.md를 각각 생성하세요.\n각 soul.md는 `===== {persona_id} =====` 구분자로 나눠주세요.\n\n"]
    
    for pid in persona_ids:
        profile = load_profile(pid)
        parts.append(f"### {pid}\n```json\n{json.dumps(profile, ensure_ascii=False, indent=2)}\n```\n\n")
    
    parts.append("위 페르소나들의 soul.md를 각각 생성하세요. 구분자: ===== P0XX =====")
    return "\n".join(parts)

if __name__ == "__main__":
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    end = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    ids = get_persona_ids(start, end)
    prompt = build_prompt_for_batch(ids)
    
    print(f"Generated prompt for {len(ids)} personas: {ids[0]}~{ids[-1]}")
    print(f"Prompt length: {len(prompt)} chars")
    
    # 프롬프트를 파일로 저장 (delegate_task에서 사용)
    out_path = f"ralphthon-harness/scripts/batch_prompt_{start:03d}_{end:03d}.txt"
    with open(out_path, "w") as f:
        f.write(prompt)
    print(f"Saved to: {out_path}")
