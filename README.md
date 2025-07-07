# Intelligent Resume Parser

## Overview
A modular, ML/NLP-powered resume parser that extracts structured information from PDF and DOCX resumes and outputs JSON/tabular summaries. Designed for easy integration and extensibility.

---

## Features
- Accepts PDF and DOCX resumes
- Extracts: Name, Contact Info, Summary, Skills, Work Experience, Education, Certifications, Languages, Projects, and more
- Handles various resume formats and noise
- Outputs structured JSON in a hierarchical format
- Modular, testable, and ready for integration

---

## Project Structure
```
resume_parser/
  app/
    __init__.py
    extractor.py      # Extraction logic for all fields
    parser.py         # File reading and text extraction (PDF/DOCX)
    schemas.py        # Pydantic models for structured data
    utils.py          # Utility functions (regex for email, phone, URLs, etc.)
  frontend/           # (Optional) Web UI
  main.py             # CLI entry point
  models/             # ML/NLP models (if any)
  tests/              # Unit tests
  requirements.txt    # Python dependencies
  README.md           # This file
```

---

## Code Flow & How It Works

### 1. **Entry Point: `main.py`**
- Parses command-line arguments (`--file path/to/resume.pdf`)
- Calls `extract_text()` to extract raw text from the PDF or DOCX
- Passes the text to `extract_resume()` to parse structured data
- Saves the output as a `.json` file with the same base name as the input

**Pseudocode:**
```python
text = extract_text(resume_file)
resume = extract_resume(text)
with open(output_file, 'w') as f:
    json.dump(resume, f)
```

### 2. **Text Extraction: `app/parser.py`**
- Uses `pdfplumber` for PDFs and `python-docx` for DOCX files
- Returns the full text content for further processing

### 3. **Field Extraction: `app/extractor.py`**
- Contains functions to extract each field (name, email, phone, skills, etc.)
- Uses regular expressions and section header detection to find relevant info
- Handles multi-line and category-based skills, multi-line education, and robust work experience parsing
- Returns a `Resume` Pydantic model

**Example: Skills Extraction**
```python
def extract_skills(text):
    # Find KEY COMPETENCIES / TECHNICAL SKILLS section
    # Extract all category lines (Languages, Databases, DevOps, etc.)
    # Split and flatten all skills into a list
```

### 4. **Schemas: `app/schemas.py`**
- Defines the data structure for Resume, WorkExperience, Education, etc. using Pydantic
- Ensures output is always valid JSON and easy to extend

### 5. **Utilities: `app/utils.py`**
- Contains regex-based helpers for extracting emails, phone numbers, LinkedIn, and all URLs

---

## How Extraction Works (Step-by-Step)

1. **File Input**: User provides a PDF or DOCX resume file.
2. **Text Extraction**: The file is read and all text is extracted.
3. **Section Detection**: The parser looks for key section headers (e.g., "KEY COMPETENCIES / TECHNICAL SKILLS", "PROFESSIONAL EXPERIENCE", "EDUCATION").
4. **Field Extraction**:
    - **Contact Info**: Regex for email, phone, LinkedIn, and all URLs.
    - **Skills**: All lines under the skills section are split and flattened into a list.
    - **Work Experience**: Each job is detected by company/date patterns, with position and description extracted.
    - **Education**: Degree and university/year are matched, even if on separate lines.
    - **Other Fields**: (Certifications, languages, projects) can be added similarly.
5. **Output**: All extracted data is saved as a hierarchical JSON file.

---

## Example Output
```json
{
  "name": "Aman Pratap Singh",
  "email": "amanpratapsingh1440@gmail.com",
  "phone": "+91-8920560095",
  "linkedin": "https://www.linkedin.com/in/amanpratapsingh1440",
  "urls": [
    "https://github.com/amanpratapsingh14"
  ],
  "summary": "Full Stack Developer with ...",
  "skills": [
    "C++", "Python", "Django", "FastAPI", "JavaScript", "Node.js", "Express.js", "React.js", "Next.js", "PostgreSQL", "MSSQL", "MongoDB", "Redis", "Docker", "GitHub Actions", "CI/CD", "GCP", "AWS", "Shell Scripting", "Postman", "REST API Design", "Numpy", "Pandas", "DSA"
  ],
  "work_experience": [
    {
      "company": "Kitaabh Technologies Private Limited",
      "position": "Software Development Engineer I",
      "duration": "2024 - Present",
      "description": [
        "Developed and scaled 80+ RESTful APIs ...",
        "Automated CI/CD pipelines ..."
      ]
    },
    ...
  ],
  "education": [
    {
      "degree": "Bachelor of Technology – Computer Science & Engineering",
      "university": "Dr. A.P.J. Abdul Kalam Technical University (AKTU)",
      "years": "June 2019 - April 2023"
    }
  ],
  "certifications": null,
  "languages": null,
  "projects": null,
  "address": null
}
```

---

## Extending the Parser
- To add new fields (e.g., certifications, languages), add extraction logic in `extractor.py` and update the `Resume` schema in `schemas.py`.
- To support new file types, add extraction logic in `parser.py`.
- For advanced NLP, you can integrate spaCy or other ML models in the `models/` directory.

---

## Testing
- Unit tests are in the `tests/` directory.
- Run tests with:
```bash
pytest
```

---

## Contributing
Pull requests are welcome! Please open an issue or discussion for major changes.

---

## License
MIT License
