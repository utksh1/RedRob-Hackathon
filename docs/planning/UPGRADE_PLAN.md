# Mid → Top: Detailed Upgrade Plan

> **Purpose:** A concrete, code-level implementation plan to move the Track 1 ranker from
> "Mid" (rule-based keyword heuristics) to "Top" (semantic relevance + honest reasoning +
> differentiated scoring + complete deliverables).
>
> **Status:** Phase 2 precision pass is implemented and validated. The ranker now has
> BM25/TF-IDF relevance, precision subfeatures, conservative hard-filter rescue, a
> top-300 precision reranker, varied reasoning, regenerated `submission.csv`, GitHub PR,
> and the reorganized `backend/`, `frontend/`, `docs/` project layout.
> Remaining work is mostly submission packaging: team metadata, sandbox deployment URL,
> and final PDF deck export.
>
> **Read first:** [HONEST_ASSESSMENT.md](HONEST_ASSESSMENT.md) for the gap analysis,
> [submission_spec_extracted.md](submission_spec_extracted.md) for the scoring rules,
> [job_description_extracted.md](job_description_extracted.md) for what "fit" means.

---

## Baseline (locked) — measured on the full 100K, 2026-06-08

The keyword-heuristic system, reproduced end-to-end on the real `candidates.json` (100,000 rows).
This is the **"before"** column for the ablation table.

| Metric | Baseline value |
|---|---|
| Runtime (full 100K, CPU) | **13.7 s** (budget 300 s) |
| Honeypots detected / excluded | 96 / 96 |
| Hard-filtered | 47,293 |
| Scored | 52,611 |
| Format valid | ✅ 100 rows, unique IDs, ranks 1–100, non-increasing |
| **Score spread (rank1 − rank100)** | **0.0613** (0.9542 → 0.8929) |
| Mean score | 0.9112 |
| Reasoning frame | **single template** for all 100 (slot-fills only) |

Phase-1 targets: (a) widen spread well beyond **0.0613**; (b) replace the single reasoning
template with genuinely varied, concern-bearing text. Artifact saved as `submission_baseline.csv`.

---

## Phase 1 validation — measured on the full 100K

The upgraded BM25/TF-IDF relevance + varied-reasoning run completed successfully on the full
`candidates.json` pool and regenerated `submission.csv`.

| Metric | Phase 1 value |
|---|---|
| Runtime (full 100K, CPU) | **20.5 s** (budget 300 s) |
| Honeypots detected / excluded | 96 / 96 |
| Hard-filtered | 47,293 |
| Scored | 52,611 |
| Format valid | ✅ `validate_submission.py` passed |
| **Score spread (rank1 − rank100)** | **0.0501** (0.9681 → 0.9180) |
| Top-10 overlap vs baseline | 8 / 10 |
| Top-10 promoted vs baseline | `CAND_0010257`, `CAND_0043860` |
| Honeypots in final top-100 | 0 |
| Reasoning variation | 100 unique strings; 88 punctuation skeletons |

Note: the upgraded ranking improves semantic evidence and reasoning quality, but the top-100
numeric spread is narrower than the baseline. Keep this as an honest diagnostic; do not stretch
scores artificially unless the scoring spec explicitly rewards score calibration.

---

## Phase 2 precision pass — measured on the full 100K

The current submitted ranking path is **FitRank v1 + precision reranker**. It keeps the
interpretable BM25/TF-IDF and structured scoring backbone, then adds transparent precision
features and reranks only the top 300 candidates.

| Metric | Phase 2 value |
|---|---|
| Runtime (full 100K, CPU) | **42.7 s** (budget 300 s) |
| Honeypots detected / excluded | 96 / 96 |
| Hard-filtered | 47,293 |
| Scored | 52,611 |
| Format valid | ✅ `validate_submission.py` passed |
| **Score spread (rank1 − rank100)** | **0.0990** (0.9990 → 0.9000) |
| Top-10 overlap vs baseline | 4 / 10 |
| Honeypots in final top-100 | 0 |
| Reasoning variation | 100 unique strings; 100 punctuation skeletons |

Implemented precision signals:

- Separate **vector/semantic search** from generic search.
- Separate **production retrieval/ranking** from toy/demo RAG.
- Reward evaluation evidence: **NDCG, MRR, MAP, A/B tests, offline/online evaluation**.
- Reward production/deployment evidence: **real users, latency, monitoring, index refresh,
  embedding drift, quality regression**.
- Penalize **toy/demo RAG** and **CV/speech-only** profiles when they lack retrieval/ranking depth.
- Add conservative rescue for odd-title candidates only when strong retrieval/ranking evidence exists.

Current tradeoff: runtime increased from 13.7 s baseline to 42.7 s, still only ~14% of the
5-minute budget. The added time buys a more precise top-10/top-50 ordering, which matters most
because the scoring metric heavily weights NDCG@10 and NDCG@50.

---

## 0. Why we are "Mid" (proven in the current code)

The tier table is Redrob's own self-estimate ([HONEST_ASSESSMENT.md](HONEST_ASSESSMENT.md)),
not official scoring — but the diagnosis is confirmed by the code:

| # | Root cause | Where in code | Effect on score |
|---|---|---|---|
| 1 | **Keyword matching disguised as understanding** — all "semantic" functions are substring matches against fixed word lists | [scorers.py:65](../../backend/src/scorers.py#L65) `_skill_match`, [scorers.py:89](../../backend/src/scorers.py#L89) `_score_description_text` | Misses the JD's "plain-language Tier 5" candidates → directly lowers NDCG |
| 2 | **`_score_description_text` returns `0.0` when no keywords hit** | [scorers.py:105](../../backend/src/scorers.py#L105) | A real retrieval engineer who avoids buzzwords scores zero on description |
| 3 | **No ranking model** — composite is a fixed hand-weighted linear sum | [scorers.py:635](../../backend/src/scorers.py#L635) | Nothing optimizes NDCG@10 (50% of grade); top-10 ordering is near-arbitrary |
| 4 | **Score spread is 0.8929–0.9542** (0.06 across 100) | symptom of #3 | Poor differentiation among top candidates = weak NDCG |
| 5 | **Templated reasoning**, one f-string for all 100, zero honest concerns | [ranker.py:113](../../backend/src/ranker.py#L113) | Explicitly penalized at Stage 4 manual review |
| 6 | **Missing mandatory deliverables**: sandbox, `submission_metadata.yaml`, GitHub push, PDF deck, real git history | — | Eliminated at Stage 1/3 regardless of score |

### How the scoring pipeline shapes priorities
- **Stage 2 (automatic NDCG scoring) gates everything.** Reasoning and deck are only
  reviewed at **Stage 4**, and only for top-N submissions. So **ranking quality comes first** —
  it's what gets you *into* Stage 4.
- Composite metric: `0.50·NDCG@10 + 0.30·NDCG@50 + 0.15·MAP + 0.05·P@10`.
  **80% of the grade is the quality + ordering of your top 50.**
- Therefore: **#1–#4 (ranking) move your actual score. #5–#6 (reasoning/deliverables)
  win among teams who already rank well.** Both are needed; ranking is sequenced first.

---

## 1. Hard environment constraints (do not violate)

From [submission_spec_extracted.md](submission_spec_extracted.md) §3:

| Constraint | Limit | Implication for this plan |
|---|---|---|
| Runtime | ≤ 5 min wall-clock for the **ranking step** | Pre-computation (e.g. embeddings) may exceed this **only if done offline** and shipped as artifacts; the `rank.py` step that emits the CSV must fit in 5 min |
| Memory | ≤ 16 GB | 100K profiles in RAM is fine; keep vectors compact (float32) |
| Compute | CPU only, no GPU | No GPU inference in `rank.py` |
| Network | **Off** during ranking | No hosted LLM/API calls. Any model must be local |
| Disk | ≤ 5 GB intermediate | Pre-computed embeddings for 100K × 384-dim float32 ≈ 150 MB — safe |
| Submissions | 3 max, last valid counts | Validate locally before every upload |

### Current dependency reality (verified)
- Python **3.14.5**, **numpy 2.4.6** installed. **No scikit-learn, no scipy, no lightgbm.**
- The repo's current selling point is **"zero dependencies, pure Python"** ([README.md](../README.md)).

**Decision:** Preserve the zero/low-dependency, fully-reproducible ethos where possible, because
reproducibility is a Stage-3 gate and a stated judging value. Two viable tracks:

- **Track A (recommended, low-risk):** Implement **BM25 + TF-IDF cosine in pure Python/numpy**.
  No new heavy deps, stays "reproducible in a clean container," runs in seconds.
- **Track B (higher ceiling, more risk):** Add **pre-computed sentence embeddings**
  (`bge-small-en-v1.5`, 384-dim) generated **offline**, shipped as a `.npy` artifact; `rank.py`
  loads vectors and does cosine — no model load at rank time. Requires `sentence-transformers` +
  `torch` **only in the offline pre-compute script**, documented separately so the rank step
  stays clean.

Start with **Track A**. Add **Track B** as a second relevance signal if time allows.

---

## 2. Data contract (from `candidate_schema.json`)

Fields the new code will rely on (all confirmed present in the schema):

- `profile.summary`, `profile.headline`, `profile.current_title`, `profile.current_company`,
  `profile.years_of_experience`, `profile.location`, `profile.country`, `profile.current_industry`
- `career_history[]`: `title`, `company`, `description`, `duration_months`, `is_current`,
  `start_date`, `end_date`
- `skills[]`: `name`, `proficiency`, `endorsements`, `duration_months`
- `education[]`: `degree`, `field_of_study`, `tier`, `end_year`
- `redrob_signals`: all 23 signals (see [redrob_signals_doc_extracted.md](redrob_signals_doc_extracted.md))

> **No ground-truth labels are provided** (scoring is against a hidden truth). This is the key
> reason a supervised LTR model (LambdaMART) needs **pseudo-labels** — see §4.

---

## 3. Target architecture

```
Load 100K candidates
   │
[Stage 1] Honeypot detection            (KEEP as-is — already good, 96 caught)
   │
[Stage 2] Hard filters                  (KEEP unchanged for Phase 1 — see §3.4)
   │
[Stage 3] Feature extraction
   │   ├─ existing 6 axes (skills, career, behavioral, exp, education, logistics)
   │   └─ relevance + precision features
   │       ├─ BM25(JD, profile_text) + TFIDF cosine [+ optional embedding cosine]
   │       ├─ vector/search/evaluation/production hits
   │       └─ toy-RAG and CV/speech-only risk flags
   │
[Stage 4] Scoring & ranking
   │   ├─ weighted blend incl. relevance and precision bonus/penalty
   │   └─ top-300 precision rerank (implemented)
   │
[Stage 5] Reasoning generation          (REWRITE — varied + honest concerns)
   │
Output CSV  +  validate_submission.py  +  metadata + deck
```

### 3.1 NEW module: `backend/src/relevance.py` (the core upgrade)

**Responsibility:** Produce a continuous JD-relevance score per candidate from *free text*,
not keyword lists. This is the single highest-leverage change.

**Inputs**
- `JD_TEXT`: the full job description text, stored as a constant (extracted from
  [job_description_extracted.md](job_description_extracted.md)). Include the "what we actually need"
  and "ideal candidate" paragraphs — they carry the real signal.
- Per candidate, a concatenated **profile document**:
  ```
  doc = headline + summary
      + " ".join(current_title repeated for emphasis)
      + " ".join(role.title + role.description for role in career_history)
      + " ".join(skill.name for skill in skills)
  ```
  Weight recent roles more (e.g. repeat current-role description ×2).

**Algorithm (Track A — pure Python/numpy)**
1. **Tokenize**: lowercase, strip punctuation, split on whitespace, drop stopwords. Keep a small
   custom stopword list (no NLTK dependency). Keep technical tokens like `bm25`, `c++`, `a/b`.
2. **Build corpus statistics in one pass**: document frequencies `df[term]`, doc lengths,
   `avgdl`. Vocab built from the corpus (not the JD only).
3. **BM25 score** of `JD_TEXT` against each candidate doc:
   `score = Σ_term∈JD idf(term) · (tf·(k1+1)) / (tf + k1·(1 − b + b·|d|/avgdl))`,
   with `k1=1.5`, `b=0.75`. `idf(term) = ln((N − df + 0.5)/(df + 0.5) + 1)`.
4. **TF-IDF cosine** as a second view: build sparse tf-idf vectors (dict-based), cosine vs the
   JD tf-idf vector. Catches overlap BM25's saturation misses.
5. **Normalize** each signal to [0,1] across the *scored* population (min-max or rank-based;
   rank-based is robust to outliers and naturally widens spread).
6. Return `{"bm25": x, "tfidf_cos": y, "relevance": blend}` where
   `relevance = 0.6·bm25_norm + 0.4·tfidf_norm`.

**Performance:** One pass to build stats, one pass to score. For ~53K post-filter docs this is a
few seconds in pure Python; vectorize the hot loop with numpy where practical. Well within budget.

**Why it fixes the trap:** A candidate who wrote *"built a system that recommends products to
users based on browsing history and tuned it with offline NDCG before an A/B test"* shares many
high-IDF terms with the JD (`recommends`, `NDCG`, `A/B`, `offline`, `tuned`) **without** containing
the exact tokens in `DESC_KEYWORDS_CORE`. BM25/TF-IDF reward that overlap; the current code scores
it 0.0.

**Track B add-on (optional):** `backend/src/embed_precompute.py` (offline, not run by `rank.py`):
- Load `BAAI/bge-small-en-v1.5` via `sentence-transformers`, encode `JD_TEXT` and every candidate
  doc, save `embeddings.npy` (id-aligned) + `jd_vector.npy`.
- `rank.py` loads these and computes cosine — no model at rank time, network stays off.
- Document this clearly in README as a pre-compute step (spec §10.3 explicitly allows it).
- Blend: `relevance = 0.4·bm25 + 0.2·tfidf + 0.4·embed_cos`.

### 3.2 Changes to `backend/src/scorers.py`

- Add `relevance` to the composite. Re-balance `WEIGHTS` so career/skills no longer double-count
  keyword presence. Proposed starting weights (tune later):
  ```python
  WEIGHTS = {
      "relevance":  0.30,   # NEW — free-text JD match
      "career":     0.22,   # was 0.30
      "skills":     0.16,   # was 0.25
      "behavioral": 0.14,   # was 0.20
      "experience": 0.12,   # was 0.15
      "education":  0.03,   # was 0.05
      "logistics":  0.03,   # was 0.05
  }  # sum = 1.00
  ```
- Keep the **availability multiplier** ([scorers.py:400](../../backend/src/scorers.py#L400)) — it correctly
  encodes the JD's "not actually available" point. Consider softening floor from 0.3 only after
  measuring its effect on spread.
- Fix `_score_description_text` so "no keywords" is not the same as "negative" — but this becomes
  secondary once `relevance` carries the semantic load.

### 3.3 Score differentiation (fixes the 0.06 spread)
- Rank-normalize the relevance signal (step 5 above) so it spans the full [0,1] before blending.
- After computing composites for all scored candidates, **spread is a diagnostic, not a target** —
  don't artificially stretch. The relevance axis naturally widens it because BM25 varies widely.
- Sanity check post-run: top-100 score range should be noticeably wider than 0.06.

### 3.4 Hard-filter rescue (implemented conservatively)
- `filter_pure_non_technical` ([hard_filters.py:70](../../backend/src/hard_filters.py#L70)) currently uses
  keyword hits. Risk: it drops a genuine engineer with an odd title.
- Current implementation runs a cheap lexical rescue check before this hard filter rejects a
  negative-title profile. It rescues only candidates with multiple core retrieval/ranking hits,
  strong production/evaluation support, and low toy/CV-only risk. Entire-career consulting,
  impossible location, and zero-experience filters remain hard disqualifiers.

---

## 4. Optional future ceiling — Learning-to-Rank (LambdaMART)

> Higher ceiling, higher risk. Only after Phase 1 ships and is validated. Requires `lightgbm`.

**Problem:** no ground-truth labels. **Solution:** pseudo-labels from confident rules.
1. **Construct graded pseudo-labels (0–3)** from strong, JD-derived signals:
   - tier 3: India-based product-company ML/AI engineer, 5–9 yrs, high relevance, real
     retrieval/ranking terms in descriptions, available.
   - tier 0: honeypots + hard-filtered + bottom-relevance.
   - tiers 1–2: graded interpolation.
2. **Features**: the 6 axes + relevance sub-signals + raw signals (notice, recency, etc.).
3. **Train** `LGBMRanker(objective="lambdarank")`, **group = the single JD** (or synthetic
   sub-groups), **GroupKFold**, report internal NDCG.
4. **Use the model only to rerank** the top ~1–2K from Phase 1 (keeps it fast + safe).
5. **Honesty in the deck/README:** state plainly that labels weren't provided, so pseudo-labels
   were derived from the JD — judges reward this over pretending.

**Caveat:** pseudo-label LTR can *amplify* the rule bias it's trained on. Treat as an experiment;
keep Phase 1 as the shippable baseline. Do **not** submit an LTR run you can't beat-test against
Phase 1 on sanity checks.

---

## 5. Reasoning rewrite (`backend/src/ranker.py`) — passes Stage 4

Current: one f-string template for all 100 ([ranker.py:113](../../backend/src/ranker.py#L113)). The spec
([submission_spec_extracted.md](submission_spec_extracted.md) §3) checks 6 things; we must satisfy
each **deterministically, with no network** (LLM is off-limits at rank time):

| Stage-4 check | How the new generator satisfies it |
|---|---|
| Specific facts | Pull real values: exact years, current title/company, 2–3 named skills actually present, a concrete signal value (response rate %, notice days) |
| JD connection | Map to JD requirements: name the matched requirement ("production retrieval", "ranking eval", "product-company ML") that the candidate's text actually evidences |
| Honest concerns | **Detect and state** real gaps: notice > 60d, last active > 90d, < 4 or > 11 yrs, all-recent tenure < 18mo (title-chaser), consulting stint, no GitHub, weak relevance on an otherwise strong profile |
| No hallucination | Only reference skills/companies/terms found in the candidate's own JSON; never invent |
| Variation | Build from **components chosen by the candidate's actual profile** (which strengths/concerns fire), plus 3–4 sentence-frame variants selected by a hash of candidate_id → structurally different rows |
| Rank consistency | Tone scales with rank band: ranks 1–10 lead with strengths; 11–50 balanced; 51–100 explicitly hedged ("adjacent fit; included for X but Y is a concern") |

**Design:** a small rule engine that emits `(strength_phrases, concern_phrases)` from the profile,
then composes 1–2 sentences using a frame picked deterministically. No two rows identical; every
claim traceable to data. Keep ≤ ~300 chars.

**Example targets** (illustrative, must be data-derived):
- Rank 3: *"Senior ML Engineer, 6.7 yrs at a product company; description shows production vector
  search and offline NDCG evaluation — matches the JD's retrieval + ranking-eval asks. Responsive
  (88%), 30-day notice."*
- Rank 78: *"Strong NLP background but most retrieval work is 4+ years old and last active 140 days
  ago; included as adjacent fit given product-company ML experience, with availability as the main
  concern."*

---

## 6. Missing deliverables (Stage 1 & 3 gates)

| Deliverable | Spec ref | Plan |
|---|---|---|
| `validate_submission.py` run | §4, §6 | Run the bundle's validator on `submission.csv` before every upload; fix any format issue. Add a `make validate` shortcut |
| `submission_metadata.yaml` | §10.3 | Fill from `submission_metadata_template.yaml`: team, contacts, GitHub URL, sandbox link, AI tools (declare Claude honestly), compute env, ≤200-word methodology |
| Sandbox / demo link | §10.5 | **Streamlit** app: upload ≤100-candidate sample → run pipeline → show ranked table + reasoning. Deploy on Streamlit Cloud (free). Must run end-to-end in ≤5 min on CPU |
| GitHub repo + real history | §5 Stage 4 | Push with **meaningful commit sequence** (EDA → baseline → relevance → reasoning → tuning), not one dump. The honest-assessment + this plan are good early commits |
| PDF methodology deck | §10.2 (recommended) | 6–8 slides: problem → trap → architecture → relevance method → reasoning approach → results/sanity → reproducibility. Reuse the SkillProof/strategy decks' style |
| README update | §10.3 | Document the single reproduce command, the optional offline pre-compute step, and the dependency list honestly |

---

## 7. Validation (no ground truth — validate by proxy)

We can't compute true NDCG locally (truth is hidden). Validate everything we *can*:

1. **Format** (auto-validator): exactly 100 rows, ranks 1–100 once each, unique IDs, scores
   non-increasing, all IDs exist in candidates file, UTF-8 CSV.
2. **Budget**: full run < 300 s on CPU; print elapsed.
3. **Honeypots**: 0 detected-honeypots appear in top-100 (cross-check against Stage-1 set).
4. **Trap resistance**: no negative-title keyword-stuffers in top-100; manually confirm a known
   plain-language candidate now ranks higher than before.
5. **Spread**: top-100 score range measured against 0.0613 baseline; current Phase 2 is 0.0990.
6. **Reasoning audit**: sample 10 rows → all distinct, all facts traceable to JSON, concerns
   present on weaker ranks, tone matches rank (mirror the exact Stage-4 checklist).
7. **Ablation table** (for the deck): keyword-only vs +relevance vs +reasoning — show the
   top-10 churn and spread change. This is the "numbers" judges look for.

---

## 8. Sequenced task list (do in this order)

**Phase 1 — Ranking quality**
1. [x] Extract `JD_TEXT` constant into `backend/src/jd_text.py` from the JD doc.
2. [x] Build `backend/src/relevance.py`: tokenizer + corpus stats + BM25 + TF-IDF cosine.
3. [x] Wire `relevance` into `score_candidate` + rebalance `WEIGHTS`; normalize the signal.
4. [x] Re-run on the sample (50) for correctness, then full set; check budget + spread.
5. [x] Add conservative hard-filter rescue for strong retrieval/ranking evidence.

**Phase 2 — Reasoning (Stage-4 win)**
6. [x] Rewrite `generate_reasoning`: strength/concern rule engine + deterministic frame variation.
7. [x] Run the §7.6 reasoning audit.

**Phase 3 — Precision pass**
8. [x] Add relevance subfeatures: BM25 norm, TF-IDF norm, core JD hits, vector hits,
   evaluation hits, production hits, toy-RAG risk, CV/speech-only risk.
9. [x] Add precision bonus/penalty into `score_candidate`.
10. [x] Add top-300 soft reranker focused on production retrieval, vector search, and evaluation.
11. [x] Regenerate and validate `submission.csv`.

**Phase 4 — Submission deliverables**
12. [x] Reorganize project into `backend/`, `frontend/`, `docs/`.
13. [x] Push to GitHub PR with real commit history.
14. [x] Update README, tech stack, methodology deck draft, and metadata summary.
15. [ ] Fill team/contact fields in `submission_metadata.yaml`.
16. [ ] Deploy Streamlit sandbox and add `sandbox_demo_link`.
17. [ ] Export final PDF methodology deck.

**Phase 5 — Optional extra tuning**
18. [ ] Generate `top100_audit.csv` and `top300_audit.csv`.
19. [ ] Manually audit false positives/false negatives in top 150.
20. [ ] Tune top-300 reranker weights only if audit shows clear errors.
21. [ ] (If time) Pre-computed `bge-small` embeddings as a 3rd relevance signal.
22. [ ] (If time) LambdaMART rerank on pseudo-labels (§4), only if it beats Phase 2 sanity checks.

---

## 9. Open items

- [x] **Full dataset presence.** `India_runs_data_and_ai_challenge/candidates.json` is present
  and contains the full 100K pool as line-delimited JSON despite the `.json` extension.
- [x] **Dependency policy.** Phase 1 keeps Track A pure-Python at rank time. Optional embedding
  artifacts are supported only if precomputed and present; no hosted calls are used.
- [ ] **Submission identity.** Team name, contacts, and sandbox URL still need user input in
  `submission_metadata.yaml`.
- [x] **GitHub PR.** Current PR: `https://github.com/Shivam990q/RedRob-Hackathon/pull/1`.
- [ ] **`REFERENCE_DATE`** is hard-coded to 2026-06-01 ([config.py:13](../../backend/src/config.py#L13));
  confirm it matches the dataset's "now" so recency math is correct.
- [ ] **Registration/deadline** confusion (8 vs 28 June) noted in strategy docs — confirm the real
  Track 1 deadline so the build schedule is safe.

---

## 10. Risk notes

- **Pseudo-label LTR can hurt.** It learns our own rule bias. Keep Phase 1 as the safe baseline;
  only submit LTR if it demonstrably improves sanity checks. (3-submission cap means we can't
  experiment freely on the live scorer.)
- **No live feedback.** Scores are revealed only at the end (spec §8). All tuning is local/by-proxy
  — over-tuning to our own heuristics is the main danger; lean on the relevance signal and honest
  reasoning, which are robust, over clever weight-fiddling.
- **Reproducibility is a hard gate.** Any artifact `rank.py` needs (embeddings, indexes) must be in
  the repo or produced by a documented script; the rank step must run clean, offline, ≤5 min.
- **Further tuning should be evidence-led.** The current reranker makes a large top-10 change.
  Do not keep adjusting weights blindly; generate audit CSVs, inspect the candidates, and only
  change weights for clear false-positive/false-negative patterns.
