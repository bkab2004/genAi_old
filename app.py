"""
GenVendorAI – AI-Powered Vendor Intelligence and Risk Assessment System
=======================================================================
Final-Year B.Tech Capstone Project in Computer Science and Engineering (AI & ML)
Pimpri Chinchwad College of Engineering (PCCOE), Pune | Project Group ID: 104

Main Streamlit Application Entry Point
"""

import os
import sys
import json
import shutil
import pandas as pd
import streamlit as st
from datetime import datetime

# ============================================================
# PROJECT ROOT PATH CONFIGURATION
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Package-style imports
from database.database import (
    init_db, save_vendor, get_all_vendors, get_all_vendors_df,
    get_vendor_by_id, get_vendor_by_gstin, check_duplicate,
    update_vendor_assessment, save_document_record, save_assessment_record,
    get_latest_assessment, export_vendors_to_csv, delete_vendor, get_vendor_stats
)
from ocr.ocr_engine import extract_text_from_pdf
from ocr.extractor import extract_vendor_details
from validation.validator import validate_vendor
from ai.embeddings import get_vendor_embedding_text
from ai.vector_store import (
    init_vector_store, add_vendor_to_index, search_similar_vendors,
    rebuild_vector_index, get_vector_store_stats
)
from ai.semantic_search import semantic_search_vendors
from ai.risk_engine import generate_vendor_risk_assessment
from dashboard.dashboard import show_dashboard
from audit.audit_logger import log_event, get_all_audit_logs, get_audit_logs_df, clear_audit_logs
from reports.report_generator import generate_vendor_pdf_report, generate_vendor_html_report
from sample_data.seed_data import seed_database_with_demo_vendors
from sample_data.generate_sample_pdfs import generate_all_sample_pdfs, SAMPLE_DOCS_DIR

# ============================================================
# PAGE CONFIGURATION & CUSTOM STYLES
# ============================================================
st.set_page_config(
    page_title="GenVendorAI | Vendor Intelligence & Risk System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Enterprise CSS
st.markdown("""
<style>
    /* Metric Cards */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 700;
    }
    
    /* Workflow step badges */
    .step-badge {
        display: inline-block;
        padding: 4px 10px;
        background-color: #3b82f6;
        color: white;
        border-radius: 6px;
        font-size: 12px;
        font-weight: bold;
        margin-bottom: 8px;
    }
    
    .status-badge-approved {
        background-color: #d1fae5;
        color: #065f46;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 13px;
    }
    
    .status-badge-review {
        background-color: #fef3c7;
        color: #92400e;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 13px;
    }
    
    .status-badge-reject {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 13px;
    }
    
    /* Section containers */
    .card-container {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# INITIALIZE SYSTEM STATE
# ============================================================
@st.cache_resource
def bootstrap_system():
    """Initializes DB schema, vector store, and sample test PDFs on first boot."""
    init_db()
    init_vector_store()
    seed_database_with_demo_vendors()
    generate_all_sample_pdfs()
    return True

bootstrap_system()


# ============================================================
# SIDEBAR NAVIGATION & SYSTEM INFO
# ============================================================
st.sidebar.markdown("# 🤖 **GenVendorAI**")
st.sidebar.markdown("**AI-Powered Vendor MDM & Risk Platform**")
st.sidebar.caption("Final-Year B.Tech Capstone Project • PCCOE Pune")
st.sidebar.divider()

page = st.sidebar.radio(
    "Navigation Menu",
    [
        "📄 Vendor Processing",
        "📊 Dashboard",
        "🔎 Semantic Search",
        "📋 Vendor Database",
        "⚠️ Risk & Compliance",
        "📝 Audit Logs",
        "📑 Reports"
    ]
)

st.sidebar.divider()

# Quick System Stats in Sidebar
stats = get_vendor_stats()
st.sidebar.markdown("### 📊 System Status")
st.sidebar.write(f"• **Active Vendors:** {stats['total_vendors']}")
st.sidebar.write(f"• **Approved:** 🟢 {stats['approved']}")
st.sidebar.write(f"• **Under Review:** 🟡 {stats['under_review']}")
st.sidebar.write(f"• **Rejected:** 🔴 {stats['rejected']}")

vec_stats = get_vector_store_stats()
st.sidebar.caption(f"Vector Engine: `{vec_stats['engine']}` ({vec_stats['indexed_vendors']} indexed)")

st.sidebar.divider()
if st.sidebar.button("🔄 Reset / Seed Demo Data", help="Re-initializes demo dataset with 6 diverse vendors"):
    seed_database_with_demo_vendors(force=True)
    st.sidebar.success("Database re-seeded successfully!")
    st.rerun()


# ============================================================
# PAGE 1: VENDOR PROCESSING (7-STEP WORKFLOW)
# ============================================================
if page == "📄 Vendor Processing":
    st.title("📄 AI-Powered Vendor Onboarding & Risk Processing")
    st.markdown(
        "Upload vendor documents (Registration certificates, GST filings, PAN cards, Bank verification letters, Quotations) "
        "to trigger end-to-end extraction, statutory validation, semantic deduplication, and explainable AI risk scoring."
    )
    st.divider()

    # Document Selection Mode
    upload_tab, sample_tab = st.tabs(["📤 Upload PDF Document", "📁 Choose Pre-loaded Sample PDF"])

    uploaded_pdf_path = None
    source_filename = None

    with upload_tab:
        uploaded_file = st.file_uploader(
            "Upload Vendor Document (PDF format)",
            type=["pdf"],
            help="Select a digital or scanned vendor PDF"
        )
        if uploaded_file is not None:
            upload_dir = os.path.join(BASE_DIR, "documents", "uploads")
            os.makedirs(upload_dir, exist_ok=True)
            saved_path = os.path.join(upload_dir, uploaded_file.name)
            with open(saved_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            uploaded_pdf_path = saved_path
            source_filename = uploaded_file.name
            st.success(f"✅ Uploaded: **{uploaded_file.name}** ({len(uploaded_file.getbuffer()) / 1024:.1f} KB)")

    with sample_tab:
        st.markdown("Select from pre-generated sample vendor documents across different test scenarios:")
        sample_files = [f for f in os.listdir(SAMPLE_DOCS_DIR) if f.endswith(".pdf")] if os.path.exists(SAMPLE_DOCS_DIR) else []
        if sample_files:
            selected_sample = st.selectbox("Select Sample Document", sample_files)
            if st.button("Load Selected Sample"):
                uploaded_pdf_path = os.path.join(SAMPLE_DOCS_DIR, selected_sample)
                source_filename = selected_sample
                st.session_state["active_sample_path"] = uploaded_pdf_path
                st.session_state["active_sample_name"] = source_filename

        if "active_sample_path" in st.session_state and not uploaded_pdf_path:
            uploaded_pdf_path = st.session_state["active_sample_path"]
            source_filename = st.session_state["active_sample_name"]
            st.info(f"Loaded Sample: **{source_filename}**")

    st.markdown("---")

    if uploaded_pdf_path:
        st.markdown(f"### ⚙️ Processing Queue: `{source_filename}`")
        
        col_btn1, col_btn2 = st.columns([2, 5])
        with col_btn1:
            run_pipeline = st.button("🚀 Run Full Vendor Intelligence Pipeline", type="primary", use_container_width=True)

        if run_pipeline:
            # Create progress bar & stepper
            progress_bar = st.progress(0)
            status_text = st.empty()

            try:
                # ----------------------------------------------------
                # STEP 1: DOCUMENT INGESTION & OCR
                # ----------------------------------------------------
                status_text.text("Step 1/7: Document Ingestion & Text/OCR Extraction...")
                progress_bar.progress(15)

                extracted_text, method_used, doc_meta = extract_text_from_pdf(uploaded_pdf_path, return_meta=True)
                
                log_event(
                    event_type="DOCUMENT_UPLOADED",
                    vendor_name=source_filename,
                    status="SUCCESS",
                    details={"filename": source_filename, "method": method_used, "char_count": len(extracted_text)}
                )

                st.markdown("#### 📑 Step 1: Document Text & OCR Extraction")
                col_meta1, col_meta2 = st.columns(2)
                with col_meta1:
                    st.success(f"✅ Extraction Method: **{method_used}**")
                with col_meta2:
                    st.info(f"Characters Extracted: **{len(extracted_text):,}** | Pages: **{doc_meta.get('page_count', 1)}**")

                with st.expander("🔍 View Raw Extracted Text / OCR Buffer"):
                    st.text_area("Extracted Text", extracted_text, height=180)

                # ----------------------------------------------------
                # STEP 2: VENDOR INFORMATION EXTRACTION
                # ----------------------------------------------------
                status_text.text("Step 2/7: Structured Vendor Information Extraction...")
                progress_bar.progress(30)

                vendor_details = extract_vendor_details(extracted_text)
                vendor_details["source_document"] = source_filename

                log_event(
                    event_type="VENDOR_EXTRACTED",
                    vendor_name=vendor_details.get("Vendor Name"),
                    status="SUCCESS",
                    details=vendor_details
                )

                st.markdown("#### 📋 Step 2: Extracted Vendor Master Fields")
                c1, c2 = st.columns(2)
                with c1:
                    st.text_input("Vendor Name", vendor_details.get("Vendor Name", "Not available"), disabled=True)
                    st.text_input("GSTIN", vendor_details.get("GSTIN", "Not available"), disabled=True)
                    st.text_input("PAN", vendor_details.get("PAN", "Not available"), disabled=True)
                    st.text_input("Business Category", vendor_details.get("Business Category", "Not available"), disabled=True)
                    st.text_area("Address", vendor_details.get("Address", "Not available"), height=70, disabled=True)
                with c2:
                    st.text_input("Contact Person", vendor_details.get("Contact Person", "Not available"), disabled=True)
                    st.text_input("Phone", vendor_details.get("Phone", "Not available"), disabled=True)
                    st.text_input("Email", vendor_details.get("Email", "Not available"), disabled=True)
                    st.text_input("Bank Name", vendor_details.get("Bank Name", "Not available"), disabled=True)
                    st.text_input("Account Number", vendor_details.get("Account Number", "Not available"), disabled=True)
                    st.text_input("IFSC Code", vendor_details.get("IFSC Code", "Not available"), disabled=True)

                st.markdown("---")

                # ----------------------------------------------------
                # STEP 3: STATUTORY & FORMAT VALIDATION
                # ----------------------------------------------------
                status_text.text("Step 3/7: Regulatory & Format Validation...")
                progress_bar.progress(45)

                validation_results = validate_vendor(vendor_details)
                val_score = validation_results.get("Validation Score", 0.0)
                overall_valid = validation_results.get("Overall Status", False)

                log_event(
                    event_type="VALIDATION_COMPLETED",
                    vendor_name=vendor_details.get("Vendor Name"),
                    status="SUCCESS" if overall_valid else "FAILED",
                    details={"score": val_score, "results": validation_results.get("Details")}
                )

                st.markdown(f"#### ✅ Step 3: Statutory Validation (Score: **{val_score:.0f}%**)")
                vcol1, vcol2 = st.columns([1, 3])
                with vcol1:
                    if overall_valid:
                        st.success("🟢 VALIDATION: PASSED")
                    else:
                        st.error("🔴 VALIDATION: FAILED")
                    st.metric("Field Validation Score", f"{val_score:.0f}%")

                with vcol2:
                    val_details = validation_results.get("Details", {})
                    v_fields = ["GSTIN", "PAN", "Email", "Phone", "IFSC Code", "Account Number", "Vendor Name", "Address"]
                    v_grid = [v_fields[i:i+4] for i in range(0, len(v_fields), 4)]
                    for row in v_grid:
                        cols = st.columns(4)
                        for idx, f in enumerate(row):
                            with cols[idx]:
                                is_ok = validation_results.get(f, False)
                                icon = "✅" if is_ok else "❌"
                                st.write(f"**{icon} {f}**")
                                st.caption(val_details.get(f, ""))

                st.markdown("---")

                # ----------------------------------------------------
                # STEP 4: EXACT DUPLICATE DETECTION
                # ----------------------------------------------------
                status_text.text("Step 4/7: Checking Exact Duplicate Records...")
                progress_bar.progress(60)

                is_dup, dup_field, existing_record = check_duplicate(vendor_details)
                
                log_event(
                    event_type="DUPLICATE_CHECKED",
                    vendor_name=vendor_details.get("Vendor Name"),
                    status="DUPLICATE" if is_dup else "UNIQUE",
                    details={"is_duplicate": is_dup, "duplicate_field": dup_field}
                )

                st.markdown("#### 🔍 Step 4: Exact Duplicate Detection")
                if is_dup:
                    st.error(f"⚠️ **Exact Duplicate Vendor Detected!** Matched on: **{dup_field}**")
                    if existing_record:
                        with st.expander("View Conflicting Existing Master Record"):
                            st.json(existing_record)
                else:
                    st.success("✅ **No Exact Duplicate Found.** Vendor record is unique in database.")

                st.markdown("---")

                # ----------------------------------------------------
                # STEP 5: SEMANTIC DUPLICATE & SIMILARITY SEARCH
                # ----------------------------------------------------
                status_text.text("Step 5/7: AI Semantic Similarity & Vector Search...")
                progress_bar.progress(75)

                query_text = get_vendor_embedding_text(vendor_details)
                similar_vendors = search_similar_vendors(query_text, top_k=3, threshold=0.10)
                
                max_sim = 0.0
                top_similar_name = None
                if similar_vendors:
                    # Filter out exact self if already in vector db
                    for item in similar_vendors:
                        v_name = item["vendor"].get("Vendor Name") or item["vendor"].get("vendor_name", "")
                        sim = item["similarity"]
                        if v_name.lower() != vendor_details.get("Vendor Name", "").lower():
                            if sim > max_sim:
                                max_sim = sim
                                top_similar_name = v_name

                st.markdown(f"#### 🧠 Step 5: Semantic Similarity Analysis (FAISS Embeddings)")
                if similar_vendors:
                    sim_cols = st.columns(len(similar_vendors))
                    for i, sim_item in enumerate(similar_vendors):
                        with sim_cols[i]:
                            s_v = sim_item["vendor"]
                            s_name = s_v.get("Vendor Name") or s_v.get("vendor_name", "Unknown")
                            s_cat = s_v.get("Business Category") or s_v.get("business_category", "General")
                            s_pct = sim_item.get("similarity_pct", "0%")
                            s_tier = sim_item.get("tier", "Low")
                            
                            st.markdown(f"**{i+1}. {s_name}**")
                            st.caption(f"Category: {s_cat}")
                            st.metric("Similarity", s_pct, delta=s_tier)
                else:
                    st.info("No prior vendor records available for semantic comparison.")

                st.markdown("---")

                # ----------------------------------------------------
                # STEP 6: EXPLAINABLE AI RISK ASSESSMENT
                # ----------------------------------------------------
                status_text.text("Step 6/7: Computing Explainable AI Risk Evaluation...")
                progress_bar.progress(90)

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

                # Update vendor details dict with evaluation fields
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

                st.markdown("#### 🤖 Step 6: Explainable AI Risk Assessment")
                kpi1, kpi2, kpi3 = st.columns(3)
                with kpi1:
                    st.metric("🎯 Risk Score", f"{risk_score} / 100")
                with kpi2:
                    if risk_level == "LOW":
                        st.metric("⚠️ Risk Level", "🟢 LOW RISK")
                    elif risk_level == "MEDIUM":
                        st.metric("⚠️ Risk Level", "🟡 MEDIUM RISK")
                    else:
                        st.metric("⚠️ Risk Level", "🔴 HIGH RISK")
                with kpi3:
                    if recommendation == "APPROVE":
                        st.metric("📌 AI Recommendation", "✅ APPROVE")
                    elif recommendation == "REVIEW":
                        st.metric("📌 AI Recommendation", "⚠️ REVIEW")
                    else:
                        st.metric("📌 AI Recommendation", "❌ REJECT")

                st.info(f"**Executive Rationale:** {assessment.get('Summary')}")

                rcol1, rcol2 = st.columns(2)
                with rcol1:
                    st.markdown("##### ✅ Positive Compliance Strengths")
                    for pf in assessment.get("Positive Findings", []):
                        st.write(f"• {pf}")
                with rcol2:
                    st.markdown("##### ⚠️ Flagged Risk Factors")
                    rf_list = assessment.get("Risk Factors", [])
                    if rf_list:
                        for rf in rf_list:
                            st.write(f"• 🔴 {rf}")
                    else:
                        st.write("• No significant risk factors identified.")

                st.markdown("---")

                # ----------------------------------------------------
                # STEP 7: FINAL ONBOARDING DECISION & PERSISTENCE
                # ----------------------------------------------------
                status_text.text("Step 7/7: Master Record Persistence & Audit Log...")
                progress_bar.progress(100)

                st.markdown("#### 🎯 Step 7: Final Onboarding Decision")
                
                vendor_id = None
                if not is_dup:
                    # Save to SQLite DB
                    vendor_id = save_vendor(vendor_details)
                    save_document_record(
                        vendor_id=vendor_id,
                        filename=source_filename,
                        file_path=uploaded_pdf_path,
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
                    # Add to FAISS Vector Store
                    add_vendor_to_index(vendor_details)
                    
                    log_event(
                        event_type="VENDOR_CREATED",
                        vendor_id=vendor_id,
                        vendor_name=vendor_details.get("Vendor Name"),
                        status="SUCCESS",
                        details={"recommendation": recommendation, "risk_score": risk_score}
                    )
                    
                    if recommendation == "APPROVE":
                        st.success(f"🎉 **Vendor Approved & Activated in Master Database!** (Assigned ID: #{vendor_id})")
                    elif recommendation == "REVIEW":
                        st.warning(f"⚠️ **Vendor Enrolled for Secondary Compliance Review.** (Assigned ID: #{vendor_id})")
                    else:
                        st.error(f"🔴 **Vendor Master Record Flagged as Rejected.** (Assigned ID: #{vendor_id})")
                else:
                    st.error("🚫 **Action Blocked**: Duplicate vendor entry prevented. Record was NOT added to master database.")

                # Report Download Options
                st.markdown("---")
                st.markdown("#### 📑 Compliance & Audit Report Download")
                rep_c1, rep_c2 = st.columns(2)
                
                # Generate PDF
                pdf_report_path = generate_vendor_pdf_report(vendor_details, assessment)
                if os.path.exists(pdf_report_path):
                    with open(pdf_report_path, "rb") as pf:
                        with rep_c1:
                            st.download_button(
                                label="📥 Download Official Assessment Report (PDF)",
                                data=pf.read(),
                                file_name=os.path.basename(pdf_report_path),
                                mime="application/pdf",
                                type="primary"
                            )

                html_report_str = generate_vendor_html_report(vendor_details, assessment)
                with rep_c2:
                    st.download_button(
                        label="🌐 Download Web Compliance Report (HTML)",
                        data=html_report_str.encode("utf-8"),
                        file_name=f"Compliance_Report_{vendor_details.get('Vendor Name', 'Vendor').replace(' ', '_')}.html",
                        mime="text/html"
                    )

                status_text.text("✅ Full vendor intelligence pipeline completed successfully!")

            except Exception as e:
                st.error(f"❌ An error occurred during document processing: {e}")
                with st.expander("Detailed Error Traceback"):
                    st.exception(e)


# ============================================================
# PAGE 2: DASHBOARD
# ============================================================
elif page == "📊 Dashboard":
    show_dashboard()


# ============================================================
# PAGE 3: SEMANTIC SEARCH
# ============================================================
elif page == "🔎 Semantic Search":
    st.title("🔎 Natural-Language Semantic Vendor Search")
    st.markdown(
        "Query your vendor master knowledge base using natural language queries. "
        "The system retrieves semantically relevant suppliers based on dense vector representations (`all-MiniLM-L6-v2` + FAISS)."
    )
    st.divider()

    # Search Box & Filters
    col_q, col_cat = st.columns([3, 1])
    with col_q:
        search_query = st.text_input(
            "Natural Language Query",
            placeholder="e.g. 'IT software companies in Pune', 'construction contractors with valid GST', 'logistics fleet'"
        )
    with col_cat:
        cat_filter = st.selectbox(
            "Filter Category",
            ["All", "Information Technology", "Construction & Infrastructure", "Manufacturing & Industrial", "Logistics & Supply Chain", "Healthcare & Pharmaceuticals", "Consulting & Professional Services"]
        )

    col_s1, col_s2 = st.columns([1, 3])
    with col_s1:
        min_sim = st.slider("Minimum Similarity Threshold (%)", min_value=10, max_value=90, value=25, step=5) / 100.0

    if search_query:
        with st.spinner("🧠 Searching vector knowledge base..."):
            results = semantic_search_vendors(
                query=search_query,
                top_k=10,
                min_similarity=min_sim,
                category_filter=cat_filter if cat_filter != "All" else None
            )

        if results:
            st.success(f"Found **{len(results)}** semantically relevant vendor profiles.")
            for i, res in enumerate(results):
                with st.container():
                    st.markdown(f"### {i+1}. {res['Vendor Name']}")
                    c1, c2, c3, c4 = st.columns(4)
                    with c1:
                        st.caption("Business Category")
                        st.write(f"🏢 **{res['Business Category']}**")
                    with c2:
                        st.caption("Semantic Match Score")
                        st.write(f"🧠 **{res['Similarity Pct']}** ({res['Similarity Tier']})")
                    with c3:
                        st.caption("Risk Score")
                        r_col = "🟢" if res['Risk Level'] == "LOW" else ("🟡" if res['Risk Level'] == "MEDIUM" else "🔴")
                        st.write(f"{r_col} **{res['Risk Score']}/100 ({res['Risk Level']})**")
                    with c4:
                        st.caption("Onboarding Decision")
                        st.write(f"📌 **{res['Recommendation']}**")

                    st.write(f"📍 **Address:** {res['Address']}")
                    st.write(f"🧾 **GSTIN:** `{res['GSTIN']}` | **PAN:** `{res['PAN']}` | 📞 **Phone:** {res['Phone']} | ✉️ **Email:** {res['Email']}")
                    st.markdown("---")
        else:
            st.info("No matching vendors found meeting the similarity criteria. Try expanding your search terms or lowering the similarity threshold.")


# ============================================================
# PAGE 4: VENDOR DATABASE (CRUD & MASTER TABLE)
# ============================================================
elif page == "📋 Vendor Database":
    st.title("📋 Vendor Master Database")
    st.caption("Centralized enterprise repository of all onboarded suppliers, tax identifiers, and risk status.")

    df = get_all_vendors_df()

    if df.empty:
        st.info("The vendor database is currently empty. Please upload documents or seed demo vendors.")
        if st.button("🌱 Load Demo Vendors", type="primary"):
            seed_database_with_demo_vendors(force=True)
            st.rerun()
    else:
        # Search & Filter Controls
        f_col1, f_col2, f_col3, f_col4 = st.columns(4)
        with f_col1:
            search_name = st.text_input("Search by Name / GSTIN", "")
        with f_col2:
            filter_cat = st.selectbox("Category", ["All"] + sorted(list(df["business_category"].dropna().unique())))
        with f_col3:
            filter_risk = st.selectbox("Risk Level", ["All", "LOW", "MEDIUM", "HIGH"])
        with f_col4:
            filter_rec = st.selectbox("Recommendation", ["All", "APPROVE", "REVIEW", "REJECT"])

        # Filter DataFrame
        filtered_df = df.copy()
        if search_name:
            filtered_df = filtered_df[
                filtered_df["vendor_name"].str.contains(search_name, case=False, na=False) |
                filtered_df["gstin"].str.contains(search_name, case=False, na=False)
            ]
        if filter_cat != "All":
            filtered_df = filtered_df[filtered_df["business_category"] == filter_cat]
        if filter_risk != "All":
            filtered_df = filtered_df[filtered_df["risk_level"] == filter_risk]
        if filter_rec != "All":
            filtered_df = filtered_df[filtered_df["recommendation"] == filter_rec]

        st.markdown(f"**Showing {len(filtered_df)} of {len(df)} total vendors**")

        # Display table
        show_cols = [
            "id", "vendor_name", "business_category", "gstin", "pan",
            "risk_score", "risk_level", "recommendation", "validation_status", "created_at"
        ]
        st.dataframe(
            filtered_df[show_cols].rename(columns={
                "id": "ID",
                "vendor_name": "Vendor Name",
                "business_category": "Category",
                "gstin": "GSTIN",
                "pan": "PAN",
                "risk_score": "Risk",
                "risk_level": "Level",
                "recommendation": "Decision",
                "validation_status": "Validation",
                "created_at": "Onboarded Date"
            }),
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")
        
        # Vendor Details Modal / Viewer
        st.markdown("### 🔍 Inspect Individual Vendor Profile")
        v_ids = filtered_df["id"].tolist()
        if v_ids:
            selected_v_id = st.selectbox("Select Vendor ID to inspect", v_ids)
            selected_vendor = get_vendor_by_id(selected_v_id)
            if selected_vendor:
                with st.expander(f"Detailed Profile: {selected_vendor['vendor_name']} (#{selected_vendor['id']})", expanded=True):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.write(f"• **Vendor Name:** {selected_vendor['vendor_name']}")
                        st.write(f"• **GSTIN:** `{selected_vendor['gstin']}`")
                        st.write(f"• **PAN:** `{selected_vendor['pan']}`")
                        st.write(f"• **Address:** {selected_vendor['address']}")
                        st.write(f"• **Category:** {selected_vendor['business_category']}")
                    with c2:
                        st.write(f"• **Contact Person:** {selected_vendor['contact_person']}")
                        st.write(f"• **Phone:** {selected_vendor['phone']}")
                        st.write(f"• **Email:** {selected_vendor['email']}")
                        st.write(f"• **Bank:** {selected_vendor['bank_name']} | A/C: `{selected_vendor['account_number']}` | IFSC: `{selected_vendor['ifsc_code']}`")
                        st.write(f"• **Source File:** {selected_vendor['source_document']}")

                    st.markdown("---")
                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        # Report generation
                        assessment_rec = get_latest_assessment(selected_v_id)
                        pdf_path = generate_vendor_pdf_report(selected_vendor, assessment_rec)
                        if os.path.exists(pdf_path):
                            with open(pdf_path, "rb") as pf:
                                st.download_button(
                                    label="📥 Download Assessment PDF",
                                    data=pf.read(),
                                    file_name=os.path.basename(pdf_path),
                                    mime="application/pdf",
                                    key=f"dl_pdf_{selected_v_id}"
                                )
                    with btn_col2:
                        if st.button("🗑️ Delete Vendor Record", key=f"del_{selected_v_id}"):
                            delete_vendor(selected_v_id)
                            log_event(
                                event_type="VENDOR_DELETED",
                                vendor_id=selected_v_id,
                                vendor_name=selected_vendor['vendor_name'],
                                status="SUCCESS",
                                details="Vendor record manually removed"
                            )
                            st.success("Vendor deleted successfully!")
                            st.rerun()

        # CSV Export
        st.markdown("---")
        csv_bytes = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Entire Vendor Master (CSV)",
            data=csv_bytes,
            file_name="GenVendorAI_Vendor_Database.csv",
            mime="text/csv",
            type="primary"
        )


# ============================================================
# PAGE 5: RISK & COMPLIANCE
# ============================================================
elif page == "⚠️ Risk & Compliance":
    st.title("⚠️ Risk & Compliance Intelligence Center")
    st.caption("Deep-dive into regulatory compliance, GST/PAN consistency audits, and risk tier analytics.")

    df = get_all_vendors_df()

    if df.empty:
        st.info("No vendor data available. Please load demo data or process documents.")
    else:
        # High Risk Section
        high_risk_df = df[df["risk_level"] == "HIGH"]
        med_risk_df = df[df["risk_level"] == "MEDIUM"]
        low_risk_df = df[df["risk_level"] == "LOW"]

        tab_matrix, tab_tax, tab_rules = st.tabs(["📊 Compliance Matrix", "🧾 GST / PAN Integrity", "📐 Scoring Rubric"])

        with tab_matrix:
            st.markdown("### Risk Tier Summary")
            k1, k2, k3 = st.columns(3)
            with k1:
                st.metric("🟢 Low Risk Tier (0-30)", len(low_risk_df), "Safe to Onboard")
            with k2:
                st.metric("🟡 Medium Risk Tier (31-65)", len(med_risk_df), "Requires Officer Review")
            with k3:
                st.metric("🔴 High Risk Tier (66-100)", len(high_risk_df), "Prohibited / Flagged")

            st.markdown("---")
            st.markdown("#### High Risk & Flagged Vendors Watchlist")
            if not high_risk_df.empty:
                st.dataframe(
                    high_risk_df[["id", "vendor_name", "business_category", "gstin", "risk_score", "recommendation", "duplicate_status"]],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.success("✅ No vendors currently in the High Risk tier.")

        with tab_tax:
            st.markdown("### 🧾 Tax Identifier State Distribution")
            df["state_code"] = df["gstin"].str[:2]
            state_counts = df["state_code"].value_counts().reset_index()
            state_counts.columns = ["State Code", "Vendor Count"]
            st.dataframe(state_counts, use_container_width=True, hide_index=True)

        with tab_rules:
            st.markdown("""
            ### 📐 Transparent AI Risk Scoring Model
            The GenVendorAI Risk Engine calculates an explainable risk score (0 to 100) based on weighted regulatory criteria:

            | Regulatory Dimension | Risk Impact | Rationale |
            |---|---|---|
            | **Invalid / Missing GSTIN** | +25 pts | Statutory requirement for input tax credit claims under Indian GST laws. |
            | **Invalid / Missing PAN** | +20 pts | Required for corporate TDS deduction and legal entity recognition. |
            | **GSTIN vs PAN Mismatch** | +25 pts | Potential fraud or shell entity using borrowed GSTIN registration. |
            | **Missing Banking Details (IFSC/Acc)** | +25 pts | Prevents payment failures and non-traceable disbursement risks. |
            | **Exact Duplicate Record** | +40 pts | Protects master data against duplicate invoice payment liabilities. |
            | **High Semantic Similarity (≥85%)** | +15 pts | Flags potential corporate splitting or unregistered sister concerns. |
            | **Invalid Contact (Email/Phone)** | +10 pts | Prevents unverified or dormant supplier registrations. |

            **Thresholds:**
            - **0 – 30**: Low Risk (`APPROVE`)
            - **31 – 65**: Medium Risk (`REVIEW`)
            - **66 – 100**: High Risk (`REJECT`)
            """)


# ============================================================
# PAGE 6: AUDIT LOGS
# ============================================================
elif page == "📝 Audit Logs":
    st.title("📝 Enterprise Audit Trail & Event History")
    st.caption("Immutable chronological record of all system events, document extractions, validations, and automated decisions.")

    logs_df = get_audit_logs_df(limit=300)

    if logs_df.empty:
        st.info("No audit logs recorded yet.")
    else:
        # Event type filter
        event_types = ["All"] + sorted(list(logs_df["event_type"].dropna().unique()))
        sel_event = st.selectbox("Filter by Event Type", event_types)

        filtered_logs = logs_df if sel_event == "All" else logs_df[logs_df["event_type"] == sel_event]

        st.markdown(f"**Displaying {len(filtered_logs)} audit records**")

        st.dataframe(
            filtered_logs.rename(columns={
                "id": "Log ID",
                "timestamp": "Timestamp",
                "event_type": "Event Type",
                "vendor_name": "Vendor / Entity",
                "user_action": "Actor / Trigger",
                "status": "Status",
                "details": "Payload Details"
            }),
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")
        c1, c2 = st.columns([2, 8])
        with c1:
            csv_audit = filtered_logs.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export Audit Trail (CSV)",
                data=csv_audit,
                file_name="GenVendorAI_Audit_Logs.csv",
                mime="text/csv"
            )


# ============================================================
# PAGE 7: REPORTS
# ============================================================
elif page == "📑 Reports":
    st.title("📑 Compliance Assessment Report Generator")
    st.caption("Generate, view, and export printable vendor risk assessment dossiers and compliance summaries.")

    vendors = get_all_vendors()

    if not vendors:
        st.info("No vendor records found in database to generate reports.")
    else:
        v_options = {f"{v['vendor_name']} (GSTIN: {v['gstin']})": v['id'] for v in vendors}
        selected_label = st.selectbox("Select Vendor for Assessment Report", list(v_options.keys()))
        selected_id = v_options[selected_label]
        vendor_data = get_vendor_by_id(selected_id)
        assessment_data = get_latest_assessment(selected_id)

        if vendor_data:
            st.markdown("---")
            # Report Preview
            html_rep = generate_vendor_html_report(vendor_data, assessment_data)
            st.components.v1.html(html_rep, height=600, scrolling=True)

            st.markdown("---")
            rc1, rc2 = st.columns(2)
            with rc1:
                pdf_path = generate_vendor_pdf_report(vendor_data, assessment_data)
                if os.path.exists(pdf_path):
                    with open(pdf_path, "rb") as f:
                        st.download_button(
                            label="📥 Download Printable Report (PDF)",
                            data=f.read(),
                            file_name=os.path.basename(pdf_path),
                            mime="application/pdf",
                            type="primary",
                            key="rep_page_pdf"
                        )
            with rc2:
                st.download_button(
                    label="🌐 Download Standalone Web Report (HTML)",
                    data=html_rep.encode("utf-8"),
                    file_name=f"Report_{vendor_data.get('vendor_name', 'Vendor').replace(' ', '_')}.html",
                    mime="text/html",
                    key="rep_page_html"
                )


# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.caption(
    "GenVendorAI © 2026-2027 | Department of Computer Science and Engineering (AI & ML), PCCOE Pune | "
    "Intelligent Vendor Master Data Management & Risk Assessment Platform"
)
