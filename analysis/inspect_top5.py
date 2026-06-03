"""Inspect top 5 candidates from our submission against actual profiles."""
import json, sys, csv
sys.stdout.reconfigure(encoding="utf-8")

# Load top 5 candidate IDs from our submission
with open("submission.csv", "r", encoding="utf-8") as f:
    top_ids = [r["candidate_id"] for r in list(csv.DictReader(f))[:5]]

print("Top 5 IDs:", top_ids)

# Find them in the JSONL and print key details
with open("India_runs_data_and_ai_challenge/candidates.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        c = json.loads(line)
        if c["candidate_id"] in top_ids:
            p = c["profile"]
            print()
            print("=" * 60)
            print(f"  {c['candidate_id']}")
            print("=" * 60)
            print(f"Title:    {p.get('current_title')}")
            print(f"Company:  {p.get('current_company')}")
            print(f"Years:    {p.get('years_of_experience')}")
            print(f"Location: {p.get('location')}, {p.get('country')}")
            
            skills = c.get("skills", [])
            print(f"Skills ({len(skills)}):")
            for s in skills[:10]:
                print(f"  - {s['name']} ({s.get('proficiency','?')}, {s.get('duration_months',0)}mo)")
            
            career = c.get("career_history", [])
            print(f"\nCareer ({len(career)} roles):")
            for i, role in enumerate(career[:3]):
                print(f"  {i+1}. {role.get('title')} at {role.get('company')} ({role.get('duration_months',0)}mo)")
                desc = role.get("description", "")[:250]
                print(f"     Desc: {desc}")
            
            sig = c.get("redrob_signals", {})
            print(f"\nBehavioral:")
            print(f"  Open to work:   {sig.get('open_to_work_flag')}")
            print(f"  Response rate:  {sig.get('recruiter_response_rate')}")
            print(f"  Last active:    {sig.get('last_active_date')}")
            print(f"  GitHub:         {sig.get('github_activity_score')}")
            print(f"  Notice:         {sig.get('notice_period_days')}d")
            print(f"  Verified email: {sig.get('verified_email')}")
            print(f"  Profile complete: {sig.get('profile_completeness_score')}")
            
            assess = sig.get("skill_assessment_scores", {})
            if assess:
                print(f"  Assessments: {dict(list(assess.items())[:5])}")
