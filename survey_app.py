"""
Survey Manager - a simple menu-driven console app in Python

 1. Last week's survey results
 2. Re-survey now
 3. Summary of the last three months
 4. Developer tools
 5. Quit

Run:  python survey_app.py
Data is stored in survey_data.csv (timestamp + one rating per question).
"""

import csv
import os
import random
import sys
from datetime import datetime, timedelta

DATA_FILE = "survey_data.csv"
EXPORT_FILE = "survey_export.csv"

QUESTIONS = [
    "Overall satisfaction",
    "Ease of use",
    "Performance / speed",
    "Support quality",
    "Likelihood to recommend",
]
FMT = "%Y-%m-%d %H:%M"


# ---------- input helpers ----------

def read_int(prompt, lo, hi):
    while True:
        try:
            value = int(input(prompt).strip())
            if lo <= value <= hi:
                return value
        except ValueError:
            pass
        except EOFError:
            print()
            sys.exit(0)
        print(f"  Please enter a number from {lo} to {hi}.")


def pause():
    try:
        input("\nPress Enter to continue...")
    except EOFError:
        sys.exit(0)


# ---------- storage ----------

def load_records():
    """Return a list of (datetime, [ratings]) tuples."""
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
                continue  # skip damaged lines
    return records


def save_record(ts, ratings):
    with open(DATA_FILE, "a", newline="") as f:
        csv.writer(f).writerow([ts.strftime(FMT), *ratings])


# ---------- statistics ----------

def in_range(records, start, end):
    return [r for r in records if start <= r[0] < end]


def averages(records):
    if not records:
        return None
    n = len(records)
    return [sum(r[1][q] for r in records) / n for q in range(len(QUESTIONS))]


def overall(avgs):
    return sum(avgs) / len(avgs)


def bar(value):
    filled = round(value)
    return "[" + "#" * filled + "." * (5 - filled) + "]"


def print_averages(avgs):
    for question, avg in zip(QUESTIONS, avgs):
        print(f"  {question:<26} {avg:.2f} / 5  {bar(avg)}")


# ---------- menu actions ----------

def last_week_results():
    now = datetime.now()
    week = in_range(load_records(), now - timedelta(days=7), now + timedelta(seconds=1))

    print("\n=== LAST WEEK'S SURVEY RESULTS ===")
    if not week:
        print("No surveys were recorded in the last 7 days.")
        print("Use option 2 to take a survey, or Developer Tools to add sample data.")
    else:
        print(f"Responses: {len(week)}\n")
        avgs = averages(week)
        print_averages(avgs)
        print(f"\n  Overall score: {overall(avgs):.2f} / 5")
        print("\nIndividual responses:")
        for ts, ratings in sorted(week):
            print(f"  {ts.strftime(FMT)}  ->  {' '.join(map(str, ratings))}")
    pause()


def re_survey():
    print("\n=== RE-SURVEY (rate each item 1 = poor ... 5 = excellent) ===")
    ratings = [read_int(f"  {i}. {q}: ", 1, 5) for i, q in enumerate(QUESTIONS, 1)]
    save_record(datetime.now(), ratings)
    print("\nThank you! Your response has been saved.")
    pause()


def three_month_summary():
    now = datetime.now()
    end = now + timedelta(seconds=1)
    records = in_range(load_records(), now - timedelta(days=90), end)

    print("\n=== SUMMARY OF THE LAST THREE MONTHS ===")
    if not records:
        print("No surveys were recorded in the last 90 days.")
        pause()
        return

    print(f"Total responses: {len(records)}\n")
    print("Average per question (90 days):")
    avgs = averages(records)
    print_averages(avgs)
    print(f"\n  Overall: {overall(avgs):.2f} / 5\n")

    print("Month-by-month:")
    labels = ["60-90 days ago", "30-60 days ago", "Last 30 days  "]
    scores = []
    for i, label in enumerate(labels):
        start = now - timedelta(days=30 * (3 - i))
        stop = end if i == 2 else now - timedelta(days=30 * (2 - i))
        chunk = in_range(records, start, stop)
        if chunk:
            score = overall(averages(chunk))
            scores.append(score)
            print(f"  {label} : {len(chunk):3d} responses, overall {score:.2f}")
        else:
            scores.append(None)
            print(f"  {label} : no data")

    if scores[0] is not None and scores[2] is not None:
        diff = scores[2] - scores[0]
        trend = "IMPROVING" if diff > 0.05 else "DECLINING" if diff < -0.05 else "STABLE"
        print(f"\nTrend: {trend} ({diff:+.2f} over the period)")
    pause()


# ---------- developer tools ----------

def dev_list_all():
    records = sorted(load_records())
    print(f"\n--- All records ({len(records)}) ---")
    for i, (ts, ratings) in enumerate(records, 1):
        print(f"  #{i:03d} {ts.strftime(FMT)}  ->  {' '.join(map(str, ratings))}")


def dev_generate():
    count = read_int("How many sample records (1-500)? ", 1, 500)
    now = datetime.now()
    for _ in range(count):
        ts = now - timedelta(seconds=random.randint(0, 90 * 86400))
        save_record(ts, [random.randint(1, 5) for _ in QUESTIONS])
    print(f"Added {count} random records spread over the last 90 days.")


def dev_export_csv():
    records = sorted(load_records())
    with open(EXPORT_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "satisfaction", "ease", "performance", "support", "recommend"])
        for ts, ratings in records:
            writer.writerow([ts.strftime(FMT), *ratings])
    print(f"Exported {len(records)} records to {EXPORT_FILE}")


def dev_clear():
    if read_int("Delete ALL survey data? (1 = yes, 0 = no): ", 0, 1):
        open(DATA_FILE, "w").close()
        print("All data cleared.")
    else:
        print("Cancelled.")


def developer_tools():
    actions = {1: dev_list_all, 2: dev_generate, 3: dev_export_csv, 4: dev_clear}
    while True:
        print("\n=== DEVELOPER TOOLS ===")
        print(" 1. List all raw records")
        print(" 2. Generate random sample data")
        print(" 3. Export data to CSV")
        print(" 4. Clear all data")
        print(" 5. Back to main menu")
        choice = read_int("Choose: ", 1, 5)
        if choice == 5:
            return
        actions[choice]()


# ---------- main ----------

def main():
    actions = {
        1: last_week_results,
        2: re_survey,
        3: three_month_summary,
        4: developer_tools,
    }
    while True:
        print("\n==============================")
        print("       SURVEY MANAGER")
        print("==============================")
        print(" 1. Last week's survey results")
        print(" 2. Re-survey now")
        print(" 3. Summary of last three months")
        print(" 4. Developer tools")
        print(" 5. Quit")
        choice = read_int("Choose an option: ", 1, 5)
        if choice == 5:
            print("Goodbye!")
            return
        actions[choice]()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nGoodbye!")