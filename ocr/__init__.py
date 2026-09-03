"""
GenVendorAI OCR & Document Ingestion Package
Provides PDF digital text parsing, OCR fallback, and structured pattern extraction for vendor documents.
"""

from ocr.pdf_extractor import extract_text_from_pdf_digital
from ocr.ocr_engine import extract_text_using_ocr, extract_text_from_pdf
from ocr.extractor import extract_vendor_details

__all__ = [
    "extract_text_from_pdf_digital",
    "extract_text_using_ocr",
    "extract_text_from_pdf",
    "extract_vendor_details"
]
