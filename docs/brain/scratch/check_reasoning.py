"""Assess our reasoning quality against the 6 checks in submission_spec."""
import csv, sys
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")

with open("submission.csv", "r", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

print("REASONING QUALITY ANALYSIS")
print("=" * 60)

# Check 1: Are reasonings all identical or templated?
reasonings = [r["reasoning"] for r in rows]
unique_count = len(set(reasonings))
print(f"\n1. Variation: {unique_count} unique / {len(reasonings)} total")

# Check template structure
templates = []
for r in reasonings:
    # Extract the template by removing specific values
    template = r
    # Remove specific names/numbers to see if template is the same
    import re
    template = re.sub(r'\d+\.?\d*', 'N', template)
    template = re.sub(r'CAND_\d+', 'CAND', template)
    templates.append(template)

template_counts = Counter(templates)
print(f"   Unique templates: {len(template_counts)}")
print(f"   Most common template appears: {template_counts.most_common(1)[0][1]} times")

# Check 2: Do they reference specific facts?
specific_checks = {
    "has_years": 0,
    "has_company": 0,
    "has_skills": 0,
    "has_response_rate": 0,
    "has_notice": 0,
    "has_github": 0,
}
for r in reasonings:
    if "yrs" in r: specific_checks["has_years"] += 1
    if "(product)" in r or "(consulting)" in r: specific_checks["has_company"] += 1
    if "skills:" in r: specific_checks["has_skills"] += 1
    if "response" in r or "responsive" in r: specific_checks["has_response_rate"] += 1
    if "notice" in r: specific_checks["has_notice"] += 1
    if "GitHub" in r: specific_checks["has_github"] += 1

print(f"\n2. Specific facts referenced:")
for k, v in specific_checks.items():
    print(f"   {k}: {v}/100")

# Check 3: Honest concerns?
concerns = sum(1 for r in reasonings if "concern" in r.lower() or "gap" in r.lower() or "however" in r.lower())
print(f"\n3. Honest concerns acknowledged: {concerns}/100")

# Check 4: Rank consistency - do high ranks have better language?
high_rank_scores = [float(rows[i]["score"]) for i in range(10)]
low_rank_scores = [float(rows[i]["score"]) for i in range(90, 100)]
print(f"\n4. Score range:")
print(f"   Top 10:    {min(high_rank_scores):.4f} - {max(high_rank_scores):.4f}")
print(f"   Bottom 10: {min(low_rank_scores):.4f} - {max(low_rank_scores):.4f}")
print(f"   Spread:    {max(high_rank_scores) - min(low_rank_scores):.4f}")

# Check 5: Template pattern
print(f"\n5. Template structure check:")
print(f"   Sample Rank 1: {reasonings[0][:120]}...")
print(f"   Sample Rank 50: {reasonings[49][:120]}...")
print(f"   Sample Rank 100: {reasonings[99][:120]}...")

# VERDICT
print()
print("=" * 60)
print("VERDICT: REASONING WEAKNESSES")
print("=" * 60)
print("""
CRITICAL ISSUES:
- Reasoning follows an IDENTICAL template for all 100 candidates
- No honest concerns or gap acknowledgments
- No rank-specific tone variation
- The spec EXPLICITLY penalizes: 'Templated reasoning that just 
  inserts the candidate name'

This is EXACTLY what our reasoning does.
""")
