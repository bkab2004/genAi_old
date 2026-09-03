"""
GenVendorAI Database Module
Provides robust SQLite connection management, schema initialization, CRUD operations, duplicate checks, and analytics queries.
"""

import os
import sqlite3
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "vendors.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "database", "schema.sql")


def get_db_connection() -> sqlite3.Connection:
    """Returns a connection to the SQLite database with row factory enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes the database schema if tables do not exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if os.path.exists(SCHEMA_PATH):
            with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
                schema_sql = f.read()
            cursor.executescript(schema_sql)
        else:
            # Fallback inline creation
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS vendors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vendor_name TEXT NOT NULL,
                gstin TEXT UNIQUE,
                pan TEXT,
                address TEXT,
                contact_person TEXT,
                phone TEXT,
                email TEXT,
                business_category TEXT,
                bank_name TEXT,
                account_number TEXT,
                ifsc_code TEXT,
                risk_score INTEGER DEFAULT 0,
                risk_level TEXT DEFAULT 'UNKNOWN',
                recommendation TEXT DEFAULT 'PENDING',
                validation_status TEXT DEFAULT 'PENDING',
                duplicate_status TEXT DEFAULT 'UNIQUE',
                similarity_score REAL DEFAULT 0.0,
                source_document TEXT,
                processing_status TEXT DEFAULT 'COMPLETED',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vendor_id INTEGER,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_type TEXT DEFAULT 'PDF',
                extraction_method TEXT DEFAULT 'DIRECT',
                extracted_text TEXT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vendor_id INTEGER,
                gstin TEXT,
                risk_score INTEGER,
                risk_level TEXT,
                recommendation TEXT,
                positive_findings TEXT,
                risk_factors TEXT,
                summary TEXT,
                assessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                event_type TEXT NOT NULL,
                vendor_id INTEGER,
                vendor_name TEXT,
                user_action TEXT,
                status TEXT,
                details TEXT
            );
            """)
        conn.commit()


def check_duplicate(vendor_data: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
    """
    Checks if a vendor already exists by GSTIN, PAN, Email, or exact Name.
    Returns: (is_duplicate: bool, duplicate_field: str or None, existing_record: dict or None)
    """
    init_db()
    gstin = str(vendor_data.get("GSTIN") or vendor_data.get("gstin") or "").strip().upper()
    pan = str(vendor_data.get("PAN") or vendor_data.get("pan") or "").strip().upper()
    email = str(vendor_data.get("Email") or vendor_data.get("email") or "").strip().lower()
    name = str(vendor_data.get("Vendor Name") or vendor_data.get("vendor_name") or "").strip()

    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Check GSTIN
        if gstin and gstin != "NOT AVAILABLE":
            cursor.execute("SELECT * FROM vendors WHERE UPPER(TRIM(gstin)) = ?", (gstin,))
            row = cursor.fetchone()
            if row:
                return True, f"GSTIN ({gstin})", dict(row)

        # 2. Check PAN
        if pan and pan != "NOT AVAILABLE":
            cursor.execute("SELECT * FROM vendors WHERE UPPER(TRIM(pan)) = ?", (pan,))
            row = cursor.fetchone()
            if row:
                return True, f"PAN ({pan})", dict(row)

        # 3. Check Email
        if email and email != "not available" and "@" in email:
            cursor.execute("SELECT * FROM vendors WHERE LOWER(TRIM(email)) = ?", (email,))
            row = cursor.fetchone()
            if row:
                return True, f"Email ({email})", dict(row)

        # 4. Check exact Vendor Name (case-insensitive)
        if name and name.lower() != "not available":
            cursor.execute("SELECT * FROM vendors WHERE LOWER(TRIM(vendor_name)) = ?", (name.lower(),))
            row = cursor.fetchone()
            if row:
                return True, f"Vendor Name ({name})", dict(row)

    return False, None, None


def save_vendor(vendor_data: Dict[str, Any]) -> int:
    """
    Saves a new vendor record to the database or updates if ID exists.
    Returns inserted/updated vendor ID.
    """
    init_db()
    
    # Helper to resolve field variations
    def get_val(keys: List[str], default: str = "Not available") -> str:
        for k in keys:
            if k in vendor_data and vendor_data[k] is not None:
                val = str(vendor_data[k]).strip()
                if val:
                    return val
        return default

    vendor_name = get_val(["Vendor Name", "vendor_name", "Company Name", "Supplier Name"])
    gstin = get_val(["GSTIN", "gstin", "GST", "GST Number"])
    pan = get_val(["PAN", "pan", "PAN Number"])
    address = get_val(["Address", "address", "Registered Address"])
    contact_person = get_val(["Contact Person", "contact_person", "Contact Name"])
    phone = get_val(["Phone", "phone", "Mobile", "Contact Number"])
    email = get_val(["Email", "email", "Email Address"])
    business_category = get_val(["Business Category", "business_category", "Category", "Industry"])
    bank_name = get_val(["Bank Name", "bank_name", "Bank"])
    account_number = get_val(["Account Number", "account_number", "Bank Account Number"])
    ifsc_code = get_val(["IFSC Code", "ifsc_code", "IFSC"])
    
    risk_score = vendor_data.get("Risk Score", vendor_data.get("risk_score", 0))
    try:
        risk_score = int(risk_score)
    except:
        risk_score = 0
        
    risk_level = get_val(["Risk Level", "risk_level"], "UNKNOWN")
    recommendation = get_val(["Recommendation", "AI Recommendation", "recommendation"], "PENDING")
    validation_status = get_val(["Validation Status", "validation_status"], "PENDING")
    duplicate_status = get_val(["Duplicate Status", "duplicate_status"], "UNIQUE")
    similarity_score = float(vendor_data.get("Similarity Score", vendor_data.get("similarity_score", 0.0)))
    source_document = get_val(["Source Document", "source_document", "filename"], "Direct Upload")
    processing_status = get_val(["Processing Status", "processing_status"], "COMPLETED")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO vendors (
                vendor_name, gstin, pan, address, contact_person, phone, email,
                business_category, bank_name, account_number, ifsc_code,
                risk_score, risk_level, recommendation, validation_status,
                duplicate_status, similarity_score, source_document, processing_status,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            vendor_name, gstin, pan, address, contact_person, phone, email,
            business_category, bank_name, account_number, ifsc_code,
            risk_score, risk_level, recommendation, validation_status,
            duplicate_status, similarity_score, source_document, processing_status,
            now, now
        ))
        vendor_id = cursor.lastrowid
        conn.commit()
        return vendor_id


def update_vendor_assessment(
    gstin: str,
    risk_score: int,
    risk_level: str,
    recommendation: str,
    validation_status: str,
    duplicate_status: str,
    similarity_score: float = 0.0
):
    """Updates AI risk assessment & validation results for a vendor by GSTIN or Name."""
    init_db()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE vendors
            SET risk_score = ?,
                risk_level = ?,
                recommendation = ?,
                validation_status = ?,
                duplicate_status = ?,
                similarity_score = ?,
                updated_at = ?
            WHERE UPPER(TRIM(gstin)) = ? OR UPPER(TRIM(gstin)) LIKE ?
        """, (
            risk_score, risk_level, recommendation, validation_status,
            duplicate_status, similarity_score, now,
            gstin.strip().upper(), f"%{gstin.strip().upper()}%"
        ))
        conn.commit()


def save_document_record(
    vendor_id: Optional[int],
    filename: str,
    file_path: str,
    extraction_method: str = "DIRECT",
    extracted_text: str = ""
) -> int:
    """Saves document processing metadata."""
    init_db()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO documents (vendor_id, filename, file_path, extraction_method, extracted_text, uploaded_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (vendor_id, filename, file_path, extraction_method, extracted_text, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        doc_id = cursor.lastrowid
        conn.commit()
        return doc_id


def save_assessment_record(
    vendor_id: Optional[int],
    gstin: str,
    risk_score: int,
    risk_level: str,
    recommendation: str,
    positive_findings: str,
    risk_factors: str,
    summary: str
) -> int:
    """Saves granular AI risk evaluation findings."""
    init_db()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO assessments (
                vendor_id, gstin, risk_score, risk_level, recommendation,
                positive_findings, risk_factors, summary, assessed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            vendor_id, gstin, risk_score, risk_level, recommendation,
            positive_findings, risk_factors, summary, datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        assessment_id = cursor.lastrowid
        conn.commit()
        return assessment_id


def get_latest_assessment(vendor_id: int) -> Optional[Dict[str, Any]]:
    """Retrieves the latest assessment details for a vendor."""
    init_db()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM assessments WHERE vendor_id = ? ORDER BY id DESC LIMIT 1
        """, (vendor_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_all_vendors() -> List[Dict[str, Any]]:
    """Retrieves all vendors ordered by most recently updated."""
    init_db()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vendors ORDER BY id DESC")
        rows = cursor.fetchall()
        return [dict(r) for r in rows]


def get_all_vendors_df() -> pd.DataFrame:
    """Returns all vendors as a pandas DataFrame."""
    init_db()
    with get_db_connection() as conn:
        df = pd.read_sql_query("SELECT * FROM vendors ORDER BY id DESC", conn)
        return df


def get_vendor_by_id(vendor_id: int) -> Optional[Dict[str, Any]]:
    """Retrieves single vendor by primary key."""
    init_db()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vendors WHERE id = ?", (vendor_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_vendor_by_gstin(gstin: str) -> Optional[Dict[str, Any]]:
    """Retrieves single vendor by GSTIN."""
    init_db()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM vendors WHERE UPPER(TRIM(gstin)) = ?", (gstin.strip().upper(),))
        row = cursor.fetchone()
        return dict(row) if row else None


def delete_vendor(vendor_id: int) -> bool:
    """Deletes vendor record and associated assessments/documents."""
    init_db()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM vendors WHERE id = ?", (vendor_id,))
        cursor.execute("DELETE FROM assessments WHERE vendor_id = ?", (vendor_id,))
        cursor.execute("DELETE FROM documents WHERE vendor_id = ?", (vendor_id,))
        conn.commit()
        return cursor.rowcount > 0


def export_vendors_to_csv(filepath: Optional[str] = None) -> str:
    """Exports vendor database to a CSV file. Returns CSV file path."""
    df = get_all_vendors_df()
    if not filepath:
        os.makedirs(os.path.join(BASE_DIR, "reports"), exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(BASE_DIR, "reports", f"vendors_export_{timestamp}.csv")
    df.to_csv(filepath, index=False)
    return filepath


def get_vendor_stats() -> Dict[str, Any]:
    """Calculates aggregate statistics for KPIs and charts."""
    init_db()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM vendors")
        total_vendors = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM vendors WHERE UPPER(recommendation) = 'APPROVE'")
        approved = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM vendors WHERE UPPER(recommendation) = 'REVIEW'")
        under_review = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM vendors WHERE UPPER(recommendation) = 'REJECT'")
        rejected = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM vendors WHERE UPPER(risk_level) = 'LOW'")
        low_risk = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM vendors WHERE UPPER(risk_level) = 'MEDIUM'")
        medium_risk = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM vendors WHERE UPPER(risk_level) = 'HIGH'")
        high_risk = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM vendors WHERE UPPER(validation_status) = 'VALID'")
        valid_records = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM vendors WHERE UPPER(duplicate_status) != 'UNIQUE'")
        duplicate_records = cursor.fetchone()[0]

        return {
            "total_vendors": total_vendors,
            "approved": approved,
            "under_review": under_review,
            "rejected": rejected,
            "low_risk": low_risk,
            "medium_risk": medium_risk,
            "high_risk": high_risk,
            "valid_records": valid_records,
            "duplicate_records": duplicate_records
        }
