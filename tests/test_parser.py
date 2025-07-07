from app.extractor import extract_resume
from app.schemas import Resume

def test_extract_resume():
    sample = '''John Doe\nSenior Software Engineer\nEmail: john.doe@example.com\nPhone: +1 234 567 8900\nLinkedIn: linkedin.com/in/johndoe\n\nSummary:\nExperienced software engineer with 7+ years in backend systems and distributed applications...\n\nSkills: Java, Spring Boot, Microservices, Docker, Kubernetes, MongoDB\n\nWork Experience:\nCompany: ABC Corp\nPosition: Backend Developer\nDuration: Jan 2019 – Present\n- Built REST APIs handling 1M+ users.\n- Led migration to microservices.\n\nCompany: XYZ Ltd\nPosition: Software Engineer\nDuration: June 2016 – Dec 2018\n- Designed database schema for enterprise applications...\n\nEducation:\nB.Tech in Computer Science, XYZ University, 2012–2016\n'''
    resume = extract_resume(sample)
    assert resume.name == "John Doe"
    assert resume.email == "john.doe@example.com"
    assert resume.phone == "+1 234 567 8900"
    assert resume.linkedin == "linkedin.com/in/johndoe"
    assert resume.summary.startswith("Experienced software engineer")
    assert "Java" in resume.skills
    assert resume.work_experience[0].company == "ABC Corp"
    assert resume.education[0].degree.startswith("B.Tech")
