"""
GenVendorAI Dashboard Module
Renders an executive-grade analytics dashboard using Plotly and Streamlit with real-time KPI metrics,
category distributions, risk breakdowns, validation trends, and decision summaries.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database.database import get_all_vendors_df, get_vendor_stats, export_vendors_to_csv


def show_dashboard():
    """Renders the complete analytics dashboard."""
    st.title("📊 Enterprise Vendor Analytics & Compliance Dashboard")
    st.caption("Real-time monitoring of vendor master data, regulatory risk tiers, duplicate alerts, and onboarding throughput.")

    df = get_all_vendors_df()
    stats = get_vendor_stats()

    total_vendors = stats["total_vendors"]

    if total_vendors == 0:
        st.warning("⚠️ No vendor records found in the database. Please seed demo data or process vendor documents to view analytics.")
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🌱 Load Demo Dataset", type="primary"):
                from sample_data.seed_data import seed_database_with_demo_vendors
                seeded = seed_database_with_demo_vendors(force=True)
                st.success(f"Successfully seeded {seeded} demo vendors!")
                st.rerun()
        return

    # ========================================================
    # ROW 1: TOP KPI METRIC CARDS
    # ========================================================
    st.markdown("### 📈 Key Operational Indicators")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    approved_pct = (stats["approved"] / total_vendors * 100) if total_vendors else 0
    review_pct = (stats["under_review"] / total_vendors * 100) if total_vendors else 0
    rejected_pct = (stats["rejected"] / total_vendors * 100) if total_vendors else 0

    with col1:
        st.metric(
            label="Total Master Records",
            value=f"{total_vendors:,}",
            delta="Active MDM Hub"
        )
    with col2:
        st.metric(
            label="Approved Vendors",
            value=f"{stats['approved']}",
            delta=f"{approved_pct:.1f}% rate",
            delta_color="normal"
        )
    with col3:
        st.metric(
            label="Under Review",
            value=f"{stats['under_review']}",
            delta=f"{review_pct:.1f}% backlog",
            delta_color="off"
        )
    with col4:
        st.metric(
            label="Rejected Entries",
            value=f"{stats['rejected']}",
            delta=f"{rejected_pct:.1f}% risk blocked",
            delta_color="inverse"
        )
    with col5:
        st.metric(
            label="Valid Format Rate",
            value=f"{stats['valid_records']}",
            delta=f"{(stats['valid_records'] / total_vendors * 100):.1f}% verified"
        )

    st.markdown("---")

    # ========================================================
    # ROW 2: CHARTS (Category Distribution & Risk Levels)
    # ========================================================
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("#### 🏢 Industry & Category Breakdown")
        if "business_category" in df.columns and not df["business_category"].dropna().empty:
            cat_counts = df["business_category"].value_counts().reset_index()
            cat_counts.columns = ["Business Category", "Count"]

            fig_cat = px.bar(
                cat_counts,
                x="Count",
                y="Business Category",
                orientation='h',
                color="Count",
                color_continuous_scale="Blues",
                text="Count",
                title="Vendors by Procurement Category"
            )
            fig_cat.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                xaxis_title="Number of Vendors",
                yaxis_title="",
                height=340,
                margin=dict(l=10, r=10, t=40, b=10)
            )
            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            st.info("No category data available.")

    with chart_col2:
        st.markdown("#### 🎯 AI Risk Tier Distribution")
        risk_counts = df["risk_level"].value_counts().reset_index()
        risk_counts.columns = ["Risk Level", "Count"]

        color_map = {
            "LOW": "#10B981",       # Emerald Green
            "MEDIUM": "#F59E0B",    # Amber
            "HIGH": "#EF4444",      # Red
            "UNKNOWN": "#94A3B8"    # Gray
        }

        fig_risk = px.pie(
            risk_counts,
            names="Risk Level",
            values="Count",
            hole=0.45,
            color="Risk Level",
            color_discrete_map=color_map,
            title="Vendor Risk Classification Breakdown"
        )
        fig_risk.update_traces(textposition='inside', textinfo='percent+label')
        fig_risk.update_layout(
            height=340,
            margin=dict(l=10, r=10, t=40, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_risk, use_container_width=True)

    # ========================================================
    # ROW 3: CHARTS (Recommendation Breakdown & Risk vs Score)
    # ========================================================
    chart_col3, chart_col4 = st.columns(2)

    with chart_col3:
        st.markdown("#### 📌 Decision Support Distribution")
        rec_counts = df["recommendation"].value_counts().reset_index()
        rec_counts.columns = ["Recommendation", "Count"]

        rec_color_map = {
            "APPROVE": "#10B981",
            "REVIEW": "#F59E0B",
            "REJECT": "#EF4444",
            "PENDING": "#94A3B8"
        }

        fig_rec = px.pie(
            rec_counts,
            names="Recommendation",
            values="Count",
            hole=0.45,
            color="Recommendation",
            color_discrete_map=rec_color_map,
            title="Procurement Recommendations"
        )
        fig_rec.update_traces(textposition='inside', textinfo='percent+label')
        fig_rec.update_layout(
            height=340,
            margin=dict(l=10, r=10, t=40, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_rec, use_container_width=True)

    with chart_col4:
        st.markdown("#### ⚡ Average Risk Score by Category")
        if "business_category" in df.columns and "risk_score" in df.columns:
            avg_risk = df.groupby("business_category")["risk_score"].mean().reset_index()
            avg_risk.columns = ["Business Category", "Avg Risk Score"]
            avg_risk["Avg Risk Score"] = avg_risk["Avg Risk Score"].round(1)

            fig_bar = px.bar(
                avg_risk,
                x="Business Category",
                y="Avg Risk Score",
                color="Avg Risk Score",
                color_continuous_scale="Reds",
                text="Avg Risk Score",
                title="Mean Risk Score per Procurement Domain (0-100)"
            )
            fig_bar.update_layout(
                xaxis_title="",
                yaxis_title="Mean Risk Score (0-100)",
                height=340,
                margin=dict(l=10, r=10, t=40, b=10)
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    # ========================================================
    # ROW 4: REGISTRATION TIMELINE & DUPLICATE METRICS
    # ========================================================
    st.markdown("#### 📅 Master Data Onboarding Timeline")
    if "created_at" in df.columns and not df["created_at"].dropna().empty:
        df_time = df.copy()
        df_time["date"] = pd.to_datetime(df_time["created_at"]).dt.date
        time_counts = df_time.groupby("date").size().reset_index(name="Daily Onboarded")
        time_counts["Cumulative Vendors"] = time_counts["Daily Onboarded"].cumsum()

        fig_time = go.Figure()
        fig_time.add_trace(go.Bar(
            x=time_counts["date"],
            y=time_counts["Daily Onboarded"],
            name="Daily Uploads",
            marker_color="#93C5FD"
        ))
        fig_time.add_trace(go.Scatter(
            x=time_counts["date"],
            y=time_counts["Cumulative Vendors"],
            name="Cumulative Total",
            mode="lines+markers",
            line=dict(color="#1D4ED8", width=3)
        ))
        fig_time.update_layout(
            height=300,
            margin=dict(l=10, r=10, t=30, b=10),
            xaxis_title="Date",
            yaxis_title="Vendor Count",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_time, use_container_width=True)

    # ========================================================
    # ROW 5: RECENT HIGH-RISK & DUPLICATE ALERTS TABLE
    # ========================================================
    st.markdown("#### 🚨 Active Compliance & Risk Watchlist")
    flagged = df[(df["risk_level"] == "HIGH") | (df["recommendation"] == "REJECT") | (df["duplicate_status"] != "UNIQUE")]
    
    if not flagged.empty:
        st.warning(f"⚠️ {len(flagged)} vendors currently flagged on the compliance watchlist.")
        display_cols = ["id", "vendor_name", "business_category", "gstin", "risk_score", "risk_level", "recommendation", "duplicate_status"]
        st.dataframe(
            flagged[display_cols].rename(columns={
                "id": "ID",
                "vendor_name": "Vendor Name",
                "business_category": "Category",
                "gstin": "GSTIN",
                "risk_score": "Risk (0-100)",
                "risk_level": "Risk Level",
                "recommendation": "Decision",
                "duplicate_status": "Duplicate Status"
            }),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success("✅ No high-risk or duplicate vendor violations currently on active watchlist.")

    # ========================================================
    # EXPORT DATA
    # ========================================================
    st.markdown("---")
    col_exp1, col_exp2 = st.columns([2, 8])
    with col_exp1:
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Full Database (CSV)",
            data=csv_data,
            file_name="GenVendorAI_Vendor_Master_Database.csv",
            mime="text/csv",
            type="secondary"
        )
