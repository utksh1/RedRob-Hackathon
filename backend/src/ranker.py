"""Candidate ranking and per-candidate reasoning."""

from datetime import date, datetime

from backend.src.config import (
    CONSULTING_FIRMS,
    SKILLS_TIER1,
    SKILLS_TIER2,
    REFERENCE_DATE,
    PREFERRED_CITIES,
)


def _skill_match(name: str, keyword_set: set[str]) -> bool:
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


def _rotate(values: list[str], seed: int, limit: int = 3) -> list[str]:
    """Deterministically rotate evidence so repeated high-level profiles do not read identical."""
    if not values:
        return []
    start = seed % len(values)
    rotated = values[start:] + values[:start]
    return rotated[:limit]


def _sentence_list(values: list[str]) -> str:
    if not values:
        return ""
    if len(values) == 1:
        return values[0]
    if len(values) == 2:
        return f"{values[0]} and {values[1]}"
    return f"{', '.join(values[:-1])}, and {values[-1]}"


_WORK_KINDS = [
    (("vector search", "semantic search", "embedding search", "vector database",
      "faiss", "milvus", "pinecone", "weaviate", "qdrant"),
     "vector/semantic search", "the JD's vector retrieval requirement"),
    (("index refresh", "embedding drift", "retrieval-quality regression",
      "quality regression", "real users", "deployed retrieval", "production retrieval"),
     "production retrieval systems", "the JD's production retrieval requirement"),
    (("rag", "retrieval augmented", "retrieval-augmented"),
     "RAG/retrieval work", "the JD's retrieval requirement"),
    (("ranking", "learning to rank", "learning-to-rank", "ltr"),
     "ranking systems", "the JD's ranking + evaluation focus"),
    (("ndcg", "mrr", "map", "a/b test", "ab test", "offline evaluation"),
     "ranking evaluation", "the JD's evaluation-framework requirement"),
    (("recommendation", "recommender", "personalization", "personalisation"),
     "recommendation/personalization", "the JD's recommendation-at-scale ask"),
    (("fine-tun", "lora", "qlora", "peft", "llm", "large language model"),
     "LLM fine-tuning", "the JD's nice-to-have LLM fine-tuning"),
    (("nlp", "natural language", "sentiment", "classification", "ner", "text"),
     "NLP/classification", "ML depth, though not core retrieval"),
    (("speech recognition", "tts", "text to speech"),
     "speech ML", "ML depth, but the JD disfavors speech-only profiles"),
    (("computer vision", "image", "object detection", "segmentation", "ocr"),
     "computer vision", "ML depth, but the JD disfavors CV-only profiles"),
    (("fraud", "churn", "forecast", "predictive", "feature engineering", "regression"),
     "applied ML modeling", "general ML, not search/ranking"),
    (("data pipeline", "etl", "spark", "airflow", "warehouse", "data engineering"),
     "data engineering", "adjacent infra, light on ranking"),
]


def _classify_work(career: list[dict]) -> tuple[str, str, bool]:
    recent_text = career[0].get("description", "").lower() if career else ""
    all_text = " ".join(r.get("description", "").lower() for r in career)

    for source in (recent_text, all_text):
        for keywords, phrase, jd_conn in _WORK_KINDS:
            if any(kw in source for kw in keywords):
                is_core = phrase in (
                    "vector/semantic search", "production retrieval systems",
                    "ranking systems", "ranking evaluation",
                    "recommendation/personalization",
                )
                return phrase, jd_conn, is_core
    return "ML engineering", "general engineering signal", False


def _extract(candidate: dict, scores: dict) -> dict:
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

    rel_skills = []
    for s in candidate.get("skills", []):
        nm = s.get("name", "")
        if _skill_match(nm, SKILLS_TIER1):
            rel_skills.append(nm)
        elif _skill_match(nm, SKILLS_TIER2) and len(rel_skills) < 6:
            rel_skills.append(nm)
    seen = set()
    rel_skills = [x for x in rel_skills if not (x.lower() in seen or seen.add(x.lower()))]

    resp = signals.get("recruiter_response_rate", 0.0)
    notice = signals.get("notice_period_days", None)
    github = signals.get("github_activity_score", -1)
    open_flag = signals.get("open_to_work_flag", False)
    last_active = _parse_date(signals.get("last_active_date"))
    days_inactive = (REFERENCE_DATE - last_active).days if last_active else None

    avg_tenure = (sum(r.get("duration_months", 0) for r in career) / len(career)) if career else None
    has_consulting_stint = any(_is_consulting(r.get("company", "")) for r in career)
    relevance = scores.get("relevance", 0.0)
    availability = scores.get("availability_mult", 1.0)

    strengths = []
    if company_type == "product":
        strengths.append(("product", "product-company background"))
    if 5 <= years <= 9:
        strengths.append(("exp", "in the 5-9 yr sweet spot"))
    if is_core:
        strengths.append(("core", f"recent {work_phrase} work"))
    if scores.get("production_retrieval", 0.0) >= 0.85:
        strengths.append(("prodrel", "production-grade retrieval/ranking evidence"))
    if scores.get("evaluation_hits", 0.0) >= 1:
        strengths.append(("eval", "ranking evaluation evidence"))
    if scores.get("vector_hits", 0.0) >= 2:
        strengths.append(("vector", "vector-search/tooling depth"))
    if relevance >= 0.9:
        strengths.append(("rel", f"high JD text relevance ({relevance:.2f})"))
    if resp >= 0.7:
        strengths.append(("resp", f"responsive to recruiters ({resp:.0%})"))
    if notice is not None and notice <= 30:
        strengths.append(("notice", f"short {notice}-day notice"))
    if availability >= 0.95:
        strengths.append(("avail", "strong availability signals"))
    if github >= 50:
        strengths.append(("git", f"active GitHub ({github:.0f})"))
    if rel_skills:
        strengths.append(("skills", "named " + ", ".join(rel_skills[:3])))

    concerns = []
    if years and years < 4:
        concerns.append(f"only {_fmt_years(years)} yrs experience")
    elif years and years > 11:
        concerns.append(f"{_fmt_years(years)} yrs — above the JD's band")
    if not is_core:
        concerns.append(f"work is {work_phrase}, not core retrieval/ranking")
    if relevance < 0.75:
        concerns.append(f"lower JD text match ({relevance:.2f})")
    if scores.get("toy_rag_risk", 0.0) >= 0.5:
        concerns.append("possible toy/demo RAG signal")
    if scores.get("cv_speech_only_risk", 0.0) >= 0.5:
        concerns.append("CV/speech-heavy profile, light on retrieval")
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
        "strengths": strengths, "concerns": concerns, "relevance": relevance,
    }


def generate_reasoning(candidate: dict, scores: dict, rank: int = 50) -> str:
    """Compose a short, data-grounded reasoning string."""
    f = _extract(candidate, scores)
    title, company, years = f["title"], f["company"], _fmt_years(f["years"])
    strengths = [p for _, p in f["strengths"]]
    concerns = f["concerns"]

    loc = f["location"] or f["country"] or "location n/a"
    seed = int("".join(ch for ch in candidate["candidate_id"] if ch.isdigit()) or "0")

    if rank <= 10:
        band = "top"
        n_conc = 1
    elif rank <= 50:
        band = "mid"
        n_conc = 2
    else:
        band = "low"
        n_conc = 2

    chosen_strengths = _rotate(strengths, seed, limit=3)
    strong_str = _sentence_list(chosen_strengths) if chosen_strengths else f"{f['work_phrase']} background"
    conc_str = _sentence_list(_rotate(concerns, seed // 7, limit=n_conc))
    core = f["is_core"]
    jd = f["jd_conn"]
    strong_fit = core or len(strengths) >= 2

    if band == "top":
        if strong_fit:
            frames = [
                f"{title} at {company}, {years} yrs ({loc}): {strong_str}"
                + (f" - matches {jd}." if core else "."),
                f"Strong fit: {years}-yr {title} from {company}. Evidence: {strong_str}."
                + (f" JD link: {jd}." if core else ""),
                f"{title} ({years} yrs, {loc}) stands out for {strong_str}"
                + (f"; this supports {jd}." if core else "."),
                f"Ranked high for {strong_str}. Current role: {title} at {company}, {years} yrs"
                + (f"; clear fit for {jd}." if core else "."),
            ]
        else:
            frames = [
                f"{title}, {years} yrs at {company} ({loc}): {strong_str}.",
                f"Measured top-pool pick: {title} ({years} yrs at {company}); {strong_str}.",
                f"{title} in {loc}, {years} yrs. Main evidence: {strong_str}.",
            ]
        out = frames[seed % len(frames)]
        if conc_str:
            out += f" Note: {conc_str}."
    elif band == "mid":
        frames = [
            f"{title}, {years} yrs at {company} ({f['company_type']}); {strong_str}."
            + (f" Fits {jd}." if core else ""),
            f"{years}-yr {title} at {company}: {strong_str}"
            + (f" - relevant to {jd}." if core else "."),
            f"{title} in {loc}, {years} yrs. Strengths: {strong_str}.",
            f"Balanced pick: {strong_str}. Profile context: {title} at {company}, {years} yrs.",
            f"Useful fit for this JD because of {strong_str}; currently {title} at {company}.",
        ]
        out = frames[seed % len(frames)]
        if conc_str:
            out += f" Concerns: {conc_str}."
    else:
        lead = [
            f"Adjacent fit: {title}, {years} yrs at {company}.",
            f"Included as a borderline pick: {title} ({years} yrs, {loc}).",
            f"{title} at {company}, {years} yrs; below the top tier.",
            f"Lower-ranked but still relevant: {title}, {years} yrs at {company}.",
            f"Back-half selection from {loc}: {title} with {years} yrs.",
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
    """Sort scored candidates and produce the top-N output."""
    sorted_candidates = sorted(
        scored_candidates,
        key=lambda x: (-x[1]["final_score"], x[0]["candidate_id"]),
    )

    rerank_window = sorted_candidates[:300]
    tail = sorted_candidates[300:]

    def rerank_score(item: tuple[dict, dict]) -> float:
        _candidate, scores = item
        bonus = (
            scores.get("production_retrieval", 0.0) * 0.012
            + min(0.008, scores.get("evaluation_hits", 0.0) * 0.003)
            + min(0.006, scores.get("vector_hits", 0.0) * 0.001)
            + min(0.004, scores.get("production_hits", 0.0) * 0.001)
        )
        penalty = (
            scores.get("toy_rag_risk", 0.0) * 0.012
            + scores.get("cv_speech_only_risk", 0.0) * 0.015
        )
        return scores["final_score"] + bonus - penalty

    annotated_window = []
    for candidate, scores in rerank_window:
        scores = dict(scores)
        scores["rank_score"] = rerank_score((candidate, scores))
        annotated_window.append((candidate, scores))

    sorted_candidates = sorted(
        annotated_window,
        key=lambda x: (-x[1]["rank_score"], -x[1]["final_score"], x[0]["candidate_id"]),
    ) + tail

    top_slice = sorted_candidates[:top_n]
    raw_rank_scores = [scores.get("rank_score", scores["final_score"]) for _, scores in top_slice]
    lo = min(raw_rank_scores) if raw_rank_scores else 0.0
    hi = max(raw_rank_scores) if raw_rank_scores else 1.0
    span = hi - lo if hi > lo else 1.0

    results = []
    for i, (candidate, scores) in enumerate(top_slice):
        rank = i + 1
        raw_score = scores.get("rank_score", scores["final_score"])
        score = 0.90 + 0.099 * ((raw_score - lo) / span)
        reasoning = generate_reasoning(candidate, scores, rank=rank)

        results.append({
            "candidate_id": candidate["candidate_id"],
            "rank": rank,
            "score": round(score, 4),
            "reasoning": reasoning,
        })

    return results
