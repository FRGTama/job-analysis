"""
Vietnam IT Job Market Dashboard — Streamlit
3 pages: Overview | Skills | Salary
"""

import subprocess
import sys
from collections import Counter
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Vietnam IT Job Market", layout="wide")
PROJECT = Path(__file__).resolve().parent.parent
RAW_PATH = PROJECT / "data/raw_jobs.csv"
CLEANED_PATH = PROJECT / "data/cleaned_jobs.csv"


# ──────────────────────────────────────────────────────────────────────
# Auto-pipeline: run crawl + analysis if data is missing
# ──────────────────────────────────────────────────────────────────────
def _run_pipeline():
    if not CLEANED_PATH.exists():
        with st.spinner("Preparing data pipeline ..."):
            if not RAW_PATH.exists():
                st.info("Crawling job data from ybox.vn (~71s for full crawl) ...")
                r = subprocess.run(
                    [sys.executable, "crawler/crawl_jobs.py"],
                    cwd=PROJECT,
                    capture_output=True,
                    text=True,
                )
                if r.returncode != 0:
                    st.error(f"Crawl failed:\n{r.stderr[-800:]}")
                    st.stop()
            st.info("Cleaning data and generating charts ...")
            r = subprocess.run(
                [sys.executable, "analysis.py"],
                cwd=PROJECT,
                capture_output=True,
                text=True,
            )
            if r.returncode != 0:
                st.error(f"Analysis failed:\n{r.stderr[-800:]}")
                st.stop()
        st.success("Pipeline complete!")
        return True
    return False


if "pipeline_done" not in st.session_state:
    st.session_state.pipeline_done = False

if not st.session_state.pipeline_done:
    if _run_pipeline():
        st.session_state.pipeline_done = True
        st.rerun()
    else:
        st.session_state.pipeline_done = True


@st.cache_data
def load_data():
    df = pd.read_csv(CLEANED_PATH)
    df["is_salary_public"] = df["is_salary_public"].astype(bool)
    return df


def parse_skills_list(skills_str):
    if pd.isna(skills_str) or skills_str.strip() == "":
        return []
    return [s.strip() for s in skills_str.split(";") if s.strip()]


# ──────────────────────────────────────────────────────────────────────
df = load_data()
st.title("Vietnam IT Job Market Analytics")
st.markdown(f"**{len(df):,}** job postings analyzed | {df['company_name'].nunique():,} companies | {df['city'].nunique()} cities")

page = st.sidebar.radio("Page", ["Overview", "Skills", "Salary"])

# ═══════════════════════════════════════════════════════════════════════
if page == "Overview":
    st.header("Job Market Overview")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Jobs", len(df))
    col2.metric("Companies", df["company_name"].nunique())
    col3.metric("Cities", df["city"].nunique())
    pct = df["is_salary_public"].mean() * 100
    col4.metric("Salary Disclosed", f"{pct:.0f}%")

    st.markdown("---")

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Top 10 Hiring Cities")
        city_counts = df["city"].value_counts().head(10)
        st.bar_chart(city_counts)

    with c2:
        st.subheader("Experience Level Distribution")
        exp = df[df["experience_level"] != "Unknown"]["experience_level"]
        st.bar_chart(exp.value_counts())

    c3, c4 = st.columns(2)

    with c3:
        st.subheader("Work Model Distribution")
        wm = df["work_model"].value_counts()
        st.bar_chart(wm)

    with c4:
        st.subheader("Salary Disclosure")
        disc = df["is_salary_public"].sum()
        st.metric("Disclosed Jobs", f"{disc:,} / {len(df):,}")
        st.progress(disc / len(df))

# ═══════════════════════════════════════════════════════════════════════
elif page == "Skills":
    st.header("Skill Demand Analysis")

    all_skills = []
    for s in df["skills_normalized"].dropna():
        all_skills.extend(parse_skills_list(s))

    skill_counts = Counter(all_skills)

    top_n = st.slider("Top N skills", 5, 50, 15)
    top = skill_counts.most_common(top_n)

    st.subheader(f"Top {top_n} Most Demanded Skills")
    chart_data = pd.DataFrame(top, columns=["Skill", "Count"])
    chart = (
    alt.Chart(chart_data)
    .mark_bar()
    .encode(
        x=alt.X("Count:Q"),
        y=alt.Y("Skill:N", sort="-x")
    )
    )
    st.altair_chart(chart, use_container_width=True)

    st.markdown("---")

    st.subheader("Skills by Experience Level")
    level_filter = st.selectbox(
        "Select Level",
        ["Internship", "Fresher", "Junior", "Mid-level", "Senior", "Manager"],
    )

    level_df = df[df["experience_level"] == level_filter]
    level_skills = []
    for s in level_df["skills_normalized"].dropna():
        level_skills.extend(parse_skills_list(s))

    if level_skills:
        lc = Counter(level_skills).most_common(10)
        lc_df = pd.DataFrame(lc, columns=["Skill", "Count"])

        chart = ( alt.Chart(lc_df).mark_bar().encode(
                x=alt.X("Count:Q"),
                y=alt.Y("Skill:N", sort="-x")
            )
        )
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info(f"No skills data for {level_filter} level")

# ═══════════════════════════════════════════════════════════════════════
elif page == "Salary":
    st.header("Salary Analysis")

    sal = df[df["is_salary_public"] & (df["experience_level"] != "Unknown")].copy()
    sal["avg_salary"] = (sal["salary_min"] + sal["salary_max"]) / 2

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Average Salary by Experience Level")
        avg_by_level = (
            sal.groupby("experience_level")["avg_salary"]
            .agg(["mean", "count"])
            .round(1)
        )
        avg_by_level.columns = ["Avg (M VND)", "Count"]
        st.dataframe(avg_by_level, use_container_width=True)

    with c2:
        st.subheader("Salary Range by Experience")
        st.bar_chart(
            sal.groupby("experience_level")["avg_salary"].mean().round(1)
        )

    st.markdown("---")

    st.subheader("Salary Range Distribution")
    st.write(
        f"Min: {sal['avg_salary'].min():.1f}M | "
        f"Median: {sal['avg_salary'].median():.1f}M | "
        f"Max: {sal['avg_salary'].max():.1f}M VND/month"
    )

    hist_data = sal["avg_salary"].dropna()
    if len(hist_data) > 0:
        import matplotlib.pyplot as plt
        import numpy as np

        fig, ax = plt.subplots(figsize=(8, 3))
        ax.hist(hist_data, bins=20, edgecolor="white")
        ax.set_xlabel("Average Salary (Million VND/month)")
        ax.set_ylabel("Jobs")
        st.pyplot(fig)

    st.markdown("---")
    st.subheader("Missing Salary by Level")
    missing_by_level = (
        df.groupby("experience_level")["is_salary_public"]
        .agg([("disclosed", "sum"), ("total", "count")])
    )
    missing_by_level["pct_disclosed"] = (
        (missing_by_level["disclosed"] / missing_by_level["total"] * 100)
        .round(1)
    )
    st.dataframe(missing_by_level, use_container_width=True)
