import os
from typing import List

from pypdf import PdfReader
from docx import Document

from config import CHUNK_SIZE, CHUNK_OVERLAP


def load_txt(file_path: str) -> str:
    """
    Reads text from .txt file.
    """
    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
        return file.read()


def load_pdf(file_path: str) -> str:
    """
    Reads text from text-based PDF file.
    Note: Scanned image PDFs need OCR, which is not added in this beginner version.
    """
    text = ""

    reader = PdfReader(file_path)

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


def load_docx(file_path: str) -> str:
    """
    Reads text from .docx file.
    """
    document = Document(file_path)

    paragraphs = []

    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            paragraphs.append(paragraph.text.strip())

    return "\n".join(paragraphs)


def load_document(file_path: str) -> str:
    """
    Detects file extension and calls correct loader.
    """
    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".txt":
        return load_txt(file_path)

    if extension == ".pdf":
        return load_pdf(file_path)

    if extension == ".docx":
        return load_docx(file_path)

    raise ValueError("Unsupported file type. Please upload .txt, .pdf, or .docx file.")


def clean_text(text: str) -> str:
    """
    Cleans unnecessary spaces and blank lines.
    """
    text = text.replace("\r", " ")
    text = text.replace("\t", " ")

    lines = []

    for line in text.splitlines():
        clean_line = line.strip()

        if clean_line:
            lines.append(clean_line)

    return "\n".join(lines)


def chunk_text(text: str) -> List[str]:
    """
    Splits large document text into smaller overlapping chunks.
    RAG works better with chunks instead of sending full document at once.
    """
    text = clean_text(text)

    chunks = []
    start = 0

    while start < len(text):
        end = start + CHUNK_SIZE

        chunk = text[start:end]

        if chunk.strip():
            chunks.append(chunk.strip())

        start = end - CHUNK_OVERLAP

        if start < 0:
            start = 0

    return chunks