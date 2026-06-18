# Vietnam IT Job Market Analytics

A data pipeline + dashboard that collects, cleans, and analyzes IT job postings from [ybox.vn](https://ybox.vn/tuyen-dung).

## Overview

This project crawls IT job postings, cleans the data, provides SQL analytics, and visualizes insights through an interactive Streamlit dashboard. It answers questions like:

- Which IT skills are most in demand?
- What are the salary ranges by role and experience level?
- How does the remote/hybrid/onsite ratio look?
- Which cities have the most IT job openings?

## Motivation

Understanding the IT job market is critical for students, job seekers, and employers. This project demonstrates a complete data engineering pipeline — from web crawling to production dashboards — focused on the Vietnam IT hiring landscape.

## Data Pipeline

```
Crawler → raw_jobs.csv → analysis.py (clean + chart) → cleaned_jobs.csv + PNGs → Dashboard
```

1. **Crawler** (`crawler/crawl_jobs.py`): Playwright-based crawler hits ybox.vn CDN API, collecting ~6,000 job postings. Supports `-page N` CLI flag for limiting pages during development.
2. **Cleaning + Analysis** (`analysis.py`): Normalizes locations, salaries, skills, and experience levels; generates 7 chart PNGs to `dashboard/screenshots/`.
3. **SQL** (`sql/`): Schema and business queries for structured analysis.
4. **Dashboard** (`dashboard/app.py`): Streamlit app with Overview, Skills, and Salary pages.

## Dataset

| Metric | Value |
|--------|-------|
| Total jobs available | ~6,000 |
| Fields collected | 13 (title, company, location, salary, skills, etc.) |
| Source | ybox.vn CDN API |
| Date collected | June 2026 |

## Key Features

- Rate-limited Playwright crawler with checkpoint recovery
- Pure-function parsing module (`parse_job.py`) — no I/O, testable
- Skill normalization dictionary (103 entries)
- SQL schema with joined analytics queries
- Interactive Streamlit dashboard (3 pages)
- Single-script cleaning + analysis pipeline (no Jupyter dependency)

## Tech Stack

| Layer | Tools |
|-------|-------|
| Crawling | Python, Playwright |
| Processing | Pandas, NumPy |
| Storage | CSV, SQLite (SQL schema) |
| Analysis | Matplotlib, Seaborn |
| Dashboard | Streamlit |

## How to Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

### 2. Run the crawler

```bash
cd crawler
python crawl_jobs.py
```

Output: `data/raw_jobs.csv` (~6,000 rows)

To limit pages (fast iteration):
```bash
python crawl_jobs.py -page 3
```

### 3. Clean data & generate charts

```bash
python analysis.py
```

Outputs: `data/cleaned_jobs.csv` + 7 chart PNGs in `dashboard/screenshots/`

### 4. Launch dashboard

```bash
cd dashboard
streamlit run app.py
```

Open http://localhost:8501 in your browser.

## Project Structure

```
job-market-analysis/
├── analysis.py                   # Cleaning + analysis pipeline
├── crawler/
│   ├── __init__.py
│   ├── parse_job.py              # Pure parsing functions
│   └── crawl_jobs.py             # Playwright crawler + CDN API
├── data/
│   ├── raw_jobs.csv              # Raw crawler output (gitignored)
│   ├── cleaned_jobs.csv          # Post-cleaning output (gitignored)
│   └── skills_dictionary.csv     # Skill normalization lookup
├── sql/
│   ├── schema.sql                # Table definitions
│   └── queries.sql               # Business analytics queries
├── dashboard/
│   ├── app.py                    # Streamlit dashboard
│   └── screenshots/              # Chart PNGs (gitignored)
├── README.md
└── requirements.txt
```

## Key Insights (from sample analysis)

- Python, SQL, and JavaScript are among the most frequent skills.
- Ho Chi Minh City and Ha Noi dominate the IT job market.
- Most jobs are Onsite; Remote and Hybrid remain a minority.
- Many intern/fresher roles do not disclose salary ranges.

## Limitations

- Data source limited to ybox.vn — not representative of the full Vietnam IT market.
- Skill extraction relies on keyword matching in job titles (some skills may be missed).
- Salary data only partially disclosed (public listings only).
- Single crawl snapshot — does not track trends over time.
