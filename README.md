# Vietnam IT Job Market Analytics

A data pipeline and interactive dashboard for collecting, cleaning, analyzing, and visualizing IT job postings from [ybox.vn](https://ybox.vn/tuyen-dung).

## Demo

Live Streamlit dashboard:
https://job-analysis-ijgqnttkhnjngrqknvvbmp.streamlit.app/

## Overview

This project analyzes the Vietnam IT job market by crawling job postings, cleaning raw data, running SQL-based analytics, and visualizing insights through a Streamlit dashboard.

It answers questions such as:

* Which IT skills are most in demand?
* What are the salary ranges by role and experience level?
* How common are remote, hybrid, and onsite jobs?
* Which cities have the most IT job openings?
* Which roles are most common in the current hiring market?

## Motivation

For students and job seekers, understanding the job market helps with choosing the right skills, estimating salary expectations, and identifying suitable career paths.

For this project, the goal was to build a complete data pipeline that covers the full workflow:

```text
Crawling → Cleaning → Storage → SQL Analytics → Dashboard Visualization
```

The project demonstrates practical data engineering and analytics skills using real-world job posting data from the Vietnam IT hiring market.

## Data Pipeline

```text
Crawler → raw_jobs.csv → analysis.py → cleaned_jobs.csv + charts → Streamlit Dashboard
```

### 1. Crawler

The crawler is located in:

```text
crawler/crawl_jobs.py
```

It uses Playwright to collect IT job postings from the ybox.vn CDN API.

Features:

* Collects around 6,000 job postings
* Supports rate-limited crawling
* Supports checkpoint recovery
* Supports a `-page N` flag for faster development runs

Example:

```bash
python crawler/crawl_jobs.py -page 3
```

### 2. Data Cleaning and Analysis

The cleaning and analysis pipeline is located in:

```text
analysis.py
```

It handles:

* Location normalization
* Salary parsing
* Skill extraction
* Experience level parsing
* Work model classification
* Chart generation

Outputs:

```text
data/cleaned_jobs.csv
dashboard/screenshots/
```

### 3. SQL Analytics

The SQL files are stored in:

```text
sql/
```

They include:

* `schema.sql` — database table definitions
* `queries.sql` — business analytics queries

The SQL layer allows structured analysis of job trends, salary ranges, skills, locations, and experience levels.

### 4. Streamlit Dashboard

The dashboard is located in:

```text
dashboard/app.py
```

It provides an interactive interface with multiple pages for exploring:

* Market overview
* In-demand skills
* Salary insights
* Location distribution
* Work model distribution

The dashboard also checks whether the cleaned dataset exists. If the required data file is missing, it can automatically trigger the pipeline on first launch.

## Dataset

| Metric               | Value           |
| -------------------- | --------------- |
| Total jobs collected | ~6,000          |
| Fields collected     | 13              |
| Source               | ybox.vn CDN API |
| Date collected       | June 2026       |
| Format               | CSV             |

Example fields include:

* Job title
* Company
* Location
* Salary
* Skills
* Experience level
* Work model
* Job URL

## Key Features

* Playwright-based crawler using the ybox.vn CDN API
* Checkpoint recovery for safer crawling
* Pure-function parsing module for easier testing
* Skill normalization dictionary with 103 entries
* Salary parsing and normalization
* Experience level classification
* SQL schema and analytics queries
* Interactive Streamlit dashboard
* Single-script cleaning and analysis pipeline
* No Jupyter Notebook dependency

## Tech Stack

| Layer           | Tools                 |
| --------------- | --------------------- |
| Crawling        | Python, Playwright    |
| Data Processing | Pandas, NumPy         |
| Storage         | CSV, SQLite schema    |
| Analysis        | Matplotlib, Seaborn   |
| Dashboard       | Streamlit             |
| SQL Analytics   | SQLite-compatible SQL |

## Project Structure

```text
job-market-analysis/
├── analysis.py                   # Cleaning + analysis pipeline
├── crawler/
│   ├── __init__.py
│   ├── parse_job.py              # Pure parsing functions
│   └── crawl_jobs.py             # Playwright crawler + CDN API
├── data/
│   ├── raw_jobs.csv              # Raw crawler output, gitignored
│   ├── cleaned_jobs.csv          # Cleaned output, gitignored
│   └── skills_dictionary.csv     # Skill normalization lookup
├── sql/
│   ├── schema.sql                # Table definitions
│   └── queries.sql               # Business analytics queries
├── dashboard/
│   ├── app.py                    # Streamlit dashboard
│   └── screenshots/              # Generated chart images, gitignored
├── README.md
└── requirements.txt
```

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

Output:

```text
data/raw_jobs.csv
```

To limit pages during development:

```bash
python crawl_jobs.py -page 3
```

### 3. Clean data and generate charts

From the project root:

```bash
python analysis.py
```

Outputs:

```text
data/cleaned_jobs.csv
dashboard/screenshots/
```

### 4. Launch the dashboard

```bash
cd dashboard
streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

## Key Insights

From the sample analysis:

* Python, SQL, and JavaScript are among the most frequent skills.
* Ho Chi Minh City and Ha Noi dominate the IT job market.
* Most IT jobs are onsite.
* Remote and hybrid roles exist but are still a minority.
* Many intern and fresher roles do not disclose salary ranges.
* Salary visibility is inconsistent across job postings.

## Limitations

* The dataset is limited to ybox.vn, so it may not represent the entire Vietnam IT job market.
* Skill extraction currently relies on keyword matching, so some skills may be missed.
* Salary data is only available when publicly disclosed in job postings.
* The current dataset is based on a single crawl snapshot.
* The project does not yet track market changes over time.
* Experience level classification is currently rule-based and may misclassify ambiguous titles.

## Future Improvements

### Machine Learning Job Level Classification

The current system uses rule-based parsing to classify experience levels such as Intern, Fresher, Junior, Middle, and Senior.

A future improvement is to train a machine learning model to classify unknown or ambiguous job levels based on:

* Job title
* Job description
* Required skills
* Salary range
* Location
* Work model
* Company information

A baseline model could use TF-IDF with Logistic Regression or Random Forest. A stronger version could use sentence embeddings from the job title and description, then train a classifier such as XGBoost, LightGBM, or a neural model.

This would improve classification for vague job titles such as:

```text
Software Engineer
Backend Developer
AI Engineer
Data Analyst
```

### Salary Estimation for Missing Salary Data

Many job postings do not disclose salary. A future model could estimate salary ranges for jobs with missing salary information.

Instead of predicting only one value, the model could estimate:

* Minimum salary
* Maximum salary
* Median expected salary
* Confidence range

Possible input features:

* Experience level
* Skills
* Job title
* Job description
* City
* Work model
* Company
* Role category

This would make the dashboard more useful for students and job seekers because it could provide approximate salary expectations even when job postings hide salary information.

### Time-Series Crawling and Salary Forecasting

The current dataset is based on a single crawl snapshot. To support real forecasting, the crawler could be scheduled to run daily or weekly and store historical snapshots.

This would allow the project to analyze:

* Salary changes over time
* Skill demand trends
* Growth of AI, backend, frontend, and data roles
* Remote and hybrid job trends
* Hiring demand by city

Once enough historical data is collected, the project could use time-series forecasting to predict future salary trends and skill demand.

### Better Skill Extraction

The current skill extraction process relies on keyword matching. A future version could improve this by using NLP techniques such as:

* Named entity recognition
* Fuzzy matching
* Embedding-based similarity
* LLM-assisted skill extraction
* Expanded skill dictionaries

This would help detect variations such as:

```text
React
ReactJS
React.js
```

or:

```text
PostgreSQL
Postgres
```

### Multi-Source Data Collection

The project could be expanded to collect jobs from multiple platforms, such as:

* ITviec
* TopCV
* VietnamWorks
* LinkedIn
* Company career pages

This would reduce source bias and make the analysis more representative of the broader Vietnam IT market.

### Job Recommendation System

A future dashboard feature could allow users to input their current skills and target role, then receive job recommendations.

Example input:

```text
Python, SQL, FastAPI, Docker
Target level: Intern / Fresher
```

Possible output:

* Matching jobs
* Missing skills
* Estimated salary range
* Suggested skills to learn next

### Model Explainability

If machine learning models are added, the dashboard should explain why a prediction was made.

Example:

```text
Predicted level: Senior

Reason:
- Requires 5+ years of experience
- Mentions system design
- Requires mentoring responsibility
- Salary range is above market median
```

This would make the ML features more transparent and useful.

## Possible ML Extension

A future version of this project could extend the dashboard from descriptive analytics into predictive analytics.

The ML pipeline could include:

```text
Cleaned job data
→ Feature extraction
→ Text embeddings / TF-IDF
→ Job level classifier
→ Salary estimation model
→ Dashboard prediction layer
```

This would allow the dashboard to infer hidden information from job descriptions, required skills, locations, and work models.

## Conclusion

This project demonstrates a practical end-to-end data pipeline for analyzing the Vietnam IT job market.

It covers:

* Web crawling
* Data cleaning
* Feature extraction
* SQL analytics
* Dashboard visualization

Future improvements could turn it into a more advanced market intelligence tool with machine learning-based job level classification, salary estimation, trend forecasting, and personalized job recommendations.
