"""
claude_client.py — OFFLINE LLM relevance labeling (distillation source).

⚠️  COMPLIANCE BOUNDARY — READ THIS FIRST
    This module calls the Anthropic API and is **never** imported by rank.py.
    The submission spec forbids hosted-LLM calls *during ranking* (CPU-only,
    no network, ≤5 min). This script runs OFFLINE during development only, to
    produce label/eval artifacts:

        candidates.json  ──(this script, offline)──▶  pseudo_labels.jsonl
                                                            │
                              train a small CPU reranker ◀──┘  (Phase 4b)
                                          │
                              ships as weights → rank.py runs it offline

    Two legitimate uses, both offline:
      1. EVAL  — grade a sample of our top-100 to sanity-check ranking quality
                 (we have no ground truth; an LLM judge is a proxy).
      2. DISTILL — grade a few thousand candidates to create training labels
                 for a compact learning-to-rank model that runs within budget.

Requirements (dev only — NOT added to the zero-dep rank.py path):
    pip install anthropic
    export ANTHROPIC_API_KEY=sk-ant-...

Usage:
    # Grade a 200-candidate sample (single calls, with rationale):
    python -m src.claude_client --candidates ./India_runs_data_and_ai_challenge/candidates.json \
        --sample 200 --out pseudo_labels.jsonl

    # Grade many candidates cheaply via the Batches API (50% cost):
    python -m src.claude_client --candidates ./...candidates.json --sample 4000 --batch --out pseudo_labels.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
import time

from src.jd_text import JD_TEXT

# Default model — the skill mandates claude-opus-4-8 unless the user picks another.
# (Override with --model for cheaper bulk labeling, e.g. claude-sonnet-4-6.)
DEFAULT_MODEL = "claude-opus-4-8"

# Graded relevance tiers — aligned with the submission's NDCG ground-truth scale
# (P@10 counts tier 3+ as "relevant"; honeypots are forced tier 0).
RELEVANCE_RUBRIC = """\
Grade the candidate's fit for THIS job on a 0-3 tier scale:

  3 = Strong fit. Production embeddings/retrieval/ranking/search/recommendation work
      at a PRODUCT company, roughly 5-9 yrs, with evaluation rigor (NDCG/MAP/A-B), and
      reachable (recent activity, responsive). The JD's bullseye.
  2 = Relevant. Real applied ML at a product company, but not core retrieval/ranking
      (e.g. NLP classification, general ML), or slightly outside the experience band,
      or minor availability concerns.
  1 = Adjacent / weak. Generic ML, off-domain (CV-only, fraud, data-eng), consulting-heavy
      career, or significant availability concerns.
  0 = Not a fit. Non-technical career, pure research with no production, <2 yrs relevant,
      OR an impossible/contradictory profile (a planted honeypot).

Judge the CAREER DESCRIPTIONS (what they actually built), not the skills list — a
keyword-stuffed skills section with a non-technical career is tier 0, and a plain-language
description of real retrieval work with no buzzwords can be tier 3.
"""

SYSTEM_PROMPT = (
    "You are a strict, fair senior technical recruiter grading candidate fit for a "
    "specific job description. Be objective and evidence-based. Reward demonstrated, "
    "described work over claimed skills. Penalize impossible/contradictory profiles."
)


# ─────────────────────────────────────────────────────────
# Pydantic schema for the structured grade (anthropic pulls in pydantic)
# ─────────────────────────────────────────────────────────
def _label_model():
    from pydantic import BaseModel, Field

    class RelevanceLabel(BaseModel):
        tier: int = Field(ge=0, le=3, description="Relevance tier 0-3 per the rubric")
        is_honeypot: bool = Field(description="True if the profile is impossible/contradictory")
        rationale: str = Field(description="One sentence citing the deciding evidence")

    return RelevanceLabel


# JSON schema mirror (for the Batches path, which builds raw requests)
LABEL_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "tier": {"type": "integer", "enum": [0, 1, 2, 3]},
        "is_honeypot": {"type": "boolean"},
        "rationale": {"type": "string"},
    },
    "required": ["tier", "is_honeypot", "rationale"],
    "additionalProperties": False,
}


def build_profile_digest(candidate: dict) -> str:
    """Compact, token-efficient candidate digest for the grader."""
    p = candidate.get("profile", {})
    lines = [
        f"Title: {p.get('current_title', '?')} @ {p.get('current_company', '?')}",
        f"Experience: {p.get('years_of_experience', '?')} yrs | "
        f"Location: {p.get('location', '?')}, {p.get('country', '?')}",
        f"Headline: {p.get('headline', '')}",
        f"Summary: {p.get('summary', '')}",
        "Career:",
    ]
    for r in candidate.get("career_history", [])[:5]:
        lines.append(
            f"  - {r.get('title', '?')} @ {r.get('company', '?')} "
            f"({r.get('duration_months', '?')}mo): {r.get('description', '')[:300]}"
        )
    skills = ", ".join(s.get("name", "") for s in candidate.get("skills", [])[:20])
    lines.append(f"Skills (claimed): {skills}")
    return "\n".join(lines)


def _user_prompt(candidate: dict) -> str:
    return (
        f"JOB DESCRIPTION:\n{JD_TEXT}\n\n"
        f"{RELEVANCE_RUBRIC}\n\n"
        f"CANDIDATE PROFILE:\n{build_profile_digest(candidate)}\n\n"
        f"Grade this candidate."
    )


# ─────────────────────────────────────────────────────────
# Single-call grading (with rationale + adaptive thinking)
# ─────────────────────────────────────────────────────────
def grade_candidate(client, candidate: dict, model: str = DEFAULT_MODEL) -> dict:
    """Grade one candidate. Returns {candidate_id, tier, is_honeypot, rationale}."""
    RelevanceLabel = _label_model()
    response = client.messages.parse(
        model=model,
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        thinking={"type": "adaptive"},      # let Claude reason about borderline fits
        output_config={"effort": "low"},    # a single graded judgment — keep it cheap
        messages=[{"role": "user", "content": _user_prompt(candidate)}],
        output_format=RelevanceLabel,
    )
    label = response.parsed_output
    return {
        "candidate_id": candidate["candidate_id"],
        "tier": label.tier,
        "is_honeypot": label.is_honeypot,
        "rationale": label.rationale,
    }


# ─────────────────────────────────────────────────────────
# Batch grading (Batches API — 50% cost, ideal for bulk distillation labels)
# ─────────────────────────────────────────────────────────
def grade_batch(client, candidates: list[dict], model: str = DEFAULT_MODEL) -> list[dict]:
    """Grade many candidates via the Batches API. Polls until complete."""
    from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
    from anthropic.types.messages.batch_create_params import Request

    requests = [
        Request(
            custom_id=c["candidate_id"],
            params=MessageCreateParamsNonStreaming(
                model=model,
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": _user_prompt(c)}],
                output_config={"format": {"type": "json_schema", "schema": LABEL_JSON_SCHEMA}},
            ),
        )
        for c in candidates
    ]

    batch = client.messages.batches.create(requests=requests)
    print(f"Batch {batch.id} created with {len(requests)} requests; polling…", file=sys.stderr)

    while True:
        batch = client.messages.batches.retrieve(batch.id)
        if batch.processing_status == "ended":
            break
        print(f"  status={batch.processing_status} "
              f"done={batch.request_counts.succeeded} err={batch.request_counts.errored}",
              file=sys.stderr)
        time.sleep(30)

    results = []
    for result in client.messages.batches.results(batch.id):
        if result.result.type != "succeeded":
            print(f"  ! {result.custom_id}: {result.result.type}", file=sys.stderr)
            continue
        msg = result.result.message
        text = next((b.text for b in msg.content if b.type == "text"), "{}")
        try:
            label = json.loads(text)
        except json.JSONDecodeError:
            continue
        results.append({
            "candidate_id": result.custom_id,
            "tier": label.get("tier"),
            "is_honeypot": label.get("is_honeypot"),
            "rationale": label.get("rationale"),
        })
    return results


# ─────────────────────────────────────────────────────────
# Data loading + CLI
# ─────────────────────────────────────────────────────────
def load_candidates(path: str, sample: int | None) -> list[dict]:
    import gzip
    opener = gzip.open if path.endswith(".gz") else open
    out = []
    with opener(path, "rt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            out.append(json.loads(line))
            if sample and len(out) >= sample:
                break
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="OFFLINE LLM relevance labeling (not used during ranking).")
    ap.add_argument("--candidates", required=True, help="candidates.json(.gz)")
    ap.add_argument("--out", default="pseudo_labels.jsonl")
    ap.add_argument("--sample", type=int, default=200, help="how many candidates to label")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--batch", action="store_true", help="use the Batches API (50%% cost)")
    args = ap.parse_args()

    try:
        import anthropic
    except ImportError:
        print("This offline tool needs the Anthropic SDK: pip install anthropic", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env
    candidates = load_candidates(args.candidates, args.sample)
    print(f"Loaded {len(candidates)} candidates; grading with {args.model} "
          f"({'batch' if args.batch else 'single-call'})…", file=sys.stderr)

    if args.batch:
        labels = grade_batch(client, candidates, model=args.model)
    else:
        labels = []
        for i, c in enumerate(candidates, 1):
            try:
                labels.append(grade_candidate(client, c, model=args.model))
            except Exception as e:  # keep going on transient failures
                print(f"  ! {c['candidate_id']}: {e}", file=sys.stderr)
            if i % 25 == 0:
                print(f"  graded {i}/{len(candidates)}", file=sys.stderr)

    with open(args.out, "w", encoding="utf-8") as f:
        for row in labels:
            f.write(json.dumps(row) + "\n")
    print(f"Wrote {len(labels)} labels to {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
