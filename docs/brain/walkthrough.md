# Walkthrough: RedRob Candidate Ranking System

## What Was Built

A **pure-Python multi-dimensional candidate ranking system** for the RedRob Hackathon's "Intelligent Candidate Discovery & Ranking Challenge". The system processes 100K candidate profiles against a Senior AI Engineer JD and produces a top-100 ranked CSV.

## Files Created

| File | Purpose |
|---|---|
| [rank.py](file:///c:/Users/Rose/Videos/FUTURE/RedRob%20Hackathon/rank.py) | CLI entry point with self-validation |
| [src/config.py](file:///c:/Users/Rose/Videos/FUTURE/RedRob%20Hackathon/src/config.py) | All tunable constants (skills taxonomy, title classifications, keyword sets, weights, thresholds) |
| [src/honeypot_detector.py](file:///c:/Users/Rose/Videos/FUTURE/RedRob%20Hackathon/src/honeypot_detector.py) | 6-check honeypot detection (expert-zero-duration, career-date mismatches, timeline conflicts, assessment contradictions, impossible education, too-many-experts) |
| [src/hard_filters.py](file:///c:/Users/Rose/Videos/FUTURE/RedRob%20Hackathon/src/hard_filters.py) | JD-based disqualification (all-consulting career, impossible location, zero experience, non-technical keyword stuffers) |
| [src/scorers.py](file:///c:/Users/Rose/Videos/FUTURE/RedRob%20Hackathon/src/scorers.py) | 6-axis scoring engine + availability multiplier |
| [src/ranker.py](file:///c:/Users/Rose/Videos/FUTURE/RedRob%20Hackathon/src/ranker.py) | Ranking + reasoning generation |
| [src/pipeline.py](file:///c:/Users/Rose/Videos/FUTURE/RedRob%20Hackathon/src/pipeline.py) | 5-stage pipeline orchestrator |
| [README.md](file:///c:/Users/Rose/Videos/FUTURE/RedRob%20Hackathon/README.md) | Comprehensive documentation for Stage 3 reproduction |
| [submission.csv](file:///c:/Users/Rose/Videos/FUTURE/RedRob%20Hackathon/submission.csv) | Final output |

## Key Results

| Metric | Value |
|---|---|
| Execution time | **36 seconds** (budget: 300s) |
| Honeypots detected | 96 (expected ~80) |
| Hard-filtered | 47,293 (47.3% eliminated) |
| Scored | 52,611 |
| Output | 100 candidates, all ML/AI engineers at product companies |
| Score range | 0.8929 – 0.9542 |

## Validation

✅ Exactly **100 rows** in output CSV
✅ **Unique candidate_ids** (no duplicates)  
✅ **Scores in descending order** (rank 1 has highest score)  
✅ **Ranks 1 to 100** (1-indexed)  
✅ **Zero non-technical titles** in top-100 (no HR Managers, Accountants, etc.)  
✅ **All product companies** in top-100 (99 product, 1 mixed consulting with ML work)  
✅ **Completed in 36s** (12% of 5-minute budget)  
✅ **Zero external dependencies** (pure Python 3.10+)  

## What Makes This Approach Strong

1. **Reads between the lines**: The JD explicitly warns against keyword matching. Our system weights career descriptions (what they *did*) over skill lists (what they *claim*).

2. **Catches traps**: The sample_submission.csv ranks HR Managers and Accountants with AI keywords. Our system correctly filters these as keyword stuffers.

3. **Behavioral gating**: Unavailable candidates (stale profiles, low response rates) are penalized via the availability multiplier, per the JD's emphasis.

4. **No ML model overhead**: Runs in 36s on CPU with zero dependencies, making it trivially reproducible for Stage 3.

## Next Steps for Submission

1. **Sandbox**: Deploy on Streamlit Cloud or HuggingFace Spaces for the required demo link
2. **GitHub repo**: Push all code to a public/private repository
3. **Portal metadata**: Team name, contact info, AI tools declaration
4. **submission_metadata.yaml**: Fill in the template from the hackathon bundle
