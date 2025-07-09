import os
import docx2txt
from PyPDF2 import PdfReader

resume_dir = "resume_folder"
output_dir = "output_json"
os.makedirs(output_dir, exist_ok=True)

for filename in os.listdir(resume_dir):
    file_path = os.path.join(resume_dir, filename)
    base, ext = os.path.splitext(filename)
    ext = ext.lower()
    if ext not in [".pdf", ".docx"]:
        continue
    text = ""
    if ext == ".docx":
        text = docx2txt.process(file_path)
    elif ext == ".pdf":
        with open(file_path, "rb") as f:
            reader = PdfReader(f)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
    raw_txt_path = os.path.join(output_dir, f"{base}_raw.txt")
    with open(raw_txt_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Extracted raw text for {filename} -> {raw_txt_path}") 