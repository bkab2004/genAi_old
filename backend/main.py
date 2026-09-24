"""
GenVendorAI FastAPI Application Main Entry Point
================================================
Exposes RESTful endpoints for document ingestion, OCR parsing, statutory validation,
semantic vector search, explainable AI risk scoring, and analytics dashboards.
"""

import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Set base path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from database.database import init_db
from ai.vector_store import init_vector_store
from sample_data.seed_data import seed_database_with_demo_vendors
from sample_data.generate_sample_pdfs import generate_all_sample_pdfs

from backend.routes.process_routes import router as process_router
from backend.routes.vendor_routes import router as vendor_router
from backend.routes.search_routes import router as search_router
from backend.routes.analytics_routes import router as analytics_router
from backend.routes.report_routes import router as report_router
from backend.routes.audit_routes import router as audit_router
from backend.routes.chat_routes import router as chat_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle startup and shutdown handler."""
    print("🚀 Initializing GenVendorAI Backend Systems...")
    init_db()
    init_vector_store()
    seed_database_with_demo_vendors()
    generate_all_sample_pdfs()
    print("✅ GenVendorAI Backend Ready and Listening.")
    yield
    print("🛑 GenVendorAI Backend Shutting Down.")


app = FastAPI(
    title="GenVendorAI – Vendor Intelligence & Risk API",
    description="Enterprise REST API for AI-powered Vendor Master Data Management, OCR Extraction, Regulatory Validation, and Risk Scoring.",
    version="2.0.0",
    lifespan=lifespan
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(process_router)
app.include_router(vendor_router)
app.include_router(search_router)
app.include_router(analytics_router)
app.include_router(report_router)
app.include_router(audit_router)
app.include_router(chat_router)

# Mount Frontend Static Assets
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/api/health", tags=["System"])
def health_check():
    """System health check and operational status."""
    return {
        "status": "HEALTHY",
        "service": "GenVendorAI API Engine",
        "version": "2.0.0",
        "timestamp": os.path.getmtime(__file__) if os.path.exists(__file__) else None
    }


@app.get("/", include_in_schema=False)
def serve_frontend_spa():
    """Serves the frontend Single Page Application (SPA)."""
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "GenVendorAI Backend is active. Visit /docs for Swagger API documentation."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
