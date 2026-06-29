# DECK — Track 1 Methodology — Slide-by-Slide Ready Content

> **How to use:** paste each slide into Gamma/Canva, add the noted visual, export PDF as
> `RedRobRanker_IndiaRuns_[Team].pdf`. 8 slides. `[VISUAL: ...]` = put a diagram/chart there.
> All numbers are measured on the real 100K pool (see [README.md](../../README.md) ablation).

---

## SLIDE 1 — TITLE
```
Intelligent Candidate Ranker
We don't match keywords — we read what they actually built.

Track 1 · Senior AI Engineer JD · 100,000 candidates → ranked top 100
Team: [name] · India Runs 2026
```
`[VISUAL: clean title; a faint funnel 100,000 → 100. CPU-only · ~43s · standard-library ranker badge.]`

---

## SLIDE 2 — THE PROBLEM (the JD's own trap)
```
The JD says the obvious answer is a trap:
"The right answer is NOT the candidates with the most AI keywords —
 that's a trap we built into the dataset."

So two failures must be avoided:
• Keyword-stuffers — a "Marketing Manager" with 9 AI skills listed
• Missed "plain-language" talent — someone who built real retrieval
  but never wrote "RAG" or "Pinecone"
```
`[VISUAL: two resume cards side by side — one buzzword-stuffed (reject), one plain-language retrieval engineer (accept).]`

---

## SLIDE 3 — ARCHITECTURE (5 stages)
```
1. Honeypot detection   → flag ~96 impossible profiles (forced tier-0)
2. Hard filters         → drop ~47K (all-consulting, non-India no-relocate, non-technical)
3. Relevance + scoring  → BM25/TF-IDF JD match + 6 structured axes
4. Composite ranking    → weighted blend × availability gate
5. Reasoning            → varied, concern-aware, per candidate

Pure Python · CPU-only · no network · ~43s on 100K (budget: 300s)
```
`[VISUAL: left-to-right pipeline diagram, 100,000 → 96 honeypots out → 47K filtered → 52,611 scored → top 100.]`

---

## SLIDE 4 — THE CORE IDEA: relevance, not keywords
```
The ranking is driven by how the candidate's OWN words overlap the JD —
BM25 + TF-IDF over (summary + every career description), not a keyword list.

Why it beats keyword matching:
• "built a system that recommends items, tuned with offline NDCG before an
   A/B test" → scores high on NDCG, offline, A/B — with zero buzzwords
• A keyword-only system scores that candidate ZERO

Rare JD terms (embedding drift, hybrid retrieval, re-ranking) weigh most.
```
`[VISUAL: the example sentence with JD-overlapping terms highlighted; arrow to a high relevance bar.]`

---

## SLIDE 5 — RESULTS: precision reranking
```
We can't compute NDCG locally (ground truth is hidden) — so we measure the
ranking change and reasoning quality directly.

The precision pass reranks only the top 300, rewarding:
  PROMOTE   → vector/semantic search, NDCG/MRR/MAP, A/B tests,
              production deployment, index refresh, embedding drift
  PENALIZE  → toy/demo RAG, CV/speech-only profiles, generic applied ML

Result: only 4 of the baseline top-10 remain, but every top-100 row still validates,
with 0 honeypots and 100/100 distinct reasoning strings.
```
`[VISUAL: top-300 rerank diagram — production retrieval/eval evidence moves up; toy/CV-only moves down.]`

---

## SLIDE 6 — EXPLAINABILITY: honest, varied reasoning
```
Every candidate gets reasoning that cites real facts, names the JD requirement,
and surfaces honest concerns — tone scaled to rank.

#1   "Strong fit — Senior ML Engineer, 7.2 yrs at Zomato; recent production
      retrieval/search work. Evidences the JD's embeddings-retrieval requirement."
#75  "NLP Engineer, below the top tier. Upside: product-company, 5-9 yr band.
      Concerns: long 90-day notice; not flagged open-to-work."

100/100 distinct · 0 templated · 68/100 surface a concern term.
```
`[VISUAL: two reasoning cards (rank 1 glowing, rank 75 hedged) with facts/concerns colour-coded.]`

---

## SLIDE 7 — TRUST: honeypots, availability, reproducibility
```
• Honeypots: 96 impossible profiles flagged and kept out of the top 100
  (spec disqualifies >10% honeypot rate — we run 0%).
• Availability gate: a perfect-on-paper candidate inactive 6 months with a 5%
  response rate is down-weighted — "not actually available", per the JD.
• Reproducible: one command, no GPU, no API calls, standard-library ranker.
    python rank.py --candidates candidates.json --out submission.csv
• Sandbox: live Streamlit demo ranks an uploaded sample end-to-end.
```
`[VISUAL: three trust badges — 0% honeypots · availability-gated · 1-command reproducible.]`

---

## SLIDE 8 — COST + ROADMAP (Redrob fit)
```
Cost-aware by design — Redrob's whole thesis:
• Ranks 100K on a laptop CPU in ~43s. No GPU, no per-candidate LLM calls.
• Optional sentence embeddings are precomputed offline and loaded as compact local
  artifacts; the ranking path never calls a hosted model or uses network.

Roadmap: top-300 manual audit · pseudo-label learning-to-rank only if it beats
the current precision reranker · the same engine powers lead-ranking in Redrob's GTM.

"We don't find the best resume — we find the right person, in plain language."
```
`[VISUAL: cost comparison — per-candidate GPT call (✗, won't fit budget) vs our CPU pipeline (✓ ~43s); small roadmap arrow.]`

---

## DESIGN NOTES
- One accent colour (Redrob-ish blue/teal), one font (Inter/Poppins), a visual on every slide.
- Slides 3 (architecture), 4 (relevance idea), and 5 (ablation churn) are the "wow" slides — most effort there.
- Footer on each: "RedRob Candidate Ranker · #IndiaRuns".
- Keep speaker detail off the slides; say it aloud. ≤8 slides, PDF export.

## SPEAKER NOTES (≈30s each)
1. "We rank 100K candidates for the Senior AI Engineer role — and the trick is we read what they built, not the keywords they listed."
2. "The JD literally says keyword-matching is a trap, with two failure modes: stuffers get in, real plain-language talent gets dropped."
3. "Five stages, all CPU, 43 seconds. Honeypots out, obvious disqualifiers out, then scoring."
4. "The core: BM25/TF-IDF of the JD against the candidate's own career text. Real retrieval work scores high even with no buzzwords; keyword systems score it zero."
5. "Ground truth is hidden, so we validate by proxy: the precision pass promotes production retrieval/evaluation evidence and penalizes toy RAG or CV-only profiles."
6. "Every rank gets honest reasoning — strengths, the JD tie, and real concerns — tone matching the rank. Nothing templated."
7. "Trust: zero honeypots in the top 100, availability gating, and one-command reproduction with no network."
8. "It's cheap — laptop CPU, 43 seconds — and optional embeddings are local artifacts, not live calls. That's Redrob's cost thesis, and the same engine ranks sales leads too."

## JUDGE Q&A
| Question | Answer |
|---|---|
| "Why no GPU or live embedding model?" | "BM25+TF-IDF is the safe default; optional sentence embeddings are pre-computed offline and loaded as local vectors, so the rank step stays CPU-only and network-free." |
| "How do you know it's good without NDCG?" | "We can't see the truth, so we validate by proxy: 0% honeypots, trap-resistance, the 18-candidate churn toward JD-core roles, and an LLM-judge spot-check (offline)." |
| "Isn't this still keyword matching?" | "No — BM25/TF-IDF score *term overlap with the JD's own language* weighted by rarity, over full descriptions. It promotes candidates with no buzzwords at all." |
| "Did you use AI?" | "Yes — Claude as a dev assistant, declared. The ranking step has zero LLM calls; the engineering, relevance design, and tuning were ours." |
