"""
01 — Data Cleaning Pipeline
===========================
Input:  data/raw_jobs.csv
Output: data/cleaned_jobs.csv

Run:
    python notebooks/01_data_cleaning.py
"""

import re
from pathlib import Path
from collections import Counter

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns

matplotlib.use("Agg")
plt.style.use("ggplot")
sns.set_palette("Set2")



PROJECT = Path(__file__).resolve().parent.parent
DATA = PROJECT / "data"
RAW = DATA / "raw_jobs.csv"
CLEANED = DATA / "cleaned_jobs.csv"
SKILL_DICT = DATA / "skills_dictionary.csv"
DASHBOARD = PROJECT / "dashboard"
SCREENSHOTS = DASHBOARD / "screenshots"

CITY_MAP = {
    "HCM": "Ho Chi Minh City",
    "HN": "Ha Noi",
    "Đà Nẵng": "Da Nang",
    "Hải Phòng": "Hai Phong",
    "Cần Thơ": "Can Tho",
    "Huế": "Hue",
    "Nha Trang": "Nha Trang",
    "Online": "Remote",
    "Toàn Quốc": "Nationwide",
}

LEVEL_ORDER = ["Internship", "Fresher", "Junior", "Mid-level", "Senior", "Manager"]


def _safe_print(label: str, mapping: dict) -> None:
    """Print a dict summary, replacing non-ASCII with '?' to avoid terminal errors."""
    try:
        items = {str(k)[:30]: v for k, v in mapping.items()}
        print(f"{label}", items)
    except UnicodeEncodeError:
        # Fallback: print counts only
        print(f"{label} {len(mapping)} entries (Vietnamese chars in terminal)")


# ──────────────────────────────────────────────────────────────────────
# Loading
# ──────────────────────────────────────────────────────────────────────

def load_raw_data() -> pd.DataFrame:
    """Load the raw crawler output."""
    if not RAW.exists():
        raise FileNotFoundError(f"{RAW} not found. Run the crawler first: python crawler/crawl_jobs.py")

    df = pd.read_csv(RAW)
    print(f"[load]  {len(df):,} rows from {RAW.name}")
    print(f"[load]  columns: {list(df.columns)}")
    return df


# ──────────────────────────────────────────────────────────────────────
# Cleaning steps
# ──────────────────────────────────────────────────────────────────────

def drop_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    df = df.drop_duplicates(subset=["job_url"])
    dropped = before - len(df)
    if dropped:
        print(f"[dedup] {dropped} duplicates removed ({before} → {len(df)})")
    return df


def normalize_city(raw: str | float | None) -> str:
    if pd.isna(raw) or not str(raw).strip():
        return ""
    first = str(raw).split("/")[0].split("-")[0].split(",")[0].strip()
    return CITY_MAP.get(first, first)


def add_city_column(df: pd.DataFrame) -> pd.DataFrame:
    df["city"] = df["location"].apply(normalize_city)
    top = df["city"].value_counts().head(10)
    _safe_print("[city]  top cities:", dict(top))
    return df


def flag_salary_disclosure(df: pd.DataFrame) -> pd.DataFrame:
    df["is_salary_public"] = df["salary_min"].notna()
    pct = df["is_salary_public"].mean() * 100
    print(f"[salary] disclosed: {df['is_salary_public'].sum():,} / {len(df):,} ({pct:.1f}%)")
    return df


def normalize_work_model(df: pd.DataFrame) -> pd.DataFrame:
    allowed = {"Remote", "Hybrid", "Onsite"}
    df["work_model"] = df["work_model"].apply(
        lambda v: v if v in allowed else "Unknown"
    )
    _safe_print("[wm]    ", dict(df["work_model"].value_counts()))
    return df


def load_skill_dictionary() -> dict[str, str]:
    """Return {raw_skill_lower: normalized_skill}."""
    if not SKILL_DICT.exists():
        print(f"[warn]  {SKILL_DICT.name} not found — skills will not be normalized")
        return {}

    skill_df = pd.read_csv(SKILL_DICT)
    mapping = {}
    for _, row in skill_df.iterrows():
        key = str(row["raw_skill"]).strip().lower()
        val = str(row["normalized_skill"]).strip()
        if key and val:
            mapping[key] = val
    print(f"[skill]  loaded {len(mapping)} entries from {SKILL_DICT.name}")
    return mapping


def normalize_skills_str(skills_str: str | None, mapping: dict[str, str]) -> list[str]:
    if pd.isna(skills_str) or not str(skills_str).strip():
        return []
    raw = [s.strip().lower() for s in re.split(r"[;,]", str(skills_str)) if s.strip()]
    # keep order, dedupe
    seen = set()
    result = []
    for s in raw:
        norm = mapping.get(s, s)
        if norm not in seen:
            seen.add(norm)
            result.append(norm)
    return result


def add_skills_column(df: pd.DataFrame) -> pd.DataFrame:
    mapping = load_skill_dictionary()
    df["skills_list"] = df["skills"].apply(lambda s: normalize_skills_str(s, mapping))
    df["skill_count"] = df["skills_list"].apply(len)
    total_skills = df["skill_count"].sum()
    print(f"[skill]  {total_skills:,} total skill occurrences across {len(df)} jobs")
    return df


def normalize_experience(df: pd.DataFrame) -> pd.DataFrame:
    df["experience_level"] = df["experience_level"].fillna("Unknown")
    counts = df["experience_level"].value_counts()
    _safe_print("[exp]   ", dict(counts.sort_index()))
    return df


# ──────────────────────────────────────────────────────────────────────
# Output
# ──────────────────────────────────────────────────────────────────────

def build_output(df: pd.DataFrame) -> pd.DataFrame:
    """Select, order, and serialize cleaned columns."""
    df = df.copy()
    df.insert(0, "job_id", range(1, len(df) + 1))

    # Flatten skills_list → semicolon string for CSV
    df["skills_normalized"] = df["skills_list"].apply(lambda lst: "; ".join(lst))

    columns = [
        "job_id",
        "job_title",
        "company_name",
        "city",
        "salary_min",
        "salary_max",
        "is_salary_public",
        "experience_level",
        "work_model",
        "skills_normalized",
        "skill_count",
        "posted_date",
        "job_url",
        "description",
    ]
    return df[columns]


def save_cleaned(df: pd.DataFrame) -> None:
    df.to_csv(CLEANED, index=False, encoding="utf-8-sig")
    print(f"\n[save]  {len(df):,} rows -> {CLEANED.name}")


# ──────────────────────────────────────────────────────────────────────
# Main pipeline
# ──────────────────────────────────────────────────────────────────────

def run_pipeline() -> None:
    print("=" * 60)
    print("01 — Data Cleaning Pipeline")
    print("=" * 60)

    df = load_raw_data()
    df = drop_duplicates(df)
    df = add_city_column(df)
    df = flag_salary_disclosure(df)
    df = normalize_work_model(df)
    df = add_skills_column(df)
    df = normalize_experience(df)

    out = build_output(df)
    save_cleaned(out)

    print("\nDone.")
    

"""
02 — Analysis & Insights
=========================
Input:  data/cleaned_jobs.csv
Output: chart PNGs → dashboard/

Run:
    python notebooks/02_analysis.py
"""


# ──────────────────────────────────────────────────────────────────────
# Loading
# ──────────────────────────────────────────────────────────────────────

def load_data() -> pd.DataFrame:
    if not CLEANED.exists():
        raise FileNotFoundError(
            f"{CLEANED} not found. Run cleaning first: python notebooks/01_data_cleaning.py"
        )
    df = pd.read_csv(CLEANED)
    df["is_salary_public"] = df["is_salary_public"].astype(bool)
    print(f"[load] {len(df):,} cleaned rows")
    return df


def parse_skills(skills_str: str | None) -> list[str]:
    if pd.isna(skills_str) or not skills_str.strip():
        return []
    return [s.strip() for s in skills_str.split(";") if s.strip()]


def _save(fig, name: str) -> None:
    path = SCREENSHOTS / name
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"  saved -> {path.name}")
    plt.close(fig)


# ──────────────────────────────────────────────────────────────────────
# Charts
# ──────────────────────────────────────────────────────────────────────

def chart_top_skills(df: pd.DataFrame, top_n: int = 15) -> None:
    """Top N most demanded skills."""
    all_skills: list[str] = []
    for s in df["skills_normalized"].dropna():
        all_skills.extend(parse_skills(s))

    counts = Counter(all_skills).most_common(top_n)
    if not counts:
        print("[chart] no skills data — skipping top skills")
        return

    names, vals = zip(*reversed(counts))
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(names, vals)
    ax.set_xlabel("Job Count")
    ax.set_title(f"Top {top_n} Most Demanded Skills")
    _save(fig, "chart_top_skills.png")


def chart_jobs_by_city(df: pd.DataFrame) -> None:
    top = df["city"].value_counts().head(10)
    fig, ax = plt.subplots(figsize=(8, 5))
    top.plot.bar(ax=ax)
    ax.set_title("Top 10 Hiring Cities")
    ax.set_ylabel("Job Count")
    ax.tick_params(axis="x", rotation=45)
    _save(fig, "chart_cities.png")


def chart_work_model(df: pd.DataFrame) -> None:
    wm = df["work_model"].value_counts()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    wm.plot.pie(ax=ax1, autopct="%1.1f%%", startangle=90)
    ax1.set_ylabel("")
    wm.plot.bar(ax=ax2)
    ax2.set_title("Work Model Distribution")
    ax2.tick_params(axis="x", rotation=0)
    _save(fig, "chart_work_model.png")


def chart_experience_level(df: pd.DataFrame) -> None:
    exp = df[df["experience_level"] != "Unknown"]["experience_level"]
    fig, ax = plt.subplots(figsize=(8, 4))
    order = ["Internship", "Fresher", "Junior", "Mid-level", "Senior", "Manager"]
    counts = exp.value_counts()
    ordered = pd.Series({k: counts.get(k, 0) for k in order})
    ordered.plot.bar(ax=ax)
    ax.set_title("Jobs by Experience Level")
    ax.set_xlabel("")
    ax.tick_params(axis="x", rotation=30)
    _save(fig, "chart_experience.png")


def chart_salary_by_level(df: pd.DataFrame) -> None:
    sal = df[df["is_salary_public"] & (df["experience_level"] != "Unknown")].copy()
    if sal.empty:
        print("[chart] no salary data — skipping salary chart")
        return

    sal["avg_salary"] = (sal["salary_min"] + sal["salary_max"]) / 2
    order = ["Internship", "Fresher", "Junior", "Mid-level", "Senior", "Manager"]

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.boxplot(data=sal, x="experience_level", y="avg_salary", order=order, ax=ax)
    ax.set_title("Salary Range by Experience Level (Million VND/month)")
    ax.set_xlabel("")
    ax.set_ylabel("Average Salary (Million VND)")
    _save(fig, "chart_salary_by_level.png")


def chart_salary_disclosure(df: pd.DataFrame) -> None:
    disclosed = df["is_salary_public"].sum()
    total = len(df)
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie(
        [disclosed, total - disclosed],
        labels=["Disclosed", "Not Disclosed"],
        autopct="%1.1f%%",
        startangle=90,
        colors=["#4CAF50", "#E0E0E0"],
    )
    ax.set_title("Salary Disclosure Rate")
    _save(fig, "chart_disclosure.png")


def chart_skills_by_level(df: pd.DataFrame) -> None:
    """Entry-level vs senior skill comparison."""
    entry = df[df["experience_level"].isin(["Internship", "Fresher"])]
    senior = df[df["experience_level"].isin(["Senior", "Manager"])]

    def _gather(data: pd.DataFrame) -> list[tuple[str, int]]:
        skills: list[str] = []
        for s in data["skills_normalized"].dropna():
            skills.extend(parse_skills(s))
        return Counter(skills).most_common(10)

    entry_skills = _gather(entry)
    senior_skills = _gather(senior)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    if entry_skills:
        na, va = zip(*reversed(entry_skills))
        ax1.barh(na, va)
    ax1.set_title("Entry-level (Intern/Fresher)")

    if senior_skills:
        ns, vs = zip(*reversed(senior_skills))
        ax2.barh(ns, vs)
    ax2.set_title("Senior / Manager")

    _save(fig, "chart_skills_by_level.png")


# ──────────────────────────────────────────────────────────────────────
# Summary
# ──────────────────────────────────────────────────────────────────────

def print_summary(df: pd.DataFrame) -> None:
    disclosed = df["is_salary_public"].sum()
    total = len(df)

    print("\n" + "=" * 50)
    print("VIETNAM IT JOB MARKET — SUMMARY")
    print("=" * 50)
    print(f"  Total jobs analyzed:      {total:,}")
    print(f"  Companies represented:    {df['company_name'].nunique():,}")
    print(f"  Cities represented:       {df['city'].nunique()}")
    print(f"  Salary disclosure rate:   {disclosed/total*100:.1f}%")
    print()

    print("Top 5 cities:")
    for city, cnt in df["city"].value_counts().head(5).items():
        print(f"  {city:30s} {cnt}")
    print()

    print("Work model distribution:")
    for wm, cnt in df["work_model"].value_counts().items():
        print(f"  {wm:10s} {cnt:5d}  ({cnt/total*100:.1f}%)")
    print()


# ──────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────

def run_analysis() -> None:
    print("=" * 50)
    print("02 — Analysis & Insights")
    print("=" * 50)

    DASHBOARD.mkdir(parents=True, exist_ok=True)

    df = load_data()

    charts = [
        ("Top skills",      chart_top_skills,       df),
        ("Cities",          chart_jobs_by_city,     df),
        ("Work model",      chart_work_model,       df),
        ("Experience",      chart_experience_level, df),
        ("Salary by level", chart_salary_by_level,  df),
        ("Disclosure",      chart_salary_disclosure,df),
        ("Skills by level", chart_skills_by_level,  df),
    ]

    for label, func, *args in charts:
        print(f"\n[chart] {label} ...")
        try:
            func(*args)
        except Exception as exc:
            print(f"  [!] failed: {exc}")

    print_summary(df)
    print(f"\nCharts saved to {DASHBOARD}/")


if __name__ == "__main__":
    run_pipeline()
    run_analysis()
