import csv, sys
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")

with open("submission.csv", "r", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

print(f"Total rows: {len(rows)}")
print(f"Ranks: {rows[0]['rank']} to {rows[-1]['rank']}")
print(f"Score range: {rows[0]['score']} to {rows[-1]['score']}")

ids = [r["candidate_id"] for r in rows]
print(f"Unique IDs: {len(set(ids))}")

scores = [float(r["score"]) for r in rows]
print(f"Scores descending: {all(scores[i] >= scores[i+1] for i in range(len(scores)-1))}")

# Title distribution
titles = []
for r in rows:
    title = r["reasoning"].split(" with ")[0]
    titles.append(title)
tc = Counter(titles)
print("\nTitle distribution:")
for t, c in tc.most_common():
    print(f"  {t}: {c}")

# Company distribution
companies = []
for r in rows:
    try:
        company = r["reasoning"].split(" at ")[1].split(" (")[0]
    except:
        company = "?"
    companies.append(company)
cc = Counter(companies)
print("\nTop companies:")
for co, c in cc.most_common(15):
    print(f"  {co}: {c}")
