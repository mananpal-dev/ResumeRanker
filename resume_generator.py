import io
import random
import textwrap
import zipfile
from collections import Counter
from dataclasses import dataclass
from typing import List

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Resume Forge Studio",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=DM+Sans:wght@400;500;700;800&display=swap');

    :root {
        --bg: #f4efe6;
        --canvas: #fcf8f1;
        --card: rgba(255, 251, 244, 0.88);
        --ink: #1d2935;
        --muted: #697382;
        --line: rgba(29, 41, 53, 0.08);
        --emerald: #0d7b67;
        --amber: #b9842b;
        --coral: #b65b4e;
        --navy: #1d3f63;
        --mist: #e3efe9;
        --wash: #f7ecd7;
        --shadow: 0 24px 60px rgba(31, 36, 44, 0.08);
    }

    .stApp {
        background:
            radial-gradient(circle at 10% 8%, rgba(185,132,43,0.12), transparent 22%),
            radial-gradient(circle at 88% 12%, rgba(13,123,103,0.14), transparent 24%),
            linear-gradient(180deg, #f7f2ea 0%, #f3ede3 45%, #f8f3eb 100%);
        color: var(--ink);
    }

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
        color: var(--ink);
    }

    h1, h2, h3, h4, .serif {
        font-family: 'Fraunces', serif !important;
        color: var(--ink);
        letter-spacing: 0.15px;
    }

    .block-container {
        max-width: 1380px;
        padding-top: 1.1rem;
        padding-bottom: 2rem;
    }

    .hero {
        position: relative;
        overflow: hidden;
        background:
            linear-gradient(135deg, rgba(255,251,244,0.96), rgba(244,238,227,0.94)),
            linear-gradient(120deg, #fff7ea, #eef4ef);
        border: 1px solid var(--line);
        border-radius: 34px;
        padding: 2.6rem 2.5rem;
        box-shadow: var(--shadow);
        margin-bottom: 1.15rem;
    }

    .hero:before {
        content: "";
        position: absolute;
        right: -80px;
        top: -120px;
        width: 340px;
        height: 340px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(13,123,103,0.16), transparent 62%);
    }

    .hero:after {
        content: "";
        position: absolute;
        left: -110px;
        bottom: -200px;
        width: 360px;
        height: 360px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(185,132,43,0.16), transparent 62%);
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
        padding: 0.42rem 0.86rem;
        border-radius: 999px;
        background: rgba(13,123,103,0.10);
        color: var(--emerald);
        font-size: 0.76rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    .hero-title {
        margin-top: 0.95rem;
        font-size: 4.05rem;
        line-height: 0.94;
        max-width: 780px;
    }

    .hero-copy {
        margin-top: 0.85rem;
        max-width: 730px;
        color: var(--muted);
        font-size: 1rem;
        line-height: 1.76;
    }

    .hero-panel {
        width: 320px;
        background: rgba(255,255,255,0.72);
        border: 1px solid var(--line);
        border-radius: 24px;
        padding: 1.05rem;
        box-shadow: 0 12px 30px rgba(31,36,44,0.05);
    }

    .hero-panel .k {
        font-size: 0.74rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--muted);
        font-weight: 800;
    }

    .hero-panel .v {
        margin-top: 0.28rem;
        font-size: 1.85rem;
        font-weight: 800;
    }

    .hero-panel .s {
        margin-top: 0.36rem;
        color: var(--muted);
        font-size: 0.9rem;
        line-height: 1.65;
    }

    .ribbon-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 1rem;
        margin-bottom: 1.1rem;
    }

    .ribbon {
        background: rgba(255,255,255,0.78);
        border: 1px solid var(--line);
        border-radius: 22px;
        padding: 1rem 1rem 0.95rem;
        box-shadow: 0 10px 28px rgba(31,36,44,0.04);
    }

    .ribbon .label {
        color: var(--muted);
        font-size: 0.74rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 800;
    }

    .ribbon .value {
        margin-top: 0.28rem;
        font-size: 1.58rem;
        font-weight: 800;
    }

    .ribbon .sub {
        margin-top: 0.18rem;
        color: var(--muted);
        font-size: 0.86rem;
    }

    .section-shell {
        background: var(--card);
        border: 1px solid var(--line);
        border-radius: 26px;
        padding: 1.1rem 1.15rem 1.2rem;
        box-shadow: var(--shadow);
    }

    .resume-card {
        background: linear-gradient(180deg, rgba(255,255,255,0.97), rgba(251,246,238,0.97));
        border: 1px solid var(--line);
        border-radius: 28px;
        box-shadow: var(--shadow);
        overflow: hidden;
        margin-bottom: 1rem;
    }

    .resume-head {
        padding: 1.25rem 1.3rem 0.95rem;
        border-bottom: 1px solid var(--line);
        background: linear-gradient(120deg, rgba(227,239,233,0.75), rgba(247,236,215,0.72));
    }

    .resume-name {
        font-size: 1.8rem;
        font-weight: 800;
        color: var(--ink);
    }

    .resume-role {
        margin-top: 0.24rem;
        color: var(--muted);
        font-size: 0.97rem;
    }

    .chip-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.45rem;
        margin-top: 0.78rem;
    }

    .chip {
        border-radius: 999px;
        padding: 0.38rem 0.76rem;
        font-size: 0.76rem;
        font-weight: 700;
        border: 1px solid transparent;
        display: inline-flex;
        align-items: center;
    }

    .chip.emerald { background: #def1eb; color: #0d7b67; border-color: #c7e6dc; }
    .chip.amber { background: #f8edd8; color: #9a6a18; border-color: #ecd5a7; }
    .chip.coral { background: #f6e4df; color: #974b40; border-color: #e9c7bf; }
    .chip.navy { background: #e5edf6; color: #264767; border-color: #d1deed; }

    .resume-body {
        padding: 1rem 1.3rem 1.25rem;
    }

    .metric-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 0.82rem;
        margin-bottom: 0.95rem;
    }

    .metric {
        background: rgba(247,243,234,0.95);
        border: 1px solid rgba(29,41,53,0.05);
        border-radius: 18px;
        padding: 0.84rem;
    }

    .metric .k {
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--muted);
        font-weight: 800;
    }

    .metric .v {
        margin-top: 0.28rem;
        font-size: 1.04rem;
        font-weight: 800;
        color: var(--ink);
    }

    .summary-box {
        background: linear-gradient(90deg, #103f5a, #1d6b69);
        color: #fffdfa;
        border-radius: 18px;
        padding: 0.95rem 1rem;
        margin: 0.85rem 0;
    }

    .summary-box span {
        color: rgba(255,255,255,0.84);
        font-size: 0.92rem;
    }

    .skill-pill {
        display: inline-block;
        padding: 0.31rem 0.72rem;
        border-radius: 999px;
        background: #f1f5f8;
        color: #334155;
        border: 1px solid rgba(51,65,85,0.10);
        margin: 0.18rem;
        font-size: 0.76rem;
        font-weight: 700;
    }

    .small-note {
        color: var(--muted);
        font-size: 0.89rem;
        line-height: 1.68;
    }

    .stButton > button, .stDownloadButton > button {
        border-radius: 14px;
        border: 1px solid rgba(29,41,53,0.08);
        background: linear-gradient(135deg, #1d2935, #23685d);
        color: white;
        font-weight: 800;
        box-shadow: 0 12px 28px rgba(29,41,53,0.10);
    }

    .stTabs [data-baseweb="tab"] {
        background: rgba(255,255,255,0.74);
        border: 1px solid var(--line);
        border-radius: 14px;
        font-weight: 800;
        padding: 0.52rem 0.92rem;
    }

    .stTabs [aria-selected="true"] {
        background: #1d2935 !important;
        color: #fffdfa !important;
    }

    [data-testid="stSidebar"] {
        background:
            radial-gradient(circle at top right, rgba(185,132,43,0.18), transparent 28%),
            linear-gradient(180deg, #1a242f 0%, #243240 62%, #2e3d4d 100%);
    }

    [data-testid="stSidebar"] * {
        color: #f7f4ee !important;
    }

    @media (max-width: 980px) {
        .ribbon-grid, .metric-grid {
            grid-template-columns: 1fr 1fr;
        }
    }

    @media (max-width: 760px) {
        .hero-title {
            font-size: 2.8rem;
        }
        .ribbon-grid, .metric-grid {
            grid-template-columns: 1fr;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


ROLE_LIBRARY = {
    "Data Scientist": {
        "core_skills": ["Python", "Pandas", "NumPy", "Scikit-learn", "SQL", "Machine Learning", "Statistics", "A/B Testing", "NLP", "TensorFlow", "PyTorch", "Feature Engineering"],
        "tools": ["Jupyter", "MLflow", "Docker", "AWS", "PostgreSQL", "Power BI", "Git", "Airflow"],
        "projects": ["customer churn prediction", "pricing intelligence engine", "resume ranking NLP system", "forecasting pipeline", "fraud scoring model"],
        "certs": ["AWS Certified Machine Learning", "TensorFlow Developer Certificate", "Google Data Analytics"],
    },
    "Machine Learning Engineer": {
        "core_skills": ["Python", "PyTorch", "TensorFlow", "MLOps", "Docker", "Kubernetes", "FastAPI", "CI/CD", "Feature Engineering", "Model Deployment", "SQL", "Monitoring"],
        "tools": ["Airflow", "MLflow", "GCP", "AWS", "Redis", "GitHub Actions", "Prometheus", "Grafana"],
        "projects": ["real-time recommendation engine", "model serving platform", "document understanding service", "fraud detection API", "inference optimization pipeline"],
        "certs": ["Google Professional ML Engineer", "AWS Solutions Architect Associate", "Databricks ML Associate"],
    },
    "Frontend Developer": {
        "core_skills": ["React", "TypeScript", "JavaScript", "HTML", "CSS", "Next.js", "Responsive Design", "Accessibility", "Redux", "UI Systems", "Performance Optimization"],
        "tools": ["Figma", "Storybook", "Vite", "Tailwind CSS", "Jest", "Cypress", "Framer Motion", "Webpack"],
        "projects": ["design system rollout", "multi-step onboarding experience", "analytics dashboard", "e-commerce storefront", "candidate portal redesign"],
        "certs": ["Meta Front-End Developer", "Google UX Design", "Scrum Fundamentals"],
    },
    "Backend Developer": {
        "core_skills": ["Python", "FastAPI", "Django", "Node.js", "REST APIs", "PostgreSQL", "Redis", "System Design", "Docker", "CI/CD", "Authentication", "Caching"],
        "tools": ["AWS", "RabbitMQ", "GitHub Actions", "Nginx", "MongoDB", "Prometheus", "Celery", "Docker Compose"],
        "projects": ["payment reconciliation service", "candidate management API", "inventory platform", "workflow automation engine", "document processing backend"],
        "certs": ["AWS Developer Associate", "Oracle Java Foundations", "Postman API Fundamentals"],
    },
    "Full Stack Developer": {
        "core_skills": ["React", "TypeScript", "Python", "FastAPI", "Node.js", "PostgreSQL", "REST APIs", "Docker", "Cloud Deployment", "Testing", "UI Architecture", "State Management"],
        "tools": ["AWS", "Vercel", "GitHub Actions", "Redis", "Jest", "Figma", "Supabase", "Netlify"],
        "projects": ["hiring dashboard", "crm platform", "project collaboration suite", "internal automation portal", "resume workflow app"],
        "certs": ["AWS Cloud Practitioner", "Scrum Fundamentals", "Google Project Management"],
    },
    "Product Manager": {
        "core_skills": ["Roadmapping", "Stakeholder Management", "Analytics", "User Research", "Experimentation", "Agile", "Go-to-Market", "SQL", "Prioritization", "PRDs", "Market Analysis"],
        "tools": ["Jira", "Notion", "Amplitude", "Mixpanel", "Figma", "Looker", "Miro", "Confluence"],
        "projects": ["growth funnel redesign", "retention initiative", "mobile onboarding launch", "marketplace expansion", "self-serve analytics rollout"],
        "certs": ["CSPO", "Google Project Management", "Product School PM"],
    },
}

FIRST_NAMES = [
    "Aarav", "Ishita", "Rohan", "Sana", "Vivaan", "Ananya", "Kabir", "Meera",
    "Dev", "Aditi", "Arjun", "Kiara", "Nikhil", "Tanya", "Reyansh", "Myra",
    "Dhruv", "Siya", "Yash", "Ritika", "Kunal", "Prisha", "Neil", "Rhea",
]
LAST_NAMES = [
    "Sharma", "Reddy", "Patel", "Malhotra", "Verma", "Kapoor", "Nair", "Joshi",
    "Mehta", "Bose", "Chauhan", "Sethi", "Iyer", "Bhatia", "Khanna", "Rao",
    "Menon", "Singh", "Agarwal", "Mishra", "Pillai", "Desai", "Bansal", "Saxena",
]
COMPANIES = [
    "NovaGrid", "Verity Labs", "BlueOrbit", "Northscale", "MintBridge",
    "AetherWorks", "CrestIQ", "LatticeFox", "BrightLayer", "CloudSpire",
    "PixelHarbor", "QuantNest",
]
COLLEGES = [
    "IIT Delhi", "BITS Pilani", "NIT Trichy", "VIT Vellore",
    "Delhi Technological University", "PES University",
    "SRM Institute of Science and Technology", "Manipal Institute of Technology",
]
CITIES = ["Bengaluru", "Hyderabad", "Pune", "Chennai", "Gurugram", "Noida", "Mumbai", "Kochi", "Ahmedabad"]
SOFT_SKILLS = [
    "clear stakeholder communication", "ownership mindset", "cross-functional collaboration",
    "structured problem solving", "fast execution", "mentoring ability",
    "product thinking", "documentation discipline", "decision-making under ambiguity",
]
SUMMARY_STYLES = [
    "Outcome-driven professional with a strong track record of turning ambiguous business needs into measurable results.",
    "Growth-minded builder known for balancing execution speed with quality, stakeholder trust, and user impact.",
    "Detail-oriented operator who combines analytical depth, product instinct, and calm leadership under pressure.",
    "Execution-focused contributor who thrives in fast-moving teams and consistently turns ideas into dependable delivery.",
]
ACHIEVEMENT_VERBS = ["Built", "Led", "Delivered", "Launched", "Improved", "Scaled", "Designed", "Automated", "Optimized"]
IMPACT_PHRASES = [
    "reduced processing time by {n}%",
    "increased conversion by {n}%",
    "improved model accuracy by {n}%",
    "saved {n}+ hours per month",
    "cut manual effort by {n}%",
    "boosted stakeholder visibility by {n}%",
    "raised user satisfaction by {n}%",
]


@dataclass
class ResumeProfile:
    name: str
    role: str
    years: int
    city: str
    email: str
    phone: str
    linkedin: str
    github: str
    summary: str
    skills: List[str]
    tools: List[str]
    strengths: List[str]
    education: str
    certifications: List[str]
    experience_lines: List[str]
    projects: List[str]
    tone: str


def generate_name(existing: set) -> str:
    attempts = 0
    while attempts < 5000:
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        if name not in existing:
            existing.add(name)
            return name
        attempts += 1
    name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)} {random.randint(1, 999)}"
    existing.add(name)
    return name


def role_seniority_title(role: str, years: int) -> str:
    if years <= 1:
        return f"Junior {role}"
    if years <= 3:
        return role
    if years <= 6:
        return f"Senior {role}"
    return f"Lead {role}"


def make_email(name: str) -> str:
    handle = name.lower().replace(" ", ".")
    suffix = random.choice(["mailforge.dev", "careergrid.dev", "inboxlab.dev"])
    return f"{handle}@{suffix}"


def make_phone() -> str:
    return f"+91 {random.randint(70000, 99999)} {random.randint(10000, 99999)}"


def sample_unique(items: List[str], count: int) -> List[str]:
    count = min(count, len(items))
    return random.sample(items, count)


def build_summary(role: str, years: int, tone: str, strengths: List[str]) -> str:
    intro = random.choice(SUMMARY_STYLES)
    seniority = role_seniority_title(role, years)
    strength_line = ", ".join(strengths[:3])
    tone_lines = {
        "Executive": "Brings polished communication, business alignment, and high-trust delivery.",
        "Modern": "Balances current tooling, strong execution, and thoughtful team collaboration.",
        "ATS-Friendly": "Uses clear, role-aligned language with measurable outcomes and relevant keywords.",
        "Ambitious": "Shows strong upward momentum, curiosity, and comfort handling stretch responsibilities.",
        "Calm & Strategic": "Operates with maturity, prioritization discipline, and consistent decision quality.",
    }
    tone_note = tone_lines.get(tone, "Delivers strong results with a balanced professional style.")
    return (
        f"{seniority} based in India with {years}+ years of experience. {intro} "
        f"Known for {strength_line}. {tone_note}"
    )


def build_achievement(role_data: dict, years: int) -> str:
    verb = random.choice(ACHIEVEMENT_VERBS)
    project = random.choice(role_data["projects"])
    impact = random.choice(IMPACT_PHRASES).format(n=random.randint(18, 74))
    scope = random.choice([
        "across cross-functional teams",
        "for internal stakeholders",
        "for a customer-facing product",
        "within a fast-scaling environment",
        "while improving operational visibility",
    ])
    return f"{verb} a {project} initiative that {impact} {scope}."


def build_projects(role_data: dict) -> List[str]:
    items = []
    for project in sample_unique(role_data["projects"], min(3, len(role_data["projects"]))):
        impact = random.choice(IMPACT_PHRASES).format(n=random.randint(20, 68))
        angle = random.choice([
            "through strong execution and clear documentation",
            "using practical prioritization and measurable experimentation",
            "with close stakeholder alignment and iterative delivery",
            "while balancing speed, quality, and maintainability",
        ])
        items.append(f"{project.title()} — {impact} {angle}.")
    return items


def build_experience(role_data: dict, years: int) -> List[str]:
    lines = []
    employer_count = 2 if years < 4 else 3
    used_companies = set()
    for _ in range(employer_count):
        company = random.choice([c for c in COMPANIES if c not in used_companies] or COMPANIES)
        used_companies.add(company)
        title = random.choice(["Engineer", "Specialist", "Associate", "Consultant", "Analyst"])
        lines.append(f"{role_seniority_title(title, years)} at {company}: {build_achievement(role_data, years)}")
    return lines


def generate_resume_profile(
    role: str,
    years: int,
    skill_count: int,
    include_gaps: bool,
    tone: str,
    name_registry: set,
) -> ResumeProfile:
    role_data = ROLE_LIBRARY[role]
    name = generate_name(name_registry)
    city = random.choice(CITIES)

    base_skills = role_data["core_skills"][:]
    random.shuffle(base_skills)
    picked_skills = base_skills[: min(skill_count, len(base_skills))]

    if include_gaps and len(picked_skills) > 4:
        gap_drop = random.choice([1, 2])
        picked_skills = picked_skills[:-gap_drop]

    tools = sample_unique(role_data["tools"], min(random.randint(3, 5), len(role_data["tools"])))
    strengths = sample_unique(SOFT_SKILLS, 3)
    degree = random.choice(["B.Tech", "M.Tech", "B.E.", "MBA", "B.Sc", "MCA"])
    education = f"{degree} — {random.choice(COLLEGES)}"
    certifications = sample_unique(role_data["certs"], min(random.randint(1, 2), len(role_data["certs"])))

    return ResumeProfile(
        name=name,
        role=role_seniority_title(role, years),
        years=years,
        city=city,
        email=make_email(name),
        phone=make_phone(),
        linkedin=f"linkedin.com/in/{name.lower().replace(' ', '-')}",
        github=f"github.com/{name.lower().replace(' ', '')}",
        summary=build_summary(role, years, tone, strengths),
        skills=picked_skills,
        tools=tools,
        strengths=strengths,
        education=education,
        certifications=certifications,
        experience_lines=build_experience(role_data, years),
        projects=build_projects(role_data),
        tone=tone,
    )


def render_resume_text(profile: ResumeProfile) -> str:
    lines = [
        profile.name.upper(),
        profile.role,
        f"{profile.city} | {profile.email} | {profile.phone}",
        f"LinkedIn: {profile.linkedin} | GitHub: {profile.github}",
        "",
        "PROFESSIONAL SUMMARY",
        textwrap.fill(profile.summary, width=92),
        "",
        "CORE SKILLS",
        ", ".join(profile.skills),
        "",
        "TOOLS & PLATFORMS",
        ", ".join(profile.tools),
        "",
        "CAREER HIGHLIGHTS",
    ]
    lines.extend([f"- {item}" for item in profile.experience_lines])
    lines.extend(["", "SELECTED PROJECTS"])
    lines.extend([f"- {item}" for item in profile.projects])
    lines.extend(["", "STRENGTHS"])
    lines.extend([f"- {item.title()}" for item in profile.strengths])
    lines.extend(["", "EDUCATION", profile.education])
    if profile.certifications:
        lines.extend(["", "CERTIFICATIONS"])
        lines.extend([f"- {item}" for item in profile.certifications])
    return "\n".join(lines)


def build_zip(profiles: List[ResumeProfile]) -> bytes:
    mem = io.BytesIO()
    with zipfile.ZipFile(mem, "w", zipfile.ZIP_DEFLATED) as zf:
        for idx, profile in enumerate(profiles, start=1):
            filename = f"{idx:02d}_{profile.name.lower().replace(' ', '_')}.txt"
            zf.writestr(filename, render_resume_text(profile))
    mem.seek(0)
    return mem.read()


def as_dataframe(profiles: List[ResumeProfile]) -> pd.DataFrame:
    rows = []
    for idx, profile in enumerate(profiles, start=1):
        rows.append(
            {
                "No.": idx,
                "Candidate": profile.name,
                "Role": profile.role,
                "Experience": f"{profile.years} yrs",
                "City": profile.city,
                "Tone": profile.tone,
                "Top Skills": ", ".join(profile.skills[:5]),
                "Email": profile.email,
                "LinkedIn": profile.linkedin,
            }
        )
    return pd.DataFrame(rows)


def skill_overlap_percent(profiles: List[ResumeProfile]) -> int:
    if not profiles:
        return 0
    all_skills = [skill for profile in profiles for skill in profile.skills]
    if not all_skills:
        return 0
    unique = len(set(all_skills))
    total = len(all_skills)
    return int(round((1 - unique / total) * 100)) if total else 0


st.markdown(
    """
    <div class="hero">
      <div class="hero-row">
        <div>
          <div class="eyebrow">Synthetic Resume Lab · Demo Data Studio</div>
          <div class="hero-title">Generate polished sample resumes that make your ATS demo feel credible.</div>
          <div class="hero-copy">
            Create realistic recruiter-facing resumes with believable summaries, measured achievements,
            intentional variation, and clean export flows you can immediately plug into your resume ranker.
          </div>
        </div>
        <div class="hero-panel">
          <div class="k">Best for</div>
          <div class="v">Portfolio demos with substance</div>
          <div class="s">
            Instead of random filler text, this generator produces cohesive candidate narratives with
            role-fit signals, strong formatting, and optional gaps that help your ranking logic look sharper.
          </div>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)


tab_generate, tab_preview, tab_about = st.tabs(["Generate", "Preview & Export", "About"])


with st.sidebar:
    st.markdown("## Resume Forge Studio")
    st.markdown("Create premium synthetic resumes for recruiter demos, ATS testing, and shortlist mockups.")
    st.markdown("---")
    selected_role = st.selectbox("Target role", list(ROLE_LIBRARY.keys()), index=0)
    resume_count = st.slider("Number of resumes", 1, 20, 8)
    years_min, years_max = st.select_slider("Experience range", options=list(range(0, 13)), value=(1, 6))
    skill_count = st.slider("Skills per resume", 5, 10, 8)
    tone = st.selectbox("Resume tone", ["Executive", "Modern", "ATS-Friendly", "Ambitious", "Calm & Strategic"], index=0)
    include_gaps = st.toggle("Add intentional skill gaps", value=True)
    random_seed = st.number_input("Random seed", min_value=1, max_value=999999, value=42, step=1)
    generate_btn = st.button("Generate Resume Set", use_container_width=True)


if "generated_profiles" not in st.session_state:
    st.session_state["generated_profiles"] = []


def generate_profiles():
    random.seed(int(random_seed))
    profiles = []
    name_registry = set()
    for _ in range(resume_count):
        years = random.randint(years_min, years_max)
        profiles.append(
            generate_resume_profile(
                role=selected_role,
                years=years,
                skill_count=skill_count,
                include_gaps=include_gaps,
                tone=tone,
                name_registry=name_registry,
            )
        )
    st.session_state["generated_profiles"] = profiles


if generate_btn:
    generate_profiles()


profiles: List[ResumeProfile] = st.session_state.get("generated_profiles", [])


with tab_generate:
    st.markdown(
        f"""
        <div class="ribbon-grid">
          <div class="ribbon">
            <div class="label">Target Role</div>
            <div class="value">{selected_role}</div>
            <div class="sub">Primary candidate profile</div>
          </div>
          <div class="ribbon">
            <div class="label">Batch Size</div>
            <div class="value">{resume_count}</div>
            <div class="sub">Generated resumes per run</div>
          </div>
          <div class="ribbon">
            <div class="label">Experience Window</div>
            <div class="value">{years_min}–{years_max} yrs</div>
            <div class="sub">Range of seniority for demos</div>
          </div>
          <div class="ribbon">
            <div class="label">Narrative Tone</div>
            <div class="value">{tone}</div>
            <div class="sub">How polished each resume sounds</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.25, 1])

    with left:
        st.markdown('<div class="section-shell">', unsafe_allow_html=True)
        st.markdown("## What this generator improves")
        st.markdown(
            """
            - Produces realistic resumes instead of generic placeholder text
            - Balances role fit, skills, tools, projects, and measurable impact
            - Simulates both strong-fit and imperfect candidates for better ranking demos
            - Makes exports presentation-ready for recruiter-facing walkthroughs
            - Helps you generate repeatable test datasets with seed control
            """
        )
        st.markdown(
            '<div class="small-note">Tip: keep the same seed for stable demos, then change the seed to generate a fresh cast of candidates without changing your slider setup.</div>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section-shell">', unsafe_allow_html=True)
        st.markdown("## Suggested demo flows")
        st.markdown(
            """
            - Create one high-fit batch and one gap-heavy batch, then compare ranking quality
            - Use Product Manager or Frontend sets to prove cross-role flexibility
            - Export ZIP files and feed them into your Streamlit or Tkinter ranker
            - Refresh with new seeds to create multiple recruiter-review scenarios
            """
        )
        st.markdown("</div>", unsafe_allow_html=True)


with tab_preview:
    if not profiles:
        st.info("Generate a resume set from the sidebar to preview and export it.")
    else:
        top_skills = Counter()
        for profile in profiles:
            for skill in profile.skills:
                top_skills[skill] += 1

        avg_years = sum(p.years for p in profiles) / len(profiles)
        overlap = skill_overlap_percent(profiles)
        top_skill = top_skills.most_common(1)[0][0] if top_skills else "N/A"

        st.markdown(
            f"""
            <div class="ribbon-grid">
              <div class="ribbon">
                <div class="label">Generated</div>
                <div class="value">{len(profiles)}</div>
                <div class="sub">Recruiter-ready sample resumes</div>
              </div>
              <div class="ribbon">
                <div class="label">Average Experience</div>
                <div class="value">{avg_years:.1f} yrs</div>
                <div class="sub">Across the current batch</div>
              </div>
              <div class="ribbon">
                <div class="label">Most Common Skill</div>
                <div class="value">{top_skill}</div>
                <div class="sub">Useful for parser validation</div>
              </div>
              <div class="ribbon">
                <div class="label">Skill Reuse Level</div>
                <div class="value">{overlap}%</div>
                <div class="sub">Shared-signal intensity across profiles</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        zip_bytes = build_zip(profiles)
        df = as_dataframe(profiles)
        csv_bytes = df.to_csv(index=False).encode("utf-8")

        d1, d2 = st.columns(2)
        with d1:
            st.download_button(
                "Download all resumes as ZIP",
                data=zip_bytes,
                file_name=f"{selected_role.lower().replace(' ', '_')}_resume_set.zip",
                mime="application/zip",
                use_container_width=True,
            )
        with d2:
            st.download_button(
                "Download candidate summary CSV",
                data=csv_bytes,
                file_name=f"{selected_role.lower().replace(' ', '_')}_resume_index.csv",
                mime="text/csv",
                use_container_width=True,
            )

        st.markdown("## Generated resume previews")
        for idx, profile in enumerate(profiles, start=1):
            summary = (
                f"{profile.name} is modeled as a {profile.role.lower()} with {profile.years} years of experience, "
                f"a {profile.tone.lower()} tone, and strong emphasis on {', '.join(profile.skills[:3])}."
            )
            st.markdown(
                f"""
                <div class="resume-card">
                  <div class="resume-head">
                    <div class="resume-name">{profile.name}</div>
                    <div class="resume-role">{profile.role} · {profile.city}</div>
                    <div class="chip-row">
                      <span class="chip emerald">{profile.years} years experience</span>
                      <span class="chip amber">{profile.tone}</span>
                      <span class="chip navy">{selected_role}</span>
                      <span class="chip coral">{'Intentional gaps' if include_gaps else 'Strong-fit profile'}</span>
                    </div>
                  </div>
                  <div class="resume-body">
                    <div class="metric-grid">
                      <div class="metric"><div class="k">Email</div><div class="v">{profile.email}</div></div>
                      <div class="metric"><div class="k">Phone</div><div class="v">{profile.phone}</div></div>
                      <div class="metric"><div class="k">LinkedIn</div><div class="v">{profile.linkedin}</div></div>
                      <div class="metric"><div class="k">Education</div><div class="v">{profile.education.split('—')[0].strip()}</div></div>
                    </div>

                    <div class="summary-box">
                      <strong>Generator note:</strong>
                      <span> {summary}</span>
                    </div>

                    <div><strong>Professional summary</strong></div>
                    <div class="small-note" style="margin-top:0.35rem;">{profile.summary}</div>

                    <div style="margin-top:0.9rem;"><strong>Skill cloud</strong></div>
                    <div>
                      {"".join(f'<span class="skill-pill">{skill}</span>' for skill in profile.skills + profile.tools[:3])}
                    </div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.expander(f"Open full resume text for {profile.name}"):
                resume_text = render_resume_text(profile)
                st.text_area("Resume text", value=resume_text, height=420, key=f"resume_preview_{idx}")
                st.download_button(
                    f"Download {profile.name} resume",
                    data=resume_text.encode("utf-8"),
                    file_name=f"{profile.name.lower().replace(' ', '_')}.txt",
                    mime="text/plain",
                    key=f"dl_{idx}",
                )

        st.markdown("## Candidate index")
        st.dataframe(df, use_container_width=True)


with tab_about:
    st.markdown("## About Resume Forge Studio")
    st.markdown(
        """
        Resume Forge Studio is built to support one specific goal: making your resume-ranking project feel polished in demos, interviews, and portfolio walkthroughs.

        What it does well:
        - Generates cleaner, more believable sample resumes
        - Produces exportable `.txt` files that work naturally with parser-based ranking flows
        - Gives you enough variation to demo shortlist quality, edge cases, and ranking confidence

        Suggested usage:
        1. Run `streamlit run resume_generator.py`
        2. Generate a role-specific batch
        3. Download the ZIP of `.txt` resumes
        4. Feed those files into your ranking project
        5. Show both tools together for a complete recruiter workflow demo
        """
    )
