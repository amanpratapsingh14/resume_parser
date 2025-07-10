# Resume Parser Project

## Overview

This project is an end-to-end pipeline for parsing resumes (CVs) in PDF or DOCX format and extracting structured information using a combination of LLM (Ollama + Qwen3) and custom-trained spaCy NER. It provides both an API (FastAPI) and a Streamlit frontend for uploading resumes and viewing results.

**Key Features:**
- Accepts resumes in PDF or DOCX format.
- Extracts: Name, Contact Info, Summary, Skills, Work Experience, Education, Certifications, Languages, Projects, and more.
- Uses an LLM (Qwen3 via Ollama) for initial parsing and schema normalization.
- Trains a custom spaCy NER model on the extracted data for further automation.
- Provides both API and web UI for interaction.

---

## Installation

### System Requirements
- Python 3.10+
- GCC and build tools
- 4GB+ RAM (for LLM model)

### Multi-OS Installation

#### Ubuntu/Debian
```sh
sudo apt update
sudo apt install -y build-essential python3-pip python3-venv python3-dev
```

#### CentOS/RHEL/Fedora
```sh
# CentOS/RHEL
sudo yum groupinstall "Development Tools"
sudo yum install python3-pip python3-devel

# Fedora
sudo dnf groupinstall "Development Tools"
sudo dnf install python3-pip python3-devel
```

#### macOS
```sh
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python3 gcc
```

#### Windows
```sh
# Install Visual Studio Build Tools
# Download from: https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022

# Install Python from: https://www.python.org/downloads/
```

#### Arch Linux
```sh
sudo pacman -S base-devel python-pip python-setuptools python-wheel gcc
```

### Python Environment Setup
```sh
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install --upgrade pip setuptools wheel
```

### Install Python Packages
Install core dependencies first to avoid build issues:
```sh
pip install numpy cymem preshed murmurhash blis
```
Then install all project requirements:
```sh
pip install -r requirements.txt
```

### Ollama LLM Setup
Install Ollama:
```sh
# Linux/macOS
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# Download from: https://ollama.com/download
```

Start the Qwen3 model:
```sh
ollama run qwen3:0.6b
```

### spaCy Model Setup
Download the English model:
```sh
python -m spacy download en_core_web_sm
```

---

## Folder Structure

```
resume_parser/
│
├── app/                    # Backend logic and scripts
│   ├── main.py             # FastAPI backend (resume upload, parsing, NER update)
│   ├── generate_ner_training_data.py  # Script to generate NER training data from parsed resumes
│   ├── extract_raw_texts.py           # (Optional) Script to extract raw text from resumes
│   ├── ner_training_utils.py          # Helper functions for NER data formatting
│   ├── spacy_config.cfg    # spaCy training configuration
│
├── frontend/
│   └── streamlit_app.py    # Streamlit web UI for uploading resumes and viewing results
│
├── output_json/            # Output directory for parsed JSON and raw text files
│   ├── <resume>.json
│   └── <resume>_raw.txt
│
├── uploaded_resumes/       # Place to upload or drop new resumes (PDF/DOCX)
│
├── process_output/         # Logs and process outputs
│   └── process_log.txt
│
├── ner_model/              # Directory for trained spaCy NER model
│
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
└── ... (other files)
```

---

## Code Flow

1. **Resume Upload**
   - User uploads a resume via the API (`/upload_resume`) or the Streamlit UI.
   - The file is saved to `uploaded_resumes/`.

2. **Text Extraction & LLM Parsing**
   - The backend extracts raw text from the resume.
   - The extracted text is sent to the Qwen3 LLM (via Ollama) with a prompt to produce a normalized JSON structure.

3. **Output Storage**
   - The parsed JSON and raw text are saved in `output_json/`.

4. **NER Training Data Generation**
   - The script `app/generate_ner_training_data.py` reads all parsed JSONs and raw texts, and generates a spaCy-compatible NER training file (`ner_training_data.jsonl`).

5. **NER Model Training**
   - The spaCy config (`app/spacy_config.cfg`) is used to validate and train a custom NER model using the generated data.
   - The trained model is saved in `ner_model/`.

6. **API/Frontend Usage**
   - The API can be used to upload new resumes and trigger the pipeline.
   - The Streamlit frontend provides a user-friendly interface for uploads and viewing results.

---

## API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### POST /upload_resume
Upload a resume file (PDF or DOCX) for parsing.

**Request:**
- **Content-Type:** `multipart/form-data`
- **Body:** Form data with file field

**Parameters:**
- `file` (required): Resume file in PDF or DOCX format

**Response:**
- **Status:** 200 OK
- **Content-Type:** `application/json`
- **Body:** Parsed resume data in JSON format

**Example Request (cURL):**
```bash
curl -X POST "http://localhost:8000/upload_resume" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@/path/to/your/resume.pdf"
```

**Example Request (Python):**
```python
import requests

url = "http://localhost:8000/upload_resume"
files = {"file": open("resume.pdf", "rb")}

response = requests.post(url, files=files)
if response.status_code == 200:
    data = response.json()
    print("Parsed data:", data)
else:
    print("Error:", response.text)
```

**Example Response:**
```json
{
  "name": "John Doe",
  "email": "john.doe@email.com",
  "phone": "+1-555-123-4567",
  "linkedin": "linkedin.com/in/johndoe",
  "summary": "Experienced software developer with 5+ years in web development...",
  "skills": ["Python", "JavaScript", "React", "Node.js"],
  "work_experience": [
    {
      "company": "Tech Corp",
      "position": "Senior Developer",
      "duration": "2020-2023",
      "description": ["Led development of web applications", "Mentored junior developers"]
    }
  ],
  "education": [
    {
      "degree": "Bachelor of Science in Computer Science",
      "university": "University of Technology",
      "years": "2016-2020"
    }
  ],
  "projects": ["E-commerce platform", "Mobile app development"],
  "certifications": ["AWS Certified Developer"],
  "languages": ["English", "Spanish"],
  "achievements": ["Employee of the Year 2022"],
  "responsibilities": ["Code review", "Technical architecture"],
  "extra_curricular": ["Open source contributor"],
  "address": "123 Main St, City, State 12345",
  "urls": ["github.com/johndoe"]
}
```

**Error Responses:**
- `400 Bad Request`: Invalid file type or missing file
- `500 Internal Server Error`: Processing error

---

## Advanced Usage

### 1. Batch Processing
Process multiple resumes at once:

```python
import os
import requests
from pathlib import Path

def batch_process_resumes(directory):
    url = "http://localhost:8000/upload_resume"
    results = []
    
    for file_path in Path(directory).glob("*.pdf"):
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(url, files=files)
            if response.status_code == 200:
                results.append({
                    "file": file_path.name,
                    "data": response.json()
                })
            else:
                print(f"Error processing {file_path}: {response.text}")
    
    return results

# Usage
results = batch_process_resumes("./resumes/")
```

### 2. Custom NER Training
Train the model with your own data:

```python
# 1. Generate training data
import subprocess
subprocess.run(["python", "app/generate_ner_training_data.py"])

# 2. Validate data
subprocess.run(["python", "-m", "spacy", "debug", "data", "app/spacy_config.cfg"])

# 3. Train model
subprocess.run([
    "python", "-m", "spacy", "train", "app/spacy_config.cfg",
    "--output", "./ner_model"
])
```

### 3. Using the Trained NER Model
```python
import spacy

# Load the trained model
nlp = spacy.load("./ner_model")

# Process text
text = "John Doe is a Python developer at Tech Corp"
doc = nlp(text)

# Extract entities
for ent in doc.ents:
    print(f"{ent.text} - {ent.label_}")
```

### 4. Integration with External Systems
```python
import requests
import json

class ResumeParserAPI:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def parse_resume(self, file_path):
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(f"{self.base_url}/upload_resume", files=files)
            return response.json() if response.status_code == 200 else None
    
    def get_candidates_by_skill(self, skill, output_dir="output_json"):
        candidates = []
        for file_path in Path(output_dir).glob("*.json"):
            with open(file_path) as f:
                data = json.load(f)
                if skill.lower() in [s.lower() for s in data.get("skills", [])]:
                    candidates.append(data)
        return candidates

# Usage
parser = ResumeParserAPI()
resume_data = parser.parse_resume("candidate_resume.pdf")
python_devs = parser.get_candidates_by_skill("Python")
```

---

## Step-by-Step Usage

### 1. Data Preparation & NER Training

1. Generate NER training data from resume JSONs:
   ```sh
   python app/generate_ner_training_data.py
   ```
2. Validate your data:
   ```sh
   python -m spacy debug data app/spacy_config.cfg
   ```
3. Train the NER model:
   ```sh
   python -m spacy train app/spacy_config.cfg --output ./ner_model
   ```

### 2. Running the API

Start the FastAPI server:
```sh
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 3. Running the Streamlit Frontend

```sh
streamlit run frontend/streamlit_app.py
```

### 4. Using the Web Interface

1. Open your browser to `http://localhost:8501`
2. Upload a PDF or DOCX resume
3. Choose between JSON or tabular view
4. View the parsed results

---

## Configuration

### Environment Variables
```sh
export OLLAMA_HOST=http://localhost:11434
export SPACY_MODEL=en_core_web_sm
export UPLOAD_DIR=uploaded_resumes
export OUTPUT_DIR=output_json
```

### Customizing the LLM Prompt
Edit the `PROMPT_TEMPLATE` in `app/main.py` to modify how the LLM parses resumes.

### spaCy Configuration
Modify `app/spacy_config.cfg` to adjust training parameters, model architecture, or add new components.

---

## Notes

- Ensure `ollama run qwen3:0.6b` is running before uploading resumes.
- Place resumes in `uploaded_resumes/` or use the API/Streamlit UI to upload.
- Output JSON and raw text will be saved in `output_json/`.
- NER training data is generated from these outputs.
- The trained spaCy model will be saved in `ner_model/`.

---

## Troubleshooting

### Common Issues

**Build Errors:**
- Ensure all system dependencies are installed
- Use a compatible Python version (3.10+)
- Install core scientific packages first: `pip install numpy cymem preshed murmurhash blis`

**LLM Not Responding:**
- Make sure Ollama is running: `ollama serve`
- Check if the model is loaded: `ollama list`
- Verify the model name in `app/main.py` matches your installed model

**spaCy Training Issues:**
- Check that your NER training data contains valid entities
- Ensure the training data format is correct (JSONL)
- Validate the configuration: `python -m spacy debug data app/spacy_config.cfg`

**File Upload Errors:**
- Only PDF and DOCX files are supported
- Check file permissions and disk space
- Ensure the upload directory exists and is writable

### Performance Optimization

**For Large Scale Processing:**
- Use batch processing for multiple resumes
- Consider using a GPU for spaCy training
- Implement caching for repeated requests
- Use async processing for better throughput

**Memory Optimization:**
- Process resumes in smaller batches
- Clear memory after processing large files
- Use streaming for large file uploads

---

## License

MIT License (or your chosen license)