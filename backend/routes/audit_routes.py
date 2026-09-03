"""
GenVendorAI Audit Routes
Endpoints for querying and managing the enterprise audit trail.
"""

from typing import Optional
from fastapi import APIRouter
from audit.audit_logger import get_all_audit_logs, get_logs_by_event_type, clear_audit_logs

router = APIRouter(prefix="/api/audit", tags=["Enterprise Audit Trail"])


@router.get("/logs")
def fetch_audit_logs(event_type: Optional[str] = None, limit: int = 100):
    """Retrieves chronological audit trail records."""
    if event_type and event_type.upper() != "ALL":
        logs = get_logs_by_event_type(event_type)
    else:
        logs = get_all_audit_logs(limit=limit)

    return {
        "total": len(logs),
        "logs": logs
    }


@router.delete("/clear")
def clear_logs_endpoint():
    """Clears all audit logs for demonstration reset purposes."""
    clear_audit_logs()
    return {"success": True, "message": "Audit logs cleared successfully."}
