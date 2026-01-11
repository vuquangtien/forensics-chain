#!/usr/bin/env python3
"""
Comprehensive Demo Script - Forensic Chain
Demonstrates complete forensic investigation workflow from evidence collection to court.
"""
import sys
import os
import hashlib
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.smart_contract import ForensicContract
from src.evidence_store import EvidenceStore


def print_header(title, width=80):
    """Print formatted section header."""
    print("\n" + "=" * width)
    print(f"  {title}".center(width))
    print("=" * width)


def print_step(step_num, description):
    """Print step description."""
    print(f"\n[STEP {step_num}] {description}")
    print("-" * 80)


def print_result(success, message, indent=2):
    """Print operation result."""
    status = "✓ SUCCESS" if success else "✗ FAILED"
    spaces = " " * indent
    print(f"{spaces}{status}: {message}")


def print_info(label, value, indent=2):
    """Print information."""
    spaces = " " * indent
    print(f"{spaces}{label}: {value}")


def pause(seconds=1):
    """Pause execution for dramatic effect."""
    time.sleep(seconds)


def main():
    print_header("FORENSIC-CHAIN COMPREHENSIVE DEMO")
    print("\n  This demo simulates a complete digital forensics workflow:")
    print("    1. Crime scene investigation and evidence collection")
    print("    2. Forensic laboratory analysis")
    print("    3. Prosecutor case preparation")
    print("    4. Court presentation and verification")
    print("\n  Case: Cybercrime Investigation - Unauthorized Access")
    
    input("\nPress ENTER to begin...")
    
    # Initialize system
    print_header("SYSTEM INITIALIZATION")
    contract = ForensicContract()
    evidence_store = EvidenceStore()
    print_result(True, "Forensic Chain system initialized")
    print_result(True, "Evidence store initialized")
    pause()
    
    # ==================== PHASE 1: PARTICIPANT REGISTRATION ====================
    print_header("PHASE 1: PARTICIPANT REGISTRATION")
    print_step(1, "Registering Law Enforcement Officers and Officials")
    
    participants = [
        {
            "id": "INV-2026-001",
            "name": "Detective John Smith",
            "role": "investigator",
            "org": "Metro Police Department - Cybercrime Unit"
        },
        {
            "id": "INV-2026-002",
            "name": "Officer Sarah Johnson",
            "role": "investigator",
            "org": "Metro Police Department - Digital Forensics"
        },
        {
            "id": "FOR-2026-001",
            "name": "Dr. Michael Chen",
            "role": "forensic_expert",
            "org": "State Forensic Laboratory"
        },
        {
            "id": "FOR-2026-002",
            "name": "Dr. Emily Rodriguez",
            "role": "forensic_expert",
            "org": "State Forensic Laboratory - Digital Evidence"
        },
        {
            "id": "PRO-2026-001",
            "name": "ADA Robert Williams",
            "role": "prosecutor",
            "org": "District Attorney's Office"
        },
        {
            "id": "JUD-2026-001",
            "name": "Judge Patricia Anderson",
            "role": "judge",
            "org": "District Court"
        },
        {
            "id": "ADMIN-001",
            "name": "System Administrator",
            "role": "admin",
            "org": "Forensic Chain Operations"
        }
    ]
    
    for p in participants:
        success, msg = contract.register_participant(
            p["id"], p["name"], p["role"], p["org"]
        )
        print_result(success, f"{p['name']} ({p['role'].upper()})")
        pause(0.3)
    
    print(f"\n  Total registered participants: {len(contract.participant_registry)}")
    pause()
    
    # ==================== PHASE 2: CRIME SCENE INVESTIGATION ====================
    print_header("PHASE 2: CRIME SCENE INVESTIGATION")
    print_step(2, "Evidence Collection at Crime Scene")
    
    print("\n  Case Details:")
    print("    Case ID: CASE-2026-CYB-001")
    print("    Crime: Unauthorized computer access and data theft")
    print("    Location: TechCorp Inc., Server Room")
    print("    Date: January 8, 2026")
    print("    Investigator: Detective John Smith")
    
    pause()
    
    # Simulate evidence files
    evidence_items = [
        {
            "content": b"Server access log showing unauthorized login from IP 192.168.1.100 at 02:15 AM",
            "description": "Server access logs - showing unauthorized access attempt",
            "type": "log_file",
            "filename": "server_access.log"
        },
        {
            "content": b"Security camera footage showing individual entering server room at 02:10 AM",
            "description": "Security camera footage - Server room entrance",
            "type": "video",
            "filename": "camera_footage.mp4"
        },
        {
            "content": b"Hard drive image from compromised server containing malware",
            "description": "Forensic disk image - Compromised server HDD",
            "type": "disk_image",
            "filename": "server_disk.img"
        },
        {
            "content": b"Network packet capture showing data exfiltration to external server",
            "description": "Network traffic capture - Data exfiltration evidence",
            "type": "pcap",
            "filename": "network_capture.pcap"
        }
    ]
    
    print("\n  Creating evidence records on blockchain...")
    evidence_ids = []
    
    for idx, item in enumerate(evidence_items, 1):
        print(f"\n  Evidence #{idx}: {item['description']}")
        
        # Calculate hash
        file_hash = hashlib.sha256(item["content"]).hexdigest()
        evidence_id = file_hash[:16]
        evidence_ids.append(evidence_id)
        
        # Create evidence on blockchain
        success, msg = contract.create_evidence(
            evidence_id=evidence_id,
            description=item["description"],
            creator_id="INV-2026-001",
            file_hash=file_hash,
            file_location=f"/evidence_store/CASE-2026-CYB-001/{item['filename']}",
            case_id="CASE-2026-CYB-001",
            metadata={
                "type": item["type"],
                "collected_by": "Detective John Smith",
                "collection_date": "2026-01-08T14:30:00",
                "location": "TechCorp Inc., Server Room",
                "classification": "confidential"
            }
        )
        print_result(success, msg, indent=4)
        print_info("Evidence ID", evidence_id, indent=4)
        print_info("File Hash", file_hash[:32] + "...", indent=4)
        pause(0.5)
    
    # ==================== PHASE 3: EVIDENCE TRANSFER TO FORENSICS ====================
    print_header("PHASE 3: FORENSIC LABORATORY ANALYSIS")
    print_step(3, "Transferring Evidence to Forensic Laboratory")
    
    print("\n  Detective Smith transfers evidence to forensic experts for analysis...")
    
    # Transfer first two pieces of evidence to Dr. Chen
    for i in [0, 1]:
        success, msg = contract.transfer_evidence(
            evidence_id=evidence_ids[i],
            from_owner_id="INV-2026-001",
            to_owner_id="FOR-2026-001",
            reason=f"Transfer to forensic laboratory for {evidence_items[i]['type']} analysis"
        )
        print_result(success, msg, indent=2)
        pause(0.5)
    
    # Transfer other two to Dr. Rodriguez
    for i in [2, 3]:
        success, msg = contract.transfer_evidence(
            evidence_id=evidence_ids[i],
            from_owner_id="INV-2026-001",
            to_owner_id="FOR-2026-002",
            reason=f"Transfer to forensic laboratory for {evidence_items[i]['type']} analysis"
        )
        print_result(success, msg, indent=2)
        pause(0.5)
    
    print_step(4, "Forensic Analysis Results")
    print("\n  Forensic experts analyze evidence and document findings...")
    pause()
    
    # Show evidence history
    print(f"\n  Chain of Custody for Evidence #{evidence_ids[0][:8]}...")
    evidence = contract.get_evidence(evidence_ids[0])
    for idx, transfer in enumerate(evidence["transfer_history"], 1):
        print(f"    {idx}. {transfer['from_owner']} → {transfer['to_owner']}")
        print(f"       Reason: {transfer['reason']}")
        print(f"       Time: {transfer['timestamp']}")
    
    # ==================== PHASE 4: PROSECUTOR PREPARATION ====================
    print_header("PHASE 4: PROSECUTOR CASE PREPARATION")
    print_step(5, "Transferring Evidence to District Attorney")
    
    print("\n  Forensic analysis complete. Transferring all evidence to prosecutor...")
    
    for idx, ev_id in enumerate(evidence_ids):
        evidence = contract.get_evidence(ev_id)
        current_owner = evidence["current_owner_id"]
        
        success, msg = contract.transfer_evidence(
            evidence_id=ev_id,
            from_owner_id=current_owner,
            to_owner_id="PRO-2026-001",
            reason="Evidence analysis complete - Transferred for prosecution"
        )
        print_result(success, msg, indent=2)
        pause(0.3)
    
    print("\n  Prosecutor reviews evidence for case preparation...")
    pause()
    
    # ==================== PHASE 5: COURT PROCEEDINGS ====================
    print_header("PHASE 5: COURT PROCEEDINGS")
    print_step(6, "Evidence Presentation in Court")
    
    print("\n  Prosecutor submits evidence to court for trial...")
    
    for idx, ev_id in enumerate(evidence_ids):
        success, msg = contract.transfer_evidence(
            evidence_id=ev_id,
            from_owner_id="PRO-2026-001",
            to_owner_id="JUD-2026-001",
            reason="Evidence submitted for court proceedings - Case #2026-CYB-001"
        )
        print_result(success, msg, indent=2)
        pause(0.3)
    
    # ==================== PHASE 6: INTEGRITY VERIFICATION ====================
    print_header("PHASE 6: EVIDENCE INTEGRITY VERIFICATION")
    print_step(7, "Court Verifies Evidence Authenticity")
    
    print("\n  Judge orders verification of evidence integrity...")
    pause()
    
    for idx, (ev_id, item) in enumerate(zip(evidence_ids, evidence_items), 1):
        print(f"\n  Verifying Evidence #{idx}: {item['description']}")
        
        # Verify with correct hash
        file_hash = hashlib.sha256(item["content"]).hexdigest()
        is_valid, msg = contract.verify_evidence_integrity(ev_id, file_hash)
        print_result(is_valid, msg, indent=4)
        pause(0.5)
    
    # Test tampering detection
    print("\n  Testing tampering detection (simulated modified file)...")
    tampered_hash = hashlib.sha256(b"Modified content - tampered").hexdigest()
    is_valid, msg = contract.verify_evidence_integrity(evidence_ids[0], tampered_hash)
    print_result(not is_valid, msg, indent=4)
    
    # Verify blockchain
    print("\n  Verifying blockchain integrity...")
    is_valid, msg = contract.verify_blockchain()
    print_result(is_valid, msg, indent=2)
    pause()
    
    # ==================== PHASE 7: COMPLETE CHAIN OF CUSTODY ====================
    print_header("PHASE 7: COMPLETE CHAIN OF CUSTODY REPORT")
    print_step(8, "Generating Chain of Custody Documentation")
    
    print(f"\n  Evidence ID: {evidence_ids[0]}")
    print(f"  Description: {evidence_items[0]['description']}")
    print("\n  Complete Chain of Custody:")
    
    history = contract.get_evidence_history(evidence_ids[0])
    for idx, tx in enumerate(history, 1):
        print(f"\n    Transaction #{idx}")
        print(f"      Type: {tx['type']}")
        print(f"      Block: #{tx['block_index']}")
        print(f"      Time: {tx['timestamp']}")
        if 'from_owner' in tx:
            print(f"      From: {tx['from_owner']}")
            print(f"      To: {tx['to_owner']}")
            print(f"      Reason: {tx['reason']}")
    
    # ==================== FINAL STATISTICS ====================
    print_header("SYSTEM STATISTICS")
    
    info = contract.get_blockchain_info()
    
    print(f"\n  Blockchain Information:")
    print(f"    Total Blocks: {info['total_blocks']}")
    print(f"    Blockchain Valid: {info['is_valid']}")
    print(f"    Mining Difficulty: {info['difficulty']}")
    print(f"    Latest Block Hash: {info['latest_block_hash'][:32]}...")
    
    print(f"\n  Registry Statistics:")
    print(f"    Total Participants: {len(contract.participant_registry)}")
    print(f"    Total Evidence Items: {len(contract.evidence_registry)}")
    print(f"    Active Evidence: {len(contract.list_all_evidence(active_only=True))}")
    
    # Count transactions by type
    all_blocks = contract.blockchain.to_dict()
    tx_types = {}
    for block in all_blocks:
        for tx in block['transactions']:
            tx_type = tx.get('type', 'unknown')
            tx_types[tx_type] = tx_types.get(tx_type, 0) + 1
    
    print(f"\n  Transaction Summary:")
    for tx_type, count in sorted(tx_types.items()):
        print(f"    {tx_type}: {count}")
    
    print_header("DEMO COMPLETE")
    print("\n  ✓ Full forensic investigation workflow demonstrated")
    print("  ✓ Chain of custody maintained throughout entire process")
    print("  ✓ Evidence integrity verified on blockchain")
    print("  ✓ All transfers properly documented and immutable")
    print("\n  The Forensic-Chain system ensures:")
    print("    • Complete traceability of evidence")
    print("    • Tamper-proof chain of custody")
    print("    • Cryptographic verification of authenticity")
    print("    • Compliance with legal requirements")
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
