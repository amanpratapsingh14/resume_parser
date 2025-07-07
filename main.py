import argparse
import json
import os
from app.parser import extract_text
from app.extractor import extract_resume
from pydantic.json import pydantic_encoder

def main():
    parser = argparse.ArgumentParser(description="Intelligent Resume Parser")
    parser.add_argument('--file', type=str, required=True, help='Path to resume file (PDF or DOCX)')
    args = parser.parse_args()

    text = extract_text(args.file)
    resume = extract_resume(text)

    # Hierarchical order for JSON output
    resume_dict = resume.model_dump()
    ordered = {
        "name": resume_dict.get("name"),
        "email": resume_dict.get("email"),
        "phone": resume_dict.get("phone"),
        "linkedin": resume_dict.get("linkedin"),
        "urls": resume_dict.get("urls"),
        "summary": resume_dict.get("summary"),
        "skills": resume_dict.get("skills"),
        "work_experience": resume_dict.get("work_experience"),
        "education": resume_dict.get("education"),
        "certifications": resume_dict.get("certifications"),
        "languages": resume_dict.get("languages"),
        "projects": resume_dict.get("projects"),
        "address": resume_dict.get("address"),
    }

    # Output file name
    base, _ = os.path.splitext(args.file)
    output_file = base + ".json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(ordered, f, default=pydantic_encoder, indent=2, ensure_ascii=False)
    print(f"Extracted data saved to {output_file}")

if __name__ == "__main__":
    main()
