import io

import pymupdf
from docx import Document


def extract_pdf_text(file_bytes: bytes) -> str:
    
    document = pymupdf.open(
        stream=file_bytes,
        filetype="pdf"
    )

    text = ""

    for page in document:
        text += page.get_text()

    document.close()

    return text.strip()


def extract_docx_text(file_bytes: bytes) -> str:

    document = Document(
        io.BytesIO(file_bytes)
    )

    text = []

    for paragraph in document.paragraphs:

        if paragraph.text.strip():
            text.append(
                paragraph.text.strip()
            )

    return "\n".join(text).strip()


def extract_resume_text(
    file_bytes: bytes,
    file_type: str
) -> str:

    if file_type == "pdf":

        return extract_pdf_text(file_bytes)

    if file_type == "docx":

        return extract_docx_text(file_bytes)

    raise ValueError(
        "Unsupported file type"
    )