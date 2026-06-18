-- ============================================================
-- Vietnam IT Job Market Analytics — Business Queries
-- ============================================================

-- 1. Top 15 most demanded skills
SELECT
    s.skill_name,
    COUNT(*) AS job_count
FROM job_skills js
JOIN skills s ON js.skill_id = s.skill_id
GROUP BY s.skill_name
ORDER BY job_count DESC
LIMIT 15;

-- 2. Top cities by job count
SELECT
    city,
    COUNT(*) AS job_count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM jobs WHERE city != ''), 1) AS pct
FROM jobs
WHERE city != ''
GROUP BY city
ORDER BY job_count DESC;

-- 3. Jobs by work model distribution
SELECT
    work_model,
    COUNT(*) AS job_count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM jobs), 1) AS pct
FROM jobs
GROUP BY work_model
ORDER BY job_count DESC;

-- 4. Jobs by experience level
SELECT
    experience_level,
    COUNT(*) AS job_count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM jobs WHERE experience_level != 'Unknown'), 1) AS pct
FROM jobs
WHERE experience_level != 'Unknown'
GROUP BY experience_level
ORDER BY
    CASE experience_level
        WHEN 'Internship' THEN 1
        WHEN 'Fresher' THEN 2
        WHEN 'Junior' THEN 3
        WHEN 'Mid-level' THEN 4
        WHEN 'Senior' THEN 5
        ELSE 6
    END;

-- 5. Average salary by experience level
SELECT
    experience_level,
    COUNT(*) AS jobs_with_salary,
    ROUND(AVG((salary_min + salary_max) / 2), 2) AS avg_salary_mil,
    ROUND(AVG(salary_min), 2) AS avg_salary_min,
    ROUND(AVG(salary_max), 2) AS avg_salary_max
FROM jobs
WHERE is_salary_public = TRUE
  AND salary_min IS NOT NULL
  AND experience_level != 'Unknown'
GROUP BY experience_level
ORDER BY avg_salary_mil DESC;

-- 6. Salary disclosure rate
SELECT
    CASE WHEN is_salary_public THEN 'Disclosed' ELSE 'Not Disclosed' END AS status,
    COUNT(*) AS count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM jobs), 1) AS pct
FROM jobs
GROUP BY is_salary_public;

-- 7. Top skills for Internship & Fresher roles
SELECT
    s.skill_name,
    COUNT(*) AS job_count
FROM job_skills js
JOIN skills s ON js.skill_id = s.skill_id
JOIN jobs j ON js.job_id = j.job_id
WHERE j.experience_level IN ('Internship', 'Fresher')
GROUP BY s.skill_name
ORDER BY job_count DESC
LIMIT 10;

-- 8. Skills most commonly paired together (co-occurrence)
SELECT
    s1.skill_name AS skill_a,
    s2.skill_name AS skill_b,
    COUNT(*) AS pair_count
FROM job_skills js1
JOIN job_skills js2 ON js1.job_id = js2.job_id AND js1.skill_id < js2.skill_id
JOIN skills s1 ON js1.skill_id = s1.skill_id
JOIN skills s2 ON js2.skill_id = s2.skill_id
GROUP BY s1.skill_name, s2.skill_name
ORDER BY pair_count DESC
LIMIT 15;

-- 9. Companies posting the most IT jobs
SELECT
    company_name,
    COUNT(*) AS job_count
FROM jobs
WHERE company_name != ''
GROUP BY company_name
ORDER BY job_count DESC
LIMIT 10;

-- 10. Monthly posting trend
SELECT
    strftime('%Y-%m', posted_date) AS month,
    COUNT(*) AS job_count
FROM jobs
WHERE posted_date IS NOT NULL AND posted_date != ''
GROUP BY month
ORDER BY month DESC
LIMIT 12;
