"""
GenVendorAI Vendor Intelligence Chatbot Module
Implements Retrieval-Augmented Generation (RAG) and conversational AI over
the Vendor Master Database, FAISS vector store, compliance rules, and risk assessments.
Works 100% offline and locally out-of-the-box.
"""

import os
import re
import json
from typing import Dict, Any, List, Optional
from database.database import (
    get_all_vendors, get_vendor_by_id, get_vendor_by_gstin,
    get_vendor_stats, get_latest_assessment
)
from ai.semantic_search import semantic_search_vendors


class VendorIntelligenceChatbot:
    """
    Conversational AI Assistant for GenVendorAI.
    Combines intent detection, entity extraction, FAISS vector retrieval,
    and structured context synthesis for procurement intelligence.
    """

    def __init__(self):
        self.system_name = "GenVendorAI Copilot"

    def process_message(self, user_message: str, history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Main entry point: processes user query and returns structured response.
        
        Returns:
            dict containing:
                - 'reply': Markdown formatted response string
                - 'sources': List of referenced vendor entities
                - 'suggested_actions': List of quick follow-up prompt chips
        """
        msg = user_message.strip()
        if not msg:
            return {
                "reply": "Please enter a question or query regarding your vendor master data, compliance status, or risk assessments.",
                "sources": [],
                "suggested_actions": ["Show database overview", "Find low-risk IT suppliers", "Show high-risk watchlist"]
            }

        msg_lower = msg.lower()

        # Intent 1: Greetings & System Help
        if re.search(r"\b(hello|hi|hey|greetings|who are you|what can you do|help)\b", msg_lower) and len(msg_lower.split()) <= 5:
            return self._handle_greeting()

        # Intent 2: Master Database Stats / Overview
        if re.search(r"\b(stats|statistics|overview|how many|total vendors|approval rate|summary|count)\b", msg_lower):
            return self._handle_stats_inquiry()

        # Intent 3: High-Risk / Rejected / Watchlist Inquiry
        if re.search(r"\b(high risk|watchlist|flagged|rejected|review|violations|defaulters|risky|fraud)\b", msg_lower):
            return self._handle_watchlist_inquiry(msg_lower)

        # Intent 4: Specific Vendor Query (ByName or GSTIN/PAN)
        vendor_match = self._find_specific_vendor_in_query(msg)
        if vendor_match:
            return self._handle_specific_vendor_inquiry(vendor_match)

        # Intent 5: Category Specific Query (IT, Construction, Manufacturing, Logistics, Healthcare, Consulting)
        cat_match = self._detect_category_in_query(msg_lower)
        if cat_match and not re.search(r"\b(compare|all)\b", msg_lower):
            return self._handle_category_inquiry(cat_match, msg)

        # Intent 6: Compliance / Validation Rules Explanation
        if re.search(r"\b(gstin rule|pan rule|ifsc rule|how is risk calculated|scoring formula|penalty|validation rule)\b", msg_lower):
            return self._handle_compliance_rules_inquiry(msg_lower)

        # Intent 7: Default -> Dense Semantic Search & Contextual RAG Synthesis
        return self._handle_semantic_rag_search(msg)

    def _handle_greeting(self) -> Dict[str, Any]:
        reply = (
            "👋 **Hello! I am your GenVendorAI Procurement Intelligence Copilot.**\n\n"
            "I can assist you with real-time intelligence on your vendor master registry, compliance audits, and AI risk evaluations.\n\n"
            "**Here are some things you can ask me:**\n"
            "- 📊 *\"Give me an overview of all master vendors\"*\n"
            "- 🏢 *\"Tell me about Zenith Cloud Technologies\"*\n"
            "- ⚠️ *\"Which vendors are flagged on the high-risk watchlist?\"*\n"
            "- 🔎 *\"Find civil construction and infrastructure contractors in Maharashtra\"*\n"
            "- 🏦 *\"What are the bank details and GSTIN of BuildCraft Infrastructure?\"*\n"
            "- ⚖️ *\"How is statutory compliance and risk score calculated?\"*"
        )
        return {
            "reply": reply,
            "sources": [],
            "suggested_actions": [
                "Show database overview",
                "Show high-risk watchlist",
                "Find IT suppliers in Pune",
                "How is risk calculated?"
            ]
        }

    def _handle_stats_inquiry(self) -> Dict[str, Any]:
        stats = get_vendor_stats()
        total = stats.get("total_vendors", 0)
        app = stats.get("approved", 0)
        rev = stats.get("under_review", 0)
        rej = stats.get("rejected", 0)
        valid = stats.get("valid_records", 0)
        
        app_rate = f"{(app / total * 100):.1f}%" if total > 0 else "0%"
        valid_rate = f"{(valid / total * 100):.1f}%" if total > 0 else "0%"

        reply = (
            f"### 📊 Master Vendor Database Executive Summary\n\n"
            f"Here is the real-time operational status of your master registry:\n\n"
            f"| Metric | Count | Percentage / Status |\n"
            f"|---|---|---|\n"
            f"| **Total Master Records** | **{total}** | Active MDM Registry |\n"
            f"| 🟢 **Approved Vendors** | **{app}** | {app_rate} approval rate |\n"
            f"| 🟡 **Under Review** | **{rev}** | Active compliance backlog |\n"
            f"| 🔴 **Rejected Entries** | **{rej}** | High-risk / fraud blocked |\n"
            f"| ✅ **Valid Statutory Formats** | **{valid}** | {valid_rate} format integrity |\n\n"
            f"💡 *Would you like to inspect high-risk entities, download the executive summary PDF, or query a specific domain?*"
        )
        return {
            "reply": reply,
            "sources": [],
            "suggested_actions": ["Show high-risk watchlist", "List all approved vendors", "Download Executive Summary PDF"]
        }

    def _handle_watchlist_inquiry(self, msg_lower: str) -> Dict[str, Any]:
        vendors = get_all_vendors()
        flagged = []

        for v in vendors:
            r_level = v.get("risk_level", "LOW")
            rec = v.get("recommendation", "APPROVE")
            r_score = v.get("risk_score", 0)
            if r_level in ("HIGH", "MEDIUM") or rec in ("REJECT", "REVIEW") or r_score >= 25:
                flagged.append(v)

        if not flagged:
            return {
                "reply": "✅ **Good news!** No vendors are currently flagged on the active compliance watchlist. All onboarded vendors meet statutory criteria with low risk scores.",
                "sources": [],
                "suggested_actions": ["Show database overview", "Find IT suppliers", "Run document processing"]
            }

        reply = f"### ⚠️ Active Compliance & Risk Watchlist ({len(flagged)} Vendors Flagged)\n\n"
        reply += "The following vendors require compliance review or have been blocked due to risk exceptions:\n\n"

        sources = []
        for v in flagged:
            vid = v.get("id")
            vname = v.get("vendor_name", "Unknown")
            cat = v.get("business_category", "N/A")
            gst = v.get("gstin", "N/A")
            score = v.get("risk_score", 0)
            tier = v.get("risk_level", "MEDIUM")
            rec = v.get("recommendation", "REVIEW")
            badge = "🔴 REJECT" if rec == "REJECT" else "🟡 REVIEW"
            sources.append(vname)

            reply += (
                f"• **{vname}** (`#{vid}`) — **{badge}** (Risk: **{score}/100**, {tier})\n"
                f"  - Category: *{cat}* | GSTIN: `{gst}`\n"
                f"  - *Reason:* Validation: `{v.get('validation_status', 'VALID')}`, Duplicate Flag: `{v.get('duplicate_status', 'UNIQUE')}`\n\n"
            )

        reply += "👉 *You can inspect full details or download audit dossiers for any flagged vendor.*"
        return {
            "reply": reply,
            "sources": sources,
            "suggested_actions": [f"Tell me about {sources[0]}" if sources else "Show database overview", "Download Executive Summary PDF"]
        }

    def _handle_specific_vendor_inquiry(self, vendor: Dict[str, Any]) -> Dict[str, Any]:
        vid = vendor.get("id")
        vname = vendor.get("vendor_name", "Unknown Vendor")
        gstin = vendor.get("gstin", "N/A")
        pan = vendor.get("pan", "N/A")
        cat = vendor.get("business_category", "N/A")
        addr = vendor.get("address", "N/A")
        contact = vendor.get("contact_person", "N/A")
        phone = vendor.get("phone", "N/A")
        email = vendor.get("email", "N/A")
        bank = vendor.get("bank_name", "N/A")
        acc = vendor.get("account_number", "N/A")
        ifsc = vendor.get("ifsc_code", "N/A")
        score = vendor.get("risk_score", 0)
        tier = vendor.get("risk_level", "LOW")
        rec = vendor.get("recommendation", "APPROVE")
        rec_badge = "🟢 APPROVE" if rec == "APPROVE" else ("🟡 REVIEW" if rec == "REVIEW" else "🔴 REJECT")

        assessment = get_latest_assessment(vid) if vid else None
        summary = (assessment.get("summary") if assessment else None) or "Standard automated assessment completed."

        pos_items = []
        risk_items = []
        if assessment:
            pos = assessment.get("positive_findings", [])
            if isinstance(pos, str):
                try: pos = json.loads(pos)
                except: pos = [pos]
            pos_items = pos if isinstance(pos, list) else []

            rf = assessment.get("risk_factors", [])
            if isinstance(rf, str):
                try: rf = json.loads(rf)
                except: rf = [rf]
            risk_items = rf if isinstance(rf, list) else []

        pos_str = "\n".join([f"  - ✅ {p}" for p in pos_items[:3]]) if pos_items else "  - ✅ Standard compliance verified."
        risk_str = "\n".join([f"  - ⚠️ {r}" for r in risk_items[:3]]) if risk_items else "  - ✅ No critical risk factors identified."

        reply = (
            f"### 📋 Vendor Intelligence Profile: {vname}\n\n"
            f"**Master Record:** `#{vid}` | **Decision Recommendation:** **{rec_badge}** | **Risk Score:** **{score}/100 ({tier})**\n\n"
            f"| Attribute | Verified Value |\n"
            f"|---|---|\n"
            f"| **Business Domain** | {cat} |\n"
            f"| **Statutory GSTIN** | `{gstin}` |\n"
            f"| **Income Tax PAN** | `{pan}` |\n"
            f"| **Registered Address** | {addr} |\n"
            f"| **Contact Signatory** | {contact} ({phone} / {email}) |\n"
            f"| **Banking Coordinates** | {bank} • A/C: `{acc}` • IFSC: `{ifsc}` |\n\n"
            f"**📝 AI Assessment Summary:**\n"
            f"> {summary}\n\n"
            f"**Verified Strengths:**\n{pos_str}\n\n"
            f"**Risk Exceptions / Notes:**\n{risk_str}\n"
        )

        return {
            "reply": reply,
            "sources": [vname],
            "suggested_actions": [f"Download PDF Report for #{vid}", "Show all vendors in " + cat, "Show high-risk watchlist"]
        }

    def _handle_category_inquiry(self, category: str, original_query: str) -> Dict[str, Any]:
        vendors = get_all_vendors()
        matches = [v for v in vendors if category.lower() in v.get("business_category", "").lower()]

        if not matches:
            return {
                "reply": f"No vendors are currently registered under the **{category}** category in the master database. You can onboard new suppliers via the **Vendor Processing** tab.",
                "sources": [],
                "suggested_actions": ["Show database overview", "Find IT suppliers", "Find construction suppliers"]
            }

        reply = f"### 🏢 Registered Vendors in **{category}** ({len(matches)} Found)\n\n"
        sources = []
        for v in matches:
            vname = v.get("vendor_name", "Unknown")
            sources.append(vname)
            rec = v.get("recommendation", "APPROVE")
            badge = "🟢" if rec == "APPROVE" else ("🟡" if rec == "REVIEW" else "🔴")
            reply += (
                f"• **{vname}** (`#{v.get('id')}`) {badge} — Risk: **{v.get('risk_score')}/100**\n"
                f"  - GSTIN: `{v.get('gstin')}` | PAN: `{v.get('pan')}` | Location: *{v.get('address')}*\n"
                f"  - Bank: *{v.get('bank_name')}* (`{v.get('ifsc_code')}`)\n\n"
            )

        return {
            "reply": reply,
            "sources": sources,
            "suggested_actions": [f"Tell me about {sources[0]}" if sources else "Show database overview", "Compare category risk scores"]
        }

    def _handle_compliance_rules_inquiry(self, msg_lower: str) -> Dict[str, Any]:
        reply = (
            "### ⚖️ GenVendorAI Statutory Regulatory Rules & Scoring Model\n\n"
            "GenVendorAI enforces deterministic Indian statutory compliance and transparent multi-factor risk scoring:\n\n"
            "#### 1. Statutory Validation Specifications:\n"
            "- **GSTIN (15 chars):** Verifies state code (01–38, 97, 99), 14th char `'Z'`, and pattern `^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$`.\n"
            "- **PAN (10 chars):** Verifies structure `^[A-Z]{5}[0-9]{4}[A-Z]{1}$` and decodes the 4th character (`C`=Company, `P`=Individual, `F`=Firm, `D`=Enterprise/Demo).\n"
            "- **Cross-Consistency:** Validates that characters 3–12 of GSTIN strictly match the submitted PAN.\n"
            "- **IFSC Code (11 chars):** Validates RBI syntax `^[A-Z]{4}0[A-Z0-9]{6}$` (5th char mandatory digit `'0'`).\n\n"
            "#### 2. Risk Penalty Matrix (0–100 Scale):\n"
            "| Violation / Risk Factor | Penalty Points |\n"
            "|---|---|\n"
            "| Missing / Invalid GSTIN | **+25 points** |\n"
            "| GSTIN–PAN Mismatch | **+25 points** |\n"
            "| Missing / Invalid PAN | **+20 points** |\n"
            "| Banking Failure (A/C or IFSC) | **+25 points** |\n"
            "| Exact Database Duplicate | **+40 points** |\n"
            "| Semantic Near-Duplicate (>=85%) | **+15 points** |\n\n"
            "#### 3. Decision Thresholds:\n"
            "- 🟢 **APPROVE:** Risk Score **0 – 25** (LOW RISK)\n"
            "- 🟡 **REVIEW:** Risk Score **26 – 50** (MEDIUM RISK)\n"
            "- 🔴 **REJECT:** Risk Score **> 50** (HIGH RISK)"
        )
        return {
            "reply": reply,
            "sources": [],
            "suggested_actions": ["Show high-risk watchlist", "Show database overview", "Find IT suppliers"]
        }

    def _handle_semantic_rag_search(self, query: str) -> Dict[str, Any]:
        results = semantic_search_vendors(query=query, top_k=4, min_similarity=0.20)

        if not results:
            return {
                "reply": (
                    f"I searched the master vendor database and vector knowledge base for *\"{query}\"*, but found no matching records meeting the semantic similarity threshold.\n\n"
                    "💡 *Try refining your terms, asking for a broader category (e.g. IT, Construction, Logistics), or querying by vendor name or location.*"
                ),
                "sources": [],
                "suggested_actions": ["Show database overview", "List all IT suppliers", "Show high-risk watchlist"]
            }

        reply = f"### 🔎 Semantic Retrieval Results for: *\"{query}\"*\n\n"
        reply += f"I analyzed your query in the 384-dimensional latent space (Sentence-BERT + FAISS) and retrieved the top matching vendor profiles:\n\n"

        sources = []
        for r in results:
            vname = r.get("Vendor Name", "Unknown")
            cat = r.get("Business Category", "N/A")
            addr = r.get("Address", "N/A")
            sim_pct = r.get("Similarity Pct", "0%")
            score = r.get("Risk Score", 0)
            tier = r.get("Risk Level", "LOW")
            rec = r.get("Recommendation", "APPROVE")
            badge = "🟢 APPROVE" if rec == "APPROVE" else ("🟡 REVIEW" if rec == "REVIEW" else "🔴 REJECT")
            sources.append(vname)

            reply += (
                f"#### • {vname} (Match: **{sim_pct}**) — {badge}\n"
                f"- **Category:** *{cat}* | **Location:** *{addr}*\n"
                f"- **GSTIN:** `{r.get('GSTIN')}` | **PAN:** `{r.get('PAN')}`\n"
                f"- **Risk Level:** **{score}/100 ({tier})** | **Bank:** *{r.get('Bank Name')}*\n\n"
            )

        reply += "💡 *You can click on any vendor name to view their full master record or download their official PDF dossier.*"
        return {
            "reply": reply,
            "sources": sources,
            "suggested_actions": [f"Tell me about {sources[0]}" if sources else "Show database overview", "Download Executive Summary PDF"]
        }

    def _find_specific_vendor_in_query(self, query: str) -> Optional[Dict[str, Any]]:
        vendors = get_all_vendors()
        q_clean = query.lower()

        # Check by GSTIN or PAN
        for v in vendors:
            gst = (v.get("gstin") or "").lower()
            pan = (v.get("pan") or "").lower()
            if gst and gst in q_clean:
                return v
            if pan and pan in q_clean:
                return v

        # Check by Vendor Name (fuzzy token overlap)
        best_vendor = None
        max_overlap = 0

        for v in vendors:
            vname = v.get("vendor_name", "").lower()
            # Normalize tokens
            tokens = [t for t in re.split(r"\W+", vname) if len(t) > 2 and t not in ("pvt", "ltd", "llp", "private", "limited", "and", "the", "solutions", "services", "technologies", "works")]
            if not tokens:
                tokens = [t for t in re.split(r"\W+", vname) if len(t) > 2]

            matches = sum(1 for t in tokens if t in q_clean)
            if matches > max_overlap and (matches >= 2 or (len(tokens) == 1 and matches == 1)):
                max_overlap = matches
                best_vendor = v

        return best_vendor

    def _detect_category_in_query(self, query_lower: str) -> Optional[str]:
        cat_map = {
            "Information Technology": ["it", "software", "cloud", "saas", "tech", "developer", "app development", "cybersecurity"],
            "Construction & Infrastructure": ["construction", "builder", "civil", "infrastructure", "cement", "engineering works"],
            "Manufacturing & Industrial": ["manufacturing", "fabrication", "machinery", "foundry", "forging", "tools"],
            "Logistics & Supply Chain": ["logistics", "freight", "transport", "cargo", "courier", "warehousing", "shipping"],
            "Healthcare & Pharmaceuticals": ["healthcare", "pharma", "pharmaceutical", "medical", "biotech", "hospital"],
            "Consulting & Professional Services": ["consulting", "advisory", "audit", "legal", "financial services", "taxation"]
        }

        for cat, keywords in cat_map.items():
            for kw in keywords:
                if re.search(r"\b" + re.escape(kw) + r"\b", query_lower):
                    return cat

        return None


# Global Chatbot Singleton
_chatbot_instance = None

def get_chatbot() -> VendorIntelligenceChatbot:
    global _chatbot_instance
    if _chatbot_instance is None:
        _chatbot_instance = VendorIntelligenceChatbot()
    return _chatbot_instance
