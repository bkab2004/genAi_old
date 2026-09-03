"""
GenVendorAI Risk Engine Module
Implements an explainable, multi-factor AI risk assessment and decision-support engine for vendor master data.
Computes risk scores (0-100), risk classifications (LOW, MEDIUM, HIGH), and onboarding recommendations (APPROVE, REVIEW, REJECT).
"""

from typing import Dict, Any, List, Optional
from validation.validator import (
    validate_gstin, validate_pan, validate_email, validate_phone,
    validate_ifsc, validate_account_number, validate_vendor_name, validate_address
)


def generate_vendor_risk_assessment(
    vendor_details: Dict[str, Any],
    is_duplicate: bool = False,
    duplicate_reason: Optional[str] = None,
    max_semantic_similarity: float = 0.0,
    most_similar_vendor_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Computes an explainable risk evaluation score, risk category, and procurement decision.
    
    Scoring Model (0 = Lowest Risk, 100 = Maximum Risk):
    - Base: 0
    - Invalid/Missing GSTIN: +25
    - Invalid/Missing PAN: +20
    - GSTIN / PAN Mismatch: +25
    - Missing/Invalid Bank Account: +15
    - Missing/Invalid IFSC: +10
    - Missing/Invalid Email: +10
    - Missing/Invalid Phone: +10
    - Incomplete Name/Address: +15
    - Exact Duplicate Detection: +40
    - High Semantic Similarity (>=85%): +15
    """
    risk_score = 0
    positive_findings = []
    risk_factors = []

    # 1. Vendor Name Evaluation
    vname = vendor_details.get("Vendor Name") or vendor_details.get("vendor_name", "")
    name_ok, name_msg = validate_vendor_name(vname)
    if name_ok:
        positive_findings.append(f"Legal vendor name identified: '{vname}'")
    else:
        risk_score += 15
        risk_factors.append(f"Vendor Name issue: {name_msg}")

    # 2. GSTIN Evaluation
    gstin = vendor_details.get("GSTIN") or vendor_details.get("gstin", "")
    gst_ok, gst_msg = validate_gstin(gstin)
    if gst_ok:
        positive_findings.append(f"Valid 15-character GSTIN: {gst_msg}")
    else:
        risk_score += 25
        risk_factors.append(f"GSTIN compliance failure: {gst_msg}")

    # 3. PAN Evaluation
    pan = vendor_details.get("PAN") or vendor_details.get("pan", "")
    pan_ok, pan_msg = validate_pan(pan)
    if pan_ok:
        positive_findings.append(f"Valid Income Tax PAN: {pan_msg}")
    else:
        risk_score += 20
        risk_factors.append(f"PAN compliance failure: {pan_msg}")

    # 4. GSTIN <-> PAN Consistency
    if gst_ok and pan_ok:
        embedded_pan = gstin.strip().upper()[2:12]
        if embedded_pan != pan.strip().upper():
            risk_score += 25
            risk_factors.append(f"Critical Identifier Mismatch: Embedded GSTIN PAN ({embedded_pan}) != Provided PAN ({pan})")
        else:
            positive_findings.append("Perfect consistency between GSTIN state identifier and PAN registration.")

    # 5. Banking Verification
    bank_name = vendor_details.get("Bank Name") or vendor_details.get("bank_name", "")
    acc_num = vendor_details.get("Account Number") or vendor_details.get("account_number", "")
    ifsc = vendor_details.get("IFSC Code") or vendor_details.get("ifsc_code", "")

    acc_ok, acc_msg = validate_account_number(acc_num)
    ifsc_ok, ifsc_msg = validate_ifsc(ifsc)

    if acc_ok and ifsc_ok:
        b_label = f" ({bank_name})" if bank_name and bank_name != "Not available" else ""
        positive_findings.append(f"Bank details verified{b_label}: Valid Account Number and standard RBI IFSC code.")
    else:
        if not acc_ok:
            risk_score += 15
            risk_factors.append(f"Banking Risk: {acc_msg}")
        if not ifsc_ok:
            risk_score += 10
            risk_factors.append(f"Banking Risk: {ifsc_msg}")

    # 6. Contact Information (Email & Phone)
    email = vendor_details.get("Email") or vendor_details.get("email", "")
    phone = vendor_details.get("Phone") or vendor_details.get("phone", "")

    email_ok, email_msg = validate_email(email)
    phone_ok, phone_msg = validate_phone(phone)

    if email_ok:
        positive_findings.append(f"Corporate communication email verified: {email}")
    else:
        risk_score += 10
        risk_factors.append(f"Contact Verification: {email_msg}")

    if phone_ok:
        positive_findings.append(f"Direct mobile/contact number verified: {phone}")
    else:
        risk_score += 10
        risk_factors.append(f"Contact Verification: {phone_msg}")

    # 7. Address Presence
    addr = vendor_details.get("Address") or vendor_details.get("address", "")
    addr_ok, addr_msg = validate_address(addr)
    if addr_ok:
        positive_findings.append(f"Registered physical address verified: {addr[:60]}...")
    else:
        risk_score += 10
        risk_factors.append(f"Address Verification: {addr_msg}")

    # 8. Exact Duplicate Factor
    if is_duplicate:
        risk_score += 40
        risk_factors.append(f"Duplicate Master Record: Vendor already exists in database matched by {duplicate_reason or 'Identifier'}")

    # 9. Semantic Similarity Factor (Possible split entity or shell vendor)
    if max_semantic_similarity >= 0.85:
        risk_score += 15
        s_name = f" ('{most_similar_vendor_name}')" if most_similar_vendor_name else ""
        risk_factors.append(f"High Semantic Similarity ({max_semantic_similarity:.1%}) with existing registered vendor{s_name}. Potential split entity or shell duplicate.")
    elif max_semantic_similarity >= 0.70:
        s_name = f" ('{most_similar_vendor_name}')" if most_similar_vendor_name else ""
        positive_findings.append(f"Moderate semantic overlap ({max_semantic_similarity:.1%}) observed with peer vendor{s_name} within same industry domain.")

    # Clamp Risk Score to [0, 100]
    risk_score = max(0, min(100, risk_score))

    # Risk Classification
    if risk_score <= 30:
        risk_level = "LOW"
    elif risk_score <= 65:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    # Onboarding Decision Recommendation
    if is_duplicate:
        recommendation = "REJECT"
    elif risk_level == "LOW" and (gst_ok or pan_ok) and name_ok:
        recommendation = "APPROVE"
    elif risk_level == "MEDIUM":
        recommendation = "REVIEW"
    else:
        recommendation = "REJECT"

    # Human-readable summary synthesis
    if recommendation == "APPROVE":
        summary = (
            f"Vendor '{vname}' has successfully cleared statutory validation with a Low Risk profile ({risk_score}/100). "
            f"All critical regulatory identifiers (GSTIN/PAN/Banking) are verified and consistent. Recommended for immediate ERP activation."
        )
    elif recommendation == "REVIEW":
        summary = (
            f"Vendor '{vname}' exhibits a Medium Risk profile ({risk_score}/100). "
            f"While core identity is established, {len(risk_factors)} risk factors were detected requiring human compliance officer verification before ERP onboarding."
        )
    else:
        summary = (
            f"Vendor '{vname}' has been flagged as High Risk ({risk_score}/100) due to critical non-compliance or duplicate records. "
            f"Onboarding rejected to protect enterprise master data integrity and prevent downstream financial exposure."
        )

    return {
        "Risk Score": risk_score,
        "Risk Level": risk_level,
        "Recommendation": recommendation,
        "Positive Findings": positive_findings,
        "Risk Factors": risk_factors,
        "Summary": summary
    }


def generate_vendor_assessment(vendor_details: Dict[str, Any]) -> Dict[str, Any]:
    """Compatibility alias for generate_vendor_risk_assessment."""
    return generate_vendor_risk_assessment(vendor_details)
