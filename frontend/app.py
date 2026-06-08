"""
Streamlit sandbox for the RedRob candidate ranker.

Satisfies the submission spec's mandatory sandbox/demo requirement (§10.5): a hosted
environment that accepts a small candidate sample (≤100), runs the *real* ranking
pipeline end-to-end, and shows the ranked table with reasoning — all on CPU, no network,
well within the 5-minute budget.

Run locally:
    pip install streamlit
    streamlit run frontend/app.py

Deploy (free): push to GitHub, then point Streamlit Community Cloud at `frontend/app.py`.

Notes:
  - This calls the same backend/src/ pipeline that produces submission.csv — no separate logic.
  - It loads only the uploaded sample (or the bundled 50-candidate sample), never the
    full 487 MB pool, so it stays fast and within free-tier memory.
"""

import io
import json

import streamlit as st

from backend.src.honeypot_detector import detect_honeypot
from backend.src.hard_filters import apply_hard_filters
from backend.src.scorers import score_candidate
from backend.src.ranker import rank_candidates
from backend.src.relevance import RelevanceScorer
from backend.src.jd_text import JD_TEXT

SAMPLE_PATH = "India_runs_data_and_ai_challenge/sample_candidates.json"


def _read_candidates(raw: bytes) -> list[dict]:
    """Accept either a JSON array or JSONL (one object per line)."""
    text = raw.decode("utf-8").strip()
    if not text:
        return []
    if text[0] == "[":
        return json.loads(text)
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def run_pipeline_sample(candidates: list[dict], top_n: int):
    """The same five stages as rank.py, on a small in-memory sample."""
    stats = {"total": len(candidates)}

    honeypot_ids = {c["candidate_id"] for c in candidates if detect_honeypot(c)[0]}
    stats["honeypots"] = len(honeypot_ids)
    remaining = [c for c in candidates if c["candidate_id"] not in honeypot_ids]

    filtered = [c for c in remaining if apply_hard_filters(c)[0]]
    stats["filtered_out"] = len(remaining) - len(filtered)
    stats["scored"] = len(filtered)

    if not filtered:
        return [], stats

    relevance_scorer = RelevanceScorer(JD_TEXT).fit(filtered)
    rel = relevance_scorer.relevance_scores()
    details = relevance_scorer.feature_scores()
    scored = [
        (
            c,
            score_candidate(
                c,
                relevance=rel.get(c["candidate_id"], 0.0),
                relevance_detail=details.get(c["candidate_id"], {}),
            ),
        )
        for c in filtered
    ]
    results = rank_candidates(scored, top_n=min(top_n, len(scored)))
    return results, stats


# ─────────────────────────────────────────────────────────
st.set_page_config(page_title="RedRob Candidate Ranker", page_icon="🎯", layout="wide")
st.title("🎯 RedRob — Intelligent Candidate Ranker")
st.caption(
    "Ranks candidates for the **Senior AI Engineer** JD. BM25 + TF-IDF JD-relevance over "
    "free-text career history (not keyword lists), 6 structured axes, availability gating, "
    "and honest per-candidate reasoning. Pure-Python, CPU-only, no network."
)

with st.sidebar:
    st.header("Input")
    uploaded = st.file_uploader("Candidate sample (.json array or .jsonl)", type=["json", "jsonl"])
    top_n = st.slider("Top-N to show", 5, 100, 20)
    use_sample = st.button("Use bundled 50-candidate sample")
    st.markdown("---")
    st.markdown(
        "Upload ≤100 candidates matching the dataset schema, or click the sample button. "
        "The full 100K pool is ranked offline via `python rank.py`."
    )

candidates = None
if uploaded is not None:
    candidates = _read_candidates(uploaded.read())
elif use_sample:
    with open(SAMPLE_PATH, "rb") as f:
        candidates = _read_candidates(f.read())

if candidates:
    if len(candidates) > 100:
        st.warning(f"{len(candidates)} candidates uploaded — using the first 100 (sandbox limit).")
        candidates = candidates[:100]

    with st.spinner(f"Ranking {len(candidates)} candidates…"):
        results, stats = run_pipeline_sample(candidates, top_n)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Candidates", stats["total"])
    c2.metric("Honeypots flagged", stats["honeypots"])
    c3.metric("Hard-filtered", stats["filtered_out"])
    c4.metric("Ranked", len(results))

    if results:
        profiles = {c["candidate_id"]: c["profile"] for c in candidates}
        rows = []
        for r in results:
            p = profiles.get(r["candidate_id"], {})
            rows.append({
                "Rank": r["rank"],
                "Score": r["score"],
                "Title": p.get("current_title", ""),
                "Company": p.get("current_company", ""),
                "Years": p.get("years_of_experience", ""),
                "Reasoning": r["reasoning"],
            })
        st.dataframe(rows, use_container_width=True, hide_index=True)

        csv = io.StringIO()
        csv.write("candidate_id,rank,score,reasoning\n")
        for r in results:
            reasoning = r["reasoning"].replace('"', '""')
            csv.write(f'{r["candidate_id"]},{r["rank"]},{r["score"]},"{reasoning}"\n')
        st.download_button("⬇ Download ranked CSV", csv.getvalue(),
                           file_name="sandbox_submission.csv", mime="text/csv")
    else:
        st.info("No candidates survived filtering in this sample.")
else:
    st.info("⬅ Upload a candidate sample or click **Use bundled 50-candidate sample** to begin.")
