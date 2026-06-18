"""
Pure parsing functions for ybox.vn job post data.
No I/O, no side effects — takes a post dict, returns a row dict.
"""

import re
import pandas as pd

SKILL_PATTERNS = [
    (r"\bpython\b", "Python"),
    (r"\bjava\b(?!\s*script)", "Java"),
    (r"\bjavascript\b|js\b", "JavaScript"),
    (r"\btypescript\b|ts\b", "TypeScript"),
    (r"\breact\b|reactjs", "React"),
    (r"\bnode\s*\.?\s*js|nodejs", "Node.js"),
    (r"\bangular\b", "Angular"),
    (r"\bvue\b|vuejs", "Vue.js"),
    (r"\bflutter\b", "Flutter"),
    (r"\breact\s*native\b", "React Native"),
    (r"\bphp\b", "PHP"),
    (r"\.net\b|c#|csharp", ".NET/C#"),
    (r"\bc\+\+\b", "C++"),
    (r"\bruby\b", "Ruby"),
    (r"\bgo(lang)?\b", "Go"),
    (r"\brust\b", "Rust"),
    (r"\bkotlin\b", "Kotlin"),
    (r"\bswift\b", "Swift"),
    (r"\bsql\b|mysql|postgresql|oracle\b", "SQL"),
    (r"\bmongodb\b|nosql", "MongoDB"),
    (r"\baws\b", "AWS"),
    (r"\bazure\b", "Azure"),
    (r"\bgcp\b|google\s*cloud", "GCP"),
    (r"\bdocker\b", "Docker"),
    (r"\bkubernetes\b|k8s", "Kubernetes"),
    (r"\bdevops\b", "DevOps"),
    (r"ci\s*/\s*cd|jenkins|gitlab", "CI/CD"),
    (r"\bmachine\s*learning\b|deep\s*learning\b|ml\b", "Machine Learning"),
    (r"\bai\b|artificial\s*intelligence", "AI"),
    (r"\bdata\s*engineer|data\s*analyst|data\s*scien", "Data Engineering"),
    (r"\bblockchain\b|solidity|web3", "Blockchain"),
    (r"\bcyber\s*security\b|bảo\s*mật", "Security"),
    (r"\bembedded\b|nhúng|iot|firmware", "Embedded/IoT"),
    (r"\bnetwork\b|mạng|cisco", "Networking"),
    (r"\btester\b|testing\b|kiểm\s*thử\b|qa\b", "Testing/QA"),
    (r"\blinux\b|unix", "Linux"),
    (r"\bgit\b", "Git"),
    (r"\bagile\b|scrum", "Agile/Scrum"),
    (r"\bsap\b", "SAP"),
    (r"\bsalesforce\b", "Salesforce"),
    (r"\bandroid\b", "Android"),
    (r"\bios\b", "iOS"),
    (r"\bhtml\b|css\b|html5|css3", "HTML/CSS"),
    (r"\brest\s*api\b|api\b", "REST API"),
    (r"\bgraphql\b", "GraphQL"),
    (r"\bexcel\b|power\s*bi\b|tableau\b|looker\b", "Analytics Tools"),
    (r"\blaravel\b", "Laravel"),
    (r"\bdjango\b", "Django"),
    (r"\bspring\b", "Spring"),
    (r"\btensorflow\b|pytorch\b", "ML Frameworks"),
    (r"\btiktok\b", "TikTok"),
]


def extract_skills(title: str) -> list:
    """Extract IT skills from a job title using keyword matching."""
    if not title:
        return []
    found = []
    title_lower = title.lower()
    for pattern, skill in SKILL_PATTERNS:
        if re.search(pattern, title_lower):
            found.append(skill)
    return found


def parse_location(title: str) -> str:
    """Extract location from [BRACKETS] in title."""
    if not title:
        return ""
    match = re.match(r"^\[([^\]]+)\]", title)
    if not match:
        return ""
    return match.group(1).strip()


def parse_work_model(title: str) -> str:
    """Detect Remote / Hybrid / Onsite from title keywords."""
    if not title:
        return "Unknown"
    t = title.lower()
    if re.search(r"remote|từ\s*xa|online\b|làm\s*việc\s*từ\s*xa|wfh", t):
        return "Remote"
    if re.search(r"hybrid|kết\s*hợp|linh\s*hoạt", t):
        return "Hybrid"
    if re.search(r"onsite|tại\s*văn\s*phòng|tại\s*chỗ|on\s*\.?\s*site", t):
        return "Onsite"
    return "Unknown"


def parse_experience_level(title: str) -> str:
    """Detect experience level from title keywords."""
    if not title:
        return "Unknown"
    t = title.lower()
    if re.search(r"thực\s*tập|internship|intern\b", t):
        return "Internship"
    if re.search(r"fresher|mới\s*tốt\s*nghiệp", t):
        return "Fresher"
    if re.search(r"nhân\s*viên|junior\b|jr\b", t):
        return "Junior"
    if re.search(r"chuyên\s*viên|mid.?level\b|middle\b", t):
        return "Mid-level"
    if re.search(r"trưởng\b|quản\s*lý|manager|lead\b|giám\s*đốc|senior\b|sr\b|head\b", t):
        return "Senior"
    # Broad fallback: if title mentions developer/engineer but no level, default to Junior
    if re.search(r"developer|engineer|programmer|tester|analyst|designer|lập\s*trình|kỹ\s*sư|kiểm\s*thử", t):
        return "Junior"
    return "Unknown"


def parse_salary(title: str) -> tuple:
    """Extract salary_min, salary_max from title.

    Patterns:
      - "Lương 8-15 Triệu", "Thu Nhập Upto 20 Triệu/Tháng"
      - "Mức Lương 8-15 Triệu/Tháng"
    """
    if not title:
        return None, None
    patterns = [
        r"(?:lương|thu\s*nhập|mức\s*lương)\s*(?:upto|up\s*to|lên\s*đến|từ)?\s*(\d{1,3}(?:[.,]\d)?)\s*(?:[-–đến]+\s*(\d{1,3}(?:[.,]\d)?))?\s*(?:triệu|tr|m|million)",
        r"(\d{1,3}(?:[.,]\d)?)\s*[-–]\s*(\d{1,3}(?:[.,]\d)?)\s*(?:triệu|tr|m|million)",
    ]
    for pat in patterns:
        m = re.search(pat, title, re.IGNORECASE)
        if m:
            lo = float(m.group(1).replace(",", ""))
            hi = float(m.group(2).replace(",", "")) if m.group(2) else None
            return lo, hi
    return None, None


def parse_company(title: str) -> str:
    """Extract company name between [LOCATION] and 'tuyển dụng'."""
    if not title:
        return ""
    m = re.search(r"\]\s*(.+?)\s*tuyển\s*dụng", title, re.IGNORECASE)
    if not m:
        return ""
    raw = m.group(1).strip()
    raw = re.sub(r"\s{2,}", " ", raw)
    raw = re.sub(r"\s+\d{4}$", "", raw)
    return raw


def build_job_url(slug: str, post_id: str) -> str:
    """Build the job detail URL from slug and ID."""
    return f"https://ybox.vn/tuyen-dung/{slug}-{post_id}"


def parse_post(post: dict) -> dict:
    """Convert a raw ybox.vn CDN API post JSON into a structured row.

    Args:
        post: A post dict from the CDN API (has _id, title, slug, etc.)

    Returns:
        A flat dict with standardised fields.
    """
    title = (post.get("title") or "").strip()

    skills = extract_skills(title)
    salary_min, salary_max = parse_salary(title)

    return {
        "job_title": title,
        "company_name": parse_company(title) or post.get("publisher", {}).get("fullName", ""),
        "location": parse_location(title),
        "salary_min": salary_min,
        "salary_max": salary_max,
        "skills": "; ".join(skills),
        "experience_level": parse_experience_level(title),
        "work_model": parse_work_model(title),
        "posted_date": post.get("publishedAt", ""),
        "job_url": build_job_url(post.get("slug", ""), post.get("_id", "")),
        "description": (post.get("summary") or "")[:500],
        "company_logo": post.get("publisher", {}).get("avatar", ""),
        "views": post.get("statistics", {}).get("totalViews", 0),
    }


def extract_edges_from_json(data: dict) -> list:
    """Unpack all job edges from a CDN API response.

    Returns a combined list of post dicts from NewestPosts,
    HighlightPosts, and SelectivePosts.
    """
    all_edges = []
    for key in ("NewestPosts", "HighlightPosts", "SelectivePosts"):
        block = data.get(key)
        if block and "edges" in block:
            all_edges.extend(block["edges"])
    return all_edges


def posts_to_dataframe(posts: list) -> pd.DataFrame:
    """Parse a list of raw post dicts into a clean DataFrame."""
    rows = [parse_post(p) for p in posts if p.get("title")]
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.drop_duplicates(subset=["job_url"])
    return df
