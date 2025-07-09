from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import os
import shutil
import docx2txt
from PyPDF2 import PdfReader
import re
import json
from ollama import chat

app = FastAPI()

UPLOAD_DIR = "uploaded_resumes"
OUTPUT_DIR = "output_json"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

MODEL_NAME = "qwen3:0.6b"
PROMPT_TEMPLATE = '''You are a resume parser. Parse the given resume string into JSON format with as much detail as possible. 

- Map any synonymous section headers to the following standard keys:
  - 'education' or 'academic' → 'education'
  - 'skills', 'technical skills', 'core competency', etc. → 'skills'
  - 'work experience', 'professional experience', etc. → 'work_experience'
  - 'projects', 'personal projects', etc. → 'projects'
  - 'certifications', 'licenses', etc. → 'certifications'
  - 'languages', 'spoken languages', etc. → 'languages'
  - 'achievements', 'awards', etc. → 'achievements'
  - 'responsibilities', 'key responsibilities', etc. → 'responsibilities'
  - 'extra curricular', 'extracurricular', etc. → 'extra_curricular'
- Always use the following JSON structure, even if the resume uses different section names:

{
  "name": "",
  "email": "",
  "phone": "",
  "linkedin": "",
  "summary": "",
  "skills": [""],
  "work_experience": [
    {
      "company": "",
      "position": "",
      "duration": "",
      "description": [""]
    }
  ],
  "education": [
    {
      "degree": "",
      "university": "",
      "years": ""
    }
  ],
  "projects": [],
  "certifications": [],
  "languages": [],
  "achievements": [],
  "responsibilities": [],
  "extra_curricular": [],
  "address": "",
  "urls": []
}

- For each section, extract as much detail as possible.
- For 'work_experience', ALWAYS extract ALL jobs, not just the most recent. Each job should include company, position, duration, and a list of bullet points in 'description'.
- Example:
"work_experience": [
  {
    "company": "ABC Corp",
    "position": "Backend Developer",
    "duration": "Jan 2019 – Present",
    "description": [
      "Built REST APIs handling 1M+ users.",
      "Led migration to microservices."
    ]
  },
  {
    "company": "XYZ Ltd",
    "position": "Software Engineer",
    "duration": "June 2016 – Dec 2018",
    "description": [
      "Designed database schema for enterprise applications..."
    ]
  }
]
- For 'education', include degree, university, and years.
- If a section is missing, leave it as an empty string or empty list as appropriate.
- Return only the JSON data, no extra text.

Parse the following resume:''' 

def extract_text_from_file(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".docx":
        return docx2txt.process(file_path)
    elif ext == ".pdf":
        with open(file_path, "rb") as f:
            reader = PdfReader(f)
            return "\n".join(page.extract_text() or "" for page in reader.pages)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

def parse_resume_with_llm(text: str) -> dict:
    prompt = PROMPT_TEMPLATE + text
    response = chat(model=MODEL_NAME, messages=[
        {'role': 'user', 'content': prompt},
    ], host="host.docker.internal")
    content = response['message']['content']
    match = re.search(r'\{.*\}', content, re.DOTALL)
    if match:
        json_str = match.group(0)
        try:
            data = json.loads(json_str)
            return data
        except Exception as e:
            raise ValueError(f'Error parsing JSON: {e}\nRaw response: {content}')
    else:
        raise ValueError('No JSON found in response.')

@app.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)):
    if not (file.filename.endswith('.pdf') or file.filename.endswith('.docx')):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported.")
    save_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    try:
        text = extract_text_from_file(save_path)
        data = parse_resume_with_llm(text)
        # Save to output_json folder
        base_name = os.path.splitext(os.path.basename(file.filename))[0]
        output_path = os.path.join(OUTPUT_DIR, f'{base_name}.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))