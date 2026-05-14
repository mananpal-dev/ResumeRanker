# ============================================================
#   main.py  –  Tkinter Desktop App  |  AI Resume Ranker v2.0
#   Run:  python main.py
# ============================================================

import os, sys, threading, time
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from config import APP_NAME, APP_VERSION, SHORTLIST_THRESHOLD, MAYBE_THRESHOLD
from utils.ranker import rank_resumes, compute_summary, CandidateResult
from utils.exporter import export_csv, export_json, export_txt_report


# ── Colour palette ────────────────────────────────────────────
BG_DARK   = "#0f0c29"
BG_PANEL  = "#1a1535"
BG_CARD   = "#201c40"
ACCENT    = "#6c63ff"
ACCENT2   = "#a78bff"
GREEN     = "#00e17a"
YELLOW    = "#f5a623"
RED       = "#ff6b6b"
TEXT      = "#e2d9ff"
TEXT_DIM  = "#7a7099"
WHITE     = "#ffffff"

FONT_TITLE  = ("Helvetica", 22, "bold")
FONT_HEADER = ("Helvetica", 13, "bold")
FONT_BODY   = ("Helvetica", 11)
FONT_SMALL  = ("Helvetica", 9)
FONT_MONO   = ("Courier", 10)


class ResumeRankerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry("1100x780")
        self.root.minsize(900, 650)
        self.root.configure(bg=BG_DARK)

        self.selected_folder = None
        self.selected_jd     = None
        self.results         = []
        self.summary         = {}

        self._build_ui()

    # ─────────────────────────────────────────────────────────
    def _build_ui(self):
        # ── Left panel ──
        left = tk.Frame(self.root, bg=BG_PANEL, width=300)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=0)
        left.pack_propagate(False)

        # ── Right panel ──
        right = tk.Frame(self.root, bg=BG_DARK)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._build_left(left)
        self._build_right(right)

    # ─────────────────────────────────────────────────────────
    def _build_left(self, parent):
        # Brand
        tk.Label(parent, text="🎯", font=("Helvetica", 38), bg=BG_PANEL, fg=ACCENT).pack(pady=(30,4))
        tk.Label(parent, text="AI Resume Ranker", font=("Helvetica", 16, "bold"),
                 bg=BG_PANEL, fg=WHITE).pack()
        tk.Label(parent, text=f"v{APP_VERSION} · by Manan Pal", font=FONT_SMALL,
                 bg=BG_PANEL, fg=TEXT_DIM).pack(pady=(0,20))

        separator(parent, BG_PANEL)

        # ── Resume folder ──
        section_label(parent, "📂 Resume Folder")
        tk.Button(parent, text="Browse Folder", font=FONT_BODY,
                  bg=ACCENT, fg=WHITE, relief=tk.FLAT, cursor="hand2",
                  command=self._choose_folder).pack(padx=20, pady=4, fill=tk.X)
        self.folder_label = tk.Label(parent, text="No folder selected", font=FONT_SMALL,
                                     bg=BG_PANEL, fg=TEXT_DIM, wraplength=240, justify=tk.LEFT)
        self.folder_label.pack(padx=20, pady=(0,12))

        # ── JD file ──
        section_label(parent, "📋 Job Description")
        tk.Button(parent, text="Browse .txt File", font=FONT_BODY,
                  bg=ACCENT, fg=WHITE, relief=tk.FLAT, cursor="hand2",
                  command=self._choose_jd).pack(padx=20, pady=4, fill=tk.X)
        self.jd_label = tk.Label(parent, text="No JD selected", font=FONT_SMALL,
                                 bg=BG_PANEL, fg=TEXT_DIM, wraplength=240, justify=tk.LEFT)
        self.jd_label.pack(padx=20, pady=(0,12))

        separator(parent, BG_PANEL)

        # ── Options ──
        section_label(parent, "⚙️ Options")

        self.top_n_var = tk.IntVar(value=10)
        tk.Label(parent, text="Show top N results:", font=FONT_SMALL,
                 bg=BG_PANEL, fg=TEXT_DIM).pack(padx=20, anchor=tk.W)
        tk.Spinbox(parent, from_=5, to=100, textvariable=self.top_n_var,
                   width=6, bg=BG_CARD, fg=TEXT, insertbackground=TEXT,
                   relief=tk.FLAT, font=FONT_BODY).pack(padx=20, pady=(2,10), anchor=tk.W)

        separator(parent, BG_PANEL)

        # ── Run button ──
        self.run_btn = tk.Button(
            parent, text="🚀  Start Ranking", font=("Helvetica", 13, "bold"),
            bg=GREEN, fg=BG_DARK, relief=tk.FLAT, cursor="hand2",
            pady=12, command=self._start_ranking
        )
        self.run_btn.pack(padx=20, pady=12, fill=tk.X)

        # ── Progress bar ──
        self.progress = ttk.Progressbar(parent, mode="determinate", length=240)
        self.progress.pack(padx=20, pady=4, fill=tk.X)
        self.status_label = tk.Label(parent, text="", font=FONT_SMALL,
                                     bg=BG_PANEL, fg=TEXT_DIM)
        self.status_label.pack(padx=20)

        separator(parent, BG_PANEL)

        # ── Export buttons ──
        section_label(parent, "📥 Export")
        for label, cmd in [
            ("CSV Report", self._export_csv),
            ("JSON Data",  self._export_json),
            ("TXT Report", self._export_txt),
        ]:
            tk.Button(parent, text=label, font=FONT_SMALL,
                      bg=BG_CARD, fg=ACCENT2, relief=tk.FLAT, cursor="hand2",
                      command=cmd).pack(padx=20, pady=3, fill=tk.X)

    # ─────────────────────────────────────────────────────────
    def _build_right(self, parent):
        # Header
        header = tk.Frame(parent, bg=ACCENT, height=6)
        header.pack(fill=tk.X)

        # Notebook / Tabs
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.TNotebook", background=BG_DARK, borderwidth=0)
        style.configure("Custom.TNotebook.Tab",
                        background=BG_PANEL, foreground=TEXT_DIM,
                        padding=[14,8], font=FONT_BODY)
        style.map("Custom.TNotebook.Tab",
                  background=[("selected", BG_CARD)],
                  foreground=[("selected", ACCENT2)])

        self.notebook = ttk.Notebook(parent, style="Custom.TNotebook")
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # Tabs
        self.tab_results  = tk.Frame(self.notebook, bg=BG_DARK)
        self.tab_summary  = tk.Frame(self.notebook, bg=BG_DARK)
        self.tab_skills   = tk.Frame(self.notebook, bg=BG_DARK)

        self.notebook.add(self.tab_results, text="🏆  Rankings")
        self.notebook.add(self.tab_summary, text="📊  Summary")
        self.notebook.add(self.tab_skills,  text="🔬  Skill Map")

        self._build_results_tab()
        self._build_summary_tab()
        self._build_skills_tab()

    # ─────────────────────────────────────────────────────────
    def _build_results_tab(self):
        parent = self.tab_results

        # Toolbar
        toolbar = tk.Frame(parent, bg=BG_PANEL, pady=6)
        toolbar.pack(fill=tk.X)

        tk.Label(toolbar, text="Filter:", font=FONT_SMALL, bg=BG_PANEL, fg=TEXT_DIM).pack(side=tk.LEFT, padx=(12,4))

        self.filter_var = tk.StringVar(value="All")
        for label in ["All", "Shortlisted", "Maybe", "Not Relevant"]:
            tk.Radiobutton(
                toolbar, text=label, variable=self.filter_var, value=label,
                bg=BG_PANEL, fg=TEXT, selectcolor=BG_CARD,
                activebackground=BG_PANEL, font=FONT_SMALL,
                command=self._refresh_results
            ).pack(side=tk.LEFT, padx=6)

        tk.Button(toolbar, text="🔄 Refresh", font=FONT_SMALL,
                  bg=BG_CARD, fg=ACCENT2, relief=tk.FLAT,
                  command=self._refresh_results).pack(side=tk.RIGHT, padx=12)

        # Treeview
        cols = ("Rank", "Filename", "Score", "TF-IDF", "Keywords", "Seniority",
                "Education", "Exp(yr)", "Status", "Skills", "Coverage%")
        self.tree = ttk.Treeview(parent, columns=cols, show="headings", height=28)

        col_widths = [45, 200, 70, 70, 70, 80, 80, 60, 110, 260, 75]
        for col, w in zip(cols, col_widths):
            self.tree.heading(col, text=col,
                              command=lambda c=col: self._sort_tree(c))
            self.tree.column(col, width=w, anchor=tk.CENTER)

        tree_style = ttk.Style()
        tree_style.configure("Treeview",
                             background=BG_CARD, foreground=TEXT,
                             rowheight=26, fieldbackground=BG_CARD,
                             borderwidth=0, font=FONT_SMALL)
        tree_style.configure("Treeview.Heading",
                             background=BG_PANEL, foreground=ACCENT2,
                             font=FONT_SMALL, relief=tk.FLAT)
        tree_style.map("Treeview", background=[("selected", ACCENT)])

        # Tag colours for status
        self.tree.tag_configure("Shortlisted",  background="#0a2e1a", foreground=GREEN)
        self.tree.tag_configure("Maybe",        background="#2e200a", foreground=YELLOW)
        self.tree.tag_configure("Not Relevant", background="#2e0a0a", foreground=RED)

        vsb = ttk.Scrollbar(parent, orient="vertical",   command=self.tree.yview)
        hsb = ttk.Scrollbar(parent, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<Double-Button-1>", self._show_detail)

    # ─────────────────────────────────────────────────────────
    def _build_summary_tab(self):
        self.summary_text = tk.Text(
            self.tab_summary, bg=BG_DARK, fg=TEXT, font=FONT_MONO,
            relief=tk.FLAT, padx=20, pady=20, wrap=tk.WORD,
            insertbackground=TEXT
        )
        self.summary_text.pack(fill=tk.BOTH, expand=True)

    # ─────────────────────────────────────────────────────────
    def _build_skills_tab(self):
        self.skills_text = tk.Text(
            self.tab_skills, bg=BG_DARK, fg=TEXT, font=FONT_MONO,
            relief=tk.FLAT, padx=20, pady=20, wrap=tk.WORD
        )
        self.skills_text.pack(fill=tk.BOTH, expand=True)

    # ─────────────────────────────────────────────────────────
    def _choose_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.selected_folder = folder
            self.folder_label.config(text=os.path.basename(folder), fg=ACCENT2)

    def _choose_jd(self):
        jd = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All", "*.*")])
        if jd:
            self.selected_jd = jd
            self.jd_label.config(text=os.path.basename(jd), fg=ACCENT2)

    # ─────────────────────────────────────────────────────────
    def _start_ranking(self):
        if not self.selected_folder:
            messagebox.showwarning("Missing", "Please select a resume folder.")
            return
        if not self.selected_jd:
            messagebox.showwarning("Missing", "Please select a job description file.")
            return

        self.run_btn.config(state=tk.DISABLED, text="⏳ Ranking…")
        self.progress["value"] = 0
        threading.Thread(target=self._run_ranking_thread, daemon=True).start()

    def _run_ranking_thread(self):
        try:
            with open(self.selected_jd, 'r', encoding='utf-8', errors='ignore') as f:
                jd_text = f.read()

            def progress_cb(cur, total, fname):
                pct = int(cur / total * 90)
                self.root.after(0, lambda: self.progress.config(value=pct))
                self.root.after(0, lambda: self.status_label.config(
                    text=f"Analysing {cur}/{total}: {fname[:30]}…"))

            self.results, ignored = rank_resumes(
                self.selected_folder, jd_text, progress_callback=progress_cb
            )
            self.summary  = compute_summary(self.results)
            self.jd_text  = jd_text

            self.root.after(0, lambda: self._on_ranking_done(ignored))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            self.root.after(0, lambda: self.run_btn.config(state=tk.NORMAL, text="🚀  Start Ranking"))

    def _on_ranking_done(self, ignored):
        self.progress["value"] = 100
        self.status_label.config(text=f"✅ Done — {len(self.results)} candidates ranked")
        self.run_btn.config(state=tk.NORMAL, text="🚀  Start Ranking")

        self._refresh_results()
        self._refresh_summary()
        self._refresh_skills()

        if ignored:
            messagebox.showinfo(
                "Skipped files",
                f"{len(ignored)} file(s) were skipped (too short / unreadable):\n" + "\n".join(ignored[:10])
            )

    # ─────────────────────────────────────────────────────────
    def _refresh_results(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        flt = self.filter_var.get()
        top_n = self.top_n_var.get()

        filtered = [r for r in self.results
                    if flt == "All" or r.status == flt][:top_n]

        for r in filtered:
            skills_str = ", ".join(r.all_skills_flat[:6])
            if len(r.all_skills_flat) > 6:
                skills_str += f" +{len(r.all_skills_flat)-6}"

            tag = r.status.replace(" ", "_") if r.status != "Not Relevant" else "Not Relevant"

            self.tree.insert("", tk.END, values=(
                f"#{r.rank}",
                r.filename,
                f"{r.final_score:.4f}",
                f"{r.tfidf_score:.3f}",
                f"{r.keyword_score:.3f}",
                r.seniority,
                r.education,
                r.experience_years,
                r.status,
                skills_str,
                f"{r.skill_coverage}%",
            ), tags=(r.status,))

    def _refresh_summary(self):
        s = self.summary
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        text = f"""
╔══════════════════════════════════════════════════════════════╗
║           AI RESUME RANKER  v{APP_VERSION}  │  {now}           ║
╚══════════════════════════════════════════════════════════════╝

── CANDIDATE SUMMARY ────────────────────────────────────────

  Total Candidates   :  {s.get('total', 0)}
  ✅ Shortlisted      :  {s.get('shortlisted', 0)}
  🤔 Maybe            :  {s.get('maybe', 0)}
  ❌ Not Relevant     :  {s.get('not_relevant', 0)}
  Average Score      :  {s.get('avg_score', 0):.4f}
  Top Score          :  {s.get('top_score', 0):.4f}
  Lowest Score       :  {s.get('low_score', 0):.4f}
  Best Candidate     :  {s.get('top_candidate', '')}

── TOP 5 DETAILED ───────────────────────────────────────────
"""
        for r in self.results[:5]:
            text += f"""
  #{r.rank}  {r.filename}
      Score    :  {r.final_score:.4f}
      Status   :  {r.status}
      Skills   :  {', '.join(r.all_skills_flat[:8]) or 'None'}
      Coverage :  {r.skill_coverage}%
      Seniority:  {r.seniority}  |  Education: {r.education}  |  Exp: {r.experience_years}yr
      Missing  :  {', '.join(r.missing_skills[:5]) or 'None'}
"""

        self.summary_text.config(state=tk.NORMAL)
        self.summary_text.delete("1.0", tk.END)
        self.summary_text.insert(tk.END, text)
        self.summary_text.config(state=tk.DISABLED)

    def _refresh_skills(self):
        from collections import Counter
        counter = Counter()
        for r in self.results:
            for s in r.all_skills_flat:
                counter[s] += 1

        lines = ["── SKILL FREQUENCY ACROSS ALL RESUMES ──────────────────────\n"]
        for skill, cnt in counter.most_common(40):
            bar = "█" * cnt
            lines.append(f"  {skill:<30} {bar}  ({cnt})")

        lines += ["\n── SKILL GROUPS ─────────────────────────────────────────────\n"]
        from config import SKILL_GROUPS
        for grp, skills in SKILL_GROUPS.items():
            found = [s for s in skills if s in counter]
            lines.append(f"\n  {grp}:")
            lines.append(f"    Found:   {', '.join(found) or '—'}")
            lines.append(f"    Missing: {', '.join(s for s in skills if s not in counter)[:80] or '—'}")

        self.skills_text.config(state=tk.NORMAL)
        self.skills_text.delete("1.0", tk.END)
        self.skills_text.insert(tk.END, "\n".join(lines))
        self.skills_text.config(state=tk.DISABLED)

    # ─────────────────────────────────────────────────────────
    def _show_detail(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        item  = self.tree.item(sel[0])
        fname = item["values"][1]
        r = next((x for x in self.results if x.filename == fname), None)
        if not r:
            return

        win = tk.Toplevel(self.root)
        win.title(f"Detail: {fname}")
        win.geometry("700x540")
        win.configure(bg=BG_DARK)

        txt = tk.Text(win, bg=BG_DARK, fg=TEXT, font=FONT_MONO,
                      relief=tk.FLAT, padx=20, pady=20, wrap=tk.WORD)
        txt.pack(fill=tk.BOTH, expand=True)

        detail = f"""
CANDIDATE DETAIL  ─  {fname}
{'─'*50}
Name       : {r.name or 'N/A'}
Email      : {r.email or 'N/A'}
Phone      : {r.phone or 'N/A'}
LinkedIn   : {r.linkedin or 'N/A'}
GitHub     : {r.github or 'N/A'}

── SCORES ──────────────────────────────────
Final Score  : {r.final_score:.4f}
TF-IDF       : {r.tfidf_score:.4f}
Keyword      : {r.keyword_score:.4f}
Seniority    : {r.seniority_score:.4f}  ({r.seniority})
Education    : {r.education_score:.4f}  ({r.education})
Experience   : {r.experience_years} years
Status       : {r.status}
Coverage     : {r.skill_coverage}%

── MATCHED SKILLS ──────────────────────────
"""
        for grp, skills in r.matched_skills.items():
            detail += f"  {grp}: {', '.join(skills)}\n"

        detail += f"""
── MISSING SKILLS ──────────────────────────
{', '.join(r.missing_skills) or 'None'}

── RESUME TEXT PREVIEW (first 800 chars) ───
{r.raw_text[:800]}…
"""
        txt.insert(tk.END, detail)
        txt.config(state=tk.DISABLED)

    # ─────────────────────────────────────────────────────────
    def _sort_tree(self, col):
        items = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        try:
            items.sort(key=lambda t: float(t[0].replace("#","").replace("%","")), reverse=True)
        except ValueError:
            items.sort(reverse=False)
        for idx, (_, k) in enumerate(items):
            self.tree.move(k, "", idx)

    def _export_csv(self):
        if not self.results:
            messagebox.showwarning("No data", "Run ranking first."); return
        path = filedialog.asksaveasfilename(defaultextension=".csv",
               filetypes=[("CSV","*.csv")], initialfile="ranked_resumes.csv")
        if path:
            export_csv(self.results, path)
            messagebox.showinfo("Exported", f"CSV saved:\n{path}")

    def _export_json(self):
        if not self.results:
            messagebox.showwarning("No data", "Run ranking first."); return
        path = filedialog.asksaveasfilename(defaultextension=".json",
               filetypes=[("JSON","*.json")], initialfile="ranking_results.json")
        if path:
            export_json(self.results, self.summary, path)
            messagebox.showinfo("Exported", f"JSON saved:\n{path}")

    def _export_txt(self):
        if not self.results:
            messagebox.showwarning("No data", "Run ranking first."); return
        path = filedialog.asksaveasfilename(defaultextension=".txt",
               filetypes=[("Text","*.txt")], initialfile="ranking_report.txt")
        if path:
            export_txt_report(self.results, self.summary, getattr(self, "jd_text", ""), path)
            messagebox.showinfo("Exported", f"Report saved:\n{path}")


# ── Helpers ────────────────────────────────────────────────────
def separator(parent, bg):
    tk.Frame(parent, bg="#2d2855", height=1).pack(fill=tk.X, padx=16, pady=8)

def section_label(parent, text):
    tk.Label(parent, text=text, font=("Helvetica", 10, "bold"),
             bg=BG_PANEL, fg=ACCENT2, anchor=tk.W).pack(padx=20, anchor=tk.W, pady=(6,2))


# ── Entry point ────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app  = ResumeRankerApp(root)
    root.mainloop()
