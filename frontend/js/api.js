/**
 * GenVendorAI Frontend API Client
 * Connects UI components to FastAPI Backend Endpoints
 */

const API_BASE = window.location.origin;

const API = {
    async getHealth() {
        const res = await fetch(`${API_BASE}/api/health`);
        return res.json();
    },

    async uploadDocument(formData) {
        const res = await fetch(`${API_BASE}/api/process/upload`, {
            method: 'POST',
            body: formData
        });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Upload and processing failed.');
        }
        return res.json();
    },

    async getSamples() {
        const res = await fetch(`${API_BASE}/api/process/samples`);
        return res.json();
    },

    async processSample(filename) {
        const res = await fetch(`${API_BASE}/api/process/sample/${encodeURIComponent(filename)}`, {
            method: 'POST'
        });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Sample processing failed.');
        }
        return res.json();
    },

    async getVendors(params = {}) {
        const query = new URLSearchParams(params).toString();
        const res = await fetch(`${API_BASE}/api/vendors?${query}`);
        return res.json();
    },

    async getVendor(id) {
        const res = await fetch(`${API_BASE}/api/vendors/${id}`);
        if (!res.ok) throw new Error('Vendor not found');
        return res.json();
    },

    async deleteVendor(id) {
        const res = await fetch(`${API_BASE}/api/vendors/${id}`, {
            method: 'DELETE'
        });
        return res.json();
    },

    async seedData() {
        const res = await fetch(`${API_BASE}/api/vendors/seed`, {
            method: 'POST'
        });
        return res.json();
    },

    async semanticSearch(payload) {
        const res = await fetch(`${API_BASE}/api/search/semantic`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        return res.json();
    },

    async getStats() {
        const res = await fetch(`${API_BASE}/api/analytics/stats`);
        return res.json();
    },

    async getCharts() {
        const res = await fetch(`${API_BASE}/api/analytics/charts`);
        return res.json();
    },

    async getAuditLogs(eventType = 'All') {
        const res = await fetch(`${API_BASE}/api/audit/logs?event_type=${encodeURIComponent(eventType)}`);
        return res.json();
    },

    async clearAuditLogs() {
        const res = await fetch(`${API_BASE}/api/audit/clear`, {
            method: 'DELETE'
        });
        return res.json();
    },

    getReportPdfUrl(vendorId) {
        return `${API_BASE}/api/reports/${vendorId}/pdf`;
    },

    getExecutiveSummaryPdfUrl() {
        return `${API_BASE}/api/reports/summary/pdf`;
    },

    async getReportHtml(vendorId) {
        const res = await fetch(`${API_BASE}/api/reports/${vendorId}/html`);
        return res.text();
    },

    async sendChatMessage(message, history = []) {
        const res = await fetch(`${API_BASE}/api/chat/message`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message, history })
        });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Chat assistant failed to respond.');
        }
        return res.json();
    },

    async getChatSuggestions() {
        const res = await fetch(`${API_BASE}/api/chat/suggestions`);
        return res.json();
    }
};

window.API = API;
