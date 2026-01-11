"""
REST API Module - Forensic Chain
Provides API endpoints for interacting with the system via HTTP.
"""
from flask import Flask, request, jsonify, render_template
import os
import sys

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.smart_contract import ForensicContract
from src.evidence_store import EvidenceStore

app = Flask(__name__)
contract = ForensicContract()
evidence_store = EvidenceStore()


# ============== WEB UI ENDPOINTS ==============

@app.route('/')
def index():
    """Serve the web UI."""
    return render_template('index.html')


def api_response(success: bool, message: str, data=None):
    """Standard response format."""
    return jsonify({
        "success": success,
        "message": message,
        "data": data
    })

def validate_required_fields(data, required):
    """Validate required fields in request data."""
    if not data:
        return False, "No data provided"
    missing = [field for field in required if field not in data]
    if missing:
        return False, f"Missing required fields: {missing}"
    return True, "Valid"


# ============== PARTICIPANT ENDPOINTS ==============

@app.route('/api/participants', methods=['POST'])
def register_participant():
    """Register new participant."""
    data = request.json
    valid, msg = validate_required_fields(data, ['participant_id', 'name', 'role', 'organization'])
    if not valid:
        return api_response(False, msg), 400
    
    success, msg = contract.register_participant(
        data['participant_id'], data['name'], 
        data['role'], data['organization']
    )
    return api_response(success, msg), 200 if success else 400


@app.route('/api/participants/<participant_id>', methods=['GET'])
def get_participant(participant_id):
    """Get participant information."""
    participant = contract.get_participant(participant_id)
    if participant:
        return api_response(True, "Success", participant.to_dict())
    return api_response(False, "Participant not found"), 404


@app.route('/api/participants', methods=['GET'])
def list_participants():
    """List all participants."""
    participants = [p.to_dict() for p in contract.participant_registry.values()]
    return api_response(True, f"Found {len(participants)} participants", participants)


# ============== EVIDENCE ENDPOINTS ==============

@app.route('/api/evidence', methods=['POST'])
def create_evidence():
    """Create new evidence."""
    data = request.json
    valid, msg = validate_required_fields(data, 
        ['evidence_id', 'description', 'creator_id', 'file_hash', 'file_location', 'case_id'])
    if not valid:
        return api_response(False, msg), 400
    
    success, msg = contract.create_evidence(
        evidence_id=data['evidence_id'],
        description=data['description'],
        creator_id=data['creator_id'],
        file_hash=data['file_hash'],
        file_location=data['file_location'],
        case_id=data['case_id'],
        metadata=data.get('metadata', {})
    )
    return api_response(success, msg), 200 if success else 400


@app.route('/api/evidence/<evidence_id>', methods=['GET'])
def get_evidence(evidence_id):
    """Get evidence information."""
    evidence = contract.get_evidence(evidence_id)
    if evidence:
        return api_response(True, "Success", evidence)
    return api_response(False, "Evidence not found"), 404


@app.route('/api/evidence', methods=['GET'])
def list_evidence():
    """List all evidence."""
    active_only = request.args.get('active_only', 'true').lower() == 'true'
    evidence_list = contract.list_all_evidence(active_only=active_only)
    return api_response(True, f"Found {len(evidence_list)} evidence items", evidence_list)


@app.route('/api/evidence/<evidence_id>/history', methods=['GET'])
def get_evidence_history(evidence_id):
    """Get evidence transaction history."""
    history = contract.get_evidence_history(evidence_id)
    return api_response(True, f"Found {len(history)} transactions", history)


@app.route('/api/evidence/transfer', methods=['POST'])
def transfer_evidence():
    """Transfer evidence ownership."""
    data = request.json
    valid, msg = validate_required_fields(data, ['evidence_id', 'from_owner_id', 'to_owner_id', 'reason'])
    if not valid:
        return api_response(False, msg), 400
    
    success, msg = contract.transfer_evidence(
        data['evidence_id'], data['from_owner_id'],
        data['to_owner_id'], data['reason']
    )
    return api_response(success, msg), 200 if success else 400


@app.route('/api/evidence/<evidence_id>', methods=['DELETE'])
def delete_evidence(evidence_id):
    """Delete (deactivate) evidence."""
    data = request.json or {}
    requester_id = data.get('requester_id')
    reason = data.get('reason', 'No reason provided')
    
    if not requester_id:
        return api_response(False, "Missing requester_id"), 400
    
    success, msg = contract.delete_evidence(evidence_id, requester_id, reason)
    return api_response(success, msg), 200 if success else 400


@app.route('/api/evidence/<evidence_id>/verify', methods=['POST'])
def verify_evidence(evidence_id):
    """Verify evidence integrity."""
    data = request.json
    file_hash = data.get('file_hash')
    
    if not file_hash:
        return api_response(False, "Missing file_hash"), 400
    
    is_valid, msg = contract.verify_evidence_integrity(evidence_id, file_hash)
    return api_response(is_valid, msg)


# ============== EVIDENCE STORE ENDPOINTS ==============

@app.route('/api/store/upload', methods=['POST'])
def store_evidence_file():
    """Upload and store evidence file."""
    if 'file' not in request.files:
        return api_response(False, "No file provided"), 400
    
    file = request.files['file']
    evidence_id = request.form.get('evidence_id')
    case_id = request.form.get('case_id')
    
    if not evidence_id or not case_id:
        return api_response(False, "Missing evidence_id or case_id"), 400
    
    # Save temporary file
    temp_path = f"./temp_{evidence_id}"
    file.save(temp_path)
    
    # Store in evidence store
    success, storage_path, file_hash = evidence_store.store_evidence(
        temp_path, evidence_id, case_id
    )
    
    # Clean up temp file
    if os.path.exists(temp_path):
        os.remove(temp_path)
    
    if success:
        return api_response(True, "File stored successfully", {
            "storage_path": storage_path,
            "file_hash": file_hash
        })
    else:
        return api_response(False, file_hash), 400


@app.route('/api/store/verify/<evidence_id>', methods=['POST'])
def verify_stored_file(evidence_id):
    """Verify stored file integrity."""
    data = request.json
    storage_path = data.get('storage_path')
    expected_hash = data.get('expected_hash')
    
    if not storage_path or not expected_hash:
        return api_response(False, "Missing storage_path or expected_hash"), 400
    
    is_valid, msg = evidence_store.verify_file_integrity(storage_path, expected_hash)
    return api_response(is_valid, msg)


@app.route('/api/store/stats', methods=['GET'])
def get_storage_stats():
    """Get storage statistics."""
    stats = evidence_store.get_storage_stats()
    return api_response(True, "Storage statistics", stats)


@app.route('/api/store/case/<case_id>', methods=['GET'])
def list_case_evidence_files(case_id):
    """List all evidence files for a case."""
    files = evidence_store.list_evidence_by_case(case_id)
    return api_response(True, f"Found {len(files)} files", files)


# ============== CASE ENDPOINTS ==============

@app.route('/api/cases/<case_id>/evidence', methods=['GET'])
def get_case_evidence(case_id):
    """Get all evidence for a case."""
    evidence_list = contract.get_evidence_by_case(case_id)
    return api_response(True, f"Found {len(evidence_list)} evidence items for case {case_id}", evidence_list)


# ============== BLOCKCHAIN ENDPOINTS ==============

@app.route('/api/blockchain', methods=['GET'])
def get_blockchain():
    """Get entire blockchain."""
    chain = contract.blockchain.to_dict()
    return api_response(True, f"Blockchain has {len(chain)} blocks", chain)


@app.route('/api/blockchain/info', methods=['GET'])
def get_blockchain_info():
    """Get blockchain overview information."""
    info = contract.get_blockchain_info()
    return api_response(True, "Success", info)


@app.route('/api/blockchain/verify', methods=['GET'])
def verify_blockchain():
    """Verify blockchain integrity."""
    is_valid, msg = contract.verify_blockchain()
    return api_response(is_valid, msg)


# ============== UTILITY ENDPOINTS ==============

@app.route('/api/hash', methods=['POST'])
def calculate_hash():
    """Calculate SHA256 hash for data."""
    data = request.json
    content = data.get('content', '')
    hash_value = hashlib.sha256(content.encode()).hexdigest()
    return api_response(True, "Success", {"hash": hash_value})


@app.route('/api/health', methods=['GET'])
def health_check():
    """Check system status."""
    return api_response(True, "System is running normally", {
        "status": "healthy",
        "blockchain_valid": contract.blockchain.is_chain_valid(),
        "total_evidence": len(contract.evidence_registry),
        "total_participants": len(contract.participant_registry),
        "storage_stats": evidence_store.get_storage_stats()
    })


@app.route('/api', methods=['GET'])
def api_info():
    """API information endpoint."""
    return api_response(True, "Forensic-Chain API", {
        "version": "1.0.0",
        "description": "Digital Forensics Chain of Custody Management System",
        "endpoints": {
            "participants": "/api/participants",
            "evidence": "/api/evidence",
            "blockchain": "/api/blockchain",
            "storage": "/api/store",
            "health": "/api/health"
        }
    })


if __name__ == '__main__':
    print("=" * 60)
    print("  FORENSIC-CHAIN API SERVER")
    print("  Digital Forensics Chain of Custody Management System")
    print("=" * 60)
    print("\n  Server starting at: http://localhost:5000")
    print("  Press CTRL+C to stop\n")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)
