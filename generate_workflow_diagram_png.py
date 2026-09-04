"""
Generate High-Resolution (300 DPI 4K) System Architecture & Workflow Block Diagram PNG
for GenVendorAI – AI-Powered Vendor Intelligence and Risk Assessment System.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PNG = os.path.join(BASE_DIR, "GenVendorAI_System_Workflow_BlockDiagram.png")


def create_diagram():
    # 16:9 Aspect Ratio Figure (High Resolution 3840 x 2160 at 300 DPI)
    fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=300)
    fig.patch.set_facecolor('#0B0F19')
    ax.set_facecolor('#0B0F19')
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Color Palette
    C_HEADER = '#1E3A8A'
    C_BLUE = '#2563EB'
    C_CYAN = '#06B6D4'
    C_EMERALD = '#059669'
    C_AMBER = '#D97706'
    C_PURPLE = '#7C3AED'
    C_ROSE = '#E11D48'
    C_CARD_BG = '#111827'
    C_CARD_BORDER = '#374151'
    C_TEXT_WHITE = '#F8FAFC'
    C_TEXT_MUTED = '#94A3B8'
    C_TEXT_ACCENT = '#38BDF8'

    # Title Header Block
    header_box = patches.FancyBboxPatch(
        (2, 88), 96, 10,
        boxstyle="round,pad=0.5,rounding_size=1.2",
        fc='#0F172A', ec='#3B82F6', lw=2
    )
    ax.add_patch(header_box)
    
    ax.text(50, 95, "GenVendorAI: AI-Powered Vendor Intelligence & Risk Assessment System",
            fontsize=18, fontweight='bold', color=C_TEXT_WHITE, ha='center', va='center')
    ax.text(50, 90.5, "End-to-End Autonomous Workflow • Multi-Modal Document AI • Sentence-BERT • FAISS Vector Store • Statutory Compliance • Explainable Decision Support",
            fontsize=9.5, fontweight='medium', color=C_TEXT_ACCENT, ha='center', va='center')

    # Helper function to draw stage cards
    def draw_card(x, y, w, h, title, stage_num, icon_text, items, border_color, accent_badge=None):
        card = patches.FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.6,rounding_size=1.0",
            fc=C_CARD_BG, ec=border_color, lw=2
        )
        ax.add_patch(card)

        # Header Ribbon
        ribbon = patches.FancyBboxPatch(
            (x, y + h - 4.5), w, 4.5,
            boxstyle="round,pad=0.2,rounding_size=0.8",
            fc=border_color, ec='none'
        )
        ax.add_patch(ribbon)
        
        # Stage Badge
        ax.text(x + 1.5, y + h - 2.2, f"STAGE {stage_num}",
                fontsize=7.5, fontweight='bold', color='#FFFFFF', va='center')
        ax.text(x + w - 1.5, y + h - 2.2, icon_text,
                fontsize=8, fontweight='bold', color='#FFFFFF', ha='right', va='center')

        # Title
        ax.text(x + w/2, y + h - 7, title,
                fontsize=11, fontweight='bold', color=C_TEXT_WHITE, ha='center', va='center')
        
        # Divider Line
        ax.plot([x + 2, x + w - 2], [y + h - 9.5, y + h - 9.5], color='#374151', lw=1)

        # Content Bullet Items
        curr_y = y + h - 13
        for item in items:
            ax.text(x + 2, curr_y, item, fontsize=7.2, color='#E2E8F0', va='top', wrap=True)
            curr_y -= 4.2

        if accent_badge:
            badge_box = patches.FancyBboxPatch(
                (x + 2, y + 1.5), w - 4, 3,
                boxstyle="round,pad=0.2,rounding_size=0.5",
                fc='#1E293B', ec=border_color, lw=1
            )
            ax.add_patch(badge_box)
            ax.text(x + w/2, y + 3, accent_badge, fontsize=6.8, fontweight='bold', color=C_TEXT_ACCENT, ha='center', va='center')

    # Helper function to draw connector arrows
    def draw_arrow(x1, y1, x2, y2, label=None, color='#3B82F6'):
        ax.annotate(
            "", xy=(x2, y2), xytext=(x1, y1),
            arrowprops=dict(arrowstyle="->,head_width=0.4,head_length=0.6",
                            color=color, lw=2.5, ls='-', connectionstyle="arc3,rad=0")
        )
        if label:
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2 + 1.5
            ax.text(mid_x, mid_y, label, fontsize=7, fontweight='bold', color='#93C5FD', ha='center', va='center',
                    bbox=dict(boxstyle="round,pad=0.2", fc='#0B0F19', ec='#1E3A8A', lw=0.8))

    # STAGE 1: DOCUMENT INGESTION & OCR
    draw_card(
        x=2, y=48, w=14, h=36,
        title="1. Multi-Modal Ingestion",
        stage_num="01", icon_text="PDF / OCR",
        items=[
            "• Digital PDF Stream Decoding",
            "  (PyMuPDF / pdfplumber)",
            "• Scanned Raster Detection",
            "• Adaptive Image Pre-Filter",
            "  - 1.8x Contrast Filter",
            "  - Spatial High-Pass Sharpen",
            "• Tesseract LSTM Neural OCR",
            "• Multi-page Text Extraction"
        ],
        border_color=C_BLUE,
        accent_badge="Latency: 25ms (Direct) / 380ms (OCR)"
    )

    # STAGE 2: TABLE-AWARE ENTITY PARSER
    draw_card(
        x=18.5, y=48, w=14, h=36,
        title="2. Entity Extraction",
        stage_num="02", icon_text="NLP Parser",
        items=[
            "• Table-Aware KV Tokenizer",
            "  (Tabs, Colons, Multi-spaces)",
            "• 11 Canonical Master Fields:",
            "  - Legal Name, GSTIN, PAN",
            "  - Address, Contact Person",
            "  - Phone, Email, Category",
            "  - Bank Name, A/C, IFSC",
            "• Layout Heuristics & NLP",
            "• 98.4% - 100% Digital Yield"
        ],
        border_color=C_CYAN,
        accent_badge="Accuracy: 98.4% - 100%"
    )

    # STAGE 3: STATUTORY REGULATORY VALIDATION
    draw_card(
        x=35, y=48, w=14, h=36,
        title="3. Statutory Validation",
        stage_num="03", icon_text="Compliance",
        items=[
            "• 15-char GSTIN Checksum",
            "  (37 State/UT Codes, 'Z' check)",
            "• PAN 4th-Char Entity Type",
            "  (C=Co, P=Ind, F=Firm, D=Demo)",
            "• Cross-Consistency Check",
            "  (GSTIN[2:12] == PAN)",
            "• RBI 11-char IFSC Code",
            "• RFC Email & 10-Digit Phone",
            "• 0 - 100% Validation Score"
        ],
        border_color=C_EMERALD,
        accent_badge="Accuracy: 100% Deterministic"
    )

    # STAGE 4: DUAL-LAYER DEDUPLICATION (EXACT + SBERT/FAISS)
    draw_card(
        x=51.5, y=48, w=15.5, h=36,
        title="4. Dual Deduplication",
        stage_num="04", icon_text="SBERT + FAISS",
        items=[
            "• Layer 1: Deterministic SQL",
            "  (Indexed GSTIN / PAN / Email)",
            "• Layer 2: Semantic Similarity",
            "  - SBERT all-MiniLM-L6-v2",
            "  - 384-D Dense Vectors (R^384)",
            "  - FAISS IndexFlatIP Cosine",
            "• Sister-Concern Detection",
            "• Flags Overlaps >= 85%",
            "• 94.8% Precision / 92.3% Recall"
        ],
        border_color=C_PURPLE,
        accent_badge="Speed: < 2ms / 384-D Cosine"
    )

    # STAGE 5: EXPLAINABLE AI RISK SCORING ENGINE
    draw_card(
        x=69.5, y=48, w=14, h=36,
        title="5. Explainable Risk AI",
        stage_num="05", icon_text="XAI Scoring",
        items=[
            "• Transparent Penalty Matrix",
            "  - GSTIN/PAN Missing: +25/+20",
            "  - Identifier Mismatch: +25",
            "  - Banking Risk: +25",
            "  - Exact Duplicate: +40",
            "  - Semantic Peer (>=85%): +15",
            "• Positive Compliance Findings",
            "• Flagged Risk Exceptions",
            "• Risk Score: 0 - 100 Scale"
        ],
        border_color=C_AMBER,
        accent_badge="Tiers: LOW / MEDIUM / HIGH"
    )

    # STAGE 6: DECISION SUPPORT & MULTI-CHANNEL OUTPUT
    draw_card(
        x=85.5, y=48, w=13, h=36,
        title="6. Decision & Output",
        stage_num="06", icon_text="Dossiers",
        items=[
            "• Procurement Decisions:",
            "  - APPROVE (0 - 25 Score)",
            "  - REVIEW (26 - 50 Score)",
            "  - REJECT (> 50 Score)",
            "• Official PDF Dossier (ReportLab)",
            "• Standalone HTML Dossier",
            "• FastAPI REST Endpoints",
            "• Modern SPA Dashboard"
        ],
        border_color=C_ROSE,
        accent_badge="Dossier Latency: 65ms"
    )

    # Inter-Stage Connecting Arrows (Top Row)
    draw_arrow(16, 66, 18.5, 66, "Raw Text")
    draw_arrow(32.5, 66, 35, 66, "11 Fields")
    draw_arrow(49, 66, 51.5, 66, "Valid Score")
    draw_arrow(67, 66, 69.5, 66, "Vectors")
    draw_arrow(83.5, 66, 85.5, 66, "Risk Score")

    # BOTTOM LAYER: MASTER REPOSITORY & AUDIT TRAIL INFRASTRUCTURE
    bottom_box = patches.FancyBboxPatch(
        (2, 6), 96.5, 36,
        boxstyle="round,pad=0.8,rounding_size=1.2",
        fc='#0F172A', ec='#334155', lw=1.5
    )
    ax.add_patch(bottom_box)

    ax.text(50, 39, "Enterprise Master Data Infrastructure, Vector Index & Immutable Audit Logs (100% Local & Offline)",
            fontsize=12, fontweight='bold', color=C_TEXT_WHITE, ha='center', va='center')

    # Sub-box 1: Relational SQLite DB
    db_box = patches.FancyBboxPatch(
        (4, 9), 28, 26,
        boxstyle="round,pad=0.5,rounding_size=0.8",
        fc='#1E293B', ec='#3B82F6', lw=1.2
    )
    ax.add_patch(db_box)
    ax.text(18, 31.5, "Master SQLite Database (vendors.db)", fontsize=9.5, fontweight='bold', color='#60A5FA', ha='center', va='center')
    ax.plot([6, 30], [29.5, 29.5], color='#475569', lw=0.8)
    db_text = (
        "• 'vendors' Table (21 Master Fields, Unique GSTIN)\n"
        "• 'documents' Table (File Path, MD5, OCR Type)\n"
        "• 'assessments' Table (Historical Risk JSON)\n"
        "• 'audit_logs' Table (Immutable Append-Only Trail)\n"
        "• Schema Auto-Migration & Master CSV Export"
    )
    ax.text(6, 27.5, db_text, fontsize=7.2, color='#CBD5E1', va='top')

    # Sub-box 2: Vector Index & Embeddings
    vec_box = patches.FancyBboxPatch(
        (35.5, 9), 29, 26,
        boxstyle="round,pad=0.5,rounding_size=0.8",
        fc='#1E293B', ec='#A855F7', lw=1.2
    )
    ax.add_patch(vec_box)
    ax.text(50, 31.5, "Dense Vector Store & SBERT Engine", fontsize=9.5, fontweight='bold', color='#C084FC', ha='center', va='center')
    ax.plot([37.5, 62.5], [29.5, 29.5], color='#475569', lw=0.8)
    vec_text = (
        "• SBERT all-MiniLM-L6-v2 Encoder (384 Dimensions)\n"
        "• FAISS IndexFlatIP (Cosine Inner-Product Metric)\n"
        "• Serialized Index (vendor_index.faiss)\n"
        "• Metadata Dictionary (vendor_metadata.pkl)\n"
        "• Real-Time Incremental Index Rebuilding (< 2ms)"
    )
    ax.text(37.5, 27.5, vec_text, fontsize=7.2, color='#CBD5E1', va='top')

    # Sub-box 3: Full-Stack Presentation & Integration
    api_box = patches.FancyBboxPatch(
        (68, 9), 28.5, 26,
        boxstyle="round,pad=0.5,rounding_size=0.8",
        fc='#1E293B', ec='#10B981', lw=1.2
    )
    ax.add_patch(api_box)
    ax.text(82.25, 31.5, "FastAPI Backend & Web Dashboard", fontsize=9.5, fontweight='bold', color='#34D399', ha='center', va='center')
    ax.plot([70, 94.5], [29.5, 29.5], color='#475569', lw=0.8)
    api_text = (
        "• FastAPI REST Endpoints & CORS Middleware\n"
        "• Interactive Swagger OpenAPI 3.0 at /docs\n"
        "• Modern Web SPA (Tailwind CSS, Chart.js, Lucide)\n"
        "• Live Cosine Threshold Slider & Search Meters\n"
        "• Alternative Streamlit Interface (app.py)"
    )
    ax.text(70, 27.5, api_text, fontsize=7.2, color='#CBD5E1', va='top')

    # Connecting vertical arrows from Top Pipeline to Bottom DB/Vector Layer
    ax.annotate("", xy=(18, 36), xytext=(25.5, 48),
                arrowprops=dict(arrowstyle="->,head_width=0.3,head_length=0.5", color='#3B82F6', lw=1.5, ls='--'))
    ax.annotate("", xy=(50, 36), xytext=(59.25, 48),
                arrowprops=dict(arrowstyle="->,head_width=0.3,head_length=0.5", color='#A855F7', lw=1.5, ls='--'))
    ax.annotate("", xy=(82, 36), xytext=(92, 48),
                arrowprops=dict(arrowstyle="->,head_width=0.3,head_length=0.5", color='#10B981', lw=1.5, ls='--'))

    # Footer Metadata
    ax.text(50, 2, "GenVendorAI Architecture • Final-Year B.Tech Capstone Project (Group 104) • PCCOE Pune • Academic Year 2026-2027",
            fontsize=8, color='#64748B', ha='center', va='center')

    plt.tight_layout()
    plt.savefig(OUTPUT_PNG, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"Generated High-Resolution Workflow Block Diagram PNG at: {OUTPUT_PNG}")
    return OUTPUT_PNG


if __name__ == "__main__":
    create_diagram()
