"""
GenVendorAI Analytics Routes
Provides executive KPI metrics and formatted data structures for frontend Chart.js visualizations.
"""

import pandas as pd
from fastapi import APIRouter
from database.database import get_all_vendors_df, get_vendor_stats

router = APIRouter(prefix="/api/analytics", tags=["Executive Analytics & Dashboard"])


@router.get("/stats")
def get_stats():
    """Returns top KPI indicators."""
    return get_vendor_stats()


@router.get("/charts")
def get_chart_data():
    """Returns aggregated datasets formatted for frontend Chart.js components."""
    df = get_all_vendors_df()
    
    if df.empty:
        return {
            "category_distribution": {"labels": [], "data": []},
            "risk_distribution": {"labels": ["LOW", "MEDIUM", "HIGH"], "data": [0, 0, 0]},
            "recommendation_distribution": {"labels": ["APPROVE", "REVIEW", "REJECT"], "data": [0, 0, 0]},
            "risk_by_category": {"labels": [], "data": []},
            "timeline": {"labels": [], "data": [], "cumulative": []},
            "watchlist": []
        }

    # 1. Category Distribution
    cat_counts = df["business_category"].value_counts()
    category_distribution = {
        "labels": cat_counts.index.tolist(),
        "data": cat_counts.values.tolist()
    }

    # 2. Risk Distribution
    risk_map = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
    for r in df["risk_level"].dropna():
        r_up = r.upper()
        if r_up in risk_map:
            risk_map[r_up] += 1
    risk_distribution = {
        "labels": list(risk_map.keys()),
        "data": list(risk_map.values())
    }

    # 3. Recommendation Distribution
    rec_map = {"APPROVE": 0, "REVIEW": 0, "REJECT": 0}
    for rec in df["recommendation"].dropna():
        rec_up = rec.upper()
        if rec_up in rec_map:
            rec_map[rec_up] += 1
    recommendation_distribution = {
        "labels": list(rec_map.keys()),
        "data": list(rec_map.values())
    }

    # 4. Average Risk Score by Category
    avg_risk = df.groupby("business_category")["risk_score"].mean().round(1)
    risk_by_category = {
        "labels": avg_risk.index.tolist(),
        "data": avg_risk.values.tolist()
    }

    # 5. Timeline
    df_time = df.copy()
    df_time["date"] = pd.to_datetime(df_time["created_at"]).dt.strftime("%Y-%m-%d")
    time_grouped = df_time.groupby("date").size()
    timeline = {
        "labels": time_grouped.index.tolist(),
        "data": time_grouped.values.tolist(),
        "cumulative": time_grouped.cumsum().tolist()
    }

    # 6. Watchlist (High Risk, Reject, Duplicate)
    flagged = df[(df["risk_level"] == "HIGH") | (df["recommendation"] == "REJECT") | (df["duplicate_status"] != "UNIQUE")]
    watchlist = flagged[["id", "vendor_name", "business_category", "gstin", "risk_score", "risk_level", "recommendation", "duplicate_status"]].to_dict(orient="records")

    return {
        "category_distribution": category_distribution,
        "risk_distribution": risk_distribution,
        "recommendation_distribution": recommendation_distribution,
        "risk_by_category": risk_by_category,
        "timeline": timeline,
        "watchlist": watchlist
    }
