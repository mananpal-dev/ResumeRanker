# ============================================================
#   utils/exporter.py  –  CSV / JSON / TXT report exporters
# ============================================================

import csv
import json
import os
from datetime import datetime
from typing import List

from utils.ranker import CandidateResult, compute_summary


# ── CSV export ────────────────────────────────────────────────
def export_csv(results: List[CandidateResult], path: str = "ranked_resumes.csv"):
    fieldnames = [
        "Rank", "Filename", "Name", "Email", "Phone",
        "Final Score", "TF-IDF Score", "Keyword Score",
        "Seniority", "Education", "Experience (yrs)",
        "Status", "Skill Coverage %",
        "Matched Skills", "Missing Skills",
        "LinkedIn", "GitHub"
    ]
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow({
                "Rank":              r.rank,
                "Filename":         r.filename,
                "Name":             r.name,
                "Email":            r.email,
                "Phone":            r.phone,
                "Final Score":      f"{r.final_score:.4f}",
                "TF-IDF Score":     f"{r.tfidf_score:.4f}",
                "Keyword Score":    f"{r.keyword_score:.4f}",
                "Seniority":        r.seniority,
                "Education":        r.education,
                "Experience (yrs)": r.experience_years,
                "Status":           r.status,
                "Skill Coverage %": r.skill_coverage,
                "Matched Skills":   ", ".join(r.all_skills_flat),
                "Missing Skills":   ", ".join(r.missing_skills),
                "LinkedIn":         r.linkedin,
                "GitHub":           r.github,
            })
    return path


# ── JSON export ───────────────────────────────────────────────
def export_json(results: List[CandidateResult], summary: dict, path: str = "ranking_results.json"):
    data = {
        "generated_at": datetime.now().isoformat(),
        "summary":      summary,
        "candidates":   []
    }
    for r in results:
        data["candidates"].append({
            "rank":           r.rank,
            "filename":       r.filename,
            "name":           r.name,
            "email":          r.email,
            "phone":          r.phone,
            "linkedin":       r.linkedin,
            "github":         r.github,
            "scores": {
                "final":      r.final_score,
                "tfidf":      r.tfidf_score,
                "keyword":    r.keyword_score,
                "seniority":  r.seniority_score,
                "education":  r.education_score,
            },
            "status":          r.status,
            "seniority":       r.seniority,
            "education":       r.education,
            "experience_years": r.experience_years,
            "skill_coverage":   r.skill_coverage,
            "matched_skills":   r.matched_skills,
            "missing_skills":   r.missing_skills,
        })
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    return path


# ── Plain-text report ─────────────────────────────────────────
def export_txt_report(
    results: List[CandidateResult],
    summary: dict,
    jd_text: str,
    path: str = "ranking_report.txt"
):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sep = "=" * 70
    lines = [
        sep,
        f"  AI RESUME RANKER  v2.0  |  Report generated: {now}",
        sep,
        "",
        "── JOB DESCRIPTION SNIPPET ──────────────────────────────────",
        jd_text[:400].strip() + ("..." if len(jd_text) > 400 else ""),
        "",
        "── SUMMARY ──────────────────────────────────────────────────",
        f"  Total candidates   : {summary.get('total', 0)}",
        f"  ✅ Shortlisted      : {summary.get('shortlisted', 0)}",
        f"  🤔 Maybe            : {summary.get('maybe', 0)}",
        f"  ❌ Not Relevant     : {summary.get('not_relevant', 0)}",
        f"  Average score      : {summary.get('avg_score', 0):.4f}",
        f"  Top score          : {summary.get('top_score', 0):.4f}",
        f"  Top candidate      : {summary.get('top_candidate', '')}",
        "",
        "── RANKED CANDIDATES ────────────────────────────────────────",
    ]

    for r in results:
        lines += [
            "",
            f"  #{r.rank}  {r.filename}",
            f"      Status   : {r.status}",
            f"      Score    : {r.final_score:.4f}  (TF-IDF={r.tfidf_score:.3f} | KW={r.keyword_score:.3f})",
            f"      Seniority: {r.seniority}  |  Education: {r.education}  |  Exp: {r.experience_years}yr",
            f"      Skills   : {', '.join(r.all_skills_flat) or 'None detected'}",
            f"      Missing  : {', '.join(r.missing_skills[:5]) or 'None'}",
            f"      Coverage : {r.skill_coverage}%",
        ]
        if r.email:
            lines.append(f"      Email    : {r.email}")
        if r.linkedin:
            lines.append(f"      LinkedIn : {r.linkedin}")

    lines += ["", sep, "  END OF REPORT", sep]

    with open(path, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))
    return path
