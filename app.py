# ============================================================
#   app.py  –  Streamlit Web App  |  AI Resume Ranker 
#   Run:  streamlit run app.py
# ============================================================

import base64
import os
import sys
import tempfile
import time
from collections import Counter
from typing import List

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, os.path.dirname(__file__))

from config import (
    APP_VERSION,
    INTERVIEW_READY_SCORE,
    MAYBE_THRESHOLD,
    PRIORITY_HIGH_COVERAGE,
    PRIORITY_HIGH_EXP,
    PRIORITY_HIGH_SCORE,
    PRIORITY_MEDIUM_COVERAGE,
    PRIORITY_MEDIUM_SCORE,
    RECRUITER_DECISIONS,
    SHORTLIST_THRESHOLD,
)
from utils.exporter import export_csv, export_json, export_txt_report
from utils.ranker import CandidateResult, compute_summary, rank_resumes

BASE_DIR = os.path.dirname(__file__)
SAMPLE_JD_PATH = os.path.join(BASE_DIR, "sample_jd.txt")
SAMPLE_RESUME_CANDIDATES = [
    os.path.join(BASE_DIR, "resume"),
    os.path.join(BASE_DIR, "resumes"),
    os.path.join(BASE_DIR, "sample_resumes"),
]


st.set_page_config(
    page_title="AI Resume Ranker",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)


for key, default in {
    "recruiter_notes": {},
    "recruiter_decisions": {},
    "jd_text_override": "",
    "results": None,
    "summary": None,
    "data_source": "sample",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=DM+Sans:wght@400;500;700;800&display=swap');

    :root {
        --bg: #0d0f14;
        --surface: #151922;
        --surface-2: #1a1f2a;
        --ink: #f5f7fb;
        --muted: #c9d1dc;
        --line: rgba(246, 196, 83, 0.12);
        --emerald: #ffd166;
        --emerald-soft: #2a2416;
        --gold: #ffbf5f;
        --gold-soft: #2a2116;
        --coral: #ff9f5a;
        --coral-soft: #2b1d15;
        --navy: #ffd677;
        --navy-soft: #201c27;
        --shadow: 0 22px 60px rgba(0, 0, 0, 0.34);
    }

    .stApp {
        background:
            radial-gradient(circle at 8% 8%, rgba(255,191,95,0.18), transparent 24%),
            radial-gradient(circle at 86% 10%, rgba(255,159,90,0.12), transparent 24%),
            linear-gradient(180deg, #0d0f14 0%, #12151c 46%, #171b24 100%);
        color: var(--ink);
    }

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
        color: var(--ink);
    }

    h1, h2, h3, h4, .display-serif {
        font-family: 'Fraunces', serif !important;
        letter-spacing: 0.2px;
        color: var(--ink);
    }

    .block-container {
        max-width: 1380px;
        padding-top: 1.05rem;
        padding-bottom: 2rem;
    }

    .hero {
        position: relative;
        overflow: hidden;
        background:
            linear-gradient(135deg, rgba(24,27,36,0.97), rgba(17,20,28,0.96)),
            linear-gradient(120deg, #191d26, #10131a);
        border: 1px solid var(--line);
        border-radius: 34px;
        padding: 2.7rem 2.45rem 2.25rem;
        box-shadow: var(--shadow);
        margin-bottom: 1.2rem;
    }

    .hero::before {
        content: "";
        position: absolute;
        width: 380px;
        height: 380px;
        right: -110px;
        top: -150px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(255,191,95,0.16), transparent 60%);
    }

    .hero::after {
        content: "";
        position: absolute;
        width: 360px;
        height: 360px;
        left: -110px;
        bottom: -210px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(255,159,90,0.16), transparent 62%);
    }

    .hero-row {
        position: relative;
        z-index: 2;
        display: flex;
        gap: 1.8rem;
        justify-content: space-between;
        align-items: flex-start;
        flex-wrap: wrap;
    }

    .eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 0.42rem 0.82rem;
        border-radius: 999px;
        background: rgba(246,196,83,0.10);
        color: var(--emerald);
        font-weight: 800;
        font-size: 0.76rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .hero-title {
        margin-top: 0.95rem;
        font-size: 4rem;
        line-height: 0.94;
        max-width: 780px;
    }

    .hero-sub {
        margin-top: 0.9rem;
        max-width: 710px;
        color: var(--muted);
        font-size: 1rem;
        line-height: 1.74;
    }

    .hero-panel {
        min-width: 300px;
        max-width: 330px;
        background: rgba(24,28,37,0.9);
        border: 1px solid var(--line);
        border-radius: 24px;
        padding: 1.05rem;
        box-shadow: 0 12px 30px rgba(27,35,44,0.05);
    }

    .hero-panel-title {
        font-size: 0.74rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--muted);
        font-weight: 800;
    }

    .hero-panel-value {
        margin-top: 0.28rem;
        font-size: 1.9rem;
        font-weight: 800;
    }

    .hero-panel-note {
        margin-top: 0.36rem;
        color: var(--muted);
        font-size: 0.9rem;
        line-height: 1.62;
    }

    .ribbon-row {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 1rem;
        margin: 1rem 0 1.45rem;
    }

    .ribbon-card {
        background: rgba(22,26,35,0.92);
        border: 1px solid var(--line);
        border-radius: 22px;
        padding: 1rem 1rem 0.94rem;
        box-shadow: 0 10px 26px rgba(27,35,44,0.04);
    }

    .ribbon-label {
        font-size: 0.74rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: var(--muted);
    }

    .ribbon-value {
        margin-top: 0.3rem;
        font-size: 1.58rem;
        font-weight: 800;
    }

    .ribbon-sub {
        margin-top: 0.18rem;
        color: var(--muted);
        font-size: 0.86rem;
    }

    .signal-grid {
        display: grid;
        grid-template-columns: 1.25fr 1fr 1fr;
        gap: 1rem;
        margin: 0.6rem 0 1.55rem;
    }

    .signal-card {
        border-radius: 24px;
        padding: 1.15rem 1.15rem 1rem;
        box-shadow: var(--shadow);
        border: 1px solid var(--line);
        min-height: 150px;
    }

    .signal-card.emerald {
        background: linear-gradient(180deg, #211b12, #16120d);
    }

    .signal-card.gold {
        background: linear-gradient(180deg, #261e13, #17120d);
    }

    .signal-card.coral {
        background: linear-gradient(180deg, #291d15, #17110c);
    }

    .signal-kicker {
        font-size: 0.74rem;
        text-transform: uppercase;
        font-weight: 800;
        letter-spacing: 0.08em;
        color: rgba(255,255,255,0.72);
    }

    .signal-title {
        margin-top: 0.42rem;
        font-size: 1.4rem;
        font-weight: 800;
    }

    .signal-copy {
        margin-top: 0.45rem;
        font-size: 0.92rem;
        line-height: 1.62;
        color: rgba(255,255,255,0.88);
    }

    .section-card {
        background: rgba(22,26,35,0.92);
        border: 1px solid var(--line);
        border-radius: 26px;
        padding: 1.12rem 1.15rem 1.2rem;
        box-shadow: var(--shadow);
    }

    .candidate-card {
        position: relative;
        overflow: hidden;
        background: linear-gradient(180deg, rgba(24,27,36,0.98), rgba(17,20,28,0.98));
        border: 1px solid var(--line);
        border-radius: 28px;
        padding: 1.2rem 1.25rem 1.15rem;
        margin-bottom: 1rem;
        box-shadow: var(--shadow);
    }

    .candidate-card::before {
        content: "";
        position: absolute;
        inset: 0 auto 0 0;
        width: 7px;
        background: linear-gradient(180deg, #ff9f5a, #f6c453);
    }

    .candidate-top {
        display: flex;
        justify-content: space-between;
        gap: 1rem;
        align-items: flex-start;
    }

    .rank-pill {
        min-width: 82px;
        text-align: center;
        background: #0d0f14;
        color: #f6c453;
        border-radius: 20px;
        padding: 0.7rem 0.82rem;
    }

    .rank-pill .k {
        display: block;
        font-size: 0.72rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        opacity: 0.76;
    }

    .rank-pill .v {
        display: block;
        font-size: 1.28rem;
        font-weight: 800;
        margin-top: 0.14rem;
    }

    .candidate-name {
        font-size: 1.52rem;
        font-weight: 800;
        color: var(--ink);
        margin: 0;
    }

    .candidate-file {
        color: var(--muted);
        font-size: 0.86rem;
        margin-top: 0.18rem;
    }

    .candidate-headline {
        margin-top: 0.62rem;
        color: rgba(255,255,255,0.88);
        font-size: 0.95rem;
        line-height: 1.68;
    }

    .chip-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.46rem;
        margin: 0.84rem 0 0.72rem;
    }

    .status-chip, .priority-chip, .soft-chip {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        border-radius: 999px;
        padding: 0.42rem 0.82rem;
        font-size: 0.78rem;
        font-weight: 700;
        border: 1px solid transparent;
    }

    .status-shortlisted { background: #231f15; color: #ffd978; border-color: #624b21; }
    .status-maybe { background: #2a2116; color: #ffcc72; border-color: #6d4e22; }
    .status-not { background: #2a1c15; color: #ffb96d; border-color: #6c4125; }
    .priority-high { background: #2b2315; color: #ffd978; }
    .priority-mid { background: #292115; color: #ffca6c; }
    .priority-low { background: #251c16; color: #efb36f; }
    .soft-chip { background: #1b202a; color: #f5f7fb; border-color: rgba(246,196,83,0.10); }

    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 0.8rem;
        margin-top: 0.94rem;
    }

    .metric-mini {
        background: rgba(29,34,44,0.96);
        border: 1px solid rgba(246,196,83,0.08);
        border-radius: 18px;
        padding: 0.8rem;
    }

    .metric-mini .label {
        font-size: 0.72rem;
        letter-spacing: 0.07em;
        text-transform: uppercase;
        color: var(--muted);
        font-weight: 800;
    }

    .metric-mini .value {
        margin-top: 0.28rem;
        font-size: 1.08rem;
        font-weight: 800;
        color: var(--ink);
    }

    .score-track {
        margin-top: 0.84rem;
        height: 11px;
        background: #2a2e38;
        border-radius: 999px;
        overflow: hidden;
    }

    .score-fill {
        height: 100%;
        border-radius: 999px;
        background: linear-gradient(90deg, #ff9f5a 0%, #f6c453 100%);
    }

    .score-note {
        margin-top: 0.4rem;
        font-size: 0.84rem;
        color: var(--muted);
    }

    .section-title {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--muted);
        font-weight: 800;
        margin-bottom: 0.45rem;
        margin-top: 1rem;
    }

    .skill-tag, .missing-tag {
        display: inline-block;
        border-radius: 999px;
        padding: 0.3rem 0.72rem;
        font-size: 0.76rem;
        margin: 0.18rem;
        font-weight: 700;
    }

    .skill-tag {
        background: #211d15;
        border: 1px solid #5f4922;
        color: #ffd978;
    }

    .missing-tag {
        background: #2a1d16;
        border: 1px solid #704426;
        color: #ffbd73;
    }

    .priority-banner {
        background: linear-gradient(90deg, #10131a, #261e13);
        color: #f5f7fb;
        border-radius: 18px;
        padding: 0.92rem 1rem;
        margin-top: 1rem;
        display: flex;
        justify-content: space-between;
        gap: 1rem;
        align-items: center;
        flex-wrap: wrap;
    }

    .priority-banner strong {
        color: #ffd978;
    }

    .priority-banner span {
        color: rgba(255,255,255,0.82);
        font-size: 0.9rem;
    }

    .table-card {
        background: rgba(22,26,35,0.92);
        border: 1px solid var(--line);
        border-radius: 22px;
        padding: 1rem;
        box-shadow: var(--shadow);
    }

    .muted-text {
        color: var(--muted);
        font-size: 0.89rem;
    }

    [data-testid="stSidebar"] {
        background:
            radial-gradient(circle at top right, rgba(255,191,95,0.18), transparent 28%),
            linear-gradient(180deg, #0f1117 0%, #141822 62%, #1a1f2a 100%);
    }

    [data-testid="stSidebar"] * {
        color: #f5f7fb !important;
    }

    .stButton > button, .stDownloadButton > button {
        border-radius: 14px;
        border: 1px solid rgba(246,196,83,0.18);
        background: linear-gradient(135deg, #f6c453, #ff9f5a);
        color: #0d0f14;
        font-weight: 800;
        box-shadow: 0 12px 28px rgba(0,0,0,0.24);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 0.45rem;
    }

    .stTabs [data-baseweb="tab"] {
        background: rgba(24,27,36,0.95);
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: 0.52rem 0.92rem;
        font-weight: 800;
        color: #f5f7fb !important;
    }

    .stTabs [aria-selected="true"] {
        background: #1d2330 !important;
        color: #ffffff !important;
        border-color: rgba(246,196,83,0.55) !important;
        box-shadow: inset 0 0 0 1px rgba(246,196,83,0.35);
    }

    div[data-testid="stExpander"] {
        border: 1px solid var(--line);
        border-radius: 18px;
        background: rgba(22,26,35,0.9);
        overflow: hidden;
    }

    .stTextArea textarea,
    .stTextInput input,
    .stSelectbox div[data-baseweb="select"],
    .stMultiSelect div[data-baseweb="select"],
    .stNumberInput input {
        background: #141821 !important;
        color: #f5f7fb !important;
        border: 1px solid rgba(246,196,83,0.14) !important;
    }

    .stMarkdown, .stText, p, li, label, span {
        color: var(--ink);
    }

    @media (max-width: 1100px) {
        .ribbon-row, .metrics-grid, .signal-grid {
            grid-template-columns: 1fr 1fr;
        }
    }

    @media (max-width: 760px) {
        .hero-title {
            font-size: 2.7rem;
        }
        .ribbon-row, .metrics-grid, .signal-grid {
            grid-template-columns: 1fr;
        }
        .candidate-top {
            flex-direction: column;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def status_chip(status: str) -> str:
    if status == "Shortlisted":
        return '<span class="status-chip status-shortlisted">Shortlisted</span>'
    if status == "Maybe":
        return '<span class="status-chip status-maybe">Maybe</span>'
    return '<span class="status-chip status-not">Not Relevant</span>'


def priority_chip(priority: str) -> str:
    mapping = {
        "High Priority": "priority-high",
        "Strong Review": "priority-mid",
        "Hold for Review": "priority-mid",
        "Low Priority": "priority-low",
    }
    cls = mapping.get(priority, "priority-low")
    return f'<span class="priority-chip {cls}">{priority}</span>'


def score_bar(score: float) -> str:
    pct = max(0, min(int(score * 100), 100))
    return (
        '<div class="score-track"><div class="score-fill" style="width:'
        f"{pct}%\"></div></div><div class=\"score-note\">Overall match score: <strong>{pct}%</strong></div>"
    )


def safe_text(value) -> str:
    if value is None:
        return "N/A"
    value = str(value).strip()
    return value if value else "N/A"


def titleize(value) -> str:
    text = safe_text(value)
    return text.title() if text != "N/A" else text


def skill_tags(skills: list, missing: bool = False, limit: int = 12) -> str:
    cls = "missing-tag" if missing else "skill-tag"
    clean = [str(s).strip() for s in skills if str(s).strip()]
    return " ".join(f'<span class="{cls}">{item}</span>' for item in clean[:limit])


def hex_to_rgba(hex_color: str, alpha: float = 0.18) -> str:
    color = hex_color.lstrip("#")
    if len(color) != 6:
        return f"rgba(15,118,110,{alpha})"
    r = int(color[0:2], 16)
    g = int(color[2:4], 16)
    b = int(color[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def _dl_button(label: str, data: bytes, filename: str, mime: str):
    b64 = base64.b64encode(data).decode()
    href = (
        f'<a href="data:{mime};base64,{b64}" download="{filename}" style="text-decoration:none;">'
        f'<button style="background:linear-gradient(135deg,#1d2935,#23685d);color:white;'
        f'border:none;border-radius:14px;font-family:DM Sans,sans-serif;font-weight:800;'
        f'padding:0.72rem 1.18rem;cursor:pointer;margin:4px;">{label}</button></a>'
    )
    st.markdown(href, unsafe_allow_html=True)


def get_sample_resume_dir() -> str:
    for path in SAMPLE_RESUME_CANDIDATES:
        if os.path.isdir(path):
            return path
    return ""


def sample_assets_available() -> bool:
    sample_dir = get_sample_resume_dir()
    return os.path.isfile(SAMPLE_JD_PATH) and bool(sample_dir)


def load_sample_jd_text() -> str:
    if not os.path.isfile(SAMPLE_JD_PATH):
        return ""
    with open(SAMPLE_JD_PATH, "r", encoding="utf-8", errors="ignore") as handle:
        return handle.read()


def build_candidate_palette(names: List[str]) -> dict:
    palette = [
        "#ffb84d", "#4dd0e1", "#ff7a90", "#9b87f5", "#67d17a",
        "#f97316", "#22c55e", "#60a5fa", "#f472b6", "#a3e635",
        "#facc15", "#38bdf8", "#fb7185", "#c084fc", "#34d399",
        "#f59e0b", "#818cf8", "#2dd4bf", "#e879f9", "#84cc16",
    ]
    return {name: palette[idx % len(palette)] for idx, name in enumerate(names)}


def run_ranking_pipeline(resume_dir: str, jd_text: str):
    prog_bar = st.progress(0, text="Preparing ranking run...")
    status_txt = st.empty()

    def progress_cb(cur, total, fname):
        pct = int(cur / total * 88) if total else 0
        prog_bar.progress(pct, text=f"Processing {fname}...")
        status_txt.text(f"Analysing {cur}/{total}: {fname}")

    started = time.time()
    results, ignored = rank_resumes(resume_dir, jd_text, progress_callback=progress_cb)
    elapsed = time.time() - started
    prog_bar.progress(100, text="Ranking complete")
    status_txt.empty()

    summary = compute_summary(results)
    st.session_state["results"] = results
    st.session_state["summary"] = summary
    st.session_state["jd_text"] = jd_text
    st.session_state["ignored"] = ignored
    st.session_state["elapsed"] = elapsed

    st.success(f"Ranked {len(results)} candidate(s) in {elapsed:.2f}s. Open the Results or Recruiter Brief tab next.")
    if ignored:
        st.warning(f"Skipped {len(ignored)} file(s): {', '.join(ignored)}")


def get_priority_label(candidate: CandidateResult) -> str:
    if (
        candidate.final_score >= PRIORITY_HIGH_SCORE
        and candidate.skill_coverage >= PRIORITY_HIGH_COVERAGE
        and candidate.experience_years >= PRIORITY_HIGH_EXP
    ):
        return "High Priority"
    if (
        candidate.final_score >= PRIORITY_MEDIUM_SCORE
        and candidate.skill_coverage >= PRIORITY_MEDIUM_COVERAGE
    ):
        return "Strong Review"
    if candidate.final_score >= MAYBE_THRESHOLD:
        return "Hold for Review"
    return "Low Priority"


def recommended_action(candidate: CandidateResult) -> str:
    if candidate.status == "Shortlisted" and candidate.final_score >= 0.80:
        return "Move to recruiter screen"
    if candidate.status == "Shortlisted":
        return "Send to hiring manager"
    if candidate.status == "Maybe":
        return "Keep in backup pipeline"
    return "Archive for now"


def interview_readiness(candidate: CandidateResult) -> str:
    if candidate.status == "Shortlisted" and candidate.final_score >= INTERVIEW_READY_SCORE:
        return "Ready now"
    if candidate.status == "Maybe":
        return "Needs closer review"
    return "Not recommended yet"


def recruiter_summary(candidate: CandidateResult) -> str:
    pct = int(candidate.final_score * 100)
    if candidate.status == "Shortlisted":
        return (
            f"This profile looks interview-worthy with a {pct}% match score, "
            f"{candidate.experience_years} years of experience, and {candidate.skill_coverage}% skill coverage."
        )
    if candidate.status == "Maybe":
        return (
            f"This candidate has a usable base at {pct}% match, but the slate would benefit from targeted "
            f"validation around skill gaps and role alignment."
        )
    return (
        f"This profile currently presents limited fit at {pct}% match and is better positioned as an archive "
        f"or future-role candidate."
    )


def top_strengths(candidate: CandidateResult, limit: int = 4) -> list:
    strengths = [s for s in candidate.all_skills_flat if str(s).strip()][:limit]
    if candidate.experience_years >= 5 and "Solid experience level" not in strengths:
        strengths.append("Solid experience level")
    if candidate.skill_coverage >= 60 and "Broad JD coverage" not in strengths:
        strengths.append("Broad JD coverage")
    return strengths[:limit]


def key_risks(candidate: CandidateResult, limit: int = 4) -> list:
    risks = [s for s in candidate.missing_skills if str(s).strip()][:limit]
    if candidate.experience_years <= 1 and len(risks) < limit:
        risks.append("Limited hands-on experience")
    if candidate.status == "Maybe" and len(risks) < limit:
        risks.append("Needs manager review for closer fit")
    return risks[:limit]


def candidate_contact_sheet(results: List[CandidateResult]) -> pd.DataFrame:
    rows = []
    for r in results:
        rows.append(
            {
                "Rank": r.rank,
                "Candidate": r.name or r.filename,
                "Status": r.status,
                "Priority": get_priority_label(r),
                "Recommended Action": recommended_action(r),
                "Email": safe_text(r.email),
                "Phone": safe_text(r.phone),
                "LinkedIn": safe_text(r.linkedin),
                "Experience (Years)": r.experience_years,
                "Education": titleize(r.education),
                "Match Score": f"{r.final_score:.0%}",
            }
        )
    return pd.DataFrame(rows)


def candidate_table(results: List[CandidateResult]) -> pd.DataFrame:
    rows = []
    for r in results:
        rows.append(
            {
                "Rank": r.rank,
                "Candidate": r.name or r.filename,
                "Status": r.status,
                "Priority": get_priority_label(r),
                "Action": recommended_action(r),
                "Interview Readiness": interview_readiness(r),
                "Match Score": f"{r.final_score:.0%}",
                "Experience": f"{r.experience_years} yrs",
                "Education": titleize(r.education),
                "Coverage": f"{r.skill_coverage}%",
                "Top Skills": ", ".join(r.all_skills_flat[:6]) if r.all_skills_flat else "N/A",
                "Main Gaps": ", ".join(r.missing_skills[:4]) if r.missing_skills else "None",
            }
        )
    return pd.DataFrame(rows)


with st.sidebar:
    st.markdown("## AI Resume Ranker")
    st.markdown("---")

    st.markdown("### Recruiter Controls")
    top_n = st.slider("Show top candidates", 5, 50, 12)
    filter_status = st.multiselect(
        "Filter by status",
        ["Shortlisted", "Maybe", "Not Relevant"],
        default=["Shortlisted", "Maybe", "Not Relevant"],
    )
    min_score = st.slider("Minimum match score", 0.0, 1.0, 0.0, 0.01)
    min_exp = st.slider("Minimum experience (years)", 0, 20, 0)

    st.markdown("---")
    st.markdown("### Recruiter Signals")
    st.markdown(f"- **Shortlisted**: score >= `{SHORTLIST_THRESHOLD}`")
    st.markdown(f"- **Maybe**: score >= `{MAYBE_THRESHOLD}`")
    st.markdown("- **Priority** blends score, coverage, and experience")
    st.markdown("- **Readiness** helps guide who can move first")

    st.markdown("---")
    st.markdown("### Designed For")
    st.markdown(
        """
        - Hiring demos
        - Recruiter-facing portfolio reviews
        - Faster shortlist discussions
        - Cleaner first-pass screening
        """
    )


st.markdown(
    """
    <div class="hero">
      <div class="hero-row">
        <div>
          <div class="eyebrow">Recruiter Intelligence Suite · Executive Screening View</div>
          <div class="hero-title">Turn raw resumes into a shortlist that feels client-ready.</div>
          <div class="hero-sub">
            A sharper front end for first-pass screening: upload resumes, rank them against the role,
            review recruiter signals, compare candidates side by side, and export a presentation-ready slate.
          </div>
        </div>
        <div class="hero-panel">
          <div class="hero-panel-title">Best for</div>
          <div class="hero-panel-value">Signal-rich screening</div>
          <div class="hero-panel-note">
            Preserve the ranking engine underneath, then layer on cleaner hierarchy, stronger recruiter framing,
            and decision support that makes the product feel more premium.
          </div>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)


tab_upload, tab_results, tab_brief, tab_analytics, tab_compare, tab_about = st.tabs(
    ["Upload & Rank", "Results", "Recruiter Brief", "Analytics", "Compare", "About"]
)


with tab_upload:
    st.markdown("## Role Setup")
    st.markdown(
        "<div class='muted-text'>For deployment, you can run the site directly from bundled sample resumes and a bundled job description so recruiters never have to upload files.</div>",
        unsafe_allow_html=True,
    )

    sample_dir = get_sample_resume_dir()
    has_sample_assets = sample_assets_available()

    source_col, info_col = st.columns([1.15, 1])
    with source_col:
        data_source = st.radio(
            "Resume source",
            ["Bundled sample resumes", "Upload my own resumes"],
            index=0 if st.session_state.get("data_source", "sample") == "sample" else 1,
            horizontal=True,
        )
        st.session_state["data_source"] = "sample" if data_source == "Bundled sample resumes" else "upload"

    with info_col:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        if has_sample_assets:
            sample_count = len(
                [
                    name for name in os.listdir(sample_dir)
                    if os.path.isfile(os.path.join(sample_dir, name))
                ]
            )
            st.markdown("**Bundled demo data detected**")
            st.markdown(f"- JD file: `sample_jd.txt`")
            st.markdown(f"- Resume folder: `{os.path.basename(sample_dir)}`")
            st.markdown(f"- Resume files found: `{sample_count}`")
        else:
            st.markdown("**Bundled demo data not found yet**")
            st.markdown("- Add `sample_jd.txt` to the project root")
            st.markdown("- Add a folder like `resume/` with your sample resumes")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("## Job Description")
    col_jd, col_ex = st.columns([3, 1])
    with col_jd:
        if st.session_state["data_source"] == "sample":
            jd_input_mode = "Bundled sample JD"
            st.radio("Input mode", ["Bundled sample JD"], horizontal=True, index=0, disabled=True)
        else:
            jd_input_mode = st.radio("Input mode", ["Type / Paste", "Upload .txt file"], horizontal=True)

    jd_text = ""
    with col_jd:
        if jd_input_mode == "Bundled sample JD":
            jd_text = load_sample_jd_text()
            st.text_area(
                "Job Description",
                value=jd_text if jd_text else "sample_jd.txt was not found in the app folder.",
                height=240,
                disabled=True,
                key="sample_jd_preview",
            )
        elif jd_input_mode == "Type / Paste":
            jd_text = st.text_area(
                "Job Description",
                height=240,
                placeholder="Paste the full job description here — role summary, must-have skills, responsibilities, and experience expectations...",
            )
        else:
            jd_file = st.file_uploader("Upload JD (.txt)", type=["txt"])
            if jd_file:
                jd_text = jd_file.read().decode("utf-8", errors="ignore")
                st.success(f"Loaded: {jd_file.name} ({len(jd_text.split())} words)")

    with col_ex:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        if st.session_state["data_source"] == "sample":
            st.markdown("**Bundled mode**")
            st.markdown("The app will rank the sample resumes shipped with the project.")
        elif st.button("Load Example JD", use_container_width=True):
            jd_text = """Senior Data Scientist – Python, Machine Learning, NLP

We are looking for an experienced Data Scientist with strong skills in Python,
machine learning, and natural language processing. The ideal candidate will have:

- 4+ years of experience with Python, pandas, numpy, scikit-learn
- Deep expertise in NLP, transformer models (BERT, GPT), and LLMs
- Proficiency in TensorFlow or PyTorch
- Experience with SQL, PostgreSQL, and cloud platforms (AWS / GCP)
- Strong knowledge of MLflow, Docker, and CI/CD pipelines
- Familiarity with FastAPI or Flask for model deployment
- Excellent communication and problem-solving skills

Education: B.Tech / M.Tech in CS, Data Science, or related field.
"""
            st.session_state["jd_text_override"] = jd_text
            st.rerun()
        st.markdown(
            "<div class='muted-text'>Bundled mode is ideal for deployed portfolio demos because reviewers can click once and see the shortlist immediately.</div>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.get("jd_text_override"):
        jd_text = st.session_state["jd_text_override"]
        st.text_area("Job Description (example loaded)", jd_text, height=240, key="jd_display")

    st.markdown("---")
    uploaded_files = []
    if st.session_state["data_source"] == "upload":
        st.markdown("---")
        st.markdown("## Resume Upload")

        uploaded_files = st.file_uploader(
            "Drop PDF / DOCX / TXT resume files here",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=True,
        )

        if uploaded_files:
            st.success(f"{len(uploaded_files)} file(s) uploaded")
            with st.expander("View uploaded files"):
                for item in uploaded_files:
                    st.write(f"• {item.name} ({item.size / 1024:.1f} KB)")
    else:
        st.markdown("---")
        st.markdown("## Sample Resume Set")
        if has_sample_assets:
            sample_files = sorted(
                [
                    name for name in os.listdir(sample_dir)
                    if os.path.isfile(os.path.join(sample_dir, name))
                ]
            )
            st.success(f"{len(sample_files)} bundled sample resume file(s) ready")
            with st.expander("View bundled sample files"):
                for name in sample_files:
                    st.write(f"• {name}")
        else:
            st.warning("Bundled sample assets are not available yet.")

    st.markdown("---")
    run_col, _ = st.columns([1, 3])
    with run_col:
        if st.session_state["data_source"] == "sample":
            run_btn = st.button("Run Sample Ranking", use_container_width=True)
        else:
            run_btn = st.button("Run Ranking", use_container_width=True)

    if run_btn:
        if st.session_state["data_source"] == "sample":
            if not has_sample_assets:
                st.error("Bundled sample assets were not found. Add `sample_jd.txt` and a `resume/` folder in the app root.")
            elif not jd_text.strip():
                st.error("`sample_jd.txt` is empty or unreadable.")
            else:
                run_ranking_pipeline(sample_dir, jd_text)
        else:
            if not jd_text.strip():
                st.error("Please enter a Job Description first.")
            elif not uploaded_files:
                st.error("Please upload at least one resume.")
            else:
                with tempfile.TemporaryDirectory() as tmpdir:
                    for uploaded in uploaded_files:
                        dest = os.path.join(tmpdir, uploaded.name)
                        with open(dest, "wb") as out:
                            out.write(uploaded.read())
                    run_ranking_pipeline(tmpdir, jd_text)


with tab_results:
    if not st.session_state.get("results"):
        st.info("Go to Upload & Rank to process resumes.")
    else:
        results: List[CandidateResult] = st.session_state["results"]
        summary = st.session_state["summary"] or {}
        jd_text_stored = st.session_state.get("jd_text", "")
        elapsed = st.session_state.get("elapsed", 0.0)

        filtered = [
            r for r in results
            if r.status in filter_status and r.final_score >= min_score and r.experience_years >= min_exp
        ][:top_n]

        shortlisted_count = sum(1 for r in filtered if r.status == "Shortlisted")
        maybe_count = sum(1 for r in filtered if r.status == "Maybe")
        high_priority = sum(1 for r in filtered if get_priority_label(r) == "High Priority")
        avg_score = sum(r.final_score for r in filtered) / len(filtered) if filtered else 0

        st.markdown(
            f"""
            <div class="ribbon-row">
              <div class="ribbon-card">
                <div class="ribbon-label">Candidates in View</div>
                <div class="ribbon-value">{len(filtered)}</div>
                <div class="ribbon-sub">Filtered shortlist window</div>
              </div>
              <div class="ribbon-card">
                <div class="ribbon-label">Shortlisted</div>
                <div class="ribbon-value">{shortlisted_count}</div>
                <div class="ribbon-sub">Profiles ready to prioritize</div>
              </div>
              <div class="ribbon-card">
                <div class="ribbon-label">High Priority</div>
                <div class="ribbon-value">{high_priority}</div>
                <div class="ribbon-sub">Strong fit across score, coverage, and experience</div>
              </div>
              <div class="ribbon-card">
                <div class="ribbon-label">Average Match</div>
                <div class="ribbon-value">{avg_score:.0%}</div>
                <div class="ribbon-sub">Across visible candidates</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        lead = filtered[0] if filtered else None
        lead_signal = (
            f"{lead.name or lead.filename} leads the current view with a {lead.final_score:.0%} match and "
            f"{lead.skill_coverage}% coverage."
            if lead else
            "Adjust your filters or rank resumes to generate a lead candidate signal."
        )
        pipeline_signal = (
            f"{shortlisted_count} candidates are recruiter-ready and {maybe_count} remain in the review band."
            if filtered else
            "Pipeline balance will appear here once ranked candidates are visible."
        )
        speed_signal = f"Batch processing time: {elapsed:.2f}s." if elapsed else "Processing speed appears after ranking."

        st.markdown(
            f"""
            <div class="signal-grid">
              <div class="signal-card emerald">
                <div class="signal-kicker">Lead Signal</div>
                <div class="signal-title">Who stands out first</div>
                <div class="signal-copy">{lead_signal}</div>
              </div>
              <div class="signal-card gold">
                <div class="signal-kicker">Pipeline Health</div>
                <div class="signal-title">How strong the slate looks</div>
                <div class="signal-copy">{pipeline_signal}</div>
              </div>
              <div class="signal-card coral">
                <div class="signal-kicker">Execution</div>
                <div class="signal-title">Decision speed</div>
                <div class="signal-copy">{speed_signal}</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("## Candidate Results")
        if not filtered:
            st.warning("No candidates match the current filters.")
        else:
            for r in filtered:
                matched_preview = skill_tags(r.all_skills_flat, limit=10) or "None detected"
                missing_preview = skill_tags(r.missing_skills, missing=True, limit=10) or "None"
                priority = get_priority_label(r)
                note_key = f"note_{r.filename}"
                decision_key = f"decision_{r.filename}"
                default_decision = st.session_state["recruiter_decisions"].get(r.filename, recommended_action(r))

                st.markdown(
                    f"""
                    <div class="candidate-card">
                      <div class="candidate-top">
                        <div style="flex:1;">
                          <div class="candidate-name">{safe_text(r.name) if safe_text(r.name) != "N/A" else r.filename}</div>
                          <div class="candidate-file">{r.filename}</div>
                          <div class="candidate-headline">{recruiter_summary(r)}</div>

                          <div class="chip-row">
                            {status_chip(r.status)}
                            {priority_chip(priority)}
                            <span class="soft-chip">Interview readiness: {interview_readiness(r)}</span>
                            <span class="soft-chip">Next step: {recommended_action(r)}</span>
                          </div>

                          {score_bar(r.final_score)}

                          <div class="metrics-grid">
                            <div class="metric-mini"><div class="label">Experience</div><div class="value">{r.experience_years} years</div></div>
                            <div class="metric-mini"><div class="label">Education</div><div class="value">{titleize(r.education)}</div></div>
                            <div class="metric-mini"><div class="label">Skill Coverage</div><div class="value">{r.skill_coverage}%</div></div>
                            <div class="metric-mini"><div class="label">Seniority</div><div class="value">{titleize(r.seniority)}</div></div>
                          </div>

                          <div class="section-title">Key matched skills</div>
                          <div>{matched_preview}</div>

                          <div class="section-title">Important missing skills</div>
                          <div>{missing_preview}</div>

                          <div class="priority-banner">
                            <strong>Recommended recruiter action: {recommended_action(r)}</strong>
                            <span>Priority: {priority} · Contact visibility: {"Complete" if r.email or r.phone or r.linkedin else "Limited"}</span>
                          </div>
                        </div>

                        <div class="rank-pill">
                          <span class="k">Rank</span>
                          <span class="v">#{r.rank}</span>
                        </div>
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                with st.expander(f"Open recruiter details for {r.filename}"):
                    d1, d2 = st.columns(2)

                    with d1:
                        st.markdown("**Contact**")
                        st.markdown(f"- Email: {safe_text(r.email)}")
                        st.markdown(f"- Phone: {safe_text(r.phone)}")
                        st.markdown(f"- LinkedIn: {safe_text(r.linkedin)}")
                        st.markdown(f"- GitHub: {safe_text(r.github)}")
                        st.markdown("**Top strengths**")
                        strengths = top_strengths(r)
                        for item in strengths or ["No standout strengths surfaced"]:
                            st.markdown(f"- {item}")

                    with d2:
                        st.markdown("**Decision support**")
                        st.markdown(f"- Match Score: {r.final_score:.0%}")
                        st.markdown(f"- Interview Readiness: {interview_readiness(r)}")
                        st.markdown(f"- Priority: {priority}")
                        st.markdown(f"- Suggested Action: {recommended_action(r)}")
                        st.markdown("**Risks / gaps**")
                        risks = key_risks(r)
                        for item in risks or ["No major risks surfaced"]:
                            st.markdown(f"- {item}")

                    if r.matched_skills:
                        st.markdown("**Matched skills by area**")
                        for group, skills in r.matched_skills.items():
                            clean = [item for item in skills if str(item).strip()]
                            if clean:
                                st.markdown(f"- **{group}:** {', '.join(clean)}")

                    decision_value = st.selectbox(
                        "Recruiter decision",
                        RECRUITER_DECISIONS,
                        index=RECRUITER_DECISIONS.index(default_decision) if default_decision in RECRUITER_DECISIONS else 0,
                        key=decision_key,
                    )
                    st.session_state["recruiter_decisions"][r.filename] = decision_value

                    note_value = st.text_area(
                        "Recruiter notes",
                        value=st.session_state["recruiter_notes"].get(r.filename, ""),
                        placeholder="Add interview notes, talking points, concerns, or follow-up guidance...",
                        height=120,
                        key=note_key,
                    )
                    st.session_state["recruiter_notes"][r.filename] = note_value

        st.markdown("---")
        st.markdown("## Export Results")
        ec1, ec2, ec3 = st.columns(3)

        with tempfile.TemporaryDirectory() as tdir:
            csv_path = export_csv(results, os.path.join(tdir, "ranked_resumes.csv"))
            json_path = export_json(results, summary, os.path.join(tdir, "ranking_results.json"))
            txt_path = export_txt_report(results, summary, jd_text_stored, os.path.join(tdir, "ranking_report.txt"))

            with open(csv_path, "rb") as handle:
                csv_bytes = handle.read()
            with open(json_path, "rb") as handle:
                json_bytes = handle.read()
            with open(txt_path, "rb") as handle:
                txt_bytes = handle.read()

        with ec1:
            _dl_button("Download CSV", csv_bytes, "ranked_resumes.csv", "text/csv")
        with ec2:
            _dl_button("Download JSON", json_bytes, "ranking_results.json", "application/json")
        with ec3:
            _dl_button("Download Report", txt_bytes, "ranking_report.txt", "text/plain")


with tab_brief:
    if not st.session_state.get("results"):
        st.info("Run the ranking first to generate the recruiter brief.")
    else:
        results: List[CandidateResult] = st.session_state["results"]
        shortlist = [r for r in results if r.status == "Shortlisted"]
        maybes = [r for r in results if r.status == "Maybe"]
        lead = results[0] if results else None

        st.markdown("## Recruiter Brief")
        st.markdown(
            "<div class='muted-text'>A presentation-ready hiring summary built from the ranked slate.</div>",
            unsafe_allow_html=True,
        )

        top_names = ", ".join([(r.name or r.filename) for r in results[:3]]) if results else "N/A"
        lead_line = (
            f"Top recommendation: {lead.name or lead.filename} at {lead.final_score:.0%} match."
            if lead else "No lead candidate yet."
        )
        shortlist_line = f"{len(shortlist)} candidate(s) are currently shortlisted and {len(maybes)} are in the review band."
        risk_count = sum(1 for r in results[:5] if len(r.missing_skills) >= 5)
        risk_line = f"{risk_count} of the top 5 profiles show notable capability gaps that should be probed in screening."

        st.markdown(
            f"""
            <div class="signal-grid">
              <div class="signal-card emerald">
                <div class="signal-kicker">Executive Summary</div>
                <div class="signal-title">Top slate snapshot</div>
                <div class="signal-copy">{lead_line}<br><br>Top visible names: {top_names}</div>
              </div>
              <div class="signal-card gold">
                <div class="signal-kicker">Pipeline Quality</div>
                <div class="signal-title">Who can move now</div>
                <div class="signal-copy">{shortlist_line}</div>
              </div>
              <div class="signal-card coral">
                <div class="signal-kicker">Attention Area</div>
                <div class="signal-title">What needs probing</div>
                <div class="signal-copy">{risk_line}</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        for idx, candidate in enumerate(results[:3], start=1):
            st.markdown(
                f"""
                <div class="section-card" style="margin-bottom:1rem;">
                  <div class="section-title">Top {idx} candidate spotlight</div>
                  <h3 style="margin:0.1rem 0 0.6rem 0;">{candidate.name or candidate.filename}</h3>
                  <div class="muted-text">{recruiter_summary(candidate)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            c1, c2, c3 = st.columns(3)
            c1.metric("Match Score", f"{candidate.final_score:.0%}")
            c2.metric("Experience", f"{candidate.experience_years} yrs")
            c3.metric("Coverage", f"{candidate.skill_coverage}%")

            left, right = st.columns(2)
            with left:
                st.markdown("**What stands out**")
                for item in top_strengths(candidate, limit=5):
                    st.markdown(f"- {item}")
            with right:
                st.markdown("**What to validate in screening**")
                for item in key_risks(candidate, limit=5):
                    st.markdown(f"- {item}")

        st.markdown("---")
        st.markdown("## Recruiter Contact Sheet")
        sheet_df = candidate_contact_sheet(results)
        st.markdown('<div class="table-card">', unsafe_allow_html=True)
        st.dataframe(sheet_df, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        log_rows = []
        for candidate in results[:10]:
            log_rows.append(
                {
                    "Rank": candidate.rank,
                    "Candidate": candidate.name or candidate.filename,
                    "Status": candidate.status,
                    "Priority": get_priority_label(candidate),
                    "Action": st.session_state["recruiter_decisions"].get(candidate.filename, recommended_action(candidate)),
                    "Notes": st.session_state["recruiter_notes"].get(candidate.filename, ""),
                }
            )
        log_df = pd.DataFrame(log_rows)
        st.markdown("## Recruiter Decision Log")
        st.markdown('<div class="table-card">', unsafe_allow_html=True)
        st.dataframe(log_df, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)


with tab_analytics:
    if not st.session_state.get("results"):
        st.info("Run the ranking first.")
    else:
        results: List[CandidateResult] = st.session_state["results"]

        st.markdown("## Hiring Analytics")

        df = pd.DataFrame(
            [
                {
                    "Candidate": r.filename,
                    "Name": r.name or r.filename,
                    "Score": r.final_score,
                    "Status": r.status,
                    "Seniority": r.seniority,
                    "Education": titleize(r.education),
                    "Experience": r.experience_years,
                    "Coverage %": r.skill_coverage,
                    "Skills Count": len(r.all_skills_flat),
                    "Priority": get_priority_label(r),
                }
                for r in results
            ]
        )
        candidate_palette = build_candidate_palette(df["Name"].tolist())

        c1, c2 = st.columns(2)
        with c1:
            fig1 = px.bar(
                df.head(15),
                x="Score",
                y="Name",
                orientation="h",
                color="Name",
                color_discrete_map=candidate_palette,
                title="Top Candidate Match Scores",
                template="simple_white",
            )
            fig1.update_layout(
                plot_bgcolor="rgba(255,255,255,0)",
                paper_bgcolor="rgba(255,255,255,0)",
                font_family="DM Sans",
                yaxis=dict(autorange="reversed"),
                title_font=dict(family="Fraunces", size=20),
                xaxis_tickformat=".0%",
                legend_title_text="",
            )
            st.plotly_chart(fig1, use_container_width=True)

        with c2:
            status_counts = df["Status"].value_counts().reset_index()
            status_counts.columns = ["Status", "Count"]
            fig2 = px.pie(
                status_counts,
                values="Count",
                names="Status",
                color="Status",
                color_discrete_map={
                    "Shortlisted": "#0f766e",
                    "Maybe": "#bc862f",
                    "Not Relevant": "#b6554d",
                },
                title="Status Distribution",
                hole=0.58,
                template="simple_white",
            )
            fig2.update_layout(
                plot_bgcolor="rgba(255,255,255,0)",
                paper_bgcolor="rgba(255,255,255,0)",
                font_family="DM Sans",
                title_font=dict(family="Fraunces", size=20),
                legend_title_text="",
            )
            st.plotly_chart(fig2, use_container_width=True)

        c3, c4 = st.columns(2)
        with c3:
            fig3 = px.scatter(
                df,
                x="Experience",
                y="Score",
                color="Name",
                size="Coverage %",
                hover_name="Name",
                color_discrete_map=candidate_palette,
                title="Experience vs Match Score",
                template="simple_white",
            )
            fig3.update_layout(
                plot_bgcolor="rgba(255,255,255,0)",
                paper_bgcolor="rgba(255,255,255,0)",
                font_family="DM Sans",
                title_font=dict(family="Fraunces", size=20),
                yaxis_tickformat=".0%",
                legend_title_text="",
            )
            st.plotly_chart(fig3, use_container_width=True)

        with c4:
            fig4 = px.histogram(
                df,
                x="Coverage %",
                nbins=10,
                title="Skill Coverage Distribution",
                template="simple_white",
                color_discrete_sequence=["#183b60"],
            )
            fig4.update_layout(
                plot_bgcolor="rgba(255,255,255,0)",
                paper_bgcolor="rgba(255,255,255,0)",
                font_family="DM Sans",
                title_font=dict(family="Fraunces", size=20),
            )
            st.plotly_chart(fig4, use_container_width=True)

        st.markdown("### Most Common Skills Across Resumes")
        counter = Counter()
        for result in results:
            for skill in result.all_skills_flat:
                counter[skill] += 1

        if counter:
            skill_df = pd.DataFrame(counter.most_common(20), columns=["Skill", "Count"])
            fig5 = px.bar(
                skill_df,
                x="Count",
                y="Skill",
                orientation="h",
                title="Top 20 Skills Found",
                template="simple_white",
                color="Count",
                color_continuous_scale=["#e4edf7", "#183b60"],
            )
            fig5.update_layout(
                plot_bgcolor="rgba(255,255,255,0)",
                paper_bgcolor="rgba(255,255,255,0)",
                font_family="DM Sans",
                title_font=dict(family="Fraunces", size=20),
                yaxis=dict(autorange="reversed"),
                coloraxis_showscale=False,
            )
            st.plotly_chart(fig5, use_container_width=True)

        st.markdown("### Candidate Summary Table")
        st.markdown('<div class="table-card">', unsafe_allow_html=True)
        st.dataframe(candidate_table(results), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)


with tab_compare:
    if not st.session_state.get("results"):
        st.info("Run the ranking first.")
    else:
        results: List[CandidateResult] = st.session_state["results"]
        st.markdown("## Candidate Comparison")

        names = [r.filename for r in results]
        sel_a = st.selectbox("Candidate A", names, index=0)
        sel_b = st.selectbox("Candidate B", names, index=min(1, len(names) - 1))

        candidate_a = next(r for r in results if r.filename == sel_a)
        candidate_b = next(r for r in results if r.filename == sel_b)

        def show_candidate_panel(column, candidate: CandidateResult):
            with column:
                st.markdown('<div class="section-card">', unsafe_allow_html=True)
                st.markdown(f"### {candidate.name or candidate.filename}")
                st.markdown(f"**Status:** {candidate.status}")
                st.metric("Match Score", f"{candidate.final_score:.0%}")
                st.metric("Experience", f"{candidate.experience_years} yrs")
                st.metric("Skill Coverage", f"{candidate.skill_coverage}%")
                st.markdown(f"**Education:** {titleize(candidate.education)}")
                st.markdown(f"**Seniority:** {titleize(candidate.seniority)}")
                st.markdown(f"**Priority:** {get_priority_label(candidate)}")
                st.markdown(f"**Action:** {recommended_action(candidate)}")
                st.markdown(f"**Email:** {safe_text(candidate.email)}")
                st.markdown(f"**Phone:** {safe_text(candidate.phone)}")
                st.markdown(f"**LinkedIn:** {safe_text(candidate.linkedin)}")
                st.markdown("</div>", unsafe_allow_html=True)

        col_a, col_b = st.columns(2)
        show_candidate_panel(col_a, candidate_a)
        show_candidate_panel(col_b, candidate_b)

        categories = ["Match Score", "Skill Coverage", "Experience (norm)"]

        def norm_exp(value):
            return min(value / 15, 1.0)

        fig_radar = go.Figure()
        for candidate, color in [(candidate_a, "#0f766e"), (candidate_b, "#bc862f")]:
            vals = [candidate.final_score, candidate.skill_coverage / 100, norm_exp(candidate.experience_years)]
            fig_radar.add_trace(
                go.Scatterpolar(
                    r=vals + [vals[0]],
                    theta=categories + [categories[0]],
                    fill="toself",
                    name=candidate.name or candidate.filename,
                    line_color=color,
                    fillcolor=hex_to_rgba(color, 0.18),
                )
            )

        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1]), bgcolor="rgba(255,255,255,0)"),
            showlegend=True,
            template="simple_white",
            paper_bgcolor="rgba(255,255,255,0)",
            title="Candidate Comparison Radar",
            title_font=dict(family="Fraunces", size=22),
            font=dict(family="DM Sans"),
        )
        st.plotly_chart(fig_radar, use_container_width=True)

        set_a = set(candidate_a.all_skills_flat)
        set_b = set(candidate_b.all_skills_flat)
        shared = set_a & set_b
        only_a = set_a - set_b
        only_b = set_b - set_a

        s1, s2, s3 = st.columns(3)
        with s1:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown(f"**Only in {candidate_a.name or candidate_a.filename}**")
            for item in sorted(only_a)[:20]:
                st.markdown(f"- {item}")
            st.markdown("</div>", unsafe_allow_html=True)
        with s2:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("**Shared Skills**")
            for item in sorted(shared)[:20]:
                st.markdown(f"- {item}")
            st.markdown("</div>", unsafe_allow_html=True)
        with s3:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown(f"**Only in {candidate_b.name or candidate_b.filename}**")
            for item in sorted(only_b)[:20]:
                st.markdown(f"- {item}")
            st.markdown("</div>", unsafe_allow_html=True)


with tab_about:
    st.markdown(
        """
        ## About AI Resume Ranker

        This version keeps your ranking workflow intact while upgrading the interface into something that feels more recruiter-facing and presentation-ready.

        What changed:
        - Stronger visual hierarchy with a warmer executive editorial style
        - Cleaner candidate cards with clearer recruiter cues
        - Better framing for shortlist, priority, readiness, and next steps
        - A sharper recruiter brief for top-slate storytelling
        - More polished analytics and comparison surfaces
        - Decision logging that fits portfolio and demo use

        Best use:
        Run ranking in front of a recruiter, interviewer, or reviewer and walk them from upload through shortlist and recommendation without the UI feeling like a rough technical prototype.
        """
    )
