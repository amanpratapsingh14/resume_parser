import os
import time
import subprocess
from datetime import datetime

RESUME_DIR = "resume_folder"
OUTPUT_DIR = "output_json"
PROCESS_OUTPUT_DIR = "process_output"
os.makedirs(PROCESS_OUTPUT_DIR, exist_ok=True)

def start_servers():
    uvicorn_cmd = ["uvicorn", "app.api:app", "--reload", "--port", "8080"]
    streamlit_cmd = ["streamlit", "run", "frontend/streamlit_app.py"]
    uvicorn_proc = subprocess.Popen(uvicorn_cmd)
    streamlit_proc = subprocess.Popen(streamlit_cmd)
    return uvicorn_proc, streamlit_proc

def get_resume_files():
    return set(f for f in os.listdir(RESUME_DIR) if f.endswith(('.pdf', '.docx')))

def log_process(message):
    with open(os.path.join(PROCESS_OUTPUT_DIR, "process_log.txt"), "a") as f:
        f.write(f"{datetime.now()}: {message}\n")

def main_loop():
    seen_files = get_resume_files()
    log_process("Orchestrator started.")
    while True:
        time.sleep(120)  # 2 minutes
        current_files = get_resume_files()
        new_files = current_files - seen_files
        if new_files:
            log_process(f"New files detected: {new_files}")
            subprocess.run(["python", "app/extract_raw_texts.py"])
            subprocess.run(["python", "app/generate_ner_data.py"])
            subprocess.run(["python", "-m", "spacy", "convert", "ner_training_data.json", "./", "--lang", "en"])
            subprocess.run([
                "python", "-m", "spacy", "train", "app/spacy_config.cfg",
                "--output", "./ner_model",
                "--paths.train", "./ner_training_data.spacy",
                "--paths.dev", "./ner_training_data.spacy"
            ])
            log_process(f"Model trained with files: {new_files}")
        seen_files = current_files

if __name__ == "__main__":
    uvicorn_proc, streamlit_proc = start_servers()
    try:
        main_loop()
    except KeyboardInterrupt:
        log_process("Orchestrator stopped by user.")
        uvicorn_proc.terminate()
        streamlit_proc.terminate()