# ============================================================
#   app.py  –  Streamlit Web App  |  AI Resume Ranker v3.0
#   Run:  streamlit run app.py
# ============================================================

import os
import sys
import tempfile
import time
import base64
from collections import Counter
from typing import List

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# local modules
sys.path.insert(0, os.path.dirname(__file__))
from config import APP_VERSION, SHORTLIST_THRESHOLD, MAYBE_THRESHOLD
from utils.ranker import rank_resumes, compute_summary, CandidateResult
from utils.exporter import export_csv, export_json, export_txt_report


# ── Page config ───────────────────────────────────────────────
st.set_page_config(
    page_title="AI Resume Ranker",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Session state ─────────────────────────────────────────────
if "recruiter_notes" not in st.session_state:
    st.session_state["recruiter_notes"] = {}

if "recruiter_decisions" not in st.session_state:
    st.session_state["recruiter_decisions"] = {}

if "jd_text_override" not in st.session_state:
    st.session_state["jd_text_override"] = ""


# ── Custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
    --bg: #f7f3ec;
    --surface: #fffdf8;
    --surface-2: #f2ebe0;
    --ink: #17221f;
    --muted: #6f756c;
    --line: rgba(23, 34, 31, 0.08);
    --teal: #0f766e;
    --teal-soft: #d9f2ee;
    --gold: #c48a2c;
    --gold-soft: #f9edd7;
    --coral: #b94f37;
    --coral-soft: #f7dfda;
    --olive: #5d6c3f;
    --olive-soft: #e7edd8;
    --navy: #1e334d;
    --navy-soft: #dfe7f1;
    --shadow: 0 18px 60px rgba(31, 37, 34, 0.08);
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(196,138,44,0.12), transparent 28%),
        radial-gradient(circle at top right, rgba(15,118,110,0.10), transparent 24%),
        linear-gradient(180deg, #f8f5ef 0%, #f4efe6 48%, #f8f4ee 100%);
    color: var(--ink);
}

html, body, [class*="css"] {
    font-family: 'Manrope', sans-serif;
    color: var(--ink);
}

h1, h2, h3, h4, .display-serif {
    font-family: 'Instrument Serif', serif !important;
    letter-spacing: 0.2px;
    color: var(--ink);
}

section.main > div {
    padding-top: 1.1rem;
}

.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
    max-width: 1360px;
}

.hero-shell {
    position: relative;
    overflow: hidden;
    background:
        linear-gradient(135deg, rgba(255,253,248,0.95), rgba(247,243,236,0.92)),
        linear-gradient(120deg, #fff9ef, #f1f4ec);
    border: 1px solid rgba(23, 34, 31, 0.08);
    border-radius: 28px;
    padding: 2.5rem 2.4rem 2rem 2.4rem;
    box-shadow: var(--shadow);
    margin-bottom: 1.25rem;
}
.hero-shell::before {
    content: "";
    position: absolute;
    width: 420px;
    height: 420px;
    right: -120px;
    top: -160px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(15,118,110,0.16), transparent 60%);
}
.hero-shell::after {
    content: "";
    position: absolute;
    width: 360px;
    height: 360px;
    left: -120px;
    bottom: -200px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(196,138,44,0.18), transparent 62%);
}
.hero-row {
    position: relative;
    z-index: 2;
    display: flex;
    gap: 2rem;
    justify-content: space-between;
    align-items: flex-start;
    flex-wrap: wrap;
}
.hero-copy {
    max-width: 760px;
}
.hero-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 0.42rem 0.8rem;
    border-radius: 999px;
    background: rgba(15,118,110,0.08);
    color: var(--teal);
    font-weight: 700;
    font-size: 0.8rem;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}
.hero-title {
    margin: 0.9rem 0 0 0;
    font-size: 3.7rem;
    line-height: 0.94;
    max-width: 760px;
}
.hero-sub {
    margin-top: 0.9rem;
    font-size: 1.02rem;
    color: var(--muted);
    max-width: 680px;
    line-height: 1.7;
}
.hero-panel {
    min-width: 260px;
    background: rgba(255,255,255,0.72);
    border: 1px solid rgba(23,34,31,0.08);
    border-radius: 20px;
    padding: 1rem 1rem 0.9rem 1rem;
    box-shadow: 0 10px 30px rgba(31,37,34,0.05);
}
.hero-panel-title {
    font-size: 0.76rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--muted);
    font-weight: 800;
}
.hero-panel-value {
    font-size: 1.8rem;
    font-weight: 800;
    color: var(--ink);
    margin-top: 0.25rem;
}
.hero-panel-note {
    color: var(--muted);
    font-size: 0.88rem;
    line-height: 1.5;
}

.ribbon-row {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 1rem;
    margin: 1rem 0 1.6rem 0;
}
.ribbon-card {
    background: rgba(255,255,255,0.74);
    border: 1px solid rgba(23,34,31,0.08);
    border-radius: 18px;
    padding: 1rem 1rem 0.9rem 1rem;
    box-shadow: 0 8px 24px rgba(31,37,34,0.04);
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
    font-size: 1.55rem;
    font-weight: 800;
    color: var(--ink);
}
.ribbon-sub {
    margin-top: 0.2rem;
    color: var(--muted);
    font-size: 0.86rem;
}

.signal-board {
    display: grid;
    grid-template-columns: 1.2fr 1fr 1fr;
    gap: 1rem;
    margin: 0.8rem 0 1.7rem 0;
}
.signal-card {
    border-radius: 22px;
    padding: 1.15rem 1.15rem 1rem 1.15rem;
    box-shadow: var(--shadow);
    border: 1px solid rgba(23,34,31,0.08);
    min-height: 142px;
}
.signal-card.teal {
    background: linear-gradient(180deg, #f8fffd, #eaf8f5);
}
.signal-card.gold {
    background: linear-gradient(180deg, #fffaf3, #f9edd7);
}
.signal-card.coral {
    background: linear-gradient(180deg, #fff8f6, #f7dfda);
}
.signal-kicker {
    font-size: 0.74rem;
    text-transform: uppercase;
    font-weight: 800;
    letter-spacing: 0.08em;
    color: rgba(23,34,31,0.64);
}
.signal-title {
    font-size: 1.4rem;
    font-weight: 800;
    margin-top: 0.4rem;
    color: var(--ink);
}
.signal-copy {
    margin-top: 0.4rem;
    font-size: 0.92rem;
    line-height: 1.6;
    color: rgba(23,34,31,0.74);
}

.section-card {
    background: rgba(255,255,255,0.8);
    border: 1px solid rgba(23,34,31,0.08);
    border-radius: 24px;
    padding: 1.15rem 1.15rem 1.2rem 1.15rem;
    box-shadow: var(--shadow);
}

.candidate-card {
    position: relative;
    overflow: hidden;
    background:
        linear-gradient(180deg, rgba(255,255,255,0.95), rgba(252,249,243,0.95));
    border: 1px solid rgba(23,34,31,0.08);
    border-radius: 26px;
    padding: 1.2rem 1.25rem 1.15rem 1.25rem;
    margin-bottom: 1rem;
    box-shadow: var(--shadow);
}
.candidate-card::before {
    content: "";
    position: absolute;
    inset: 0 auto 0 0;
    width: 6px;
    background: linear-gradient(180deg, #0f766e, #c48a2c);
}
.candidate-top {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    align-items: flex-start;
}
.rank-pill {
    min-width: 70px;
    text-align: center;
    background: #17221f;
    color: #fffdf8;
    border-radius: 18px;
    padding: 0.65rem 0.8rem;
}
.rank-pill .rk {
    display: block;
    font-size: 0.72rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    opacity: 0.75;
}
.rank-pill .rv {
    display: block;
    font-size: 1.25rem;
    font-weight: 800;
    margin-top: 0.15rem;
}
.candidate-name {
    font-size: 1.45rem;
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
    margin-top: 0.6rem;
    color: rgba(23,34,31,0.80);
    font-size: 0.95rem;
    line-height: 1.65;
}
.chip-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.45rem;
    margin: 0.8rem 0 0.7rem 0;
}
.soft-chip, .priority-chip, .status-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    border-radius: 999px;
    padding: 0.42rem 0.8rem;
    font-size: 0.78rem;
    font-weight: 700;
    border: 1px solid transparent;
}
.status-shortlisted {
    background: #dff6ed;
    color: #0d7b58;
    border-color: #b8e9d6;
}
.status-maybe {
    background: #fff2db;
    color: #9a6612;
    border-color: #f0d6a4;
}
.status-not {
    background: #fde6e1;
    color: #a04532;
    border-color: #efc0b5;
}
.priority-high {
    background: #e6f7f2;
    color: #0f766e;
}
.priority-medium {
    background: #fff2db;
    color: #9a6612;
}
.priority-low {
    background: #f3e7e3;
    color: #8f5347;
}
.soft-chip {
    background: #eef1f4;
    color: #32424d;
    border-color: rgba(50,66,77,0.10);
}
.metrics-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 0.8rem;
    margin-top: 0.9rem;
}
.metric-mini {
    background: rgba(247,243,236,0.9);
    border: 1px solid rgba(23,34,31,0.06);
    border-radius: 18px;
    padding: 0.8rem 0.8rem 0.75rem 0.8rem;
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
    font-size: 1.1rem;
    font-weight: 800;
    color: var(--ink);
}
.score-track {
    margin-top: 0.8rem;
    height: 10px;
    background: #ece6db;
    border-radius: 999px;
    overflow: hidden;
}
.score-fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #0f766e 0%, #c48a2c 100%);
}
.score-note {
    margin-top: 0.38rem;
    font-size: 0.84rem;
    color: var(--muted);
}
.skill-section {
    margin-top: 0.95rem;
}
.section-title {
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--muted);
    font-weight: 800;
    margin-bottom: 0.45rem;
}
.skill-tag {
    display: inline-block;
    background: #e3f3ef;
    border: 1px solid #c6e5de;
    color: #0f5f59;
    border-radius: 999px;
    padding: 0.3rem 0.72rem;
    font-size: 0.76rem;
    margin: 0.18rem;
    font-weight: 600;
}
.missing-tag {
    display: inline-block;
    background: #f8e8e3;
    border: 1px solid #ebc8bf;
    color: #9f4735;
    border-radius: 999px;
    padding: 0.3rem 0.72rem;
    font-size: 0.76rem;
    margin: 0.18rem;
    font-weight: 600;
}

.priority-banner {
    background: linear-gradient(90deg, #17221f, #2c403b);
    color: #fffdf8;
    border-radius: 18px;
    padding: 0.9rem 1rem;
    margin-top: 0.95rem;
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    align-items: center;
    flex-wrap: wrap;
}
.priority-banner strong {
    color: #fff;
}
.priority-banner span {
    color: rgba(255,255,255,0.8);
    font-size: 0.9rem;
}

.note-box {
    background: #fffdf8;
    border: 1px solid rgba(23,34,31,0.08);
    border-radius: 18px;
    padding: 0.9rem;
}

.table-card {
    background: rgba(255,255,255,0.82);
    border: 1px solid rgba(23,34,31,0.08);
    border-radius: 22px;
    padding: 1rem;
    box-shadow: var(--shadow);
}

[data-testid="stSidebar"] {
    background:
        radial-gradient(circle at top right, rgba(196,138,44,0.18), transparent 26%),
        linear-gradient(180deg, #16211f 0%, #23312d 60%, #2d3d38 100%);
}
[data-testid="stSidebar"] * {
    color: #f7f3ec !important;
}
[data-testid="stSidebar"] .stSlider [data-baseweb="thumb"] {
    background: #f5d38c !important;
}
[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] {
    background: rgba(255,255,255,0.14) !important;
    border-radius: 999px !important;
}

.stButton > button {
    border-radius: 14px;
    border: 1px solid rgba(23,34,31,0.08);
    background: linear-gradient(135deg, #17221f, #355047);
    color: #fffdf8;
    font-weight: 800;
    padding: 0.66rem 1.2rem;
    box-shadow: 0 12px 30px rgba(23,34,31,0.10);
}
.stButton > button:hover {
    transform: translateY(-1px);
    border-color: rgba(23,34,31,0.18);
}

.stDownloadButton > button {
    border-radius: 14px;
    border: 1px solid rgba(23,34,31,0.08);
    background: linear-gradient(135deg, #0f766e, #1c958a);
    color: white;
    font-weight: 800;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 0.45rem;
}
.stTabs [data-baseweb="tab"] {
    background: rgba(255,255,255,0.72);
    border: 1px solid rgba(23,34,31,0.08);
    border-radius: 14px;
    padding: 0.5rem 0.9rem;
    font-family: 'Manrope', sans-serif;
    font-weight: 800;
    color: var(--ink);
}
.stTabs [aria-selected="true"] {
    background: #17221f !important;
    color: #fffdf8 !important;
}

div[data-testid="stExpander"] {
    border: 1px solid rgba(23,34,31,0.08);
    border-radius: 18px;
    background: rgba(255,255,255,0.7);
    overflow: hidden;
}
div[data-testid="stExpander"] details summary {
    padding: 0.2rem 0.3rem;
}

.stTextArea textarea,
.stTextInput input,
.stSelectbox div[data-baseweb="select"],
.stMultiSelect div[data-baseweb="select"] {
    border-radius: 14px !important;
}

hr {
    border-color: rgba(23,34,31,0.08) !important;
}

.small-muted {
    color: var(--muted);
    font-size: 0.88rem;
}

@media (max-width: 1100px) {
    .ribbon-row, .metrics-grid, .signal-board {
        grid-template-columns: 1fr 1fr;
    }
}

@media (max-width: 760px) {
    .hero-title {
        font-size: 2.65rem;
    }
    .ribbon-row, .metrics-grid, .signal-board {
        grid-template-columns: 1fr;
    }
    .candidate-top {
        flex-direction: column;
    }
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────

def status_chip(status: str) -> str:
    if status == "Shortlisted":
        return '<span class="status-chip status-shortlisted">Shortlisted</span>'
    if status == "Maybe":
        return '<span class="status-chip status-maybe">Maybe</span>'
    return '<span class="status-chip status-not">Not Relevant</span>'


def score_bar(score: float) -> str:
    pct = max(0, min(int(score * 100), 100))
    return f"""
    <div class="score-track">
        <div class="score-fill" style="width:{pct}%;"></div>
    </div>
    <div class="score-note">Overall match score: <strong>{pct}%</strong></div>
    """


def skill_tags(skills: list, missing: bool = False, limit: int = 12) -> str:
    cls = "missing-tag" if missing else "skill-tag"
    clean = [str(s).strip() for s in skills if str(s).strip()]
    shown = clean[:limit]
    return " ".join(f'<span class="{cls}">{s}</span>' for s in shown)


def safe_text(value) -> str:
    if value is None:
        return "N/A"
    value = str(value).strip()
    return value if value else "N/A"


def titleize(value) -> str:
    text = safe_text(value)
    return text.title() if text != "N/A" else text


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
        f'<button style="background:linear-gradient(135deg,#0f766e,#1c958a);color:white;'
        f'border:none;border-radius:14px;font-family:Manrope,sans-serif;font-weight:800;'
        f'padding:0.7rem 1.15rem;cursor:pointer;margin:4px;">{label}</button></a>'
    )
    st.markdown(href, unsafe_allow_html=True)


def get_priority_label(candidate: CandidateResult) -> str:
    score = candidate.final_score
    coverage = candidate.skill_coverage
    exp = candidate.experience_years

    if score >= 0.82 and coverage >= 65 and exp >= 4:
        return "High Priority"
    if score >= 0.62 and coverage >= 45:
        return "Strong Review"
    if score >= 0.45:
        return "Hold for Review"
    return "Low Priority"


def priority_chip(priority: str) -> str:
    mapping = {
        "High Priority": "priority-high",
        "Strong Review": "priority-medium",
        "Hold for Review": "priority-medium",
        "Low Priority": "priority-low",
    }
    cls = mapping.get(priority, "priority-low")
    return f'<span class="priority-chip {cls}">{priority}</span>'


def recommended_action(candidate: CandidateResult) -> str:
    if candidate.status == "Shortlisted" and candidate.final_score >= 0.8:
        return "Move to recruiter screen"
    if candidate.status == "Shortlisted":
        return "Send to hiring manager"
    if candidate.status == "Maybe":
        return "Keep in backup pipeline"
    return "Archive for now"


def recruiter_summary(candidate: CandidateResult) -> str:
    match_score = int(candidate.final_score * 100)
    exp = candidate.experience_years
    coverage = candidate.skill_coverage

    if candidate.status == "Shortlisted":
        return (
            f"This profile looks interview-worthy with a {match_score}% match score, "
            f"{exp} years of experience, and {coverage}% skill coverage."
        )
    if candidate.status == "Maybe":
        return (
            f"This candidate has some alignment at {match_score}% match, but will need a closer look "
            f"around gaps and role fit before advancing."
        )
    return (
        f"This profile currently shows limited fit at {match_score}% match. "
        f"It may be better suited for a different role or future opening."
    )


def top_strengths(candidate: CandidateResult, limit: int = 4) -> list:
    skills = [s for s in candidate.all_skills_flat if str(s).strip()]
    strengths = skills[:limit]
    if candidate.experience_years >= 5:
        strengths.append("Solid experience level")
    if candidate.skill_coverage >= 60:
        strengths.append("Broad JD coverage")
    seen = []
    for item in strengths:
        if item not in seen:
            seen.append(item)
    return seen[:limit]


def key_risks(candidate: CandidateResult, limit: int = 4) -> list:
    risks = [s for s in candidate.missing_skills if str(s).strip()][:limit]
    if candidate.experience_years <= 1:
        risks.append("Limited hands-on experience")
    if candidate.status == "Maybe" and len(risks) < limit:
        risks.append("Needs manager review for closer fit")
    seen = []
    for item in risks:
        if item not in seen:
            seen.append(item)
    return seen[:limit]


def interview_readiness(candidate: CandidateResult) -> str:
    if candidate.status == "Shortlisted" and candidate.final_score >= 0.75:
        return "Ready now"
    if candidate.status == "Maybe":
        return "Needs closer review"
    return "Not recommended yet"


def candidate_contact_sheet(results: List[CandidateResult]) -> pd.DataFrame:
    rows = []
    for r in results:
        rows.append({
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
        })
    return pd.DataFrame(rows)


def candidate_table(results: List[CandidateResult]) -> pd.DataFrame:
    rows = []
    for r in results:
        rows.append({
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
        })
    return pd.DataFrame(rows)


# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## AI Resume Ranker")
    st.markdown(f"**Version {APP_VERSION}**")
    st.markdown("---")

    st.markdown("### Recruiter Controls")
    top_n = st.slider("Show top candidates", 5, 50, 10)
    filter_status = st.multiselect(
        "Filter by status",
        ["Shortlisted", "Maybe", "Not Relevant"],
        default=["Shortlisted", "Maybe", "Not Relevant"]
    )
    min_score = st.slider("Minimum match score", 0.0, 1.0, 0.0, 0.01)
    min_exp = st.slider("Minimum experience (years)", 0, 20, 0)

    st.markdown("---")
    st.markdown("### Recruiter Signals")
    st.markdown(f"- **Shortlisted**: score ≥ `{SHORTLIST_THRESHOLD}`")
    st.markdown(f"- **Maybe**: score ≥ `{MAYBE_THRESHOLD}`")
    st.markdown("- **Priority** blends score, skill coverage, and experience")
    st.markdown("- **Action** suggests the next recruiter move")

    st.markdown("---")
    st.markdown("### What This Version Adds")
    st.markdown("""
- Recruiter brief
- Priority labels
- Recommended next actions
- Contact sheet
- Save-notes workflow
- Stronger executive-style design
""")


# ── Hero ──────────────────────────────────────────────────────
st.markdown("""
<div class="hero-shell">
  <div class="hero-row">
    <div class="hero-copy">
      <div class="hero-eyebrow">Recruiter Studio · Candidate Intelligence</div>
      <div class="hero-title">Screen sharper. Shortlist faster. Present candidates with confidence.</div>
      <div class="hero-sub">
        A polished hiring dashboard for turning raw resumes into recruiter-ready decisions,
        complete with match signals, contact visibility, interview readiness, and decision support.
      </div>
    </div>
    <div class="hero-panel">
      <div class="hero-panel-title">Designed for first-pass hiring decisions</div>
      <div class="hero-panel-value">Signal over noise</div>
      <div class="hero-panel-note">
        Keep the ranking logic you already trust, then layer on presentation, recruiter notes,
        and decision guidance that feels client-ready.
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ── Tabs ──────────────────────────────────────────────────────
tab_upload, tab_results, tab_brief, tab_analytics, tab_compare, tab_about = st.tabs([
    "Upload & Rank",
    "Results",
    "Recruiter Brief",
    "Analytics",
    "Compare",
    "About"
])


# ══════════════════════════
#  TAB 1 – UPLOAD & RANK
# ══════════════════════════
with tab_upload:
    st.markdown("## Job Description")
    st.markdown("<div class='small-muted'>Paste the role brief or upload a `.txt` description to start ranking resumes.</div>", unsafe_allow_html=True)

    col_jd, col_ex = st.columns([3, 1])
    with col_jd:
        jd_input_mode = st.radio("Input mode", ["Type / Paste", "Upload .txt file"], horizontal=True)

    jd_text = ""
    with col_jd:
        if jd_input_mode == "Type / Paste":
            jd_text = st.text_area(
                "Job Description",
                height=240,
                placeholder="Paste the full job description here — role summary, requirements, must-have skills, and experience..."
            )
        else:
            jd_file = st.file_uploader("Upload JD (.txt)", type=["txt"])
            if jd_file:
                jd_text = jd_file.read().decode("utf-8", errors="ignore")
                st.success(f"Loaded: {jd_file.name} ({len(jd_text.split())} words)")

    with col_ex:
        st.markdown("<div class='section-card'>", unsafe_allow_html=True)
        if st.button("Load Example JD", use_container_width=True):
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
        st.markdown("<div class='small-muted'>Use the example to demo the dashboard quickly.</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.get("jd_text_override"):
        jd_text = st.session_state["jd_text_override"]
        st.text_area("Job Description (example loaded)", jd_text, height=240, key="jd_display")

    st.markdown("---")
    st.markdown("## Resume Upload")

    uploaded_files = st.file_uploader(
        "Drop PDF / DOCX / TXT resume files here",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True
    )

    if uploaded_files:
        st.success(f"{len(uploaded_files)} file(s) uploaded")
        with st.expander("View uploaded files"):
            for f in uploaded_files:
                st.write(f"• {f.name} ({f.size / 1024:.1f} KB)")

    st.markdown("---")
    run_col, _ = st.columns([1, 3])
    with run_col:
        run_btn = st.button("Run Ranking", use_container_width=True)

    if run_btn:
        if not jd_text.strip():
            st.error("Please enter a Job Description first.")
        elif not uploaded_files:
            st.error("Please upload at least one resume.")
        else:
            with tempfile.TemporaryDirectory() as tmpdir:
                for uf in uploaded_files:
                    dest = os.path.join(tmpdir, uf.name)
                    with open(dest, "wb") as out:
                        out.write(uf.read())

                prog_bar = st.progress(0, text="Starting...")
                status_txt = st.empty()

                def progress_cb(cur, total, fname):
                    pct = int(cur / total * 85)
                    prog_bar.progress(pct, text=f"Processing {fname}...")
                    status_txt.text(f"Analysing {cur}/{total}: {fname}")

                t0 = time.time()
                results, ignored = rank_resumes(tmpdir, jd_text, progress_callback=progress_cb)
                elapsed = time.time() - t0

                prog_bar.progress(100, text="Done")
                status_txt.empty()

            summary = compute_summary(results)

            st.session_state["results"] = results
            st.session_state["summary"] = summary
            st.session_state["jd_text"] = jd_text
            st.session_state["ignored"] = ignored
            st.session_state["elapsed"] = elapsed

            st.success(f"Ranked {len(results)} candidate(s) in {elapsed:.2f}s. Open the Results or Recruiter Brief tab.")

            if ignored:
                st.warning(f"Skipped {len(ignored)} file(s): {', '.join(ignored)}")


# ══════════════════════════
#  TAB 2 – RESULTS
# ══════════════════════════
with tab_results:
    if "results" not in st.session_state:
        st.info("Go to the Upload & Rank tab to get started.")
    else:
        results: List[CandidateResult] = st.session_state["results"]
        summary = st.session_state["summary"]
        jd_text_stored = st.session_state.get("jd_text", "")
        elapsed = st.session_state.get("elapsed", 0)

        filtered = [
            r for r in results
            if r.status in filter_status
            and r.final_score >= min_score
            and r.experience_years >= min_exp
        ][:top_n]

        shortlisted_count = sum(1 for r in filtered if r.status == "Shortlisted")
        maybe_count = sum(1 for r in filtered if r.status == "Maybe")
        avg_score = sum(r.final_score for r in filtered) / len(filtered) if filtered else 0
        high_priority = sum(1 for r in filtered if get_priority_label(r) == "High Priority")

        st.markdown(f"""
        <div class="ribbon-row">
          <div class="ribbon-card">
            <div class="ribbon-label">Candidates in View</div>
            <div class="ribbon-value">{len(filtered)}</div>
            <div class="ribbon-sub">Filtered shortlist window</div>
          </div>
          <div class="ribbon-card">
            <div class="ribbon-label">Shortlisted</div>
            <div class="ribbon-value">{shortlisted_count}</div>
            <div class="ribbon-sub">Ready to prioritize</div>
          </div>
          <div class="ribbon-card">
            <div class="ribbon-label">High Priority</div>
            <div class="ribbon-value">{high_priority}</div>
            <div class="ribbon-sub">Strong score + coverage + experience</div>
          </div>
          <div class="ribbon-card">
            <div class="ribbon-label">Average Match</div>
            <div class="ribbon-value">{avg_score:.0%}</div>
            <div class="ribbon-sub">Across visible candidates</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        leader = filtered[0] if filtered else None
        signal_1 = (
            f"{leader.name or leader.filename} leads the current slate with a {leader.final_score:.0%} match."
            if leader else
            "Upload and rank resumes to generate your lead-candidate insight."
        )
        signal_2 = (
            f"{shortlisted_count} profiles are currently recruiter-ready, while {maybe_count} may need manager review."
            if filtered else
            "Status mix will appear here once candidates are ranked."
        )
        signal_3 = (
            f"Average time to rank this batch: {elapsed:.2f}s."
            if "elapsed" in st.session_state else
            "Processing speed signal will appear after ranking."
        )

        st.markdown(f"""
        <div class="signal-board">
          <div class="signal-card teal">
            <div class="signal-kicker">Lead Signal</div>
            <div class="signal-title">Who stands out first</div>
            <div class="signal-copy">{signal_1}</div>
          </div>
          <div class="signal-card gold">
            <div class="signal-kicker">Pipeline View</div>
            <div class="signal-title">How the slate stacks up</div>
            <div class="signal-copy">{signal_2}</div>
          </div>
          <div class="signal-card coral">
            <div class="signal-kicker">Workflow</div>
            <div class="signal-title">Decision speed</div>
            <div class="signal-copy">{signal_3}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

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

                st.markdown(f"""
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
                        <div class="metric-mini">
                          <div class="label">Experience</div>
                          <div class="value">{r.experience_years} years</div>
                        </div>
                        <div class="metric-mini">
                          <div class="label">Education</div>
                          <div class="value">{titleize(r.education)}</div>
                        </div>
                        <div class="metric-mini">
                          <div class="label">Skill Coverage</div>
                          <div class="value">{r.skill_coverage}%</div>
                        </div>
                        <div class="metric-mini">
                          <div class="label">Seniority</div>
                          <div class="value">{titleize(r.seniority)}</div>
                        </div>
                      </div>

                      <div class="skill-section">
                        <div class="section-title">Key matched skills</div>
                        <div>{matched_preview}</div>
                      </div>

                      <div class="skill-section">
                        <div class="section-title">Important missing skills</div>
                        <div>{missing_preview}</div>
                      </div>

                      <div class="priority-banner">
                        <strong>Recommended recruiter action: {recommended_action(r)}</strong>
                        <span>Priority: {priority} · Contact visibility: {("Complete" if r.email or r.phone or r.linkedin else "Limited")}</span>
                      </div>
                    </div>

                    <div class="rank-pill">
                      <span class="rk">Rank</span>
                      <span class="rv">#{r.rank}</span>
                    </div>
                  </div>
                </div>
                """, unsafe_allow_html=True)

                with st.expander(f"Open recruiter details for {r.filename}"):
                    d1, d2 = st.columns(2)

                    with d1:
                        st.markdown("**Contact**")
                        st.markdown(f"- Email: {safe_text(r.email)}")
                        st.markdown(f"- Phone: {safe_text(r.phone)}")
                        st.markdown(f"- LinkedIn: {safe_text(r.linkedin)}")
                        st.markdown(f"- GitHub: {safe_text(r.github)}")

                        strengths = top_strengths(r)
                        st.markdown("**Top strengths**")
                        if strengths:
                            for item in strengths:
                                st.markdown(f"- {item}")
                        else:
                            st.markdown("- No standout strengths surfaced")

                    with d2:
                        st.markdown("**Decision support**")
                        st.markdown(f"- Match Score: {r.final_score:.0%}")
                        st.markdown(f"- Interview Readiness: {interview_readiness(r)}")
                        st.markdown(f"- Priority: {priority}")
                        st.markdown(f"- Suggested Action: {recommended_action(r)}")

                        risks = key_risks(r)
                        st.markdown("**Risks / gaps**")
                        if risks:
                            for item in risks:
                                st.markdown(f"- {item}")
                        else:
                            st.markdown("- No major risks surfaced")

                    if r.matched_skills:
                        st.markdown("**Matched skills by area**")
                        for grp, skills in r.matched_skills.items():
                            clean_skills = [s for s in skills if str(s).strip()]
                            if clean_skills:
                                st.markdown(f"- **{grp}:** {', '.join(clean_skills)}")

                    decision_value = st.selectbox(
                        "Recruiter decision",
                        [
                            "Move to recruiter screen",
                            "Send to hiring manager",
                            "Keep in backup pipeline",
                            "Archive for now"
                        ],
                        index=[
                            "Move to recruiter screen",
                            "Send to hiring manager",
                            "Keep in backup pipeline",
                            "Archive for now"
                        ].index(default_decision if default_decision in [
                            "Move to recruiter screen",
                            "Send to hiring manager",
                            "Keep in backup pipeline",
                            "Archive for now"
                        ] else "Archive for now"),
                        key=decision_key
                    )
                    st.session_state["recruiter_decisions"][r.filename] = decision_value

                    note_value = st.text_area(
                        "Recruiter notes",
                        value=st.session_state["recruiter_notes"].get(r.filename, ""),
                        placeholder="Add interview notes, talking points, or concerns...",
                        height=120,
                        key=note_key
                    )
                    st.session_state["recruiter_notes"][r.filename] = note_value

        st.markdown("---")
        st.markdown("## Export Results")
        ec1, ec2, ec3 = st.columns(3)

        with tempfile.TemporaryDirectory() as tdir:
            csv_path = export_csv(results, os.path.join(tdir, "ranked_resumes.csv"))
            json_path = export_json(results, summary, os.path.join(tdir, "ranking_results.json"))
            txt_path = export_txt_report(results, summary, jd_text_stored, os.path.join(tdir, "ranking_report.txt"))

            with open(csv_path, "rb") as f:
                csv_bytes = f.read()
            with open(json_path, "rb") as f:
                json_bytes = f.read()
            with open(txt_path, "rb") as f:
                txt_bytes = f.read()

        with ec1:
            _dl_button("Download CSV", csv_bytes, "ranked_resumes.csv", "text/csv")
        with ec2:
            _dl_button("Download JSON", json_bytes, "ranking_results.json", "application/json")
        with ec3:
            _dl_button("Download Report", txt_bytes, "ranking_report.txt", "text/plain")


# ══════════════════════════
#  TAB 3 – RECRUITER BRIEF
# ══════════════════════════
with tab_brief:
    if "results" not in st.session_state:
        st.info("Run the ranking first to generate the recruiter brief.")
    else:
        results: List[CandidateResult] = st.session_state["results"]
        shortlist = [r for r in results if r.status == "Shortlisted"]
        maybes = [r for r in results if r.status == "Maybe"]
        lead = results[0] if results else None

        st.markdown("## Recruiter Brief")
        st.markdown("<div class='small-muted'>A presentation-ready hiring summary built from the ranked slate.</div>", unsafe_allow_html=True)

        top_names = ", ".join([(r.name or r.filename) for r in results[:3]]) if results else "N/A"
        lead_line = (
            f"Top recommendation: {lead.name or lead.filename} at {lead.final_score:.0%} match."
            if lead else
            "No lead candidate yet."
        )
        shortlist_line = f"{len(shortlist)} candidate(s) are currently shortlisted and {len(maybes)} are in the review band."
        risk_count = sum(1 for r in results[:5] if len(r.missing_skills) >= 5)
        risk_line = f"{risk_count} of the top 5 profiles show notable capability gaps that should be probed in screening."

        st.markdown(f"""
        <div class="signal-board">
          <div class="signal-card teal">
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
        """, unsafe_allow_html=True)

        if results:
            top3 = results[:3]
            for idx, cand in enumerate(top3, start=1):
                st.markdown(f"""
                <div class="section-card" style="margin-bottom:1rem;">
                  <div class="section-title">Top {idx} candidate spotlight</div>
                  <h3 style="margin:0.1rem 0 0.6rem 0;">{cand.name or cand.filename}</h3>
                  <div class="small-muted">{recruiter_summary(cand)}</div>
                </div>
                """, unsafe_allow_html=True)

                c1, c2, c3 = st.columns(3)
                c1.metric("Match Score", f"{cand.final_score:.0%}")
                c2.metric("Experience", f"{cand.experience_years} yrs")
                c3.metric("Coverage", f"{cand.skill_coverage}%")

                strengths = top_strengths(cand, limit=5)
                risks = key_risks(cand, limit=5)

                left, right = st.columns(2)
                with left:
                    st.markdown("**What stands out**")
                    for item in strengths:
                        st.markdown(f"- {item}")
                with right:
                    st.markdown("**What to validate in screening**")
                    for item in risks:
                        st.markdown(f"- {item}")

        st.markdown("---")
        st.markdown("## Recruiter Contact Sheet")
        sheet_df = candidate_contact_sheet(results)
        st.markdown('<div class="table-card">', unsafe_allow_html=True)
        st.dataframe(sheet_df, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        brief_lines = []
        for r in results[:10]:
            brief_lines.append({
                "Rank": r.rank,
                "Candidate": r.name or r.filename,
                "Status": r.status,
                "Priority": get_priority_label(r),
                "Action": st.session_state["recruiter_decisions"].get(r.filename, recommended_action(r)),
                "Notes": st.session_state["recruiter_notes"].get(r.filename, "")
            })
        notes_df = pd.DataFrame(brief_lines)
        st.markdown("## Recruiter Decision Log")
        st.markdown('<div class="table-card">', unsafe_allow_html=True)
        st.dataframe(notes_df, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════
#  TAB 4 – ANALYTICS
# ══════════════════════════
with tab_analytics:
    if "results" not in st.session_state:
        st.info("Run the ranking first.")
    else:
        results: List[CandidateResult] = st.session_state["results"]

        st.markdown("## Hiring Analytics")

        df = pd.DataFrame([{
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
        } for r in results])

        col_a, col_b = st.columns(2)

        with col_a:
            fig1 = px.bar(
                df.head(15),
                x="Score",
                y="Name",
                orientation="h",
                color="Status",
                color_discrete_map={
                    "Shortlisted": "#0f766e",
                    "Maybe": "#c48a2c",
                    "Not Relevant": "#b94f37"
                },
                title="Top Candidate Match Scores",
                template="simple_white"
            )
            fig1.update_layout(
                plot_bgcolor="rgba(255,255,255,0)",
                paper_bgcolor="rgba(255,255,255,0)",
                font_family="Manrope",
                yaxis=dict(autorange="reversed"),
                title_font=dict(family="Instrument Serif", size=20),
                xaxis_tickformat=".0%",
                legend_title_text=""
            )
            st.plotly_chart(fig1, use_container_width=True)

        with col_b:
            status_counts = df["Status"].value_counts().reset_index()
            status_counts.columns = ["Status", "Count"]
            fig2 = px.pie(
                status_counts,
                values="Count",
                names="Status",
                color="Status",
                color_discrete_map={
                    "Shortlisted": "#0f766e",
                    "Maybe": "#c48a2c",
                    "Not Relevant": "#b94f37"
                },
                title="Status Distribution",
                hole=0.55,
                template="simple_white"
            )
            fig2.update_layout(
                plot_bgcolor="rgba(255,255,255,0)",
                paper_bgcolor="rgba(255,255,255,0)",
                font_family="Manrope",
                title_font=dict(family="Instrument Serif", size=20),
                legend_title_text=""
            )
            st.plotly_chart(fig2, use_container_width=True)

        col_c, col_d = st.columns(2)

        with col_c:
            fig3 = px.scatter(
                df,
                x="Experience",
                y="Score",
                color="Priority",
                size="Coverage %",
                hover_name="Name",
                color_discrete_map={
                    "High Priority": "#0f766e",
                    "Strong Review": "#c48a2c",
                    "Hold for Review": "#d0a050",
                    "Low Priority": "#b94f37",
                },
                title="Experience vs Match Score",
                template="simple_white"
            )
            fig3.update_layout(
                plot_bgcolor="rgba(255,255,255,0)",
                paper_bgcolor="rgba(255,255,255,0)",
                font_family="Manrope",
                title_font=dict(family="Instrument Serif", size=20),
                yaxis_tickformat=".0%",
                legend_title_text=""
            )
            st.plotly_chart(fig3, use_container_width=True)

        with col_d:
            fig4 = px.histogram(
                df,
                x="Coverage %",
                nbins=10,
                title="Skill Coverage Distribution",
                template="simple_white",
                color_discrete_sequence=["#1e334d"]
            )
            fig4.update_layout(
                plot_bgcolor="rgba(255,255,255,0)",
                paper_bgcolor="rgba(255,255,255,0)",
                font_family="Manrope",
                title_font=dict(family="Instrument Serif", size=20)
            )
            st.plotly_chart(fig4, use_container_width=True)

        st.markdown("### Most Common Skills Across Resumes")
        all_skills_counter = Counter()
        for r in results:
            for s in r.all_skills_flat:
                all_skills_counter[s] += 1

        if all_skills_counter:
            skill_df = pd.DataFrame(all_skills_counter.most_common(20), columns=["Skill", "Count"])
            fig5 = px.bar(
                skill_df,
                x="Count",
                y="Skill",
                orientation="h",
                title="Top 20 Skills Found",
                template="simple_white",
                color="Count",
                color_continuous_scale=["#dfe7f1", "#1e334d"]
            )
            fig5.update_layout(
                plot_bgcolor="rgba(255,255,255,0)",
                paper_bgcolor="rgba(255,255,255,0)",
                font_family="Manrope",
                title_font=dict(family="Instrument Serif", size=20),
                yaxis=dict(autorange="reversed"),
                coloraxis_showscale=False
            )
            st.plotly_chart(fig5, use_container_width=True)

        st.markdown("### Candidate Summary Table")
        display_df = candidate_table(results)
        st.markdown('<div class="table-card">', unsafe_allow_html=True)
        st.dataframe(display_df, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════
#  TAB 5 – COMPARE
# ══════════════════════════
with tab_compare:
    if "results" not in st.session_state:
        st.info("Run the ranking first.")
    else:
        results: List[CandidateResult] = st.session_state["results"]

        st.markdown("## Candidate Comparison")

        names = [r.filename for r in results]
        sel_a = st.selectbox("Candidate A", names, index=0)
        sel_b = st.selectbox("Candidate B", names, index=min(1, len(names) - 1))

        ca = next(r for r in results if r.filename == sel_a)
        cb = next(r for r in results if r.filename == sel_b)

        col_ca, col_cb = st.columns(2)

        def show_candidate_panel(col, c: CandidateResult):
            with col:
                st.markdown(f'<div class="section-card">', unsafe_allow_html=True)
                st.markdown(f"### {c.name or c.filename}")
                st.markdown(f"**Status:** {c.status}")
                st.metric("Match Score", f"{c.final_score:.0%}")
                st.metric("Experience", f"{c.experience_years} yrs")
                st.metric("Skill Coverage", f"{c.skill_coverage}%")
                st.markdown(f"**Education:** {titleize(c.education)}")
                st.markdown(f"**Seniority:** {titleize(c.seniority)}")
                st.markdown(f"**Priority:** {get_priority_label(c)}")
                st.markdown(f"**Action:** {recommended_action(c)}")
                st.markdown(f"**Email:** {safe_text(c.email)}")
                st.markdown(f"**Phone:** {safe_text(c.phone)}")
                st.markdown(f"**LinkedIn:** {safe_text(c.linkedin)}")
                st.markdown('</div>', unsafe_allow_html=True)

        show_candidate_panel(col_ca, ca)
        show_candidate_panel(col_cb, cb)

        categories = ["Match Score", "Skill Coverage", "Experience (norm)"]
        def norm_exp(e):
            return min(e / 15, 1.0)

        fig_radar = go.Figure()
        for c, color in [(ca, "#0f766e"), (cb, "#c48a2c")]:
            vals = [c.final_score, c.skill_coverage / 100, norm_exp(c.experience_years)]
            fig_radar.add_trace(go.Scatterpolar(
                r=vals + [vals[0]],
                theta=categories + [categories[0]],
                fill="toself",
                name=c.name or c.filename,
                line_color=color,
                fillcolor=hex_to_rgba(color, 0.18)
            ))

        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 1]),
                bgcolor="rgba(255,255,255,0)"
            ),
            showlegend=True,
            template="simple_white",
            paper_bgcolor="rgba(255,255,255,0)",
            title="Candidate Comparison Radar",
            title_font=dict(family="Instrument Serif", size=22),
            font=dict(family="Manrope")
        )
        st.plotly_chart(fig_radar, use_container_width=True)

        set_a = set(ca.all_skills_flat)
        set_b = set(cb.all_skills_flat)
        shared = set_a & set_b
        only_a = set_a - set_b
        only_b = set_b - set_a

        s1, s2, s3 = st.columns(3)
        with s1:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown(f"**Only in {ca.name or ca.filename}**")
            for s in sorted(only_a)[:20]:
                st.markdown(f"- {s}")
            st.markdown('</div>', unsafe_allow_html=True)
        with s2:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown("**Shared Skills**")
            for s in sorted(shared)[:20]:
                st.markdown(f"- {s}")
            st.markdown('</div>', unsafe_allow_html=True)
        with s3:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown(f"**Only in {cb.name or cb.filename}**")
            for s in sorted(only_b)[:20]:
                st.markdown(f"- {s}")
            st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════
#  TAB 6 – ABOUT
# ══════════════════════════
with tab_about:
    st.markdown("""
## About AI Resume Ranker

This version keeps your ranking workflow intact while making the experience feel more like a recruiter-facing product than a technical demo.

### What was added
- A redesigned visual system with a more editorial, premium feel
- Recruiter-ready candidate cards with clearer hierarchy
- Priority labels and recommended next actions
- Recruiter Brief tab for top-slate storytelling
- Recruiter notes and decision tracking
- Contact sheet and decision log views
- Cleaner analytics focused on hiring decisions

### Best use
Use it as a first-pass screening dashboard, then hand the shortlist to hiring managers with stronger context and cleaner presentation.
""")
