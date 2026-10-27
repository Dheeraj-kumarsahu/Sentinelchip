# Survey Manager (Python + Tkinter)

A desktop application built with **Python and Tkinter** for collecting, reviewing and summarising survey responses. It has a clean sidebar menu, large readable fonts, progress bars, a bar chart and a built-in developer tool, so the results can be shown clearly during a demo or presentation.

---

## Features

| # | Menu option | What it does |
|---|-------------|--------------|
| 1 | **Last week's results** | Shows the average score for each question (with progress bars), the overall score, and a table of every response from the past 7 days. |
| 2 | **Re-survey now** | A form with 5 questions rated 1 (poor) to 5 (excellent). It will not submit until every question is answered. |
| 3 | **Three-month summary** | Shows the 90-day averages, a bar chart of the three 30-day periods, and a trend: Improving, Stable or Declining. |
| 4 | **Developer tools** | Generate random sample data, export all data to CSV, clear all data, and view every raw record in a table. |
| 5 | **Quit** | Closes the app after asking for confirmation. |

### Other highlights
- Large, high-contrast fonts for good visibility on a projector.
- Automatically picks a clean font that is installed on the computer (Segoe UI, Calibri, Helvetica Neue, Arial, DejaVu Sans or Verdana).
- Data is saved in a plain CSV file, so it is easy to open in Excel or Google Sheets.
- Damaged lines in the data file are skipped instead of crashing the app.

---

## Technologies Used

- **Language:** Python 3
- **GUI library:** Tkinter (with `ttk` widgets: Progressbar, Treeview, Scrollbar)
- **Standard library modules:** `csv`, `os`, `random`, `datetime`, `tkinter.messagebox`, `tkinter.simpledialog`
- **Storage:** CSV file (`survey_data.csv`)

No third-party packages are needed.

---

## Requirements

- Python 3.8 or newer
- Tkinter (included with the standard Python installer on Windows and macOS)

On Linux, Tkinter may need to be installed separately:

```bash
sudo apt install python3-tk
```

---

## How to Run

1. Download or clone the project folder.
2. Open a terminal in that folder.
3. Run:

```bash
python survey_app_gui.py
```

(On some systems use `python3 survey_app_gui.py`.)

### First-time use
There is no data on the first run. To see the charts and tables straight away:

1. Click **4 Developer tools**.
2. Click **Generate sample data** and enter a number, for example `40`.
3. Go back to **1 Last week's results** and **3 Three-month summary**.

---

## Project Structure

```
survey-manager/
├── survey_app_gui.py     # Tkinter desktop app (main project)
├── survey_app.py         # Console version in Python (optional)
├── survey_app.c          # Console version in C (optional)
├── survey_data.csv       # Created automatically when the first response is saved
├── survey_export.csv     # Created when you use "Export to CSV"
└── README.md
```

---

## How It Works

### Data format
Each survey response is one line in `survey_data.csv`:

```
2026-10-27 14:30,4,5,3,4,5
```

The first value is the date and time. The next five values are the ratings for the five questions.

### Survey questions
1. Overall satisfaction
2. Ease of use
3. Performance / speed
4. Support quality
5. Likelihood to recommend

### Time periods
- **Last week:** responses from the past 7 days.
- **Three months:** responses from the past 90 days, split into three 30-day periods (60-90 days ago, 30-60 days ago, last 30 days).
- **Trend:** the overall score of the last 30 days compared with the 60-90 days period. A difference above +0.05 is "Improving", below -0.05 is "Declining", otherwise "Stable".

### Code layout (`survey_app_gui.py`)
- **Data layer:** `load_records()`, `save_record()`, `in_range()`, `averages()`, `overall()`
- **Font helper:** `pick_font()` and `F(size, bold)`
- **`App` class:** builds the sidebar and one method per screen: `show_week()`, `show_survey()`, `show_summary()`, `show_dev()` and `quit_app()`

---

## Customisation

- **Change the questions:** edit the `QUESTIONS` list at the top of `survey_app_gui.py`. Keep it at 5 items, or update the CSV handling if you change the count.
- **Change the font size:** all sizes go through the helper `F(size, bold)`. Increase the numbers where it is used to make the text larger.
- **Change the colours:** edit `BG`, `SIDEBAR`, `ACCENT`, `TEXT` and `MUTED` near the top of the file.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: No module named 'tkinter'` | Install Tkinter: `sudo apt install python3-tk` (Linux), or reinstall Python with the "tcl/tk" option (Windows/macOS). |
| Window shows "No surveys were recorded" | Add data with **Re-survey now** or **Developer tools > Generate sample data**. |
| Want to start fresh | Use **Developer tools > Clear all data**, or delete `survey_data.csv`. |
| Text looks too small or too large | Adjust the numbers passed to `F(...)` in the code. |

---

## Possible Future Improvements

- Add more charts (line graph of scores over time).
- Let the user create their own survey questions from inside the app.
- Add user names or departments to each response.
- Store data in SQLite instead of CSV.
- Package the app as a standalone `.exe` with PyInstaller.

---

## Author

**Your Name**
B.Tech Computer Science Engineering
Your College Name

---

## License

This project is for educational purposes. Add a license of your choice (for example MIT) if you plan to share it publicly.
