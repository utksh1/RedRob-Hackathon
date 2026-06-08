"""
Relevance scorer — pure-Python BM25 + TF-IDF cosine of the JD against each candidate.

This is the core Phase-1 upgrade. The baseline system "understands" candidates by
substring-matching against fixed keyword lists, which the JD explicitly calls a trap:
a candidate who describes real retrieval/ranking work in plain language (without the
buzzwords in our lists) scores zero. BM25 and TF-IDF instead reward *term overlap with
the JD's own language*, weighted by how rare each term is — so "built a system that
recommends items and tuned it with offline NDCG before an A/B test" lights up on
`recommends`, `NDCG`, `offline`, `A/B` even though it contains none of our hard-coded
phrases.

Design:
  - Zero external dependencies (stdlib only) — preserves the repo's reproducibility.
  - One pass to tokenize + build corpus statistics (document frequencies, avg length).
  - Per candidate: BM25(JD, doc) and TF-IDF cosine(JD, doc).
  - Continuous normalization (divide by the 99th percentile) so variance is preserved
    *within* the top candidates — this is what widens the final score spread.

Usage:
    scorer = RelevanceScorer(JD_TEXT)
    scorer.fit(candidates)                 # candidates: list of candidate dicts
    rel = scorer.relevance_scores()        # {candidate_id: relevance in [0, 1]}
    detail = scorer.detail("CAND_0000001") # {"bm25":.., "tfidf_cos":.., "relevance":..}
"""

import math
import re
from collections import Counter


# ── Tokenizer ────────────────────────────────────────────
# Keep technical tokens intact: c++, a/b, tf-idf, bm25, node.js, ci/cd, k8s.
_TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9+#./\-]*")

# Small custom stopword list (no NLTK dependency). Domain words like "model",
# "system", "data" are intentionally NOT stopped — they carry signal here.
_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "if", "then", "else", "of", "to", "in",
    "on", "at", "for", "with", "without", "by", "from", "as", "is", "are", "was",
    "were", "be", "been", "being", "this", "that", "these", "those", "it", "its",
    "we", "you", "they", "he", "she", "i", "our", "your", "their", "his", "her",
    "us", "them", "who", "what", "which", "when", "where", "why", "how", "not",
    "no", "yes", "do", "does", "did", "done", "have", "has", "had", "having",
    "will", "would", "shall", "should", "can", "could", "may", "might", "must",
    "than", "so", "such", "also", "more", "most", "some", "any", "all", "each",
    "every", "both", "few", "many", "much", "very", "too", "just", "only", "own",
    "same", "other", "into", "over", "under", "up", "down", "out", "about", "after",
    "before", "between", "during", "while", "because", "across", "per", "etc",
    "one", "two", "three", "us", "im", "ive", "dont", "cant",
}

_MIN_TOKEN_LEN = 2

# BM25 hyperparameters (standard defaults)
_BM25_K1 = 1.5
_BM25_B = 0.75


def tokenize(text: str) -> list[str]:
    """Lowercase, extract technical-aware tokens, drop stopwords and 1-char noise."""
    if not text:
        return []
    out = []
    for tok in _TOKEN_RE.findall(text.lower()):
        if len(tok) < _MIN_TOKEN_LEN:
            continue
        if tok in _STOPWORDS:
            continue
        out.append(tok)
    return out


def build_candidate_document(candidate: dict) -> str:
    """
    Assemble the free-text document for a candidate. Recent / current role and the
    summary are emphasised (repeated) so they weigh more in term frequency.
    """
    profile = candidate.get("profile", {})
    parts: list[str] = []

    # Headline + summary carry the candidate's own framing.
    parts.append(profile.get("headline", ""))
    parts.append(profile.get("summary", ""))
    parts.append(profile.get("summary", ""))  # emphasise summary (x2)

    # Current title/industry, emphasised.
    parts.append(profile.get("current_title", ""))
    parts.append(profile.get("current_title", ""))
    parts.append(profile.get("current_industry", ""))

    # Career history: title + description; the most recent role (index 0) emphasised.
    for i, role in enumerate(candidate.get("career_history", [])):
        title = role.get("title", "")
        desc = role.get("description", "")
        if i == 0:
            parts.append(title)
            parts.append(desc)
            parts.append(desc)  # most-recent role emphasised (x2)
        else:
            parts.append(title)
            parts.append(desc)

    # Skill names (as plain text — overlap with JD language, not our taxonomy).
    parts.append(" ".join(s.get("name", "") for s in candidate.get("skills", [])))

    return " ".join(p for p in parts if p)


def _percentile(sorted_vals: list[float], pct: float) -> float:
    """Linear-interpolation percentile of an already-sorted list. pct in [0, 100]."""
    if not sorted_vals:
        return 0.0
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    k = (len(sorted_vals) - 1) * (pct / 100.0)
    lo = math.floor(k)
    hi = math.ceil(k)
    if lo == hi:
        return sorted_vals[int(k)]
    return sorted_vals[lo] * (hi - k) + sorted_vals[hi] * (k - lo)


class RelevanceScorer:
    """BM25 + TF-IDF cosine of the JD query against a corpus of candidate documents."""

    def __init__(self, jd_text: str, bm25_weight: float = 0.6):
        self.jd_tokens = tokenize(jd_text)
        # JD query term frequencies (a term repeated in the JD weighs more).
        self.jd_tf = Counter(self.jd_tokens)
        self.bm25_weight = bm25_weight

        # Filled by fit():
        self._ids: list[str] = []
        self._doc_counts: list[Counter] = []
        self._doc_len: list[int] = []
        self._df: Counter = Counter()
        self._N: int = 0
        self._avgdl: float = 0.0
        self._idf: dict[str, float] = {}
        self._bm25_norm: dict[str, float] = {}
        self._tfidf_norm: dict[str, float] = {}
        self._emb_norm: dict[str, float] = {}
        self._has_embeddings: bool = False
        self._relevance: dict[str, float] = {}
        self._raw: dict[str, tuple[float, float]] = {}  # id -> (bm25_raw, tfidf_raw)

    # ── Fit ──────────────────────────────────────────────
    def fit(self, candidates: list[dict], embedding_cos: dict[str, float] | None = None) -> "RelevanceScorer":
        """
        Build corpus stats and score every candidate.

        embedding_cos (optional): {candidate_id: cosine(jd, candidate)} precomputed
        offline from sentence embeddings (see scripts/precompute_embeddings.py). When
        present, it becomes a third relevance signal blended with BM25 + TF-IDF. When
        absent (the default, zero-dependency path), relevance is BM25 + TF-IDF only.
        """
        # Pass 1: tokenize every doc, accumulate document frequencies + lengths.
        for cand in candidates:
            cid = cand["candidate_id"]
            counts = Counter(tokenize(build_candidate_document(cand)))
            self._ids.append(cid)
            self._doc_counts.append(counts)
            self._doc_len.append(sum(counts.values()))
            self._df.update(counts.keys())

        self._N = len(self._ids)
        self._avgdl = (sum(self._doc_len) / self._N) if self._N else 0.0

        # IDF for every corpus term (BM25 idf form, floored at 0).
        for term, df in self._df.items():
            self._idf[term] = max(0.0, math.log((self._N - df + 0.5) / (df + 0.5) + 1.0))

        # Precompute the JD's TF-IDF vector (over JD terms present in the corpus).
        jd_vec: dict[str, float] = {}
        for term, tf in self.jd_tf.items():
            idf = self._idf.get(term)
            if idf:
                jd_vec[term] = (1.0 + math.log(tf)) * idf
        jd_norm = math.sqrt(sum(v * v for v in jd_vec.values())) or 1.0

        # Pass 2: score each document (BM25 + TF-IDF cosine).
        raw_bm25: dict[str, float] = {}
        raw_tfidf: dict[str, float] = {}
        for cid, counts, dl in zip(self._ids, self._doc_counts, self._doc_len):
            # BM25: sum over JD query terms that appear in this doc.
            bm25 = 0.0
            denom_len = _BM25_K1 * (1.0 - _BM25_B + _BM25_B * (dl / self._avgdl if self._avgdl else 0.0))
            for term, qtf in self.jd_tf.items():
                tf = counts.get(term, 0)
                if not tf:
                    continue
                idf = self._idf.get(term, 0.0)
                bm25 += idf * (tf * (_BM25_K1 + 1.0)) / (tf + denom_len)

            # TF-IDF cosine: dot product over the JD∩doc terms / (||jd|| · ||doc||).
            dot = 0.0
            doc_sq = 0.0
            for term, tf in counts.items():
                idf = self._idf.get(term, 0.0)
                if not idf:
                    continue
                w = (1.0 + math.log(tf)) * idf
                doc_sq += w * w
                if term in jd_vec:
                    dot += w * jd_vec[term]
            doc_norm = math.sqrt(doc_sq) or 1.0
            cos = dot / (jd_norm * doc_norm)

            raw_bm25[cid] = bm25
            raw_tfidf[cid] = cos
            self._raw[cid] = (bm25, cos)

        # Continuous normalization: divide by the 99th-percentile (robust to outliers),
        # clamp to [0, 1]. Preserves variance among the top docs → widens final spread.
        self._bm25_norm = self._normalize(raw_bm25)
        self._tfidf_norm = self._normalize(raw_tfidf)

        # Optional third signal: sentence-embedding cosine (precomputed offline).
        if embedding_cos:
            self._has_embeddings = True
            self._emb_norm = self._normalize(embedding_cos)
            # Re-balance: embeddings carry real semantic signal, so give the three
            # signals 0.4 / 0.2 / 0.4 (lexical-BM25 / lexical-TFIDF / dense).
            for cid in self._ids:
                self._relevance[cid] = (
                    0.4 * self._bm25_norm[cid]
                    + 0.2 * self._tfidf_norm[cid]
                    + 0.4 * self._emb_norm.get(cid, 0.0)
                )
        else:
            self._has_embeddings = False
            for cid in self._ids:
                self._relevance[cid] = (
                    self.bm25_weight * self._bm25_norm[cid]
                    + (1.0 - self.bm25_weight) * self._tfidf_norm[cid]
                )
        return self

    @staticmethod
    def _normalize(raw: dict[str, float]) -> dict[str, float]:
        if not raw:
            return {}
        hi = _percentile(sorted(raw.values()), 99.0) or 1.0
        return {cid: max(0.0, min(1.0, v / hi)) for cid, v in raw.items()}

    # ── Accessors ────────────────────────────────────────
    def relevance_scores(self) -> dict[str, float]:
        """{candidate_id: blended relevance in [0, 1]}."""
        return self._relevance

    def detail(self, candidate_id: str) -> dict[str, float]:
        bm25_raw, tfidf_raw = self._raw.get(candidate_id, (0.0, 0.0))
        return {
            "bm25_raw": round(bm25_raw, 4),
            "tfidf_cos": round(tfidf_raw, 4),
            "bm25_norm": round(self._bm25_norm.get(candidate_id, 0.0), 4),
            "tfidf_norm": round(self._tfidf_norm.get(candidate_id, 0.0), 4),
            "relevance": round(self._relevance.get(candidate_id, 0.0), 4),
        }
