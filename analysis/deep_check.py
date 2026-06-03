"""Check for candidates who describe real ranking/search work but
don't use buzzword skill names — the 'plain language Tier 5' trap."""
import json, sys, csv
sys.stdout.reconfigure(encoding="utf-8")

# Load our submission IDs
with open("submission.csv", "r", encoding="utf-8") as f:
    our_ids = set(r["candidate_id"] for r in csv.DictReader(f))

# Search for candidates who have ranking/search/retrieval/recommendation
# in their career DESCRIPTIONS but NOT in their skills list
found = []
with open("India_runs_data_and_ai_challenge/candidates.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        c = json.loads(line)
        if c["candidate_id"] in our_ids:
            continue  # skip candidates we already picked
        
        # Check career descriptions for real work keywords
        all_desc = " ".join(r.get("description", "").lower() for r in c.get("career_history", []))
        
        deep_signals = [
            "ranking pipeline", "retrieval system", "search system",
            "recommendation system", "embeddings", "bge", "sentence-transformer",
            "vector search", "hybrid retrieval", "bm25", "ndcg", "mrr",
            "fine-tuned", "lora", "qlora", "re-ranker", "learning to rank"
        ]
        
        hits = [kw for kw in deep_signals if kw in all_desc]
        
        if len(hits) >= 3:
            p = c["profile"]
            years = p.get("years_of_experience", 0)
            if 4 <= years <= 10:
                # Check skill names — are they using buzzwords or plain language?
                skill_names = [s["name"].lower() for s in c.get("skills", [])]
                skill_str = " ".join(skill_names)
                
                sig = c.get("redrob_signals", {})
                
                found.append({
                    "id": c["candidate_id"],
                    "title": p.get("current_title"),
                    "company": p.get("current_company"),
                    "years": years,
                    "location": f"{p.get('location')}, {p.get('country')}",
                    "desc_hits": hits,
                    "open_to_work": sig.get("open_to_work_flag"),
                    "response_rate": sig.get("recruiter_response_rate"),
                    "last_active": sig.get("last_active_date"),
                })

print(f"Found {len(found)} potentially missed candidates with deep description signals")
print()
for c in found[:15]:
    print(f"{c['id']}: {c['title']} at {c['company']} ({c['years']}y)")
    print(f"  Location: {c['location']}")
    print(f"  Desc hits: {c['desc_hits']}")
    print(f"  Open: {c['open_to_work']}, Response: {c['response_rate']}, Active: {c['last_active']}")
    print()

# Also check: how many of our top 100 have REPEATED career descriptions?
print("=" * 60)
print("CHECKING FOR DUPLICATE DESCRIPTIONS IN OUR TOP 100")
print("=" * 60)

# Reload all candidates
all_cands = {}
with open("India_runs_data_and_ai_challenge/candidates.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        c = json.loads(line)
        if c["candidate_id"] in our_ids:
            all_cands[c["candidate_id"]] = c

# Check for duplicate descriptions
desc_map = {}
for cid, c in all_cands.items():
    for role in c.get("career_history", []):
        desc = role.get("description", "")[:100]
        if desc in desc_map:
            desc_map[desc].append(f"{cid}/{role.get('company')}")
        else:
            desc_map[desc] = [f"{cid}/{role.get('company')}"]

print("\nDuplicate description patterns in our top 100:")
dupe_count = 0
for desc, cids in sorted(desc_map.items(), key=lambda x: -len(x[1])):
    if len(cids) > 1:
        dupe_count += 1
        if dupe_count <= 10:
            print(f"  '{desc[:80]}...'")
            for cid in cids[:5]:
                print(f"    - {cid}")
print(f"\nTotal duplicate description groups: {dupe_count}")
