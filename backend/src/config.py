"""
Configuration constants for the RedRob Candidate Ranking System.

All tunable parameters — weights, thresholds, keyword lists, company lists —
are centralized here for easy experimentation.
"""

from datetime import date

# ──────────────────────────────────────────────
# Reference date (for recency calculations)
# ──────────────────────────────────────────────
REFERENCE_DATE = date(2026, 6, 1)

# ──────────────────────────────────────────────
# Composite scoring weights (must sum to 1.0)
# ──────────────────────────────────────────────
# `relevance` is the BM25 + TF-IDF JD-match axis (backend/src/relevance.py). It carries the
# free-text semantic signal, so career/skills are down-weighted from the keyword-only
# baseline to avoid double-counting keyword presence.
WEIGHTS = {
    "relevance":   0.30,
    "career":      0.22,
    "skills":      0.16,
    "behavioral":  0.14,
    "experience":  0.12,
    "education":   0.03,
    "logistics":   0.03,
}

# ──────────────────────────────────────────────
# Experience fit (Gaussian scoring)
# ──────────────────────────────────────────────
EXPERIENCE_PEAK = 7.0       # ideal years
EXPERIENCE_SIGMA = 3.0      # spread
EXPERIENCE_MIN = 3.0        # below this → heavy penalty
EXPERIENCE_MAX = 15.0       # above this → diminishing returns

# ──────────────────────────────────────────────
# Consulting firms (entire career = disqualifier per JD)
# ──────────────────────────────────────────────
CONSULTING_FIRMS = {
    "tcs", "tata consultancy services",
    "infosys",
    "wipro",
    "accenture",
    "cognizant",
    "capgemini",
    "hcl", "hcl technologies",
    "tech mahindra",
    "mindtree", "ltimindtree",
    "mphasis",
    "l&t infotech", "lti",
    "persistent systems",
    "cts",
}

# ──────────────────────────────────────────────
# Skill classification
# ──────────────────────────────────────────────

# Tier 1: Must-have skills per JD (highest value)
SKILLS_TIER1 = {
    # Embeddings & retrieval
    "embeddings", "sentence-transformers", "sentence transformers",
    "bge", "e5", "openai embeddings",
    # Vector databases
    "pinecone", "weaviate", "qdrant", "milvus", "faiss",
    "elasticsearch", "opensearch",
    # NLP / IR
    "nlp", "natural language processing", "information retrieval",
    # Ranking & search
    "ranking", "retrieval", "search", "recommendation",
    "learning to rank", "re-ranking",
    # Python (core requirement)
    "python",
}

# Tier 2: Nice-to-have skills per JD
SKILLS_TIER2 = {
    # LLM fine-tuning
    "lora", "qlora", "peft", "fine-tuning llms", "fine-tuning",
    "llm", "large language models",
    # ML frameworks
    "pytorch", "tensorflow", "scikit-learn", "xgboost", "lightgbm",
    "keras",
    # Transformers
    "transformers", "huggingface", "hugging face", "bert", "gpt",
    # Data engineering
    "spark", "pyspark", "airflow", "sql", "databricks", "dbt",
    # MLOps
    "mlflow", "weights & biases", "wandb", "bentoml", "kubeflow",
    "docker", "kubernetes",
    # Cloud
    "aws", "gcp", "azure",
    # General ML
    "machine learning", "deep learning", "statistical modeling",
    "feature engineering", "data science", "data engineering",
    # Specific ML areas
    "gans", "reinforcement learning", "object detection",
    "image classification", "speech recognition", "tts",
    "computer vision",
    # Databases
    "redis", "mongodb", "postgresql", "kafka",
    # Programming
    "java", "go", "rust", "c++", "scala",
}

# Anti-skills: suggest a non-technical career (used for keyword-stuffer detection)
SKILLS_ANTI = {
    "photoshop", "illustrator", "indesign", "figma", "sketch",
    "canva", "after effects", "premiere pro",
    "accounting", "tally", "sap",
    "seo", "content writing", "copywriting", "marketing",
    "solidworks", "autocad", "ansys", "creo", "catia",
    "civil engineering", "structural engineering",
    "six sigma", "lean manufacturing", "supply chain",
    "powerpoint", "excel",
}

# ──────────────────────────────────────────────
# Title classification
# ──────────────────────────────────────────────

# Titles strongly relevant to the JD
TITLES_STRONG_POSITIVE = {
    "ml engineer", "machine learning engineer",
    "ai engineer", "artificial intelligence engineer",
    "data scientist", "senior data scientist",
    "research engineer", "applied scientist",
    "search engineer", "ranking engineer",
    "nlp engineer", "ir engineer",
    "senior ml engineer", "senior machine learning engineer",
    "senior ai engineer",
    "lead ml engineer", "lead machine learning engineer",
    "staff ml engineer", "principal ml engineer",
    "junior ml engineer",
}

# Titles mildly relevant (could be ML-adjacent)
TITLES_MILD_POSITIVE = {
    "software engineer", "senior software engineer",
    "backend engineer", "senior backend engineer",
    "data engineer", "senior data engineer",
    "data analyst", "analytics engineer",
    "full stack engineer", "platform engineer",
    "devops engineer", "sre",
}

# Titles explicitly irrelevant per JD
TITLES_NEGATIVE = {
    "hr manager", "human resources manager",
    "marketing manager",
    "accountant", "senior accountant",
    "graphic designer", "senior graphic designer",
    "content writer", "senior content writer",
    "civil engineer", "senior civil engineer",
    "mechanical engineer", "senior mechanical engineer",
    "operations manager", "senior operations manager",
    "sales executive", "senior sales executive",
    "customer support", "customer service",
    "project manager", "program manager",
    "business analyst",
    "product manager",
}

# ──────────────────────────────────────────────
# Career description keywords (for semantic scoring)
# ──────────────────────────────────────────────

# High-value keywords in role descriptions (weight 3)
DESC_KEYWORDS_CORE = [
    "embedding", "retrieval", "ranking system", "recommendation system",
    "search system", "vector database", "semantic search", "similarity search",
    "information retrieval", "re-ranking", "reranking", "vector search",
    "candidate ranking", "candidate matching", "talent matching",
    "hybrid search", "dense retrieval", "sparse retrieval",
    "bm25", "tf-idf", "inverted index",
]

# Strong ML/AI keywords in descriptions (weight 2)
DESC_KEYWORDS_STRONG = [
    "machine learning", "deep learning", "neural network",
    "model training", "model deployment", "ml pipeline",
    "nlp", "natural language", "transformer", "bert", "gpt",
    "fine-tuning", "fine tuning", "inference", "serving",
    "a/b testing", "experimentation", "evaluation metric",
    "classification", "regression", "feature engineering",
    "data pipeline", "data science", "data-driven",
    "pytorch", "tensorflow", "scikit",
    "deployed", "production", "real users", "at scale",
    "recommendation", "personalization",
    "llm", "large language model",
]

# Moderate keywords (weight 1)
DESC_KEYWORDS_MODERATE = [
    "python", "api", "microservice", "backend",
    "cloud", "aws", "gcp", "azure",
    "docker", "kubernetes",
    "sql", "database", "data warehouse",
    "spark", "airflow", "kafka",
    "analytics", "dashboard", "metrics",
    "algorithm", "optimization",
]

# Negative keywords in descriptions (weight -2)
DESC_KEYWORDS_NEGATIVE = [
    "accounting", "financial reporting", "tax filing", "audit",
    "ledger", "accounts payable", "accounts receivable", "gl",
    "ind-as", "gaap", "statutory compliance",
    "mechanical engineering", "cad", "solidworks", "creo", "ansys",
    "manufacturing", "tooling", "dfm", "dfma", "production scale-up",
    "customer support", "support agent", "tier-1", "tier-2", "ticket",
    "escalation process", "knowledge base", "agent training",
    "brand design", "packaging design", "creative direction",
    "adobe suite", "visual system", "typography", "logo",
    "content writing", "seo strategy", "editorial calendar",
    "freelance writer", "longform article", "blog post",
    "warehouse", "fulfillment", "picking", "packing", "outbound",
    "supply chain", "logistics", "inventory",
    "sales", "quota", "cold calling", "lead generation",
    "civil engineering", "structural", "construction",
    "six sigma", "lean", "process re-engineering",
]

# ──────────────────────────────────────────────
# Location / logistics
# ──────────────────────────────────────────────

PREFERRED_CITIES = {
    "pune", "noida", "hyderabad", "mumbai", "delhi",
    "gurgaon", "gurugram", "bengaluru", "bangalore",
    "chennai", "kolkata", "new delhi",
}

PREFERRED_REGIONS = {
    "maharashtra", "uttar pradesh", "telangana",
    "karnataka", "haryana", "delhi ncr",
    "tamil nadu", "west bengal",
}

# ──────────────────────────────────────────────
# Behavioral thresholds
# ──────────────────────────────────────────────

# Last active date: days since last login
ACTIVE_EXCELLENT = 30       # active within last month
ACTIVE_GOOD = 90            # active within last 3 months
ACTIVE_STALE = 180          # 6 months → heavy penalty
ACTIVE_DEAD = 365           # 1 year → near-zero availability

# Response rate thresholds
RESPONSE_RATE_EXCELLENT = 0.7
RESPONSE_RATE_GOOD = 0.4
RESPONSE_RATE_POOR = 0.1

# Notice period (days)
NOTICE_IDEAL = 30           # sub-30 is best per JD
NOTICE_OK = 60
NOTICE_LONG = 90

# Salary range (INR LPA) — reasonable for Senior AI Engineer in India
SALARY_MIN_REASONABLE = 10
SALARY_MAX_REASONABLE = 80

# ──────────────────────────────────────────────
# Honeypot detection thresholds
# ──────────────────────────────────────────────

# Duration mismatch: if computed duration and stated duration differ by this much
HONEYPOT_DURATION_MISMATCH_MONTHS = 30

# Expert skills with zero duration
HONEYPOT_EXPERT_ZERO_DURATION_THRESHOLD = 2  # 2+ such skills → honeypot

# Too many expert skills for low experience
HONEYPOT_EXPERT_SKILLS_VS_EXPERIENCE_RATIO = 3  # expert_count / years > this → suspicious

# Experience vs career timeline mismatch
HONEYPOT_EXPERIENCE_TIMELINE_MISMATCH_YEARS = 5

# Skill assessment contradiction
HONEYPOT_ASSESSMENT_VS_PROFICIENCY_GAP = 30  # expert but score < 30
