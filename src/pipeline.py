"""
Pipeline Orchestrator — runs the 5-stage ranking pipeline.

Stage 1: Honeypot Detection  → flag ~80 impossible profiles
Stage 2: Hard Filters        → eliminate disqualified candidates
Stage 3: Multi-Dim Scoring   → score all remaining candidates on 6 axes
Stage 4: Composite Ranking   → combine scores and sort
Stage 5: Top-100 + Reasoning → produce final CSV output
"""

import json
import time
import sys
from typing import TextIO

from src.honeypot_detector import detect_honeypot
from src.hard_filters import apply_hard_filters
from src.scorers import score_candidate
from src.ranker import rank_candidates
from src.relevance import RelevanceScorer
from src.jd_text import JD_TEXT


def _log(msg: str) -> None:
    """Print a timestamped log message."""
    elapsed = time.time() - _log.start_time
    print(f"  [{elapsed:6.1f}s] {msg}", file=sys.stderr)

_log.start_time = time.time()


def load_candidates(filepath: str) -> list[dict]:
    """
    Load candidates from a JSONL file.
    Handles both plain .jsonl and gzipped .jsonl.gz files.
    """
    import gzip

    candidates = []
    opener = gzip.open if filepath.endswith(".gz") else open
    kwargs = {"mode": "rt", "encoding": "utf-8"}

    with opener(filepath, **kwargs) as f:
        for line in f:
            line = line.strip()
            if line:
                candidates.append(json.loads(line))

    return candidates


def run_pipeline(
    candidates: list[dict],
    top_n: int = 100,
    verbose: bool = True,
) -> tuple[list[dict], dict]:
    """
    Run the full 5-stage pipeline.

    Args:
        candidates: list of candidate dicts
        top_n: number of top candidates to output
        verbose: whether to print progress

    Returns:
        (results: list[dict], stats: dict)
    """
    _log.start_time = time.time()
    stats = {
        "total_candidates": len(candidates),
        "honeypots_detected": 0,
        "hard_filtered": 0,
        "scored": 0,
    }

    if verbose:
        _log(f"Starting pipeline with {len(candidates)} candidates")

    # ───────────────────────────────────
    # Stage 1: Honeypot Detection
    # ───────────────────────────────────
    if verbose:
        _log("Stage 1: Honeypot detection...")

    honeypot_ids = set()
    for candidate in candidates:
        is_honeypot, reasons = detect_honeypot(candidate)
        if is_honeypot:
            honeypot_ids.add(candidate["candidate_id"])

    stats["honeypots_detected"] = len(honeypot_ids)
    if verbose:
        _log(f"  → Detected {len(honeypot_ids)} honeypots")

    # Remove honeypots
    remaining = [c for c in candidates if c["candidate_id"] not in honeypot_ids]

    # ───────────────────────────────────
    # Stage 2: Hard Filters
    # ───────────────────────────────────
    if verbose:
        _log("Stage 2: Hard filters...")

    filtered = []
    rejected_count = 0
    for candidate in remaining:
        should_keep, reason = apply_hard_filters(candidate)
        if should_keep:
            filtered.append(candidate)
        else:
            rejected_count += 1

    stats["hard_filtered"] = rejected_count
    if verbose:
        _log(f"  → Filtered out {rejected_count} candidates, {len(filtered)} remaining")

    # ───────────────────────────────────
    # Stage 3: Multi-Dimensional Scoring
    # ───────────────────────────────────
    if verbose:
        _log(f"Stage 3: Scoring {len(filtered)} candidates...")

    # 3a. Build the relevance index (BM25 + TF-IDF of the JD vs each profile).
    # This needs corpus-level statistics, so it runs once over the whole filtered set
    # before per-candidate scoring.
    if verbose:
        _log("  → Building relevance index (BM25 + TF-IDF)...")
    relevance_scorer = RelevanceScorer(JD_TEXT).fit(filtered)
    relevance_map = relevance_scorer.relevance_scores()
    if verbose:
        _log(f"  → Relevance computed for {len(relevance_map)} candidates")

    scored = []
    for i, candidate in enumerate(filtered):
        rel = relevance_map.get(candidate["candidate_id"], 0.0)
        scores = score_candidate(candidate, relevance=rel)
        scored.append((candidate, scores))

        if verbose and (i + 1) % 10000 == 0:
            _log(f"  → Scored {i + 1}/{len(filtered)}")

    stats["scored"] = len(scored)
    if verbose:
        _log(f"  → Scoring complete")

    # ───────────────────────────────────
    # Stage 4 & 5: Ranking + Reasoning
    # ───────────────────────────────────
    if verbose:
        _log("Stage 4-5: Ranking and reasoning generation...")

    results = rank_candidates(scored, top_n=top_n)

    if verbose:
        _log(f"  → Top {len(results)} candidates selected")

        # Print summary of top 10
        _log("  ─── Top 10 Preview ───")
        for r in results[:10]:
            _log(f"  #{r['rank']:3d}  {r['candidate_id']}  "
                 f"score={r['score']:.4f}  {r['reasoning'][:80]}...")

    elapsed = time.time() - _log.start_time
    stats["elapsed_seconds"] = round(elapsed, 1)

    if verbose:
        _log(f"Pipeline complete in {elapsed:.1f}s")

    return results, stats
