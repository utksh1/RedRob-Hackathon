# Models And Artifacts

This folder is reserved for optional model artifacts.

The current submission does not require a trained model file. FitRank v1 is an
interpretable hybrid ranking model implemented in `backend/src/` using:

- BM25 + TF-IDF JD relevance
- structured candidate scoring features
- availability gating
- a deterministic top-300 precision reranker

Optional future artifacts can live here, for example:

- precomputed candidate embeddings
- an ID-to-vector map
- an offline-trained reranker

Do not put the full 100K candidate dataset here.
