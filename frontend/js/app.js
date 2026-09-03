/**
 * GenVendorAI Main Application Logic
 * Single Page Application Controller, Data Visualizations, and Pipeline Execution
 */

// Global State
const State = {
    currentView: 'processing',
    charts: {},
    currentResult: null,
    vendors: []
};

// Toast Notifications
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast border-l-4 ${
        type === 'success' ? 'border-emerald-500 bg-slate-800' :
        type === 'error' ? 'border-rose-500 bg-slate-800' :
        type === 'warning' ? 'border-amber-500 bg-slate-800' : 'border-blue-500 bg-slate-800'
    }`;
    
    const icon = type === 'success' ? '✅' : type === 'error' ? '❌' : type === 'warning' ? '⚠️' : 'ℹ️';
    toast.innerHTML = `<span>${icon}</span><span class="flex-1">${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(10px)';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// Navigation View Switcher
function navigateTo(viewName) {
    State.currentView = viewName;
    
    // Hide all views
    document.querySelectorAll('.view-section').forEach(el => el.classList.add('hidden'));
    
    // Show target view
    const target = document.getElementById(`view-${viewName}`);
    if (target) target.classList.remove('hidden');

    // Update active nav button
    document.querySelectorAll('.nav-btn').forEach(btn => {
        if (btn.dataset.view === viewName) {
            btn.classList.add('bg-blue-600/20', 'text-blue-400', 'border-blue-500/30');
            btn.classList.remove('text-slate-400', 'hover:bg-slate-800/50');
        } else {
            btn.classList.remove('bg-blue-600/20', 'text-blue-400', 'border-blue-500/30');
            btn.classList.add('text-slate-400', 'hover:bg-slate-800/50');
        }
    });

    // View specific loaders
    if (viewName === 'dashboard') loadDashboard();
    if (viewName === 'database') loadDatabase();
    if (viewName === 'audit') loadAuditLogs();
    if (viewName === 'reports') loadReportsView();
    if (viewName === 'risk') loadRiskView();
}

// ============================================================
// PIPELINE & DOCUMENT PROCESSING
// ============================================================

async function initProcessingView() {
    // Load pre-generated samples
    try {
        const data = await API.getSamples();
        const select = document.getElementById('sample-select');
        if (select && data.samples) {
            select.innerHTML = '<option value="">-- Choose Pre-loaded Test Document --</option>';
            data.samples.forEach(s => {
                const opt = document.createElement('option');
                opt.value = s;
                opt.textContent = s;
                select.appendChild(opt);
            });
        }
    } catch (e) {
        console.warn('Samples load failed:', e);
    }

    // Drag & drop setup
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('pdf-file-input');

    if (dropzone && fileInput) {
        dropzone.addEventListener('click', () => fileInput.click());
        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropzone.classList.add('border-blue-500', 'bg-blue-950/20');
        });
        dropzone.addEventListener('dragleave', () => {
            dropzone.classList.remove('border-blue-500', 'bg-blue-950/20');
        });
        dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropzone.classList.remove('border-blue-500', 'bg-blue-950/20');
            if (e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files;
                handleFileSelected(fileInput.files[0]);
            }
        });

        fileInput.addEventListener('change', () => {
            if (fileInput.files.length) {
                handleFileSelected(fileInput.files[0]);
            }
        });
    }

    // Process uploaded file button
    const processUploadBtn = document.getElementById('btn-process-upload');
    if (processUploadBtn) {
        processUploadBtn.addEventListener('click', async () => {
            if (!fileInput.files.length) {
                showToast('Please select a PDF document first.', 'warning');
                return;
            }
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            await executePipeline(formData, true);
        });
    }

    // Process sample button
    const processSampleBtn = document.getElementById('btn-process-sample');
    if (processSampleBtn) {
        processSampleBtn.addEventListener('click', async () => {
            const select = document.getElementById('sample-select');
            if (!select.value) {
                showToast('Please choose a sample document from the dropdown.', 'warning');
                return;
            }
            await executePipeline(select.value, false);
        });
    }
}

function handleFileSelected(file) {
    const label = document.getElementById('selected-file-label');
    if (label) {
        label.textContent = `Selected: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
        label.classList.remove('hidden');
    }
}

async function executePipeline(input, isUpload = true) {
    const statusContainer = document.getElementById('pipeline-status');
    const resultsContainer = document.getElementById('pipeline-results');
    
    statusContainer.classList.remove('hidden');
    resultsContainer.classList.add('hidden');

    // Stepper animation
    const steps = [
        'Document Ingestion & OCR Extraction...',
        'Extracting Structured Attributes...',
        'Validating Indian Regulatory Compliance...',
        'Checking Exact Master Duplicates...',
        'Generating Dense Embeddings & FAISS Vector Matching...',
        'Computing Explainable AI Risk Score...',
        'Final Onboarding Decision & Activation...'
    ];

    let stepIdx = 0;
    const stepLabel = document.getElementById('current-step-label');
    const stepProgress = document.getElementById('pipeline-progress-bar');
    
    const interval = setInterval(() => {
        if (stepIdx < steps.length) {
            stepLabel.textContent = steps[stepIdx];
            stepProgress.style.width = `${((stepIdx + 1) / steps.length) * 100}%`;
            stepIdx++;
        }
    }, 400);

    try {
        let result;
        if (isUpload) {
            result = await API.uploadDocument(input);
        } else {
            result = await API.processSample(input);
        }

        clearInterval(interval);
        stepProgress.style.width = '100%';
        stepLabel.textContent = '✅ Pipeline processing completed successfully!';

        setTimeout(() => {
            statusContainer.classList.add('hidden');
            renderPipelineResults(result);
            showToast('Document processed and assessed successfully!', 'success');
        }, 500);

    } catch (e) {
        clearInterval(interval);
        statusContainer.classList.add('hidden');
        showToast(e.message || 'Processing failed', 'error');
    }
}

function renderPipelineResults(data) {
    const c = document.getElementById('pipeline-results');
    c.classList.remove('hidden');
    State.currentResult = data;

    const v = data.step2_fields;
    const val = data.step3_validation;
    const dup = data.step4_duplicate;
    const sim = data.step5_similarity;
    const risk = data.step6_risk_assessment;
    const dec = data.step7_decision;

    // Decision Badge Banner
    const banner = document.getElementById('decision-banner');
    const recBadge = document.getElementById('decision-badge');
    const recTitle = document.getElementById('decision-title');
    const recDesc = document.getElementById('decision-desc');

    if (dec.recommendation === 'APPROVE') {
        banner.className = 'p-6 rounded-xl border border-emerald-500/30 bg-emerald-950/20';
        recBadge.className = 'px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider bg-emerald-500 text-slate-950';
        recBadge.textContent = '🟢 APPROVED';
        recTitle.textContent = `Vendor Master Record Activated (ID: #${data.vendor_id || 'Active'})`;
        recDesc.textContent = risk.Summary;
    } else if (dec.recommendation === 'REVIEW') {
        banner.className = 'p-6 rounded-xl border border-amber-500/30 bg-amber-950/20';
        recBadge.className = 'px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider bg-amber-500 text-slate-950';
        recBadge.textContent = '🟡 REQUIRES MANUAL REVIEW';
        recTitle.textContent = `Secondary Compliance Review Required (ID: #${data.vendor_id || 'Pending'})`;
        recDesc.textContent = risk.Summary;
    } else {
        banner.className = 'p-6 rounded-xl border border-rose-500/30 bg-rose-950/20';
        recBadge.className = 'px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider bg-rose-500 text-slate-950';
        recBadge.textContent = '🔴 REJECTED';
        recTitle.textContent = dup.is_duplicate ? `Rejected: Duplicate Entity Detected` : `Rejected: Critical Non-Compliance`;
        recDesc.textContent = risk.Summary;
    }

    // Step 1: OCR
    document.getElementById('res-ocr-method').textContent = data.step1_ocr.method;
    document.getElementById('res-ocr-chars').textContent = `${data.step1_ocr.char_count.toLocaleString()} characters`;
    document.getElementById('res-ocr-text').textContent = data.step1_ocr.extracted_text;

    // Step 2: Extracted Fields
    document.getElementById('res-name').textContent = v['Vendor Name'] || 'N/A';
    document.getElementById('res-gstin').textContent = v['GSTIN'] || 'N/A';
    document.getElementById('res-pan').textContent = v['PAN'] || 'N/A';
    document.getElementById('res-category').textContent = v['Business Category'] || 'N/A';
    document.getElementById('res-address').textContent = v['Address'] || 'N/A';
    document.getElementById('res-contact').textContent = v['Contact Person'] || 'N/A';
    document.getElementById('res-phone').textContent = v['Phone'] || 'N/A';
    document.getElementById('res-email').textContent = v['Email'] || 'N/A';
    document.getElementById('res-bank').textContent = `${v['Bank Name']} | A/C: ${v['Account Number']} | IFSC: ${v['IFSC Code']}`;

    // Step 3: Validation
    document.getElementById('res-val-score').textContent = `${val.validation_score.toFixed(0)}%`;
    const valGrid = document.getElementById('res-val-grid');
    valGrid.innerHTML = '';
    for (const [fName, fDetail] of Object.entries(val.fields)) {
        const isOk = !fDetail.toLowerCase().includes('missing') && !fDetail.toLowerCase().includes('invalid') && !fDetail.toLowerCase().includes('mismatch');
        const card = document.createElement('div');
        card.className = `p-3 rounded-lg border ${isOk ? 'border-emerald-500/20 bg-emerald-950/10' : 'border-rose-500/20 bg-rose-950/10'}`;
        card.innerHTML = `
            <div class="flex items-center justify-between">
                <span class="text-xs font-semibold text-slate-300">${fName}</span>
                <span class="text-xs font-bold ${isOk ? 'text-emerald-400' : 'text-rose-400'}">${isOk ? 'VALID' : 'FAILED'}</span>
            </div>
            <p class="text-xs text-slate-400 mt-1 truncate" title="${fDetail}">${fDetail}</p>
        `;
        valGrid.appendChild(card);
    }

    // Step 4: Duplicate
    const dupCard = document.getElementById('res-dup-card');
    if (dup.is_duplicate) {
        dupCard.className = 'p-4 rounded-lg border border-rose-500/40 bg-rose-950/20 text-rose-300 text-sm';
        dupCard.innerHTML = `⚠️ <b>Duplicate Record Detected!</b> Matched on existing master record by <code>${dup.duplicate_field}</code>.`;
    } else {
        dupCard.className = 'p-4 rounded-lg border border-emerald-500/40 bg-emerald-950/20 text-emerald-300 text-sm';
        dupCard.innerHTML = `✅ <b>No Exact Duplicate Found.</b> Vendor tax identifiers and identity are unique in master database.`;
    }

    // Step 5: Semantic Peers
    const peersContainer = document.getElementById('res-peers-container');
    peersContainer.innerHTML = '';
    if (sim.peers && sim.peers.length) {
        sim.peers.forEach(p => {
            const pv = p.vendor;
            const peerDiv = document.createElement('div');
            peerDiv.className = 'p-3 rounded-lg border border-slate-700 bg-slate-800/40 flex items-center justify-between';
            peerDiv.innerHTML = `
                <div>
                    <h5 class="text-sm font-semibold text-slate-200">${pv['Vendor Name'] || pv['vendor_name']}</h5>
                    <p class="text-xs text-slate-400">${pv['Business Category'] || pv['business_category']} • ${pv['Address'] || 'N/A'}</p>
                </div>
                <div class="text-right">
                    <span class="text-sm font-bold text-indigo-400">${p.similarity_pct}</span>
                    <p class="text-xs text-slate-500">${p.tier}</p>
                </div>
            `;
            peersContainer.appendChild(peerDiv);
        });
    } else {
        peersContainer.innerHTML = '<p class="text-xs text-slate-500">No prior peer records found for comparison.</p>';
    }

    // Step 6: Risk Breakdown
    document.getElementById('res-risk-score').textContent = `${risk['Risk Score']} / 100`;
    document.getElementById('res-risk-level').textContent = risk['Risk Level'];
    
    const posList = document.getElementById('res-pos-findings');
    posList.innerHTML = '';
    (risk['Positive Findings'] || []).forEach(item => {
        const li = document.createElement('li');
        li.className = 'text-xs text-emerald-300 flex items-start gap-1.5';
        li.innerHTML = `<span>✅</span><span>${item}</span>`;
        posList.appendChild(li);
    });

    const riskList = document.getElementById('res-risk-factors');
    riskList.innerHTML = '';
    const rfArr = risk['Risk Factors'] || [];
    if (rfArr.length) {
        rfArr.forEach(item => {
            const li = document.createElement('li');
            li.className = 'text-xs text-rose-300 flex items-start gap-1.5';
            li.innerHTML = `<span>⚠️</span><span>${item}</span>`;
            riskList.appendChild(li);
        });
    } else {
        riskList.innerHTML = '<li class="text-xs text-slate-400">No significant risk factors flagged.</li>';
    }

    // PDF Download Button in Step 7
    const btnPdf = document.getElementById('btn-download-result-pdf');
    if (data.vendor_id) {
        btnPdf.onclick = () => window.open(API.getReportPdfUrl(data.vendor_id), '_blank');
        btnPdf.classList.remove('hidden');
    } else {
        btnPdf.classList.add('hidden');
    }

    c.scrollIntoView({ behavior: 'smooth' });
}


// ============================================================
// DASHBOARD & DATA VISUALIZATIONS (CHART.JS)
// ============================================================

async function loadDashboard() {
    try {
        const stats = await API.getStats();
        const charts = await API.getCharts();

        // Top Metrics
        document.getElementById('kpi-total').textContent = (stats.total_vendors || 0).toLocaleString();
        document.getElementById('kpi-approved').textContent = stats.approved || 0;
        document.getElementById('kpi-review').textContent = stats.under_review || 0;
        document.getElementById('kpi-rejected').textContent = stats.rejected || 0;
        document.getElementById('kpi-valid').textContent = stats.valid_records || 0;

        // Rates
        const tot = stats.total_vendors || 1;
        document.getElementById('kpi-approved-rate').textContent = `${((stats.approved / tot) * 100).toFixed(1)}%`;
        document.getElementById('kpi-review-rate').textContent = `${((stats.under_review / tot) * 100).toFixed(1)}%`;
        document.getElementById('kpi-rejected-rate').textContent = `${((stats.rejected / tot) * 100).toFixed(1)}%`;
        document.getElementById('kpi-valid-rate').textContent = `${((stats.valid_records / tot) * 100).toFixed(1)}% verified`;

        // Render Charts
        renderCategoryChart(charts.category_distribution);
        renderRiskDonutChart(charts.risk_distribution);
        renderRecChart(charts.recommendation_distribution);
        renderRiskBarChart(charts.risk_by_category);

        // Render Watchlist
        renderWatchlist(charts.watchlist);

    } catch (e) {
        console.error('Dashboard load failed:', e);
        showToast('Failed to load dashboard metrics.', 'error');
    }
}

function renderCategoryChart(data) {
    const ctx = document.getElementById('chart-category');
    if (!ctx) return;
    if (State.charts.category) State.charts.category.destroy();

    State.charts.category = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels || [],
            datasets: [{
                label: 'Vendors',
                data: data.data || [],
                backgroundColor: 'rgba(59, 130, 246, 0.7)',
                borderColor: '#3b82f6',
                borderWidth: 1,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { ticks: { color: '#94a3b8', font: { size: 10 } }, grid: { display: false } },
                y: { ticks: { color: '#94a3b8', precision: 0 }, grid: { color: 'rgba(255,255,255,0.05)' } }
            }
        }
    });
}

function renderRiskDonutChart(data) {
    const ctx = document.getElementById('chart-risk');
    if (!ctx) return;
    if (State.charts.risk) State.charts.risk.destroy();

    State.charts.risk = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.labels || ['LOW', 'MEDIUM', 'HIGH'],
            datasets: [{
                data: data.data || [0, 0, 0],
                backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom', labels: { color: '#cbd5e1', font: { size: 11 } } }
            },
            cutout: '70%'
        }
    });
}

function renderRecChart(data) {
    const ctx = document.getElementById('chart-rec');
    if (!ctx) return;
    if (State.charts.rec) State.charts.rec.destroy();

    State.charts.rec = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.labels || ['APPROVE', 'REVIEW', 'REJECT'],
            datasets: [{
                data: data.data || [0, 0, 0],
                backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom', labels: { color: '#cbd5e1', font: { size: 11 } } }
            },
            cutout: '70%'
        }
    });
}

function renderRiskBarChart(data) {
    const ctx = document.getElementById('chart-risk-cat');
    if (!ctx) return;
    if (State.charts.riskCat) State.charts.riskCat.destroy();

    State.charts.riskCat = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels || [],
            datasets: [{
                label: 'Mean Risk Score',
                data: data.data || [],
                backgroundColor: 'rgba(239, 68, 68, 0.7)',
                borderColor: '#ef4444',
                borderWidth: 1,
                borderRadius: 6
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { ticks: { color: '#94a3b8' }, max: 100, grid: { color: 'rgba(255,255,255,0.05)' } },
                y: { ticks: { color: '#94a3b8', font: { size: 10 } }, grid: { display: false } }
            }
        }
    });
}

function renderWatchlist(items) {
    const tbody = document.getElementById('watchlist-tbody');
    if (!tbody) return;
    tbody.innerHTML = '';

    if (!items || !items.length) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center py-6 text-slate-500 text-sm">✅ No active compliance violations or duplicate alerts.</td></tr>';
        return;
    }

    items.forEach(item => {
        const tr = document.createElement('tr');
        tr.className = 'border-b border-slate-800 hover:bg-slate-800/30 text-xs';
        tr.innerHTML = `
            <td class="py-3 px-4 font-mono text-slate-400">#${item.id}</td>
            <td class="py-3 px-4 font-semibold text-slate-200">${item.vendor_name}</td>
            <td class="py-3 px-4 text-slate-400">${item.business_category}</td>
            <td class="py-3 px-4 font-mono text-slate-300">${item.gstin || 'N/A'}</td>
            <td class="py-3 px-4 font-bold ${item.risk_level === 'HIGH' ? 'text-rose-400' : 'text-amber-400'}">${item.risk_score} / 100 (${item.risk_level})</td>
            <td class="py-3 px-4">
                <span class="px-2 py-0.5 rounded text-[10px] font-bold ${item.recommendation === 'REJECT' ? 'bg-rose-950 text-rose-400 border border-rose-800' : 'bg-amber-950 text-amber-400 border border-amber-800'}">${item.recommendation}</span>
            </td>
        `;
        tbody.appendChild(tr);
    });
}


// ============================================================
// SEMANTIC SEARCH
// ============================================================

function initSearchView() {
    const btn = document.getElementById('btn-search-exec');
    const input = document.getElementById('search-query-input');
    const slider = document.getElementById('search-sim-slider');
    const sliderVal = document.getElementById('search-sim-val');
    const catSelect = document.getElementById('search-cat-select');

    if (slider && sliderVal) {
        slider.addEventListener('input', () => {
            sliderVal.textContent = `${slider.value}%`;
        });
    }

    async function doSearch() {
        const q = input.value.trim();
        if (!q) {
            showToast('Please enter a natural language search query.', 'warning');
            return;
        }

        const resultsContainer = document.getElementById('search-results-list');
        resultsContainer.innerHTML = '<div class="col-span-2 text-center py-12 text-slate-400"><span class="animate-spin inline-block mr-2">⚙️</span> Searching vector embeddings via FAISS...</div>';

        try {
            const data = await API.semanticSearch({
                query: q,
                min_similarity: parseInt(slider.value) / 100,
                category: catSelect.value,
                top_k: 12
            });

            resultsContainer.innerHTML = '';
            document.getElementById('search-count-badge').textContent = `Found ${data.total} matches`;

            if (!data.results || !data.results.length) {
                resultsContainer.innerHTML = '<div class="col-span-2 text-center py-12 text-slate-500">No matching vendor records found meeting the similarity threshold. Try lowering the threshold or refining terms.</div>';
                return;
            }

            data.results.forEach((item, idx) => {
                const card = document.createElement('div');
                card.className = 'glass-card glass-card-hover p-5 rounded-xl flex flex-col justify-between';
                
                const recClass = item.Recommendation === 'APPROVE' ? 'bg-emerald-950 text-emerald-400 border-emerald-800' : item.Recommendation === 'REVIEW' ? 'bg-amber-950 text-amber-400 border-amber-800' : 'bg-rose-950 text-rose-400 border-rose-800';
                
                card.innerHTML = `
                    <div>
                        <div class="flex items-start justify-between gap-2 mb-2">
                            <h4 class="font-bold text-slate-100 text-base leading-snug">${item['Vendor Name']}</h4>
                            <span class="px-2 py-0.5 rounded text-[10px] font-bold border ${recClass}">${item.Recommendation}</span>
                        </div>
                        <p class="text-xs text-indigo-400 font-medium mb-3">🏢 ${item['Business Category']}</p>
                        <p class="text-xs text-slate-400 mb-3">📍 ${item.Address}</p>
                        <div class="grid grid-cols-2 gap-2 text-xs font-mono bg-slate-900/60 p-2.5 rounded-lg mb-3">
                            <div><span class="text-slate-500">GSTIN:</span> ${item.GSTIN}</div>
                            <div><span class="text-slate-500">PAN:</span> ${item.PAN}</div>
                            <div><span class="text-slate-500">Phone:</span> ${item.Phone}</div>
                            <div><span class="text-slate-500">Email:</span> ${item.Email}</div>
                        </div>
                    </div>
                    <div class="pt-3 border-t border-slate-700/60 flex items-center justify-between">
                        <div class="flex items-center gap-2">
                            <div class="w-2.5 h-2.5 rounded-full ${item['Risk Level'] === 'LOW' ? 'bg-emerald-500' : item['Risk Level'] === 'MEDIUM' ? 'bg-amber-500' : 'bg-rose-500'}"></div>
                            <span class="text-xs font-bold text-slate-300">Risk: ${item['Risk Score']}/100</span>
                        </div>
                        <span class="text-xs font-extrabold text-blue-400 bg-blue-950/60 px-2.5 py-1 rounded-full border border-blue-800/40">⚡ ${item['Similarity Pct']} Match</span>
                    </div>
                `;
                resultsContainer.appendChild(card);
            });

        } catch (e) {
            resultsContainer.innerHTML = `<div class="col-span-2 text-center py-12 text-rose-400">Search error: ${e.message}</div>`;
        }
    }

    if (btn) btn.addEventListener('click', doSearch);
    if (input) input.addEventListener('keypress', (e) => { if (e.key === 'Enter') doSearch(); });
}


// ============================================================
// VENDOR DATABASE & CRUD
// ============================================================

async function loadDatabase() {
    const tbody = document.getElementById('db-table-body');
    const searchInput = document.getElementById('db-search-input');
    const catFilter = document.getElementById('db-cat-filter');
    const riskFilter = document.getElementById('db-risk-filter');
    const recFilter = document.getElementById('db-rec-filter');

    if (!tbody) return;
    tbody.innerHTML = '<tr><td colspan="7" class="text-center py-8 text-slate-400"><span class="animate-spin inline-block mr-2">⚙️</span> Loading master records...</td></tr>';

    try {
        const params = {};
        if (searchInput && searchInput.value) params.search = searchInput.value;
        if (catFilter && catFilter.value !== 'All') params.category = catFilter.value;
        if (riskFilter && riskFilter.value !== 'All') params.risk_level = riskFilter.value;
        if (recFilter && recFilter.value !== 'All') params.recommendation = recFilter.value;

        const data = await API.getVendors(params);
        State.vendors = data.vendors || [];

        tbody.innerHTML = '';
        document.getElementById('db-total-count').textContent = `Showing ${State.vendors.length} vendors`;

        if (!State.vendors.length) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center py-8 text-slate-500">No vendor records match the filter criteria.</td></tr>';
            return;
        }

        State.vendors.forEach(v => {
            const tr = document.createElement('tr');
            tr.className = 'border-b border-slate-800 hover:bg-slate-800/40 text-xs transition';
            
            const recClass = v.recommendation === 'APPROVE' ? 'bg-emerald-950 text-emerald-400 border-emerald-800' : v.recommendation === 'REVIEW' ? 'bg-amber-950 text-amber-400 border-amber-800' : 'bg-rose-950 text-rose-400 border-rose-800';
            const riskCol = v.risk_level === 'LOW' ? 'text-emerald-400' : v.risk_level === 'MEDIUM' ? 'text-amber-400' : 'text-rose-400';

            tr.innerHTML = `
                <td class="py-3 px-4 font-mono text-slate-400">#${v.id}</td>
                <td class="py-3 px-4 font-semibold text-slate-100">${v.vendor_name}</td>
                <td class="py-3 px-4 text-slate-400">${v.business_category || 'N/A'}</td>
                <td class="py-3 px-4 font-mono text-slate-300">${v.gstin || 'N/A'}</td>
                <td class="py-3 px-4 font-bold ${riskCol}">${v.risk_score} / 100 (${v.risk_level})</td>
                <td class="py-3 px-4"><span class="px-2 py-0.5 rounded text-[10px] font-bold border ${recClass}">${v.recommendation}</span></td>
                <td class="py-3 px-4 text-right space-x-1.5">
                    <button onclick="window.open(API.getReportPdfUrl(${v.id}), '_blank')" class="px-2.5 py-1 rounded bg-emerald-600/20 text-emerald-400 hover:bg-emerald-600/40 border border-emerald-500/30 font-semibold transition" title="Download Official PDF Report">📄 PDF</button>
                    <button onclick="openVendorModal(${v.id})" class="px-2.5 py-1 rounded bg-blue-600/20 text-blue-400 hover:bg-blue-600/40 border border-blue-500/30 transition">View</button>
                    <button onclick="deleteVendorRecord(${v.id})" class="px-2.5 py-1 rounded bg-rose-600/20 text-rose-400 hover:bg-rose-600/40 border border-rose-500/30 transition">Delete</button>
                </td>
            `;
            tbody.appendChild(tr);
        });

    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center py-8 text-rose-400">Failed to load database: ${e.message}</td></tr>`;
    }
}

async function openVendorModal(id) {
    const modal = document.getElementById('vendor-modal');
    if (!modal) return;

    try {
        const data = await API.getVendor(id);
        const v = data.vendor;
        const a = data.assessment || {};

        document.getElementById('modal-title').textContent = v.vendor_name;
        document.getElementById('modal-id-badge').textContent = `#${v.id}`;
        document.getElementById('modal-gstin').textContent = v.gstin || 'N/A';
        document.getElementById('modal-pan').textContent = v.pan || 'N/A';
        document.getElementById('modal-category').textContent = v.business_category || 'N/A';
        document.getElementById('modal-address').textContent = v.address || 'N/A';
        document.getElementById('modal-contact').textContent = v.contact_person || 'N/A';
        document.getElementById('modal-phone').textContent = v.phone || 'N/A';
        document.getElementById('modal-email').textContent = v.email || 'N/A';
        document.getElementById('modal-bank').textContent = `${v.bank_name} | A/C: ${v.account_number} | IFSC: ${v.ifsc_code}`;
        document.getElementById('modal-summary').textContent = a.summary || 'Assessment recorded.';

        document.getElementById('modal-btn-pdf').onclick = () => window.open(API.getReportPdfUrl(v.id), '_blank');

        modal.classList.remove('hidden');
    } catch (e) {
        showToast('Failed to load vendor details', 'error');
    }
}

function closeVendorModal() {
    const modal = document.getElementById('vendor-modal');
    if (modal) modal.classList.add('hidden');
}

async function deleteVendorRecord(id) {
    if (!confirm(`Are you sure you want to delete vendor #${id}?`)) return;
    try {
        await API.deleteVendor(id);
        showToast(`Vendor #${id} deleted successfully.`, 'success');
        loadDatabase();
    } catch (e) {
        showToast('Failed to delete vendor record', 'error');
    }
}


// ============================================================
// AUDIT LOGS
// ============================================================

async function loadAuditLogs() {
    const tbody = document.getElementById('audit-tbody');
    const filter = document.getElementById('audit-event-filter');
    if (!tbody) return;

    tbody.innerHTML = '<tr><td colspan="6" class="text-center py-6 text-slate-400">Loading audit history...</td></tr>';

    try {
        const ev = filter ? filter.value : 'All';
        const data = await API.getAuditLogs(ev);
        tbody.innerHTML = '';

        if (!data.logs || !data.logs.length) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center py-6 text-slate-500">No audit logs recorded yet.</td></tr>';
            return;
        }

        data.logs.forEach(l => {
            const tr = document.createElement('tr');
            tr.className = 'border-b border-slate-800 hover:bg-slate-800/30 text-xs';
            tr.innerHTML = `
                <td class="py-2.5 px-4 font-mono text-slate-400">${l.timestamp}</td>
                <td class="py-2.5 px-4 font-bold text-indigo-400 font-mono">${l.event_type}</td>
                <td class="py-2.5 px-4 text-slate-200 font-medium">${l.vendor_name || 'N/A'}</td>
                <td class="py-2.5 px-4 text-slate-400">${l.user_action || 'System'}</td>
                <td class="py-2.5 px-4"><span class="px-2 py-0.5 rounded text-[10px] font-bold ${l.status === 'SUCCESS' ? 'bg-emerald-950 text-emerald-400' : 'bg-rose-950 text-rose-400'}">${l.status}</span></td>
                <td class="py-2.5 px-4 font-mono text-[11px] text-slate-400 truncate max-w-xs" title="${l.details || ''}">${l.details || '-'}</td>
            `;
            tbody.appendChild(tr);
        });

    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-center py-6 text-rose-400">Failed to load audit trail: ${e.message}</td></tr>`;
    }
}


// ============================================================
// REPORTS VIEW
// ============================================================

async function loadReportsView() {
    const select = document.getElementById('report-vendor-select');
    if (!select) return;

    try {
        const data = await API.getVendors();
        select.innerHTML = '<option value="">-- Choose Vendor to Generate Compliance Dossier --</option>';
        (data.vendors || []).forEach(v => {
            const opt = document.createElement('option');
            opt.value = v.id;
            opt.textContent = `${v.vendor_name} (GSTIN: ${v.gstin || 'N/A'}) - ${v.recommendation}`;
            select.appendChild(opt);
        });

        const btnExecPdf = document.getElementById('btn-report-exec-pdf');
        if (btnExecPdf) {
            btnExecPdf.onclick = () => window.open(API.getExecutiveSummaryPdfUrl(), '_blank');
        }

        select.onchange = async () => {
            if (!select.value) return;
            const previewContainer = document.getElementById('report-preview-frame');
            const btnPdf = document.getElementById('btn-report-dl-pdf');
            
            previewContainer.src = `${API_BASE}/api/reports/${select.value}/html`;
            previewContainer.classList.remove('hidden');
            
            btnPdf.onclick = () => window.open(API.getReportPdfUrl(select.value), '_blank');
            btnPdf.classList.remove('hidden');
        };

    } catch (e) {
        showToast('Failed to load vendors for reports', 'error');
    }
}

function loadRiskView() {
    // Risk view static rubric & state distribution
}


// ============================================================
// APP INITIALIZATION
// ============================================================

document.addEventListener('DOMContentLoaded', () => {
    // Setup Nav Buttons
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const view = btn.dataset.view;
            if (view) navigateTo(view);
        });
    });

    // Seed Data Button in Topbar
    const btnSeed = document.getElementById('btn-seed-data');
    if (btnSeed) {
        btnSeed.addEventListener('click', async () => {
            try {
                const res = await API.seedData();
                showToast(res.message, 'success');
                if (State.currentView === 'dashboard') loadDashboard();
                if (State.currentView === 'database') loadDatabase();
            } catch (e) {
                showToast('Seeding failed', 'error');
            }
        });
    }

    // Init Component Handlers
    initProcessingView();
    initSearchView();

    // Default start view
    navigateTo('processing');
});
