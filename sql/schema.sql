CREATE TABLE jobs (
    job_id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_title TEXT NOT NULL,
    company_name TEXT,
    city TEXT,
    district TEXT,
    salary_min REAL,
    salary_max REAL,
    salary_currency TEXT DEFAULT 'VND',
    is_salary_public BOOLEAN DEFAULT FALSE,
    experience_level TEXT,
    work_model TEXT,
    skill_count INTEGER DEFAULT 0,
    posted_date DATE,
    job_url TEXT UNIQUE
);

CREATE TABLE skills (
    skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_name TEXT UNIQUE NOT NULL,
    skill_category TEXT
);

CREATE TABLE job_skills (
    job_id INTEGER NOT NULL,
    skill_id INTEGER NOT NULL,
    PRIMARY KEY (job_id, skill_id),
    FOREIGN KEY (job_id) REFERENCES jobs(job_id),
    FOREIGN KEY (skill_id) REFERENCES skills(skill_id)
);
