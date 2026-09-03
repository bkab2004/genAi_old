"""
GenVendorAI Audit Logger Module
Maintains an immutable and queryable audit trail of all vendor processing operations,
document extractions, validation passes, duplicate checks, and AI decision events.
"""

import json
import sqlite3
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime
from database.database import get_db_connection, init_db


def log_event(
    event_type: str,
    vendor_id: Optional[int] = None,
    vendor_name: Optional[str] = None,
    user_action: str = "System Automated",
    status: str = "SUCCESS",
    details: Optional[Any] = None
) -> int:
    """
    Logs a structured event to the audit_logs table.
    
    Supported event types:
    - DOCUMENT_UPLOADED
    - OCR_COMPLETED
    - VENDOR_EXTRACTED
    - VALIDATION_COMPLETED
    - DUPLICATE_CHECKED
    - VENDOR_CREATED
    - RISK_ASSESSMENT_COMPLETED
    - VENDOR_APPROVED
    - VENDOR_REJECTED
    - VENDOR_DELETED
    - REPORT_GENERATED
    - SYSTEM_INITIALIZED
    """
    init_db()
    
    # Format details safely to JSON or string
    details_str = ""
    if details is not None:
        if isinstance(details, (dict, list)):
            try:
                details_str = json.dumps(details, default=str)
            except Exception:
                details_str = str(details)
        else:
            details_str = str(details)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO audit_logs (timestamp, event_type, vendor_id, vendor_name, user_action, status, details)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (now, event_type, vendor_id, vendor_name or "N/A", user_action, status, details_str))
            log_id = cursor.lastrowid
            conn.commit()
            return log_id
    except Exception as e:
        print(f"[AuditLogger Error] Failed to log event {event_type}: {e}")
        return -1


def get_all_audit_logs(limit: int = 200) -> List[Dict[str, Any]]:
    """Retrieves all audit logs up to limit, ordered by most recent first."""
    init_db()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM audit_logs ORDER BY id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        return [dict(r) for r in rows]


def get_audit_logs_df(limit: int = 500) -> pd.DataFrame:
    """Returns audit logs as a pandas DataFrame."""
    init_db()
    with get_db_connection() as conn:
        df = pd.read_sql_query("SELECT * FROM audit_logs ORDER BY id DESC LIMIT ?", conn, params=(limit,))
        return df


def get_logs_by_vendor(vendor_id: int) -> List[Dict[str, Any]]:
    """Retrieves logs specific to a given vendor ID."""
    init_db()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM audit_logs WHERE vendor_id = ? ORDER BY id DESC", (vendor_id,))
        rows = cursor.fetchall()
        return [dict(r) for r in rows]


def get_logs_by_event_type(event_type: str) -> List[Dict[str, Any]]:
    """Retrieves logs filtered by event type."""
    init_db()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM audit_logs WHERE event_type = ? ORDER BY id DESC", (event_type,))
        rows = cursor.fetchall()
        return [dict(r) for r in rows]


def clear_audit_logs():
    """Clears all audit logs (for demo reset purposes)."""
    init_db()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM audit_logs")
        conn.commit()
