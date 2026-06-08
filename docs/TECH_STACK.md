# Tech Stack

This project is intentionally lightweight: the ranking step must run offline, CPU-only,
and under the 5-minute hackathon limit. The stack below separates the production
submission path from the optional demo/sandbox path.

## Ranking Engine

| Layer | Technology | Purpose |
|---|---|---|
| Language | Python 3.10+ | Single runtime for ranking, validation, and sandbox logic |
| Core dependencies | Python standard library | Keeps `rank.py` reproducible with no install step |
| Candidate loading | JSON / JSONL parser | Supports the full `candidates.json` JSONL file and JSON-array samples |
| Relevance model | Pure-Python BM25 + TF-IDF | Scores free-text JD overlap without hosted APIs or heavy ML frameworks |
| Structured scoring | Rule-based 7-axis scorer | Relevance, career, skills, behavioral, experience, education, logistics |
| Ranking | Deterministic weighted composite | Sorts by final score with candidate ID tie-breaks |
| Reasoning | Deterministic rule engine | Generates varied, fact-grounded strengths and honest concerns |
| Validation | Custom Python validator | Checks CSV format, row count, rank order, score order, and candidate IDs |

## Frontend / Sandbox

| Layer | Technology | Purpose |
|---|---|---|
| UI framework | Streamlit | Lightweight hosted demo for the mandatory sandbox requirement |
| Frontend components | Streamlit widgets | File upload, Top-N slider, metrics, ranked table, CSV download |
| Backend execution | Same Python pipeline modules | The sandbox calls the real ranking/scoring/reasoning code, not a duplicate implementation |
| Input format | JSON array or JSONL | Upload up to 100 candidates matching the challenge schema |
| Output | Interactive table + downloadable CSV | Shows rank, score, profile context, and reasoning |
| Hosting target | Streamlit Community Cloud | Free deployment from GitHub for the sandbox link |

## Data And Artifacts

| Artifact | Role |
|---|---|
| `India_runs_data_and_ai_challenge/candidates.json` | Full 100K candidate pool; JSONL despite `.json` extension |
| `India_runs_data_and_ai_challenge/sample_candidates.json` | 50-candidate JSON-array sample for sandbox/local tests |
| `submission.csv` | Final top-100 ranked output |
| `submission_baseline.csv` | Baseline output used for ablation comparison |
| `submission_metadata.yaml` | Portal metadata; team/contact/GitHub/sandbox fields still need final values |
| `docs/11_DECK_Track1_Methodology.md` | Methodology deck draft |

## Optional Future Stack

These are not required for the current Phase 1 submission, but they are compatible with
the architecture if time allows.

| Option | Technology | Use |
|---|---|---|
| Dense semantic relevance | Precomputed sentence-transformer embeddings | Add embedding cosine as a third relevance signal while keeping ranking offline |
| Embedding storage | `.npy` matrix + ID map | Load precomputed vectors without model inference during `rank.py` |
| Learning-to-rank experiment | LightGBM LambdaMART | Optional reranker from pseudo-labels; higher risk because no ground-truth labels are provided |

## Deployment / Repro Commands

```bash
# Final ranking submission
python rank.py \
  --candidates ./India_runs_data_and_ai_challenge/candidates.json \
  --out ./submission.csv

# Validate output
python validate_submission.py \
  --submission submission.csv \
  --candidates ./India_runs_data_and_ai_challenge/candidates.json

# Local sandbox
pip install streamlit
streamlit run app.py
```

## Current Next Step

The ranking path is already implemented and validated. The next practical step is to
finish the submission deliverables:

1. Fill `submission_metadata.yaml` with team name, contact, GitHub URL, and sandbox URL.
2. Push the repo to GitHub.
3. Deploy `app.py` on Streamlit Community Cloud and paste that URL into the metadata.
4. Export or polish the methodology deck from `docs/11_DECK_Track1_Methodology.md`.
5. Run the final `rank.py` + `validate_submission.py` commands once more before upload.
