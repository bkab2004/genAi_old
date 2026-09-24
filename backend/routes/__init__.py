"""
GenVendorAI API Routes Package
"""
from backend.routes.process_routes import router as process_router
from backend.routes.vendor_routes import router as vendor_router
from backend.routes.search_routes import router as search_router
from backend.routes.analytics_routes import router as analytics_router
from backend.routes.report_routes import router as report_router
from backend.routes.audit_routes import router as audit_router
from backend.routes.chat_routes import router as chat_router

__all__ = [
    "process_router",
    "vendor_router",
    "search_router",
    "analytics_router",
    "report_router",
    "audit_router",
    "chat_router"
]
