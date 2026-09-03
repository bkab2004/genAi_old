"""
GenVendorAI Vendor Details Extractor Module
Uses pattern matching, regular expressions, and NLP heuristics to extract
structured vendor attributes from raw unstructured or semi-structured document text.

Supports:
- Colon/dash/pipe-separated key-value lines (e.g. "Vendor Name: ABC Corp")
- Tab-separated table rows from PDF extraction (e.g. "Vendor Name\tABC Corp")
- Multi-space separated columns from pdfplumber table extraction
- Mixed formats common in scanned OCR output
"""

import re
from typing import Dict, Any, Optional, List, Tuple


# Universal separator pattern: colon, dash, pipe, equals, tab, or 2+ spaces
# This is used throughout all regex patterns to match ANY key-value delimiter
SEP = r'[\t:\-\|\=]|\s{2,}'


# Category keyword maps for automated business classification
CATEGORY_KEYWORDS = {
    "Information Technology": [
        "software", "cloud", "saas", "cybersecurity", "hardware", "networking",
        "it services", "developer", "artificial intelligence", "tech", "data center",
        "web development", "app development", "systems", "solutions"
    ],
    "Construction & Infrastructure": [
        "construction", "builder", "civil", "infrastructure", "cement", "concrete",
        "contractor", "architect", "engineering works", "excavation", "steel structures",
        "building materials", "heavy equipment"
    ],
    "Manufacturing & Industrial": [
        "manufacturing", "fabrication", "machinery", "industrial", "automotive",
        "plastics", "metals", "tools", "foundry", "assembly", "textiles", "chemicals",
        "production", "precision engineering"
    ],
    "Logistics & Supply Chain": [
        "logistics", "freight", "transport", "warehousing", "courier", "shipping",
        "cargo", "distribution", "fleet", "supply chain", "forwarding", "express"
    ],
    "Healthcare & Pharmaceuticals": [
        "healthcare", "hospital", "pharma", "pharmaceutical", "medical devices",
        "diagnostics", "surgical", "biotech", "clinical", "medicines", "drugs"
    ],
    "Consulting & Professional Services": [
        "consulting", "advisory", "audit", "legal", "financial services", "staffing",
        "recruitment", "taxation", "management consulting", "corporate solutions"
    ],
    "Facilities & Office Supplies": [
        "facility management", "security services", "housekeeping", "catering",
        "office supplies", "stationery", "furniture", "maintenance", "janitorial"
    ]
}

# Mapping of normalized key names to canonical field names
KV_KEY_MAP = {
    "vendor name": "Vendor Name",
    "company name": "Vendor Name",
    "supplier name": "Vendor Name",
    "business name": "Vendor Name",
    "entity name": "Vendor Name",
    "name of vendor": "Vendor Name",
    "name of company": "Vendor Name",
    "name of firm": "Vendor Name",
    "name of supplier": "Vendor Name",
    "gstin": "GSTIN",
    "gst no": "GSTIN",
    "gst no.": "GSTIN",
    "gst number": "GSTIN",
    "gst": "GSTIN",
    "pan": "PAN",
    "pan no": "PAN",
    "pan no.": "PAN",
    "pan number": "PAN",
    "permanent account number": "PAN",
    "address": "Address",
    "registered address": "Address",
    "office address": "Address",
    "vendor address": "Address",
    "plant address": "Address",
    "location": "Address",
    "contact person": "Contact Person",
    "representative": "Contact Person",
    "authorized signatory": "Contact Person",
    "contact name": "Contact Person",
    "attention": "Contact Person",
    "attn": "Contact Person",
    "phone": "Phone",
    "mobile": "Phone",
    "contact": "Phone",
    "tel": "Phone",
    "telephone": "Phone",
    "cell": "Phone",
    "phone no": "Phone",
    "phone no.": "Phone",
    "mobile no": "Phone",
    "mobile no.": "Phone",
    "contact no": "Phone",
    "contact no.": "Phone",
    "email": "Email",
    "e-mail": "Email",
    "email address": "Email",
    "mail": "Email",
    "business category": "Business Category",
    "category": "Business Category",
    "industry": "Business Category",
    "sector": "Business Category",
    "nature of business": "Business Category",
    "domain": "Business Category",
    "bank name": "Bank Name",
    "bank": "Bank Name",
    "beneficiary bank": "Bank Name",
    "account number": "Account Number",
    "account no": "Account Number",
    "account no.": "Account Number",
    "a/c no": "Account Number",
    "a/c no.": "Account Number",
    "a/c number": "Account Number",
    "bank a/c": "Account Number",
    "ifsc code": "IFSC Code",
    "ifsc": "IFSC Code",
    "rtgs/neft ifsc": "IFSC Code",
}


def clean_extracted_value(val: Optional[str]) -> str:
    """Cleans up leading/trailing punctuation and excess whitespace."""
    if not val:
        return "Not available"
    cleaned = val.strip().strip(":").strip("-").strip("|").strip("=").strip()
    # Remove leading tab or multiple spaces
    cleaned = re.sub(r'^\s+', '', cleaned)
    return cleaned if cleaned else "Not available"


def _parse_table_kv(text: str) -> Dict[str, str]:
    """
    Pre-parses structured table/KV text where fields and values are separated
    by tabs, multiple spaces, colons, pipes, or other common delimiters.
    
    This catches the very common PDF table extraction format:
        Vendor Name    ABC Technologies Pvt Ltd
        GSTIN          27ABCDE1234F1Z5
    
    Returns a dict mapping canonical field names to extracted values.
    """
    kv_results = {}
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    
    for line in lines:
        # Try tab split first (most common in PDF table extraction)
        if "\t" in line:
            parts = line.split("\t", 1)
            if len(parts) == 2:
                key = parts[0].strip().lower()
                val = parts[1].strip()
                canonical = KV_KEY_MAP.get(key)
                if canonical and val:
                    kv_results[canonical] = val
                    continue
        
        # Try colon-separated (standard key: value)
        colon_match = re.match(r'^([^:]{2,40})\s*:\s*(.+)$', line)
        if colon_match:
            key = colon_match.group(1).strip().lower()
            val = colon_match.group(2).strip()
            canonical = KV_KEY_MAP.get(key)
            if canonical and val:
                kv_results[canonical] = val
                continue
        
        # Try multi-space separated (2+ spaces between key and value)
        space_match = re.match(r'^([A-Za-z/\s]{2,40}?)\s{2,}(.+)$', line)
        if space_match:
            key = space_match.group(1).strip().lower()
            val = space_match.group(2).strip()
            canonical = KV_KEY_MAP.get(key)
            if canonical and val:
                kv_results[canonical] = val
                continue
    
    return kv_results


def extract_vendor_name(text: str, table_kv: Dict[str, str] = None) -> str:
    """Extracts the vendor/company name from labeled lines or top header."""
    # Priority 1: Table KV pre-parse result
    if table_kv and table_kv.get("Vendor Name"):
        return table_kv["Vendor Name"]
    
    # Priority 2: Labeled company/vendor name with flexible separators
    patterns = [
        r"(?:Vendor\s*Name|Company\s*Name|Supplier\s*Name|Business\s*Name|Entity\s*Name)\s*(?:" + SEP + r")\s*([^\n\r]+)",
        r"(?:M/s\.?|Messrs\.?)\s*([^\n\r,]+)",
        r"(?:Name\s*of\s*(?:the\s*)?(?:Vendor|Company|Firm|Supplier))\s*(?:" + SEP + r")\s*([^\n\r]+)",
        r"^(?:Company|Vendor)\s*(?:" + SEP + r")\s*([^\n\r]+)"
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            cand = clean_extracted_value(match.group(1))
            # Basic cleanup if trailing labels captured
            cand = re.split(r"(?:GSTIN|PAN|Address|Phone|Email|Date)", cand, flags=re.IGNORECASE)[0].strip()
            if len(cand) >= 2:
                return cand

    # Priority 3: First non-empty header line before metadata
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    for line in lines[:5]:
        # Skip header/title lines and table header rows
        if re.search(r"(?:Invoice|Registration|Document|Form|GST|PAN|Tax|Date|Page|Government|^Field\b|Vendor\s*Information)", line, re.IGNORECASE):
            continue
        if len(line) > 3 and not line.isdigit():
            return line
                
    return "Not available"


def extract_gstin(text: str, table_kv: Dict[str, str] = None) -> str:
    """Extracts 15-character Indian GSTIN."""
    # Priority 1: Table KV pre-parse
    if table_kv and table_kv.get("GSTIN"):
        cand = table_kv["GSTIN"].strip().upper()
        if re.match(r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$', cand):
            return cand
    
    # Priority 2: Labeled GSTIN with flexible separator
    labeled_pattern = r"(?:GSTIN|GST\s*No\.?|GST\s*Number|GST)\s*(?:" + SEP + r")?\s*([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1})"
    match = re.search(labeled_pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).upper()

    # Priority 3: Standalone 15-character GSTIN regex
    standalone_pattern = r"\b([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1})\b"
    match = re.search(standalone_pattern, text)
    if match:
        return match.group(1).upper()

    return "Not available"


def extract_pan(text: str, gstin: Optional[str] = None, table_kv: Dict[str, str] = None) -> str:
    """Extracts 10-character Indian PAN or derives from valid GSTIN."""
    # Priority 1: Table KV pre-parse
    if table_kv and table_kv.get("PAN"):
        cand = table_kv["PAN"].strip().upper()
        if re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', cand):
            return cand
    
    # Priority 2: Labeled PAN with flexible separator
    labeled_pattern = r"(?:PAN|PAN\s*No\.?|PAN\s*Number|Permanent\s*Account\s*Number)\s*(?:" + SEP + r")?\s*([A-Z]{5}[0-9]{4}[A-Z]{1})"
    match = re.search(labeled_pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).upper()

    # Priority 3: Standalone PAN regex
    standalone_pattern = r"\b([A-Z]{5}[0-9]{4}[A-Z]{1})\b"
    for match in re.finditer(standalone_pattern, text):
        pan_cand = match.group(1).upper()
        # Avoid matching random uppercase word strings if possible
        if not pan_cand.startswith("GSTIN") and not pan_cand.startswith("TOTAL"):
            return pan_cand

    # Priority 4: Derive from GSTIN if valid (characters 2 to 12)
    if gstin and gstin != "Not available" and len(gstin) == 15:
        derived = gstin[2:12].upper()
        if re.match(r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$", derived):
            return derived

    return "Not available"


def extract_email(text: str, table_kv: Dict[str, str] = None) -> str:
    """Extracts email address."""
    # Priority 1: Table KV pre-parse
    if table_kv and table_kv.get("Email"):
        cand = table_kv["Email"].strip().lower()
        if re.match(r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$', cand):
            return cand
    
    # Priority 2: Labeled email with flexible separator
    labeled_pattern = r"(?:Email|E-mail|Email\s*Address|Mail)\s*(?:" + SEP + r")?\s*([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})"
    match = re.search(labeled_pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).lower().strip()

    # Priority 3: Standalone email
    standalone_pattern = r"\b([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})\b"
    match = re.search(standalone_pattern, text)
    if match:
        return match.group(1).lower().strip()

    return "Not available"


def extract_phone(text: str, table_kv: Dict[str, str] = None) -> str:
    """Extracts 10-digit Indian phone/mobile number with optional prefix."""
    # Priority 1: Table KV pre-parse
    if table_kv and table_kv.get("Phone"):
        raw = table_kv["Phone"].strip()
        digits_only = re.sub(r"\D", "", raw)
        if len(digits_only) == 10:
            return digits_only
        elif len(digits_only) == 12 and digits_only.startswith("91"):
            return digits_only[2:]
        elif len(digits_only) == 11 and digits_only.startswith("0"):
            return digits_only[1:]
        # Return raw if it at least contains digits
        if digits_only:
            return raw
    
    # Priority 2: Labeled Phone with flexible separator
    # Allow digits with spaces/dashes inside the phone number (e.g. +91 98765 43210)
    labeled_pattern = r"(?:Phone|Mobile|Contact|Tel|Telephone|Cell)\s*(?:No\.?|Number)?\s*(?:" + SEP + r")?\s*((?:\+91[\-\s]?)?[\d\s\-]{10,15})"
    match = re.search(labeled_pattern, text, re.IGNORECASE)
    if match:
        raw_phone = match.group(1).strip()
        # Normalize digits
        digits_only = re.sub(r"\D", "", raw_phone)
        if len(digits_only) == 10:
            return digits_only
        elif len(digits_only) == 12 and digits_only.startswith("91"):
            return digits_only[2:]
        elif len(digits_only) == 11 and digits_only.startswith("0"):
            return digits_only[1:]
        return raw_phone

    # Priority 3: Standalone 10 digit Indian mobile (with optional +91/0 prefix and spaces)
    standalone_pattern = r"(?:\+91[\s\-]?|0[\s\-]?)?([6-9]\d[\s\-]?\d{3,4}[\s\-]?\d{4,5})"
    match = re.search(standalone_pattern, text)
    if match:
        digits = re.sub(r"\D", "", match.group(1))
        if len(digits) == 10:
            return digits

    return "Not available"


def extract_contact_person(text: str, table_kv: Dict[str, str] = None) -> str:
    """Extracts Contact Person or Representative name."""
    # Priority 1: Table KV pre-parse
    if table_kv and table_kv.get("Contact Person"):
        cand = table_kv["Contact Person"].strip()
        if len(cand) > 2:
            return cand
    
    # Priority 2: Labeled patterns with flexible separators
    patterns = [
        r"(?:Contact\s*Person|Representative|Authorized\s*Signatory|Contact\s*Name|Officer|Director)\s*(?:" + SEP + r")\s*([^\n\r,]+)",
        r"(?:Attention|Attn|Kind\s*Attn)\s*(?:" + SEP + r")\s*([^\n\r,]+)"
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            cand = clean_extracted_value(match.group(1))
            cand = re.split(r"(?:Phone|Email|Designation|Address|Date)", cand, flags=re.IGNORECASE)[0].strip()
            if len(cand) > 2:
                return cand
    return "Not available"


def extract_address(text: str, table_kv: Dict[str, str] = None) -> str:
    """Extracts physical or registered address."""
    # Priority 1: Table KV pre-parse
    if table_kv and table_kv.get("Address"):
        cand = table_kv["Address"].strip()
        if len(cand) > 5:
            return cand
    
    # Priority 2: Labeled patterns with flexible separators
    patterns = [
        r"(?:Registered\s*Address|Office\s*Address|Vendor\s*Address|Address|Location|Plant\s*Address)\s*(?:" + SEP + r")\s*([^\n\r]+(?:\n[^\n\r]+){0,3})",
        r"(?:Address)\s*(?:" + SEP + r")\s*([^\n\r]+)"
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            cand = match.group(1).strip()
            # Stop if hits other field markers
            cand_clean = re.split(r"(?:GSTIN|PAN|Bank|Account|IFSC|Phone|Email|Contact)", cand, flags=re.IGNORECASE)[0]
            # Replace multiple linebreaks with single comma
            cand_clean = ", ".join([line.strip() for line in cand_clean.split("\n") if line.strip()])
            if len(cand_clean) > 5:
                return cand_clean

    return "Not available"


def extract_business_category(text: str, table_kv: Dict[str, str] = None) -> str:
    """Extracts or classifies the business category based on text heuristics."""
    # Priority 1: Table KV pre-parse
    if table_kv and table_kv.get("Business Category"):
        cand = table_kv["Business Category"].strip()
        if len(cand) > 2:
            return cand
    
    # Priority 2: Explicit label with flexible separator
    labeled_pattern = r"(?:Business\s*Category|Category|Industry|Sector|Nature\s*of\s*Business|Domain)\s*(?:" + SEP + r")\s*([^\n\r,]+)"
    match = re.search(labeled_pattern, text, re.IGNORECASE)
    if match:
        cand = clean_extracted_value(match.group(1))
        if len(cand) > 2:
            return cand

    # Priority 3: Keyword scoring across predefined categories
    text_lower = text.lower()
    best_cat = "General Services"
    max_matches = 0

    for category, keywords in CATEGORY_KEYWORDS.items():
        matches = sum(1 for kw in keywords if kw in text_lower)
        if matches > max_matches:
            max_matches = matches
            best_cat = category

    return best_cat if max_matches > 0 else "General Services"


def extract_bank_details(text: str, table_kv: Dict[str, str] = None) -> Tuple[str, str, str]:
    """
    Extracts Bank Name, Account Number, and IFSC code.
    Returns (bank_name, account_number, ifsc_code).
    """
    bank_name = "Not available"
    account_number = "Not available"
    ifsc_code = "Not available"

    # Priority 1: Table KV pre-parse
    if table_kv:
        if table_kv.get("Bank Name"):
            bn = table_kv["Bank Name"].strip()
            if len(bn) > 2:
                bank_name = bn
        if table_kv.get("Account Number"):
            an = re.sub(r"\D", "", table_kv["Account Number"].strip())
            if len(an) >= 9:
                account_number = an
        if table_kv.get("IFSC Code"):
            ic = table_kv["IFSC Code"].strip().upper()
            if re.match(r'^[A-Z]{4}0[A-Z0-9]{6}$', ic):
                ifsc_code = ic

    # Only fall back to regex if table KV didn't populate all fields
    
    # Bank Name
    if bank_name == "Not available":
        bank_pattern = r"(?:Bank\s*Name|Bank|Beneficiary\s*Bank)\s*(?:" + SEP + r")\s*([^\n\r,]+)"
        match = re.search(bank_pattern, text, re.IGNORECASE)
        if match:
            bank_name = clean_extracted_value(match.group(1))
            bank_name = re.split(r"(?:Account|A/c|IFSC|Branch|MICR)", bank_name, flags=re.IGNORECASE)[0].strip()

    # Account Number
    if account_number == "Not available":
        acc_patterns = [
            r"(?:Account\s*No\.?|Account\s*Number|A/C\s*No\.?|A/c\s*Number|Bank\s*A/c)\s*(?:" + SEP + r")?\s*([0-9]{9,18})",
            r"\b([0-9]{9,18})\b"
        ]
        for pattern in acc_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                cand = match.group(1).strip()
                if len(cand) >= 9 and not cand.startswith("1900") and not cand.startswith("202"):
                    account_number = cand
                    break

    # IFSC Code
    if ifsc_code == "Not available":
        ifsc_pattern = r"(?:IFSC|IFSC\s*Code|RTGS/NEFT\s*IFSC)\s*(?:" + SEP + r")?\s*([A-Z]{4}0[A-Z0-9]{6})"
        match = re.search(ifsc_pattern, text, re.IGNORECASE)
        if match:
            ifsc_code = match.group(1).upper().strip()
        else:
            standalone_ifsc = re.search(r"\b([A-Z]{4}0[A-Z0-9]{6})\b", text)
            if standalone_ifsc:
                ifsc_code = standalone_ifsc.group(1).upper().strip()

    return bank_name, account_number, ifsc_code


def extract_vendor_details(text: str) -> Dict[str, str]:
    """
    Main extraction pipeline: parses raw text and extracts all target vendor fields.
    
    Uses a two-phase approach:
    1. Table-aware KV pre-parser: catches structured table/tab/multi-space data
    2. Regex fallback: catches unstructured or partially labeled text
    
    Returns standard dictionary:
    - Vendor Name
    - GSTIN
    - PAN
    - Address
    - Contact Person
    - Phone
    - Email
    - Business Category
    - Bank Name
    - Account Number
    - IFSC Code
    """
    # Phase 1: Pre-parse any table/KV structured data
    table_kv = _parse_table_kv(text)
    
    # Phase 2: Extract each field with table_kv as priority override
    gstin = extract_gstin(text, table_kv=table_kv)
    pan = extract_pan(text, gstin=gstin, table_kv=table_kv)
    vendor_name = extract_vendor_name(text, table_kv=table_kv)
    email = extract_email(text, table_kv=table_kv)
    phone = extract_phone(text, table_kv=table_kv)
    contact_person = extract_contact_person(text, table_kv=table_kv)
    address = extract_address(text, table_kv=table_kv)
    category = extract_business_category(text, table_kv=table_kv)
    bank_name, account_num, ifsc = extract_bank_details(text, table_kv=table_kv)

    return {
        "Vendor Name": vendor_name,
        "GSTIN": gstin,
        "PAN": pan,
        "Address": address,
        "Contact Person": contact_person,
        "Phone": phone,
        "Email": email,
        "Business Category": category,
        "Bank Name": bank_name,
        "Account Number": account_num,
        "IFSC Code": ifsc
    }
