"""
Honeypot Detector — identifies ~80 candidates with impossible profiles.

Honeypots are forced to relevance tier 0 in the ground truth.
If >10% of your top-100 are honeypots → disqualified.

Detection signals:
- Expert proficiency in skills with 0 duration
- Career duration vs date range mismatches
- Experience years vs career timeline impossibilities
- Skill assessment score vs proficiency contradictions
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from backend.src.config import (
    REFERENCE_DATE,
    HONEYPOT_DURATION_MISMATCH_MONTHS,
    HONEYPOT_EXPERT_ZERO_DURATION_THRESHOLD,
    HONEYPOT_EXPERT_SKILLS_VS_EXPERIENCE_RATIO,
    HONEYPOT_EXPERIENCE_TIMELINE_MISMATCH_YEARS,
    HONEYPOT_ASSESSMENT_VS_PROFICIENCY_GAP,
)


def _parse_date(date_str: str | None) -> date | None:
    """Parse a date string (YYYY-MM-DD) into a date object."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def _check_expert_zero_duration(candidate: dict) -> int:
    """Count skills claimed as 'expert' with 0 months of duration."""
    count = 0
    for skill in candidate.get("skills", []):
        if (skill.get("proficiency") == "expert" and
                skill.get("duration_months", 0) == 0):
            count += 1
    return count


def _check_career_duration_mismatch(candidate: dict) -> int:
    """Count career entries where stated duration wildly mismatches date range."""
    flags = 0
    for role in candidate.get("career_history", []):
        start = _parse_date(role.get("start_date"))
        end = _parse_date(role.get("end_date"))
        stated_months = role.get("duration_months", 0)

        if start and end:
            # Compute actual months between dates
            actual_months = (end.year - start.year) * 12 + (end.month - start.month)
            if actual_months < 0:
                # End date before start date — impossible
                flags += 2
            elif abs(actual_months - stated_months) > HONEYPOT_DURATION_MISMATCH_MONTHS:
                flags += 1
        elif start and role.get("is_current", False):
            # Current role: compare duration to time since start
            actual_months = ((REFERENCE_DATE.year - start.year) * 12 +
                             (REFERENCE_DATE.month - start.month))
            if actual_months < 0:
                flags += 2  # Start date in the future
            elif abs(actual_months - stated_months) > HONEYPOT_DURATION_MISMATCH_MONTHS:
                flags += 1
    return flags


def _check_experience_vs_timeline(candidate: dict) -> bool:
    """Check if years_of_experience is wildly inconsistent with career history."""
    claimed_years = candidate.get("profile", {}).get("years_of_experience", 0)
    career = candidate.get("career_history", [])

    if not career:
        return False

    # Find the earliest start date
    earliest_start = None
    for role in career:
        start = _parse_date(role.get("start_date"))
        if start and (earliest_start is None or start < earliest_start):
            earliest_start = start

    if earliest_start:
        # Max possible years = reference_date - earliest_start
        max_possible_years = (REFERENCE_DATE - earliest_start).days / 365.25
        if claimed_years > max_possible_years + HONEYPOT_EXPERIENCE_TIMELINE_MISMATCH_YEARS:
            return True

    # Also check total duration_months vs claimed years
    total_months = sum(r.get("duration_months", 0) for r in career)
    total_years = total_months / 12
    # Allow for overlapping roles, but flag extreme mismatches
    if claimed_years > 0 and total_years > claimed_years * 2.5:
        return True

    return False


def _check_assessment_contradictions(candidate: dict) -> int:
    """Count skills where assessment scores contradict proficiency claims."""
    flags = 0
    assessments = (candidate.get("redrob_signals", {})
                   .get("skill_assessment_scores", {}))

    skill_profs = {}
    for skill in candidate.get("skills", []):
        skill_profs[skill["name"].lower()] = skill.get("proficiency", "beginner")

    for skill_name, score in assessments.items():
        prof = skill_profs.get(skill_name.lower(), "beginner")
        # Expert claims but terrible assessment score
        if prof in ("expert", "advanced") and score < HONEYPOT_ASSESSMENT_VS_PROFICIENCY_GAP:
            flags += 1
    return flags


def _check_impossible_education(candidate: dict) -> bool:
    """Check for impossible education timelines."""
    education = candidate.get("education", [])
    claimed_years = candidate.get("profile", {}).get("years_of_experience", 0)

    for edu in education:
        end_year = edu.get("end_year", 0)
        if end_year > 0 and claimed_years > 0:
            # If they graduated recently but claim many years of experience
            years_since_grad = REFERENCE_DATE.year - end_year
            if claimed_years > years_since_grad + 3:  # 3 year buffer for concurrent work
                return True
    return False


def _check_too_many_experts(candidate: dict) -> bool:
    """Flag candidates with unrealistically many expert-level skills."""
    skills = candidate.get("skills", [])
    expert_count = sum(1 for s in skills
                       if s.get("proficiency") == "expert")
    years = candidate.get("profile", {}).get("years_of_experience", 1)

    if years < 1:
        years = 1

    # More than N expert skills per year of experience is suspicious
    if (expert_count >= 5 and
            expert_count / years > HONEYPOT_EXPERT_SKILLS_VS_EXPERIENCE_RATIO):
        return True

    # Expert in 10+ skills with very low total duration
    if expert_count >= 10:
        avg_duration = sum(s.get("duration_months", 0) for s in skills
                          if s.get("proficiency") == "expert") / expert_count
        if avg_duration < 6:
            return True

    return False


def detect_honeypot(candidate: dict) -> tuple[bool, list[str]]:
    """
    Determine if a candidate is a honeypot (impossible profile).

    Returns:
        (is_honeypot: bool, reasons: list[str])
    """
    signals = []
    score = 0  # accumulate suspicion

    # Check 1: Expert skills with zero duration
    expert_zero = _check_expert_zero_duration(candidate)
    if expert_zero >= HONEYPOT_EXPERT_ZERO_DURATION_THRESHOLD:
        signals.append(f"{expert_zero} expert skills with 0 months duration")
        score += expert_zero * 2

    # Check 2: Career duration mismatches
    duration_flags = _check_career_duration_mismatch(candidate)
    if duration_flags > 0:
        signals.append(f"career duration mismatch (severity: {duration_flags})")
        score += duration_flags * 3

    # Check 3: Experience vs timeline
    if _check_experience_vs_timeline(candidate):
        signals.append("experience years inconsistent with career timeline")
        score += 4

    # Check 4: Assessment contradictions
    assess_flags = _check_assessment_contradictions(candidate)
    if assess_flags >= 2:
        signals.append(f"{assess_flags} assessment-proficiency contradictions")
        score += assess_flags * 2

    # Check 5: Impossible education timeline
    if _check_impossible_education(candidate):
        signals.append("education timeline impossible")
        score += 3

    # Check 6: Too many expert skills
    if _check_too_many_experts(candidate):
        signals.append("unrealistically many expert-level skills")
        score += 4

    # Threshold: need multiple signals or one very strong signal
    is_honeypot = score >= 4
    return is_honeypot, signals
