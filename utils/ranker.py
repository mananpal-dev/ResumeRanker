# ============================================================
#   utils/ranker.py  –  Scoring & ranking engine
# ============================================================

import os
import time
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from config import (
    TFIDF_WEIGHT, KEYWORD_WEIGHT, SENIORITY_WEIGHT, EDUCATION_WEIGHT,
    KEYWORD_BOOST_PER_MATCH, SHORTLIST_THRESHOLD, MAYBE_THRESHOLD,
    BOOST_KEYWORDS, SENIORITY_TIERS, EDUCATION_TIERS
)
from utils.text_processing import (
    extract_text, clean_text, is_valid,
    extract_email, extract_phone, extract_name,
    extract_linkedin, extract_github,
    detect_skills, detect_all_skills_flat,
    detect_seniority, detect_education,
    extract_years_of_experience
)


# ── Data model ────────────────────────────────────────────────
@dataclass
class CandidateResult:
    filename:       str
    name:           str
    email:          str
    phone:          str
    linkedin:       str
    github:         str
    raw_text:       str
    cleaned_text:   str

    tfidf_score:    float = 0.0
    keyword_score:  float = 0.0
    seniority_score: float = 0.0
    education_score: float = 0.0
    final_score:    float = 0.0

    matched_skills: Dict[str, List[str]] = field(default_factory=dict)
    all_skills_flat: List[str] = field(default_factory=list)
    seniority:      str = "unknown"
    education:      str = "unknown"
    experience_years: int = 0
    status:         str = "Not Relevant"   # Shortlisted / Maybe / Not Relevant
    rank:           int = 0

    # skill gap analysis
    missing_skills: List[str] = field(default_factory=list)
    skill_coverage: float = 0.0   # % of JD keywords found in resume


def _status(score: float) -> str:
    if score >= SHORTLIST_THRESHOLD:
        return "Shortlisted"
    elif score >= MAYBE_THRESHOLD:
        return "Maybe"
    return "Not Relevant"


def _seniority_score(resume_text: str, jd_text: str) -> float:
    """Return 1.0 if seniority matches JD, 0.5 if close, 0.0 otherwise."""
    jd_tier = detect_seniority(jd_text)
    res_tier = detect_seniority(resume_text)
    if jd_tier == "unknown" or res_tier == "unknown":
        return 0.5   # neutral when unknown
    if jd_tier == res_tier:
        return 1.0
    adjacent = {("senior", "mid"), ("mid", "junior"), ("mid", "senior")}
    if (jd_tier, res_tier) in adjacent or (res_tier, jd_tier) in adjacent:
        return 0.5
    return 0.0


def _education_score(resume_text: str, jd_text: str) -> float:
    tier_order = ["diploma", "bachelors", "masters", "phd", "unknown"]
    jd_edu = detect_education(jd_text)
    res_edu = detect_education(resume_text)
    if jd_edu == "unknown":
        return 0.5
    if res_edu == "unknown":
        return 0.3
    j = tier_order.index(jd_edu) if jd_edu in tier_order else 0
    r = tier_order.index(res_edu) if res_edu in tier_order else 0
    if r >= j:
        return 1.0
    if r == j - 1:
        return 0.6
    return 0.2


def _skill_gap(jd_keywords: List[str], candidate_skills: List[str]) -> Tuple[List[str], float]:
    matched = set(candidate_skills)
    missing = [k for k in jd_keywords if k not in matched]
    coverage = (len(jd_keywords) - len(missing)) / max(len(jd_keywords), 1)
    return missing, coverage


# ── Main ranking function ─────────────────────────────────────
def rank_resumes(
    resume_folder: str,
    jd_text: str,
    progress_callback=None   # callable(current, total, filename)
) -> Tuple[List[CandidateResult], List[str]]:
    """
    Returns:
        ranked_results  – list of CandidateResult sorted by final_score DESC
        ignored_files   – list of filenames skipped (too short / unreadable)
    """
    start_time = time.time()

    # ── 1. Collect resumes ─────────────────────────────────────
    supported_ext = (".pdf", ".docx", ".doc", ".txt")
    all_files = [
        f for f in os.listdir(resume_folder)
        if os.path.splitext(f)[1].lower() in supported_ext
    ]

    parsed: Dict[str, str] = {}   # filename → raw text
    ignored: List[str] = []

    for idx, fname in enumerate(all_files):
        if progress_callback:
            progress_callback(idx + 1, len(all_files), fname)

        path = os.path.join(resume_folder, fname)
        raw = extract_text(path)

        if not raw.strip() or not is_valid(raw):
            ignored.append(fname)
            continue

        parsed[fname] = raw

    if not parsed:
        return [], ignored

    # ── 2. TF-IDF cosine similarity ────────────────────────────
    cleaned_jd = clean_text(jd_text)
    docs = [cleaned_jd] + [clean_text(t) for t in parsed.values()]

    vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
    tfidf_matrix = vectorizer.fit_transform(docs)
    similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

    # JD keywords for gap analysis
    jd_keywords = [k for k in BOOST_KEYWORDS if k in cleaned_jd.lower()]

    # ── 3. Build CandidateResult objects ──────────────────────
    results: List[CandidateResult] = []

    for i, (fname, raw) in enumerate(parsed.items()):
        cleaned = clean_text(raw)

        skills_grouped = detect_skills(cleaned)
        all_skills = detect_all_skills_flat(cleaned)

        # keyword score
        matched_kw = [k for k in BOOST_KEYWORDS if k in cleaned]
        kw_score = min(len(matched_kw) * KEYWORD_BOOST_PER_MATCH, 1.0)

        # seniority + education scores
        sen_score = _seniority_score(cleaned, cleaned_jd)
        edu_score = _education_score(cleaned, cleaned_jd)

        # weighted final
        tfidf_s = float(similarities[i])
        final = (
            TFIDF_WEIGHT    * tfidf_s  +
            KEYWORD_WEIGHT  * kw_score +
            SENIORITY_WEIGHT * sen_score +
            EDUCATION_WEIGHT * edu_score
        )
        final = round(min(final, 1.0), 4)

        missing, coverage = _skill_gap(jd_keywords, all_skills)

        c = CandidateResult(
            filename        = fname,
            name            = extract_name(raw),
            email           = extract_email(raw),
            phone           = extract_phone(raw),
            linkedin        = extract_linkedin(raw),
            github          = extract_github(raw),
            raw_text        = raw,
            cleaned_text    = cleaned,
            tfidf_score     = round(tfidf_s, 4),
            keyword_score   = round(kw_score, 4),
            seniority_score = round(sen_score, 4),
            education_score = round(edu_score, 4),
            final_score     = final,
            matched_skills  = skills_grouped,
            all_skills_flat = all_skills,
            seniority       = detect_seniority(cleaned),
            education       = detect_education(cleaned),
            experience_years = extract_years_of_experience(raw),
            status          = _status(final),
            missing_skills  = missing,
            skill_coverage  = round(coverage * 100, 1),
        )
        results.append(c)

    # ── 4. Sort & assign ranks ─────────────────────────────────
    results.sort(key=lambda x: x.final_score, reverse=True)
    for rank, r in enumerate(results, 1):
        r.rank = rank

    return results, ignored


# ── Summary stats ─────────────────────────────────────────────
def compute_summary(results: List[CandidateResult]) -> Dict:
    if not results:
        return {}
    scores = [r.final_score for r in results]
    shortlisted = [r for r in results if r.status == "Shortlisted"]
    maybe       = [r for r in results if r.status == "Maybe"]
    not_rel     = [r for r in results if r.status == "Not Relevant"]

    return {
        "total":          len(results),
        "shortlisted":    len(shortlisted),
        "maybe":          len(maybe),
        "not_relevant":   len(not_rel),
        "avg_score":      round(float(np.mean(scores)), 4),
        "top_score":      round(float(np.max(scores)), 4),
        "low_score":      round(float(np.min(scores)), 4),
        "top_candidate":  results[0].filename if results else "",
    }
