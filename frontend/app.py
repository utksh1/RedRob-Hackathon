"""Streamlit sandbox for ranking uploaded candidate files."""

import io
import json
import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.src.honeypot_detector import detect_honeypot
from backend.src.hard_filters import apply_hard_filters
from backend.src.scorers import score_candidate
from backend.src.ranker import rank_candidates
from backend.src.relevance import RelevanceScorer
from backend.src.jd_text import JD_TEXT

SAMPLE_PATH = "India_runs_data_and_ai_challenge/sample_candidates.json"


def _read_candidates(raw: bytes) -> list[dict]:
    text = raw.decode("utf-8").strip()
    if not text:
        return []
    if text[0] == "[":
        return json.loads(text)
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def run_pipeline_sample(candidates: list[dict], top_n: int):
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

st.set_page_config(page_title="RedRob Candidate Ranker", page_icon="🎯", layout="wide")
st.title("🎯 RedRob — Intelligent Candidate Ranker")
st.caption(
    "Ranks candidates for the **Senior AI Engineer** JD. BM25 + TF-IDF JD-relevance over "
    "free-text career history (not keyword lists), 6 structured axes, availability gating, "
    "and honest per-candidate reasoning. Pure-Python, CPU-only, no network."
)

with st.sidebar:
    st.header("Input")
    uploaded = st.file_uploader("Candidate file (.json array or .jsonl)", type=["json", "jsonl"])
    top_n_requested = st.number_input(
        "Top-N to show",
        min_value=1,
        max_value=1_000_000,
        value=100,
        step=10,
        help="Enter any Top-N. It will be capped to the number of candidates that survive filtering.",
    )
    use_sample = st.button("Use bundled 50-candidate sample")
    st.markdown("---")
    st.markdown(
        "Upload candidates matching the dataset schema, or click the sample button. "
        "Local Streamlit upload limit is configured to 5 GB."
    )

candidates = None
if uploaded is not None:
    candidates = _read_candidates(uploaded.read())
elif use_sample:
    with open(SAMPLE_PATH, "rb") as f:
        candidates = _read_candidates(f.read())

if candidates:
    top_n = min(int(top_n_requested), len(candidates))

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
