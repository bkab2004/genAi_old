"""
GenVendorAI PDF Digital Text Extractor Module
Handles direct text layer extraction using PyMuPDF (fitz) or pdfplumber.
"""

import os
from typing import Tuple, Dict, Any


def extract_text_from_pdf_digital(pdf_path: str) -> Tuple[str, Dict[str, Any]]:
    """
    Extracts selectable text and metadata from a PDF file using PyMuPDF (fitz) or pdfplumber.
    
    Returns:
        tuple: (extracted_text: str, metadata: dict)
    """
    if not os.path.exists(pdf_path):
        return "", {"error": f"File not found: {pdf_path}", "page_count": 0}

    extracted_text = ""
    metadata = {
        "filename": os.path.basename(pdf_path),
        "page_count": 0,
        "extraction_method": "PyMuPDF (Digital Text Layer)"
    }

    # Attempt 1: PyMuPDF
    try:
        import pymupdf as fitz
        doc = fitz.open(pdf_path)
        metadata["page_count"] = len(doc)
        pages_text = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            if text and text.strip():
                pages_text.append(text.strip())
        doc.close()
        
        extracted_text = "\n\n".join(pages_text)
        if len(extracted_text.strip()) >= 50:
            return extracted_text, metadata
    except Exception as e:
        metadata["fitz_error"] = str(e)

    # Attempt 2: pdfplumber fallback
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            metadata["page_count"] = len(pdf.pages)
            pages_text = []
            for page in pdf.pages:
                text = page.extract_text()
                if text and text.strip():
                    pages_text.append(text.strip())
            extracted_text = "\n\n".join(pages_text)
            if len(extracted_text.strip()) >= 50:
                metadata["extraction_method"] = "pdfplumber (Digital Text Layer)"
                return extracted_text, metadata
    except Exception as e:
        metadata["pdfplumber_error"] = str(e)

    return extracted_text.strip(), metadata
