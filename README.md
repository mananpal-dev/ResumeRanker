<div align="center">

# AI Resume Ranker

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-Web_App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-NLP_Engine-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![Plotly](https://img.shields.io/badge/Plotly-Analytics-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-B5F23C?style=for-the-badge)](LICENSE)

<br/>

**[🌐 Live Demo](https://resume-ranker-by-manan.streamlit.app)** &nbsp;·&nbsp; **[👤 Portfolio](https://manan-pal-portfolio.vercel.app)** &nbsp;·&nbsp; **[💻 GitHub](https://github.com/mananpal-dev/ResumeRanker)**

<br/>

> *Most ATS tools are black boxes. This one shows its work.*

</div>

---

## What This Is

AI Resume Ranker is a full-stack screening dashboard that combines weighted NLP scoring with a recruiter-facing interface. Drop in resumes and a job description — it returns a ranked shortlist with match scores, skill gap analysis, priority labels, interview readiness signals, and recommended next actions. The UI is built to present, not just prototype.

Two interfaces ship together:

- **Streamlit web app** — recruiter dashboard with analytics, radar comparison, and decision logging
- **Tkinter desktop app** — fast local GUI with a dedicated Recruiter View tab for notes and decisions

---

## How the Scoring Works

```
Final Score = 0.60 × TF-IDF Cosine Similarity
            + 0.25 × Keyword Match Score
            + 0.10 × Seniority Match
            + 0.05 × Education Match
```

| Component | Weight | What It Measures |
|---|---|---|
| TF-IDF Cosine Similarity | 60% | Bigram vector comparison between resume and JD |
| Keyword Match Score | 25% | Exact match against 80+ curated skills across 6 groups |
| Seniority Match | 10% | Junior / Mid / Senior alignment with the JD |
| Education Match | 5% | Diploma → Bachelor → Master → PhD tier comparison |

### Status Thresholds

| Score | Status |
|---|---|
| ≥ 0.45 | ✅ Shortlisted |
| ≥ 0.20 | 🤔 Maybe |
| < 0.20 | ❌ Not Relevant |

### Priority Labels

On top of status, each candidate gets a recruiter-facing priority tier — blending score, skill coverage, and experience into one signal.

| Label | Criteria |
|---|---|
| High Priority | Score ≥ 0.82 · Coverage ≥ 65% · Experience ≥ 4yr |
| Strong Review | Score ≥ 0.62 · Coverage ≥ 45% |
| Hold for Review | Score ≥ 0.20 |
| Low Priority | Below all thresholds |

---

## Features

**Scoring & Ranking**
- Multi-factor NLP pipeline — TF-IDF bigrams, keyword matching, seniority, education
- 80+ curated skills across 6 groups: Languages, ML/AI, Frameworks, Web/API, Databases/Cloud, Tools
- Skill gap analysis showing exact missing skills per candidate and per category
- Experience extraction from free text and date ranges
- All thresholds configurable in `config.py` — no code changes needed elsewhere

**Recruiter Intelligence**
- Priority labels combining three signals into one actionable tier
- Interview readiness per candidate
- Recommended next action — recruiter screen / hiring manager / backup pipeline / archive
- Contact completeness visibility — email, phone, LinkedIn, GitHub
- Per-candidate recruiter notes and decision dropdown, persisted within session
- Decision log table from the Recruiter Brief tab

**Interfaces**
- Streamlit: dark editorial dashboard with signal cards, analytics, radar comparison, contact sheet, and recruiter brief
- Tkinter: desktop app with Rankings, Summary, Recruiter View, and Skill Map tabs
- Double-click any candidate in the desktop app to open a full detail and notes panel

**Analytics**
- Match score bar chart across top candidates
- Status distribution donut chart
- Experience vs match score scatter plot
- Skill coverage histogram
- Top 20 skills frequency chart
- Side-by-side radar comparison with skill overlap breakdown

**Exports**
- CSV ranked results
- JSON with full scoring breakdown
- TXT recruiter report
- Bundled sample mode for zero-friction portfolio demos

---

## Project Structure

```
AI-Resume-Ranker/
│
├── app.py                    ← Streamlit web app
├── main.py                   ← Tkinter desktop app
├── resume_generator.py       ← Synthetic resume generator
├── config.py                 ← All settings, weights, thresholds
│
├── utils/
│   ├── __init__.py
│   ├── text_processing.py    ← PDF / DOCX parsing, NLP helpers
│   ├── ranker.py             ← Core scoring and ranking engine
│   └── exporter.py           ← CSV / JSON / TXT exporters
│
├── resumes/                  ← Place candidate resumes here
├── sample_jd.txt             ← Bundled JD for demo mode
├── requirements.txt
└── README.md
```

---

## Installation

### 1. Clone the repo
```bash
git clone https://github.com/mananpal-dev/ResumeRanker.git
cd ResumeRanker
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add your data
- Drop PDF, DOCX, or TXT resumes into `/resumes`
- Paste the target job description into `sample_jd.txt`

---

## Running the App

### Streamlit Web App
```bash
streamlit run app.py
```
Opens the full recruiter dashboard in your browser — rank candidates, review signals, export shortlists.

### Tkinter Desktop App
```bash
python main.py
```
Local GUI with Rankings, Summary, Recruiter View, and Skill Map tabs. Double-click any candidate to open a detail panel with notes.

### Synthetic Resume Generator
```bash
streamlit run resume_generator.py
```
Generates realistic test resumes for 6 target roles with varied seniority, skills, tone, and optional intentional skill gaps. Export as ZIP or individual `.txt` files — feed directly into the ranker.

---

## Bundled Demo Mode

For portfolio demos where you don't want reviewers to upload anything, set up the sample assets once:

```
ResumeRanker/
├── sample_jd.txt
└── resumes/
    ├── candidate_01.pdf
    ├── candidate_02.pdf
    └── ...
```

Select **Bundled sample resumes** in the app — reviewers click once and immediately see a full ranked shortlist with recruiter signals, no uploads required.

🔗 See it live: [resume-ranker-by-manan.streamlit.app](https://resume-ranker-by-manan.streamlit.app)

---

## Configuration

Everything lives in `config.py`:

```python
# Scoring weights
TFIDF_WEIGHT     = 0.60
KEYWORD_WEIGHT   = 0.25
SENIORITY_WEIGHT = 0.10
EDUCATION_WEIGHT = 0.05

# Status thresholds
SHORTLIST_THRESHOLD = 0.45
MAYBE_THRESHOLD     = 0.20

# Priority thresholds
PRIORITY_HIGH_SCORE    = 0.82
PRIORITY_HIGH_COVERAGE = 65
PRIORITY_HIGH_EXP      = 4

# Interview readiness
INTERVIEW_READY_SCORE  = 0.75
```

Change any value and re-run. Nothing else needs touching.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.9+ |
| NLP / ML | scikit-learn · TF-IDF · Cosine Similarity |
| PDF Parsing | pdfplumber · PyPDF2 |
| DOCX Parsing | docx2txt |
| Web UI | Streamlit |
| Charts | Plotly |
| Desktop UI | Tkinter |
| Data | pandas · numpy |

---

## Example Output

```
===== RANKED CANDIDATES =====

#01  aisha_rahman_swe.pdf
     Status    : ✅ Shortlisted
     Score     : 0.9421  (TF-IDF: 0.881  KW: 0.912)
     Priority  : High Priority
     Readiness : Ready now
     Action    : Move to recruiter screen
     Skills    : python, react, aws, docker, machine learning
     Missing   : langchain, kafka, airflow
     Coverage  : 94%  |  Seniority: senior  |  Exp: 6yr

#02  priya_kapoor_ml.pdf
     Status    : ✅ Shortlisted
     Score     : 0.9102  (TF-IDF: 0.854  KW: 0.889)
     Priority  : High Priority
     ...

===== SUMMARY =====
  Total: 12  |  Shortlisted: 4  |  Maybe: 5  |  Not Relevant: 3
  High Priority: 2  |  Avg Score: 0.6214  |  Top Score: 0.9421
```

---

## Roadmap

- [ ] BERT-based semantic similarity
- [ ] GPT-powered candidate summary generation
- [ ] Resume anonymisation for bias-free screening
- [ ] Batch email generation for shortlisted candidates
- [ ] FastAPI REST endpoint
- [ ] Docker containerisation

---

## Dataset Credits

Sample resumes used for testing are sourced from publicly available datasets on Kaggle for educational purposes only.

---

## Author

<div align="center">

**Manan Pal**  
B.Tech CSE · Aspiring Software & AI Developer

[![Portfolio](https://img.shields.io/badge/Portfolio-Visit-B5F23C?style=for-the-badge&logo=vercel&logoColor=black)](https://manan-pal-portfolio.vercel.app)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/mananpal-dev)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/mananpal-dev)
[![Live Demo](https://img.shields.io/badge/Live_Demo-Open_App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://resume-ranker-by-manan.streamlit.app)

</div>

---

<div align="center">

⭐ **Star this repo if it helped you**

*Built to make hiring smarter, faster, and fairer.*

</div>