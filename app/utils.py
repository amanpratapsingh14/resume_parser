import re
from typing import Optional, List

def extract_email(text: str) -> Optional[str]:
    match = re.search(r"[\w\.-]+@[\w\.-]+", text)
    return match.group(0) if match else None

def extract_phone(text: str) -> Optional[str]:
    match = re.search(r"(\+?\d[\d\s\-]{7,}\d)", text)
    return match.group(0) if match else None

def extract_linkedin(text: str) -> Optional[str]:
    # Match both full and partial LinkedIn URLs
    match = re.search(r"(https?://)?(www\.)?linkedin\.com/in/[\w\d\-]+|linkedin\.com/in/[\w\d\-]+|in/[\w\d\-]+", text)
    if match:
        url = match.group(0)
        if not url.startswith("http"):
            url = "https://www.linkedin.com/" + url.lstrip("/")
        return url
    return None

def extract_urls(text: str) -> List[str]:
    # Extract all URLs (http(s), www, and common dev URLs)
    url_pattern = r"(https?://[\w\.-/\d%#?=&]+|www\.[\w\.-/\d%#?=&]+|github\.com/[\w\d\-]+|leetcode\.com/[\w\d\-]+|hackerrank\.com/[\w\d\-]+)"
    urls = re.findall(url_pattern, text)
    # Normalize partial URLs
    normalized = []
    for url in urls:
        if url.startswith("www."):
            url = "https://" + url
        elif url.startswith("github.com"):
            url = "https://" + url
        elif url.startswith("leetcode.com"):
            url = "https://" + url
        elif url.startswith("hackerrank.com"):
            url = "https://" + url
        normalized.append(url)
    return list(set(normalized))
