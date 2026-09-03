-- GenVendorAI Database Schema
-- SQLite schema for Vendor Master Data Management, Documents, Risk Assessments, and Audit Logs

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

CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vendor_id INTEGER,
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_type TEXT DEFAULT 'PDF',
    extraction_method TEXT DEFAULT 'DIRECT',
    extracted_text TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vendor_id) REFERENCES vendors (id) ON DELETE SET NULL
);

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
    assessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vendor_id) REFERENCES vendors (id) ON DELETE CASCADE
);

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

-- Indexes for high performance querying and duplicate lookup
CREATE INDEX IF NOT EXISTS idx_vendors_gstin ON vendors(gstin);
CREATE INDEX IF NOT EXISTS idx_vendors_pan ON vendors(pan);
CREATE INDEX IF NOT EXISTS idx_vendors_email ON vendors(email);
CREATE INDEX IF NOT EXISTS idx_vendors_risk ON vendors(risk_level);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_event ON audit_logs(event_type);
