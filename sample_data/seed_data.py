"""
GenVendorAI Seed Data Module
Provides 6 realistic Indian enterprise vendors spanning diverse industries with verified GSTIN, PAN, and Bank data.
"""

from typing import List, Dict, Any
from database.database import (
    init_db, save_vendor, save_assessment_record, get_all_vendors
)
from ai.vector_store import add_vendor_to_index
from audit.audit_logger import log_event

DEMO_VENDORS: List[Dict[str, Any]] = [
    {
        "vendor_name": "Zenith Cloud Technologies Pvt Ltd",
        "gstin": "27AABCZ1234F1Z5",
        "pan": "AABCZ1234F",
        "address": "402 Tech Park, Phase 2, Hinjewadi, Pune, Maharashtra 411057",
        "contact_person": "Rajesh Sharma",
        "phone": "9823012345",
        "email": "contact@zenithcloud.in",
        "business_category": "Information Technology",
        "bank_name": "HDFC Bank",
        "account_number": "50200012345678",
        "ifsc_code": "HDFC0001234",
        "risk_score": 10,
        "risk_level": "LOW",
        "recommendation": "APPROVE",
        "validation_status": "VALID",
        "duplicate_status": "UNIQUE",
        "similarity_score": 0.0,
        "source_document": "Demo Seed - Zenith_Registration.pdf",
        "processing_status": "COMPLETED",
        "positive_findings": [
            "Valid 15-character Maharashtra GSTIN (27AABCZ1234F1Z5)",
            "Valid Company PAN matching GSTIN registration",
            "Verified HDFC Bank corporate account and IFSC (HDFC0001234)",
            "Registered IT corporate office in Pune Hinjewadi"
        ],
        "risk_factors": [],
        "summary": "Zenith Cloud Technologies Pvt Ltd has a Low Risk score (10/100). All compliance credentials are valid. Recommended for immediate ERP activation."
    },
    {
        "vendor_name": "BuildCraft Infrastructure LLP",
        "gstin": "27AABFB5678G1Z2",
        "pan": "AABFB5678G",
        "address": "Plot 18, MIDC Industrial Area, Turbhe, Navi Mumbai, Maharashtra 400705",
        "contact_person": "Vikram Deshmukh",
        "phone": "9890123456",
        "email": "procurement@buildcraftinfra.com",
        "business_category": "Construction & Infrastructure",
        "bank_name": "State Bank of India",
        "account_number": "319800456789",
        "ifsc_code": "SBIN0005678",
        "risk_score": 15,
        "risk_level": "LOW",
        "recommendation": "APPROVE",
        "validation_status": "VALID",
        "duplicate_status": "UNIQUE",
        "similarity_score": 0.0,
        "source_document": "Demo Seed - BuildCraft_Profile.pdf",
        "processing_status": "COMPLETED",
        "positive_findings": [
            "Valid Maharashtra GSTIN (27AABFB5678G1Z2)",
            "Valid Firm/LLP PAN registered with MCA",
            "Verified SBI corporate current account",
            "Registered construction yard Turbhe MIDC"
        ],
        "risk_factors": [],
        "summary": "BuildCraft Infrastructure LLP cleared all regulatory and banking checks with Low Risk (15/100). Approved for procurement onboarding."
    },
    {
        "vendor_name": "Precision Gears & Heavy Engineering Works",
        "gstin": "33AAECP9876H1Z8",
        "pan": "AAECP9876H",
        "address": "74/A Peelamedu Industrial Estate, Coimbatore, Tamil Nadu 641004",
        "contact_person": "K. Senthil Kumar",
        "phone": "9443011223",
        "email": "sales@precisiongearsindia.com",
        "business_category": "Manufacturing & Industrial",
        "bank_name": "ICICI Bank",
        "account_number": "002305001122",
        "ifsc_code": "ICIC0000023",
        "risk_score": 12,
        "risk_level": "LOW",
        "recommendation": "APPROVE",
        "validation_status": "VALID",
        "duplicate_status": "UNIQUE",
        "similarity_score": 0.0,
        "source_document": "Demo Seed - Precision_Gears_GST.pdf",
        "processing_status": "COMPLETED",
        "positive_findings": [
            "Valid Tamil Nadu GSTIN (33AAECP9876H1Z8)",
            "Valid Industrial Engineering PAN",
            "Verified ICICI Bank business account",
            "Established manufacturing unit in Coimbatore"
        ],
        "risk_factors": [],
        "summary": "Precision Gears & Heavy Engineering Works has a Low Risk score (12/100). Full statutory and banking compliance verified."
    },
    {
        "vendor_name": "SwiftCargo Express Logistics Ltd",
        "gstin": "29AALCS4321J1Z4",
        "pan": "AALCS4321J",
        "address": "Bldg 3, Logistics Park, Nelamangala, Bengaluru, Karnataka 562123",
        "contact_person": "Anand Rao",
        "phone": "9886054321",
        "email": "operations@swiftcargologistics.com",
        "business_category": "Logistics & Supply Chain",
        "bank_name": "Axis Bank",
        "account_number": "918020033445566",
        "ifsc_code": "UTIB0000180",
        "risk_score": 18,
        "risk_level": "LOW",
        "recommendation": "APPROVE",
        "validation_status": "VALID",
        "duplicate_status": "UNIQUE",
        "similarity_score": 0.0,
        "source_document": "Demo Seed - SwiftCargo_Reg.pdf",
        "processing_status": "COMPLETED",
        "positive_findings": [
            "Valid Karnataka GSTIN (29AALCS4321J1Z4)",
            "Valid Limited Company PAN",
            "Verified Axis Bank freight settlement account",
            "Licensed multimodal logistics operator"
        ],
        "risk_factors": [],
        "summary": "SwiftCargo Express Logistics Ltd exhibits Low Risk (18/100) with complete statutory registration. Recommended for onboarding."
    },
    {
        "vendor_name": "Apex BioMed Healthcare Solutions",
        "gstin": "36AABCA7788K1Z9",
        "pan": "AABCA7788K",
        "address": "Suite 501, Pharma Towers, HITEC City, Hyderabad, Telangana 500081",
        "contact_person": "Dr. Sunita Reddy",
        "phone": "9949012398",
        "email": "info@apexbio.in",
        "business_category": "Healthcare & Pharmaceuticals",
        "bank_name": "Kotak Mahindra Bank",
        "account_number": "411200987654",
        "ifsc_code": "KKBK0000411",
        "risk_score": 10,
        "risk_level": "LOW",
        "recommendation": "APPROVE",
        "validation_status": "VALID",
        "duplicate_status": "UNIQUE",
        "similarity_score": 0.0,
        "source_document": "Demo Seed - ApexBio_Docs.pdf",
        "processing_status": "COMPLETED",
        "positive_findings": [
            "Valid Telangana GSTIN (36AABCA7788K1Z9)",
            "Valid Healthcare Company PAN",
            "Verified Kotak Bank medical supplier account",
            "Pharma Towers registered address"
        ],
        "risk_factors": [],
        "summary": "Apex BioMed Healthcare Solutions exhibits a Low Risk profile (10/100). Approved for vendor empanelment."
    },
    {
        "vendor_name": "Vanguard Strategic Consulting & Advisory LLP",
        "gstin": "07AAFFV3344M1Z1",
        "pan": "AAFFV3344M",
        "address": "Floor 9, Barakhamba Road, Connaught Place, New Delhi 110001",
        "contact_person": "Amitabh Sen",
        "phone": "9811098765",
        "email": "advisory@vanguardstrategy.in",
        "business_category": "Consulting & Professional Services",
        "bank_name": "Punjab National Bank",
        "account_number": "0123002100055443",
        "ifsc_code": "PUNB0012300",
        "risk_score": 35,
        "risk_level": "MEDIUM",
        "recommendation": "REVIEW",
        "validation_status": "VALID",
        "duplicate_status": "UNIQUE",
        "similarity_score": 0.0,
        "source_document": "Demo Seed - Vanguard_Advisory.pdf",
        "processing_status": "COMPLETED",
        "positive_findings": [
            "Valid Delhi GSTIN (07AAFFV3344M1Z1)",
            "Valid Partnership/LLP PAN registration",
            "Central New Delhi commercial address"
        ],
        "risk_factors": [
            "High service billing threshold requiring secondary finance director sign-off",
            "Dual consulting and management advisory domain classification"
        ],
        "summary": "Vanguard Strategic Consulting exhibits Medium Risk (35/100). Requires secondary approval from Legal and Finance before activation."
    }
]


def seed_database_with_demo_vendors(force: bool = False) -> int:
    """
    Seeds the SQLite database and FAISS vector index with demo vendors if empty or if force=True.
    Returns count of seeded vendors.
    """
    init_db()
    existing = get_all_vendors()
    if len(existing) > 0 and not force:
        return 0

    if force and len(existing) > 0:
        from database.database import get_db_connection
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM vendors")
            cursor.execute("DELETE FROM assessments")
            cursor.execute("DELETE FROM documents")
            conn.commit()
        existing = []

    count = 0
    for v in DEMO_VENDORS:
        gstin = v.get("gstin")
        already_there = any(ex.get("gstin") == gstin for ex in existing)
        if not already_there:
            v_id = save_vendor(v)
            save_assessment_record(
                vendor_id=v_id,
                gstin=v["gstin"],
                risk_score=v["risk_score"],
                risk_level=v["risk_level"],
                recommendation=v["recommendation"],
                positive_findings=str(v["positive_findings"]),
                risk_factors=str(v["risk_factors"]),
                summary=v["summary"]
            )
            add_vendor_to_index(v)
            log_event(
                event_type="DATABASE_SEEDED",
                vendor_id=v_id,
                vendor_name=v["vendor_name"],
                user_action="System Initialization",
                status="SUCCESS",
                details=f"Demo Vendor seeded for category {v['business_category']}"
            )
            count += 1

    return count
