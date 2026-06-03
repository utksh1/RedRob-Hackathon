# RedRob Hackathon — Intelligent Candidate Discovery & Ranking

## Overview

A rule-based multi-dimensional candidate ranking system for the **Senior AI Engineer (Founding Team)** role at Redrob AI. Processes 100,000 candidate profiles and produces a ranked top-100 list with reasoning.

## Quick Start

```bash
# No external dependencies required — runs on pure Python 3.10+
python rank.py --candidates ./India_runs_data_and_ai_challenge/candidates.jsonl --out ./submission.csv
```

**Performance:** ~36 seconds on a standard machine (well within the 5-minute budget).

## Architecture

### 5-Stage Pipeline

```
Stage 1: Honeypot Detection  → Flag ~96 impossible profiles (impossible timelines, fake expertise)
Stage 2: Hard Filters        → Eliminate ~47K disqualified candidates (wrong career, wrong location)
Stage 3: Multi-Dim Scoring   → Score remaining ~53K candidates on 6 axes
Stage 4: Composite Ranking   → Weighted combination with availability gating
Stage 5: Top-100 + Reasoning → Generate human-readable reasoning per candidate
```

### Scoring Axes (6 dimensions)

| Axis | Weight | What it measures |
|---|---|---|
| **Career Quality** | 30% | Product vs consulting, title relevance, description keyword analysis |
| **Skills Relevance** | 25% | Tier-1/Tier-2 skill match with keyword-stuffer detection |
| **Behavioral Signals** | 20% | Platform activity, response rates, engagement, verification |
| **Experience Fit** | 15% | Gaussian fit to 5-9 year sweet spot |
| **Education** | 5% | Institution tier, field relevance |
| **Logistics** | 5% | Location, notice period, salary alignment, work mode |

An **availability multiplier** (0.3–1.0) gates the entire score — unreachable candidates are penalized regardless of qualifications.

### Key Design Decisions

1. **Career descriptions > Skills lists**: The JD explicitly warns that keyword-stuffed skills lists are traps. Our system weights description analysis (35% of career score) over skill names.

2. **Keyword-stuffer detection**: Candidates with non-technical titles (HR Manager, Accountant) but high AI skill counts are penalized unless their career descriptions contain genuine ML/AI work.

3. **No ML models needed**: The JD is specific enough to encode as rules. This avoids the complexity of embedding models and keeps the system within the CPU-only, 5-minute constraint with zero dependencies.

4. **Behavioral gating**: A "perfect-on-paper" candidate who hasn't logged in for 6 months with a 5% response rate is effectively unavailable. The availability multiplier ensures these candidates drop in ranking.

## Project Structure

```
├── rank.py                     # Entry point — CLI interface
├── src/
│   ├── __init__.py
│   ├── config.py               # All tunable constants
│   ├── honeypot_detector.py    # Stage 1: impossible profile detection
│   ├── hard_filters.py         # Stage 2: JD-based disqualification
│   ├── scorers.py              # Stage 3: 6-axis scoring engine
│   ├── ranker.py               # Stage 4-5: ranking + reasoning
│   └── pipeline.py             # Orchestrates all stages
├── submission.csv              # Output
├── requirements.txt            # No external dependencies
└── India_runs_data_and_ai_challenge/
    ├── candidates.jsonl        # 100K candidate pool (487 MB)
    ├── candidate_schema.json
    ├── sample_candidates.json
    ├── sample_submission.csv
    ├── job_description.docx
    ├── submission_spec.docx
    └── redrob_signals_doc.docx
```

## Reproduction

```bash
# Single command to reproduce the submission CSV
python rank.py --candidates ./India_runs_data_and_ai_challenge/candidates.jsonl --out ./submission.csv

# With verbose output disabled
python rank.py --candidates ./India_runs_data_and_ai_challenge/candidates.jsonl --out ./submission.csv --quiet
```

## Compute Environment

- Python 3.10+ (standard library only, no pip install needed)
- Any machine with ≥4 GB RAM
- CPU only — no GPU required
- No network access during ranking

## AI Tools Used

Declared honestly per hackathon rules. AI tools were used as development assistants for:
- Code scaffolding and architecture design
- JD analysis and feature extraction
- All engineering decisions, tuning, and system design were human-directed.

## Results Summary

| Metric | Value |
|---|---|
| Total candidates | 100,000 |
| Honeypots detected | 96 |
| Hard-filtered | 47,293 |
| Scored | 52,611 |
| Output | 100 candidates |
| Execution time | 36s |
| Score range | 0.8929 – 0.9542 |

### Top-10 Preview

| Rank | Title | Company | Years | Score |
|---|---|---|---|---|
| 1 | Senior ML Engineer | Zomato | 7.2 | 0.9542 |
| 2 | Senior NLP Engineer | Niramai | 7.8 | 0.9518 |
| 3 | ML Engineer | Glance | 6.4 | 0.9495 |
| 4 | Applied ML Engineer | Dream11 | 6.7 | 0.9459 |
| 5 | Lead AI Engineer | Razorpay | 6.7 | 0.9443 |
| 6 | Senior AI Engineer | Apple | 5.9 | 0.9417 |
| 7 | NLP Engineer | Aganitha | 6.6 | 0.9386 |
| 8 | Senior ML Engineer | Genpact AI | 6.1 | 0.9378 |
| 9 | Senior AI Engineer | Netflix | 7.8 | 0.9369 |
| 10 | Staff ML Engineer | Yellow.ai | 8.6 | 0.9326 |

All top-100 candidates are ML/AI engineers at product companies with relevant experience, zero honeypots, and strong behavioral signals.
