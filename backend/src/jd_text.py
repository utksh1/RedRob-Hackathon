"""
JD_TEXT — the Senior AI Engineer job description as a single query string.

This is the *query* for the relevance scorer (backend/src/relevance.py). It is the full
signal-bearing text of the JD (job_description.docx, see
doc1/docs/extracted/job_description_extracted.md), lightly condensed to the parts that describe
what the role actually needs — so BM25/TF-IDF reward candidates whose own free-text
(summary + career descriptions) overlaps the role's real language, not a fixed
keyword list.

Kept deliberately verbatim-ish from the JD so the term distribution matches how the
employer actually wrote it (e.g. "embedding drift", "index refresh", "offline-to-online
correlation", "hybrid vs dense").
"""

JD_TEXT = """
Senior AI Engineer, founding team, AI-native talent intelligence platform.
Own the intelligence layer of the product: the ranking, retrieval, and matching
systems that decide what recruiters see when they search for candidates and what
candidates see when they search for roles.

We need deep technical depth in modern ML systems: embeddings, retrieval, ranking,
LLMs, fine-tuning. Combined with a scrappy product-engineering attitude: willing to
ship a working ranker in a week even if the underlying ML is obviously suboptimal,
because we need to learn from real users before we know what to optimize for.

First 90 days: audit the current ranking stack, which is mostly BM25 plus rule-based
scoring, working but not great. Ship a v2 ranking system that improves recruiter
engagement metrics, involving embeddings, hybrid retrieval, and LLM-based re-ranking.
Set up evaluation infrastructure: offline benchmarks, online A/B testing, and
recruiter-feedback loops. Drive the long-term architecture of candidate-JD matching
at scale.

Things you absolutely need:
Production experience with embeddings-based retrieval systems deployed to real users:
sentence-transformers, OpenAI embeddings, BGE, E5, or similar. You have handled
embedding drift, index refresh, and retrieval-quality regression in production.
Production experience with vector databases or hybrid search infrastructure: Pinecone,
Weaviate, Qdrant, Milvus, OpenSearch, Elasticsearch, FAISS, or similar. The operational
experience matters more than the specific tech.
Strong Python and code quality.
Hands-on experience designing evaluation frameworks for ranking systems: NDCG, MRR,
MAP, offline-to-online correlation, A/B test interpretation.

Nice to have:
LLM fine-tuning experience: LoRA, QLoRA, PEFT. Learning-to-rank models, XGBoost-based
or neural. Prior exposure to HR-tech, recruiting tech, or marketplace products.
Distributed systems or large-scale inference optimization. Open-source contributions
in the AI/ML space.

The ideal candidate has roughly 6 to 8 years total experience, of which 4 to 5 are in
applied ML/AI roles at product companies, not pure services. Has shipped at least one
end-to-end ranking, search, or recommendation system to real users at meaningful scale.
Has strong opinions about retrieval (hybrid vs dense), evaluation (offline vs online),
and LLM integration (when to fine-tune vs prompt), defensible with reference to systems
they actually built. Located in or willing to relocate to Noida or Pune; Hyderabad,
Mumbai, Delhi NCR welcome.

We do not want: title-chasers who switch companies every 1.5 years; framework
enthusiasts whose work is LangChain tutorials and hot-framework demos rather than
systems thinking; people whose entire career is at consulting firms; people whose
primary expertise is computer vision, speech, or robotics without NLP/IR exposure;
people whose work has been entirely closed-source for 5+ years without external
validation. Pure research or academic backgrounds without production deployment are
disqualified. Recent (under 12 months) AI experience that is only LangChain calling
OpenAI is not enough. Senior engineers who have not written production code in 18
months because they moved to architecture or tech-lead roles are not a fit.
"""
