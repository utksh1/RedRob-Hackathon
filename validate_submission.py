#!/usr/bin/env python3
"""
validate_submission.py — local replica of the spec's format validator.

The hackathon bundle references a `validate_submission.py` but it was not shipped in
this bundle, so this implements the rules from submission_spec.docx (Sections 3 and 6):

  - exactly 100 data rows (+ header)
  - required columns in order: candidate_id, rank, score, reasoning
  - rank uses each integer 1..100 exactly once
  - candidate_id unique and present in the candidates file
  - score non-increasing as rank increases (ties allowed)
  - not all scores identical
  - UTF-8, .csv

Usage:
    python validate_submission.py --submission submission.csv \
        --candidates ./India_runs_data_and_ai_challenge/candidates.json
"""

from __future__ import annotations

import argparse
import csv
import json
import sys


REQUIRED_COLUMNS = ["candidate_id", "rank", "score", "reasoning"]


def load_candidate_ids(path: str) -> set[str]:
    import gzip
    ids = set()
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                ids.add(json.loads(line)["candidate_id"])
    return ids


def validate(submission: str, candidates: str | None) -> list[str]:
    errors: list[str] = []

    if not submission.endswith(".csv"):
        errors.append(f"file must be .csv (got {submission})")

    with open(submission, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            return ["file is empty"]
        rows = list(reader)

    # Columns
    if header != REQUIRED_COLUMNS:
        errors.append(f"header must be exactly {REQUIRED_COLUMNS}, got {header}")

    # Row count
    if len(rows) != 100:
        errors.append(f"must have exactly 100 data rows, got {len(rows)}")

    ids, ranks, scores = [], [], []
    for i, row in enumerate(rows, start=1):
        if len(row) != 4:
            errors.append(f"row {i}: expected 4 fields, got {len(row)}")
            continue
        cid, rank, score, _reasoning = row
        ids.append(cid)
        try:
            ranks.append(int(rank))
        except ValueError:
            errors.append(f"row {i}: rank '{rank}' is not an int")
        try:
            scores.append(float(score))
        except ValueError:
            errors.append(f"row {i}: score '{score}' is not a float")

    # Ranks 1..100 exactly once
    if sorted(ranks) != list(range(1, 101)):
        errors.append("ranks must be each integer 1..100 exactly once")

    # Unique candidate_ids
    if len(set(ids)) != len(ids):
        dupes = {x for x in ids if ids.count(x) > 1}
        errors.append(f"duplicate candidate_ids: {sorted(dupes)[:5]}")

    # Score non-increasing
    if any(scores[i] < scores[i + 1] for i in range(len(scores) - 1)):
        errors.append("scores must be non-increasing as rank increases")

    # Not all identical
    if scores and len(set(scores)) == 1:
        errors.append("all scores are identical (model isn't differentiating)")

    # IDs exist in candidates file
    if candidates:
        valid = load_candidate_ids(candidates)
        missing = [c for c in ids if c not in valid]
        if missing:
            errors.append(f"{len(missing)} candidate_id(s) not in candidates file: {missing[:5]}")

    return errors


def main() -> None:
    ap = argparse.ArgumentParser(description="Validate a submission CSV against the spec.")
    ap.add_argument("--submission", default="submission.csv")
    ap.add_argument("--candidates", default=None,
                    help="optional: candidates.json(.gz) to verify IDs exist")
    args = ap.parse_args()

    errors = validate(args.submission, args.candidates)
    if errors:
        print(f"✗ INVALID — {len(errors)} issue(s):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        sys.exit(1)
    print(f"✓ VALID — {args.submission} passes all spec checks.")


if __name__ == "__main__":
    main()
