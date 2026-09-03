"""
GenVendorAI Process Routes
Endpoints for document upload, OCR extraction, statutory validation,
semantic deduplication, and explainable AI risk scoring.
"""

import os
import json
import shutil
from typing import Dict, Any, List
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

from database.database import (
    save_vendor, save_document_record, save_assessment_record,
    check_duplicate, init_db
)
from ocr.ocr_engine import extract_text_from_pdf
from ocr.extractor import extract_vendor_details
from validation.validator import validate_vendor
from ai.embeddings import get_vendor_embedding_text
from ai.vector_store import add_vendor_to_index, search_similar_vendors
from ai.risk_engine import generate_vendor_risk_assessment
from audit.audit_logger import log_event
from reports.report_generator import generate_vendor_pdf_report, generate_vendor_html_report
from sample_data.generate_sample_pdfs import SAMPLE_DOCS_DIR

router = APIRouter(prefix="/api/process", tags=["Document Processing & Pipeline"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UPLOAD_DIR = os.path.join(BASE_DIR, "documents", "uploads")


def _run_pipeline_for_file(pdf_path: str, filename: str) -> Dict[str, Any]:
    """Executes the complete 7-step vendor intelligence pipeline."""
    # Step 1: Text & OCR Extraction
    extracted_text, method_used, doc_meta = extract_text_from_pdf(pdf_path, return_meta=True)
    
    log_event(
        event_type="DOCUMENT_UPLOADED",
        vendor_name=filename,
        status="SUCCESS",
        details={"filename": filename, "method": method_used, "char_count": len(extracted_text)}
    )

    # Step 2: Information Extraction
    vendor_details = extract_vendor_details(extracted_text)
    vendor_details["source_document"] = filename

    log_event(
        event_type="VENDOR_EXTRACTED",
        vendor_name=vendor_details.get("Vendor Name"),
        status="SUCCESS",
        details=vendor_details
    )

    # Step 3: Statutory Validation
    validation_results = validate_vendor(vendor_details)
    val_score = validation_results.get("Validation Score", 0.0)
    overall_valid = validation_results.get("Overall Status", False)

    log_event(
        event_type="VALIDATION_COMPLETED",
        vendor_name=vendor_details.get("Vendor Name"),
        status="SUCCESS" if overall_valid else "FAILED",
        details={"score": val_score, "results": validation_results.get("Details")}
    )

    # Step 4: Exact Duplicate Check
    is_dup, dup_field, existing_record = check_duplicate(vendor_details)
    
    log_event(
        event_type="DUPLICATE_CHECKED",
        vendor_name=vendor_details.get("Vendor Name"),
        status="DUPLICATE" if is_dup else "UNIQUE",
        details={"is_duplicate": is_dup, "duplicate_field": dup_field}
    )

    # Step 5: Semantic Similarity (FAISS)
    query_text = get_vendor_embedding_text(vendor_details)
    similar_vendors = search_similar_vendors(query_text, top_k=3, threshold=0.10)
    
    max_sim = 0.0
    top_similar_name = None
    if similar_vendors:
        for item in similar_vendors:
            v_name = item["vendor"].get("Vendor Name") or item["vendor"].get("vendor_name", "")
            sim = item["similarity"]
            if v_name.lower() != vendor_details.get("Vendor Name", "").lower():
                if sim > max_sim:
                    max_sim = sim
                    top_similar_name = v_name

    # Step 6: AI Risk Assessment
    assessment = generate_vendor_risk_assessment(
        vendor_details=vendor_details,
        is_duplicate=is_dup,
        duplicate_reason=dup_field,
        max_semantic_similarity=max_sim,
        most_similar_vendor_name=top_similar_name
    )

    risk_score = assessment["Risk Score"]
    risk_level = assessment["Risk Level"]
    recommendation = assessment["Recommendation"]

    vendor_details["Risk Score"] = risk_score
    vendor_details["Risk Level"] = risk_level
    vendor_details["Recommendation"] = recommendation
    vendor_details["Validation Status"] = "VALID" if overall_valid else "INVALID"
    vendor_details["Duplicate Status"] = "DUPLICATE" if is_dup else "UNIQUE"
    vendor_details["Similarity Score"] = max_sim

    log_event(
        event_type="RISK_ASSESSMENT_COMPLETED",
        vendor_name=vendor_details.get("Vendor Name"),
        status="SUCCESS",
        details=assessment
    )

    # Step 7: Final Decision & Persistence
    vendor_id = None
    if not is_dup:
        vendor_id = save_vendor(vendor_details)
        save_document_record(
            vendor_id=vendor_id,
            filename=filename,
            file_path=pdf_path,
            extraction_method=method_used,
            extracted_text=extracted_text
        )
        save_assessment_record(
            vendor_id=vendor_id,
            gstin=vendor_details.get("GSTIN", ""),
            risk_score=risk_score,
            risk_level=risk_level,
            recommendation=recommendation,
            positive_findings=json.dumps(assessment.get("Positive Findings", [])),
            risk_factors=json.dumps(assessment.get("Risk Factors", [])),
            summary=assessment.get("Summary", "")
        )
        add_vendor_to_index(vendor_details)
        
        log_event(
            event_type="VENDOR_CREATED",
            vendor_id=vendor_id,
            vendor_name=vendor_details.get("Vendor Name"),
            status="SUCCESS",
            details={"recommendation": recommendation, "risk_score": risk_score}
        )

    # Generate PDF report
    pdf_report_path = generate_vendor_pdf_report(vendor_details, assessment)
    pdf_filename = os.path.basename(pdf_report_path) if pdf_report_path and os.path.exists(pdf_report_path) else None

    return {
        "success": True,
        "vendor_id": vendor_id,
        "filename": filename,
        "step1_ocr": {
            "method": method_used,
            "char_count": len(extracted_text),
            "page_count": doc_meta.get("page_count", 1),
            "extracted_text": extracted_text
        },
        "step2_fields": vendor_details,
        "step3_validation": {
            "overall_status": overall_valid,
            "validation_score": val_score,
            "fields": validation_results.get("Details", {})
        },
        "step4_duplicate": {
            "is_duplicate": is_dup,
            "duplicate_field": dup_field,
            "existing_record": existing_record
        },
        "step5_similarity": {
            "top_similarity_score": max_sim,
            "top_similar_name": top_similar_name,
            "peers": similar_vendors
        },
        "step6_risk_assessment": assessment,
        "step7_decision": {
            "recommendation": recommendation,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "saved_to_db": not is_dup,
            "pdf_report_filename": pdf_filename
        }
    }


@router.post("/upload")
async def upload_and_process_document(file: UploadFile = File(...)):
    """Uploads a PDF file and executes the 7-step vendor intelligence pipeline."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF documents are supported.")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    saved_path = os.path.join(UPLOAD_DIR, file.filename)
    
    with open(saved_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        result = _run_pipeline_for_file(saved_path, file.filename)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline processing failed: {str(e)}")


@router.get("/samples")
def list_sample_documents():
    """Lists available pre-generated sample vendor PDFs."""
    if not os.path.exists(SAMPLE_DOCS_DIR):
        return {"samples": []}
    files = [f for f in os.listdir(SAMPLE_DOCS_DIR) if f.endswith(".pdf")]
    return {"samples": files}


@router.post("/sample/{filename}")
def process_sample_document(filename: str):
    """Processes a chosen sample PDF by filename."""
    pdf_path = os.path.join(SAMPLE_DOCS_DIR, filename)
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail=f"Sample file not found: {filename}")

    try:
        result = _run_pipeline_for_file(pdf_path, filename)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sample processing failed: {str(e)}")
