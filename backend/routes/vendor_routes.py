"""
GenVendorAI Vendor Routes
CRUD endpoints for Vendor Master Records, database export, and demo seeding.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Response
from database.database import (
    get_all_vendors, get_all_vendors_df, get_vendor_by_id,
    delete_vendor, get_latest_assessment
)
from sample_data.seed_data import seed_database_with_demo_vendors
from audit.audit_logger import log_event

router = APIRouter(prefix="/api/vendors", tags=["Vendor Master Records"])


@router.get("")
def list_vendors(
    search: Optional[str] = None,
    category: Optional[str] = None,
    risk_level: Optional[str] = None,
    recommendation: Optional[str] = None
):
    """Retrieves all vendors with optional filters."""
    vendors = get_all_vendors()
    
    filtered = []
    for v in vendors:
        # Search match
        if search:
            s = search.lower()
            name_match = s in str(v.get("vendor_name", "")).lower()
            gst_match = s in str(v.get("gstin", "")).lower()
            pan_match = s in str(v.get("pan", "")).lower()
            if not (name_match or gst_match or pan_match):
                continue

        # Category match
        if category and category.lower() != "all":
            if category.lower() not in str(v.get("business_category", "")).lower():
                continue

        # Risk level match
        if risk_level and risk_level.upper() != "ALL":
            if str(v.get("risk_level", "")).upper() != risk_level.upper():
                continue

        # Recommendation match
        if recommendation and recommendation.upper() != "ALL":
            if str(v.get("recommendation", "")).upper() != recommendation.upper():
                continue

        filtered.append(v)

    return {
        "total": len(filtered),
        "vendors": filtered
    }


@router.get("/{vendor_id}")
def get_vendor_details(vendor_id: int):
    """Retrieves full details and latest AI assessment for a vendor."""
    vendor = get_vendor_by_id(vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    assessment = get_latest_assessment(vendor_id)
    return {
        "vendor": vendor,
        "assessment": assessment
    }


@router.delete("/{vendor_id}")
def remove_vendor(vendor_id: int):
    """Deletes a vendor record from the master database."""
    vendor = get_vendor_by_id(vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    success = delete_vendor(vendor_id)
    if success:
        log_event(
            event_type="VENDOR_DELETED",
            vendor_id=vendor_id,
            vendor_name=vendor.get("vendor_name"),
            user_action="API User Request",
            status="SUCCESS",
            details=f"Vendor #{vendor_id} permanently removed"
        )
        return {"success": True, "message": f"Vendor #{vendor_id} deleted successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to delete vendor")


@router.post("/seed")
def seed_demo_data():
    """Forces database re-seeding with 6 realistic enterprise demo vendors."""
    count = seed_database_with_demo_vendors(force=True)
    return {
        "success": True,
        "seeded_count": count,
        "message": f"Successfully re-seeded {count} demo vendors."
    }


@router.get("/export/csv")
def export_csv():
    """Streams full vendor database as a CSV file."""
    df = get_all_vendors_df()
    csv_str = df.to_csv(index=False)
    return Response(
        content=csv_str,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=GenVendorAI_Vendors_Master.csv"}
    )
