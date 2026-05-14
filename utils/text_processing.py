# ============================================================
#   utils/text_processing.py  –  PDF parsing & NLP helpers
# ============================================================

import re
import os

# ── Optional imports with graceful fallbacks ─────────────────
try:
    import PyPDF2
    _PYPDF2 = True
except ImportError:
    _PYPDF2 = False

try:
    import pdfplumber
    _PDFPLUMBER = True
except ImportError:
    _PDFPLUMBER = False

try:
    import docx2txt
    _DOCX = True
except ImportError:
    _DOCX = False

from config import MIN_WORDS, SENIORITY_TIERS, EDUCATION_TIERS, SKILL_GROUPS


# ── PDF text extraction (tries pdfplumber first, fallback PyPDF2) ──
def extract_text_from_pdf(path: str) -> str:
    text = ""

    if _PDFPLUMBER:
        try:
            import pdfplumber
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    t = page.extract_text()
                    if t:
                        text += t + "\n"
            if text.strip():
                return text
        except Exception:
            pass

    if _PYPDF2:
        try:
            with open(path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    t = page.extract_text()
                    if t:
                        text += t + "\n"
        except Exception as e:
            print(f"  [!] PDF read error ({os.path.basename(path)}): {e}")

    return text


def extract_text_from_docx(path: str) -> str:
    if not _DOCX:
        return ""
    try:
        return docx2txt.process(path)
    except Exception as e:
        print(f"  [!] DOCX read error: {e}")
        return ""


def extract_text(path: str) -> str:
    """Auto-detect file type and extract text."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(path)
    elif ext in (".docx", ".doc"):
        return extract_text_from_docx(path)
    elif ext == ".txt":
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception:
            return ""
    return ""


# ── Text cleaning ─────────────────────────────────────────────
def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s\.\+#]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def is_valid(text: str) -> bool:
    return len(text.split()) >= MIN_WORDS


# ── Contact info extraction ───────────────────────────────────
def extract_email(text: str) -> str:
    m = re.search(r'[\w.\-+]+@[\w.\-]+\.[a-zA-Z]{2,}', text)
    return m.group(0) if m else ""


def extract_phone(text: str) -> str:
    m = re.search(r'(\+?\d[\d\s\-().]{7,}\d)', text)
    return m.group(0).strip() if m else ""


def extract_name(text: str) -> str:
    """Best-effort: take the first non-blank line as candidate name."""
    for line in text.splitlines():
        line = line.strip()
        if line and len(line.split()) <= 5 and not re.search(r'[@\d]', line):
            return line
    return ""


def extract_linkedin(text: str) -> str:
    m = re.search(r'linkedin\.com/in/[\w\-]+', text, re.IGNORECASE)
    return m.group(0) if m else ""


def extract_github(text: str) -> str:
    m = re.search(r'github\.com/[\w\-]+', text, re.IGNORECASE)
    return m.group(0) if m else ""


# ── Skill detection ───────────────────────────────────────────
def detect_skills(text: str) -> dict:
    """Return a dict  group → [matched skills]."""
    t = text.lower()
    result = {}
    for group, skills in SKILL_GROUPS.items():
        matched = [s for s in skills if s in t]
        if matched:
            result[group] = matched
    return result


def detect_all_skills_flat(text: str) -> list:
    groups = detect_skills(text)
    return [s for skills in groups.values() for s in skills]


# ── Seniority detection ───────────────────────────────────────
def detect_seniority(text: str) -> str:
    t = text.lower()
    for tier, keywords in SENIORITY_TIERS.items():
        if any(kw in t for kw in keywords):
            return tier
    return "unknown"


# ── Education detection ───────────────────────────────────────
def detect_education(text: str) -> str:
    t = text.lower()
    for tier, keywords in EDUCATION_TIERS.items():
        if any(kw in t for kw in keywords):
            return tier
    return "unknown"


# ── Experience years ─────────────────────────────────────────
def extract_years_of_experience(text: str) -> int:
    """Try to guess years of experience from the resume text."""
    t = text.lower()
    # e.g. "5 years of experience", "3+ years"
    m = re.search(r'(\d+)\s*\+?\s*years?\s+(of\s+)?(experience|work)', t)
    if m:
        return int(m.group(1))
    # count year ranges like 2019-2023
    years = re.findall(r'\b(20\d{2}|19\d{2})\b', t)
    if len(years) >= 2:
        years = sorted(set(int(y) for y in years))
        return max(0, years[-1] - years[0])
    return 0
