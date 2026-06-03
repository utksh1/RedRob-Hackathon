#!/usr/bin/env python3
"""
RedRob Hackathon — Intelligent Candidate Discovery & Ranking Challenge

Entry point: ranks 100K candidates against the Senior AI Engineer JD
and produces a top-100 CSV submission.

Usage:
    python rank.py --candidates ./India_runs_data_and_ai_challenge/candidates.jsonl --out ./submission.csv

Constraints:
    - 5 minutes max execution time
    - 16 GB RAM
    - CPU only (no GPU)
    - No network access during ranking
"""

import argparse
import csv
import os
import sys
import time


def main():
    parser = argparse.ArgumentParser(
        description="Rank candidates for the Senior AI Engineer role at Redrob AI",
    )
    parser.add_argument(
        "--candidates",
        type=str,
        required=True,
        help="Path to candidates.jsonl or candidates.jsonl.gz",
    )
    parser.add_argument(
        "--out",
        type=str,
        default="submission.csv",
        help="Output CSV path (default: submission.csv)",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=100,
        help="Number of top candidates to output (default: 100)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress output",
    )
    args = parser.parse_args()

    # Validate input
    if not os.path.exists(args.candidates):
        print(f"Error: candidates file not found: {args.candidates}", file=sys.stderr)
        sys.exit(1)

    start = time.time()
    print(f"{'='*60}", file=sys.stderr)
    print(f"  RedRob Candidate Ranking System", file=sys.stderr)
    print(f"  Input:  {args.candidates}", file=sys.stderr)
    print(f"  Output: {args.out}", file=sys.stderr)
    print(f"  Top-N:  {args.top_n}", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)

    # Import pipeline (deferred to after arg parsing for fast --help)
    from src.pipeline import load_candidates, run_pipeline

    # Load candidates
    print(f"\nLoading candidates...", file=sys.stderr)
    candidates = load_candidates(args.candidates)
    load_time = time.time() - start
    print(f"  Loaded {len(candidates)} candidates in {load_time:.1f}s\n", file=sys.stderr)

    # Run pipeline
    results, stats = run_pipeline(
        candidates,
        top_n=args.top_n,
        verbose=not args.quiet,
    )

    # Write output CSV
    print(f"\nWriting {len(results)} results to {args.out}...", file=sys.stderr)
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["candidate_id", "rank", "score", "reasoning"])
        writer.writeheader()
        writer.writerows(results)

    total_time = time.time() - start

    # Summary
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"  SUMMARY", file=sys.stderr)
    print(f"  Total candidates:     {stats['total_candidates']}", file=sys.stderr)
    print(f"  Honeypots detected:   {stats['honeypots_detected']}", file=sys.stderr)
    print(f"  Hard-filtered:        {stats['hard_filtered']}", file=sys.stderr)
    print(f"  Scored candidates:    {stats['scored']}", file=sys.stderr)
    print(f"  Output rows:          {len(results)}", file=sys.stderr)
    print(f"  Total time:           {total_time:.1f}s", file=sys.stderr)
    print(f"  Output file:          {args.out}", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)

    # Validate basic correctness
    if len(results) != args.top_n:
        print(f"\n⚠ WARNING: Expected {args.top_n} results, got {len(results)}", file=sys.stderr)

    # Check score ordering
    scores = [r["score"] for r in results]
    if scores != sorted(scores, reverse=True):
        print(f"\n⚠ WARNING: Scores are not in descending order!", file=sys.stderr)

    # Check for duplicates
    ids = [r["candidate_id"] for r in results]
    if len(ids) != len(set(ids)):
        print(f"\n⚠ WARNING: Duplicate candidate_ids found!", file=sys.stderr)

    if total_time > 300:
        print(f"\n⚠ WARNING: Exceeded 5-minute budget ({total_time:.0f}s)", file=sys.stderr)
    else:
        print(f"\n✓ Completed within budget ({total_time:.0f}s / 300s)", file=sys.stderr)


if __name__ == "__main__":
    main()
