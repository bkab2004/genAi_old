"""
GenVendorAI Reports Package
Generates printable compliance and risk audit reports in PDF and HTML formats.
"""

from reports.report_generator import generate_vendor_pdf_report, generate_vendor_html_report

__all__ = [
    "generate_vendor_pdf_report",
    "generate_vendor_html_report"
]
