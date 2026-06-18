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
Crawler → raw_jobs.csv → Cleaning → cleaned_jobs.csv → SQL → Dashboard
```

1. **Crawler** (`crawler/`): Playwright-based crawler hits ybox.vn CDN API, collecting ~6,000 job postings.
2. **Cleaning** (`notebooks/01_data_cleaning.ipynb`): Normalises locations, salaries, skills, and experience levels.
3. **Analysis** (`notebooks/02_analysis.ipynb`): Exploratory analysis with charts and statistical summaries.
4. **SQL** (`sql/`): Schema and business queries for structured analysis.
5. **Dashboard** (`dashboard/app.py`): Streamlit app with Overview, Skills, and Salary pages.

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
- Skill normalization dictionary (80+ entries)
- SQL schema with joined analytics queries
- Interactive Streamlit dashboard (3 pages)
- Jupyter notebooks for reproducible analysis

## Tech Stack

| Layer | Tools |
|-------|-------|
| Crawling | Python, Playwright |
| Processing | Pandas, NumPy |
| Storage | CSV, SQLite (SQL schema) |
| Analysis | Matplotlib, Seaborn, Jupyter |
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

### 3. Clean the data

```bash
jupyter notebook notebooks/01_data_cleaning.ipynb
```

Output: `data/cleaned_jobs.csv`

### 4. Run analysis

```bash
jupyter notebook notebooks/02_analysis.ipynb
```

### 5. Launch dashboard

```bash
cd dashboard
streamlit run app.py
```

Open http://localhost:8501 in your browser.

## Project Structure

```
job-market-analysis/
├── crawler/
│   ├── parse_job.py            # Pure parsing functions
│   └── crawl_jobs.py           # Playwright crawler + CDN API
├── data/
│   ├── raw_jobs.csv            # Raw crawler output
│   ├── cleaned_jobs.csv        # Post-cleaning output
│   └── skills_dictionary.csv   # Skill normalization lookup
├── notebooks/
│   ├── 01_data_cleaning.ipynb  # Raw → Cleaned pipeline
│   └── 02_analysis.ipynb       # EDAA + visualizations
├── sql/
│   ├── schema.sql              # Table definitions
│   └── queries.sql             # Business analytics queries
├── dashboard/
│   └── app.py                  # Streamlit dashboard
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
