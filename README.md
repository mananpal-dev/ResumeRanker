<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Syne&weight=700&size=34&pause=1000&color=6C63FF&center=true&vCenter=true&width=700&lines=🎯+AI+Resume+Ranker+v2.0;NLP-Powered+Candidate+Screening;Multi-Factor+Weighted+Scoring" alt="Typing SVG" />

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-Web_App-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-ML_Engine-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![Plotly](https://img.shields.io/badge/Plotly-Analytics-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-00e17a?style=for-the-badge)](LICENSE)

<br>

> **An intelligent, multi-factor NLP system that ranks resumes against job descriptions — built to show how modern ATS works, with full explainability.**

</div>

---

## 🚀 What's New in v2.0

| Feature | v1.0 | v2.0 |
|---|:---:|:---:|
| TF-IDF cosine similarity | ✅ | ✅ Enhanced (bigrams) |
| Keyword matching | Basic | ✅ 80+ skills, 6 categories |
| Seniority detection | ❌ | ✅ |
| Education tier matching | ❌ | ✅ |
| Experience year extraction | ❌ | ✅ |
| Skill gap analysis | ❌ | ✅ |
| Contact info extraction | ❌ | ✅ Email · Phone · LinkedIn · GitHub |
| DOCX support | ❌ | ✅ |
| Streamlit web app | ❌ | ✅ Full dashboard |
| Interactive analytics | ❌ | ✅ 6 Plotly charts |
| Side-by-side comparison | ❌ | ✅ Radar chart |
| JSON export | ❌ | ✅ |
| Modular architecture | ❌ | ✅ |

---

## 🧠 How the Scoring Works

```
Final Score = 0.60 × TF-IDF_Cosine
            + 0.25 × Keyword_Match
            + 0.10 × Seniority_Match
            + 0.05 × Education_Match
```

| Component | Weight | Description |
|---|---|---|
| **TF-IDF Cosine Similarity** | 60% | Bigram TF-IDF vectors compared via cosine distance |
| **Keyword Match Score** | 25% | Exact match across 80+ curated tech skills in 6 groups |
| **Seniority Match** | 10% | Compares JD seniority tier vs resume tier |
| **Education Match** | 5% | Diploma → Bachelor → Master → PhD tier comparison |

### Status Thresholds
| Score | Status |
|---|---|
| ≥ 0.45 | ✅ **Shortlisted** |
| ≥ 0.20 | 🤔 **Maybe** |
| < 0.20 | ❌ **Not Relevant** |

---

## ✨ Key Features

- 🗂️ **Multi-format support** — PDF, DOCX, TXT resumes
- 🎯 **Weighted NLP scoring** — 4-factor formula for accurate ranking
- 🔬 **Skill gap analysis** — shows exactly which required skills a candidate is missing
- 📇 **Contact extraction** — auto-extracts email, phone, LinkedIn, GitHub
- 🎓 **Education detection** — Diploma / Bachelor / Master / PhD tier matching
- 👔 **Seniority detection** — Junior / Mid / Senior level awareness
- 📅 **Experience estimation** — reads years from resume text and date ranges
- 📊 **Analytics dashboard** — 6 interactive Plotly charts (Streamlit app)
- ⚖️ **Candidate comparison** — radar chart side-by-side comparison
- 📥 **3 export formats** — CSV, JSON, TXT report
- 🖥️ **Two interfaces** — Streamlit web app + Tkinter desktop app

---

## 📂 Project Structure

```
AI-Resume-Ranker/
│
├── app.py                  ← 🌐 Streamlit web app (run this!)
├── main.py                 ← 🖥️  Tkinter desktop app
├── config.py               ← ⚙️  All settings & thresholds
│
├── utils/
│   ├── __init__.py
│   ├── text_processing.py  ← 📝 PDF/DOCX parsing, NLP helpers
│   ├── ranker.py           ← 🧠 Core scoring & ranking engine
│   └── exporter.py         ← 📥 CSV / JSON / TXT exporters
│
├── resumes/                ← 📂 Place candidate PDFs here
├── job_description.txt     ← 📋 Sample JD (edit or replace)
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/mananpal-dev/ResumeRanker.git
cd AI-Resume-Ranker
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add your resumes
Place PDF, DOCX, or TXT resumes inside the `/resumes` folder.

### 4. Edit the job description
Open `job_description.txt` and paste your target role's JD.

---

## 🏃 Running the App

### 🌐 Streamlit Web App (recommended)
```bash
streamlit run app.py
```
Opens a full interactive dashboard in your browser with charts, filters, exports, and side-by-side comparison.

### 🖥️ Tkinter Desktop App
```bash
python main.py
```
Classic desktop GUI with tabbed interface, colour-coded results, and export options.

---

## 📊 Example Output

```
===== RANKED CANDIDATES =====

#1  john_doe.pdf
    Status   : ✅ Shortlisted
    Score    : 0.7842  (TF-IDF=0.621 | KW=0.480)
    Skills   : python, machine learning, deep learning, tensorflow,
               pandas, numpy, sql, docker, aws, fastapi
    Missing  : langchain, airflow, kafka
    Coverage : 76.9%
    Seniority: senior  |  Education: masters  |  Exp: 6yr
    Email    : john@example.com
    LinkedIn : linkedin.com/in/johndoe

#2  jane_smith.pdf
    Status   : ✅ Shortlisted
    Score    : 0.6931  (TF-IDF=0.558 | KW=0.400)
    ...

===== SUMMARY =====
  Total: 10  |  Shortlisted: 3  |  Maybe: 4  |  Not Relevant: 3
  Avg Score: 0.3821  |  Top Score: 0.7842
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.9+ |
| NLP / ML | scikit-learn, TF-IDF, Cosine Similarity |
| PDF Parsing | pdfplumber, PyPDF2 |
| DOCX Parsing | docx2txt |
| Web UI | Streamlit |
| Charts | Plotly |
| Desktop UI | Tkinter |
| Data | pandas, numpy |

---

## 📥 Dataset Credits

Sample resumes used for testing are sourced from publicly available datasets on Kaggle for educational purposes only.

Dataset: [Resume Data PDF — Kaggle](https://www.kaggle.com/datasets/hadikp/resume-data-pdf)

---

## 🗺️ Roadmap

- [ ] Resume anonymisation mode (remove names/contact for bias-free screening)
- [ ] GPT-powered resume summary generation
- [ ] Batch email generation for shortlisted candidates
- [ ] BERT-based semantic similarity (beyond TF-IDF)
- [ ] REST API endpoint (FastAPI)
- [ ] Docker containerization

---

## 👨‍💻 Author

**Manan Pal**  
B.Tech CSE Student · Aspiring Software & AI Developer

[![GitHub](https://img.shields.io/badge/GitHub-Follow-181717?style=for-the-badge&logo=github)](https://github.com/yourusername)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?style=for-the-badge&logo=linkedin)](https://linkedin.com/in/yourprofile)

---

<div align="center">

⭐ **Star this repo if it helped you** — it motivates further improvements!

*Built with ❤️ to make hiring smarter, faster, and fairer.*

</div>
