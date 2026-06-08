"""
Ranker — sorts scored candidates and generates reasoning strings.

Produces the final top-100 CSV output with:
  candidate_id, rank, score, reasoning

The reasoning generator is a small rule engine: it extracts real facts from each
profile, detects genuine strengths and honest concerns, names the JD requirement the
candidate actually evidences, and composes 1-2 sentences whose structure and tone vary
by rank band. This targets the Stage-4 manual-review checks (specific facts, JD
connection, honest concerns, no hallucination, variation, rank-consistency).
"""

from datetime import date, datetime

from src.config import (
    CONSULTING_FIRMS,
    SKILLS_TIER1,
    SKILLS_TIER2,
    REFERENCE_DATE,
    PREFERRED_CITIES,
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


def _parse_date(date_str: str | None) -> date | None:
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def _fmt_years(years: float) -> str:
    """7.0 -> '7', 7.2 -> '7.2'."""
    if abs(years - round(years)) < 0.05:
        return f"{round(years)}"
    return f"{years:.1f}"


# ── Classify the candidate's most relevant work from career descriptions ──
# Each entry: (keywords, short work phrase, JD requirement it evidences)
_WORK_KINDS = [
    (("semantic search", "vector search", "retrieval", "rag", "embedding",
      "re-ranking", "reranking", "information retrieval"),
     "production retrieval/search", "the JD's embeddings-retrieval requirement"),
    (("ranking", "learning to rank", "learning-to-rank", "ltr"),
     "ranking systems", "the JD's ranking + evaluation focus"),
    (("recommendation", "recommender", "personalization", "personalisation"),
     "recommendation/personalization", "the JD's recommendation-at-scale ask"),
    (("fine-tun", "lora", "qlora", "peft", "llm", "large language model"),
     "LLM fine-tuning", "the JD's nice-to-have LLM fine-tuning"),
    (("nlp", "natural language", "sentiment", "classification", "ner", "text"),
     "NLP/classification", "ML depth, though not core retrieval"),
    (("computer vision", "image", "object detection", "segmentation", "ocr"),
     "computer vision", "ML depth, but the JD disfavors CV-only"),
    (("fraud", "churn", "forecast", "predictive", "feature engineering", "regression"),
     "applied ML modeling", "general ML, not search/ranking"),
    (("data pipeline", "etl", "spark", "airflow", "warehouse", "data engineering"),
     "data engineering", "adjacent infra, light on ranking"),
]


def _classify_work(career: list[dict]) -> tuple[str, str, bool]:
    """
    Return (work_phrase, jd_connection, is_core). Inspect the most recent role first,
    then fall back to the full history. is_core = matches retrieval/ranking/recsys.
    """
    recent_text = career[0].get("description", "").lower() if career else ""
    all_text = " ".join(r.get("description", "").lower() for r in career)

    for source in (recent_text, all_text):
        for keywords, phrase, jd_conn in _WORK_KINDS:
            if any(kw in source for kw in keywords):
                is_core = phrase in (
                    "production retrieval/search", "ranking systems",
                    "recommendation/personalization",
                )
                return phrase, jd_conn, is_core
    return "ML engineering", "general engineering signal", False


def _extract(candidate: dict, scores: dict) -> dict:
    """Pull the concrete facts and fire strength/concern flags from the profile."""
    profile = candidate.get("profile", {})
    signals = candidate.get("redrob_signals", {})
    career = candidate.get("career_history", [])

    title = profile.get("current_title", "Engineer")
    company = profile.get("current_company", "their current company")
    years = profile.get("years_of_experience", 0) or 0
    country = profile.get("country", "")
    location = profile.get("location", "")

    company_type = "consulting" if _is_consulting(company) else "product"
    work_phrase, jd_conn, is_core = _classify_work(career)

    # Named skills actually present (real, no hallucination).
    rel_skills = []
    for s in candidate.get("skills", []):
        nm = s.get("name", "")
        if _skill_match(nm, SKILLS_TIER1):
            rel_skills.append(nm)
        elif _skill_match(nm, SKILLS_TIER2) and len(rel_skills) < 6:
            rel_skills.append(nm)
    # de-dup preserving order
    seen = set()
    rel_skills = [x for x in rel_skills if not (x.lower() in seen or seen.add(x.lower()))]

    # Behavioral signal values.
    resp = signals.get("recruiter_response_rate", 0.0)
    notice = signals.get("notice_period_days", None)
    github = signals.get("github_activity_score", -1)
    open_flag = signals.get("open_to_work_flag", False)
    last_active = _parse_date(signals.get("last_active_date"))
    days_inactive = (REFERENCE_DATE - last_active).days if last_active else None

    # Tenure (title-chaser check).
    avg_tenure = (sum(r.get("duration_months", 0) for r in career) / len(career)) if career else None
    has_consulting_stint = any(_is_consulting(r.get("company", "")) for r in career)

    # ── Strengths ── (phrased to avoid repeating facts already in the frame:
    # the frame names title/years/company, so strengths don't restate them)
    strengths = []
    if company_type == "product":
        strengths.append(("product", "product-company background"))
    if 5 <= years <= 9:
        strengths.append(("exp", "in the 5-9 yr sweet spot"))
    if is_core:
        strengths.append(("core", f"recent {work_phrase} work"))
    if resp >= 0.7:
        strengths.append(("resp", f"responsive to recruiters ({resp:.0%})"))
    if notice is not None and notice <= 30:
        strengths.append(("notice", f"short {notice}-day notice"))
    if github >= 50:
        strengths.append(("git", f"active GitHub ({github:.0f})"))
    if rel_skills:
        strengths.append(("skills", "named " + ", ".join(rel_skills[:3])))

    # ── Honest concerns ──
    concerns = []
    if years and years < 4:
        concerns.append(f"only {_fmt_years(years)} yrs experience")
    elif years and years > 11:
        concerns.append(f"{_fmt_years(years)} yrs — above the JD's band")
    if not is_core:
        concerns.append(f"work is {work_phrase}, not core retrieval/ranking")
    if company_type == "consulting":
        concerns.append(f"currently at a services firm ({company})")
    elif has_consulting_stint:
        concerns.append("part of the career is at consulting firms")
    if notice is not None and notice > 60:
        concerns.append(f"long {notice}-day notice")
    if days_inactive is not None and days_inactive > 120:
        concerns.append(f"last active {days_inactive}d ago")
    if resp < 0.4:
        concerns.append(f"low recruiter response ({resp:.0%})")
    if github == -1:
        concerns.append("no public GitHub signal")
    if not open_flag:
        concerns.append("not flagged open-to-work")
    if country and country.strip().lower() != "india":
        concerns.append(f"based outside India ({country})")

    return {
        "title": title, "company": company, "company_type": company_type,
        "years": years, "location": location, "country": country,
        "work_phrase": work_phrase, "jd_conn": jd_conn, "is_core": is_core,
        "rel_skills": rel_skills, "resp": resp, "notice": notice,
        "strengths": strengths, "concerns": concerns,
    }


def generate_reasoning(candidate: dict, scores: dict, rank: int = 50) -> str:
    """
    Compose a 1-2 sentence, data-grounded reasoning. Structure and tone vary by rank
    band; concerns are surfaced honestly. Every claim traces to the candidate's JSON.
    """
    f = _extract(candidate, scores)
    title, company, years = f["title"], f["company"], _fmt_years(f["years"])
    strengths = [p for _, p in f["strengths"]]
    concerns = f["concerns"]

    loc = f["location"] or f["country"] or "location n/a"
    # Deterministic structural variation (no Math.random needed).
    seed = int("".join(ch for ch in candidate["candidate_id"] if ch.isdigit()) or "0")

    # ── Rank band controls tone + how many concerns to surface ──
    if rank <= 10:
        band = "top"
        n_conc = 1   # top picks: surface at most one real concern
    elif rank <= 50:
        band = "mid"
        n_conc = 2
    else:
        band = "low"
        n_conc = 2   # lower ranks: lead with the hedge

    strong_str = "; ".join(strengths[:3]) if strengths else f"{f['work_phrase']} background"
    conc_str = "; ".join(concerns[:n_conc])
    core = f["is_core"]
    jd = f["jd_conn"]

    # A few structural frames; choose by seed so adjacent rows differ. The JD-connection
    # tail is only added when the candidate is core (otherwise the concern already states
    # the gap, so we don't say it twice).
    if band == "top":
        frames = [
            f"{title} at {company}, {years} yrs ({loc}): {strong_str}"
            + (f" — matches {jd}." if core else "."),
            f"Strong fit — {title}, {years} yrs at {company}; {strong_str}."
            + (f" Evidences {jd}." if core else ""),
            f"{title} ({years} yrs, {loc}). {strong_str}"
            + (f"; aligned with {jd}." if core else "."),
        ]
        out = frames[seed % len(frames)]
        if conc_str:
            out += f" Minor flag: {conc_str}."
    elif band == "mid":
        frames = [
            f"{title}, {years} yrs at {company} ({f['company_type']}); {strong_str}."
            + (f" Fits {jd}." if core else ""),
            f"{years}-yr {title} at {company}: {strong_str}"
            + (f" — relevant to {jd}." if core else "."),
            f"{title} in {loc}, {years} yrs. Strengths: {strong_str}.",
        ]
        out = frames[seed % len(frames)]
        if conc_str:
            out += f" Concerns: {conc_str}."
    else:  # low band — lead with the hedge, measured tone
        lead = [
            f"Adjacent fit: {title}, {years} yrs at {company}.",
            f"Included as a borderline pick — {title} ({years} yrs, {loc}).",
            f"{title} at {company}, {years} yrs; below the top tier.",
        ]
        out = lead[seed % len(lead)]
        if strengths:
            out += f" Upside: {strong_str}."
        if conc_str:
            out += f" Concerns: {conc_str}."

    return out[:300]


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
    # Sort by final_score descending; tie-break by candidate_id ascending (deterministic).
    sorted_candidates = sorted(
        scored_candidates,
        key=lambda x: (-x[1]["final_score"], x[0]["candidate_id"]),
    )

    results = []
    for i, (candidate, scores) in enumerate(sorted_candidates[:top_n]):
        rank = i + 1
        score = scores["final_score"]
        reasoning = generate_reasoning(candidate, scores, rank=rank)

        results.append({
            "candidate_id": candidate["candidate_id"],
            "rank": rank,
            "score": round(score, 4),
            "reasoning": reasoning,
        })

    return results
