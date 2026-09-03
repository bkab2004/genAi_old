"""
GenVendorAI Report Routes
Endpoints for generating and downloading PDF and HTML compliance dossiers,
including individual vendor risk assessments and consolidated executive summary PDFs.
"""

import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from database.database import get_vendor_by_id, get_latest_assessment, get_all_vendors, get_vendor_stats
from reports.report_generator import (
    generate_vendor_pdf_report, generate_vendor_html_report,
    generate_executive_summary_pdf_report
)

router = APIRouter(prefix="/api/reports", tags=["Compliance Reports & PDF Generation"])


@router.get("/summary/pdf")
def download_executive_summary_pdf():
    """Generates and serves a consolidated executive master vendor briefing PDF."""
    vendors = get_all_vendors()
    stats = get_vendor_stats()

    pdf_path = generate_executive_summary_pdf_report(vendors, stats)

    if not pdf_path or not os.path.exists(pdf_path):
        raise HTTPException(status_code=500, detail="Failed to generate executive PDF report.")

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=os.path.basename(pdf_path)
    )


@router.get("/{vendor_id}/pdf")
def download_pdf_report(vendor_id: int):
    """Generates and serves a downloadable individual vendor assessment PDF report."""
    vendor = get_vendor_by_id(vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    assessment = get_latest_assessment(vendor_id)
    pdf_path = generate_vendor_pdf_report(vendor, assessment)

    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=500, detail="Failed to generate PDF report file")

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=os.path.basename(pdf_path)
    )


@router.get("/{vendor_id}/html", response_class=HTMLResponse)
def view_html_report(vendor_id: int):
    """Generates and renders a standalone web compliance report."""
    vendor = get_vendor_by_id(vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    assessment = get_latest_assessment(vendor_id)
    html_content = generate_vendor_html_report(vendor, assessment)
    return HTMLResponse(content=html_content)
