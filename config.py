# ============================================================
#   config.py  –  Centralised settings for AI Resume Ranker
# ============================================================

APP_NAME    = "AI Resume Ranker"
APP_VERSION = "2.0.0"
APP_AUTHOR  = "Manan Pal"

# ── Scoring weights ─────────────────────────────────────────
TFIDF_WEIGHT    = 0.60   # weight for TF-IDF cosine similarity
KEYWORD_WEIGHT  = 0.25   # weight for exact-match keyword score
SENIORITY_WEIGHT = 0.10  # weight for seniority-level match
EDUCATION_WEIGHT = 0.05  # weight for education tier match

# ── Keyword boost amount per matched keyword ─────────────────
KEYWORD_BOOST_PER_MATCH = 0.04

# ── Minimum words in a resume to be considered valid ─────────
MIN_WORDS = 40

# ── Score thresholds ──────────────────────────────────────────
SHORTLIST_THRESHOLD   = 0.45   # ≥ this → "Shortlisted"
MAYBE_THRESHOLD       = 0.20   # ≥ this → "Maybe"
# below MAYBE_THRESHOLD → "Not Relevant"

# ── Skill taxonomy (grouped) ──────────────────────────────────
SKILL_GROUPS = {
    "Programming Languages": [
        "python", "java", "c++", "c#", "javascript", "typescript",
        "r", "scala", "go", "rust", "kotlin", "swift"
    ],
    "ML / AI": [
        "machine learning", "deep learning", "nlp",
        "natural language processing", "computer vision",
        "reinforcement learning", "llm", "generative ai",
        "transformer", "bert", "gpt", "rag"
    ],
    "Frameworks & Libraries": [
        "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn",
        "hugging face", "langchain", "openai", "pandas", "numpy",
        "matplotlib", "seaborn", "plotly", "scipy", "xgboost", "lightgbm"
    ],
    "Web & API": [
        "flask", "django", "fastapi", "rest api", "graphql",
        "react", "vue", "angular", "node", "express"
    ],
    "Databases & Cloud": [
        "sql", "mysql", "postgresql", "mongodb", "redis",
        "aws", "gcp", "azure", "docker", "kubernetes",
        "spark", "hadoop", "airflow", "kafka"
    ],
    "Tools & Practices": [
        "git", "github", "mlflow", "dvc", "ci/cd",
        "agile", "scrum", "linux", "bash"
    ],
}

# flat list used by keyword matching
BOOST_KEYWORDS = [kw for group in SKILL_GROUPS.values() for kw in group]

# ── Seniority keywords ────────────────────────────────────────
SENIORITY_TIERS = {
    "senior":  ["senior", "lead", "principal", "staff", "architect", "head of", "director"],
    "mid":     ["mid", "intermediate", "associate", "ii", "iii"],
    "junior":  ["junior", "entry", "fresher", "graduate", "intern", "trainee"],
}

# ── Education keywords ────────────────────────────────────────
EDUCATION_TIERS = {
    "phd":     ["ph.d", "phd", "doctorate", "doctoral"],
    "masters": ["m.tech", "m.sc", "msc", "m.e", "ms ", "master", "mba"],
    "bachelors": ["b.tech", "b.sc", "bsc", "b.e", "be ", "bachelor", "bca", "b.ca"],
    "diploma": ["diploma", "associate degree", "polytechnic"],
}

# ── Output paths ──────────────────────────────────────────────
CSV_OUTPUT_PATH    = "ranked_resumes.csv"
REPORT_OUTPUT_PATH = "ranking_report.txt"
