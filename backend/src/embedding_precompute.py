"""Offline sentence-embedding artifact builder for the optional relevance signal.

This script is intentionally outside the rank-time path. It may download/load a local
SentenceTransformer model and can take longer than five minutes; `rank.py` only reads
the generated compact artifacts with no network calls.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

if __package__ in (None, ""):
    PROJECT_ROOT = Path(__file__).resolve().parents[2]
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

from backend.src.jd_text import JD_TEXT
from backend.src.pipeline import load_candidates
from backend.src.relevance import build_candidate_document


DEFAULT_MODEL = "BAAI/bge-small-en-v1.5"
MATRIX_FILE = "embeddings.npy"
IDS_FILE = "embedding_ids.json"
JD_FILE = "jd_vector.npy"
META_FILE = "embedding_metadata.json"


def _auto_query_prefix(model_name: str) -> str:
    """Use the standard BGE query instruction when the default BGE model is selected."""
    if "bge" in model_name.lower():
        return "Represent this sentence for searching relevant passages: "
    return ""


def _load_encoder(model_name: str, device: str):
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise SystemExit(
            "Missing optional dependency: sentence-transformers. Install it with:\n"
            "  python -m pip install -r requirements-embeddings.txt"
        ) from exc

    return SentenceTransformer(model_name, device=device)


def _encode_texts(model, texts: list[str], batch_size: int, show_progress: bool):
    """Encode texts as normalized float32 numpy arrays."""
    return model.encode(
        texts,
        batch_size=batch_size,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=show_progress,
    ).astype("float32", copy=False)


def build_artifacts(
    candidates_path: str,
    out_dir: Path,
    model_name: str,
    batch_size: int,
    device: str,
    limit: int | None,
    query_prefix: str | None,
) -> None:
    import numpy as np

    out_dir.mkdir(parents=True, exist_ok=True)

    candidates = load_candidates(candidates_path)
    if limit is not None:
        candidates = candidates[:limit]
    if not candidates:
        raise SystemExit(f"No candidates loaded from {candidates_path}")

    ids = [c["candidate_id"] for c in candidates]
    docs = [build_candidate_document(c) for c in candidates]

    model = _load_encoder(model_name, device=device)
    prefix = _auto_query_prefix(model_name) if query_prefix is None else query_prefix

    print(f"Loaded {len(candidates)} candidates", file=sys.stderr)
    print(f"Encoding with {model_name} on {device}", file=sys.stderr)
    print(f"Output directory: {out_dir}", file=sys.stderr)

    matrix = _encode_texts(model, docs, batch_size=batch_size, show_progress=True)
    jd_text = f"{prefix}{JD_TEXT}" if prefix else JD_TEXT
    jd_vector = _encode_texts(model, [jd_text], batch_size=1, show_progress=False)[0]

    matrix_path = out_dir / MATRIX_FILE
    ids_path = out_dir / IDS_FILE
    jd_path = out_dir / JD_FILE
    meta_path = out_dir / META_FILE

    np.save(matrix_path, matrix)
    np.save(jd_path, jd_vector)
    ids_path.write_text(json.dumps(ids, indent=2), encoding="utf-8")
    meta_path.write_text(
        json.dumps(
            {
                "created_at_utc": datetime.now(timezone.utc).isoformat(),
                "source_candidates": str(Path(candidates_path)),
                "candidate_count": len(ids),
                "model": model_name,
                "device": device,
                "batch_size": batch_size,
                "embedding_dim": int(matrix.shape[1]),
                "normalized": True,
                "query_prefix": prefix,
                "document_builder": "backend.src.relevance.build_candidate_document",
                "files": {
                    "matrix": MATRIX_FILE,
                    "ids": IDS_FILE,
                    "jd_vector": JD_FILE,
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    approx_mb = matrix.nbytes / (1024 * 1024)
    print(f"Wrote {matrix_path} ({approx_mb:.1f} MB)", file=sys.stderr)
    print(f"Wrote {jd_path}", file=sys.stderr)
    print(f"Wrote {ids_path}", file=sys.stderr)
    print(f"Wrote {meta_path}", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Precompute optional sentence-embedding artifacts for rank.py",
    )
    parser.add_argument(
        "--candidates",
        required=True,
        help="Path to candidates JSONL/JSON array. Use the same source pool as rank.py.",
    )
    parser.add_argument(
        "--out-dir",
        default="embedding_artifacts",
        help="Directory for embeddings.npy, embedding_ids.json, jd_vector.npy, and metadata.",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"SentenceTransformer model name or local path (default: {DEFAULT_MODEL}).",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=128,
        help="SentenceTransformer encode batch size.",
    )
    parser.add_argument(
        "--device",
        default="cpu",
        help="Torch device for offline precompute. Use cpu for reproducibility.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional cap for smoke tests; omit for the full candidate pool.",
    )
    parser.add_argument(
        "--query-prefix",
        default=None,
        help=(
            "Optional query instruction prefix for the JD vector. Defaults to the BGE "
            "retrieval query instruction when the model name contains 'bge'; use '' to disable."
        ),
    )
    args = parser.parse_args()

    build_artifacts(
        candidates_path=args.candidates,
        out_dir=Path(args.out_dir),
        model_name=args.model,
        batch_size=args.batch_size,
        device=args.device,
        limit=args.limit,
        query_prefix=args.query_prefix,
    )


if __name__ == "__main__":
    main()
