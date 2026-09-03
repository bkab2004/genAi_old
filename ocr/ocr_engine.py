"""
GenVendorAI OCR Engine Module
Provides optical character recognition fallback for scanned, image-based, or non-searchable PDF documents.
Combines PyMuPDF page rendering / pdf2image with pytesseract OCR and image contrast enhancement.
"""

import os
from typing import Tuple, Dict, Any, Union
from PIL import Image, ImageEnhance, ImageFilter
from ocr.pdf_extractor import extract_text_from_pdf_digital


def preprocess_image_for_ocr(image: Image.Image) -> Image.Image:
    """Applies grayscale conversion, contrast enhancement, and noise reduction."""
    try:
        # Convert to Grayscale
        gray_image = image.convert("L")
        # Increase contrast
        enhancer = ImageEnhance.Contrast(gray_image)
        enhanced_image = enhancer.enhance(1.8)
        # Apply slight sharpening
        sharpened_image = enhanced_image.filter(ImageFilter.SHARPEN)
        return sharpened_image
    except Exception:
        return image


def extract_text_using_ocr(pdf_path: str) -> Tuple[str, Dict[str, Any]]:
    """
    Renders PDF pages to images and runs Tesseract OCR on each page.
    Handles environments where external poppler or tesseract might be missing.
    """
    metadata = {
        "filename": os.path.basename(pdf_path),
        "extraction_method": "OCR (Tesseract Engine)",
        "ocr_success": False,
        "notes": ""
    }

    images = []

    # Step 1: Convert PDF to images using PyMuPDF (no poppler external dependency needed!)
    try:
        import pymupdf as fitz
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc[page_num]
            # Render at high DPI (2.0 zoom = 144 DPI, 3.0 zoom = 216 DPI)
            matrix = fitz.Matrix(2.0, 2.0)
            pix = page.get_pixmap(matrix=matrix)
            mode = "RGBA" if pix.alpha else "RGB"
            img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
            images.append(img.convert("RGB"))
        doc.close()
    except Exception as e_fitz:
        # Fallback to pdf2image
        try:
            from pdf2image import convert_from_path
            images = convert_from_path(pdf_path, dpi=200)
        except Exception as e_pdf2img:
            metadata["notes"] = f"Image conversion failed: PyMuPDF ({e_fitz}), pdf2image ({e_pdf2img})"

    if not images:
        return "", metadata

    # Step 2: Run Tesseract OCR on rendered images
    extracted_pages = []
    try:
        import pytesseract
        for idx, img in enumerate(images):
            preprocessed = preprocess_image_for_ocr(img)
            # Run Tesseract with custom config
            page_text = pytesseract.image_to_string(preprocessed, config="--psm 6")
            if page_text and page_text.strip():
                extracted_pages.append(page_text.strip())
            else:
                # Retry with default PSM
                page_text_def = pytesseract.image_to_string(preprocessed)
                if page_text_def and page_text_def.strip():
                    extracted_pages.append(page_text_def.strip())

        full_text = "\n\n".join(extracted_pages)
        if full_text.strip():
            metadata["ocr_success"] = True
            return full_text.strip(), metadata
        else:
            metadata["notes"] = "OCR executed but no text was recognized on image."
    except Exception as e_tess:
        metadata["notes"] = (
            f"Tesseract OCR not accessible or errored: {e_tess}. "
            "Please ensure Tesseract is installed and configured in system PATH."
        )

    return "", metadata


def extract_text_from_pdf(pdf_path: str, return_meta: bool = False) -> Union[str, Tuple[str, str, Dict[str, Any]]]:
    """
    Unified PDF text extraction pipeline:
    1. First attempts digital text layer extraction via PyMuPDF / pdfplumber.
    2. If text is empty or insufficient (< 50 characters), triggers OCR fallback automatically.
    
    Returns:
        If return_meta is False: extracted_text (str)
        If return_meta is True: (extracted_text, method_used, metadata_dict)
    """
    # Step 1: Try digital extraction
    digital_text, meta_dig = extract_text_from_pdf_digital(pdf_path)
    
    if digital_text and len(digital_text.strip()) >= 50:
        method = "DIRECT (Digital Text Layer)"
        if return_meta:
            meta_dig["extraction_method"] = method
            return digital_text, method, meta_dig
        return digital_text

    # Step 2: Insufficient digital text -> Trigger OCR Fallback
    ocr_text, meta_ocr = extract_text_using_ocr(pdf_path)
    
    if ocr_text and len(ocr_text.strip()) > 0:
        method = "OCR (Tesseract Image Extraction)"
        if return_meta:
            meta_ocr["extraction_method"] = method
            return ocr_text, method, meta_ocr
        return ocr_text

    # Fallback to whatever digital text was available, or return empty
    method = "DIRECT (Partial / Incomplete)" if digital_text else "FAILED (No text extracted)"
    if return_meta:
        combined_meta = {**meta_dig, **meta_ocr}
        combined_meta["extraction_method"] = method
        return digital_text or "", method, combined_meta
    return digital_text or ""
