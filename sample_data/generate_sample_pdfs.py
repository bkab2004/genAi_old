"""
GenVendorAI Sample PDF Generator Module
Generates realistic vendor registration, GST, and onboarding PDF documents for live testing and demonstration.
"""

import os
from typing import List

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE_DOCS_DIR = os.path.join(BASE_DIR, "documents", "sample_docs")


SAMPLE_DOCS_DATA = [
    {
        "filename": "Sample_1_IT_InnovateTech_Solutions.pdf",
        "title": "VENDOR REGISTRATION & ONBOARDING FORM",
        "lines": [
            ("Vendor Name", "InnovateTech AI Solutions Pvt Ltd"),
            ("Business Category", "Information Technology"),
            ("GSTIN", "27AAACI9900B1Z4"),
            ("PAN", "AAACI9900B"),
            ("Address", "Cyber Park, Tower B, Level 6, Viman Nagar, Pune, Maharashtra 411014"),
            ("Contact Person", "Rohit Verma"),
            ("Designation", "Chief Operating Officer"),
            ("Phone", "9822098765"),
            ("Email", "onboarding@innovatetechai.com"),
            ("Bank Name", "HDFC Bank"),
            ("Account Number", "50200088997766"),
            ("IFSC Code", "HDFC0001045"),
            ("Services Offered", "Custom Enterprise Software, Machine Learning Pipelines, Cloud Infrastructure Optimization")
        ]
    },
    {
        "filename": "Sample_2_Construction_MetroBuild_Infra.pdf",
        "title": "SUPPLIER MASTER DATA SHEET - CONSTRUCTION",
        "lines": [
            ("Vendor Name", "MetroBuild Civil Infrastructure LLP"),
            ("Business Category", "Construction & Infrastructure"),
            ("GSTIN", "27AABFM4433E1Z6"),
            ("PAN", "AABFM4433E"),
            ("Address", "Plot 45, Industrial Corridor, Taloja MIDC, Navi Mumbai, Maharashtra 410208"),
            ("Contact Person", "Sunil Kadam"),
            ("Designation", "General Manager - Commercial"),
            ("Phone", "9819012389"),
            ("Email", "tenders@metrobuildinfra.com"),
            ("Bank Name", "State Bank of India"),
            ("Account Number", "389201994821"),
            ("IFSC Code", "SBIN0001289"),
            ("Specialization", "Highway construction, industrial precast structures, earthmoving and foundation engineering")
        ]
    },
    {
        "filename": "Sample_3_Manufacturing_ApexForgings.pdf",
        "title": "GOVERNMENT GST & VENDOR PROFILE CERTIFICATE",
        "lines": [
            ("Vendor Name", "Apex Precision Forgings & Machine Tools Ltd"),
            ("Business Category", "Manufacturing & Industrial"),
            ("GSTIN", "24AABCA5566D1Z1"),
            ("PAN", "AABCA5566D"),
            ("Address", "Survey 88, GIDC Industrial Estate, Makarpura, Vadodara, Gujarat 390010"),
            ("Contact Person", "Dharmesh Patel"),
            ("Designation", "Head of Quality & Compliance"),
            ("Phone", "9879055443"),
            ("Email", "compliance@apexforgings.in"),
            ("Bank Name", "ICICI Bank"),
            ("Account Number", "014505008877"),
            ("IFSC Code", "ICIC0000145"),
            ("Capabilities", "CNC Milling, High Precision Automotive Gears, Hydraulic components")
        ]
    },
    {
        "filename": "Sample_4_Logistics_FalconTrans_Express.pdf",
        "title": "VENDOR COMPLIANCE & BANK VERIFICATION RECORD",
        "lines": [
            ("Vendor Name", "FalconTrans Multimodal Express Pvt Ltd"),
            ("Business Category", "Logistics & Supply Chain"),
            ("GSTIN", "29AABCF8822G1Z3"),
            ("PAN", "AABCF8822G"),
            ("Address", "Express Hub 7, Whitefield Outer Ring Road, Bengaluru, Karnataka 560066"),
            ("Contact Person", "Praveen Shenoy"),
            ("Designation", "Director of Logistics"),
            ("Phone", "9845011998"),
            ("Email", "fleet@falcontrainsexpress.com"),
            ("Bank Name", "Axis Bank"),
            ("Account Number", "914020088776655"),
            ("IFSC Code", "UTIB0000244"),
            ("Fleet", "GPS-tracked temperature-controlled reefer trucks, container freight stations")
        ]
    },
    {
        "filename": "Sample_5_High_Similarity_Test_Zenith_Cloud.pdf",
        "title": "VENDOR MASTER ONBOARDING APPLICATION",
        "lines": [
            ("Vendor Name", "Zenith Cloud Systems & Technology Solutions"),
            ("Business Category", "Information Technology"),
            ("GSTIN", "27AABCZ9999F1Z0"),
            ("PAN", "AABCZ9999F"),
            ("Address", "Tech Park Phase 2, Hinjewadi IT Corridor, Pune, Maharashtra 411057"),
            ("Contact Person", "Rakesh Sharma"),
            ("Phone", "9823099999"),
            ("Email", "billing@zenithcloudsolutions.com"),
            ("Bank Name", "HDFC Bank"),
            ("Account Number", "50200099887766"),
            ("IFSC Code", "HDFC0001234"),
            ("Note", "Intentionally formatted similar to Zenith Cloud Technologies to test AI semantic duplicate detection.")
        ]
    },
    {
        "filename": "Sample_6_High_Risk_Invalid_Document.pdf",
        "title": "UNVERIFIED SUPPLIER QUOTATION & ENROLLMENT",
        "lines": [
            ("Vendor Name", "QuickSupplies Offshore Traders"),
            ("Business Category", "Facilities & Office Supplies"),
            ("GSTIN", "99INVALIDGST999"),
            ("PAN", "XYZ12345"),
            ("Address", "Temporary Shed 4, Unregistered Lane"),
            ("Contact Person", "Unknown Signatory"),
            ("Phone", "12345"),
            ("Email", "fake_mail_address"),
            ("Bank Name", "Unknown Bank"),
            ("Account Number", "0000"),
            ("IFSC Code", "INVALIDIFSC"),
            ("Alert", "High Risk document containing invalid GST, malformed PAN, missing banking details to test rejection engine.")
        ]
    }
]


def generate_all_sample_pdfs() -> List[str]:
    """
    Generates all sample PDF documents in the documents/sample_docs folder.
    Returns list of generated file paths.
    """
    os.makedirs(SAMPLE_DOCS_DIR, exist_ok=True)
    generated_files = []

    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=16,
            leading=20,
            textColor=colors.HexColor("#1E3A8A"),
            alignment=1,
            spaceAfter=8
        )
        body_style = ParagraphStyle(
            'BodyStyle',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#1E293B")
        )
        bold_style = ParagraphStyle(
            'BoldStyle',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            fontName="Helvetica-Bold",
            textColor=colors.HexColor("#0F172A")
        )

        for item in SAMPLE_DOCS_DATA:
            pdf_path = os.path.join(SAMPLE_DOCS_DIR, item["filename"])
            doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
            story = []

            story.append(Paragraph(item["title"], title_style))
            story.append(Paragraph("<font size='9' color='#64748B'><b>OFFICIAL MASTER DATA VERIFICATION RECORD</b></font>", ParagraphStyle('Sub', alignment=1, spaceAfter=12)))
            story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#3B82F6"), spaceAfter=14))

            table_rows = []
            for label, val in item["lines"]:
                table_rows.append([
                    Paragraph(f"<b>{label}:</b>", bold_style),
                    Paragraph(str(val), body_style)
                ])

            table = Table(table_rows, colWidths=[150, 380])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#F8FAFC")),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
            ]))
            story.append(table)
            story.append(Spacer(1, 20))
            story.append(Paragraph(
                "<font size='8' color='#94A3B8'>This document was generated automatically for GenVendorAI research and evaluation test suites.</font>",
                ParagraphStyle('Note', alignment=1)
            ))

            doc.build(story)
            generated_files.append(pdf_path)

    except Exception as e:
        print(f"[SamplePDFs] Warning: PDF generation failed ({e}). Creating text backups.")
        for item in SAMPLE_DOCS_DATA:
            txt_path = os.path.join(SAMPLE_DOCS_DIR, item["filename"].replace(".pdf", ".txt"))
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(f"=== {item['title']} ===\n\n")
                for k, v in item["lines"]:
                    f.write(f"{k}: {v}\n")
            generated_files.append(txt_path)

    return generated_files
