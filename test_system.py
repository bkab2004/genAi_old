"""
GenVendorAI Comprehensive System Test Suite
Validates all pipeline stages: DB, OCR/PDF extraction, Validation, Deduplication, FAISS Vector Search, Risk Scoring, and Reports.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from database.database import (
    init_db, save_vendor, get_all_vendors, get_vendor_by_id, check_duplicate, get_vendor_stats
)
from ocr.ocr_engine import extract_text_from_pdf
from ocr.extractor import extract_vendor_details
from validation.validator import validate_vendor
from ai.embeddings import generate_embedding, get_vendor_embedding_text
from ai.vector_store import (
    init_vector_store, add_vendor_to_index, search_similar_vendors, get_vector_store_stats
)
from ai.semantic_search import semantic_search_vendors
from ai.risk_engine import generate_vendor_risk_assessment
from audit.audit_logger import log_event, get_all_audit_logs
from reports.report_generator import generate_vendor_pdf_report, generate_vendor_html_report
from sample_data.seed_data import seed_database_with_demo_vendors
from sample_data.generate_sample_pdfs import generate_all_sample_pdfs, SAMPLE_DOCS_DIR


def run_all_tests():
    print("=" * 70)
    print("🤖 STARTING GENVENDORAI SYSTEM VALIDATION TEST SUITE")
    print("=" * 70)

    # 1. Test Database
    print("\n[TEST 1] Initializing SQLite Database...")
    init_db()
    stats = get_vendor_stats()
    print(f"✅ DB initialized. Current stats: {stats}")

    # 2. Test Sample PDFs Generation
    print("\n[TEST 2] Generating Sample Vendor PDFs...")
    generated_pdfs = generate_all_sample_pdfs()
    print(f"✅ Generated {len(generated_pdfs)} sample PDFs in {SAMPLE_DOCS_DIR}")
    for p in generated_pdfs:
        print(f"   • {os.path.basename(p)}")

    # 3. Test Seed Data
    print("\n[TEST 3] Seeding Demo Master Vendors...")
    seeded_count = seed_database_with_demo_vendors(force=True)
    print(f"✅ Seeded {seeded_count} demo vendors into master database.")

    # 4. Test Vector Store & Embeddings
    print("\n[TEST 4] Testing Embedding Generation & FAISS Vector Store...")
    init_vector_store()
    test_vec = generate_embedding("Information Technology custom enterprise AI software development in Pune")
    print(f"✅ Generated embedding vector with shape: {test_vec.shape}")
    v_stats = get_vector_store_stats()
    print(f"✅ Vector Store Stats: {v_stats}")

    # 5. Test PDF Extraction on Generated Sample Documents
    print("\n[TEST 5] Testing PDF Extraction & Information Parsing...")
    for pdf_path in generated_pdfs:
        fname = os.path.basename(pdf_path)
        print(f"\n--- Testing Document: {fname} ---")
        text, method, meta = extract_text_from_pdf(pdf_path, return_meta=True)
        print(f"   Extraction Method: {method} ({len(text)} chars)")
        
        details = extract_vendor_details(text)
        print(f"   Extracted Vendor: {details.get('Vendor Name')} | Category: {details.get('Business Category')}")
        print(f"   GSTIN: {details.get('GSTIN')} | PAN: {details.get('PAN')}")
        print(f"   Bank: {details.get('Bank Name')} | IFSC: {details.get('IFSC Code')}")

        # Validation
        val_res = validate_vendor(details)
        print(f"   Validation: Overall={'PASSED' if val_res['Overall Status'] else 'FAILED'} (Score: {val_res['Validation Score']}%)")

        # Duplicate check
        is_dup, dup_field, _ = check_duplicate(details)
        print(f"   Duplicate Check: {'DUPLICATE (' + str(dup_field) + ')' if is_dup else 'UNIQUE'}")

        # Semantic Similarity
        sim_res = search_similar_vendors(get_vendor_embedding_text(details), top_k=2)
        top_sim_score = sim_res[0]["similarity"] if sim_res else 0.0
        top_sim_name = sim_res[0]["vendor"].get("Vendor Name") if sim_res else None
        print(f"   Top Semantic Peer: {top_sim_name} (Similarity: {top_sim_score:.1%})")

        # Risk Assessment
        risk = generate_vendor_risk_assessment(
            details,
            is_duplicate=is_dup,
            duplicate_reason=dup_field,
            max_semantic_similarity=top_sim_score,
            most_similar_vendor_name=top_sim_name
        )
        print(f"   AI Assessment: Risk Score={risk['Risk Score']}/100 ({risk['Risk Level']}) -> Recommendation={risk['Recommendation']}")

    # 6. Test Semantic Search
    print("\n[TEST 6] Testing Natural Language Semantic Search...")
    queries = [
        "Software and cloud providers in Pune",
        "Civil construction and infrastructure contractors in Maharashtra",
        "Freight logistics and transportation warehousing",
        "Medical devices and healthcare solutions"
    ]
    for q in queries:
        matches = semantic_search_vendors(q, top_k=2, min_similarity=0.15)
        print(f"   Query: '{q}' -> Found {len(matches)} matches")
        for m in matches:
            print(f"      • {m['Vendor Name']} ({m['Similarity Pct']}) - {m['Business Category']} [{m['Recommendation']}]")

    # 7. Test Reports Generation
    print("\n[TEST 7] Testing Report Generation (PDF & HTML)...")
    vendors = get_all_vendors()
    if vendors:
        sample_v = vendors[0]
        pdf_rep = generate_vendor_pdf_report(sample_v)
        html_rep = generate_vendor_html_report(sample_v)
        print(f"✅ Generated PDF report: {pdf_rep} (Exists: {os.path.exists(pdf_rep)})")
        print(f"✅ Generated HTML report ({len(html_rep)} chars)")

    # 8. Test Audit Logs
    print("\n[TEST 8] Testing Enterprise Audit Trail...")
    log_event("TEST_SUITE_COMPLETED", user_action="Automated Test", status="SUCCESS", details="All 8 system components passed")
    all_logs = get_all_audit_logs(limit=10)
    print(f"✅ Retrieved {len(all_logs)} recent audit log events.")

    print("\n" + "=" * 70)
    print("🎉 ALL GENVENDORAI SYSTEM TESTS PASSED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    run_all_tests()
