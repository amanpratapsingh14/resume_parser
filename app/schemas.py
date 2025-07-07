from pydantic import BaseModel
from typing import List, Optional

class WorkExperience(BaseModel):
    company: str
    position: str
    duration: str
    description: List[str]

class Education(BaseModel):
    degree: str
    university: str
    years: str

class Resume(BaseModel):
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    linkedin: Optional[str]
    summary: Optional[str]
    skills: Optional[List[str]]
    work_experience: Optional[List[WorkExperience]]
    education: Optional[List[Education]]
    certifications: Optional[List[str]] = None
    languages: Optional[List[str]] = None
    projects: Optional[List[str]] = None
    address: Optional[str] = None
    urls: Optional[List[str]] = None
