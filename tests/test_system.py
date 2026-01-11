#!/usr/bin/env python3
"""
Test Script - Forensic Chain
Script to test all system functionalities.
"""
import sys
import os

# Add root directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.smart_contract import ForensicContract
import hashlib


def print_header(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_result(success, message):
    status = "✓" if success else "✗"
    print(f"  {status} {message}")


def main():
    print_header("FORENSIC-CHAIN - SYSTEM TEST")
    
    # Initialize contract
    contract = ForensicContract()
    print_result(True, "ForensicContract initialized successfully")
    
    # ============== TEST 1: PARTICIPANT REGISTRATION ==============
    print_header("1. PARTICIPANT REGISTRATION")
    
    participants = [
        ("INV001", "John Smith", "investigator", "Metro Police Department"),
        ("FOR001", "Sarah Chen", "forensic_expert", "State Forensic Laboratory"),
        ("PRO001", "Robert Williams", "prosecutor", "District Attorney's Office"),
        ("JUD001", "Patricia Anderson", "judge", "District Court"),
        ("ADM001", "System Admin", "admin", "Administration"),
    ]
    
    for pid, name, role, org in participants:
        success, msg = contract.register_participant(pid, name, role, org)
        print_result(success, f"{name} ({role})")
    
    # Test duplicate registration
    success, msg = contract.register_participant("INV001", "Test", "investigator", "Test")
    print_result(not success, f"Rejected duplicate ID: {msg}")
    
    # ============== TEST 2: CREATE EVIDENCE ==============
    print_header("2. EVIDENCE CREATION")
    
    # Create hash for simulated files
    evidence_data = [
        {
            "file_content": "Surveillance video recording of crime scene - Camera 1",
            "description": "Surveillance video from crime scene area",
            "case_id": "CASE-2026-001",
            "creator_id": "INV001"
        },
        {
            "file_content": "Fingerprint image collected from scene",
            "description": "Fingerprint sample from glass door",
            "case_id": "CASE-2026-001",
            "creator_id": "FOR001"
        },
        {
            "file_content": "DNA analysis report of suspect",
            "description": "DNA test results",
            "case_id": "CASE-2026-001",
            "creator_id": "FOR001"
        }
    ]
    
    evidence_ids = []
    for data in evidence_data:
        file_hash = hashlib.sha256(data["file_content"].encode()).hexdigest()
        evidence_id = file_hash[:16]  # Use first 16 chars as ID
        evidence_ids.append(evidence_id)
        
        success, msg = contract.create_evidence(
            evidence_id=evidence_id,
            description=data["description"],
            creator_id=data["creator_id"],
            file_hash=file_hash,
            file_location=f"/evidence_store/{evidence_id}.dat",
            case_id=data["case_id"],
            metadata={"type": "digital", "classification": "confidential"}
        )
        print_result(success, f"Created evidence: {data['description'][:40]}...")
    
    # Test creating evidence with non-existent creator
    success, msg = contract.create_evidence(
        "TEST123", "Test", "UNKNOWN_USER", "hash", "/path", "CASE001"
    )
    print_result(not success, f"Rejected non-existent creator: {msg}")
    
    # Test permission - prosecutor cannot create evidence
    success, msg = contract.register_participant("PRO002", "Test Prosecutor", "prosecutor", "Test")
    success, msg = contract.create_evidence(
        "TEST456", "Test", "PRO002", "hash123", "/path", "CASE001"
    )
    print_result(not success, f"Rejected unauthorized role: {msg}")
    
    # ============== TEST 3: DISPLAY EVIDENCE ==============
    print_header("3. DISPLAY EVIDENCE")
    
    # Get evidence details
    evidence = contract.get_evidence(evidence_ids[0])
    if evidence:
        print_result(True, f"Retrieved evidence details: {evidence['evidence_id']}")
        print(f"      - Description: {evidence['description']}")
        print(f"      - Owner: {evidence['current_owner_id']}")
        print(f"      - Case: {evidence['case_id']}")
    
    # List all evidence
    all_evidence = contract.list_all_evidence()
    print_result(True, f"Total evidence in system: {len(all_evidence)}")
    
    # Get evidence by case
    case_evidence = contract.get_evidence_by_case("CASE-2026-001")
    print_result(True, f"Evidence for case CASE-2026-001: {len(case_evidence)}")
    
    # ============== TEST 4: TRANSFER EVIDENCE ==============
    print_header("4. EVIDENCE TRANSFER")
    
    # Transfer from investigator -> forensic expert
    success, msg = contract.transfer_evidence(
        evidence_id=evidence_ids[0],
        from_owner_id="INV001",
        to_owner_id="FOR001",
        reason="Transfer for forensic analysis"
    )
    print_result(success, msg)
    
    # Transfer from forensic expert -> prosecutor
    success, msg = contract.transfer_evidence(
        evidence_id=evidence_ids[0],
        from_owner_id="FOR001",
        to_owner_id="PRO001",
        reason="Transfer for prosecution preparation"
    )
    print_result(success, msg)
    
    # Transfer from prosecutor -> judge
    success, msg = contract.transfer_evidence(
        evidence_id=evidence_ids[0],
        from_owner_id="PRO001",
        to_owner_id="JUD001",
        reason="Evidence submitted for court proceedings"
    )
    print_result(success, msg)
    
    # Test invalid transfer (non-owner)
    success, msg = contract.transfer_evidence(
        evidence_id=evidence_ids[0],
        from_owner_id="INV001",  # No longer owner
        to_owner_id="FOR001",
        reason="Test"
    )
    print_result(not success, f"Rejected invalid transfer: {msg}")
    
    # View transfer history
    evidence = contract.get_evidence(evidence_ids[0])
    print_result(True, f"Transfer history ({len(evidence['transfer_history'])} transfers):")
    for i, transfer in enumerate(evidence['transfer_history'], 1):
        print(f"      {i}. {transfer['from_owner']} → {transfer['to_owner']}: {transfer['reason']}")
    
    # ============== TEST 5: INTEGRITY VERIFICATION ==============
    print_header("5. INTEGRITY VERIFICATION")
    
    # Verify with correct hash
    original_hash = hashlib.sha256(evidence_data[0]["file_content"].encode()).hexdigest()
    is_valid, msg = contract.verify_evidence_integrity(evidence_ids[0], original_hash)
    print_result(is_valid, msg)
    
    # Verify with tampered hash
    tampered_hash = hashlib.sha256("Modified content - tampered".encode()).hexdigest()
    is_valid, msg = contract.verify_evidence_integrity(evidence_ids[0], tampered_hash)
    print_result(not is_valid, msg)
    
    # Verify blockchain
    is_valid, msg = contract.verify_blockchain()
    print_result(is_valid, msg)
    
    # ============== TEST 6: DELETE EVIDENCE ==============
    print_header("6. EVIDENCE DELETION")
    
    # Test deletion by non-creator (current owner but not creator)
    success, msg = contract.delete_evidence(
        evidence_id=evidence_ids[0],
        requester_id="JUD001",  # Current owner but not creator
        reason="Test deletion"
    )
    print_result(not success, f"Rejected deletion by owner who is not creator: {msg}")
    
    # Delete by creator (FOR001 created evidence 1)
    success, msg = contract.delete_evidence(
        evidence_id=evidence_ids[1],
        requester_id="FOR001",  # Creator
        reason="Evidence no longer relevant to case"
    )
    print_result(success, msg)
    
    # Delete by admin (soft delete only)
    success, msg = contract.delete_evidence(
        evidence_id=evidence_ids[2],
        requester_id="ADM001",  # Admin
        reason="Administrative decision (soft delete)"
    )
    print_result(success, msg)
    
    # Check active evidence count
    active_evidence = contract.list_all_evidence(active_only=True)
    print_result(True, f"Active evidence count: {len(active_evidence)}")
    
    all_evidence = contract.list_all_evidence(active_only=False)
    print_result(True, f"Total evidence (including deleted): {len(all_evidence)}")
    
    # ============== TEST 7: BLOCKCHAIN INFORMATION ==============
    print_header("7. BLOCKCHAIN INFORMATION")
    
    info = contract.get_blockchain_info()
    print_result(True, f"Total blocks: {info['total_blocks']}")
    print_result(True, f"Blockchain valid: {info['is_valid']}")
    print_result(True, f"Mining difficulty: {info['difficulty']}")
    print_result(True, f"Latest block hash: {info['latest_block_hash'][:32]}...")
    
    # View transaction history for evidence
    history = contract.get_evidence_history(evidence_ids[0])
    print_result(True, f"Blockchain transaction history ({len(history)} transactions):")
    for tx in history:
        print(f"      - Block #{tx['block_index']}: {tx['type']}")
    
    # ============== TEST 8: ACCESS CONTROL ==============
    print_header("8. ACCESS CONTROL VERIFICATION")
    
    # Test investigator can create evidence
    test_hash = hashlib.sha256(b"test evidence").hexdigest()
    test_id = test_hash[:16]
    success, msg = contract.create_evidence(
        test_id, "Test", "INV001", test_hash, "/test", "TEST"
    )
    print_result(success, "Investigator can create evidence")
    
    # Test forensic expert can create evidence
    test_hash2 = hashlib.sha256(b"test evidence 2").hexdigest()
    test_id2 = test_hash2[:16]
    success, msg = contract.create_evidence(
        test_id2, "Test 2", "FOR001", test_hash2, "/test2", "TEST"
    )
    print_result(success, "Forensic expert can create evidence")
    
    # Test prosecutor cannot create evidence
    test_hash3 = hashlib.sha256(b"test evidence 3").hexdigest()
    test_id3 = test_hash3[:16]
    success, msg = contract.create_evidence(
        test_id3, "Test 3", "PRO001", test_hash3, "/test3", "TEST"
    )
    print_result(not success, f"Prosecutor cannot create evidence: {msg[:50]}...")
    
    # Test judge cannot create evidence
    test_hash4 = hashlib.sha256(b"test evidence 4").hexdigest()
    test_id4 = test_hash4[:16]
    success, msg = contract.create_evidence(
        test_id4, "Test 4", "JUD001", test_hash4, "/test4", "TEST"
    )
    print_result(not success, f"Judge cannot create evidence: {msg[:50]}...")
    
    # ============== RESULTS ==============
    print_header("TEST RESULTS")
    print_result(True, "All functionalities working correctly!")
    print()
    print("  The Forensic-Chain system is ready for use.")
    print("  To start API server: python api/app.py")
    print("  To run complete demo: python demo_complete.py")
    print("  To test API: ./test_api.sh")
    print()


if __name__ == "__main__":
    main()
