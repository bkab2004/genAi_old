"""
GenVendorAI Database Package
Handles SQLite connection, schema initialization, CRUD operations, duplicate checks, and CSV export.
"""

from database.database import (
    get_db_connection,
    init_db,
    save_vendor,
    get_all_vendors,
    get_vendor_by_id,
    get_vendor_by_gstin,
    check_duplicate,
    update_vendor_assessment,
    save_document_record,
    save_assessment_record,
    get_latest_assessment,
    export_vendors_to_csv,
    delete_vendor,
    get_vendor_stats
)

__all__ = [
    "get_db_connection",
    "init_db",
    "save_vendor",
    "get_all_vendors",
    "get_vendor_by_id",
    "get_vendor_by_gstin",
    "check_duplicate",
    "update_vendor_assessment",
    "save_document_record",
    "save_assessment_record",
    "get_latest_assessment",
    "export_vendors_to_csv",
    "delete_vendor",
    "get_vendor_stats"
]
