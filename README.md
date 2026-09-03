# GenVendorAI – AI-Powered Vendor Intelligence and Risk Assessment System

> **MDM Capstone Project | Project Group ID: 104**  
> **Department of Computer Science & Engineering (AI & ML)**  
> **Pimpri Chinchwad College of Engineering (PCCOE), Pune**  
> **Academic Year: 2026 – 2027**  
> **Project Guide:** Dr. Ashwini Deshpande  
> **Team Members:** Chirag Jathe, Prashik Dekate, Sharad Gajjewar, Bhakti Kulkarni  

---

## 📌 Project Overview
**GenVendorAI** is an enterprise-grade AI-powered Vendor Master Data Management (MDM) and Risk Assessment platform. It ingests unstructured and semi-structured vendor documentation (PDF certificates, GST filings, PAN cards, bank verification letters, and quotations), extracts structured vendor attributes, executes regulatory and syntax validation against Indian statutory standards, detects exact and semantic duplicates using dense vector embeddings and FAISS, computes an explainable multi-factor risk score (0–100), and outputs automated onboarding recommendations (`APPROVE`, `REVIEW`, `REJECT`) with comprehensive audit logs and interactive analytics dashboards.

The platform provides a **Modern Full-Stack Web Architecture (FastAPI + Modern Web SPA)** and operates **100% locally and offline with zero mandatory paid API keys**.

---

## 🏗️ System Architecture & Workflow

```
                   +---------------------------------------+
                   |          VENDOR DOCUMENT (PDF)        |
                   +---------------------------------------+
                                       |
                                       v
                   +---------------------------------------+
                   |  PyMuPDF / pdfplumber Digital Extract |
                   +---------------------------------------+
                                       | (Fallback if scanned)
                                       v
                   +---------------------------------------+
                   |  Pytesseract OCR + Image Enhancement  |
                   +---------------------------------------+
                                       |
                                       v
                   +---------------------------------------+
                   |    Structured Information Extractor   |
                   |  (Vendor Name, GSTIN, PAN, Bank, etc) |
                   +---------------------------------------+
                                       |
                                       v
                   +---------------------------------------+
                   |       Statutory Validation Engine     |
                   |  (GSTIN Checksum, PAN Entity, IFSC)   |
                   +---------------------------------------+
                                       |
                                       v
                   +---------------------------------------+
                   |    Dual-Layer Deduplication Engine    |
                   |   - Exact Matching (GST/PAN/Email)    |
                   |   - Semantic Similarity (FAISS/SBERT) |
                   +---------------------------------------+
                                       |
                                       v
                   +---------------------------------------+
                   |    Explainable AI Risk Scoring Engine |
                   |  (Score: 0-100, Tier, Recommendation) |
                   +---------------------------------------+
                                       |
                 +---------------------+---------------------+
                 |                                           |
                 v                                           v
+-----------------------------------+     +-----------------------------------+
|  Master Database & Audit Trails   |     |    FastAPI REST API + Web SPA     |
|     (SQLite + FAISS Index)        |     |   (Chart.js, Semantic Search, UI) |
+-----------------------------------+     +-----------------------------------+
```

---

## 💻 Technology Stack

| Layer | Technologies Used |
|---|---|
| **Backend REST API** | FastAPI, Uvicorn, Python-Multipart |
| **Frontend Web App** | Modern Single Page Application (Tailwind CSS, Chart.js, Lucide Icons) |
| **Alternative UI** | Streamlit (`app.py`) |
| **Relational Database** | SQLite (`vendors.db` with schema auto-migration) |
| **Document Processing** | PyMuPDF (`pymupdf`), `pdfplumber` |
| **OCR Fallback Engine** | `pytesseract`, `pdf2image`, `Pillow` |
| **Semantic Embeddings** | Sentence-Transformers (`all-MiniLM-L6-v2`) |
| **Vector Similarity Search** | FAISS (`faiss-cpu`) IndexFlatIP (Cosine Similarity) |
| **Visualizations & Charts** | Chart.js & Plotly |
| **Dossier & Report Output** | ReportLab (PDF) and styled standalone HTML |
| **Data Analytics** | Pandas, NumPy |

---

## 📁 Full-Stack Project Structure

```
D:\GenAi\
│
├── run_fullstack.py               # Unified Launcher for FastAPI + Modern Web UI
├── start.bat                      # 1-Click Windows Batch Launcher
├── app.py                         # Streamlit Interface (Alternative UI)
├── requirements.txt               # Complete Python dependencies
├── README.md                      # Academic Project & Technical Documentation
├── test_system.py                 # System Test Suite
│
├── backend/                       # FastAPI REST API Backend
│   ├── __init__.py
│   ├── main.py                    # Application Entry, CORS, Static Mounting
│   └── routes/
│       ├── process_routes.py      # /api/process/upload, /api/process/samples
│       ├── vendor_routes.py       # /api/vendors (CRUD, filtering, export)
│       ├── search_routes.py       # /api/search/semantic (Vector query)
│       ├── analytics_routes.py   # /api/analytics/stats, /api/analytics/charts
│       ├── report_routes.py       # /api/reports/{id}/pdf, /html
│       └── audit_routes.py        # /api/audit/logs
│
├── frontend/                      # Modern, Responsive Web Frontend
│   ├── index.html                 # Single Page Application Layout
│   ├── css/
│   │   └── styles.css             # Glassmorphism, animations, dark theme
│   └── js/
│       ├── api.js                 # Frontend REST API Client
│       └── app.js                 # State management, Chart.js, workflow controller
│
├── database/                      # Shared SQLite Database Layer
│   ├── database.py
│   ├── schema.sql
│   └── vendors.db
│
├── ocr/                           # Shared OCR & PDF Extraction Layer
│   ├── pdf_extractor.py
│   ├── ocr_engine.py
│   └── extractor.py
│
├── ai/                            # Shared Sentence-Transformers & FAISS Engine
│   ├── embeddings.py
│   ├── vector_store.py
│   ├── semantic_search.py
│   └── risk_engine.py
│
├── validation/                    # Shared Regulatory Validation Engine
│   └── validator.py
│
├── dashboard/                     # Shared Analytics Visualizations
│   └── dashboard.py
│
├── audit/                         # Shared Audit Logging Layer
│   └── audit_logger.py
│
├── reports/                       # Shared PDF/HTML Report Generator
│   └── report_generator.py
│
├── sample_data/                   # Shared Sample Documents & Seeder
│   ├── seed_data.py
│   └── generate_sample_pdfs.py
│
├── documents/
│   ├── uploads/                   # Staged Uploads
│   ├── processed/                 # Archived Documents
│   └── sample_docs/               # 6 Ready-to-Test Sample PDFs
│
└── vector_db/
    ├── vendor_index.faiss         # Serialized FAISS Vector Index
    └── vendor_metadata.pkl        # Serialized Metadata Dictionary
```

---

## 🚀 How to Run the Application

### Option A: Launch Full-Stack Web Application (Recommended)
```powershell
cd D:\GenAi
python run_fullstack.py
```
*Or double click `start.bat`. This starts the FastAPI server and automatically opens the modern web frontend at `http://127.0.0.1:8000`.*

- **Web Frontend**: `http://127.0.0.1:8000/`
- **Interactive Swagger API Docs**: `http://127.0.0.1:8000/docs`
- **ReDoc API Documentation**: `http://127.0.0.1:8000/redoc`

### Option B: Launch Streamlit Dashboard
```powershell
cd D:\GenAi
python -m streamlit run app.py
```
*Opens Streamlit at `http://localhost:8501`.*

---

## 🔬 Academic & Research Contributions
1. **End-to-End Autonomous Pipeline**: Integrates document ingestion, OCR fallback, field extraction, validation, deduplication, AI risk assessment, and decision support in a unified workflow.
2. **Dual-Layer Deduplication**: Exact SQL matching + Sentence-BERT dense embeddings in FAISS.
3. **Explainable Decision Support**: Transparent 0–100 scoring with human-auditable findings rather than black-box labels.
4. **Data Sovereignty & Local AI**: 100% offline local inference without requiring paid API tokens.

---

## 📜 License & Acknowledgments
Developed as part of the Final-Year B.Tech Capstone Project (Group 104) at **Pimpri Chinchwad College of Engineering (PCCOE), Pune**, affiliated with Savitribai Phule Pune University.
