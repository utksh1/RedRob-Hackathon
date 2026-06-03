"""
Ranker — sorts scored candidates and generates reasoning strings.

Produces the final top-100 CSV output with:
  candidate_id, rank, score, reasoning
"""

from src.config import (
    CONSULTING_FIRMS,
    TITLES_STRONG_POSITIVE,
    TITLES_MILD_POSITIVE,
    SKILLS_TIER1,
    SKILLS_TIER2,
)


def _skill_match(name: str, keyword_set: set[str]) -> bool:
    """Check if a skill name matches any keyword in the set."""
    name_lower = name.lower().strip()
    for kw in keyword_set:
        if kw in name_lower or name_lower in kw:
            return True
    return False


def _is_consulting(company: str) -> bool:
    normalized = company.strip().lower()
    return any(firm in normalized for firm in CONSULTING_FIRMS)


def _title_match(title: str, title_set: set[str]) -> bool:
    title_lower = title.lower().strip()
    for t in title_set:
        if t in title_lower or title_lower in t:
            return True
    return False


def generate_reasoning(candidate: dict, scores: dict) -> str:
    """
    Generate a 1-2 sentence reasoning string for why this candidate was ranked.

    Format: "{title} with {years} yrs at {company_type}; {key_skills}; {behavioral_note}"
    """
    profile = candidate.get("profile", {})
    signals = candidate.get("redrob_signals", {})
    skills = candidate.get("skills", [])
    career = candidate.get("career_history", [])

    title = profile.get("current_title", "Unknown")
    company = profile.get("current_company", "Unknown")
    years = profile.get("years_of_experience", 0)
    country = profile.get("country", "Unknown")
    location = profile.get("location", "")

    # Company type
    if _is_consulting(company):
        company_type = "consulting"
    else:
        company_type = "product"

    # Count relevant skills
    relevant_skills = []
    for skill in skills:
        name = skill.get("name", "")
        if _skill_match(name, SKILLS_TIER1):
            relevant_skills.append(name)
        elif _skill_match(name, SKILLS_TIER2) and len(relevant_skills) < 5:
            relevant_skills.append(name)

    skill_str = ", ".join(relevant_skills[:4]) if relevant_skills else "general tech skills"

    # Behavioral note
    response_rate = signals.get("recruiter_response_rate", 0)
    open_flag = signals.get("open_to_work_flag", False)
    notice = signals.get("notice_period_days", 0)
    github = signals.get("github_activity_score", -1)

    behavioral_parts = []
    if open_flag:
        behavioral_parts.append("open to work")
    if response_rate >= 0.7:
        behavioral_parts.append(f"responsive ({response_rate:.0%})")
    elif response_rate >= 0.4:
        behavioral_parts.append(f"moderate response ({response_rate:.0%})")
    if notice <= 30:
        behavioral_parts.append(f"short notice ({notice}d)")
    if github >= 50:
        behavioral_parts.append(f"active GitHub ({github:.0f})")

    behavioral_str = "; ".join(behavioral_parts) if behavioral_parts else f"response rate {response_rate:.0%}"

    # Career depth
    career_note = ""
    if career:
        latest = career[0]
        desc_lower = latest.get("description", "").lower()
        if any(kw in desc_lower for kw in ["embedding", "retrieval", "ranking", "search", "recommendation"]):
            career_note = " with search/ranking production experience;"
        elif any(kw in desc_lower for kw in ["machine learning", "ml pipeline", "model", "deep learning"]):
            career_note = " with ML production experience;"
        elif any(kw in desc_lower for kw in ["data pipeline", "data engineering", "spark"]):
            career_note = " with data engineering experience;"

    # Location note
    loc_note = ""
    if country.lower() == "india":
        loc_note = f" in {location};" if location else " in India;"
    else:
        loc_note = f" in {country};"

    # Assemble
    reasoning = (
        f"{title} with {years:.1f} yrs at {company} ({company_type});"
        f"{career_note}{loc_note} "
        f"skills: {skill_str}; {behavioral_str}."
    )

    # Trim to reasonable length
    if len(reasoning) > 300:
        reasoning = reasoning[:297] + "..."

    return reasoning


def rank_candidates(
    scored_candidates: list[tuple[dict, dict]],
    top_n: int = 100,
) -> list[dict]:
    """
    Sort candidates by final score (descending) and produce the top-N output.

    Args:
        scored_candidates: list of (candidate, scores_dict) tuples
        top_n: number of candidates to return

    Returns:
        list of dicts with: candidate_id, rank, score, reasoning
    """
    # Sort by final_score descending
    sorted_candidates = sorted(
        scored_candidates,
        key=lambda x: x[1]["final_score"],
        reverse=True,
    )

    results = []
    for i, (candidate, scores) in enumerate(sorted_candidates[:top_n]):
        rank = i + 1
        score = scores["final_score"]
        reasoning = generate_reasoning(candidate, scores)

        results.append({
            "candidate_id": candidate["candidate_id"],
            "rank": rank,
            "score": round(score, 4),
            "reasoning": reasoning,
        })

    return results
