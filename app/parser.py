# Requires: pdfplumber, python-docx
import pdfplumber  # type: ignore
import docx  # type: ignore
from typing import Optional


def extract_text_from_pdf(file_path: str) -> str:
    """Extracts all text from a PDF file."""
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
            text += "\n"
    return text.strip()


def extract_text_from_docx(file_path: str) -> str:
    """Extracts all text from a DOCX file."""
    doc = docx.Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text.strip()


def extract_text(file_path: str) -> Optional[str]:
    """Dispatches to the correct extractor based on file extension."""
    if file_path.lower().endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.lower().endswith(".docx"):
        return extract_text_from_docx(file_path)
    else:
        raise ValueError("Unsupported file format. Only PDF and DOCX are supported.")
