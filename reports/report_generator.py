"""
GenVendorAI Report Generator Module
Generates professional audit and risk assessment reports in PDF format using ReportLab
and printable styled HTML formats.
"""

import os
from typing import Dict, Any, Optional, List
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")


def generate_vendor_html_report(vendor: Dict[str, Any], assessment: Optional[Dict[str, Any]] = None) -> str:
    """Generates an HTML string formatted for printing or browser rendering."""
    name = vendor.get("vendor_name") or vendor.get("Vendor Name", "Unknown Vendor")
    gstin = vendor.get("gstin") or vendor.get("GSTIN", "N/A")
    pan = vendor.get("pan") or vendor.get("PAN", "N/A")
    category = vendor.get("business_category") or vendor.get("Business Category", "N/A")
    address = vendor.get("address") or vendor.get("Address", "N/A")
    email = vendor.get("email") or vendor.get("Email", "N/A")
    phone = vendor.get("phone") or vendor.get("Phone", "N/A")
    contact = vendor.get("contact_person") or vendor.get("Contact Person", "N/A")
    bank = vendor.get("bank_name") or vendor.get("Bank Name", "N/A")
    acc = vendor.get("account_number") or vendor.get("Account Number", "N/A")
    ifsc = vendor.get("ifsc_code") or vendor.get("IFSC Code", "N/A")

    risk_score = vendor.get("risk_score", 0)
    risk_level = vendor.get("risk_level", "UNKNOWN")
    rec = vendor.get("recommendation", "REVIEW")
    val_status = vendor.get("validation_status", "VALID")
    dup_status = vendor.get("duplicate_status", "UNIQUE")
    source_doc = vendor.get("source_document", "Uploaded Document")

    # Colors
    rec_color = "#10b981" if rec == "APPROVE" else ("#f59e0b" if rec == "REVIEW" else "#ef4444")
    risk_color = "#10b981" if risk_level == "LOW" else ("#f59e0b" if risk_level == "MEDIUM" else "#ef4444")

    # Positive & Risk factor lists
    positive_items = []
    risk_items = []
    summary = "Assessment completed."

    if assessment:
        summary = assessment.get("summary", summary)
        pos = assessment.get("positive_findings", [])
        if isinstance(pos, str):
            import json
            try:
                pos = json.loads(pos)
            except:
                pos = [pos]
        positive_items = pos if isinstance(pos, list) else []

        rf = assessment.get("risk_factors", [])
        if isinstance(rf, str):
            import json
            try:
                rf = json.loads(rf)
            except:
                rf = [rf]
        risk_items = rf if isinstance(rf, list) else []

    pos_html = "".join([f"<li>✅ {item}</li>" for item in positive_items]) if positive_items else "<li>No positive findings recorded.</li>"
    risk_html = "".join([f"<li>⚠️ {item}</li>" for item in risk_items]) if risk_items else "<li>No major risk factors detected.</li>"

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>GenVendorAI Assessment Report - {name}</title>
<style>
    body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #1e293b; margin: 40px; background: #f8fafc; }}
    .report-card {{ background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 36px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); max-width: 900px; margin: auto; }}
    .header {{ border-bottom: 2px solid #3b82f6; padding-bottom: 20px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: center; }}
    .header-title {{ margin: 0; color: #1e3a8a; font-size: 24px; font-weight: 700; }}
    .badge {{ display: inline-block; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 14px; color: #fff; }}
    .kpi-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin: 24px 0; }}
    .kpi-box {{ background: #f1f5f9; border-radius: 8px; padding: 16px; text-align: center; }}
    .kpi-val {{ font-size: 22px; font-weight: 700; margin-top: 4px; }}
    table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
    th, td {{ padding: 10px 14px; border-bottom: 1px solid #e2e8f0; text-align: left; font-size: 14px; }}
    th {{ background: #f8fafc; color: #475569; width: 30%; }}
    .section-title {{ color: #0f172a; font-size: 18px; font-weight: 600; margin-top: 28px; border-bottom: 1px solid #cbd5e1; padding-bottom: 6px; }}
    ul {{ padding-left: 20px; }}
    li {{ margin-bottom: 6px; font-size: 14px; }}
    .footer {{ margin-top: 40px; border-top: 1px solid #e2e8f0; padding-top: 16px; font-size: 12px; color: #64748b; text-align: center; }}
</style>
</head>
<body>
<div class="report-card">
    <div class="header">
        <div>
            <h1 class="header-title">🤖 GenVendorAI Intelligence Report</h1>
            <p style="margin: 4px 0 0 0; color: #64748b; font-size: 13px;">AI-Powered Vendor Master Data & Risk Assessment System</p>
        </div>
        <div>
            <span class="badge" style="background: {rec_color};">{rec}</span>
        </div>
    </div>

    <div class="kpi-grid">
        <div class="kpi-box">
            <div style="font-size: 12px; color: #64748b; text-transform: uppercase;">Risk Score</div>
            <div class="kpi-val" style="color: {risk_color};">{risk_score} / 100</div>
        </div>
        <div class="kpi-box">
            <div style="font-size: 12px; color: #64748b; text-transform: uppercase;">Risk Classification</div>
            <div class="kpi-val" style="color: {risk_color};">{risk_level}</div>
        </div>
        <div class="kpi-box">
            <div style="font-size: 12px; color: #64748b; text-transform: uppercase;">Decision Recommendation</div>
            <div class="kpi-val" style="color: {rec_color};">{rec}</div>
        </div>
    </div>

    <div class="section-title">📋 Vendor Master Profile</div>
    <table>
        <tr><th>Vendor / Entity Name</th><td><strong>{name}</strong></td></tr>
        <tr><th>GSTIN</th><td><code>{gstin}</code></td></tr>
        <tr><th>Income Tax PAN</th><td><code>{pan}</code></td></tr>
        <tr><th>Business Category</th><td>{category}</td></tr>
        <tr><th>Registered Address</th><td>{address}</td></tr>
        <tr><th>Contact Person</th><td>{contact}</td></tr>
        <tr><th>Email Address</th><td>{email}</td></tr>
        <tr><th>Contact Phone</th><td>{phone}</td></tr>
        <tr><th>Banking Information</th><td>{bank} | A/C: {acc} | IFSC: {ifsc}</td></tr>
        <tr><th>Validation & Integrity</th><td>Status: <strong>{val_status}</strong> | Deduplication: <strong>{dup_status}</strong></td></tr>
        <tr><th>Source Document</th><td>{source_doc}</td></tr>
    </table>

    <div class="section-title">📝 Executive Assessment Summary</div>
    <p style="background: #eff6ff; border-left: 4px solid #3b82f6; padding: 12px 16px; border-radius: 4px; font-size: 14px; margin: 12px 0;">
        {summary}
    </p>

    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 16px;">
        <div>
            <div class="section-title" style="color: #059669; font-size: 16px;">✅ Verified Compliance Strengths</div>
            <ul>{pos_html}</ul>
        </div>
        <div>
            <div class="section-title" style="color: #dc2626; font-size: 16px;">⚠️ Flagged Risk Factors & Exceptions</div>
            <ul>{risk_html}</ul>
        </div>
    </div>

    <div class="footer">
        Generated on {datetime.now().strftime("%B %d, %Y at %I:%M %p")} by GenVendorAI System | Confidential Procurement Master Record
    </div>
</div>
</body>
</html>
"""
    return html


def generate_vendor_pdf_report(vendor: Dict[str, Any], assessment: Optional[Dict[str, Any]] = None) -> str:
    """
    Generates a professional single-vendor assessment dossier PDF using ReportLab.
    Returns the generated PDF file path.
    """
    os.makedirs(REPORTS_DIR, exist_ok=True)
    vendor_name = vendor.get("vendor_name") or vendor.get("Vendor Name", "Vendor")
    safe_name = "".join(c for c in vendor_name if c.isalnum() or c in (" ", "_", "-")).rstrip().replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_path = os.path.join(REPORTS_DIR, f"Assessment_Report_{safe_name}_{timestamp}.pdf")

    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors

        doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        story = []
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#1E3A8A"),
            spaceAfter=4
        )
        subtitle_style = ParagraphStyle(
            'SubTitleStyle',
            parent=styles['Normal'],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#64748B"),
            spaceAfter=10
        )
        section_style = ParagraphStyle(
            'SectionStyle',
            parent=styles['Heading2'],
            fontSize=12,
            leading=15,
            textColor=colors.HexColor("#0F172A"),
            spaceBefore=12,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            'BodyStyle',
            parent=styles['Normal'],
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor("#1E293B")
        )
        bold_body_style = ParagraphStyle(
            'BoldBodyStyle',
            parent=styles['Normal'],
            fontSize=8.5,
            leading=12,
            fontName="Helvetica-Bold",
            textColor=colors.HexColor("#0F172A")
        )

        # Header
        story.append(Paragraph("🤖 GenVendorAI Intelligence Assessment Report", title_style))
        story.append(Paragraph(f"AI-Powered Vendor Master Data Management & Risk Evaluation System • Generated: {datetime.now().strftime('%d-%b-%Y %H:%M')}", subtitle_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#3B82F6"), spaceAfter=12))

        # KPI Summary Block Table
        risk_score = vendor.get("risk_score", 0)
        risk_level = vendor.get("risk_level", "UNKNOWN")
        rec = vendor.get("recommendation", "REVIEW")

        rec_bg = colors.HexColor("#D1FAE5") if rec == "APPROVE" else (colors.HexColor("#FEF3C7") if rec == "REVIEW" else colors.HexColor("#FEE2E2"))
        rec_text_color = colors.HexColor("#065F46") if rec == "APPROVE" else (colors.HexColor("#92400E") if rec == "REVIEW" else colors.HexColor("#991B1B"))

        kpi_data = [
            [
                Paragraph("<b>RISK SCORE</b>", body_style),
                Paragraph("<b>RISK LEVEL</b>", body_style),
                Paragraph("<b>RECOMMENDATION</b>", body_style)
            ],
            [
                Paragraph(f"<font size='13'><b>{risk_score} / 100</b></font>", bold_body_style),
                Paragraph(f"<font size='13'><b>{risk_level}</b></font>", bold_body_style),
                Paragraph(f"<font size='13' color='{rec_text_color.hexval()}'><b>{rec}</b></font>", bold_body_style)
            ]
        ]
        kpi_table = Table(kpi_data, colWidths=[180, 180, 180])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
            ('BACKGROUND', (2, 0), (2, 1), rec_bg),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ]))
        story.append(kpi_table)
        story.append(Spacer(1, 10))

        # Vendor Master Details Table
        story.append(Paragraph("📋 Vendor Master Record", section_style))
        vendor_rows = [
            [Paragraph("<b>Vendor / Entity Name:</b>", body_style), Paragraph(str(vendor.get("vendor_name") or vendor.get("Vendor Name", "N/A")), body_style)],
            [Paragraph("<b>GSTIN:</b>", body_style), Paragraph(str(vendor.get("gstin") or vendor.get("GSTIN", "N/A")), body_style)],
            [Paragraph("<b>Income Tax PAN:</b>", body_style), Paragraph(str(vendor.get("pan") or vendor.get("PAN", "N/A")), body_style)],
            [Paragraph("<b>Business Category:</b>", body_style), Paragraph(str(vendor.get("business_category") or vendor.get("Business Category", "N/A")), body_style)],
            [Paragraph("<b>Registered Address:</b>", body_style), Paragraph(str(vendor.get("address") or vendor.get("Address", "N/A")), body_style)],
            [Paragraph("<b>Contact Person:</b>", body_style), Paragraph(str(vendor.get("contact_person") or vendor.get("Contact Person", "N/A")), body_style)],
            [Paragraph("<b>Phone & Email:</b>", body_style), Paragraph(f"{vendor.get('phone', 'N/A')} | {vendor.get('email', 'N/A')}", body_style)],
            [Paragraph("<b>Banking Details:</b>", body_style), Paragraph(f"Bank: {vendor.get('bank_name', 'N/A')} | A/C: {vendor.get('account_number', 'N/A')} | IFSC: {vendor.get('ifsc_code', 'N/A')}", body_style)],
            [Paragraph("<b>Validation / Duplicate:</b>", body_style), Paragraph(f"Validation: {vendor.get('validation_status', 'VALID')} | Deduplication: {vendor.get('duplicate_status', 'UNIQUE')}", body_style)],
            [Paragraph("<b>Source Document:</b>", body_style), Paragraph(str(vendor.get("source_document", "Uploaded Document")), body_style)]
        ]
        vendor_table = Table(vendor_rows, colWidths=[140, 400])
        vendor_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#F8FAFC")),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor("#1E293B")),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        story.append(vendor_table)
        story.append(Spacer(1, 10))

        # Assessment Summary
        story.append(Paragraph("📝 AI Assessment Summary", section_style))
        summary_text = (assessment.get("summary") if assessment else None) or "Automated vendor evaluation completed against compliance and duplicate benchmarks."
        story.append(Paragraph(summary_text, body_style))
        story.append(Spacer(1, 8))

        # Positive Findings & Risk Factors
        story.append(Paragraph("✅ Verified Strengths & Compliance Findings", section_style))
        pos_findings = (assessment.get("positive_findings") if assessment else None) or []
        if isinstance(pos_findings, str):
            import json
            try:
                pos_findings = json.loads(pos_findings)
            except:
                pos_findings = [pos_findings]
        if pos_findings and isinstance(pos_findings, list):
            for pf in pos_findings:
                story.append(Paragraph(f"• <b>Verified:</b> {pf}", body_style))
        else:
            story.append(Paragraph("• Standard vendor profile recorded.", body_style))

        story.append(Spacer(1, 8))
        story.append(Paragraph("⚠️ Risk Factors & Exceptions", section_style))
        risk_factors = (assessment.get("risk_factors") if assessment else None) or []
        if isinstance(risk_factors, str):
            import json
            try:
                risk_factors = json.loads(risk_factors)
            except:
                risk_factors = [risk_factors]
        if risk_factors and isinstance(risk_factors, list):
            for rf in risk_factors:
                story.append(Paragraph(f"• <font color='#DC2626'><b>Flagged:</b></font> {rf}", body_style))
        else:
            story.append(Paragraph("• No critical risk factors identified.", body_style))

        story.append(Spacer(1, 16))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"), spaceAfter=6))
        story.append(Paragraph(
            "<i>This document is an AI-generated decision support report produced by GenVendorAI. Final onboarding authorization remains subject to procurement and compliance officer sign-off.</i>",
            subtitle_style
        ))

        doc.build(story)
        return pdf_path
    except Exception as e:
        print(f"[ReportLab Error] Failed to generate PDF ({e}). Writing HTML report fallback.")
        html_content = generate_vendor_html_report(vendor, assessment)
        html_path = pdf_path.replace(".pdf", ".html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        return html_path


def generate_executive_summary_pdf_report(all_vendors: List[Dict[str, Any]], stats: Dict[str, Any]) -> str:
    """
    Generates a multi-vendor executive briefing PDF report summarizing all records,
    KPI statistics, risk breakdowns, and active watchlists.
    """
    os.makedirs(REPORTS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_path = os.path.join(REPORTS_DIR, f"Executive_Vendor_Master_Report_{timestamp}.pdf")

    try:
        from reportlab.lib.pagesizes import letter, landscape
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors

        # Use Landscape for executive overview table
        doc = SimpleDocTemplate(pdf_path, pagesize=landscape(letter), rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
        story = []
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'ExecTitle',
            parent=styles['Heading1'],
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#1E3A8A"),
            spaceAfter=4
        )
        subtitle_style = ParagraphStyle(
            'ExecSub',
            parent=styles['Normal'],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#64748B"),
            spaceAfter=8
        )
        section_style = ParagraphStyle(
            'ExecSec',
            parent=styles['Heading2'],
            fontSize=12,
            leading=15,
            textColor=colors.HexColor("#0F172A"),
            spaceBefore=10,
            spaceAfter=6
        )
        th_style = ParagraphStyle(
            'ExecTH',
            parent=styles['Normal'],
            fontSize=8,
            leading=10,
            fontName="Helvetica-Bold",
            textColor=colors.HexColor("#FFFFFF")
        )
        td_style = ParagraphStyle(
            'ExecTD',
            parent=styles['Normal'],
            fontSize=7.5,
            leading=9.5,
            textColor=colors.HexColor("#1E293B")
        )

        # Header
        story.append(Paragraph("📊 GenVendorAI Master Vendor Intelligence & Executive Audit Report", title_style))
        story.append(Paragraph(f"Consolidated Enterprise MDM Dossier • Total Vendors: {stats.get('total_vendors', 0)} • Generated: {datetime.now().strftime('%d-%b-%Y %H:%M')}", subtitle_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#3B82F6"), spaceAfter=10))

        # KPI Summary Table
        kpi_row1 = [
            Paragraph("<b>TOTAL VENDORS</b>", td_style),
            Paragraph("<b>APPROVED (🟢)</b>", td_style),
            Paragraph("<b>UNDER REVIEW (🟡)</b>", td_style),
            Paragraph("<b>REJECTED (🔴)</b>", td_style),
            Paragraph("<b>LOW RISK</b>", td_style),
            Paragraph("<b>MEDIUM RISK</b>", td_style),
            Paragraph("<b>HIGH RISK</b>", td_style)
        ]
        kpi_row2 = [
            Paragraph(f"<font size='11'><b>{stats.get('total_vendors', 0)}</b></font>", td_style),
            Paragraph(f"<font size='11' color='#059669'><b>{stats.get('approved', 0)}</b></font>", td_style),
            Paragraph(f"<font size='11' color='#D97706'><b>{stats.get('under_review', 0)}</b></font>", td_style),
            Paragraph(f"<font size='11' color='#DC2626'><b>{stats.get('rejected', 0)}</b></font>", td_style),
            Paragraph(f"<font size='11' color='#059669'><b>{stats.get('low_risk', 0)}</b></font>", td_style),
            Paragraph(f"<font size='11' color='#D97706'><b>{stats.get('medium_risk', 0)}</b></font>", td_style),
            Paragraph(f"<font size='11' color='#DC2626'><b>{stats.get('high_risk', 0)}</b></font>", td_style)
        ]
        kpi_table = Table([kpi_row1, kpi_row2], colWidths=[105, 105, 105, 105, 105, 105, 105])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1"))
        ]))
        story.append(kpi_table)
        story.append(Spacer(1, 10))

        # Master Table
        story.append(Paragraph("📋 Complete Vendor Master Records & Risk Classifications", section_style))
        table_data = [[
            Paragraph("ID", th_style),
            Paragraph("Vendor Name", th_style),
            Paragraph("Business Category", th_style),
            Paragraph("GSTIN", th_style),
            Paragraph("PAN", th_style),
            Paragraph("Risk (0-100)", th_style),
            Paragraph("Risk Tier", th_style),
            Paragraph("Decision", th_style),
            Paragraph("Validation", th_style)
        ]]

        for v in all_vendors:
            r_col = "#059669" if v.get("risk_level") == "LOW" else ("#D97706" if v.get("risk_level") == "MEDIUM" else "#DC2626")
            table_data.append([
                Paragraph(f"#{v.get('id', '')}", td_style),
                Paragraph(f"<b>{v.get('vendor_name', '')[:28]}</b>", td_style),
                Paragraph(v.get('business_category', '')[:22], td_style),
                Paragraph(f"<code>{v.get('gstin', 'N/A')[:15]}</code>", td_style),
                Paragraph(f"<code>{v.get('pan', 'N/A')}</code>", td_style),
                Paragraph(f"<b>{v.get('risk_score', 0)}</b>", td_style),
                Paragraph(f"<font color='{r_col}'><b>{v.get('risk_level', 'N/A')}</b></font>", td_style),
                Paragraph(f"<b>{v.get('recommendation', 'N/A')}</b>", td_style),
                Paragraph(v.get('validation_status', 'VALID'), td_style)
            ])

        v_table = Table(table_data, colWidths=[35, 165, 130, 110, 80, 55, 65, 60, 50])
        v_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8FAFC")]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        story.append(v_table)
        story.append(Spacer(1, 14))

        # Footer Notice
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"), spaceAfter=4))
        story.append(Paragraph(
            "<i>GenVendorAI Executive Master Dossier • Department of Computer Science & Engineering (AI & ML), PCCOE Pune • Confidential</i>",
            subtitle_style
        ))

        doc.build(story)
        return pdf_path
    except Exception as e:
        print(f"[ReportLab Error] Failed to generate Executive PDF ({e})")
        return ""
