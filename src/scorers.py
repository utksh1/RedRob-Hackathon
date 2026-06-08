"""
Multi-Dimensional Scoring Engine — 6 axes of candidate evaluation.

Each scorer returns a value in [0.0, 1.0].
The composite is computed externally using configurable weights.

Axes:
1. Skills Relevance     (0.25)  — skill match with keyword-stuffer penalty
2. Career Quality       (0.30)  — product vs consulting, title relevance, description analysis
3. Behavioral Signals   (0.20)  — availability, engagement, market validation
4. Experience Fit       (0.15)  — Gaussian centered on JD sweet spot
5. Education Fit        (0.05)  — institution tier, field relevance
6. Logistics Fit        (0.05)  — location, notice period, salary, work mode
"""

import math
from datetime import date, datetime
from typing import Any

from src.config import (
    REFERENCE_DATE,
    # Skills
    SKILLS_TIER1, SKILLS_TIER2, SKILLS_ANTI,
    # Titles
    TITLES_STRONG_POSITIVE, TITLES_MILD_POSITIVE, TITLES_NEGATIVE,
    # Career description keywords
    DESC_KEYWORDS_CORE, DESC_KEYWORDS_STRONG,
    DESC_KEYWORDS_MODERATE, DESC_KEYWORDS_NEGATIVE,
    # Consulting
    CONSULTING_FIRMS,
    # Experience
    EXPERIENCE_PEAK, EXPERIENCE_SIGMA, EXPERIENCE_MIN, EXPERIENCE_MAX,
    # Location
    PREFERRED_CITIES, PREFERRED_REGIONS,
    # Behavioral thresholds
    ACTIVE_EXCELLENT, ACTIVE_GOOD, ACTIVE_STALE, ACTIVE_DEAD,
    RESPONSE_RATE_EXCELLENT, RESPONSE_RATE_GOOD, RESPONSE_RATE_POOR,
    NOTICE_IDEAL, NOTICE_OK, NOTICE_LONG,
    SALARY_MIN_REASONABLE, SALARY_MAX_REASONABLE,
)


# ─────────────────────────────────────────────────────────
# Helper utilities
# ─────────────────────────────────────────────────────────

def _parse_date(date_str: str | None) -> date | None:
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def _gaussian(x: float, mu: float, sigma: float) -> float:
    """Gaussian function normalized to peak at 1.0."""
    return math.exp(-0.5 * ((x - mu) / sigma) ** 2)


def _skill_match(name: str, keyword_set: set[str]) -> bool:
    """Check if a skill name matches any keyword in the set (substring match)."""
    name_lower = name.lower().strip()
    for kw in keyword_set:
        if kw in name_lower or name_lower in kw:
            return True
    return False


def _title_match(title: str, title_set: set[str]) -> bool:
    """Check if a title matches any in the set (substring match)."""
    title_lower = title.lower().strip()
    for t in title_set:
        if t in title_lower or title_lower in t:
            return True
    return False


def _is_consulting(company: str) -> bool:
    """Check if company is a consulting firm."""
    normalized = company.strip().lower()
    return any(firm in normalized for firm in CONSULTING_FIRMS)


def _score_description_text(text: str) -> float:
    """
    Score a career description based on keyword relevance.
    Returns a value in roughly [-1.0, 1.0].
    """
    text_lower = text.lower()

    core_hits = sum(1 for kw in DESC_KEYWORDS_CORE if kw in text_lower)
    strong_hits = sum(1 for kw in DESC_KEYWORDS_STRONG if kw in text_lower)
    moderate_hits = sum(1 for kw in DESC_KEYWORDS_MODERATE if kw in text_lower)
    negative_hits = sum(1 for kw in DESC_KEYWORDS_NEGATIVE if kw in text_lower)

    raw = (core_hits * 3.0 + strong_hits * 2.0 +
           moderate_hits * 1.0 - negative_hits * 2.0)

    total_kw = core_hits + strong_hits + moderate_hits + negative_hits
    if total_kw == 0:
        return 0.0

    # Normalize to roughly [-1, 1]
    return _clamp(raw / (total_kw * 2.0), -1.0, 1.0)


# ─────────────────────────────────────────────────────────
# Axis 1: Skills Relevance
# ─────────────────────────────────────────────────────────

def score_skills(candidate: dict) -> float:
    """
    Score based on skill relevance, proficiency, duration, and assessment scores.
    Includes keyword-stuffer detection.
    """
    skills = candidate.get("skills", [])
    if not skills:
        return 0.0

    proficiency_weights = {
        "beginner": 0.2,
        "intermediate": 0.5,
        "advanced": 0.8,
        "expert": 1.0,
    }

    tier1_score = 0.0
    tier2_score = 0.0
    anti_count = 0
    total_relevant = 0

    has_python = False

    for skill in skills:
        name = skill.get("name", "")
        prof = skill.get("proficiency", "beginner")
        duration = skill.get("duration_months", 0)
        endorsements = skill.get("endorsements", 0)

        prof_w = proficiency_weights.get(prof, 0.2)
        dur_w = _clamp(duration / 36.0)  # normalize to 3 years
        endorse_w = _clamp(endorsements / 30.0)  # normalize to 30

        quality = prof_w * 0.5 + dur_w * 0.3 + endorse_w * 0.2

        if name.lower().strip() == "python":
            has_python = True

        if _skill_match(name, SKILLS_TIER1):
            tier1_score += quality
            total_relevant += 1
        elif _skill_match(name, SKILLS_TIER2):
            tier2_score += quality * 0.6
            total_relevant += 1

        if _skill_match(name, SKILLS_ANTI):
            anti_count += 1

    # Assessment bonus: validated skills on platform
    assessments = (candidate.get("redrob_signals", {})
                   .get("skill_assessment_scores", {}))
    assess_bonus = 0.0
    for skill_name, score in assessments.items():
        if (_skill_match(skill_name, SKILLS_TIER1) or
                _skill_match(skill_name, SKILLS_TIER2)):
            assess_bonus += (score / 100.0) * 0.15

    # Python bonus (explicitly required in JD)
    python_bonus = 0.15 if has_python else 0.0

    # Raw skill score
    raw = tier1_score + tier2_score + assess_bonus + python_bonus

    # ── Keyword stuffer detection ──
    # If career is non-technical but skills list is AI-heavy → penalize
    current_title = candidate.get("profile", {}).get("current_title", "")
    if _title_match(current_title, TITLES_NEGATIVE) and total_relevant > 4:
        # Check if descriptions back up the skills
        all_desc = " ".join(
            r.get("description", "") for r in candidate.get("career_history", [])
        )
        desc_score = _score_description_text(all_desc)
        if desc_score < 0.2:
            # Keyword stuffer: heavy penalty
            raw *= 0.15

    # High anti-skill ratio penalty
    if anti_count > total_relevant and anti_count >= 3:
        raw *= 0.5

    return _clamp(raw / 4.0)  # normalize to [0, 1]


# ─────────────────────────────────────────────────────────
# Axis 2: Career Quality
# ─────────────────────────────────────────────────────────

def score_career(candidate: dict) -> float:
    """
    Score based on career trajectory, company quality, title relevance,
    and description content analysis.
    """
    career = candidate.get("career_history", [])
    if not career:
        return 0.0

    profile = candidate.get("profile", {})

    # ── 2a. Title relevance (current + historical) ──
    current_title = profile.get("current_title", "")
    current_title_score = 0.0
    if _title_match(current_title, TITLES_STRONG_POSITIVE):
        current_title_score = 1.0
    elif _title_match(current_title, TITLES_MILD_POSITIVE):
        current_title_score = 0.5
    elif _title_match(current_title, TITLES_NEGATIVE):
        current_title_score = 0.05

    # Historical title relevance (weighted by recency)
    hist_title_score = 0.0
    for i, role in enumerate(career):
        title = role.get("title", "")
        weight = 1.0 / (i + 1)  # more recent roles weight more
        if _title_match(title, TITLES_STRONG_POSITIVE):
            hist_title_score += 1.0 * weight
        elif _title_match(title, TITLES_MILD_POSITIVE):
            hist_title_score += 0.5 * weight
        elif _title_match(title, TITLES_NEGATIVE):
            hist_title_score += 0.05 * weight

    title_component = (current_title_score * 0.5 +
                       _clamp(hist_title_score / 2.0) * 0.5)

    # ── 2b. Company quality (product vs consulting) ──
    product_months = 0
    consulting_months = 0
    for role in career:
        months = role.get("duration_months", 0)
        if _is_consulting(role.get("company", "")):
            consulting_months += months
        else:
            product_months += months

    total_months = product_months + consulting_months
    if total_months > 0:
        product_ratio = product_months / total_months
    else:
        product_ratio = 0.5  # unknown

    company_component = product_ratio

    # ── 2c. Description analysis (most important!) ──
    desc_scores = []
    for i, role in enumerate(career):
        desc = role.get("description", "")
        weight = 1.0 / (i + 1)  # recent roles matter more
        desc_scores.append(_score_description_text(desc) * weight)

    if desc_scores:
        desc_component = _clamp(
            (sum(desc_scores) / sum(1.0 / (i + 1) for i in range(len(desc_scores))) + 1.0) / 2.0
        )
    else:
        desc_component = 0.0

    # ── 2d. Job stability (penalize title-chasing) ──
    if career:
        avg_tenure_months = sum(r.get("duration_months", 0) for r in career) / len(career)
        if avg_tenure_months >= 36:
            stability = 1.0
        elif avg_tenure_months >= 24:
            stability = 0.8
        elif avg_tenure_months >= 18:
            stability = 0.6
        elif avg_tenure_months >= 12:
            stability = 0.4
        else:
            stability = 0.2
    else:
        stability = 0.5

    # ── Composite ──
    career_score = (
        title_component * 0.30 +
        company_component * 0.20 +
        desc_component * 0.35 +
        stability * 0.15
    )

    return _clamp(career_score)


# ─────────────────────────────────────────────────────────
# Axis 3: Behavioral Signals
# ─────────────────────────────────────────────────────────

def score_behavioral(candidate: dict) -> float:
    """
    Score based on platform engagement and availability signals.
    A perfect-on-paper candidate who's unreachable is worthless.
    """
    signals = candidate.get("redrob_signals", {})

    # ── 3a. Recency of activity ──
    last_active = _parse_date(signals.get("last_active_date"))
    if last_active:
        days_since = (REFERENCE_DATE - last_active).days
        if days_since <= ACTIVE_EXCELLENT:
            recency = 1.0
        elif days_since <= ACTIVE_GOOD:
            recency = 0.8
        elif days_since <= ACTIVE_STALE:
            recency = 0.5
        elif days_since <= ACTIVE_DEAD:
            recency = 0.2
        else:
            recency = 0.1
    else:
        recency = 0.3  # unknown

    # ── 3b. Response rate ──
    response_rate = signals.get("recruiter_response_rate", 0.0)
    if response_rate >= RESPONSE_RATE_EXCELLENT:
        resp_score = 1.0
    elif response_rate >= RESPONSE_RATE_GOOD:
        resp_score = 0.7
    elif response_rate >= RESPONSE_RATE_POOR:
        resp_score = 0.4
    else:
        resp_score = 0.15

    # ── 3c. Response time ──
    avg_response_hours = signals.get("avg_response_time_hours", 100)
    if avg_response_hours <= 12:
        time_score = 1.0
    elif avg_response_hours <= 48:
        time_score = 0.8
    elif avg_response_hours <= 96:
        time_score = 0.6
    elif avg_response_hours <= 168:
        time_score = 0.4
    else:
        time_score = 0.2

    # ── 3d. Interview & offer track record ──
    interview_rate = signals.get("interview_completion_rate", 0.5)
    offer_rate = signals.get("offer_acceptance_rate", -1)

    track_score = interview_rate * 0.6
    if offer_rate >= 0:
        track_score += offer_rate * 0.4
    else:
        track_score += 0.2  # neutral for no history

    # ── 3e. Platform engagement ──
    profile_complete = signals.get("profile_completeness_score", 50) / 100.0
    open_to_work = 1.0 if signals.get("open_to_work_flag", False) else 0.5
    views = _clamp(signals.get("profile_views_received_30d", 0) / 30.0)
    saved = _clamp(signals.get("saved_by_recruiters_30d", 0) / 10.0)
    search_app = _clamp(signals.get("search_appearance_30d", 0) / 200.0)

    engagement = (profile_complete * 0.3 + open_to_work * 0.2 +
                  views * 0.2 + saved * 0.2 + search_app * 0.1)

    # ── 3f. Verification signals ──
    verified = 0.0
    if signals.get("verified_email", False):
        verified += 0.4
    if signals.get("verified_phone", False):
        verified += 0.3
    if signals.get("linkedin_connected", False):
        verified += 0.3

    # ── 3g. GitHub activity ──
    github = signals.get("github_activity_score", -1)
    if github >= 0:
        github_score = github / 100.0
    else:
        github_score = 0.3  # neutral if no GitHub

    # ── Composite behavioral score ──
    behavioral = (
        recency * 0.20 +
        resp_score * 0.20 +
        time_score * 0.05 +
        track_score * 0.15 +
        engagement * 0.15 +
        verified * 0.10 +
        github_score * 0.15
    )

    return _clamp(behavioral)


def compute_availability_multiplier(candidate: dict) -> float:
    """
    Compute the availability gate multiplier (0.3 to 1.0).
    This multiplies the entire composite score.

    A candidate who's unreachable gets heavily penalized regardless
    of how perfect their skills are.
    """
    signals = candidate.get("redrob_signals", {})

    # Last active recency
    last_active = _parse_date(signals.get("last_active_date"))
    if last_active:
        days_since = (REFERENCE_DATE - last_active).days
    else:
        days_since = 365

    # Response rate
    response_rate = signals.get("recruiter_response_rate", 0.0)

    # Open to work
    open_to_work = signals.get("open_to_work_flag", False)

    # Compute multiplier
    mult = 1.0

    if days_since > ACTIVE_DEAD:
        mult *= 0.3
    elif days_since > ACTIVE_STALE:
        mult *= 0.5
    elif days_since > ACTIVE_GOOD:
        mult *= 0.7

    if response_rate < RESPONSE_RATE_POOR:
        mult *= 0.5
    elif response_rate < RESPONSE_RATE_GOOD:
        mult *= 0.75

    if not open_to_work and days_since > ACTIVE_GOOD:
        mult *= 0.8

    return _clamp(mult, 0.3, 1.0)


# ─────────────────────────────────────────────────────────
# Axis 4: Experience Fit
# ─────────────────────────────────────────────────────────

def score_experience(candidate: dict) -> float:
    """
    Score based on years of experience fit to JD requirements.
    Gaussian centered on the ideal range (5-9 years, peak at 7).
    """
    years = candidate.get("profile", {}).get("years_of_experience", 0)

    if years < EXPERIENCE_MIN:
        # Below minimum — steep penalty
        return _clamp(years / EXPERIENCE_MIN * 0.3)

    # Gaussian scoring
    gauss = _gaussian(years, EXPERIENCE_PEAK, EXPERIENCE_SIGMA)

    # Bonus for sweet spot (5-9 years)
    if 5 <= years <= 9:
        gauss = gauss * 0.8 + 0.2  # boost

    return _clamp(gauss)


# ─────────────────────────────────────────────────────────
# Axis 5: Education Fit
# ─────────────────────────────────────────────────────────

def score_education(candidate: dict) -> float:
    """
    Score based on institution tier, field relevance, and degree level.
    Education is low-weight (0.05) per the JD's emphasis on practical experience.
    """
    education = candidate.get("education", [])
    if not education:
        return 0.3  # neutral for missing education

    tier_scores = {
        "tier_1": 1.0,
        "tier_2": 0.75,
        "tier_3": 0.50,
        "tier_4": 0.30,
        "unknown": 0.40,
    }

    relevant_fields = {
        "computer science", "cs", "machine learning", "artificial intelligence",
        "data science", "information technology", "it",
        "mathematics", "statistics", "applied mathematics",
        "electrical engineering", "electronics",
        "computational linguistics",
    }

    degree_scores = {
        "ph.d": 1.0, "phd": 1.0,
        "m.tech": 0.9, "m.e.": 0.85, "m.s.": 0.85, "m.sc": 0.8,
        "mba": 0.5,
        "b.tech": 0.7, "b.e.": 0.65, "b.sc": 0.6,
    }

    best_score = 0.0

    for edu in education:
        tier = edu.get("tier", "unknown")
        field = edu.get("field_of_study", "").lower()
        degree = edu.get("degree", "").lower()

        tier_s = tier_scores.get(tier, 0.4)

        # Field relevance
        field_s = 0.3  # default for irrelevant field
        for rf in relevant_fields:
            if rf in field:
                field_s = 1.0
                break

        # Degree level
        degree_s = 0.5  # default
        for d, s in degree_scores.items():
            if d in degree:
                degree_s = s
                break

        score = tier_s * 0.4 + field_s * 0.4 + degree_s * 0.2
        best_score = max(best_score, score)

    return _clamp(best_score)


# ─────────────────────────────────────────────────────────
# Axis 6: Logistics Fit
# ─────────────────────────────────────────────────────────

def score_logistics(candidate: dict) -> float:
    """
    Score based on location, notice period, salary expectations,
    and work mode preferences.
    """
    profile = candidate.get("profile", {})
    signals = candidate.get("redrob_signals", {})

    # ── Location ──
    location = profile.get("location", "").lower()
    country = profile.get("country", "").lower()
    willing = signals.get("willing_to_relocate", False)

    if country == "india":
        # Check if in preferred city
        in_preferred = any(city in location for city in PREFERRED_CITIES)
        in_region = any(region in location for region in PREFERRED_REGIONS)
        if in_preferred:
            loc_score = 1.0
        elif in_region:
            loc_score = 0.85
        else:
            loc_score = 0.7 if willing else 0.6
    else:
        loc_score = 0.4 if willing else 0.15

    # ── Notice period ──
    notice = signals.get("notice_period_days", 60)
    if notice <= NOTICE_IDEAL:
        notice_score = 1.0
    elif notice <= NOTICE_OK:
        notice_score = 0.7
    elif notice <= NOTICE_LONG:
        notice_score = 0.5
    else:
        notice_score = 0.3

    # ── Salary ──
    salary_range = signals.get("expected_salary_range_inr_lpa", {})
    salary_min = salary_range.get("min", 0)
    salary_max = salary_range.get("max", 0)

    if salary_min > 0 and salary_max > 0:
        salary_mid = (salary_min + salary_max) / 2
        if SALARY_MIN_REASONABLE <= salary_mid <= SALARY_MAX_REASONABLE:
            salary_score = 0.8
        elif salary_mid < SALARY_MIN_REASONABLE:
            salary_score = 0.5  # might be too junior
        else:
            salary_score = 0.4  # might be too expensive
    else:
        salary_score = 0.5  # unknown

    # ── Work mode ──
    work_mode = signals.get("preferred_work_mode", "")
    mode_scores = {
        "hybrid": 1.0,    # matches JD perfectly
        "flexible": 0.9,
        "onsite": 0.8,
        "remote": 0.6,
    }
    mode_score = mode_scores.get(work_mode, 0.5)

    # ── Composite ──
    logistics = (
        loc_score * 0.40 +
        notice_score * 0.25 +
        salary_score * 0.20 +
        mode_score * 0.15
    )

    return _clamp(logistics)


# ─────────────────────────────────────────────────────────
# Composite scorer
# ─────────────────────────────────────────────────────────

def score_candidate(candidate: dict, relevance: float = 0.0) -> dict:
    """
    Compute all axis scores and the weighted composite for a candidate.

    Args:
        candidate: the candidate record.
        relevance: the BM25 + TF-IDF JD-match score in [0, 1], precomputed across the
            whole scored population by src.relevance.RelevanceScorer. Passed in (rather
            than computed here) because it needs corpus-level statistics.

    Returns a dict with individual axis scores, availability multiplier,
    and final composite score.
    """
    from src.config import WEIGHTS

    skills = score_skills(candidate)
    career = score_career(candidate)
    behavioral = score_behavioral(candidate)
    experience = score_experience(candidate)
    education = score_education(candidate)
    logistics = score_logistics(candidate)

    availability = compute_availability_multiplier(candidate)

    # Weighted composite (relevance is the free-text JD-match axis)
    raw_composite = (
        relevance * WEIGHTS["relevance"] +
        skills * WEIGHTS["skills"] +
        career * WEIGHTS["career"] +
        behavioral * WEIGHTS["behavioral"] +
        experience * WEIGHTS["experience"] +
        education * WEIGHTS["education"] +
        logistics * WEIGHTS["logistics"]
    )

    final_score = raw_composite * availability

    return {
        "relevance": round(relevance, 4),
        "skills": round(skills, 4),
        "career": round(career, 4),
        "behavioral": round(behavioral, 4),
        "experience": round(experience, 4),
        "education": round(education, 4),
        "logistics": round(logistics, 4),
        "availability_mult": round(availability, 4),
        "raw_composite": round(raw_composite, 4),
        "final_score": round(final_score, 4),
    }
