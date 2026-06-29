# RedRob Hackathon — Intelligent Candidate Discovery & Ranking

## Overview

A CPU-only, dependency-light candidate ranking system for the **Senior AI Engineer
(Founding Team)** role at Redrob AI. It processes 100,000 candidate profiles and produces
a ranked top-100 list with per-candidate reasoning, in under a minute.

The system's core idea: the JD explicitly warns that *"the right answer is not find
candidates whose skills section contains the most AI keywords — that's a trap."* So
ranking is driven by a **BM25 + TF-IDF relevance match of the full job description against
each candidate's free-text career history**, with an optional precomputed sentence-embedding
cosine signal for paraphrased experience — rewarding people who *describe* real
retrieval/ranking work in plain language, not those who merely list buzzwords.

## Quick Start

```bash
# Ranking path: Python 3.10+, no network, CPU only
python rank.py --candidates ./India_runs_data_and_ai_challenge/candidates.json --out ./submission.csv

# Validate the output against the submission spec
python validate_submission.py --submission submission.csv \
    --candidates ./India_runs_data_and_ai_challenge/candidates.json
```

**Performance:** ~43 seconds on a standard machine (well inside the 5-minute budget).

### Optional Embedding Relevance Signal

The default ranking path is dependency-light and uses BM25 + TF-IDF only. To add dense
semantic matching for paraphrases, generate sentence embeddings offline, then point
`rank.py` at the generated artifacts:

```bash
# Offline precompute: may download a local model and can run longer than 5 minutes
python -m pip install -r requirements-embeddings.txt
python -m backend.src.embedding_precompute \
    --candidates ./India_runs_data_and_ai_challenge/candidates.json \
    --out-dir ./embedding_artifacts

# Rank step: still CPU-only, no network, no model loading
REDROB_EMBEDDING_DIR=./embedding_artifacts \
python rank.py --candidates ./India_runs_data_and_ai_challenge/candidates.json --out ./submission.csv
```

When the artifacts are present, relevance is blended as `0.4 × BM25 + 0.2 × TF-IDF +
0.4 × embedding cosine`. If the artifacts are absent or invalid, the ranker falls back
to BM25 + TF-IDF automatically.

## Architecture

### 5-Stage Pipeline

```
Stage 1: Honeypot Detection  → flag ~96 impossible profiles (impossible timelines, fake expertise)
Stage 2: Hard Filters        → eliminate ~47K disqualified candidates (wrong career, wrong location)
Stage 3: Relevance + Scoring → BM25/TF-IDF (+ optional embeddings) + 6 structured axes
Stage 4: Composite Ranking   → weighted combination with availability gating
Stage 5: Top-100 + Reasoning → varied, concern-aware reasoning per candidate
```

### Scoring Axes (7 dimensions)

| Axis | Weight | What it measures |
|---|---|---|
| **Relevance (BM25 + TF-IDF + optional embeddings)** | 30% | Free-text match of the full JD against the candidate's summary + career descriptions |
| **Career Quality** | 22% | Product vs consulting, title relevance, description analysis |
| **Skills Relevance** | 16% | Tier-1/Tier-2 skill match with keyword-stuffer detection |
| **Behavioral Signals** | 14% | Platform activity, response rates, engagement, verification |
| **Experience Fit** | 12% | Gaussian fit to the 5-9 year sweet spot |
| **Education** | 3% | Institution tier, field relevance |
| **Logistics** | 3% | Location, notice period, salary alignment, work mode |

An **availability multiplier** (0.3–1.0) gates the entire score — unreachable candidates
(stale profiles, low response rates) are penalized regardless of qualifications, per the
JD's explicit instruction.

### Key Design Decisions

1. **Relevance over keywords**: The JD warns that keyword-stuffed skills lists are traps.
   The relevance axis scores the *meaning overlap* between the JD and a candidate's own
   description text via BM25 + TF-IDF — surfacing "plain-language" candidates who describe
   real ranking/retrieval work without the buzzwords, and demoting adjacent ML (sentiment,
   fraud, CV-only) that merely shares keywords.

2. **No hosted models, no network**: BM25 + TF-IDF are implemented in pure Python, and
   optional embedding artifacts are precomputed offline. The ranking step remains fully
   reproducible inside a CPU-only container — satisfying the spec's Stage-3 reproduction
   constraints (no GPU, no API calls, ≤5 min).

3. **Honest, varied reasoning**: Each reasoning cites concrete facts from the profile,
   names the JD requirement evidenced, and surfaces real concerns (long notice, inactivity,
   off-core work). Structure and tone scale with rank — directly targeting the Stage-4
   manual-review checks.

4. **Behavioral gating**: A "perfect-on-paper" candidate who hasn't logged in for months
   with a 5% response rate is effectively unavailable; the availability multiplier drops them.

## Ablation

We **cannot** compute true NDCG locally — the ground truth is hidden until results close.
So this ablation reports the measurable proxies: how much the ranking changed and the
reasoning-quality signals the Stage-4 reviewer checks.

| Variant | Top-100 vs baseline | Score spread | Reasoning |
|---|---|---|---|
| Keyword-only (baseline) | — | 0.0613 | 1 template, 0 concerns |
| + Relevance (BM25/TF-IDF) | **18 of 100 changed** | 0.0501 | (unchanged) |
| + Precision reranker + reasoning | 4/10 top-10 baseline overlap | 0.0990 | **100 unique, 100 structures, 68/100 surface a concern term** |

What the 18-candidate churn did: relevance **promoted** profiles describing
*"owned the ranking layer for an e-commerce search product"*, *"semantic search over 500K
documents"*, *"RAG chatbot"*, *"personalization infrastructure"*, and **demoted** profiles
describing *"sentiment analysis / document classification"*, *"fraud detection"*, and
*"computer vision for image moderation"* (the JD explicitly disfavors CV-only). That is the
"read between the lines" distinction the JD asks for.

> Note on score spread: NDCG ignores score magnitude (only order matters), so spread is a
> diagnostic, not a goal. It narrows slightly because the final top-100 all saturate the
> relevance axis. The meaningful change is the ranking churn, not the number range.

## Project Structure

```
├── rank.py                     # Entry point — CLI interface
├── validate_submission.py      # Local replica of the spec format validator
├── submission_metadata.yaml    # Portal metadata (team fields are TODO)
├── backend/
│   └── src/
│       ├── config.py           # All tunable constants + weights
│       ├── jd_text.py          # The JD as the relevance query
│       ├── relevance.py        # BM25 + TF-IDF + optional embedding JD-relevance scorer
│       ├── embedding_precompute.py # Offline sentence-embedding artifact builder
│       ├── honeypot_detector.py
│       ├── hard_filters.py
│       ├── scorers.py
│       ├── ranker.py
│       └── pipeline.py
├── frontend/
│   └── app.py                  # Streamlit sandbox/demo
├── docs/
│   ├── planning/               # Upgrade plan, tech stack, assessments
│   ├── deck/                   # Track 1 methodology deck draft
│   └── extracted/              # Extracted challenge/JD/reference docs
├── submission.csv              # Output
├── submission_baseline.csv     # Keyword-only baseline (ablation reference)
├── requirements.txt            # Streamlit sandbox dependency
├── requirements-embeddings.txt # Optional offline embedding precompute dependencies
└── India_runs_data_and_ai_challenge/
    └── candidates.json         # 100K candidate pool (487 MB, not committed)
```

## Compute Environment

- Python 3.10+
- Any machine with ≥4 GB RAM
- CPU only — no GPU required
- No network access during ranking
- Optional embeddings are generated before ranking; `rank.py` only reads local artifacts
- Streamlit is only needed for the optional frontend sandbox

## AI Tools Used

Declared honestly per hackathon rules. Claude (Claude Code) was used as a development
assistant for code scaffolding, JD analysis, and documentation. All engineering decisions,
the relevance design, tuning, and system architecture were human-directed.

## Results Summary

| Metric | Value |
|---|---|
| Total candidates | 100,000 |
| Honeypots detected / excluded from top-100 | 96 / 96 |
| Hard-filtered | 47,293 |
| Scored | 52,611 |
| Output | 100 candidates |
| Execution time | ~43s |
| Score range | 0.9000 – 0.9990 |

### Top-10 Preview

| Rank | Title | Company | Years | Score |
|---|---|---|---|---|
| 1 | Senior Machine Learning Engineer | Zomato | 7.2 | 0.9681 |
| 2 | Senior NLP Engineer | Niramai | 7.8 | 0.9664 |
| 3 | Applied ML Engineer | Dream11 | 6.7 | 0.9636 |
| 4 | Lead AI Engineer | Razorpay | 6.7 | 0.9620 |
| 5 | Senior AI Engineer | Apple | 5.9 | 0.9589 |
| 6 | NLP Engineer | Aganitha | 6.6 | 0.9572 |
| 7 | Senior AI Engineer | Netflix | 7.8 | 0.9566 |
| 8 | Senior Machine Learning Engineer | Genpact AI | 6.1 | 0.9564 |
| 9 | Senior Data Scientist | Google | 6.5 | 0.9530 |
| 10 | Junior ML Engineer | Aganitha | 6.1 | 0.9530 |

All top-100 candidates are ML/AI engineers at product companies with relevant experience,
zero honeypots, and strong behavioral signals.
