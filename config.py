# ============================================================
#   config.py  –  Centralised settings for AI Resume Ranker
# ============================================================

APP_NAME    = "AI Resume Ranker"
APP_VERSION = "3.0.0"
APP_AUTHOR  = "Manan Pal"

# ── Scoring weights ─────────────────────────────────────────
TFIDF_WEIGHT     = 0.60   # weight for TF-IDF cosine similarity
KEYWORD_WEIGHT   = 0.25   # weight for exact-match keyword score
SENIORITY_WEIGHT = 0.10   # weight for seniority-level match
EDUCATION_WEIGHT = 0.05   # weight for education tier match

# ── Keyword boost amount per matched keyword ─────────────────
KEYWORD_BOOST_PER_MATCH = 0.04

# ── Minimum words in a resume to be considered valid ─────────
MIN_WORDS = 40

# ── Score thresholds ──────────────────────────────────────────
SHORTLIST_THRESHOLD = 0.45   # ≥ this → "Shortlisted"
MAYBE_THRESHOLD     = 0.20   # ≥ this → "Maybe"
# below MAYBE_THRESHOLD → "Not Relevant"

# ── Recruiter priority thresholds ────────────────────────────
PRIORITY_HIGH_SCORE    = 0.82   # score + coverage + exp → "High Priority"
PRIORITY_HIGH_COVERAGE = 65     # skill coverage % floor for High Priority
PRIORITY_HIGH_EXP      = 4      # years floor for High Priority
PRIORITY_MEDIUM_SCORE  = 0.62   # score floor for "Strong Review"
PRIORITY_MEDIUM_COVERAGE = 45   # coverage floor for Strong Review

# ── Interview readiness thresholds ───────────────────────────
INTERVIEW_READY_SCORE    = 0.75  # score threshold → "Ready now"
INTERVIEW_REVIEW_STATUS  = "Maybe"

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
    "phd":       ["ph.d", "phd", "doctorate", "doctoral"],
    "masters":   ["m.tech", "m.sc", "msc", "m.e", "ms ", "master", "mba"],
    "bachelors": ["b.tech", "b.sc", "bsc", "b.e", "be ", "bachelor", "bca", "b.ca"],
    "diploma":   ["diploma", "associate degree", "polytechnic"],
}

# ── Recruiter decision options ────────────────────────────────
RECRUITER_DECISIONS = [
    "Move to recruiter screen",
    "Send to hiring manager",
    "Keep in backup pipeline",
    "Archive for now",
]
# ============================================================
#   config.py  –  Centralised settings for AI Resume Ranker
# ============================================================

APP_NAME = "AI Resume Ranker"
APP_VERSION = "4.0.0"
APP_AUTHOR = "Manan Pal"

# ── Scoring weights ─────────────────────────────────────────
TFIDF_WEIGHT = 0.60
KEYWORD_WEIGHT = 0.25
SENIORITY_WEIGHT = 0.10
EDUCATION_WEIGHT = 0.05

# ── Keyword boost amount per matched keyword ────────────────
KEYWORD_BOOST_PER_MATCH = 0.04

# ── Minimum words in a resume to be considered valid ────────
MIN_WORDS = 40

# ── Score thresholds ────────────────────────────────────────
SHORTLIST_THRESHOLD = 0.45
MAYBE_THRESHOLD = 0.20

# ── Recruiter priority thresholds ───────────────────────────
PRIORITY_HIGH_SCORE = 0.82
PRIORITY_HIGH_COVERAGE = 65
PRIORITY_HIGH_EXP = 4
PRIORITY_MEDIUM_SCORE = 0.62
PRIORITY_MEDIUM_COVERAGE = 45

# ── Interview readiness thresholds ──────────────────────────
INTERVIEW_READY_SCORE = 0.75
INTERVIEW_REVIEW_STATUS = "Maybe"

# ── Skill taxonomy (grouped) ────────────────────────────────
SKILL_GROUPS = {
    "Programming Languages": [
        "python", "java", "c++", "c#", "javascript", "typescript",
        "r", "scala", "go", "rust", "kotlin", "swift",
    ],
    "ML / AI": [
        "machine learning", "deep learning", "nlp",
        "natural language processing", "computer vision",
        "reinforcement learning", "llm", "generative ai",
        "transformer", "bert", "gpt", "rag",
    ],
    "Frameworks & Libraries": [
        "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn",
        "hugging face", "langchain", "openai", "pandas", "numpy",
        "matplotlib", "seaborn", "plotly", "scipy", "xgboost", "lightgbm",
    ],
    "Web & API": [
        "flask", "django", "fastapi", "rest api", "graphql",
        "react", "vue", "angular", "node", "express",
    ],
    "Databases & Cloud": [
        "sql", "mysql", "postgresql", "mongodb", "redis",
        "aws", "gcp", "azure", "docker", "kubernetes",
        "spark", "hadoop", "airflow", "kafka",
    ],
    "Tools & Practices": [
        "git", "github", "mlflow", "dvc", "ci/cd",
        "agile", "scrum", "linux", "bash",
    ],
}

BOOST_KEYWORDS = [kw for group in SKILL_GROUPS.values() for kw in group]

# ── Seniority keywords ──────────────────────────────────────
SENIORITY_TIERS = {
    "senior": ["senior", "lead", "principal", "staff", "architect", "head of", "director"],
    "mid": ["mid", "intermediate", "associate", "ii", "iii"],
    "junior": ["junior", "entry", "fresher", "graduate", "intern", "trainee"],
}

# ── Education keywords ──────────────────────────────────────
EDUCATION_TIERS = {
    "phd": ["ph.d", "phd", "doctorate", "doctoral"],
    "masters": ["m.tech", "m.sc", "msc", "m.e", "ms ", "master", "mba"],
    "bachelors": ["b.tech", "b.sc", "bsc", "b.e", "be ", "bachelor", "bca", "b.ca"],
    "diploma": ["diploma", "associate degree", "polytechnic"],
}

# ── Recruiter decision options ──────────────────────────────
RECRUITER_DECISIONS = [
    "Move to recruiter screen",
    "Send to hiring manager",
    "Keep in backup pipeline",
    "Archive for now",
]

# ── Shared presenter copy ───────────────────────────────────
RECRUITER_SIGNAL_COPY = {
    "high_priority": "Ready to highlight in the hiring review.",
    "strong_review": "Worth closer recruiter validation.",
    "hold": "Potential fit with targeted screening.",
    "low": "Lower confidence for the current opening.",
}

# ── Output paths ────────────────────────────────────────────
CSV_OUTPUT_PATH = "ranked_resumes.csv"
REPORT_OUTPUT_PATH = "ranking_report.txt"

# ── Output paths ──────────────────────────────────────────────
CSV_OUTPUT_PATH    = "ranked_resumes.csv"
REPORT_OUTPUT_PATH = "ranking_report.txt"