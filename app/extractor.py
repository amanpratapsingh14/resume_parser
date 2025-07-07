from app.schemas import Resume, WorkExperience, Education
from app.utils import extract_email, extract_phone, extract_linkedin, extract_urls
import re
from typing import Optional, List

def extract_name(text: str) -> Optional[str]:
    for line in text.splitlines():
        if line.strip():
            return line.strip()
    return None

def extract_summary(text: str) -> Optional[str]:
    match = re.search(r"Summary:?\n(.+?)(\n\w+:|$)", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None

def extract_skills(text: str) -> Optional[List[str]]:
    # Find the KEY COMPETENCIES / TECHNICAL SKILLS section
    match = re.search(r"KEY COMPETENCIES ?/ ?TECHNICAL SKILLS\n(.+?)(\n[A-Z][A-Z ]{3,}:|\n[A-Z][A-Z ]{3,}\n|\nPROFESSIONAL EXPERIENCE|\nWORK EXPERIENCE|\nEDUCATION|$)", text, re.DOTALL | re.IGNORECASE)
    if not match:
        return None
    section = match.group(1)
    skills = []
    for line in section.splitlines():
        line = line.strip()
        if not line or ":" not in line:
            continue
        # Remove category prefix and split
        parts = line.split(":", 1)
        skill_items = re.split(r",|;|\n", parts[1])
        for s in skill_items:
            skill = s.strip().rstrip(".")
            if skill:
                skills.append(skill)
    # Deduplicate and return
    return list(dict.fromkeys(skills)) if skills else None

def extract_work_experience(text: str) -> Optional[List[WorkExperience]]:
    # Find the Professional/Work Experience section
    match = re.search(r"(PROFESSIONAL|WORK) EXPERIENCE:?\n(.+?)(\n[A-Z][A-Z ]+:|\nEDUCATION|$)", text, re.DOTALL | re.IGNORECASE)
    if not match:
        return None
    section = match.group(2)
    lines = [l for l in section.splitlines() if l.strip()]
    experiences = []
    i = 0
    while i < len(lines):
        # Company + date pattern
        m = re.match(r"([A-Z][A-Za-z0-9&.,'() /]+) (May|June|July|August|September|October|November|December|January|February|March|April)? ?\d{4} ?(to|-|–) ?(Present|[A-Z][a-z]+ \d{4}|\d{4})", lines[i])
        if m:
            company = m.group(1).strip()
            duration = lines[i][len(company):].strip()
            # Next line: position (if not another company)
            position = ""
            description = []
            if i+1 < len(lines):
                next_line = lines[i+1].strip()
                m2 = re.match(r"([A-Z][A-Za-z0-9&.,'() /]+) (May|June|July|August|September|October|November|December|January|February|March|April)? ?\d{4} ?(to|-|–) ?(Present|[A-Z][a-z]+ \d{4}|\d{4})", next_line)
                if not m2:
                    position = next_line
                    i += 1
            # Collect description until next company/date or end
            i += 1
            while i+1 < len(lines):
                lookahead = lines[i+1].strip()
                m3 = re.match(r"([A-Z][A-Za-z0-9&.,'() /]+) (May|June|July|August|September|October|November|December|January|February|March|April)? ?\d{4} ?(to|-|–) ?(Present|[A-Z][a-z]+ \d{4}|\d{4})", lookahead)
                if m3:
                    break
                if lookahead.startswith("Key Responsibility"):
                    i += 1
                    continue
                if lookahead.startswith("-") or lookahead.startswith("•"):
                    description.append(lookahead.lstrip("-• ").strip())
                else:
                    description.append(lookahead)
                i += 1
            experiences.append(WorkExperience(company=company, position=position, duration=duration, description=description))
        i += 1
    return experiences if experiences else None

def extract_education(text: str) -> Optional[List[Education]]:
    match = re.search(r"EDUCATION:?\n(.+?)(\n[A-Z][A-Z ]+:|$)", text, re.DOTALL | re.IGNORECASE)
    if not match:
        return None
    section = match.group(1)
    lines = [l for l in section.splitlines() if l.strip()]
    degrees = []
    i = 0
    while i < len(lines):
        degree = university = years = None
        # If this line looks like a degree
        if re.search(r"Bachelor|Master|B\.|M\.|PhD|Doctor", lines[i], re.IGNORECASE):
            degree = lines[i].strip()
            # Next line: university and years
            if i+1 < len(lines):
                uni_line = lines[i+1].strip()
                # Try to extract university and years
                m = re.match(r"(.+), (.+ \d{4} ?- ?[A-Za-z]+ \d{4})", uni_line)
                if m:
                    university, years = m.groups()
                else:
                    # Try: university (years)
                    m = re.match(r"(.+)\((.+)\)", uni_line)
                    if m:
                        university, years = m.groups()
                    else:
                        university = uni_line
                        years = ""
                degrees.append(Education(degree=degree, university=university, years=years))
                i += 2
                continue
        i += 1
    return degrees if degrees else None

def extract_resume(text: str) -> Resume:
    return Resume(
        name=extract_name(text),
        email=extract_email(text),
        phone=extract_phone(text),
        linkedin=extract_linkedin(text),
        summary=extract_summary(text),
        skills=extract_skills(text),
        work_experience=extract_work_experience(text),
        education=extract_education(text),
        urls=extract_urls(text),
    )
