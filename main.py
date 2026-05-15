# ============================================================
#   main.py  –  Tkinter Desktop App  |  AI Resume Ranker v4.0
#   Run:  python main.py
# ============================================================

import os
import sys
import threading
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk

sys.path.insert(0, os.path.dirname(__file__))

from config import (
    APP_AUTHOR,
    APP_NAME,
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
    SKILL_GROUPS,
)
from utils.exporter import export_csv, export_json, export_txt_report
from utils.ranker import CandidateResult, compute_summary, rank_resumes


# ── Palette ──────────────────────────────────────────────────
MIDNIGHT = "#0e141f"
MIDNIGHT_2 = "#121b29"
SLATE = "#162235"
SLATE_2 = "#1c2a3f"
CARD = "#f6f1e8"
CARD_2 = "#fffaf3"
BORDER = "#d8cfbf"
TEXT = "#1b2736"
MUTED = "#657184"
MUTED_2 = "#8a95a5"
ACCENT = "#0f766e"
ACCENT_2 = "#17a398"
GOLD = "#c7922b"
ROSE = "#b45454"
SAND = "#efe7d8"
WHITE = "#ffffff"
SHORTLIST = "#1e8e63"
MAYBE = "#b7791f"
REJECT = "#c05656"
INK_ON_DARK = "#f3f6fb"

FONT_UI = ("Segoe UI", 10)
FONT_UI_B = ("Segoe UI Semibold", 10)
FONT_UI_XL = ("Georgia", 24, "bold")
FONT_UI_H = ("Segoe UI Semibold", 12)
FONT_UI_SM = ("Segoe UI", 9)
FONT_MONO = ("Consolas", 10)
FONT_MONO_SM = ("Consolas", 9)


def safe_ratio(score: float) -> str:
    return f"{int(round(score * 100))}%"


def get_priority_label(r: CandidateResult) -> str:
    if (
        r.final_score >= PRIORITY_HIGH_SCORE
        and r.skill_coverage >= PRIORITY_HIGH_COVERAGE
        and r.experience_years >= PRIORITY_HIGH_EXP
    ):
        return "High Priority"
    if (
        r.final_score >= PRIORITY_MEDIUM_SCORE
        and r.skill_coverage >= PRIORITY_MEDIUM_COVERAGE
    ):
        return "Strong Review"
    if r.final_score >= MAYBE_THRESHOLD:
        return "Hold for Review"
    return "Low Priority"


def get_interview_readiness(r: CandidateResult) -> str:
    if r.status == "Shortlisted" and r.final_score >= INTERVIEW_READY_SCORE:
        return "Ready now"
    if r.status == "Maybe":
        return "Needs review"
    return "Not ready"


def get_recommended_action(r: CandidateResult) -> str:
    if r.status == "Shortlisted" and r.final_score >= 0.80:
        return "Recruiter screen"
    if r.status == "Shortlisted":
        return "Hiring manager"
    if r.status == "Maybe":
        return "Backup pipeline"
    return "Archive"


def get_contact_completeness(r: CandidateResult) -> str:
    fields = [r.email, r.phone, r.linkedin, r.github]
    filled = sum(1 for field in fields if field and str(field).strip())
    return f"{filled}/4"


class MetricCard(tk.Frame):
    def __init__(self, parent, label: str, value_var: tk.StringVar, tint: str):
        super().__init__(parent, bg=CARD_2, highlightbackground=BORDER, highlightthickness=1)
        tk.Label(self, text=label, bg=CARD_2, fg=MUTED, font=("Segoe UI", 8, "bold")).pack(
            anchor=tk.W, padx=12, pady=(10, 2)
        )
        tk.Label(self, textvariable=value_var, bg=CARD_2, fg=tint, font=("Georgia", 20, "bold")).pack(
            anchor=tk.W, padx=12, pady=(0, 10)
        )


class ResumeRankerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry("1420x900")
        self.root.minsize(1120, 760)
        self.root.configure(bg=MIDNIGHT)

        self.selected_folder = None
        self.selected_jd = None
        self.jd_text = ""
        self.results = []
        self.summary = {}
        self._sort_reverse = {}
        self._recruiter_notes = {}
        self._recruiter_decisions = {}

        # All tk variables are created after tk.Tk() exists.
        self.top_n_var = tk.IntVar(value=12)
        self.filter_var = tk.StringVar(value="All")
        self.search_var = tk.StringVar(value="")
        self.status_var = tk.StringVar(value="Command center ready")

        self.metric_vars = {
            "total": tk.StringVar(value="0"),
            "shortlisted": tk.StringVar(value="0"),
            "high_priority": tk.StringVar(value="0"),
            "avg_score": tk.StringVar(value="0%"),
            "top_candidate": tk.StringVar(value="—"),
        }

        self._configure_styles()
        self._build_ui()

    # ───────────────────────────────────────────────────────
    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Shell.Treeview",
            background=CARD_2,
            foreground=TEXT,
            fieldbackground=CARD_2,
            bordercolor=BORDER,
            borderwidth=0,
            rowheight=30,
            font=FONT_UI_SM,
        )
        style.configure(
            "Shell.Treeview.Heading",
            background=SAND,
            foreground=TEXT,
            font=("Segoe UI Semibold", 9),
            relief=tk.FLAT,
            borderwidth=0,
        )
        style.map(
            "Shell.Treeview",
            background=[("selected", "#dcefe9")],
            foreground=[("selected", TEXT)],
        )
        style.configure(
            "Accent.Horizontal.TProgressbar",
            troughcolor=SLATE,
            background=ACCENT_2,
            borderwidth=0,
            thickness=6,
        )

    # ───────────────────────────────────────────────────────
    def _build_ui(self):
        self._build_header()

        shell = tk.Frame(self.root, bg=MIDNIGHT)
        shell.pack(fill=tk.BOTH, expand=True, padx=18, pady=(0, 18))

        sidebar = tk.Frame(shell, bg=SLATE, width=310)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        content = tk.Frame(shell, bg=MIDNIGHT)
        content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(16, 0))

        self._build_sidebar(sidebar)
        self._build_content(content)

    def _build_header(self):
        header = tk.Frame(self.root, bg=MIDNIGHT_2, height=112)
        header.pack(fill=tk.X, padx=18, pady=18)
        header.pack_propagate(False)

        left = tk.Frame(header, bg=MIDNIGHT_2)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=18, pady=14)

        tk.Label(
            left,
            text="Recruiter Command Center",
            font=FONT_UI_XL,
            bg=MIDNIGHT_2,
            fg=WHITE,
        ).pack(anchor=tk.W)
        tk.Label(
            left,
            text=f"{APP_NAME} v{APP_VERSION}  |  desktop review cockpit  |  {APP_AUTHOR}",
            font=FONT_UI,
            bg=MIDNIGHT_2,
            fg=MUTED_2,
        ).pack(anchor=tk.W, pady=(4, 0))
        tk.Label(
            left,
            textvariable=self.status_var,
            font=FONT_UI_SM,
            bg=MIDNIGHT_2,
            fg="#9cd7cf",
        ).pack(anchor=tk.W, pady=(8, 0))

        right = tk.Frame(header, bg=MIDNIGHT_2)
        right.pack(side=tk.RIGHT, padx=18, pady=14)

        for key, label, tint in [
            ("total", "Candidates", WHITE),
            ("shortlisted", "Shortlisted", "#9de7c7"),
            ("high_priority", "Priority", "#f5ce72"),
            ("avg_score", "Avg Match", "#83d9d0"),
        ]:
            card = tk.Frame(right, bg=SLATE, width=155, height=72, highlightbackground="#20314a", highlightthickness=1)
            card.pack(side=tk.LEFT, padx=6)
            card.pack_propagate(False)
            tk.Label(card, text=label, bg=SLATE, fg=MUTED_2, font=("Segoe UI", 8, "bold")).pack(anchor=tk.W, padx=12, pady=(11, 2))
            tk.Label(card, textvariable=self.metric_vars[key], bg=SLATE, fg=tint, font=("Georgia", 18, "bold")).pack(anchor=tk.W, padx=12)

    # ───────────────────────────────────────────────────────
    def _build_sidebar(self, parent):
        tk.Frame(parent, bg=ACCENT, height=4).pack(fill=tk.X)
        body = tk.Frame(parent, bg=SLATE)
        body.pack(fill=tk.BOTH, expand=True, padx=18, pady=18)

        tk.Label(body, text="Hiring Setup", bg=SLATE, fg=WHITE, font=("Georgia", 18, "bold")).pack(anchor=tk.W)
        tk.Label(
            body,
            text="Load the job brief, point to a resume folder, then generate a recruiter-ready slate.",
            bg=SLATE,
            fg=MUTED_2,
            font=FONT_UI,
            wraplength=250,
            justify=tk.LEFT,
        ).pack(anchor=tk.W, pady=(6, 18))

        self._section_label(body, "Inputs")
        self._action_button(body, "Select Resume Folder", self._choose_folder, ACCENT, WHITE)
        self.folder_label = self._hint_label(body, "No folder selected")

        self._action_button(body, "Select Job Description", self._choose_jd, WHITE, TEXT)
        self.jd_label = self._hint_label(body, "No JD selected")

        self._section_label(body, "Display")
        tk.Label(body, text="Visible candidates", bg=SLATE, fg=MUTED_2, font=FONT_UI_SM).pack(anchor=tk.W)
        spin_shell = tk.Frame(body, bg=MIDNIGHT_2, highlightbackground="#233550", highlightthickness=1)
        spin_shell.pack(fill=tk.X, pady=(6, 14))
        tk.Spinbox(
            spin_shell,
            from_=5,
            to=100,
            textvariable=self.top_n_var,
            width=8,
            bg=MIDNIGHT_2,
            fg=WHITE,
            insertbackground=WHITE,
            relief=tk.FLAT,
            font=FONT_MONO,
            buttonbackground=SLATE_2,
            command=self._refresh_results,
        ).pack(padx=10, pady=8, anchor=tk.W)

        tk.Label(body, text="Quick search", bg=SLATE, fg=MUTED_2, font=FONT_UI_SM).pack(anchor=tk.W)
        search_entry = tk.Entry(
            body,
            textvariable=self.search_var,
            bg=MIDNIGHT_2,
            fg=WHITE,
            insertbackground=WHITE,
            relief=tk.FLAT,
            font=FONT_UI,
        )
        search_entry.pack(fill=tk.X, pady=(6, 6), ipady=8)
        search_entry.bind("<KeyRelease>", lambda _e: self._refresh_results())

        tk.Label(body, text="Status filter", bg=SLATE, fg=MUTED_2, font=FONT_UI_SM).pack(anchor=tk.W, pady=(8, 6))
        filter_shell = tk.Frame(body, bg=SLATE)
        filter_shell.pack(fill=tk.X)
        for label in ["All", "Shortlisted", "Maybe", "Not Relevant"]:
            tk.Radiobutton(
                filter_shell,
                text=label,
                value=label,
                variable=self.filter_var,
                command=self._refresh_results,
                bg=SLATE,
                fg=WHITE,
                activebackground=SLATE,
                activeforeground=WHITE,
                selectcolor=MIDNIGHT_2,
                font=FONT_UI_SM,
                anchor=tk.W,
            ).pack(anchor=tk.W)

        self._section_label(body, "Run")
        self.run_btn = tk.Button(
            body,
            text="Start Ranking",
            font=FONT_UI_B,
            bg=GOLD,
            fg=TEXT,
            relief=tk.FLAT,
            cursor="hand2",
            pady=10,
            command=self._start_ranking,
        )
        self.run_btn.pack(fill=tk.X, pady=(2, 8))

        self.progress = ttk.Progressbar(body, mode="determinate", style="Accent.Horizontal.TProgressbar")
        self.progress.pack(fill=tk.X, pady=(0, 6))
        self.status_label = tk.Label(body, text="Waiting for input", bg=SLATE, fg=MUTED_2, font=FONT_MONO_SM)
        self.status_label.pack(anchor=tk.W)

        self._section_label(body, "Export")
        self._soft_button(body, "Export CSV", self._export_csv)
        self._soft_button(body, "Export JSON", self._export_json)
        self._soft_button(body, "Export TXT Report", self._export_txt)

        tk.Frame(body, bg=SLATE).pack(expand=True, fill=tk.BOTH)

    # ───────────────────────────────────────────────────────
    def _build_content(self, parent):
        top_strip = tk.Frame(parent, bg=MIDNIGHT)
        top_strip.pack(fill=tk.X, pady=(0, 14))

        spotlight = tk.Frame(top_strip, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        spotlight.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Label(spotlight, text="Top Candidate Spotlight", bg=CARD, fg=TEXT, font=("Georgia", 18, "bold")).pack(
            anchor=tk.W, padx=18, pady=(14, 2)
        )
        tk.Label(
            spotlight,
            textvariable=self.metric_vars["top_candidate"],
            bg=CARD,
            fg=ACCENT,
            font=("Segoe UI Semibold", 11),
        ).pack(anchor=tk.W, padx=18, pady=(0, 6))
        self.hero_note = tk.Label(
            spotlight,
            text="Run a ranking pass to generate recruiter guidance and shortlist highlights.",
            bg=CARD,
            fg=MUTED,
            font=FONT_UI,
            wraplength=760,
            justify=tk.LEFT,
        )
        self.hero_note.pack(anchor=tk.W, padx=18, pady=(0, 14))

        metrics_shell = tk.Frame(parent, bg=MIDNIGHT)
        metrics_shell.pack(fill=tk.X, pady=(0, 14))
        for key, label, tint in [
            ("total", "Total Candidates", TEXT),
            ("shortlisted", "Shortlisted", SHORTLIST),
            ("high_priority", "High Priority", GOLD),
            ("avg_score", "Average Match", ACCENT),
        ]:
            card = MetricCard(metrics_shell, label, self.metric_vars[key], tint)
            card.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        self.tab_bar = tk.Frame(parent, bg=MIDNIGHT)
        self.tab_bar.pack(fill=tk.X, pady=(0, 10))

        self.content_frame = tk.Frame(parent, bg=MIDNIGHT)
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        self.tab_rankings = tk.Frame(self.content_frame, bg=MIDNIGHT)
        self.tab_summary = tk.Frame(self.content_frame, bg=MIDNIGHT)
        self.tab_recruiter = tk.Frame(self.content_frame, bg=MIDNIGHT)
        self.tab_skills = tk.Frame(self.content_frame, bg=MIDNIGHT)

        self._build_rankings_tab(self.tab_rankings)
        self._build_summary_tab(self.tab_summary)
        self._build_recruiter_tab(self.tab_recruiter)
        self._build_skills_tab(self.tab_skills)

        self._tab_btns = {}
        for key, label, frame in [
            ("rankings", "Candidate Slate", self.tab_rankings),
            ("summary", "Executive Summary", self.tab_summary),
            ("recruiter", "Recruiter Log", self.tab_recruiter),
            ("skills", "Skill Coverage", self.tab_skills),
        ]:
            btn = tk.Button(
                self.tab_bar,
                text=label,
                font=FONT_UI_B,
                bg=SLATE,
                fg=WHITE,
                relief=tk.FLAT,
                cursor="hand2",
                padx=16,
                pady=9,
                command=lambda k=key, f=frame: self._switch_tab(k, f),
            )
            btn.pack(side=tk.LEFT, padx=(0, 8))
            self._tab_btns[key] = btn

        self._switch_tab("rankings", self.tab_rankings)

    def _switch_tab(self, key, frame):
        for panel in [self.tab_rankings, self.tab_summary, self.tab_recruiter, self.tab_skills]:
            panel.pack_forget()
        frame.pack(fill=tk.BOTH, expand=True)
        for name, btn in self._tab_btns.items():
            btn.config(bg=(GOLD if name == key else SLATE), fg=(TEXT if name == key else WHITE))

    # ───────────────────────────────────────────────────────
    def _build_rankings_tab(self, parent):
        shell = tk.Frame(parent, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        shell.pack(fill=tk.BOTH, expand=True)

        head = tk.Frame(shell, bg=CARD)
        head.pack(fill=tk.X, padx=16, pady=(14, 8))
        tk.Label(head, text="Candidate Slate", bg=CARD, fg=TEXT, font=("Georgia", 18, "bold")).pack(side=tk.LEFT)
        tk.Label(
            head,
            text="Double-click a row to open the full recruiter review card.",
            bg=CARD,
            fg=MUTED,
            font=FONT_UI_SM,
        ).pack(side=tk.RIGHT)

        cols = (
            "Rank", "Candidate", "Score", "Coverage", "Status", "Priority",
            "Readiness", "Action", "Experience", "Seniority", "Education", "Skills"
        )
        tree_area = tk.Frame(shell, bg=CARD)
        tree_area.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 12))

        self.tree = ttk.Treeview(tree_area, columns=cols, show="headings", style="Shell.Treeview")
        widths = [58, 190, 72, 76, 100, 110, 98, 118, 78, 92, 118, 260]
        for col, width in zip(cols, widths):
            self.tree.heading(col, text=col, command=lambda c=col: self._sort_tree(c))
            anchor = tk.W if col in {"Candidate", "Education", "Skills"} else tk.CENTER
            self.tree.column(col, width=width, minwidth=50, anchor=anchor)

        self.tree.tag_configure("Shortlisted", background="#edf8f4", foreground=TEXT)
        self.tree.tag_configure("Maybe", background="#fff6e7", foreground=TEXT)
        self.tree.tag_configure("Not Relevant", background="#fbeceb", foreground=TEXT)

        y_scroll = ttk.Scrollbar(tree_area, orient="vertical", command=self.tree.yview)
        x_scroll = ttk.Scrollbar(tree_area, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.bind("<Double-Button-1>", self._show_detail)

    # ───────────────────────────────────────────────────────
    def _build_summary_tab(self, parent):
        shell = tk.Frame(parent, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        shell.pack(fill=tk.BOTH, expand=True)

        tk.Label(shell, text="Executive Summary", bg=CARD, fg=TEXT, font=("Georgia", 18, "bold")).pack(
            anchor=tk.W, padx=18, pady=(14, 8)
        )
        self.summary_text = tk.Text(
            shell,
            bg=CARD,
            fg=TEXT,
            font=FONT_UI,
            relief=tk.FLAT,
            wrap=tk.WORD,
            padx=18,
            pady=8,
            insertbackground=TEXT,
            selectbackground="#d7ebe6",
        )
        self.summary_text.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 10))
        self.summary_text.tag_configure("h1", foreground=TEXT, font=("Georgia", 16, "bold"))
        self.summary_text.tag_configure("h2", foreground=ACCENT, font=("Segoe UI Semibold", 11))
        self.summary_text.tag_configure("muted", foreground=MUTED)
        self.summary_text.tag_configure("ok", foreground=SHORTLIST)
        self.summary_text.tag_configure("warn", foreground=MAYBE)
        self.summary_text.tag_configure("risk", foreground=REJECT)
        self.summary_text.tag_configure("strong", foreground=TEXT, font=("Segoe UI Semibold", 10))

    # ───────────────────────────────────────────────────────
    def _build_recruiter_tab(self, parent):
        shell = tk.Frame(parent, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        shell.pack(fill=tk.BOTH, expand=True)

        tk.Label(shell, text="Recruiter Log", bg=CARD, fg=TEXT, font=("Georgia", 18, "bold")).pack(
            anchor=tk.W, padx=18, pady=(14, 8)
        )
        tk.Label(
            shell,
            text="Double-click a row to set recruiter notes and a final decision.",
            bg=CARD,
            fg=MUTED,
            font=FONT_UI_SM,
        ).pack(anchor=tk.W, padx=18, pady=(0, 8))

        cols = ("Rank", "Candidate", "Status", "Priority", "Readiness", "Action", "Score", "Exp", "Contact", "Decision", "Notes")
        area = tk.Frame(shell, bg=CARD)
        area.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 12))

        self.rec_tree = ttk.Treeview(area, columns=cols, show="headings", style="Shell.Treeview")
        widths = [58, 190, 100, 110, 92, 120, 72, 58, 68, 150, 270]
        for col, width in zip(cols, widths):
            self.rec_tree.heading(col, text=col)
            anchor = tk.W if col in {"Candidate", "Notes"} else tk.CENTER
            self.rec_tree.column(col, width=width, minwidth=50, anchor=anchor)
        self.rec_tree.tag_configure("Shortlisted", background="#edf8f4", foreground=TEXT)
        self.rec_tree.tag_configure("Maybe", background="#fff6e7", foreground=TEXT)
        self.rec_tree.tag_configure("Not Relevant", background="#fbeceb", foreground=TEXT)

        y_scroll = ttk.Scrollbar(area, orient="vertical", command=self.rec_tree.yview)
        x_scroll = ttk.Scrollbar(area, orient="horizontal", command=self.rec_tree.xview)
        self.rec_tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        self.rec_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.rec_tree.bind("<Double-Button-1>", self._open_recruiter_notes)

    # ───────────────────────────────────────────────────────
    def _build_skills_tab(self, parent):
        shell = tk.Frame(parent, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        shell.pack(fill=tk.BOTH, expand=True)

        tk.Label(shell, text="Skill Coverage Map", bg=CARD, fg=TEXT, font=("Georgia", 18, "bold")).pack(
            anchor=tk.W, padx=18, pady=(14, 8)
        )
        self.skills_text = tk.Text(
            shell,
            bg=CARD,
            fg=TEXT,
            font=FONT_MONO,
            relief=tk.FLAT,
            wrap=tk.WORD,
            padx=18,
            pady=8,
            selectbackground="#d7ebe6",
        )
        self.skills_text.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 10))
        self.skills_text.tag_configure("h1", foreground=TEXT, font=("Georgia", 16, "bold"))
        self.skills_text.tag_configure("group", foreground=ACCENT, font=("Segoe UI Semibold", 10))
        self.skills_text.tag_configure("count", foreground=GOLD)
        self.skills_text.tag_configure("bar", foreground=ACCENT)
        self.skills_text.tag_configure("muted", foreground=MUTED)
        self.skills_text.tag_configure("risk", foreground=REJECT)
        self.skills_text.tag_configure("ok", foreground=SHORTLIST)

    # ───────────────────────────────────────────────────────
    def _choose_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.selected_folder = folder
            self.folder_label.config(text=os.path.basename(folder), fg=WHITE)
            self.status_var.set("Resume folder selected")

    def _choose_jd(self):
        jd = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if jd:
            self.selected_jd = jd
            self.jd_label.config(text=os.path.basename(jd), fg=WHITE)
            self.status_var.set("Job description selected")

    # ───────────────────────────────────────────────────────
    def _start_ranking(self):
        if not self.selected_folder:
            messagebox.showwarning("Missing input", "Please select a resume folder first.")
            return
        if not self.selected_jd:
            messagebox.showwarning("Missing input", "Please select a job description file first.")
            return

        self.run_btn.config(state=tk.DISABLED, text="Ranking in progress...", bg="#e2cda2")
        self.progress["value"] = 0
        self.status_label.config(text="Preparing ranking session...")
        self.status_var.set("Ranking resumes now")
        threading.Thread(target=self._run_ranking_thread, daemon=True).start()

    def _run_ranking_thread(self):
        try:
            with open(self.selected_jd, "r", encoding="utf-8", errors="ignore") as handle:
                jd_text = handle.read()

            def progress_cb(cur, total, fname):
                pct = int(cur / total * 92) if total else 0
                self.root.after(0, lambda: self.progress.config(value=pct))
                self.root.after(0, lambda: self.status_label.config(text=f"Scanning {cur}/{total}: {fname[:38]}"))

            results, ignored = rank_resumes(self.selected_folder, jd_text, progress_callback=progress_cb)
            summary = compute_summary(results)
            self.root.after(0, lambda: self._on_ranking_done(results, summary, jd_text, ignored))
        except Exception as exc:
            self.root.after(0, lambda: messagebox.showerror("Ranking error", str(exc)))
            self.root.after(0, self._reset_run_state)

    def _on_ranking_done(self, results, summary, jd_text, ignored):
        self.results = results
        self.summary = summary
        self.jd_text = jd_text

        self.progress["value"] = 100
        self.status_label.config(text=f"Ranking complete: {len(results)} candidate(s)")
        self.status_var.set("Ranking complete")
        self._reset_run_state(button_only=True)

        self._refresh_results()
        self._refresh_recruiter_view()
        self._refresh_summary()
        self._refresh_skills()
        self._update_dashboard_state()

        if ignored:
            messagebox.showinfo("Skipped files", f"{len(ignored)} file(s) were skipped.\n\n" + "\n".join(ignored[:12]))

    def _reset_run_state(self, button_only=False):
        self.run_btn.config(state=tk.NORMAL, text="Start Ranking", bg=GOLD)
        if not button_only:
            self.status_var.set("Command center ready")

    # ───────────────────────────────────────────────────────
    def _filtered_results(self):
        status_filter = self.filter_var.get()
        query = self.search_var.get().strip().lower()
        top_n = self.top_n_var.get()

        filtered = []
        for candidate in self.results:
            if status_filter != "All" and candidate.status != status_filter:
                continue
            haystack = " ".join(
                [
                    str(candidate.filename),
                    str(candidate.name or ""),
                    str(candidate.email or ""),
                    str(candidate.linkedin or ""),
                    " ".join(candidate.all_skills_flat[:8]),
                ]
            ).lower()
            if query and query not in haystack:
                continue
            filtered.append(candidate)
        return filtered[:top_n]

    def _refresh_results(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        filtered = self._filtered_results()
        for r in filtered:
            skill_preview = ", ".join(r.all_skills_flat[:5]) if r.all_skills_flat else "No strong skill signal"
            self.tree.insert(
                "",
                tk.END,
                values=(
                    f"#{r.rank:02d}",
                    r.name or r.filename,
                    safe_ratio(r.final_score),
                    f"{r.skill_coverage}%",
                    r.status,
                    get_priority_label(r),
                    get_interview_readiness(r),
                    get_recommended_action(r),
                    f"{r.experience_years} yr",
                    r.seniority,
                    r.education,
                    skill_preview,
                ),
                tags=(r.status,),
            )
        self._update_dashboard_state()

    def _refresh_recruiter_view(self):
        for row in self.rec_tree.get_children():
            self.rec_tree.delete(row)

        for r in self.results:
            notes = self._recruiter_notes.get(r.filename, "")
            notes_preview = notes[:42] + "..." if len(notes) > 42 else notes
            decision = self._recruiter_decisions.get(r.filename, get_recommended_action(r))
            self.rec_tree.insert(
                "",
                tk.END,
                values=(
                    f"#{r.rank:02d}",
                    r.name or r.filename,
                    r.status,
                    get_priority_label(r),
                    get_interview_readiness(r),
                    get_recommended_action(r),
                    safe_ratio(r.final_score),
                    r.experience_years,
                    get_contact_completeness(r),
                    decision,
                    notes_preview or "—",
                ),
                tags=(r.status,),
            )

    def _update_dashboard_state(self):
        total = len(self.results)
        shortlisted = sum(1 for r in self.results if r.status == "Shortlisted")
        high_priority = sum(1 for r in self.results if get_priority_label(r) == "High Priority")
        avg_score = sum(r.final_score for r in self.results) / total if total else 0
        lead = self.results[0] if self.results else None

        self.metric_vars["total"].set(str(total))
        self.metric_vars["shortlisted"].set(str(shortlisted))
        self.metric_vars["high_priority"].set(str(high_priority))
        self.metric_vars["avg_score"].set(safe_ratio(avg_score))
        self.metric_vars["top_candidate"].set(
            f"{lead.name or lead.filename}  |  {safe_ratio(lead.final_score)} match  |  {get_priority_label(lead)}"
            if lead else "—"
        )

        if lead:
            self.hero_note.config(
                text=(
                    f"{lead.name or lead.filename} leads the slate with {lead.skill_coverage}% skill coverage, "
                    f"{lead.experience_years} years of experience, and a recommended next step of "
                    f"{get_recommended_action(lead).lower()}."
                )
            )
        else:
            self.hero_note.config(
                text="Run a ranking pass to generate recruiter guidance and shortlist highlights."
            )

    def _refresh_summary(self):
        text = self.summary_text
        text.config(state=tk.NORMAL)
        text.delete("1.0", tk.END)

        def put(value, tag=None):
            text.insert(tk.END, value, tag)

        now = datetime.now().strftime("%d %b %Y  •  %I:%M %p")
        summary = self.summary or {}
        total = len(self.results)
        shortlisted = sum(1 for r in self.results if r.status == "Shortlisted")
        maybe = sum(1 for r in self.results if r.status == "Maybe")
        rejected = sum(1 for r in self.results if r.status == "Not Relevant")
        high_priority = sum(1 for r in self.results if get_priority_label(r) == "High Priority")

        put("Executive Hiring Summary\n", "h1")
        put(f"Generated {now}\n\n", "muted")

        put("Snapshot\n", "h2")
        put(f"Total candidates reviewed: {total}\n", "strong")
        put(f"Shortlisted: {shortlisted}   |   Maybe: {maybe}   |   Not Relevant: {rejected}\n", "muted")
        put(f"High-priority profiles: {high_priority}\n", "ok")
        put(f"Average match score: {safe_ratio(summary.get('avg_score', 0))}\n\n", "strong")

        if self.results:
            lead = self.results[0]
            put("Lead recommendation\n", "h2")
            put(f"{lead.name or lead.filename}\n", "strong")
            put(
                f"This candidate ranks first with {safe_ratio(lead.final_score)} match, "
                f"{lead.skill_coverage}% coverage, and {lead.experience_years} years of experience. "
                f"Suggested action: {get_recommended_action(lead)}.\n\n",
                "muted",
            )

        put("Top slate detail\n", "h2")
        for candidate in self.results[:5]:
            tone = "ok" if candidate.status == "Shortlisted" else "warn" if candidate.status == "Maybe" else "risk"
            put(f"#{candidate.rank:02d}  {candidate.name or candidate.filename}\n", "strong")
            put(
                f"Status: {candidate.status}   |   Score: {safe_ratio(candidate.final_score)}   |   "
                f"Priority: {get_priority_label(candidate)}   |   Coverage: {candidate.skill_coverage}%\n",
                tone,
            )
            put(
                f"Experience: {candidate.experience_years} years   |   Education: {candidate.education}   |   "
                f"Action: {get_recommended_action(candidate)}\n",
                "muted",
            )
            put(
                f"Matched skills: {', '.join(candidate.all_skills_flat[:8]) or 'None detected'}\n",
                "muted",
            )
            put(
                f"Main gaps: {', '.join(candidate.missing_skills[:5]) or 'None'}\n\n",
                "risk",
            )

        text.config(state=tk.DISABLED)

    def _refresh_skills(self):
        from collections import Counter

        counter = Counter()
        for candidate in self.results:
            for skill in candidate.all_skills_flat:
                counter[skill] += 1

        text = self.skills_text
        text.config(state=tk.NORMAL)
        text.delete("1.0", tk.END)

        def put(value, tag=None):
            text.insert(tk.END, value, tag)

        put("Skill Coverage Ledger\n", "h1")
        put("Top skill signals across the reviewed candidate set.\n\n", "muted")

        max_count = counter.most_common(1)[0][1] if counter else 1
        for skill, count in counter.most_common(30):
            width = max(1, int((count / max_count) * 28))
            put(f"{skill:<28}", "muted")
            put("■" * width, "bar")
            put(f"  {count}\n", "count")

        put("\nSkill group coverage\n", "group")
        for group, skills in SKILL_GROUPS.items():
            found = [s for s in skills if s in counter]
            missing = [s for s in skills if s not in counter]
            put(f"\n[{group}]\n", "group")
            put(f"Present: {', '.join(found[:10]) or '—'}\n", "ok")
            put(f"Missing: {', '.join(missing[:10]) or '—'}\n", "risk")

        text.config(state=tk.DISABLED)

    # ───────────────────────────────────────────────────────
    def _show_detail(self, _event):
        selection = self.tree.selection()
        if not selection:
            return
        row = self.tree.item(selection[0])["values"]
        name_value = row[1]
        candidate = next((item for item in self.results if (item.name or item.filename) == name_value), None)
        if candidate:
            self._open_detail_window(candidate)

    def _open_detail_window(self, candidate: CandidateResult):
        win = tk.Toplevel(self.root)
        win.title(f"Candidate Review  |  {candidate.name or candidate.filename}")
        win.geometry("860x760")
        win.configure(bg=MIDNIGHT)

        head = tk.Frame(win, bg=MIDNIGHT_2)
        head.pack(fill=tk.X, padx=16, pady=16)
        tk.Label(head, text=f"#{candidate.rank:02d}", bg=MIDNIGHT_2, fg=GOLD, font=("Georgia", 26, "bold")).pack(side=tk.LEFT, padx=16, pady=14)

        title_area = tk.Frame(head, bg=MIDNIGHT_2)
        title_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=14)
        tk.Label(title_area, text=candidate.name or candidate.filename, bg=MIDNIGHT_2, fg=WHITE, font=("Segoe UI Semibold", 14)).pack(anchor=tk.W)
        tk.Label(
            title_area,
            text=f"{candidate.status}  |  {safe_ratio(candidate.final_score)} match  |  {get_priority_label(candidate)}",
            bg=MIDNIGHT_2,
            fg="#a7d8d2",
            font=FONT_UI,
        ).pack(anchor=tk.W, pady=(4, 0))

        body = tk.Text(
            win,
            bg=CARD,
            fg=TEXT,
            font=FONT_UI,
            relief=tk.FLAT,
            wrap=tk.WORD,
            padx=20,
            pady=18,
            selectbackground="#d7ebe6",
        )
        body.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 16))
        body.tag_configure("h", foreground=ACCENT, font=("Georgia", 16, "bold"))
        body.tag_configure("muted", foreground=MUTED)
        body.tag_configure("strong", foreground=TEXT, font=("Segoe UI Semibold", 10))
        body.tag_configure("ok", foreground=SHORTLIST)
        body.tag_configure("warn", foreground=MAYBE)
        body.tag_configure("risk", foreground=REJECT)

        def put(value, tag=None):
            body.insert(tk.END, value, tag)

        put("Recruiter Signals\n", "h")
        put(f"Priority: {get_priority_label(candidate)}\n", "strong")
        put(f"Interview readiness: {get_interview_readiness(candidate)}\n", "muted")
        put(f"Recommended action: {get_recommended_action(candidate)}\n", "muted")
        put(f"Contact completeness: {get_contact_completeness(candidate)}\n\n", "muted")

        put("Contact\n", "h")
        put(f"Name: {candidate.name or 'N/A'}\n", "muted")
        put(f"Email: {candidate.email or 'N/A'}\n", "muted")
        put(f"Phone: {candidate.phone or 'N/A'}\n", "muted")
        put(f"LinkedIn: {candidate.linkedin or 'N/A'}\n", "muted")
        put(f"GitHub: {candidate.github or 'N/A'}\n\n", "muted")

        put("Scoring\n", "h")
        put(
            f"Final score: {candidate.final_score:.4f}\nTF-IDF: {candidate.tfidf_score:.4f}\n"
            f"Keyword: {candidate.keyword_score:.4f}\nSeniority: {candidate.seniority_score:.4f} ({candidate.seniority})\n"
            f"Education: {candidate.education_score:.4f} ({candidate.education})\n"
            f"Experience: {candidate.experience_years} years   |   Coverage: {candidate.skill_coverage}%\n\n",
            "muted",
        )

        put("Matched Skills\n", "h")
        for group, skills in candidate.matched_skills.items():
            put(f"{group}: {', '.join(skills)}\n", "strong")
        put("\nMissing Skills\n", "h")
        put(f"{', '.join(candidate.missing_skills) or 'None'}\n\n", "risk")

        put("Recruiter Notes\n", "h")
        put(self._recruiter_notes.get(candidate.filename, "(none recorded yet)") + "\n\n", "muted")

        put("Resume Preview\n", "h")
        preview = (candidate.raw_text[:1200] + "...") if len(candidate.raw_text) > 1200 else candidate.raw_text
        put(preview, "muted")

        body.config(state=tk.DISABLED)

    def _open_recruiter_notes(self, _event):
        selection = self.rec_tree.selection()
        if not selection:
            return
        row = self.rec_tree.item(selection[0])["values"]
        rank_num = int(str(row[0]).replace("#", ""))
        candidate = next((item for item in self.results if item.rank == rank_num), None)
        if not candidate:
            return

        win = tk.Toplevel(self.root)
        win.title(f"Recruiter Notes  |  {candidate.name or candidate.filename}")
        win.geometry("620x540")
        win.configure(bg=MIDNIGHT)

        card = tk.Frame(win, bg=CARD)
        card.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

        tk.Label(card, text="Recruiter Notes", bg=CARD, fg=TEXT, font=("Georgia", 18, "bold")).pack(
            anchor=tk.W, padx=18, pady=(16, 4)
        )
        tk.Label(
            card,
            text=f"{candidate.name or candidate.filename}  |  {get_priority_label(candidate)}  |  {safe_ratio(candidate.final_score)} match",
            bg=CARD,
            fg=MUTED,
            font=FONT_UI,
        ).pack(anchor=tk.W, padx=18, pady=(0, 12))

        row_shell = tk.Frame(card, bg=CARD)
        row_shell.pack(fill=tk.X, padx=18)
        tk.Label(row_shell, text="Decision", bg=CARD, fg=MUTED, font=FONT_UI_SM).pack(side=tk.LEFT)

        decision_var = tk.StringVar(value=self._recruiter_decisions.get(candidate.filename, get_recommended_action(candidate)))
        combo = ttk.Combobox(row_shell, textvariable=decision_var, values=RECRUITER_DECISIONS, state="readonly", width=30)
        combo.pack(side=tk.LEFT, padx=(10, 0))

        tk.Label(card, text="Notes", bg=CARD, fg=MUTED, font=FONT_UI_SM).pack(anchor=tk.W, padx=18, pady=(16, 6))
        notes = tk.Text(card, bg=CARD_2, fg=TEXT, relief=tk.FLAT, wrap=tk.WORD, height=14, padx=12, pady=12, font=FONT_UI)
        notes.pack(fill=tk.BOTH, expand=True, padx=18, pady=(0, 14))
        existing = self._recruiter_notes.get(candidate.filename, "")
        if existing:
            notes.insert("1.0", existing)

        def save_and_close():
            self._recruiter_notes[candidate.filename] = notes.get("1.0", tk.END).strip()
            self._recruiter_decisions[candidate.filename] = decision_var.get()
            self._refresh_recruiter_view()
            win.destroy()

        tk.Button(
            card,
            text="Save recruiter decision",
            command=save_and_close,
            bg=ACCENT,
            fg=WHITE,
            relief=tk.FLAT,
            font=FONT_UI_B,
            pady=10,
        ).pack(fill=tk.X, padx=18, pady=(0, 18))

    # ───────────────────────────────────────────────────────
    def _sort_tree(self, col):
        reverse = self._sort_reverse.get(col, True)
        items = [(self.tree.set(item, col), item) for item in self.tree.get_children("")]
        try:
            items.sort(
                key=lambda pair: float(pair[0].replace("#", "").replace("%", "").replace("yr", "").strip()),
                reverse=reverse,
            )
        except ValueError:
            items.sort(key=lambda pair: pair[0].lower(), reverse=reverse)
        for idx, (_, item) in enumerate(items):
            self.tree.move(item, "", idx)
        self._sort_reverse[col] = not reverse

    # ───────────────────────────────────────────────────────
    def _export_csv(self):
        if not self.results:
            messagebox.showwarning("No data", "Run ranking first.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            initialfile="ranked_resumes.csv",
        )
        if path:
            export_csv(self.results, path)
            messagebox.showinfo("Export complete", f"CSV saved to:\n{path}")

    def _export_json(self):
        if not self.results:
            messagebox.showwarning("No data", "Run ranking first.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json")],
            initialfile="ranking_results.json",
        )
        if path:
            export_json(self.results, self.summary, path)
            messagebox.showinfo("Export complete", f"JSON saved to:\n{path}")

    def _export_txt(self):
        if not self.results:
            messagebox.showwarning("No data", "Run ranking first.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text", "*.txt")],
            initialfile="ranking_report.txt",
        )
        if path:
            export_txt_report(self.results, self.summary, self.jd_text, path)
            messagebox.showinfo("Export complete", f"Report saved to:\n{path}")

    # ───────────────────────────────────────────────────────
    def _section_label(self, parent, text):
        tk.Label(parent, text=text.upper(), bg=SLATE, fg="#8dbab3", font=("Segoe UI", 8, "bold")).pack(
            anchor=tk.W, pady=(14, 8)
        )

    def _hint_label(self, parent, text):
        label = tk.Label(parent, text=text, bg=SLATE, fg=MUTED_2, font=FONT_UI_SM, wraplength=255, justify=tk.LEFT)
        label.pack(anchor=tk.W, pady=(6, 10))
        return label

    def _action_button(self, parent, text, command, bg, fg):
        tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            relief=tk.FLAT,
            cursor="hand2",
            font=FONT_UI_B,
            pady=9,
        ).pack(fill=tk.X)

    def _soft_button(self, parent, text, command):
        tk.Button(
            parent,
            text=text,
            command=command,
            bg=SLATE_2,
            fg=WHITE,
            relief=tk.FLAT,
            cursor="hand2",
            font=FONT_UI,
            pady=8,
        ).pack(fill=tk.X, pady=4)


if __name__ == "__main__":
    root = tk.Tk()
    app = ResumeRankerApp(root)
    root.mainloop()
