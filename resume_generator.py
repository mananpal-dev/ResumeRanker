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
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    :root {
        --bg: #f5f1e8;
        --paper: #fffdfa;
        --ink: #1c1a18;
        --muted: #6f665d;
        --line: rgba(28, 26, 24, 0.08);
        --forest: #1f5c4e;
        --bronze: #ad7442;
        --rose: #9d5a52;
        --navy: #25364f;
        --mint: #dff1ea;
        --goldwash: #f8ecda;
        --shadow: 0 20px 60px rgba(40, 34, 28, 0.08);
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(173,116,66,0.14), transparent 22%),
            radial-gradient(circle at top right, rgba(31,92,78,0.12), transparent 20%),
            linear-gradient(180deg, #f8f3eb 0%, #f3eee5 50%, #f7f3ec 100%);
        color: var(--ink);
    }

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: var(--ink);
    }

    h1, h2, h3, h4, .display-title {
        font-family: 'Cormorant Garamond', serif !important;
        color: var(--ink);
        letter-spacing: 0.2px;
    }

    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        max-width: 1380px;
    }

    .hero {
        background:
            linear-gradient(135deg, rgba(255,253,250,0.96), rgba(245,239,229,0.94)),
            linear-gradient(120deg, #fffaf0, #eef3ee);
        border: 1px solid var(--line);
        border-radius: 30px;
        padding: 2.6rem 2.4rem;
        box-shadow: var(--shadow);
        position: relative;
        overflow: hidden;
        margin-bottom: 1.2rem;
    }

    .hero::before {
        content: "";
        position: absolute;
        width: 320px;
        height: 320px;
        right: -80px;
        top: -130px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(31,92,78,0.16), transparent 62%);
    }

    .hero::after {
        content: "";
        position: absolute;
        width: 360px;
        height: 360px;
        left: -100px;
        bottom: -230px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(173,116,66,0.16), transparent 62%);
    }

    .hero-row {
        position: relative;
        z-index: 2;
        display: flex;
        justify-content: space-between;
        gap: 1.6rem;
        flex-wrap: wrap;
        align-items: flex-start;
    }

    .eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        border-radius: 999px;
        background: rgba(31,92,78,0.08);
        color: var(--forest);
        padding: 0.42rem 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-size: 0.76rem;
        font-weight: 800;
    }

    .hero-title {
        margin-top: 0.9rem;
        font-size: 4rem;
        line-height: 0.95;
        max-width: 760px;
    }

    .hero-copy {
        max-width: 720px;
        color: var(--muted);
        font-size: 1rem;
        line-height: 1.75;
        margin-top: 0.8rem;
    }

    .hero-panel {
        width: 290px;
        background: rgba(255,255,255,0.72);
        border: 1px solid var(--line);
        border-radius: 22px;
        padding: 1rem;
        box-shadow: 0 10px 30px rgba(40,34,28,0.05);
    }

    .hero-panel .kicker {
        font-size: 0.75rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: var(--muted);
        font-weight: 800;
    }

    .hero-panel .value {
        margin-top: 0.3rem;
        font-size: 1.8rem;
        font-weight: 800;
    }

    .hero-panel .sub {
        margin-top: 0.35rem;
        color: var(--muted);
        font-size: 0.9rem;
        line-height: 1.6;
    }

    .ribbon-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 1rem;
        margin-bottom: 1.2rem;
    }

    .ribbon {
        background: rgba(255,255,255,0.8);
        border: 1px solid var(--line);
        border-radius: 22px;
        padding: 1rem 1rem 0.9rem;
        box-shadow: 0 12px 32px rgba(40,34,28,0.04);
    }

    .ribbon .label {
        color: var(--muted);
        font-size: 0.74rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 800;
    }

    .ribbon .value {
        margin-top: 0.25rem;
        font-size: 1.55rem;
        font-weight: 800;
    }

    .ribbon .sub {
        color: var(--muted);
        font-size: 0.86rem;
        margin-top: 0.2rem;
    }

    .section-shell {
        background: rgba(255,255,255,0.82);
        border: 1px solid var(--line);
        border-radius: 26px;
        padding: 1.1rem 1.15rem 1.2rem;
        box-shadow: var(--shadow);
    }

    .resume-card {
        background: linear-gradient(180deg, rgba(255,255,255,0.96), rgba(250,247,241,0.96));
        border: 1px solid var(--line);
        border-radius: 24px;
        box-shadow: var(--shadow);
        overflow: hidden;
        margin-bottom: 1rem;
    }

    .resume-head {
        padding: 1.2rem 1.25rem 0.8rem;
        border-bottom: 1px solid var(--line);
        background: linear-gradient(120deg, rgba(223,241,234,0.65), rgba(248,236,218,0.68));
    }

    .resume-name {
        font-size: 1.65rem;
        font-weight: 800;
        color: var(--ink);
    }

    .resume-role {
        margin-top: 0.2rem;
        color: var(--muted);
        font-size: 0.96rem;
    }

    .chip-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.45rem;
        margin-top: 0.75rem;
    }

    .chip {
        border-radius: 999px;
        padding: 0.38rem 0.74rem;
        font-size: 0.76rem;
        font-weight: 700;
        border: 1px solid transparent;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    .chip.forest { background: #e1f1ec; color: #1f5c4e; border-color: #c8e4db; }
    .chip.gold { background: #faeedc; color: #9a6232; border-color: #eed4af; }
    .chip.rose { background: #f4e3e0; color: #914e47; border-color: #e6c5bf; }
    .chip.navy { background: #e5ebf4; color: #304463; border-color: #d2dcea; }

    .resume-body {
        padding: 1rem 1.25rem 1.2rem;
    }

    .metric-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 0.8rem;
        margin-bottom: 0.9rem;
    }

    .metric {
        background: rgba(247,243,234,0.9);
        border: 1px solid rgba(28,26,24,0.05);
        border-radius: 18px;
        padding: 0.8rem;
    }

    .metric .k {
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 800;
        color: var(--muted);
    }

    .metric .v {
        margin-top: 0.28rem;
        font-size: 1.05rem;
        font-weight: 800;
        color: var(--ink);
    }

    .summary-box {
        background: linear-gradient(90deg, #1f5c4e, #314f4c);
        color: #fffdf9;
        border-radius: 18px;
        padding: 0.95rem 1rem;
        margin: 0.85rem 0;
    }

    .summary-box strong {
        color: white;
    }

    .summary-box span {
        color: rgba(255,255,255,0.82);
        font-size: 0.92rem;
    }

    .skill-cloud {
        margin-top: 0.3rem;
    }

    .skill-pill {
        display: inline-block;
        padding: 0.3rem 0.7rem;
        border-radius: 999px;
        background: #f1f5f9;
        color: #334155;
        border: 1px solid rgba(51,65,85,0.10);
        margin: 0.18rem;
        font-size: 0.76rem;
        font-weight: 600;
    }

    .small-note {
        color: var(--muted);
        font-size: 0.88rem;
        line-height: 1.6;
    }

    .stButton > button, .stDownloadButton > button {
        border-radius: 14px;
        border: 1px solid rgba(28,26,24,0.08);
        background: linear-gradient(135deg, #1c1a18, #36574f);
        color: white;
        font-weight: 800;
        box-shadow: 0 12px 28px rgba(28,26,24,0.10);
    }

    .stTabs [data-baseweb="tab"] {
        background: rgba(255,255,255,0.72);
        border: 1px solid var(--line);
        border-radius: 14px;
        font-weight: 800;
        padding: 0.5rem 0.9rem;
    }

    .stTabs [aria-selected="true"] {
        background: #1c1a18 !important;
        color: #fffdf9 !important;
    }

    [data-testid="stSidebar"] {
        background:
            radial-gradient(circle at top right, rgba(173,116,66,0.18), transparent 28%),
            linear-gradient(180deg, #1f2623 0%, #2d3734 60%, #35403d 100%);
    }

    [data-testid="stSidebar"] * {
        color: #f7f3ec !important;
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
    "Dhruv", "Siya", "Yash", "Ritika", "Kunal", "Prisha", "Neil", "Rhea"
]
LAST_NAMES = [
    "Sharma", "Reddy", "Patel", "Malhotra", "Verma", "Kapoor", "Nair", "Joshi",
    "Mehta", "Bose", "Chauhan", "Sethi", "Iyer", "Bhatia", "Khanna", "Rao",
    "Menon", "Singh", "Agarwal", "Mishra", "Pillai", "Desai", "Bansal", "Saxena"
]
COMPANIES = [
    "NovaGrid", "Verity Labs", "BlueOrbit", "Northscale", "MintBridge",
    "AetherWorks", "CrestIQ", "LatticeFox", "BrightLayer", "CloudSpire",
    "PixelHarbor", "QuantNest"
]
COLLEGES = [
    "IIT Delhi", "BITS Pilani", "NIT Trichy", "VIT Vellore",
    "Delhi Technological University", "PES University",
    "SRM Institute of Science and Technology", "Manipal Institute of Technology"
]
CITIES = ["Bengaluru", "Hyderabad", "Pune", "Chennai", "Gurugram", "Noida", "Mumbai", "Kochi", "Ahmedabad"]
SOFT_SKILLS = [
    "clear stakeholder communication", "ownership mindset", "cross-functional collaboration",
    "structured problem solving", "fast execution", "mentoring ability",
    "product thinking", "documentation discipline", "decision-making under ambiguity"
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
    name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)} {random.randint(1,999)}"
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


st.markdown(
    """
    <div class="hero">
      <div class="hero-row">
        <div>
          <div class="eyebrow">Synthetic Resume Lab · Premium Demo Generator</div>
          <div class="hero-title">Generate recruiter-grade sample resumes that make your project look serious.</div>
          <div class="hero-copy">
            Build realistic test resumes in one click, vary role fit and seniority, and export polished `.txt`
            profiles you can feed straight into your ranking or ATS-style screening workflow.
          </div>
        </div>
        <div class="hero-panel">
          <div class="kicker">Best use case</div>
          <div class="value">Project demos that feel premium</div>
          <div class="sub">
            Create believable resumes with strong summaries, measurable achievements, clean formatting,
            and optional skill gaps so your testing looks intentional instead of random.
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
    st.markdown("Create polished synthetic resumes for demos, ATS testing, and recruiter mock reviews.")
    st.markdown("---")
    selected_role = st.selectbox("Target role", list(ROLE_LIBRARY.keys()), index=0)
    resume_count = st.slider("Number of resumes", 1, 20, 6)
    years_min, years_max = st.select_slider(
        "Experience range",
        options=list(range(0, 13)),
        value=(1, 6),
    )
    skill_count = st.slider("Skills per resume", 5, 10, 8)
    tone = st.selectbox("Resume tone", ["Executive", "Modern", "ATS-Friendly", "Ambitious", "Calm & Strategic"], index=0)
    include_gaps = st.toggle("Add small intentional skill gaps", value=True)
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
            <div class="sub">Primary simulation profile</div>
          </div>
          <div class="ribbon">
            <div class="label">Batch Size</div>
            <div class="value">{resume_count}</div>
            <div class="sub">Auto-generated resumes</div>
          </div>
          <div class="ribbon">
            <div class="label">Experience Window</div>
            <div class="value">{years_min}–{years_max} yrs</div>
            <div class="sub">Seniority variety for testing</div>
          </div>
          <div class="ribbon">
            <div class="label">Quality Mode</div>
            <div class="value">{tone}</div>
            <div class="sub">Presentation and summary style</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_a, col_b = st.columns([1.3, 1])

    with col_a:
        st.markdown('<div class="section-shell">', unsafe_allow_html=True)
        st.markdown("## What this generator does")
        st.markdown(
            """
            - Creates realistic synthetic resumes for your chosen role
            - Varies names, experience, tools, strengths, and project bullets
            - Adds measurable achievements so the output looks intentional
            - Lets you simulate imperfect candidates with small skill gaps
            - Exports `.txt` resumes ready for ranking-project testing
            """
        )
        st.markdown(
            '<div class="small-note">Tip: change the random seed whenever you want a fresh batch. Same seed = repeatable output, new seed = new names and new resumes.</div>',
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="section-shell">', unsafe_allow_html=True)
        st.markdown("## Demo ideas")
        st.markdown(
            """
            - Generate 10 resumes for one role and test ranking quality
            - Compare strong-fit vs partial-fit candidates
            - Stress-test export flows and parsing quality
            - Use multiple seeds to create fresh demo datasets quickly
            """
        )
        st.markdown('</div>', unsafe_allow_html=True)


with tab_preview:
    if not profiles:
        st.info("Generate a resume set from the sidebar to preview and export it.")
    else:
        top_skills = Counter()
        for profile in profiles:
            for skill in profile.skills:
                top_skills[skill] += 1

        st.markdown(
            f"""
            <div class="ribbon-grid">
              <div class="ribbon">
                <div class="label">Generated</div>
                <div class="value">{len(profiles)}</div>
                <div class="sub">Ready-to-export resumes</div>
              </div>
              <div class="ribbon">
                <div class="label">Average Experience</div>
                <div class="value">{sum(p.years for p in profiles)/len(profiles):.1f} yrs</div>
                <div class="sub">Across current batch</div>
              </div>
              <div class="ribbon">
                <div class="label">Most Common Skill</div>
                <div class="value">{top_skills.most_common(1)[0][0] if top_skills else "N/A"}</div>
                <div class="sub">Best for parser testing</div>
              </div>
              <div class="ribbon">
                <div class="label">Gap Mode</div>
                <div class="value">{"Enabled" if include_gaps else "Disabled"}</div>
                <div class="sub">Candidate realism setting</div>
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
                      <span class="chip forest">{profile.years} years experience</span>
                      <span class="chip gold">{profile.tone}</span>
                      <span class="chip navy">{selected_role}</span>
                      <span class="chip rose">{'Intentional gaps' if include_gaps else 'Strong-fit profile'}</span>
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
                    <div class="skill-cloud">
                      {"".join(f'<span class="skill-pill">{skill}</span>' for skill in profile.skills + profile.tools[:3])}
                    </div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.expander(f"Open full resume text for {profile.name}"):
                resume_text = render_resume_text(profile)
                st.text_area(
                    "Resume text",
                    value=resume_text,
                    height=420,
                    key=f"resume_preview_{idx}",
                )
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
        This file is a synthetic resume generator made to help you test and demo a resume ranking or ATS-style project.

        It is designed to impress in two ways:
        - The generated resumes look more realistic than filler data
        - The frontend feels premium and presentation-ready for interviews or portfolio demos

        Suggested usage:
        1. Run `streamlit run resume_generator.py`
        2. Generate a batch for a target role
        3. Export the ZIP of `.txt` resumes
        4. Feed those files into your ranking project
        5. Show both apps together in your demo
        """
    )
