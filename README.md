# Intelligent Resume Parser

---

## How to Run (Quick Start)

### 1. **Build the Docker Image**
```bash
sudo docker build -t resume-pipeline .
```

### 2. **Run the Docker Container**
```bash
sudo docker run -p 8080:8080 \
  -v $(pwd)/resume_folder:/app/resume_folder \
  -v $(pwd)/output_json:/app/output_json \
  -v $(pwd)/process_output:/app/process_output \
  resume-pipeline
```

- The **FastAPI backend** will be available at: [http://localhost:8080/docs](http://localhost:8080/docs)
- (If you want to run the Streamlit frontend, see below for multi-service setup.)

---

## Ollama Installation (Required for LLM Parsing)

Ollama must be installed and running on your host machine before starting the backend.

### Quick Setup (Recommended)
```bash
bash setup_ollama.sh
```

### Manual Steps
1. **Install Ollama (Linux/macOS):**
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```
2. **Start Ollama Service:**
   ```bash
   ollama serve &
   ```
3. **Download the Required Model:**
   ```bash
   ollama run qwen3:0.6b
   ```

---

## How to Run Both Backend and Frontend (Docker Compose)

You can run both the FastAPI backend (on port 8080) and the Streamlit frontend (on port 3000) together using Docker Compose:

### 1. **Start Both Services**
```bash
sudo docker compose up --build
```

- **Backend (FastAPI):** [http://localhost:8080/docs](http://localhost:8080/docs)
- **Frontend (Streamlit):** [http://localhost:3000](http://localhost:3000)

Both services share the same folders for resumes, outputs, and logs via Docker volumes.

To stop the services, press `Ctrl+C` in the terminal, then run:
```bash
sudo docker compose down
```

---

## Project Flow
1. **Upload Resume:**
   - Use the API at `/upload_resume` (see FastAPI docs) or the Streamlit frontend (if running) to upload a PDF or DOCX resume.
2. **Processing:**
   - The backend extracts text, parses the resume using an LLM, and outputs structured JSON.
3. **Output:**
   - Results are saved in the `output_json/` directory on your host machine.
4. **Logs:**
   - Processing logs are saved in `process_output/`.

---

## Features
- Accepts PDF and DOCX resumes
- Extracts: Name, Contact Info, Summary, Skills, Work Experience, Education, Certifications, Languages, Projects, and more
- Handles various resume formats and noise
- Outputs structured JSON in a hierarchical format
- Modular, testable, and ready for integration

---

## Project Structure
```text
resume_parser/
  app/                  # Backend logic (FastAPI, extraction, NER, utils)
  frontend/             # Streamlit web UI
  output_json/          # Output JSONs and raw text
  uploaded_resumes/     # Uploaded files
  requirements.txt      # Python dependencies
  dockerfile            # Docker setup
  orchestrator.py       # Orchestrates backend/frontend
  README.md             # This file
```

---

## Quickstart Workflow

### 1. **Clone the Repository**
```bash
git clone <repo-url>
cd resume_parser
```

### 2. **Install Python Dependencies**
It is recommended to use a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. **Install spaCy Model**
```bash
python -m spacy download en_core_web_sm
```
Or, as in requirements.txt:
```bash
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl
```

### 4. **Install Ollama and Download LLM Model**
Ollama is required for LLM-based parsing. Install and run the model:
```bash
# Install Ollama (Linux/macOS)
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service (if not already running)
ollama serve &

# Download the required model (qwen3:0.6b)
ollama run qwen3:0.6b
```

### 5. **Run the Backend (FastAPI) and Frontend (Streamlit)**
You can run both using the orchestrator script:
```bash
python orchestrator.py
```
- FastAPI backend: [http://localhost:8080/docs](http://localhost:8080/docs)
- Streamlit UI: [http://localhost:8501](http://localhost:8501)

Alternatively, run them separately:
```bash
# Backend
uvicorn app.main:app --reload --port 8080
# Frontend
streamlit run frontend/streamlit_app.py
```

---

## Usage
- **Web UI:** Open [http://localhost:8501](http://localhost:8501) and upload a PDF or DOCX resume. View output as JSON or in a table.
- **API:** Use `/upload_resume` endpoint (see FastAPI docs at [http://localhost:8080/docs](http://localhost:8080/docs)).
- **Outputs:** Parsed results are saved in `output_json/` as JSON files.

---

## Model Details
- **LLM Model:** Uses [qwen3:0.6b](https://ollama.com/library/qwen3) via Ollama for parsing resumes into structured JSON.
- **spaCy NER:** For custom NER training, see scripts in `app/` and use `ner_training_data.json`.

---

## Training Custom NER (Optional)
1. Place resumes in `resume_folder/`.
2. Run extraction and NER data generation:
   ```bash
   python app/extract_raw_texts.py
   python app/generate_ner_training_data.py
   # Convert and train with spaCy as needed
   ```
3. See `app/spacy_config.cfg` for training config.

---

## Docker (Optional)
Build and run everything in a container:
```bash
docker build -t resume-parser .
docker run -p 8080:8080 -p 8501:8501 resume-parser
```

---

## Troubleshooting
- **Ollama not found:** Ensure `ollama`