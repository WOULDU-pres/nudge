import json, os

with open("personas/ralphton-200-personas.json", "r") as f:
    data = json.load(f)

personas = data["personas"]
base = "ralphthon-harness/data/personas"

index_entries = []
for p in personas:
    pid = p["persona_id"]
    folder = os.path.join(base, pid)
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, "profile.json"), "w") as f:
        json.dump(p, f, ensure_ascii=False, indent=2)
    index_entries.append({
        "persona_id": pid,
        "archetype_id": p["archetype_id"],
        "archetype_name": p["archetype_name"],
        "variation_slot": p["variation_slot"],
        "cluster_tags": p["cluster_tags"],
        "summary": p["summary"]
    })

with open(os.path.join(base, "index.json"), "w") as f:
    json.dump({
        "total": len(index_entries),
        "archetypes": data["archetype_ids"],
        "variation_slots": data["variation_slots"],
        "personas": index_entries
    }, f, ensure_ascii=False, indent=2)

print(f"Created {len(personas)} persona folders")
print(f"Index: {len(index_entries)} entries")
print(f"First: {personas[0]['persona_id']} ({personas[0]['archetype_name']})")
print(f"Last: {personas[-1]['persona_id']} ({personas[-1]['archetype_name']})")
