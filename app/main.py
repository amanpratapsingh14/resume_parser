from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import os
import shutil
import docx2txt
from PyPDF2 import PdfReader
import json
from ollama import chat
import subprocess

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
- For 'education', include degree, university, and years.
- If a section is missing, leave it as an empty string or empty list as appropriate.
- Return only the JSON data, no extra text.
- "name" should be the candidate's full name, not a company or organization. If multiple names are present, choose the one most likely to be the candidate (usually at the top of the resume). Do NOT use company names for the "name" field.

Parse the following resume:''' 

EXPECTED_SCHEMA = {
    "name": "",
    "email": "",
    "phone": "",
    "linkedin": "",
    "summary": "",
    "skills": [],
    "work_experience": [],
    "education": [],
    "projects": [],
    "certifications": [],
    "languages": [],
    "achievements": [],
    "responsibilities": [],
    "extra_curricular": [],
    "address": "",
    "urls": []
}

def normalize_json(data):
    # Fill in missing keys with default values
    for key, default in EXPECTED_SCHEMA.items():
        if key not in data:
            data[key] = default
    return data

# Post-processing to fix the name field if it matches a company

def fix_name_field(data, raw_text):
    companies = [exp.get("company", "") for exp in data.get("work_experience", [])]
    if data.get("name", "") in companies:
        # Try to extract the first non-empty line from the raw text that is not a company
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        for line in lines:
            if line not in companies and len(line.split()) >= 2 and not any(char.isdigit() for char in line):
                data["name"] = line
                break
    return data

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

def extract_first_json_object(text):
    stack = []
    start = None
    for i, c in enumerate(text):
        if c == '{':
            if not stack:
                start = i
            stack.append(c)
        elif c == '}':
            if stack:
                stack.pop()
                if not stack and start is not None:
                    try:
                        return json.loads(text[start:i+1])
                    except Exception:
                        continue
    raise ValueError("No valid JSON object found in response.")

@app.post("/upload_resume")
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename or not isinstance(file.filename, str):
        raise HTTPException(status_code=400, detail="Invalid file name.")
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in [".docx", ".pdf"]:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported.")
    safe_filename = os.path.basename(file.filename)
    save_path = os.path.join(UPLOAD_DIR, safe_filename)
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    try:
        # 1. Extract raw text
        if ext == ".docx":
            text = docx2txt.process(save_path)
        elif ext == ".pdf":
            with open(save_path, "rb") as f:
                reader = PdfReader(f)
                text = "\n".join(page.extract_text() or "" for page in reader.pages)
        # 2. Prepare prompt and call LLM
        prompt = PROMPT_TEMPLATE + text
        response = chat(model=MODEL_NAME, messages=[
            {'role': 'user', 'content': prompt},
        ])
        content = response['message']['content']
        # 3. Extract JSON from LLM response
        data = extract_first_json_object(content)
        data = normalize_json(data)
        data = fix_name_field(data, text)
        # 4. Save JSON to output_json/
        base_name = os.path.splitext(os.path.basename(file.filename))[0]
        output_json_path = os.path.join(OUTPUT_DIR, f'{base_name}.json')
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[INFO] Saved JSON to {output_json_path}")
        # 5. Save raw text for NER training
        raw_txt_path = os.path.join(OUTPUT_DIR, f'{base_name}_raw.txt')
        with open(raw_txt_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"[INFO] Saved raw text to {raw_txt_path}")
        # 6. Automatically update NER training data
        try:
            print(f"[INFO] Running NER training data generation...")
            subprocess.run([
                "python", "app/generate_ner_training_data.py"
            ], check=True)
            # 7. Convert JSONL to spaCy format
            subprocess.run([
                "python", "-m", "spacy", "convert", "ner_training_data.json", "./", "--lang", "en"
            ], check=True)
            # 8. Train spaCy NER model
            subprocess.run([
                "python", "-m", "spacy", "train", "app/spacy_config.cfg",
                "--output", "./ner_model",
                "--paths.train", "./ner_training_data.spacy",
                "--paths.dev", "./ner_training_data.spacy"
            ], check=True)
        except Exception as ner_exc:
            print(f"Warning: Failed to update NER training data or train spaCy model: {ner_exc}")
        # 9. Return the JSON response
        return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))