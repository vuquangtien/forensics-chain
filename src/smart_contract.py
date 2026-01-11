"""
Smart Contract Module - Forensic Chain
Implements 4 main functions: Create, Transfer, Delete, Display evidence.
"""
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from .blockchain import Blockchain
from .models import Evidence, Participant, TransferRecord, ParticipantRole


class ForensicContract:
    """Smart Contract managing digital evidence on blockchain."""
    
    def __init__(self):
        self.blockchain = Blockchain(difficulty=2)
        self.evidence_registry: Dict[str, Evidence] = {}   # Evidence registry
        self.participant_registry: Dict[str, Participant] = {}  # Participant registry
    
    # ============== ACCESS CONTROL ==============
    
    def _check_permission(self, participant_id: str, required_roles: List[ParticipantRole]) -> Tuple[bool, str]:
        """
        Check if participant has required role.
        
        Args:
            participant_id: ID of participant
            required_roles: List of roles that are allowed
            
        Returns:
            Tuple[bool, str]: (Has permission?, Message)
        """
        participant = self.participant_registry.get(participant_id)
        if not participant:
            return False, f"Participant '{participant_id}' not found"
        
        if participant.role not in required_roles:
            return False, f"Permission denied. Required roles: {[r.value for r in required_roles]}"
        
        return True, "Permission granted"
    
    # ============== PARTICIPANT MANAGEMENT ==============
    
    def register_participant(self, participant_id: str, name: str, 
                            role: str, organization: str) -> Tuple[bool, str]:
        """Register new participant in the system."""
        if participant_id in self.participant_registry:
            return False, f"Participant with ID '{participant_id}' already exists"
        
        try:
            participant = Participant(
                participant_id=participant_id,
                name=name,
                role=ParticipantRole(role),
                organization=organization
            )
            self.participant_registry[participant_id] = participant
            
            # Record registration transaction
            self.blockchain.add_transaction({
                "type": "REGISTER_PARTICIPANT",
                "participant_id": participant_id,
                "name": name,
                "role": role
            })
            
            return True, f"Successfully registered participant: {name}"
        except ValueError:
            return False, f"Role '{role}' is invalid"
    
    def get_participant(self, participant_id: str) -> Optional[Participant]:
        """Get participant information."""
        return self.participant_registry.get(participant_id)
    
    # ============== 1. EVIDENCE CREATION ==============
    
    def create_evidence(self, evidence_id: str, description: str, 
                       creator_id: str, file_hash: str, 
                       file_location: str, case_id: str,
                       metadata: dict = None) -> Tuple[bool, str]:
        """
        Create new evidence and record it on blockchain.
        
        Args:
            evidence_id: Evidence ID (usually SHA256 of file)
            description: Evidence description
            creator_id: Creator ID
            file_hash: Hash of original file
            file_location: Storage location of file
            case_id: Related case ID
            metadata: Additional information
        
        Returns:
            Tuple[bool, str]: (Success?, Message)
        """
        # Check if ID already exists
        if evidence_id in self.evidence_registry:
            return False, f"Evidence with ID '{evidence_id}' already exists in system"
        
        # Check if creator exists
        if creator_id not in self.participant_registry:
            return False, f"Participant with ID '{creator_id}' not found"
        
        # Check permission - only investigators and forensic experts can create evidence
        has_permission, msg = self._check_permission(
            creator_id, 
            [ParticipantRole.INVESTIGATOR, ParticipantRole.FORENSIC_EXPERT, ParticipantRole.ADMIN]
        )
        if not has_permission:
            return False, msg
        
        # Create new evidence - creator is initial owner
        evidence = Evidence(
            evidence_id=evidence_id,
            description=description,
            creator_id=creator_id,
            current_owner_id=creator_id,  # Initial owner = Creator
            file_hash=file_hash,
            file_location=file_location,
            case_id=case_id,
            metadata=metadata or {}
        )
        
        # Save to registry
        self.evidence_registry[evidence_id] = evidence
        
        # Record creation transaction on blockchain
        tx_id = self.blockchain.add_transaction({
            "type": "CREATE_EVIDENCE",
            "evidence_id": evidence_id,
            "creator_id": creator_id,
            "file_hash": file_hash,
            "case_id": case_id,
            "description": description
        })
        
        # Mine block immediately to record
        self.blockchain.mine_pending_transactions()
        
        return True, f"Evidence created successfully. Transaction ID: {tx_id}"
    
    # ============== 2. EVIDENCE TRANSFER ==============
    
    def transfer_evidence(self, evidence_id: str, from_owner_id: str,
                         to_owner_id: str, reason: str) -> Tuple[bool, str]:
        """
        Transfer evidence ownership from one person to another.
        
        Args:
            evidence_id: Evidence ID
            from_owner_id: Current owner ID
            to_owner_id: Recipient ID
            reason: Transfer reason
        
        Returns:
            Tuple[bool, str]: (Success?, Message)
        """
        # Check if evidence exists
        if evidence_id not in self.evidence_registry:
            return False, f"Evidence with ID '{evidence_id}' not found"
        
        evidence = self.evidence_registry[evidence_id]
        
        # Check if evidence is still active
        if not evidence.is_active:
            return False, "Evidence has been deleted/deactivated"
        
        # Check current ownership
        if evidence.current_owner_id != from_owner_id:
            return False, f"User '{from_owner_id}' is not the current owner"
        
        # Check if recipient exists
        if to_owner_id not in self.participant_registry:
            return False, f"Recipient with ID '{to_owner_id}' not found"
        
        # Record transfer history
        transfer_record = TransferRecord(
            from_owner=from_owner_id,
            to_owner=to_owner_id,
            timestamp=datetime.now().isoformat(),
            reason=reason
        )
        evidence.transfer_history.append(transfer_record)
        
        # Update new owner
        evidence.current_owner_id = to_owner_id
        
        # Record transaction on blockchain
        tx_id = self.blockchain.add_transaction({
            "type": "TRANSFER_EVIDENCE",
            "evidence_id": evidence_id,
            "from_owner": from_owner_id,
            "to_owner": to_owner_id,
            "reason": reason
        })
        
        # Mine block
        self.blockchain.mine_pending_transactions()
        
        from_name = self.participant_registry[from_owner_id].name
        to_name = self.participant_registry[to_owner_id].name
        
        return True, f"Transfer successful from '{from_name}' to '{to_name}'. Transaction ID: {tx_id}"
    
    # ============== 3. EVIDENCE DELETION ==============
    
    def delete_evidence(self, evidence_id: str, requester_id: str, 
                       reason: str) -> Tuple[bool, str]:
        """
        Mark evidence as inactive (soft delete).
        Note: History on blockchain is still preserved.
        
        Args:
            evidence_id: Evidence ID
            requester_id: ID of person requesting deletion
            reason: Deletion reason
        
        Returns:
            Tuple[bool, str]: (Success?, Message)
        """
        # Check if evidence exists
        if evidence_id not in self.evidence_registry:
            return False, f"Evidence with ID '{evidence_id}' not found"
        
        evidence = self.evidence_registry[evidence_id]
        
        # Check if already deleted
        if not evidence.is_active:
            return False, "Evidence has already been deactivated"
        
        # Check deletion permission (only owner or admin)
        requester = self.participant_registry.get(requester_id)
        if not requester:
            return False, f"User '{requester_id}' not found"
        
        is_owner = evidence.current_owner_id == requester_id
        is_admin = requester.role == ParticipantRole.ADMIN
        
        if not (is_owner or is_admin):
            return False, "No permission to delete this evidence"
        
        # Mark as inactive (soft delete)
        evidence.is_active = False
        
        # Record transaction on blockchain
        tx_id = self.blockchain.add_transaction({
            "type": "DELETE_EVIDENCE",
            "evidence_id": evidence_id,
            "deleted_by": requester_id,
            "reason": reason
        })
        
        # Mine block
        self.blockchain.mine_pending_transactions()
        
        return True, f"Evidence deactivated. History is still preserved on blockchain. Transaction ID: {tx_id}"
    
    # ============== 4. EVIDENCE DISPLAY ==============
    
    def get_evidence(self, evidence_id: str) -> Optional[Dict]:
        """Get detailed information of evidence."""
        evidence = self.evidence_registry.get(evidence_id)
        if not evidence:
            return None
        return evidence.to_dict()
    
    def get_evidence_history(self, evidence_id: str) -> List[Dict]:
        """Get complete transaction history of evidence from blockchain."""
        return self.blockchain.get_transaction_history(evidence_id)
    
    def list_all_evidence(self, active_only: bool = True) -> List[Dict]:
        """List all evidence in the system."""
        result = []
        for evidence in self.evidence_registry.values():
            if active_only and not evidence.is_active:
                continue
            result.append(evidence.to_dict())
        return result
    
    def get_evidence_by_case(self, case_id: str) -> List[Dict]:
        """Get all evidence of a case."""
        return [
            e.to_dict() for e in self.evidence_registry.values()
            if e.case_id == case_id and e.is_active
        ]
    
    def get_evidence_by_owner(self, owner_id: str) -> List[Dict]:
        """Get all evidence owned by a participant."""
        return [
            e.to_dict() for e in self.evidence_registry.values()
            if e.current_owner_id == owner_id and e.is_active
        ]
    
    # ============== INTEGRITY VERIFICATION ==============
    
    def verify_evidence_integrity(self, evidence_id: str, current_file_hash: str) -> Tuple[bool, str]:
        """
        Verify evidence integrity by comparing hash.
        
        Args:
            evidence_id: Evidence ID
            current_file_hash: Hash of current file to check
        
        Returns:
            Tuple[bool, str]: (Valid?, Message)
        """
        evidence = self.evidence_registry.get(evidence_id)
        if not evidence:
            return False, "Evidence not found"
        
        if evidence.file_hash == current_file_hash:
            return True, "✓ Evidence valid - File has not been modified"
        else:
            return False, "✗ WARNING: File has been modified from original!"
    
    def verify_blockchain(self) -> Tuple[bool, str]:
        """Verify blockchain integrity."""
        if self.blockchain.is_chain_valid():
            return True, "✓ Blockchain valid - No signs of tampering"
        else:
            return False, "✗ WARNING: Blockchain has been modified!"
    
    def get_blockchain_info(self) -> Dict:
        """Get blockchain overview information."""
        return {
            "total_blocks": len(self.blockchain.chain),
            "is_valid": self.blockchain.is_chain_valid(),
            "pending_transactions": len(self.blockchain.pending_transactions),
            "difficulty": self.blockchain.difficulty,
            "latest_block_hash": self.blockchain.get_latest_block().hash
        }
