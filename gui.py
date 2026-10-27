"""
Survey Manager - desktop GUI (Tkinter)

 1. Last week's survey results
 2. Re-survey now
 3. Summary of the last three months
 4. Developer tools
 5. Quit

Run:  python survey_app_gui.py
Needs only Python 3 (Tkinter comes with it). Uses the same survey_data.csv
file as the console version, so both apps share data.
"""

import csv
import os
import random
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import messagebox, simpledialog, ttk

DATA_FILE = "survey_data.csv"
EXPORT_FILE = "survey_export.csv"
FMT = "%Y-%m-%d %H:%M"

QUESTIONS = [
    "Overall satisfaction",
    "Ease of use",
    "Performance / speed",
    "Support quality",
    "Likelihood to recommend",
]

BG = "#f4f6fa"
SIDEBAR = "#16203a"
ACCENT = "#2f5fc4"
TEXT = "#111827"       # near-black for maximum readability
MUTED = "#374151"      # dark grey (still high contrast)

FONT_FAMILY = "TkDefaultFont"


def pick_font():
    """Choose the first clean, widely available font installed on this PC."""
    global FONT_FAMILY
    from tkinter import font as tkfont
    installed = set(tkfont.families())
    for name in ("Segoe UI", "Calibri", "Helvetica Neue", "Arial",
                 "DejaVu Sans", "Verdana"):
        if name in installed:
            FONT_FAMILY = name
            return


def F(size, bold=False):
    """Font helper: F(14) normal, F(14, True) bold."""
    return (FONT_FAMILY, size, "bold" if bold else "normal")


# ---------------- data layer ----------------

def load_records():
    records = []
    if not os.path.exists(DATA_FILE):
        return records
    with open(DATA_FILE, newline="") as f:
        for row in csv.reader(f):
            try:
                ts = datetime.strptime(row[0], FMT)
                ratings = [int(x) for x in row[1:1 + len(QUESTIONS)]]
                if len(ratings) == len(QUESTIONS):
                    records.append((ts, ratings))
            except (ValueError, IndexError):
                continue
    return records


def save_record(ts, ratings):
    with open(DATA_FILE, "a", newline="") as f:
        csv.writer(f).writerow([ts.strftime(FMT), *ratings])


def in_range(records, start, end):
    return [r for r in records if start <= r[0] < end]


def averages(records):
    if not records:
        return None
    n = len(records)
    return [sum(r[1][q] for r in records) / n for q in range(len(QUESTIONS))]


def overall(avgs):
    return sum(avgs) / len(avgs)


# ---------------- GUI ----------------

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        pick_font()
        self.title("Survey Manager")
        self.geometry("1150x740")
        self.minsize(980, 640)
        self.configure(bg=BG)

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TProgressbar", thickness=24, troughcolor="#d5dbe8",
                        background=ACCENT)
        style.configure("Treeview", rowheight=34, font=F(13))
        style.configure("Treeview.Heading", font=F(13, True))

        self._build_sidebar()
        self.content = tk.Frame(self, bg=BG)
        self.content.pack(side="left", fill="both", expand=True, padx=24, pady=20)

        self.protocol("WM_DELETE_WINDOW", self.quit_app)
        self.show_week()

    # ----- layout helpers -----

    def _build_sidebar(self):
        bar = tk.Frame(self, bg=SIDEBAR, width=290)
        bar.pack(side="left", fill="y")
        bar.pack_propagate(False)
        tk.Label(bar, text="SURVEY\nMANAGER", bg=SIDEBAR, fg="white",
                 font=F(22, True), pady=28).pack()

        items = [
            ("1  Last week's results", self.show_week),
            ("2  Re-survey now", self.show_survey),
            ("3  Three-month summary", self.show_summary),
            ("4  Developer tools", self.show_dev),
        ]
        for text, cmd in items:
            self._side_button(bar, text, cmd)

        tk.Frame(bar, bg=SIDEBAR).pack(expand=True, fill="y")
        self._side_button(bar, "5  Quit", self.quit_app, bg="#a63d3d")
        tk.Frame(bar, bg=SIDEBAR, height=16).pack()

    def _side_button(self, parent, text, cmd, bg=SIDEBAR):
        btn = tk.Button(parent, text=text, command=cmd, anchor="w", padx=22,
                        bg=bg, fg="white", activebackground=ACCENT,
                        activeforeground="white", relief="flat", bd=0,
                        font=F(15, True), cursor="hand2", pady=14)
        btn.pack(fill="x", pady=1)

    def clear(self, title, subtitle=""):
        for w in self.content.winfo_children():
            w.destroy()
        tk.Label(self.content, text=title, bg=BG, fg=TEXT,
                 font=F(28, True)).pack(anchor="w")
        if subtitle:
            tk.Label(self.content, text=subtitle, bg=BG, fg=MUTED,
                     font=F(13)).pack(anchor="w", pady=(0, 10))

    def score_rows(self, parent, avgs):
        grid = tk.Frame(parent, bg=BG)
        grid.pack(fill="x", pady=6)
        grid.columnconfigure(1, weight=1)
        for i, (q, a) in enumerate(zip(QUESTIONS, avgs)):
            tk.Label(grid, text=q, bg=BG, fg=TEXT, anchor="w", width=24,
                     font=F(13)).grid(row=i, column=0, sticky="w", pady=4)
            ttk.Progressbar(grid, maximum=5, value=a).grid(
                row=i, column=1, sticky="ew", padx=10)
            tk.Label(grid, text=f"{a:.2f} / 5", bg=BG,
                     font=F(13, True)).grid(row=i, column=2)
        tk.Label(parent, text=f"Overall score: {overall(avgs):.2f} / 5", bg=BG,
                 fg=ACCENT, font=F(16, True)).pack(anchor="w", pady=6)

    def records_table(self, parent, records, height=8):
        cols = ("when",) + tuple(f"Q{i}" for i in range(1, len(QUESTIONS) + 1))
        tree = ttk.Treeview(parent, columns=cols, show="headings", height=height)
        tree.heading("when", text="Date / time")
        tree.column("when", width=150, anchor="w")
        for i in range(1, len(QUESTIONS) + 1):
            tree.heading(f"Q{i}", text=f"Q{i}")
            tree.column(f"Q{i}", width=50, anchor="center")
        for ts, ratings in sorted(records, reverse=True):
            tree.insert("", "end", values=(ts.strftime(FMT), *ratings))
        scroll = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        return tree

    # ----- 1. last week -----

    def show_week(self):
        self.clear("Last week's survey results", "Responses from the past 7 days")
        now = datetime.now()
        week = in_range(load_records(), now - timedelta(days=7),
                        now + timedelta(seconds=1))
        if not week:
            tk.Label(self.content, bg=BG, fg=MUTED, font=F(14),
                     justify="left",
                     text="No surveys were recorded in the last 7 days.\n"
                          "Use 'Re-survey now' or add sample data in Developer tools."
                     ).pack(anchor="w", pady=20)
            return
        tk.Label(self.content, text=f"{len(week)} responses", bg=BG,
                 font=F(13, True)).pack(anchor="w")
        self.score_rows(self.content, averages(week))
        tk.Label(self.content, text="Individual responses", bg=BG,
                 font=F(13, True)).pack(anchor="w", pady=(8, 2))
        holder = tk.Frame(self.content, bg=BG)
        holder.pack(fill="both", expand=True)
        self.records_table(holder, week)

    # ----- 2. re-survey -----

    def show_survey(self):
        self.clear("Re-survey", "Rate each item: 1 = poor ... 5 = excellent")
        self.vars = []
        card = tk.Frame(self.content, bg="white", padx=20, pady=16,
                        highlightbackground="#dfe4ee", highlightthickness=1)
        card.pack(fill="x", pady=6)
        for i, q in enumerate(QUESTIONS):
            var = tk.IntVar(value=0)
            self.vars.append(var)
            row = tk.Frame(card, bg="white")
            row.pack(fill="x", pady=6)
            tk.Label(row, text=f"{i + 1}. {q}", bg="white", fg=TEXT, width=26,
                     anchor="w", font=F(13)).pack(side="left")
            for v in range(1, 6):
                tk.Radiobutton(row, text=str(v), variable=var, value=v,
                               bg="white", fg=TEXT, font=F(13, True),
                               activebackground="white").pack(side="left", padx=6)
        tk.Button(self.content, text="Submit survey", command=self.submit_survey,
                  bg=ACCENT, fg="white", relief="flat", padx=20, pady=8,
                  font=F(14, True), cursor="hand2"
                  ).pack(anchor="w", pady=14)

    def submit_survey(self):
        ratings = [v.get() for v in self.vars]
        if 0 in ratings:
            messagebox.showwarning("Incomplete", "Please answer every question.")
            return
        save_record(datetime.now(), ratings)
        messagebox.showinfo("Thank you", "Your response has been saved.")
        self.show_survey()

    # ----- 3. three-month summary -----

    def show_summary(self):
        self.clear("Three-month summary", "Responses from the past 90 days")
        now = datetime.now()
        end = now + timedelta(seconds=1)
        records = in_range(load_records(), now - timedelta(days=90), end)
        if not records:
            tk.Label(self.content, bg=BG, fg=MUTED, font=F(14),
                     text="No surveys were recorded in the last 90 days."
                     ).pack(anchor="w", pady=20)
            return

        tk.Label(self.content, text=f"{len(records)} responses", bg=BG,
                 font=F(13, True)).pack(anchor="w")
        self.score_rows(self.content, averages(records))

        labels = ["60-90 days ago", "30-60 days ago", "Last 30 days"]
        scores, counts = [], []
        for i in range(3):
            start = now - timedelta(days=30 * (3 - i))
            stop = end if i == 2 else now - timedelta(days=30 * (2 - i))
            chunk = in_range(records, start, stop)
            counts.append(len(chunk))
            scores.append(overall(averages(chunk)) if chunk else None)

        canvas = tk.Canvas(self.content, bg="white", height=230,
                           highlightbackground="#dfe4ee", highlightthickness=1)
        canvas.pack(fill="x", pady=8)
        canvas.update_idletasks()
        w = max(canvas.winfo_width(), 600)
        for i, (label, s) in enumerate(zip(labels, scores)):
            x0 = 70 + i * (w - 140) / 3
            x1 = x0 + 110
            if s is not None:
                top = 180 - s / 5 * 140
                canvas.create_rectangle(x0, top, x1, 180, fill=ACCENT, outline="")
                canvas.create_text((x0 + x1) / 2, top - 10,
                                   text=f"{s:.2f} ({counts[i]})",
                                   font=F(11, True))
            else:
                canvas.create_text((x0 + x1) / 2, 160, text="no data",
                                   fill=MUTED, font=F(12))
            canvas.create_text((x0 + x1) / 2, 208, text=label,
                               font=F(11))

        if scores[0] is not None and scores[2] is not None:
            diff = scores[2] - scores[0]
            word, color = (("IMPROVING", "#2e8b57") if diff > 0.05 else
                           ("DECLINING", "#b03a3a") if diff < -0.05 else
                           ("STABLE", "#5b6478"))
            tk.Label(self.content, text=f"Trend: {word} ({diff:+.2f})", bg=BG,
                     fg=color, font=F(16, True)).pack(anchor="w")

    # ----- 4. developer tools -----

    def show_dev(self):
        self.clear("Developer tools", "Test data, export and reset")
        bar = tk.Frame(self.content, bg=BG)
        bar.pack(fill="x", pady=6)
        for text, cmd in [("Generate sample data", self.dev_generate),
                          ("Export to CSV", self.dev_export),
                          ("Clear all data", self.dev_clear),
                          ("Refresh", self.show_dev)]:
            tk.Button(bar, text=text, command=cmd, relief="flat", bg="#d9e1f2", fg=TEXT,
                      padx=16, pady=10, font=F(13, True),
                      cursor="hand2").pack(side="left", padx=(0, 10))
        records = load_records()
        tk.Label(self.content, text=f"All records ({len(records)})", bg=BG,
                 font=F(13, True)).pack(anchor="w", pady=(10, 2))
        holder = tk.Frame(self.content, bg=BG)
        holder.pack(fill="both", expand=True)
        self.records_table(holder, records, height=14)

    def dev_generate(self):
        count = simpledialog.askinteger("Sample data", "How many records (1-500)?",
                                        minvalue=1, maxvalue=500, parent=self)
        if not count:
            return
        now = datetime.now()
        for _ in range(count):
            ts = now - timedelta(seconds=random.randint(0, 90 * 86400))
            save_record(ts, [random.randint(1, 5) for _ in QUESTIONS])
        self.show_dev()

    def dev_export(self):
        records = sorted(load_records())
        with open(EXPORT_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "satisfaction", "ease",
                             "performance", "support", "recommend"])
            for ts, ratings in records:
                writer.writerow([ts.strftime(FMT), *ratings])
        messagebox.showinfo("Exported",
                            f"Saved {len(records)} records to {EXPORT_FILE}")

    def dev_clear(self):
        if messagebox.askyesno("Clear data", "Delete ALL survey data?"):
            open(DATA_FILE, "w").close()
            self.show_dev()

    # ----- 5. quit -----

    def quit_app(self):
        if messagebox.askyesno("Quit", "Are you sure you want to quit?"):
            self.destroy()


if __name__ == "__main__":
    App().mainloop()