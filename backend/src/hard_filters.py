"""
Hard Filters — eliminate candidates explicitly disqualified by the JD.

These filters run AFTER honeypot detection and BEFORE scoring.
They remove candidates who cannot possibly be a match regardless of other factors.
"""

from __future__ import annotations

from backend.src.config import CONSULTING_FIRMS, TITLES_NEGATIVE
from backend.src.relevance import has_strong_rescue_signal


def _normalize_company(name: str) -> str:
    """Normalize company name for matching."""
    return name.strip().lower()


def _is_consulting_firm(company: str) -> bool:
    """Check if a company is a known consulting/services firm."""
    normalized = _normalize_company(company)
    return any(firm in normalized for firm in CONSULTING_FIRMS)


def filter_entire_career_consulting(candidate: dict) -> tuple[bool, str]:
    """
    Disqualify candidates whose ENTIRE career is at consulting firms.

    Per JD: "People who have only worked at consulting firms (TCS, Infosys,
    Wipro, Accenture, Cognizant, Capgemini, etc.) in their entire career."

    If they have mixed experience (some consulting + some product), that's fine.
    """
    career = candidate.get("career_history", [])
    if not career:
        return False, ""

    all_consulting = all(_is_consulting_firm(role["company"]) for role in career)
    if all_consulting and len(career) >= 1:
        companies = ", ".join(set(role["company"] for role in career))
        return True, f"entire career at consulting firms: {companies}"

    return False, ""


def filter_location_impossible(candidate: dict) -> tuple[bool, str]:
    """
    Filter candidates who are outside India and unwilling to relocate.

    Per JD: Location is Pune/Noida, India. "Outside India: case-by-case,
    but we don't sponsor work visas."
    """
    profile = candidate.get("profile", {})
    country = profile.get("country", "").strip().lower()
    willing = candidate.get("redrob_signals", {}).get("willing_to_relocate", False)

    if country not in ("india", ""):
        if not willing:
            return True, f"outside India ({profile.get('country')}) and unwilling to relocate"
    return False, ""


def filter_zero_experience(candidate: dict) -> tuple[bool, str]:
    """
    Filter candidates with essentially zero relevant experience.
    """
    years = candidate.get("profile", {}).get("years_of_experience", 0)
    if years < 1.0:
        return True, f"insufficient experience ({years} years)"
    return False, ""


def filter_pure_non_technical(candidate: dict) -> tuple[bool, str]:
    """
    Filter candidates whose entire career + title is non-technical with
    zero evidence of ML/AI work in descriptions.

    This catches the trap: "A candidate who has all the AI keywords listed
    as skills but whose title is 'Marketing Manager' is not a fit."
    """
    profile = candidate.get("profile", {})
    current_title = profile.get("current_title", "").strip().lower()
    career = candidate.get("career_history", [])

    # Check if current title is in the negative list
    title_is_negative = any(neg in current_title for neg in TITLES_NEGATIVE)

    if not title_is_negative:
        return False, ""

    if has_strong_rescue_signal(candidate):
        return False, ""

    # Title is negative — check if ANY career description mentions ML/AI work
    ml_keywords = {
        "machine learning", "deep learning", "neural network", "embedding",
        "retrieval", "ranking", "search system", "recommendation",
        "nlp", "natural language", "model training", "model deployment",
        "data pipeline", "ml pipeline", "pytorch", "tensorflow",
        "transformer", "bert", "gpt", "fine-tuning", "inference",
        "data science", "classification", "vector database",
    }

    all_descriptions = " ".join(
        role.get("description", "").lower() for role in career
    )

    ml_hits = sum(1 for kw in ml_keywords if kw in all_descriptions)

    # Also check career titles for any technical roles
    career_titles = [role.get("title", "").lower() for role in career]
    has_tech_title = any(
        any(tech in title for tech in [
            "engineer", "developer", "scientist", "analyst",
            "architect", "ml", "ai", "data", "research"
        ])
        for title in career_titles
    )

    # If no ML keywords in descriptions AND no technical titles → filter
    if ml_hits < 3 and not has_tech_title:
        return True, f"non-technical career ({current_title}) with no ML/AI evidence"

    return False, ""


def apply_hard_filters(candidate: dict) -> tuple[bool, str | None]:
    """
    Apply all hard filters to a candidate.

    Returns:
        (should_keep: bool, rejection_reason: str | None)
    """
    filters = [
        filter_entire_career_consulting,
        filter_location_impossible,
        filter_zero_experience,
        filter_pure_non_technical,
    ]

    for filter_fn in filters:
        rejected, reason = filter_fn(candidate)
        if rejected:
            return False, reason

    return True, None
