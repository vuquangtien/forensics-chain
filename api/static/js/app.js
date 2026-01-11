// Forensic-Chain - Main JavaScript

const API_BASE = 'http://localhost:5000/api';

// State Management
let currentUser = { participant_id: null, name: null, role: null };
let allEvidence = [];

// =============================================================================
// INITIALIZATION
// =============================================================================

document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    loadCurrentUser();
    refreshDashboard();
    loadParticipants();
    populateParticipantSelects();
    
    setInterval(populateParticipantSelects, 30000);
    setInterval(refreshDashboard, 10000);
});

document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        e.target.classList.remove('active');
    }
});

// =============================================================================
// USER MANAGEMENT
// =============================================================================

function loadCurrentUser() {
    const saved = localStorage.getItem('forensic_current_user');
    if (saved) {
        currentUser = JSON.parse(saved);
        updateUserDisplay();
    } else {
        setTimeout(showLoginModal, 500);
    }
}

function updateUserDisplay() {
    document.getElementById('current-user-name').textContent = currentUser.name || 'Not logged in';
    const roleSpan = document.getElementById('current-user-role');
    roleSpan.textContent = currentUser.role || 'No role';
    roleSpan.className = currentUser.role ? `badge badge-${getRoleColor(currentUser.role)}` : 'badge';
}

function getRoleColor(role) {
    const colors = {
        'investigator': 'primary',
        'forensic_expert': 'success',
        'prosecutor': 'warning',
        'judge': 'danger',
        'admin': 'dark'
    };
    return colors[role] || 'primary';
}

async function showLoginModal() {
    const result = await apiCall('/participants');
    const select = document.getElementById('current-user-select');
    
    if (result.success && result.data.length > 0) {
        select.innerHTML = '<option value="">Select participant...</option>' +
            result.data.map(p => 
                `<option value="${p.participant_id}" data-name="${p.name}" data-role="${p.role}">
                    ${p.name} (${p.role})
                </option>`
            ).join('');
    }
    
    document.getElementById('login-modal').classList.add('active');
}

function closeLoginModal() {
    document.getElementById('login-modal').classList.remove('active');
}

function loginAsUser() {
    const select = document.getElementById('current-user-select');
    const selectedOption = select.options[select.selectedIndex];
    
    if (!select.value) {
        showAlert('Please select a participant', 'danger');
        return;
    }
    
    currentUser = {
        participant_id: select.value,
        name: selectedOption.dataset.name,
        role: selectedOption.dataset.role
    };
    
    localStorage.setItem('forensic_current_user', JSON.stringify(currentUser));
    updateUserDisplay();
    closeLoginModal();
    
    const creatorSelect = document.getElementById('creator_id');
    if (creatorSelect && ['investigator', 'forensic_expert', 'admin'].includes(currentUser.role)) {
        creatorSelect.value = currentUser.participant_id;
    }
    
    showAlert(`Logged in as ${currentUser.name}`, 'success');
}

// =============================================================================
// TAB MANAGEMENT
// =============================================================================

function initTabs() {
    const tabs = document.querySelectorAll('.nav-tab');
    const contents = document.querySelectorAll('.tab-content');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const target = tab.dataset.tab;
            
            tabs.forEach(t => t.classList.remove('active'));
            contents.forEach(c => c.classList.remove('active'));
            
            tab.classList.add('active');
            document.getElementById(target).classList.add('active');
            
            switch(target) {
                case 'dashboard': refreshDashboard(); break;
                case 'participants': loadParticipants(); break;
                case 'evidence': loadEvidence(); break;
                case 'delete': populateDeleteSelect(); break;
                case 'blockchain': loadBlockchain(); break;
            }
        });
    });
}

// =============================================================================
// API HELPERS
// =============================================================================

function showAlert(message, type = 'success') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.innerHTML = `<strong>${type === 'success' ? 'SUCCESS' : 'ERROR'}</strong> ${message}`;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(() => alertDiv.remove(), 5000);
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

async function apiCall(endpoint, method = 'GET', data = null) {
    try {
        const options = {
            method,
            headers: { 'Content-Type': 'application/json' }
        };
        
        if (data) options.body = JSON.stringify(data);
        
        const response = await fetch(`${API_BASE}${endpoint}`, options);
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        showAlert('Network error. Check if server is running.', 'danger');
        throw error;
    }
}

// =============================================================================
// DASHBOARD
// =============================================================================

async function refreshDashboard() {
    try {
        const [health, blockchain] = await Promise.all([
            apiCall('/health'),
            apiCall('/blockchain/info')
        ]);
        
        if (health.success) {
            document.getElementById('stat-participants').textContent = health.data.total_participants;
            document.getElementById('stat-evidence').textContent = health.data.total_evidence;
            document.getElementById('stat-blocks').textContent = blockchain.data.total_blocks;
            document.getElementById('stat-valid').textContent = blockchain.data.is_valid ? 'YES' : 'NO';
            document.getElementById('stat-valid').style.color = blockchain.data.is_valid ? '#10b981' : '#ef4444';
        }
    } catch (error) {
        console.error('Dashboard refresh error:', error);
    }
}

// =============================================================================
// PARTICIPANTS
// =============================================================================

async function loadParticipants() {
    const result = await apiCall('/participants');
    const container = document.getElementById('participants-list');
    
    if (result.success && result.data.length > 0) {
        container.innerHTML = result.data.map(p => `
            <div class="item-card">
                <h3>${p.name}</h3>
                <p><strong>ID:</strong> ${p.participant_id}</p>
                <p><strong>Role:</strong> <span class="badge badge-${getRoleColor(p.role)}">${p.role}</span></p>
                <p><strong>Organization:</strong> ${p.organization}</p>
                <p><strong>Registered:</strong> ${new Date(p.created_at).toLocaleString()}</p>
            </div>
        `).join('');
    } else {
        container.innerHTML = '<p style="color: #6b7280;">No participants registered yet.</p>';
    }
}

async function registerParticipant(e) {
    e.preventDefault();
    const form = e.target;
    const btn = form.querySelector('button[type="submit"]');
    const originalText = btn.textContent;
    
    btn.disabled = true;
    btn.innerHTML = '<span class="loading"></span> Registering...';
    
    const data = {
        participant_id: form.participant_id.value,
        name: form.name.value,
        role: form.role.value,
        organization: form.organization.value
    };
    
    const result = await apiCall('/participants', 'POST', data);
    
    if (result.success) {
        showAlert(result.message, 'success');
        form.reset();
        await loadParticipants();
        await populateParticipantSelects();
        refreshDashboard();
    } else {
        showAlert(result.message, 'danger');
    }
    
    btn.disabled = false;
    btn.textContent = originalText;
}

async function populateParticipantSelects() {
    const result = await apiCall('/participants');
    
    if (result.success) {
        const selects = ['creator_id', 'from_owner', 'to_owner', 'delete_requester_id'];
        
        selects.forEach(selectId => {
            const select = document.getElementById(selectId);
            if (select) {
                const currentValue = select.value;
                select.innerHTML = '<option value="">Select participant...</option>' +
                    result.data.map(p => `<option value="${p.participant_id}">${p.name} (${p.role})</option>`).join('');
                
                if (currentValue && Array.from(select.options).some(opt => opt.value === currentValue)) {
                    select.value = currentValue;
                }
            }
        });
    }
}

async function populateDeleteSelect() {
    await populateParticipantSelects();
}

// =============================================================================
// EVIDENCE
// =============================================================================

async function loadEvidence() {
    const result = await apiCall('/evidence?active_only=false');
    
    if (result.success) {
        allEvidence = result.data;
        displayEvidence(allEvidence);
        populateCaseFilter();
    } else {
        document.getElementById('evidence-list').innerHTML = '<p style="color: #6b7280;">No evidence recorded yet.</p>';
    }
}

function displayEvidence(evidence) {
    const container = document.getElementById('evidence-list');
    
    if (evidence.length > 0) {
        container.innerHTML = evidence.map(e => `
            <div class="item-card">
                <h3>${e.description}</h3>
                <p><strong>ID:</strong> <code>${e.evidence_id}</code></p>
                <p><strong>Case:</strong> ${e.case_id}</p>
                <p><strong>Owner:</strong> <span class="badge badge-success">${e.current_owner_id}</span></p>
                <p><strong>Status:</strong> ${e.is_active ? '<span class="badge badge-success">Active</span>' : '<span class="badge badge-danger">Inactive</span>'}</p>
                <p><strong>Transfers:</strong> ${e.transfer_history.length}</p>
                <button class="btn btn-primary" onclick="viewEvidenceDetails('${e.evidence_id}')">View Details</button>
            </div>
        `).join('');
    } else {
        container.innerHTML = '<p style="color: #6b7280;">No evidence matches your filters.</p>';
    }
}

function populateCaseFilter() {
    const cases = [...new Set(allEvidence.map(e => e.case_id))];
    const select = document.getElementById('filter-case');
    
    select.innerHTML = '<option value="">All Cases</option>' +
        cases.map(c => `<option value="${c}">${c}</option>`).join('');
}

function filterEvidence() {
    const searchTerm = document.getElementById('evidence-search').value.toLowerCase();
    const caseFilter = document.getElementById('filter-case').value;
    const statusFilter = document.getElementById('filter-status').value;
    
    let filtered = allEvidence;
    
    if (searchTerm) {
        filtered = filtered.filter(e => 
            e.description.toLowerCase().includes(searchTerm) ||
            e.evidence_id.toLowerCase().includes(searchTerm) ||
            e.case_id.toLowerCase().includes(searchTerm) ||
            e.creator_id.toLowerCase().includes(searchTerm) ||
            e.current_owner_id.toLowerCase().includes(searchTerm)
        );
    }
    
    if (caseFilter) {
        filtered = filtered.filter(e => e.case_id === caseFilter);
    }
    
    if (statusFilter === 'active') {
        filtered = filtered.filter(e => e.is_active);
    } else if (statusFilter === 'inactive') {
        filtered = filtered.filter(e => !e.is_active);
    }
    
    displayEvidence(filtered);
}

async function handleFileUpload(input) {
    const file = input.files[0];
    if (!file) return;
    
    document.getElementById('file_location').value = 'Processing...';
    document.getElementById('file_hash_display').value = 'Calculating...';
    
    try {
        const arrayBuffer = await file.arrayBuffer();
        const hashBuffer = await crypto.subtle.digest('SHA-256', arrayBuffer);
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        const fileHash = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
        
        const caseId = document.getElementById('case_id').value || 'temp';
        document.getElementById('file_hash_display').value = fileHash;
        document.getElementById('file_location').value = `/evidence_store/active/${caseId}/${file.name}`;
        
        showAlert('File hashed successfully', 'success');
    } catch (error) {
        showAlert('Error processing file: ' + error.message, 'danger');
        document.getElementById('file_location').value = '';
        document.getElementById('file_hash_display').value = '';
    }
}

async function createEvidence(e) {
    e.preventDefault();
    const form = e.target;
    const btn = form.querySelector('button[type="submit"]');
    const originalText = btn.textContent;
    
    btn.disabled = true;
    btn.innerHTML = '<span class="loading"></span> Creating...';
    
    let fileHash = document.getElementById('file_hash_display').value;
    if (!fileHash) {
        fileHash = await generateHash(form.description.value + Date.now());
    }
    
    const data = {
        evidence_id: fileHash.substring(0, 16),
        description: form.description.value,
        creator_id: form.creator_id.value || currentUser.participant_id,
        file_hash: fileHash,
        file_location: form.file_location.value || `/evidence_store/active/${form.case_id.value}/file.dat`,
        case_id: form.case_id.value,
        metadata: {
            type: form.evidence_type.value,
            created_via: 'web_ui'
        }
    };
    
    const result = await apiCall('/evidence', 'POST', data);
    
    if (result.success) {
        showAlert(result.message, 'success');
        form.reset();
        document.getElementById('file_hash_display').value = '';
        await loadEvidence();
        refreshDashboard();
    } else {
        showAlert(result.message, 'danger');
    }
    
    btn.disabled = false;
    btn.textContent = originalText;
}

async function viewEvidenceDetails(evidenceId) {
    const [evidence, history] = await Promise.all([
        apiCall(`/evidence/${evidenceId}`),
        apiCall(`/evidence/${evidenceId}/history`)
    ]);
    
    if (!evidence.success) {
        showAlert('Failed to load evidence details', 'danger');
        return;
    }
    
    const e = evidence.data;
    const content = document.getElementById('modal-evidence-content');
    
    content.innerHTML = `
        <div style="margin-bottom: 20px;">
            <h3 style="margin-bottom: 15px;">${e.description}</h3>
            <p><strong>Evidence ID:</strong> <code>${e.evidence_id}</code></p>
            <p><strong>Case ID:</strong> ${e.case_id}</p>
            <p><strong>File Hash:</strong> <code style="font-size: 0.85rem;">${e.file_hash}</code></p>
            <p><strong>Creator:</strong> ${e.creator_id}</p>
            <p><strong>Current Owner:</strong> <span class="badge badge-success">${e.current_owner_id}</span></p>
            <p><strong>Status:</strong> ${e.is_active ? '<span class="badge badge-success">Active</span>' : '<span class="badge badge-danger">Inactive</span>'}</p>
            <p><strong>Created:</strong> ${new Date(e.created_at).toLocaleString()}</p>
        </div>
        
        <h4 style="margin-top: 30px; margin-bottom: 15px;">Chain of Custody</h4>
        ${e.transfer_history.length > 0 ? `
            <div class="timeline">
                ${e.transfer_history.map((t, i) => `
                    <div class="timeline-item">
                        <h4>Transfer #${i + 1}</h4>
                        <p><strong>From:</strong> ${t.from_owner} → <strong>To:</strong> ${t.to_owner}</p>
                        <p><strong>Reason:</strong> ${t.reason}</p>
                        <p class="time">${new Date(t.timestamp).toLocaleString()}</p>
                    </div>
                `).join('')}
            </div>
        ` : '<p style="color: #6b7280;">No transfers yet</p>'}
        
        <h4 style="margin-top: 30px; margin-bottom: 15px;">Blockchain History</h4>
        ${history.success && history.data.length > 0 ? `
            <div class="timeline">
                ${history.data.map(tx => `
                    <div class="timeline-item">
                        <h4>${tx.type.replace(/_/g, ' ')}</h4>
                        <p><strong>Block:</strong> #${tx.block_index}</p>
                        <p><strong>Hash:</strong> <code style="font-size: 0.8rem;">${tx.block_hash.substring(0, 32)}...</code></p>
                        <p class="time">${new Date(tx.timestamp).toLocaleString()}</p>
                    </div>
                `).join('')}
            </div>
        ` : '<p style="color: #6b7280;">No blockchain records</p>'}
    `;
    
    document.getElementById('evidence-modal').classList.add('active');
}

function closeModal() {
    document.getElementById('evidence-modal').classList.remove('active');
}

// =============================================================================
// TRANSFER & DELETE
// =============================================================================

async function transferEvidence(e) {
    e.preventDefault();
    const form = e.target;
    const btn = form.querySelector('button[type="submit"]');
    const originalText = btn.textContent;
    
    btn.disabled = true;
    btn.innerHTML = '<span class="loading"></span> Transferring...';
    
    const data = {
        evidence_id: form.transfer_evidence_id.value,
        from_owner_id: form.from_owner.value,
        to_owner_id: form.to_owner.value,
        reason: form.reason.value
    };
    
    const result = await apiCall('/evidence/transfer', 'POST', data);
    
    if (result.success) {
        showAlert(result.message, 'success');
        form.reset();
        await loadEvidence();
    } else {
        showAlert(result.message, 'danger');
    }
    
    btn.disabled = false;
    btn.textContent = originalText;
}

async function deleteEvidence(e) {
    e.preventDefault();
    const form = e.target;
    
    if (!confirm('Are you sure you want to deactivate this evidence? This action will be recorded on the blockchain.')) {
        return;
    }
    
    const btn = form.querySelector('button[type="submit"]');
    const originalText = btn.textContent;
    btn.disabled = true;
    btn.innerHTML = '<span class="loading"></span> Deactivating...';
    
    const evidenceId = form.delete_evidence_id.value;
    const data = {
        requester_id: form.delete_requester_id.value || currentUser.participant_id,
        reason: form.delete_reason.value
    };
    
    const result = await apiCall(`/evidence/${evidenceId}`, 'DELETE', data);
    
    if (result.success) {
        showAlert(result.message, 'success');
        form.reset();
        await loadEvidence();
        refreshDashboard();
    } else {
        showAlert(result.message, 'danger');
    }
    
    btn.disabled = false;
    btn.textContent = originalText;
}

// =============================================================================
// BLOCKCHAIN
// =============================================================================

async function loadBlockchain() {
    const result = await apiCall('/blockchain');
    const container = document.getElementById('blockchain-viz');
    
    if (result.success && result.data.length > 0) {
        container.innerHTML = `
            <div class="blockchain-blocks">
                ${result.data.map(block => `
                    <div class="block">
                        <div class="block-header">Block #${block.index}</div>
                        <div class="block-content">
                            <p><strong>Timestamp:</strong> ${new Date(block.timestamp).toLocaleString()}</p>
                            <p><strong>Transactions:</strong> ${block.transactions.length}</p>
                            <p><strong>Previous Hash:</strong> <code style="font-size: 0.8rem;">${block.previous_hash.substring(0, 20)}...</code></p>
                            <p><strong>Current Hash:</strong> <code style="font-size: 0.8rem;">${block.hash.substring(0, 20)}...</code></p>
                            <p><strong>Nonce:</strong> ${block.nonce}</p>
                            ${block.transactions.length > 0 ? `
                                <div style="margin-top: 15px; padding: 10px; background: #f9fafb; border-radius: 4px;">
                                    <strong style="display: block; margin-bottom: 8px;">Transactions:</strong>
                                    ${block.transactions.map((tx, i) => `
                                        <div style="margin-bottom: 8px; padding: 8px; background: white; border-radius: 4px; font-size: 0.85rem;">
                                            <strong>#${i + 1}:</strong> ${tx.type ? tx.type.replace(/_/g, ' ') : 'UNKNOWN'}<br>
                                            ${tx.evidence_id ? `<span style="color: #6b7280;">Evidence: ${tx.evidence_id}</span>` : ''}
                                            ${tx.participant_id ? `<span style="color: #6b7280;">Participant: ${tx.participant_id}</span>` : ''}
                                        </div>
                                    `).join('')}
                                </div>
                            ` : ''}
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }
}

async function verifyBlockchain() {
    const btn = document.getElementById('verify-blockchain-btn');
    const originalText = btn.textContent;
    
    btn.disabled = true;
    btn.innerHTML = '<span class="loading"></span> Verifying...';
    
    const result = await apiCall('/blockchain/verify');
    
    showAlert(result.message, result.success ? 'success' : 'danger');
    
    btn.disabled = false;
    btn.textContent = originalText;
}

// =============================================================================
// UTILITIES
// =============================================================================

async function generateHash(data) {
    const encoder = new TextEncoder();
    const dataBuffer = encoder.encode(data);
    const hashBuffer = await crypto.subtle.digest('SHA-256', dataBuffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}
