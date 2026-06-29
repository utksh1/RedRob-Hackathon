"""Ranking pipeline orchestration."""

from __future__ import annotations

import sys
import json
import os
import time
from pathlib import Path

from backend.src.honeypot_detector import detect_honeypot
from backend.src.hard_filters import apply_hard_filters
from backend.src.scorers import score_candidate
from backend.src.ranker import rank_candidates
from backend.src.relevance import RelevanceScorer
from backend.src.jd_text import JD_TEXT


def _log(msg: str) -> None:
    elapsed = time.time() - _log.start_time
    print(f"  [{elapsed:6.1f}s] {msg}", file=sys.stderr)

_log.start_time = time.time()


_EMB_MATRIX = "embeddings.npy"
_EMB_IDS = "embedding_ids.json"
_EMB_JD = "jd_vector.npy"
_EMB_DIR_ENV = "REDROB_EMBEDDING_DIR"


def _embedding_paths() -> tuple[Path, Path, Path]:
    """Resolve optional embedding artifact paths."""
    artifact_dir = Path(os.environ.get(_EMB_DIR_ENV, "."))
    return (
        artifact_dir / _EMB_MATRIX,
        artifact_dir / _EMB_IDS,
        artifact_dir / _EMB_JD,
    )


def _load_embedding_cosines(candidates: list[dict], verbose: bool) -> dict[str, float] | None:
    """Load optional precomputed embedding cosines when local artifacts exist."""
    matrix_path, ids_path, jd_path = _embedding_paths()

    if not (matrix_path.exists() and ids_path.exists() and jd_path.exists()):
        return None
    try:
        import numpy as np

        with ids_path.open(encoding="utf-8") as f:
            ids = json.load(f)
        matrix = np.load(matrix_path)
        jd_vec = np.load(jd_path)

        if matrix.ndim != 2 or jd_vec.ndim != 1:
            raise ValueError("expected embeddings.npy as 2D matrix and jd_vector.npy as 1D vector")
        if matrix.shape[0] != len(ids):
            raise ValueError(f"embedding row count {matrix.shape[0]} != id count {len(ids)}")
        if matrix.shape[1] != jd_vec.shape[0]:
            raise ValueError(f"embedding dim {matrix.shape[1]} != JD dim {jd_vec.shape[0]}")

        row_of = {cid: i for i, cid in enumerate(ids)}
        selected: list[tuple[str, int]] = []
        for c in candidates:
            i = row_of.get(c["candidate_id"])
            if i is not None:
                selected.append((c["candidate_id"], i))

        if not selected:
            if verbose:
                _log("  → Embedding artifacts found but no candidate IDs matched; using BM25+TF-IDF only")
            return None

        selected_ids = [cid for cid, _ in selected]
        selected_rows = matrix[[i for _, i in selected]].astype("float32", copy=False)
        jd_vec = jd_vec.astype("float32", copy=False)

        row_norms = np.linalg.norm(selected_rows, axis=1)
        jd_norm = float(np.linalg.norm(jd_vec))
        denom = row_norms * jd_norm
        scores = np.divide(
            selected_rows @ jd_vec,
            denom,
            out=np.zeros(len(selected_ids), dtype="float32"),
            where=denom > 0,
        )
        scores = np.nan_to_num(scores, nan=0.0, posinf=0.0, neginf=0.0)
        cos = {cid: float(score) for cid, score in zip(selected_ids, scores)}

        if verbose:
            _log(f"  → Loaded embedding cosines for {len(cos)} candidates from {matrix_path.parent}")
        return cos or None
    except Exception as e:
        if verbose:
            _log(f"  → Embedding artifact present but unreadable ({e}); using BM25+TF-IDF only")
        return None


def load_candidates(filepath: str) -> list[dict]:
    """
    Load candidates from either:
      - JSONL / newline-delimited JSON, including the full candidates.json file
      - a regular JSON array, including sample_candidates.json

    Handles both plain and gzipped files.
    """
    import gzip

    opener = gzip.open if filepath.endswith(".gz") else open
    kwargs = {"mode": "rt", "encoding": "utf-8"}

    with opener(filepath, **kwargs) as f:
        first = f.read(1)
        while first and first.isspace():
            first = f.read(1)
        if not first:
            return []

        f.seek(0)
        if first == "[":
            data = json.load(f)
            if not isinstance(data, list):
                raise ValueError(f"Expected a JSON array in {filepath}")
            return data

        candidates = []
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
    """Run the ranking pipeline and return results plus run stats."""
    _log.start_time = time.time()
    stats = {
        "total_candidates": len(candidates),
        "honeypots_detected": 0,
        "hard_filtered": 0,
        "scored": 0,
    }

    if verbose:
        _log(f"Starting pipeline with {len(candidates)} candidates")

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

    remaining = [c for c in candidates if c["candidate_id"] not in honeypot_ids]

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

    if verbose:
        _log(f"Stage 3: Scoring {len(filtered)} candidates...")

    if verbose:
        _log("  → Building relevance index (BM25 + TF-IDF)...")

    embedding_cos = _load_embedding_cosines(filtered, verbose)

    relevance_scorer = RelevanceScorer(JD_TEXT).fit(filtered, embedding_cos=embedding_cos)
    relevance_map = relevance_scorer.relevance_scores()
    relevance_features = relevance_scorer.feature_scores()
    if verbose:
        mode = "BM25+TF-IDF+embeddings" if embedding_cos else "BM25+TF-IDF"
        _log(f"  → Relevance computed for {len(relevance_map)} candidates ({mode})")

    scored = []
    for i, candidate in enumerate(filtered):
        rel = relevance_map.get(candidate["candidate_id"], 0.0)
        detail = relevance_features.get(candidate["candidate_id"], {})
        scores = score_candidate(candidate, relevance=rel, relevance_detail=detail)
        scored.append((candidate, scores))

        if verbose and (i + 1) % 10000 == 0:
            _log(f"  → Scored {i + 1}/{len(filtered)}")

    stats["scored"] = len(scored)
    if verbose:
        _log(f"  → Scoring complete")

    if verbose:
        _log("Stage 4-5: Ranking and reasoning generation...")

    results = rank_candidates(scored, top_n=top_n)

    if verbose:
        _log(f"  → Top {len(results)} candidates selected")

        _log("  ─── Top 10 Preview ───")
        for r in results[:10]:
            _log(f"  #{r['rank']:3d}  {r['candidate_id']}  "
                 f"score={r['score']:.4f}  {r['reasoning'][:80]}...")

    elapsed = time.time() - _log.start_time
    stats["elapsed_seconds"] = round(elapsed, 1)

    if verbose:
        _log(f"Pipeline complete in {elapsed:.1f}s")

    return results, stats
